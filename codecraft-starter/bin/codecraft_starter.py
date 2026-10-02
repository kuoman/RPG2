#!/usr/bin/env python3
import argparse
import fnmatch
import hashlib
import hmac
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
import tomllib
from xml.etree import ElementTree
from pathlib import Path, PurePosixPath


class MavenProjectDefinition:
    def __init__(self, group_id, artifact_id, java_version):
        if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*(\.[A-Za-z_][A-Za-z0-9_]*)*", group_id):
            raise ValueError(f"invalid Maven group id: {group_id}")
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]*", artifact_id):
            raise ValueError(f"invalid Maven artifact id: {artifact_id}")
        self.group_id = group_id
        self.artifact_id = artifact_id
        self.java_version = java_version

    def pom_xml(self):
        return f'''<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 https://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>

    <groupId>{self.group_id}</groupId>
    <artifactId>{self.artifact_id}</artifactId>
    <version>1.0.0-SNAPSHOT</version>

    <properties>
        <maven.compiler.release>{self.java_version}</maven.compiler.release>
        <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
        <junit.jupiter.version>5.14.4</junit.jupiter.version>
    </properties>

    <dependencyManagement>
        <dependencies>
            <dependency>
                <groupId>org.junit</groupId>
                <artifactId>junit-bom</artifactId>
                <version>${{junit.jupiter.version}}</version>
                <type>pom</type>
                <scope>import</scope>
            </dependency>
        </dependencies>
    </dependencyManagement>

    <dependencies>
        <dependency>
            <groupId>org.junit.jupiter</groupId>
            <artifactId>junit-jupiter</artifactId>
            <scope>test</scope>
        </dependency>
    </dependencies>

    <build>
        <plugins>
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-compiler-plugin</artifactId>
                <version>3.16.0</version>
            </plugin>
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-surefire-plugin</artifactId>
                <version>3.6.0</version>
                <configuration>
                    <includes>
                        <include>**/Test*.java</include>
                        <include>**/*Test.java</include>
                        <include>**/*Tests.java</include>
                        <include>**/*TestCase.java</include>
                        <include>**/*_bdd.java</include>
                    </includes>
                </configuration>
            </plugin>
        </plugins>
    </build>
</project>
'''


class DirectoryTransaction:
    def __init__(self, target, tracked_files, owned_roots, created_directories):
        self.target = target
        self.files = {}
        self.created_files = {}
        self.owned_roots = set(owned_roots)
        self.created_directories = self.missing_directories(created_directories)
        try:
            for path in set(tracked_files):
                self.files[path] = self.snapshot_file(path)
            for path in self.owned_roots:
                if os.path.lexists(path):
                    raise ValueError(f"bootstrap-owned path already exists: {path.relative_to(target)}")
        except BaseException:
            self.discard_backups()
            raise

    def restore(self):
        for path, record in self.files.items():
            if record is None:
                expected = self.created_files.get(path)
                if expected and self.matches(path, expected):
                    path.unlink()
                continue
            previous, backup = record
            if self.matches(path, previous):
                backup.unlink()
            else:
                path.parent.mkdir(parents=True, exist_ok=True)
                os.replace(backup, path)
        for path in sorted(self.owned_roots, key=lambda item: len(item.parts), reverse=True):
            if path.is_dir() and not path.is_symlink():
                shutil.rmtree(path)
            elif path.exists() or path.is_symlink():
                path.unlink()
        for path in sorted(self.created_directories, key=lambda item: len(item.parts), reverse=True):
            try:
                path.rmdir()
            except (FileNotFoundError, OSError):
                pass
        self.discard_backups()

    def commit(self):
        self.discard_backups()

    def refresh_absent(self, paths):
        for path in paths:
            if self.files.get(path) is None and os.path.lexists(path):
                self.files[path] = self.snapshot_file(path)

    def claim_created(self, paths):
        for path in paths:
            if self.files.get(path) is None and path.is_file() and not path.is_symlink():
                self.created_files[path] = self.file_state(path)

    def discard_backups(self):
        for record in self.files.values():
            if record:
                backup = record[1]
                if backup.exists() or backup.is_symlink():
                    backup.unlink()

    @classmethod
    def snapshot_file(cls, path):
        if not os.path.lexists(path):
            return None
        if path.is_symlink() or not path.is_file():
            raise ValueError(f"bootstrap path is not a regular file: {path}")
        state = cls.file_state(path)
        descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.codecraft-backup-", dir=path.parent)
        os.close(descriptor)
        os.unlink(temporary)
        os.link(path, temporary)
        return state, Path(temporary)

    def missing_directories(self, directories):
        missing = set()
        for directory in directories:
            current = directory
            while current != self.target and current.is_relative_to(self.target):
                if current.is_symlink() or (current.exists() and not current.is_dir()):
                    raise ValueError(f"bootstrap path is not a directory: {current.relative_to(self.target)}")
                if not current.exists():
                    missing.add(current)
                current = current.parent
        return missing

    @classmethod
    def matches(cls, path, expected):
        return path.is_file() and not path.is_symlink() and cls.file_state(path) == expected

    @staticmethod
    def file_state(path):
        status = path.stat()
        return path.read_bytes(), status.st_mode & 0o777, status.st_dev, status.st_ino


class BootstrapLock:
    def __init__(self, path):
        self.path = path
        self.identity = None

    def acquire(self):
        try:
            descriptor = os.open(self.path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        except FileExistsError as error:
            raise ValueError("another CodeCraft bootstrap is already active, or its lock is stale") from error
        with os.fdopen(descriptor, "w") as stream:
            stream.write(f"pid={os.getpid()}\n")
        status = self.path.stat()
        self.identity = status.st_dev, status.st_ino

    def release(self):
        if self.identity and self.path.is_file() and not self.path.is_symlink():
            status = self.path.stat()
            if (status.st_dev, status.st_ino) == self.identity:
                self.path.unlink()


class MavenBootstrap:
    BUILD_MARKERS = (
        "pom.xml",
        "mvnw",
        "mvnw.cmd",
        ".mvn",
        "build.gradle",
        "build.gradle.kts",
        "settings.gradle",
        "settings.gradle.kts",
        "gradlew",
        "gradlew.bat",
        "gradle",
        "target",
    )
    REQUIRED_EXECUTABLES = {
        "git": "Git (git)",
        "java": "Java (java)",
        "javac": "Java compiler (javac)",
        "mvn": "Maven (mvn)",
        "python3": "Python 3 (python3)",
    }
    WRAPPER_COMMAND = [
        "mvn",
        "-N",
        "org.apache.maven.plugins:maven-wrapper-plugin:3.3.4:wrapper",
        "-Dtype=only-script",
        "-Dmaven=3.9.12",
    ]
    WRAPPER_PROPERTIES = {
        "wrapperVersion": "3.3.4",
        "distributionType": "only-script",
        "distributionUrl": (
            "https://repo.maven.apache.org/maven2/org/apache/maven/apache-maven/"
            "3.9.12/apache-maven-3.9.12-bin.zip"
        ),
    }

    def __init__(self, distribution, *, health_checker, runner=subprocess.run, executable_finder=shutil.which):
        self.distribution = distribution
        self.health_checker = health_checker
        self.runner = runner
        self.executable_finder = executable_finder

    def run(
        self,
        target,
        project_name=None,
        group_id="com.example",
        artifact_id=None,
        java_version="21",
    ):
        target = Path(target).resolve()
        if not target.is_dir():
            raise ValueError("bootstrap target must be an existing directory")
        conflicts = [marker for marker in self.BUILD_MARKERS if os.path.lexists(target / marker)]
        if conflicts:
            raise ValueError("existing build detected: " + ", ".join(conflicts))
        self.reject_symlinked_paths(target)
        if (target / ".git").is_symlink():
            raise ValueError("unrecognized .git symlink exists in bootstrap target")
        missing = [label for executable, label in self.REQUIRED_EXECUTABLES.items() if not self.executable_finder(executable)]
        if missing:
            raise ValueError("missing prerequisite: " + ", ".join(missing))
        if sys.version_info < (3, 11):
            raise ValueError("Python 3.11 or newer is required")

        project_name = (project_name or target.name).strip()
        artifact_id = artifact_id or self.default_artifact_id(target.name)
        self.distribution.context(
            project_name,
            "./mvnw verify",
            "src/main/java",
            "src/test/java",
            java_version,
        )
        self.verify_java_release(java_version)
        git_root = self.git_root(target)
        if git_root and git_root != target:
            raise ValueError(f"bootstrap target is inside another Git repository: {git_root}")
        if git_root is None and os.path.lexists(target / ".git"):
            raise ValueError("unrecognized .git node exists in bootstrap target")

        project = MavenProjectDefinition(group_id, artifact_id, java_version)
        build_probe = target / "src/main/java/CodeCraftBootstrapProbe.java"
        if os.path.lexists(build_probe):
            raise ValueError("bootstrap compiler probe path already exists")
        installation_paths = self.installation_paths(target, project_name, java_version)
        git_key_path = self.distribution.installation_key_path(target) if git_root == target else None
        if git_key_path:
            installation_paths.append(git_key_path)
        owned_roots = [target / ".mvn", target / "target"]
        if git_root is None:
            owned_roots.append(target / ".git")
        created_directories = [
            target / "src/main/java",
            target / "src/test/java",
            *(path.parent for path in installation_paths if path.is_relative_to(target)),
        ]
        lock = BootstrapLock(target / ".codecraft-bootstrap.lock")
        lock.acquire()
        try:
            transaction = DirectoryTransaction(
                target,
                [target / "pom.xml", target / "mvnw", target / "mvnw.cmd", build_probe, *installation_paths],
                owned_roots,
                created_directories,
            )
        except BaseException:
            lock.release()
            raise
        try:
            if git_root is None:
                self.run_command(["git", "init", "--quiet"], target)
            self.distribution.atomic_write(
                target / "pom.xml",
                project.pom_xml().encode(),
                0o644,
            )
            transaction.claim_created([target / "pom.xml"])
            (target / "src/main/java").mkdir(parents=True, exist_ok=True)
            (target / "src/test/java").mkdir(parents=True, exist_ok=True)
            self.run_command(self.WRAPPER_COMMAND, target)
            self.validate_wrapper(target)
            transaction.claim_created([target / "mvnw", target / "mvnw.cmd"])
            self.distribution.atomic_write(
                build_probe,
                b"public final class CodeCraftBootstrapProbe {}\n",
                0o644,
            )
            transaction.claim_created([build_probe])
            self.run_command(["./mvnw", "verify"], target)
            build_probe.unlink()
            if (target / "target").is_dir():
                shutil.rmtree(target / "target")
            transaction.refresh_absent(installation_paths)
            self.distribution.install(target, project_name, java_version=java_version)
            transaction.claim_created(installation_paths)
            problems = self.health_checker(target)
            if problems:
                raise RuntimeError("CodeCraft doctor failed: " + "; ".join(problems))
        except BaseException:
            transaction.restore()
            raise
        finally:
            lock.release()
        transaction.commit()
        return (
            f"bootstrapped {project_name} and installed CodeCraft Starter {self.distribution.version}\n\n"
            "Next AI prompt:\n"
            "Read AGENTS.md and use the project-local CodeCraft workflow. "
            "Assess the next planned behavior, but do not implement until the required human checkpoint."
        )

    def run_command(self, command, target):
        try:
            return self.runner(
                command,
                cwd=target,
                check=True,
                capture_output=True,
                text=True,
            )
        except (OSError, subprocess.CalledProcessError) as error:
            output = getattr(error, "stdout", "") or ""
            stderr = getattr(error, "stderr", "") or ""
            detail = "\n".join(part.strip() for part in (output, stderr) if part.strip()) or str(error)
            raise RuntimeError(f"command failed: {shlex.join(command)}: {detail.strip()}") from error

    def verify_java_release(self, java_version):
        with tempfile.TemporaryDirectory(prefix="codecraft-javac-") as temporary:
            source = Path(temporary) / "CodeCraftBootstrapProbe.java"
            source.write_text("public final class CodeCraftBootstrapProbe {}\n")
            self.run_command(["javac", "--release", str(java_version), str(source)], Path(temporary))

    def installation_paths(self, target, project_name, java_version):
        context = self.distribution.context(
            project_name,
            "./mvnw verify",
            "src/main/java",
            "src/test/java",
            java_version,
        )
        context["TARGET"] = str(target)
        planned = self.distribution.rendered_files(context)
        paths = [path for group in planned.values() for path, _content, _mode in group]
        paths.extend(
            self.distribution.rendered_path(target, entry)
            for group in ("mergeBlocks", "appendLines")
            for entry in self.distribution.definition[group]
        )
        paths.append(target / ".codecraft/installation.json")
        return paths

    def validate_wrapper(self, target):
        properties_path = target / ".mvn/wrapper/maven-wrapper.properties"
        if not properties_path.is_file() or not (target / "mvnw").is_file():
            raise RuntimeError("Maven wrapper generation did not create the expected files")
        properties = dict(
            line.split("=", 1)
            for line in properties_path.read_text().splitlines()
            if line and not line.startswith("#") and "=" in line
        )
        if any(properties.get(key) != value for key, value in self.WRAPPER_PROPERTIES.items()):
            raise RuntimeError("Maven wrapper generation did not honor the pinned configuration")

    @staticmethod
    def git_root(target):
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--show-toplevel"],
                cwd=target,
                capture_output=True,
                text=True,
            )
        except OSError:
            return None
        return Path(result.stdout.strip()).resolve() if result.returncode == 0 else None

    @staticmethod
    def default_artifact_id(name):
        artifact_id = re.sub(r"[^a-z0-9._-]+", "-", name.lower()).strip(".-")
        if not artifact_id:
            raise ValueError("artifact id cannot be derived from the target directory")
        return artifact_id

    @staticmethod
    def reject_symlinked_paths(target):
        for relative in ("pom.xml", "mvnw", "mvnw.cmd", ".mvn", "src/main/java", "src/test/java"):
            current = target
            for part in Path(relative).parts:
                current = current / part
                if current.is_symlink():
                    raise ValueError(f"bootstrap path contains a symlink: {relative}")

class StarterDistribution:
    def __init__(self, package):
        self.package = Path(package).resolve()
        self.payload = self.package / "payload"
        self.version = (self.package / "VERSION").read_text().strip()
        self.definition = json.loads((self.payload / "manifest.json").read_text())

    def install(
        self,
        target,
        project_name,
        verify_command="./mvnw verify",
        source_root="src/main/java",
        test_root="src/test/java",
        java_version="21",
    ):
        target = Path(target).resolve()
        self.validate_target(target)
        problems = self.package_problems()
        if problems:
            raise ValueError("invalid CodeCraft package: " + "; ".join(problems))
        installation_path = target / ".codecraft/installation.json"
        if installation_path.exists():
            installation = json.loads(installation_path.read_text())
            if installation["version"] == self.version:
                if installation.get("distributionDigest") != self.distribution_digest():
                    raise ValueError(f"CodeCraft Starter {self.version} version content changed")
                self.upgrade(target)
                return f"CodeCraft Starter {self.version} is already installed"
            return self.upgrade(target)
        context = self.context(project_name, verify_command, source_root, test_root, java_version)
        context["TARGET"] = str(target)
        planned = self.rendered_files(context)
        conflicts = [path for path, content, _mode in planned["managed"] if path.exists() and path.read_bytes() != content]
        if conflicts:
            raise ValueError("existing-file conflict: " + ", ".join(str(path.relative_to(target)) for path in conflicts))
        project_conflicts = [
            path for path, content, _mode in planned["projectOwned"] if path.exists() and path.read_bytes() != content
        ]
        if project_conflicts:
            raise ValueError(
                "project-owned adoption requires manual reconciliation: "
                + ", ".join(str(path.relative_to(target)) for path in project_conflicts)
            )
        block_updates = self.plan_blocks(target, context, None)
        transaction = self.transaction_paths(target, planned, block_updates)
        snapshots = self.snapshot(transaction)
        try:
            self.write_files(planned["managed"])
            self.write_missing(planned["projectOwned"])
            self.enroll_existing_behavior_assets(target, context)
            self.write_blocks(block_updates)
            self.append_lines(target)
            self.write_installation(target, context, planned, block_updates)
        except Exception:
            self.restore(snapshots)
            raise
        return f"installed CodeCraft Starter {self.version}"

    def upgrade(self, target):
        target = Path(target).resolve()
        self.validate_target(target)
        problems = self.package_problems()
        if problems:
            raise ValueError("invalid CodeCraft package: " + "; ".join(problems))
        installation_path = target / ".codecraft/installation.json"
        if not installation_path.exists():
            raise ValueError("CodeCraft Starter is not installed")
        installation = json.loads(installation_path.read_text())
        self.validate_installation(target, installation)
        installed_version = self.semantic_version(installation["version"])
        package_version = self.semantic_version(self.version)
        if package_version < installed_version:
            raise ValueError(f"CodeCraft Starter downgrade is not allowed: {installation['version']} to {self.version}")
        if package_version == installed_version and installation.get("distributionDigest") != self.distribution_digest():
            raise ValueError(f"CodeCraft Starter {self.version} version content changed")
        context = {**installation["context"], "TARGET": str(target)}
        planned = self.rendered_files(context)
        conflicts = []
        planned_paths = {path.relative_to(target).as_posix() for path, _content, _mode in planned["managed"]}
        removed = sorted(set(installation["managed"]) - planned_paths)
        removal_paths = self.planned_removals(target, installation, removed)
        for path, content, _mode in planned["managed"]:
            relative = path.relative_to(target).as_posix()
            previous = installation["managed"].get(relative)
            if path.exists() and previous and self.digest(path.read_bytes()) not in {previous, self.digest(content)}:
                conflicts.append(relative)
            elif path.exists() and not previous and path.read_bytes() != content:
                conflicts.append(relative)
        block_updates = self.plan_blocks(target, context, installation)
        if conflicts:
            raise ValueError("managed-file conflict: " + ", ".join(conflicts))
        transaction = self.transaction_paths(target, planned, block_updates) + removal_paths
        snapshots = self.snapshot(transaction)
        try:
            for path in removal_paths:
                path.unlink()
            self.write_files(planned["managed"])
            self.write_missing(planned["projectOwned"])
            self.enroll_existing_behavior_assets(target, context)
            self.write_blocks(block_updates)
            self.append_lines(target)
            self.write_installation(target, context, planned, block_updates)
        except Exception:
            self.restore(snapshots)
            raise
        return f"CodeCraft Starter {self.version} is current"

    def context(self, project_name, verify_command, source_root, test_root, java_version):
        command = shlex.split(verify_command)
        if not command:
            raise ValueError("verification command is empty")
        project_name = project_name.strip()
        if not project_name:
            raise ValueError("project name is empty")
        if any(character in project_name for character in ("\n", "\r", "\0")) or "{{" in project_name:
            raise ValueError("project name must be a single literal line")
        if any(character in verify_command for character in ("\n", "\r", "\0")) or "{{" in verify_command:
            raise ValueError("verification command must be a single literal line")
        java_version = str(java_version)
        if not re.fullmatch(r"[1-9]\d*", java_version):
            raise ValueError("Java version must be a positive integer")
        source_root = self.project_path(source_root)
        test_root = self.project_path(test_root)
        return {
            "PROJECT_NAME": project_name,
            "PROJECT_NAME_JSON": json.dumps(project_name),
            "VERIFY_COMMAND_JSON": json.dumps(command),
            "VERIFY_COMMAND_SHELL": shlex.join(command),
            "SOURCE_ROOT": source_root,
            "SOURCE_ROOT_JSON": json.dumps(source_root),
            "TEST_ROOT": test_root,
            "TEST_ROOT_JSON": json.dumps(test_root),
            "BDD_PATTERN": "*_bdd.java",
            "PLAN_PATH": "emergent/design/development-plan.md",
            "RESPONSIBILITY_MAP_PATH": "emergent/design/responsibility-map.md",
            "JAVA_VERSION": java_version,
        }

    @staticmethod
    def validate_target(target):
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"], cwd=target, capture_output=True, text=True
        ) if target.is_dir() else None
        if result is None or result.returncode != 0 or Path(result.stdout.strip()).resolve() != target:
            raise ValueError("target must be an existing Git repository")

    @staticmethod
    def project_path(value):
        candidate = PurePosixPath(str(value).strip())
        if (
            candidate.is_absolute()
            or ".." in candidate.parts
            or str(candidate) in {"", "."}
            or not re.fullmatch(r"[A-Za-z0-9._/-]+", candidate.as_posix())
        ):
            raise ValueError(f"project path must be repository-relative: {value}")
        return candidate.as_posix()

    @staticmethod
    def semantic_version(value):
        if not re.fullmatch(r"\d+\.\d+\.\d+", value):
            raise ValueError(f"invalid semantic version: {value}")
        return tuple(int(part) for part in value.split("."))

    def distribution_digest(self):
        digest = hashlib.sha256()
        paths = [
            path
            for path in self.package.rglob("*")
            if path.is_file() and "__pycache__" not in path.parts and path.suffix != ".pyc"
        ]
        for path in sorted(paths):
            digest.update(path.relative_to(self.package).as_posix().encode() + b"\0")
            digest.update(oct(path.stat().st_mode & 0o777).encode() + b"\0")
            digest.update(path.read_bytes() + b"\0")
        return f"sha256:{digest.hexdigest()}"

    def package_problems(self):
        problems = []
        if not re.fullmatch(r"\d+\.\d+\.\d+", self.version):
            problems.append("VERSION is not semantic versioning")
        file_entries = [
            *(entry for group in ("managed", "projectOwned") for entry in self.definition.get(group, [])),
            *self.definition.get("mergeBlocks", []),
        ]
        entries = [*file_entries, *self.definition.get("appendLines", [])]
        targets = []
        allowed_tokens = set(self.context("Example", "./mvnw verify", "src/main/java", "src/test/java", "21"))
        for entry in entries:
            relative = PurePosixPath(*entry.get("targetParts", [entry.get("target", "")]))
            if relative.is_absolute() or ".." in relative.parts or str(relative) in {"", "."}:
                problems.append(f"payload target is unsafe: {relative}")
            targets.append(relative.as_posix())
            if entry not in file_entries:
                continue
            source = (self.payload / entry.get("source", "")).resolve()
            if not source.is_relative_to(self.payload.resolve()) or not source.is_file():
                problems.append(f"payload source is missing or unsafe: {entry.get('source', '')}")
                continue
            unknown = set(re.findall(r"\{\{([A-Z_]+)\}\}", source.read_text())) - allowed_tokens
            if unknown:
                problems.append(f"unknown template tokens in {entry['source']}: {', '.join(sorted(unknown))}")
        duplicates = sorted({target for target in targets if targets.count(target) > 1})
        if duplicates:
            problems.append("duplicate payload targets: " + ", ".join(duplicates))
        expected = {
            "VERSION",
            "README.md",
            "FORWARD-TEST.md",
            "bin/codecraft_starter.py",
            "profiles/java-maven/README.md",
            "tests/test_starter.py",
            "payload/manifest.json",
            *(f"payload/{entry['source']}" for entry in file_entries if entry.get("source")),
        }
        actual = {
            path.relative_to(self.package).as_posix()
            for path in self.package.rglob("*")
            if path.is_file()
        }
        unexpected = sorted(actual - expected)
        missing = sorted(expected - actual)
        if unexpected:
            problems.append("unexpected release files: " + ", ".join(unexpected))
        if missing:
            problems.append("missing release files: " + ", ".join(missing))
        sample = self.context("Example Project", "./mvnw verify", "src/main/java", "src/test/java", "21")
        sample["TARGET"] = "/tmp/example-project"
        for entry in file_entries:
            source = self.payload / entry.get("source", "")
            if not source.is_file():
                continue
            rendered = self.render(source.read_text(), sample)
            if re.search(r"\{\{[A-Z_]+\}\}", rendered):
                problems.append(f"unrendered template token in {entry['source']}")
                continue
            try:
                if source.suffix == ".json":
                    json.loads(rendered)
                elif source.suffix == ".toml":
                    tomllib.loads(rendered)
                elif source.suffix == ".xml":
                    ElementTree.fromstring(rendered)
            except (ValueError, tomllib.TOMLDecodeError, ElementTree.ParseError) as error:
                problems.append(f"invalid rendered {source.suffix} in {entry['source']}: {error}")
        return problems

    def planned_removals(self, target, installation, removed):
        if not removed:
            return []
        migration = next(
            (
                item
                for item in self.definition.get("migrations", [])
                if item.get("from") == installation["version"] and item.get("to") == self.version
            ),
            None,
        )
        allowed = set((migration or {}).get("removeManaged", []))
        if not set(removed).issubset(allowed):
            raise ValueError("managed-file removal requires an explicit migration: " + ", ".join(removed))
        paths = []
        for relative in removed:
            path = self.rendered_path(target, {"target": relative})
            expected = installation["managed"][relative]
            if path.is_file() and self.digest(path.read_bytes()) != expected:
                raise ValueError(f"managed-file conflict: {relative}")
            if path.exists():
                paths.append(path)
        return paths

    def plan_blocks(self, target, context, installation):
        updates = []
        for entry in self.definition["mergeBlocks"]:
            path = self.rendered_path(target, entry)
            body = self.render((self.payload / entry["source"]).read_text(), context).rstrip()
            begin = f"<!-- BEGIN {entry['name']} -->"
            end = f"<!-- END {entry['name']} -->"
            block = f"{begin}\n{body}\n{end}"
            current = path.read_text() if path.exists() else ""
            if begin in current:
                prefix, remainder = current.split(begin, 1)
                old_body, suffix = remainder.split(end, 1)
                old_block = f"{begin}{old_body}{end}"
                previous = (installation or {}).get("mergeBlocks", {}).get(entry["target"])
                if not installation and old_block != block:
                    raise ValueError(f"managed-block conflict: {entry['target']}")
                if previous and self.digest(old_block.encode()) not in {previous, self.digest(block.encode())}:
                    raise ValueError(f"managed-block conflict: {entry['target']}")
                updated = prefix.rstrip() + "\n\n" + block + suffix
            else:
                separator = "\n\n" if current.strip() else ""
                updated = current.rstrip() + separator + block + "\n"
            updates.append((path, updated, block))
        return updates

    def append_lines(self, target):
        for entry in self.definition["appendLines"]:
            path = self.rendered_path(target, entry)
            existing = path.read_text().splitlines() if path.exists() else []
            additions = [line for line in entry["lines"] if line not in existing]
            if additions:
                prefix = path.read_text().rstrip() + "\n" if path.exists() and path.read_text().strip() else ""
                self.atomic_write(path, (prefix + "\n".join(additions) + "\n").encode(), 0o644)

    def write_installation(self, target, context, planned, block_updates):
        installed_context = {**context, "TARGET": str(target)}
        installation = {
            "version": self.version,
            "distributionDigest": self.distribution_digest(),
            "profile": self.definition["profile"],
            "context": installed_context,
            "managed": {
                path.relative_to(target).as_posix(): self.digest(content)
                for path, content, _mode in planned["managed"]
            },
            "managedModes": {
                path.relative_to(target).as_posix(): mode
                for path, _content, mode in planned["managed"]
            },
            "projectOwned": [path.relative_to(target).as_posix() for path, _content, _mode in planned["projectOwned"]],
            "mergeBlocks": {
                path.relative_to(target).as_posix(): self.digest(block.encode())
                for path, _updated, block in block_updates
            },
            "mergeBlockNames": {
                entry["target"]: entry["name"] for entry in self.definition["mergeBlocks"]
            },
        }
        installation["signature"] = self.installation_signature(target, installation, create_key=True)
        path = target / ".codecraft/installation.json"
        self.atomic_write(path, (json.dumps(installation, indent=2, sort_keys=True) + "\n").encode(), 0o644)

    @staticmethod
    def installation_key_path(target):
        common = subprocess.run(
            ["git", "rev-parse", "--git-common-dir"],
            cwd=target,
            capture_output=True,
            check=True,
            text=True,
        ).stdout.strip()
        path = Path(common)
        return (path if path.is_absolute() else target / path).resolve() / "codecraft-installation-key"

    @classmethod
    def installation_key(cls, target, create=False):
        path = cls.installation_key_path(target)
        if create and not path.exists():
            descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            with os.fdopen(descriptor, "wb") as stream:
                stream.write(os.urandom(32))
        if not path.is_file():
            raise ValueError("CodeCraft installation signing key is missing")
        return path.read_bytes()

    @classmethod
    def installation_signature(cls, target, installation, create_key=False):
        unsigned = {key: value for key, value in installation.items() if key != "signature"}
        payload = json.dumps(unsigned, sort_keys=True, separators=(",", ":")).encode()
        return hmac.new(cls.installation_key(target, create_key), payload, hashlib.sha256).hexdigest()

    @classmethod
    def validate_installation(cls, target, installation):
        signature = installation.get("signature", "")
        if not signature or not hmac.compare_digest(signature, cls.installation_signature(target, installation)):
            raise ValueError("CodeCraft installation manifest signature is invalid")

    def transaction_paths(self, target, planned, block_updates):
        paths = [path for group in planned.values() for path, _content, _mode in group]
        paths.extend(path for path, _updated, _block in block_updates)
        paths.extend(self.rendered_path(target, entry) for entry in self.definition["appendLines"])
        paths.append(target / ".codecraft/installation.json")
        return sorted(set(paths))

    @staticmethod
    def snapshot(paths):
        return {
            path: (path.read_bytes(), path.stat().st_mode & 0o777) if path.is_file() else None
            for path in paths
        }

    @classmethod
    def restore(cls, snapshots):
        for path, previous in snapshots.items():
            if previous is None:
                if path.exists() or path.is_symlink():
                    path.unlink()
            else:
                cls.replace_bytes(path, *previous)

    def rendered_path(self, target, entry):
        target = Path(target).resolve()
        relative = Path(*entry.get("targetParts", [entry.get("target")]))
        if relative.is_absolute() or ".." in relative.parts:
            raise ValueError(f"package target escapes repository: {relative}")
        current = target
        for part in relative.parts:
            current = current / part
            if current.is_symlink():
                raise ValueError(f"package target contains a symlink: {relative}")
        candidate = (target / relative).resolve()
        if not candidate.is_relative_to(target):
            raise ValueError(f"package target escapes repository: {relative}")
        return candidate

    def rendered_files(self, context):
        target = Path(context.get("TARGET", "."))
        groups = {"managed": [], "projectOwned": []}
        for group in groups:
            for entry in self.definition[group]:
                path = self.rendered_path(target, entry)
                source = (self.payload / entry["source"]).resolve()
                if not source.is_relative_to(self.payload.resolve()):
                    raise ValueError(f"package source escapes payload: {entry['source']}")
                content = self.render(source.read_text(), context).encode()
                groups[group].append((path, content, 0o755 if entry.get("executable") else 0o644))
        return groups

    def enroll_existing_behavior_assets(self, target, context):
        registry = target / ".codecraft/protected-assets.json"
        registered = set(json.loads(registry.read_text())) if registry.exists() else set()
        patterns = context.get(
            "PROTECTED_PATTERNS",
            [context["BDD_PATTERN"], "**/*.approved.txt", "**/*.golden", "**/*.snap", "**/fixtures/**"],
        )
        if target.exists():
            registered.update(
                path.relative_to(target).as_posix()
                for path in target.rglob("*")
                if path.is_file()
                and any(
                    fnmatch.fnmatch(path.relative_to(target).as_posix(), pattern)
                    or fnmatch.fnmatch(path.name, pattern)
                    for pattern in patterns
                )
            )
        self.atomic_write(registry, (json.dumps(sorted(registered), indent=2) + "\n").encode(), 0o644)

    @staticmethod
    def render(content, context):
        return re.sub(r"\{\{([A-Z_]+)\}\}", lambda match: str(context.get(match.group(1), match.group(0))), content)

    @staticmethod
    def digest(content):
        return hashlib.sha256(content).hexdigest()

    def write_files(self, files):
        for path, content, mode in files:
            self.atomic_write(path, content, mode)

    def write_missing(self, files):
        for path, content, mode in files:
            if not path.exists():
                self.atomic_write(path, content, mode)

    def write_blocks(self, updates):
        for path, content, _block in updates:
            mode = path.stat().st_mode & 0o777 if path.exists() else 0o644
            self.atomic_write(path, content.encode(), mode)

    def atomic_write(self, path, content, mode):
        self.replace_bytes(path, content, mode)

    @staticmethod
    def replace_bytes(path, content, mode):
        path.parent.mkdir(parents=True, exist_ok=True)
        descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
        try:
            with os.fdopen(descriptor, "wb") as stream:
                stream.write(content)
            os.chmod(temporary, mode)
            os.replace(temporary, path)
        finally:
            if os.path.exists(temporary):
                os.unlink(temporary)


class Doctor:
    def __init__(self, target):
        self.target = Path(target).resolve()

    def problems(self):
        installation_path = self.target / ".codecraft/installation.json"
        if not installation_path.exists():
            return ["CodeCraft installation manifest is missing"]
        installation = json.loads(installation_path.read_text())
        problems = []
        try:
            StarterDistribution.validate_installation(self.target, installation)
        except (OSError, ValueError, subprocess.CalledProcessError) as error:
            problems.append(str(error))
        for relative, expected in installation["managed"].items():
            path = self.target / relative
            if not path.is_file():
                problems.append(f"managed file is missing: {relative}")
            elif StarterDistribution.digest(path.read_bytes()) != expected:
                problems.append(f"managed file has locally evolved: {relative}")
            elif (path.stat().st_mode & 0o777) != installation.get("managedModes", {}).get(relative, path.stat().st_mode & 0o777):
                problems.append(f"managed file mode changed: {relative}")
        for relative, expected in installation.get("mergeBlocks", {}).items():
            path = self.target / relative
            name = installation.get("mergeBlockNames", {}).get(relative)
            if not path.is_file() or not name:
                problems.append(f"managed block is missing: {relative}")
                continue
            begin = f"<!-- BEGIN {name} -->"
            end = f"<!-- END {name} -->"
            content = path.read_text()
            if content.count(begin) != 1 or content.count(end) != 1:
                problems.append(f"managed block is missing or duplicated: {relative}")
                continue
            body = content.split(begin, 1)[1].split(end, 1)[0]
            block = f"{begin}{body}{end}"
            if StarterDistribution.digest(block.encode()) != expected:
                problems.append(f"managed block has locally evolved: {relative}")
        for relative in installation.get("projectOwned", []):
            if not (self.target / relative).is_file():
                problems.append(f"project-owned file is missing: {relative}")
        project = self.target / ".codecraft/project.json"
        if not project.is_file():
            problems.append("project configuration is missing")
        else:
            configuration = json.loads(project.read_text())
            command = configuration.get("verifyCommand", [])
            if not command or not self.command_exists(command[0]):
                problems.append("verification command is unavailable")
        git = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=self.target, capture_output=True, text=True)
        if git.returncode != 0 or Path(git.stdout.strip()).resolve() != self.target:
            problems.append("target is not a Git repository")
        return problems

    def command_exists(self, executable):
        path = Path(executable)
        if path.is_absolute():
            return path.exists()
        if "/" in executable:
            return (self.target / path).exists()
        return any((Path(directory) / executable).exists() for directory in os.environ.get("PATH", "").split(os.pathsep))


def main():
    parser = argparse.ArgumentParser(description="Bootstrap, install, upgrade, or inspect CodeCraft Starter")
    parser.add_argument("command", choices=("bootstrap", "install", "upgrade", "doctor", "package-check"))
    parser.add_argument("--target", default=".")
    parser.add_argument("--project-name")
    parser.add_argument("--group-id", default="com.example")
    parser.add_argument("--artifact-id")
    parser.add_argument("--verify-command", default="./mvnw verify")
    parser.add_argument("--source-root", default="src/main/java")
    parser.add_argument("--test-root", default="src/test/java")
    parser.add_argument("--java-version", default="21")
    arguments = parser.parse_args()
    package = Path(__file__).parents[1]
    distribution = StarterDistribution(package)
    if arguments.command == "bootstrap":
        print(
            MavenBootstrap(distribution, health_checker=lambda target: Doctor(target).problems()).run(
                arguments.target,
                arguments.project_name,
                arguments.group_id,
                arguments.artifact_id,
                arguments.java_version,
            )
        )
    elif arguments.command == "install":
        if not arguments.project_name:
            parser.error("--project-name is required for install")
        print(distribution.install(arguments.target, arguments.project_name, arguments.verify_command, arguments.source_root, arguments.test_root, arguments.java_version))
    elif arguments.command == "upgrade":
        print(distribution.upgrade(arguments.target))
    elif arguments.command == "doctor":
        problems = Doctor(arguments.target).problems()
        print("CodeCraft doctor: healthy" if not problems else "\n".join(problems))
        raise SystemExit(1 if problems else 0)
    else:
        problems = distribution.package_problems()
        print("CodeCraft package: healthy" if not problems else "\n".join(problems))
        raise SystemExit(1 if problems else 0)


if __name__ == "__main__":
    try:
        main()
    except (RuntimeError, ValueError) as error:
        raise SystemExit(f"CodeCraft Starter: {error}") from error
