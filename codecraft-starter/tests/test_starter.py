import json
import os
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock
from xml.etree import ElementTree


PACKAGE = Path(__file__).parents[1]
sys.path.insert(0, str(PACKAGE / "bin"))

from codecraft_starter import DirectoryTransaction, Doctor, MavenBootstrap, StarterDistribution


class MavenBootstrapTest(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.target = Path(self.temporary_directory.name) / "new-project"
        self.target.mkdir()
        (self.target / "README.md").write_text("# Existing project note\n")
        self.commands = []
        self.distribution = StarterDistribution(PACKAGE)
        self.bootstrap = MavenBootstrap(
            self.distribution,
            health_checker=lambda target: Doctor(target).problems(),
            runner=self.run_command,
            executable_finder=lambda executable: f"/usr/bin/{executable}",
        )

    def tearDown(self):
        self.temporary_directory.cleanup()

    def run_command(self, command, cwd, **options):
        self.commands.append(command)
        if command[:2] == ["git", "init"]:
            return subprocess.run(command, cwd=cwd, **options)
        if command == MavenBootstrap.WRAPPER_COMMAND:
            wrapper = Path(cwd) / "mvnw"
            wrapper.write_text("#!/bin/sh\nexit 0\n")
            wrapper.chmod(0o755)
            windows_wrapper = Path(cwd) / "mvnw.cmd"
            windows_wrapper.write_text("@echo off\r\n")
            properties = Path(cwd) / ".mvn/wrapper/maven-wrapper.properties"
            properties.parent.mkdir(parents=True)
            properties.write_text(
                "wrapperVersion=3.3.4\n"
                "distributionType=only-script\n"
                "distributionUrl=https://repo.maven.apache.org/maven2/org/apache/maven/"
                "apache-maven/3.9.12/apache-maven-3.9.12-bin.zip\n"
            )
        return subprocess.CompletedProcess(command, 0, "", "")

    def test_should_bootstrap_a_buildless_directory_and_install_codecraft(self):
        result = self.bootstrap.run(
            self.target,
            project_name="Sample Service",
            group_id="org.example",
            artifact_id="sample-service",
            java_version="21",
        )

        namespace = {"maven": "http://maven.apache.org/POM/4.0.0"}
        project = ElementTree.parse(self.target / "pom.xml")
        self.assertEqual("org.example", project.findtext("maven:groupId", namespaces=namespace))
        self.assertEqual("sample-service", project.findtext("maven:artifactId", namespaces=namespace))
        self.assertEqual("21", project.findtext("maven:properties/maven:maven.compiler.release", namespaces=namespace))
        self.assertTrue((self.target / "src/main/java").is_dir())
        self.assertTrue((self.target / "src/test/java").is_dir())
        self.assertFalse((self.target / "src/main/java/CodeCraftBootstrapProbe.java").exists())
        self.assertFalse((self.target / "target").exists())
        self.assertTrue((self.target / "mvnw").stat().st_mode & stat.S_IXUSR)
        self.assertTrue((self.target / ".codecraft/installation.json").is_file())
        self.assertEqual([], Doctor(self.target).problems())
        self.assertEqual(["javac", "--release", "21"], self.commands[0][:3])
        self.assertEqual(
            [["git", "init", "--quiet"], MavenBootstrap.WRAPPER_COMMAND, ["./mvnw", "verify"]],
            self.commands[1:],
        )
        properties = (self.target / ".mvn/wrapper/maven-wrapper.properties").read_text()
        self.assertIn("wrapperVersion=3.3.4", properties)
        self.assertIn("apache-maven/3.9.12/apache-maven-3.9.12-bin.zip", properties)
        self.assertIn("Read AGENTS.md", result)
        self.assertEqual("# Existing project note\n", (self.target / "README.md").read_text())
        self.assertFalse((self.target / ".codecraft-bootstrap.lock").exists())

    def test_should_refuse_an_existing_build_without_mutating_the_directory(self):
        (self.target / "build.gradle.kts").write_text("plugins { java }\n")

        with self.assertRaisesRegex(ValueError, "existing build"):
            self.bootstrap.run(self.target, project_name="Sample Service")

        self.assertEqual([], self.commands)
        self.assertEqual("plugins { java }\n", (self.target / "build.gradle.kts").read_text())
        self.assertFalse((self.target / "pom.xml").exists())
        self.assertFalse((self.target / ".git").exists())

    def test_should_treat_a_broken_symlink_as_an_existing_build_marker(self):
        (self.target / "build.gradle").symlink_to(self.target / "missing-build.gradle")

        with self.assertRaisesRegex(ValueError, "existing build"):
            self.bootstrap.run(self.target, project_name="Sample Service")

        self.assertEqual([], self.commands)
        self.assertTrue((self.target / "build.gradle").is_symlink())

    def test_should_roll_back_every_created_artifact_when_verification_fails(self):
        def fail_verification(command, cwd, **options):
            result = self.run_command(command, cwd, **options)
            if command == ["./mvnw", "verify"]:
                self.assertTrue((Path(cwd) / "src/main/java/CodeCraftBootstrapProbe.java").is_file())
                raise subprocess.CalledProcessError(1, command, stderr="verification failed")
            return result

        bootstrap = MavenBootstrap(
            self.distribution,
            health_checker=lambda target: Doctor(target).problems(),
            runner=fail_verification,
            executable_finder=lambda executable: f"/usr/bin/{executable}",
        )

        with self.assertRaisesRegex(RuntimeError, "./mvnw verify"):
            bootstrap.run(self.target, project_name="Sample Service")

        self.assertEqual(["README.md"], sorted(path.name for path in self.target.iterdir()))
        self.assertEqual("# Existing project note\n", (self.target / "README.md").read_text())

    def test_should_refuse_an_overlapping_bootstrap_run(self):
        lock = self.target / ".codecraft-bootstrap.lock"
        lock.write_text("existing bootstrap\n")

        with self.assertRaisesRegex(ValueError, "already active"):
            self.bootstrap.run(self.target, project_name="Sample Service")

        self.assertEqual("existing bootstrap\n", lock.read_text())

    def test_should_roll_back_and_release_the_lock_when_interrupted(self):
        def interrupt_verification(command, cwd, **options):
            result = self.run_command(command, cwd, **options)
            if command == ["./mvnw", "verify"]:
                raise KeyboardInterrupt()
            return result

        bootstrap = MavenBootstrap(
            self.distribution,
            health_checker=lambda target: Doctor(target).problems(),
            runner=interrupt_verification,
            executable_finder=lambda executable: f"/usr/bin/{executable}",
        )

        with self.assertRaises(KeyboardInterrupt):
            bootstrap.run(self.target, project_name="Sample Service")

        self.assertEqual(["README.md"], sorted(path.name for path in self.target.iterdir()))
        self.assertFalse((self.target / ".codecraft-bootstrap.lock").exists())

    def test_should_release_the_lock_when_transaction_setup_is_interrupted(self):
        with mock.patch("codecraft_starter.DirectoryTransaction", side_effect=KeyboardInterrupt()):
            with self.assertRaises(KeyboardInterrupt):
                self.bootstrap.run(self.target, project_name="Sample Service")

        self.assertEqual(["README.md"], sorted(path.name for path in self.target.iterdir()))
        self.assertFalse((self.target / ".codecraft-bootstrap.lock").exists())

    def test_should_remove_backups_when_transaction_snapshot_is_interrupted(self):
        first = self.target / "first.txt"
        second = self.target / "second.txt"
        first.write_text("first\n")
        second.write_text("second\n")
        real_snapshot = DirectoryTransaction.snapshot_file
        calls = 0

        def interrupt_after_one_backup(path):
            nonlocal calls
            calls += 1
            if calls == 2:
                raise KeyboardInterrupt()
            return real_snapshot(path)

        with mock.patch.object(DirectoryTransaction, "snapshot_file", side_effect=interrupt_after_one_backup):
            with self.assertRaises(KeyboardInterrupt):
                DirectoryTransaction(self.target, [first, second], [], [])

        self.assertEqual([], list(self.target.glob(".*.codecraft-backup-*")))
        self.assertEqual("first\n", first.read_text())
        self.assertEqual("second\n", second.read_text())

    def test_should_preserve_unrelated_special_nodes_and_hard_links_during_rollback(self):
        fifo = self.target / "notifications.fifo"
        os.mkfifo(fifo)
        first_link = self.target / "first-note.txt"
        second_link = self.target / "second-note.txt"
        first_link.write_text("linked note\n")
        os.link(first_link, second_link)

        def fail_verification(command, cwd, **options):
            result = self.run_command(command, cwd, **options)
            if command == ["./mvnw", "verify"]:
                raise subprocess.CalledProcessError(1, command, stderr="verification failed")
            return result

        bootstrap = MavenBootstrap(
            self.distribution,
            health_checker=lambda target: Doctor(target).problems(),
            runner=fail_verification,
            executable_finder=lambda executable: f"/usr/bin/{executable}",
        )

        with self.assertRaisesRegex(RuntimeError, "./mvnw verify"):
            bootstrap.run(self.target, project_name="Sample Service")

        self.assertTrue(fifo.is_fifo())
        self.assertEqual(first_link.stat().st_ino, second_link.stat().st_ino)
        self.assertEqual("linked note\n", first_link.read_text())

    def test_should_preserve_a_tracked_file_created_concurrently_before_rollback(self):
        def create_ignore_then_fail(command, cwd, **options):
            result = self.run_command(command, cwd, **options)
            if command == MavenBootstrap.WRAPPER_COMMAND:
                (Path(cwd) / ".gitignore").write_text("concurrent addition\n")
            if command == ["./mvnw", "verify"]:
                raise subprocess.CalledProcessError(1, command, stderr="verification failed")
            return result

        bootstrap = MavenBootstrap(
            self.distribution,
            health_checker=lambda target: Doctor(target).problems(),
            runner=create_ignore_then_fail,
            executable_finder=lambda executable: f"/usr/bin/{executable}",
        )

        with self.assertRaisesRegex(RuntimeError, "./mvnw verify"):
            bootstrap.run(self.target, project_name="Sample Service")

        self.assertEqual("concurrent addition\n", (self.target / ".gitignore").read_text())

    def test_should_report_missing_prerequisites_before_mutating_the_directory(self):
        bootstrap = MavenBootstrap(
            self.distribution,
            health_checker=lambda target: Doctor(target).problems(),
            runner=self.run_command,
            executable_finder=lambda executable: None if executable == "mvn" else f"/usr/bin/{executable}",
        )

        with self.assertRaisesRegex(ValueError, "Maven.*mvn"):
            bootstrap.run(self.target, project_name="Sample Service")

        self.assertEqual([], self.commands)
        self.assertEqual(["README.md"], sorted(path.name for path in self.target.iterdir()))

    def test_should_probe_the_requested_java_release_before_mutating_the_directory(self):
        def reject_release(command, cwd, **options):
            self.commands.append(command)
            if command[:3] == ["javac", "--release", "999"]:
                raise subprocess.CalledProcessError(2, command, stderr="release version 999 not supported")
            return subprocess.CompletedProcess(command, 0, "", "")

        bootstrap = MavenBootstrap(
            self.distribution,
            health_checker=lambda target: Doctor(target).problems(),
            runner=reject_release,
            executable_finder=lambda executable: f"/usr/bin/{executable}",
        )

        with self.assertRaisesRegex(RuntimeError, "release version 999 not supported"):
            bootstrap.run(self.target, project_name="Sample Service", java_version="999")

        self.assertEqual(1, len(self.commands))
        self.assertEqual(["README.md"], sorted(path.name for path in self.target.iterdir()))

    def test_should_reject_a_symlinked_source_root_without_writing_outside_the_target(self):
        outside = Path(self.temporary_directory.name) / "outside"
        outside.mkdir()
        (self.target / "src").symlink_to(outside, target_is_directory=True)

        with self.assertRaisesRegex(ValueError, "symlink"):
            self.bootstrap.run(self.target, project_name="Sample Service")

        self.assertEqual([], list(outside.iterdir()))
        self.assertEqual([], self.commands)

    def test_should_refuse_unrecognized_git_nodes_without_writing_through_them(self):
        for kind in ("directory", "symlink", "broken-symlink"):
            with self.subTest(kind=kind):
                target = Path(self.temporary_directory.name) / f"git-{kind}"
                target.mkdir()
                outside = Path(self.temporary_directory.name) / f"outside-{kind}"
                if kind == "directory":
                    (target / ".git").mkdir()
                elif kind == "symlink":
                    outside.mkdir()
                    (target / ".git").symlink_to(outside, target_is_directory=True)
                else:
                    (target / ".git").symlink_to(outside, target_is_directory=True)

                with self.assertRaisesRegex(ValueError, "unrecognized .git"):
                    self.bootstrap.run(target, project_name="Sample Service")

                self.assertFalse((outside / "HEAD").exists())

    def test_should_roll_back_an_unhealthy_install_without_removing_an_existing_git_repository(self):
        subprocess.run(["git", "init", "--quiet"], cwd=self.target, check=True)
        ignore = self.target / ".gitignore"
        linked_ignore = self.target / "shared-ignore"
        ignore.write_text("existing-ignore\n")
        os.link(ignore, linked_ignore)
        bootstrap = MavenBootstrap(
            self.distribution,
            health_checker=lambda _target: ["injected health failure"],
            runner=self.run_command,
            executable_finder=lambda executable: f"/usr/bin/{executable}",
        )

        with self.assertRaisesRegex(RuntimeError, "injected health failure"):
            bootstrap.run(self.target, project_name="Sample Service")

        self.assertTrue((self.target / ".git").is_dir())
        self.assertFalse((self.target / ".git/codecraft-installation-key").exists())
        self.assertEqual(ignore.stat().st_ino, linked_ignore.stat().st_ino)
        self.assertEqual("existing-ignore\n", ignore.read_text())
        self.assertEqual(
            [".git", ".gitignore", "README.md", "shared-ignore"],
            sorted(path.name for path in self.target.iterdir()),
        )

    def test_should_support_the_documented_cli_with_defaults(self):
        tools = Path(self.temporary_directory.name) / "tools"
        tools.mkdir()
        javac = tools / "javac"
        javac.write_text("#!/bin/sh\nexit 0\n")
        javac.chmod(0o755)
        maven = tools / "mvn"
        maven.write_text(
            "#!/usr/bin/env python3\n"
            "from pathlib import Path\n"
            "wrapper = Path('mvnw')\n"
            "wrapper.write_text('#!/bin/sh\\nexit 0\\n')\n"
            "wrapper.chmod(0o755)\n"
            "Path('mvnw.cmd').write_text('@echo off\\r\\n')\n"
            "properties = Path('.mvn/wrapper/maven-wrapper.properties')\n"
            "properties.parent.mkdir(parents=True)\n"
            "properties.write_text('wrapperVersion=3.3.4\\ndistributionType=only-script\\n' "
            "+ 'distributionUrl=https://repo.maven.apache.org/maven2/org/apache/maven/apache-maven/' "
            "+ '3.9.12/apache-maven-3.9.12-bin.zip\\n')\n"
        )
        maven.chmod(0o755)
        environment = {**os.environ, "PATH": str(tools) + os.pathsep + os.environ["PATH"]}

        result = subprocess.run(
            [sys.executable, str(PACKAGE / "bin/codecraft_starter.py"), "bootstrap", "--target", str(self.target)],
            capture_output=True,
            text=True,
            env=environment,
        )

        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("bootstrapped new-project", result.stdout)
        project = ElementTree.parse(self.target / "pom.xml")
        namespace = {"maven": "http://maven.apache.org/POM/4.0.0"}
        self.assertEqual("com.example", project.findtext("maven:groupId", namespaces=namespace))
        self.assertEqual("new-project", project.findtext("maven:artifactId", namespaces=namespace))


class StarterDistributionTest(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.target = Path(self.temporary_directory.name) / "sample"
        self.target.mkdir()
        subprocess.run(["git", "init", "--quiet"], cwd=self.target, check=True)
        wrapper = self.target / "mvnw"
        wrapper.write_text("#!/bin/sh\nexit 0\n")
        wrapper.chmod(wrapper.stat().st_mode | stat.S_IXUSR)
        (self.target / "AGENTS.md").write_text("# Existing project instructions\n")
        (self.target / ".gitignore").write_text("target/\n")
        self.distribution = StarterDistribution(PACKAGE)

    def tearDown(self):
        self.temporary_directory.cleanup()

    def test_should_install_a_self_contained_java_maven_workflow(self):
        result = self.distribution.install(self.target, "Sample Service")

        self.assertEqual("installed CodeCraft Starter 0.5.2", result)
        self.assertTrue((self.target / ".agents/skills/codecraft/SKILL.md").is_file())
        self.assertTrue((self.target / ".agents/skills/committer/SKILL.md").is_file())
        self.assertTrue((self.target / ".codecraft/bin/codecraft_doctor.py").is_file())
        self.assertTrue((self.target / ".codecraft/bin/verify_increment.py").is_file())
        self.assertTrue((self.target / ".codecraft/bin/commit_verified_increment.py").is_file())
        self.assertTrue((self.target / ".codecraft/bin/codecraft_run.py").is_file())
        self.assertTrue((self.target / ".codecraft/hooks/protect_assets.py").is_file())
        self.assertTrue((self.target / ".codex" / "hooks.json").is_file())
        self.assertTrue((self.target / ".claude/rules/codecraft.md").is_file())
        self.assertIn("🍀", (self.target / ".claude/rules/always.md").read_text())
        self.assertIn("Sample Service", (self.target / "automation/codecraft-working-agreement.md").read_text())
        self.assertIn("BEGIN CODECRAFT", (self.target / "AGENTS.md").read_text())
        self.assertIn(".claude/rules/always.md", (self.target / "AGENTS.md").read_text())
        self.assertIn(".codecraft/state/", (self.target / ".gitignore").read_text())
        installation = json.loads((self.target / ".codecraft/installation.json").read_text())
        self.assertEqual("0.5.2", installation["version"])
        self.assertEqual("java-maven", installation["profile"])
        self.assertEqual([], Doctor(self.target).problems())

    def test_should_be_idempotent_when_the_same_version_is_installed_again(self):
        self.distribution.install(self.target, "Sample Service")

        result = self.distribution.install(self.target, "Sample Service")

        self.assertEqual("CodeCraft Starter 0.5.2 is already installed", result)

    def test_should_preserve_project_owned_files_during_an_upgrade(self):
        self.distribution.install(self.target, "Sample Service")
        agreement = self.target / "automation/codecraft-working-agreement.md"
        agreement.write_text(agreement.read_text() + "\nLocal agreement.\n")
        review_ledger = self.target / "automation/review-decisions.json"
        review_ledger.write_text('[{"id":"local","decision":"defer"}]\n')
        conventions = self.target / ".claude/rules/always.md"
        conventions.write_text(conventions.read_text() + "\nLocal emoji convention.\n")

        result = self.distribution.upgrade(self.target)

        self.assertEqual("CodeCraft Starter 0.5.2 is current", result)
        self.assertIn("Local agreement.", agreement.read_text())
        self.assertIn('"local"', review_ledger.read_text())
        self.assertIn("Local emoji convention.", conventions.read_text())

    def test_should_manage_one_active_run_as_compact_resumable_context(self):
        self.distribution.install(self.target, "Sample Service")
        subprocess.run(["git", "config", "user.name", "CodeCraft Test"], cwd=self.target, check=True)
        subprocess.run(["git", "config", "user.email", "codecraft@example.invalid"], cwd=self.target, check=True)
        subprocess.run(["git", "add", "."], cwd=self.target, check=True)
        subprocess.run(["git", "commit", "--quiet", "-m", "baseline"], cwd=self.target, check=True)
        runner = self.target / ".codecraft/bin/codecraft_run.py"

        subprocess.run(
            [
                str(runner),
                "start",
                "sample-run",
                "--kind",
                "automation",
                "--objective",
                "Preserve compact workflow context",
                "--next-actor",
                "ai",
                "--next-action",
                "Implement the approved automation",
                "--context",
                "automation/codecraft-working-agreement.md",
            ],
            cwd=self.target,
            check=True,
            capture_output=True,
            text=True,
        )
        subprocess.run(
            [
                str(runner),
                "advance",
                "implementation",
                "--actor",
                "ai",
                "--next-action",
                "Run the focused test",
                "--command",
                "./mvnw test",
            ],
            cwd=self.target,
            check=True,
            capture_output=True,
            text=True,
        )
        resumed = subprocess.run(
            [str(runner), "resume"],
            cwd=self.target,
            check=True,
            capture_output=True,
            text=True,
        )

        self.assertIn("RUN: sample-run (automation)", resumed.stdout)
        self.assertIn("STAGE: implementation", resumed.stdout)
        self.assertIn("NEXT [ai]: Run the focused test", resumed.stdout)
        self.assertIn("COMMAND: ./mvnw test", resumed.stdout)
        self.assertTrue((self.target / ".codecraft/state/runs/sample-run.json").is_file())

    def test_should_refuse_to_overwrite_a_locally_changed_managed_file(self):
        self.distribution.install(self.target, "Sample Service")
        skill = self.target / ".agents/skills/codecraft/SKILL.md"
        skill.write_text(skill.read_text() + "\nLocal managed edit.\n")

        with self.assertRaisesRegex(ValueError, "managed-file conflict"):
            self.distribution.upgrade(self.target)

        self.assertIn("Local managed edit.", skill.read_text())

    def test_should_report_missing_commands_and_managed_files(self):
        self.distribution.install(self.target, "Sample Service")
        (self.target / "mvnw").unlink()
        (self.target / ".codecraft/bin/verify_increment.py").unlink()

        problems = Doctor(self.target).problems()

        self.assertTrue(any("verification command" in problem for problem in problems))
        self.assertTrue(any("verify_increment.py" in problem for problem in problems))

    def test_should_detect_tampered_installation_state(self):
        self.distribution.install(self.target, "Sample Service")
        manifest = self.target / ".codecraft/installation.json"
        installation = json.loads(manifest.read_text())
        installation["managed"]["invented.txt"] = "0" * 64
        manifest.write_text(json.dumps(installation))

        problems = Doctor(self.target).problems()

        self.assertTrue(any("signature is invalid" in problem for problem in problems))
        with self.assertRaisesRegex(ValueError, "signature is invalid"):
            self.distribution.upgrade(self.target)

    def test_should_refuse_an_existing_managed_file_without_partial_installation(self):
        skill = self.target / ".agents/skills/codecraft/SKILL.md"
        skill.parent.mkdir(parents=True)
        skill.write_text("existing\n")

        with self.assertRaisesRegex(ValueError, "existing-file conflict"):
            self.distribution.install(self.target, "Sample Service")

        self.assertEqual("existing\n", skill.read_text())
        self.assertFalse((self.target / ".codecraft/installation.json").exists())
        self.assertFalse((self.target / "automation/codecraft-working-agreement.md").exists())

    def test_should_roll_back_a_partially_applied_installation(self):
        original_agents = (self.target / "AGENTS.md").read_bytes()
        original_ignore = (self.target / ".gitignore").read_bytes()
        real_write = self.distribution.atomic_write
        calls = 0

        def fail_during_install(path, content, mode):
            nonlocal calls
            calls += 1
            if calls == 4:
                raise OSError("injected write failure")
            real_write(path, content, mode)

        with mock.patch.object(self.distribution, "atomic_write", side_effect=fail_during_install):
            with self.assertRaisesRegex(OSError, "injected write failure"):
                self.distribution.install(self.target, "Sample Service")

        self.assertEqual(original_agents, (self.target / "AGENTS.md").read_bytes())
        self.assertEqual(original_ignore, (self.target / ".gitignore").read_bytes())
        self.assertFalse((self.target / ".agents/skills/codecraft/SKILL.md").exists())
        self.assertFalse((self.target / ".codecraft/installation.json").exists())

    def test_should_validate_the_installed_skills(self):
        self.distribution.install(self.target, "Sample Service")
        installed_validator = self.target / ".codecraft/bin/validate_skill.py"

        codecraft = subprocess.run([str(installed_validator), str(self.target / ".agents/skills/codecraft")], check=True, capture_output=True, text=True)
        committer = subprocess.run([str(installed_validator), str(self.target / ".agents/skills/committer")], check=True, capture_output=True, text=True)

        self.assertIn("Skill is valid!", codecraft.stdout)
        self.assertIn("Skill is valid!", committer.stdout)

    def test_should_verify_and_bind_a_clean_room_increment_to_its_commit(self):
        self.distribution.install(self.target, "Sample Service")
        subprocess.run(["git", "config", "user.name", "CodeCraft Test"], cwd=self.target, check=True)
        subprocess.run(["git", "config", "user.email", "codecraft@example.invalid"], cwd=self.target, check=True)
        subprocess.run(["git", "add", "."], cwd=self.target, check=True)
        subprocess.run(["git", "commit", "--quiet", "-m", "baseline"], cwd=self.target, check=True)
        note = self.target / "notes.md"
        note.write_text("clean room\n")
        interaction_log = self.target / "automation/commit-interaction-evidence.md"
        interaction_log.parent.mkdir(parents=True, exist_ok=True)
        interaction_log.write_text("commit interaction evidence\n")
        candidate = self.target.parent / "candidate.paths"
        candidate.write_text("notes.md\n")
        evidence = self.target.parent / "evidence.paths"
        evidence.write_text("automation/commit-interaction-evidence.md\n")
        verifier = self.target / ".codecraft/bin/verify_increment.py"

        verification = subprocess.run(
            [str(verifier), "documentation", "--candidate-file", str(candidate)],
            cwd=self.target,
            capture_output=True,
            text=True,
        )
        self.assertEqual(0, verification.returncode, verification.stderr)
        subprocess.run(["git", "add", "notes.md", "automation/commit-interaction-evidence.md"], cwd=self.target, check=True)
        subprocess.run(
            [str(verifier), "documentation", "--candidate-file", str(candidate), "--evidence-file", str(evidence), "--check", "--staged"],
            cwd=self.target,
            check=True,
        )
        subprocess.run(["git", "commit", "--quiet", "-m", "d Add note", "--only", "--", "notes.md", "automation/commit-interaction-evidence.md"], cwd=self.target, check=True)
        result = subprocess.run(
            [str(verifier), "documentation", "--candidate-file", str(candidate), "--evidence-file", str(evidence), "--check", "--check-commit", "HEAD"],
            cwd=self.target,
            check=True,
            capture_output=True,
            text=True,
        )

        self.assertIn("verification receipt is current", result.stdout)

    def test_should_commit_one_receipt_bound_transaction_without_unrelated_work(self):
        self.distribution.install(self.target, "Sample Service")
        subprocess.run(["git", "config", "user.name", "CodeCraft Test"], cwd=self.target, check=True)
        subprocess.run(["git", "config", "user.email", "codecraft@example.invalid"], cwd=self.target, check=True)
        subprocess.run(["git", "add", "."], cwd=self.target, check=True)
        subprocess.run(["git", "commit", "--quiet", "-m", "baseline"], cwd=self.target, check=True)
        protected = "src/test/java/Combat_bdd.java"
        source = self.target / protected
        source.parent.mkdir(parents=True, exist_ok=True)
        source.write_text("class Combat_bdd {}\n")
        evidence_path = "automation/verified-commit-evidence.md"
        evidence = self.target / evidence_path
        evidence.write_text("verified transaction\n")
        candidate_manifest = Path(self.temporary_directory.name) / "candidate.paths"
        candidate_manifest.write_text(protected + "\n")
        evidence_manifest = Path(self.temporary_directory.name) / "evidence.paths"
        evidence_manifest.write_text(evidence_path + "\n")
        verifier = self.target / ".codecraft/bin/verify_increment.py"
        helper = self.target / ".codecraft/bin/commit_verified_increment.py"
        subprocess.run(
            [str(verifier), "behavior", "--candidate-file", str(candidate_manifest)],
            cwd=self.target,
            check=True,
            capture_output=True,
            text=True,
        )
        message = "F demonstrate verified commit transaction"
        common = [
            "behavior",
            "--candidate-file",
            str(candidate_manifest),
            "--evidence-file",
            str(evidence_manifest),
            "--message",
            message,
        ]
        prepared = subprocess.run(
            [str(helper), "prepare", *common],
            cwd=self.target,
            check=True,
            capture_output=True,
            text=True,
        )
        transaction = json.loads(prepared.stdout)["transaction"]
        evidence.write_text("changed after approval preparation\n")

        changed = subprocess.run(
            [str(helper), "execute", *common, "--transaction", transaction],
            cwd=self.target,
            capture_output=True,
            text=True,
        )

        self.assertNotEqual(0, changed.returncode)
        self.assertIn("transaction identity changed", changed.stderr)
        self.assertEqual("", subprocess.run(["git", "diff", "--cached", "--name-only"], cwd=self.target, check=True, capture_output=True, text=True).stdout)
        evidence.write_text("verified transaction\n")
        (self.target / "README.md").write_text("unrelated local work\n")

        committed = subprocess.run(
            [str(helper), "execute", *common, "--transaction", transaction],
            cwd=self.target,
            check=True,
            capture_output=True,
            text=True,
        )

        self.assertIn("verified transaction committed", committed.stdout)
        paths = subprocess.run(
            ["git", "diff-tree", "--no-commit-id", "--name-only", "-r", "HEAD"],
            cwd=self.target,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.splitlines()
        self.assertEqual(sorted([protected, evidence_path]), sorted(paths))
        self.assertEqual(message, subprocess.run(["git", "log", "-1", "--format=%s"], cwd=self.target, check=True, capture_output=True, text=True).stdout.strip())
        self.assertIn("README.md", subprocess.run(["git", "status", "--short"], cwd=self.target, check=True, capture_output=True, text=True).stdout)

        reused = subprocess.run(
            [str(helper), "execute", *common, "--transaction", transaction],
            cwd=self.target,
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(0, reused.returncode)

    def test_should_guard_one_verified_commit_execution_as_one_protected_operation(self):
        self.distribution.install(self.target, "Sample Service")
        protected = "src/test/java/Combat_bdd.java"
        source = self.target / protected
        source.parent.mkdir(parents=True, exist_ok=True)
        source.write_text("class Combat_bdd {}\n")
        (self.target / ".codecraft/protected-assets.json").write_text(json.dumps([protected]))
        candidate_manifest = Path(self.temporary_directory.name) / "candidate.paths"
        candidate_manifest.write_text(protected + "\n")
        helper = self.target / ".codecraft/bin/commit_verified_increment.py"
        guard = self.target / ".codecraft/hooks/protect_assets.py"
        command = (
            f"{helper} execute behavior --candidate-file {candidate_manifest} "
            "--message 'F demonstrate verified commit transaction' --transaction sha256:" + "0" * 64
        )
        event = {
            "hook_event_name": "PreToolUse",
            "tool_name": "Bash",
            "tool_input": {"command": command},
            "tool_use_id": "transaction-1",
            "session_id": "session-1",
            "cwd": str(self.target),
        }

        compound = self.run_guard(
            guard,
            {
                **event,
                "tool_input": {"command": command.replace(" execute ", " prepare ") + f"; rm {source}"},
                "tool_use_id": "transaction-compound",
            },
        )
        wrapped = self.run_guard(
            guard,
            {
                **event,
                "tool_input": {"command": "env " + command},
                "tool_use_id": "transaction-wrapped",
            },
        )
        denied = self.run_guard(guard, event)
        self.run_guard(
            guard,
            {"hook_event_name": "UserPromptSubmit", "prompt": "yes", "session_id": "session-1", "cwd": str(self.target)},
        )
        approved = self.run_guard(guard, event)
        denied_again = self.run_guard(guard, {**event, "tool_use_id": "transaction-2"})

        self.assertEqual("deny", denied["hookSpecificOutput"]["permissionDecision"])
        self.assertEqual("deny", compound["hookSpecificOutput"]["permissionDecision"])
        self.assertEqual("deny", wrapped["hookSpecificOutput"]["permissionDecision"])
        self.assertIn(protected, denied["hookSpecificOutput"]["permissionDecisionReason"])
        self.assertEqual({}, approved)
        self.assertEqual("deny", denied_again["hookSpecificOutput"]["permissionDecision"])

    def test_should_require_single_use_approval_for_an_existing_behavior_test(self):
        self.distribution.install(self.target, "Sample Service")
        protected = "src/test/java/Behavior_" + "bdd.java"
        source = self.target / protected
        source.parent.mkdir(parents=True, exist_ok=True)
        source.write_text("original\n")
        (self.target / ".codecraft/protected-assets.json").write_text(json.dumps([protected]))
        guard = self.target / ".codecraft/hooks/protect_assets.py"
        patch = "*** Begin Patch\n*** Update File: " + protected + "\n@@\n-original\n+changed\n*** End Patch"
        event = {
            "hook_event_name": "PreToolUse",
            "tool_name": "apply_patch",
            "tool_input": {"command": patch},
            "tool_use_id": "change-1",
            "cwd": str(self.target),
        }

        denied = self.run_guard(guard, event)
        self.run_guard(guard, {"hook_event_name": "UserPromptSubmit", "prompt": "a", "cwd": str(self.target)})
        approved = self.run_guard(guard, event)
        self.run_guard(guard, {**event, "hook_event_name": "PostToolUse"})
        denied_again = self.run_guard(guard, {**event, "tool_use_id": "change-2"})

        self.assertEqual("deny", denied["hookSpecificOutput"]["permissionDecision"])
        self.assertEqual({}, approved)
        self.assertEqual("deny", denied_again["hookSpecificOutput"]["permissionDecision"])

    def test_should_upgrade_unchanged_managed_files_and_preserve_project_evolution(self):
        self.distribution.install(self.target, "Sample Service")
        agreement = self.target / "automation/codecraft-working-agreement.md"
        agreement.write_text(agreement.read_text() + "\nProject evolution.\n")
        next_package = Path(self.temporary_directory.name) / "codecraft-starter-0.6.0"
        shutil.copytree(PACKAGE, next_package)
        (next_package / "VERSION").write_text("0.6.0\n")
        skill_source = next_package / "payload/agents/codecraft-skill.md"
        skill_source.write_text(skill_source.read_text() + "\nDistribution improvement.\n")

        result = StarterDistribution(next_package).upgrade(self.target)

        self.assertEqual("CodeCraft Starter 0.6.0 is current", result)
        self.assertIn("Distribution improvement.", (self.target / ".agents/skills/codecraft/SKILL.md").read_text())
        self.assertIn("Project evolution.", agreement.read_text())
        installation = json.loads((self.target / ".codecraft/installation.json").read_text())
        self.assertEqual("0.6.0", installation["version"])

    def test_should_apply_an_explicit_safe_managed_file_removal_migration(self):
        self.distribution.install(self.target, "Sample Service")
        next_package = Path(self.temporary_directory.name) / "codecraft-starter-0.6.0"
        shutil.copytree(PACKAGE, next_package)
        (next_package / "VERSION").write_text("0.6.0\n")
        manifest = next_package / "payload/manifest.json"
        definition = json.loads(manifest.read_text())
        removed_entry = definition["managed"].pop()
        definition["migrations"] = [
            {
                "from": "0.5.2",
                "to": "0.6.0",
                "removeManaged": [removed_entry["target"]],
            }
        ]
        manifest.write_text(json.dumps(definition))
        (next_package / "payload" / removed_entry["source"]).unlink()

        StarterDistribution(next_package).upgrade(self.target)

        self.assertFalse((self.target / removed_entry["target"]).exists())

    def test_should_reject_a_payload_target_outside_the_repository(self):
        unsafe_package = Path(self.temporary_directory.name) / "unsafe-package"
        shutil.copytree(PACKAGE, unsafe_package)
        manifest = unsafe_package / "payload/manifest.json"
        definition = json.loads(manifest.read_text())
        definition["managed"][0]["target"] = "../escape.md"
        manifest.write_text(json.dumps(definition))

        with self.assertRaisesRegex(ValueError, "target is unsafe"):
            StarterDistribution(unsafe_package).install(self.target, "Sample Service")

        self.assertFalse((self.target.parent / "escape.md").exists())

    def test_should_run_starter_tests_and_fingerprint_the_package_during_project_verification(self):
        repository = Path(__file__).parents[2]
        namespace = {"maven": "http://maven.apache.org/POM/4.0.0"}
        project = ElementTree.parse(repository / "java/pom.xml")
        executions = project.findall(".//maven:execution", namespace)
        identifiers = [execution.findtext("maven:id", namespaces=namespace) for execution in executions]
        lanes = json.loads((repository / ".codecraft/completion-lanes.json").read_text())

        self.assertIn("verify-codecraft-starter", identifiers)
        self.assertIn("codecraft-starter/**/*", lanes["lanes"]["automation"]["inputs"])

    def test_should_validate_the_distribution_manifest_and_payload(self):
        self.assertEqual([], self.distribution.package_problems())

    def test_should_reject_unexpected_release_artifacts(self):
        changed_package = Path(self.temporary_directory.name) / "changed-package"
        shutil.copytree(PACKAGE, changed_package)
        (changed_package / "unexpected.tmp").write_text("not part of the release\n")

        problems = StarterDistribution(changed_package).package_problems()

        self.assertTrue(any("unexpected release files" in problem for problem in problems))

    def test_should_reject_changed_distribution_content_under_the_same_version(self):
        self.distribution.install(self.target, "Sample Service")
        changed_package = Path(self.temporary_directory.name) / "changed-package"
        shutil.copytree(PACKAGE, changed_package)
        skill = changed_package / "payload/agents/codecraft-skill.md"
        skill.write_text(skill.read_text() + "\nUnversioned change.\n")

        with self.assertRaisesRegex(ValueError, "version content changed"):
            StarterDistribution(changed_package).install(self.target, "Sample Service")

    def test_should_reject_changed_installer_content_on_a_direct_same_version_upgrade(self):
        self.distribution.install(self.target, "Sample Service")
        changed_package = Path(self.temporary_directory.name) / "changed-package"
        shutil.copytree(PACKAGE, changed_package)
        installer = changed_package / "bin/codecraft_starter.py"
        installer.write_text(installer.read_text() + "\n# changed installer\n")

        with self.assertRaisesRegex(ValueError, "version content changed"):
            StarterDistribution(changed_package).upgrade(self.target)

    def test_should_reject_a_distribution_downgrade(self):
        newer_package = Path(self.temporary_directory.name) / "codecraft-starter-0.6.0"
        shutil.copytree(PACKAGE, newer_package)
        (newer_package / "VERSION").write_text("0.6.0\n")
        StarterDistribution(newer_package).install(self.target, "Sample Service")

        with self.assertRaisesRegex(ValueError, "downgrade"):
            self.distribution.upgrade(self.target)

    def test_should_upgrade_after_the_target_repository_moves(self):
        self.distribution.install(self.target, "Sample Service")
        moved = self.target.parent / "moved-sample"
        shutil.move(self.target, moved)

        result = self.distribution.upgrade(moved)

        self.assertEqual("CodeCraft Starter 0.5.2 is current", result)
        self.assertTrue((moved / ".agents/skills/codecraft/SKILL.md").is_file())

    def test_should_reject_non_repository_and_escaping_project_paths_before_writing(self):
        plain = Path(self.temporary_directory.name) / "plain"
        plain.mkdir()

        with self.assertRaisesRegex(ValueError, "Git repository"):
            self.distribution.install(plain, "Plain")
        with self.assertRaisesRegex(ValueError, "project path"):
            self.distribution.install(self.target, "Sample Service", test_root="../outside")

        self.assertFalse((plain / ".codecraft").exists())
        self.assertFalse((self.target / ".codecraft/installation.json").exists())

    def test_should_reject_symlinked_merge_and_append_targets_before_writing(self):
        outside_agents = self.target.parent / "outside-agents.md"
        outside_ignore = self.target.parent / "outside-ignore"
        outside_agents.write_text("outside agents\n")
        outside_ignore.write_text("outside ignore\n")
        (self.target / "AGENTS.md").unlink()
        (self.target / ".gitignore").unlink()
        (self.target / "AGENTS.md").symlink_to(outside_agents)
        (self.target / ".gitignore").symlink_to(outside_ignore)

        with self.assertRaisesRegex(ValueError, "symlink"):
            self.distribution.install(self.target, "Sample Service")

        self.assertEqual("outside agents\n", outside_agents.read_text())
        self.assertEqual("outside ignore\n", outside_ignore.read_text())
        self.assertFalse((self.target / ".codecraft/installation.json").exists())

    def test_should_refuse_to_adopt_an_unrecorded_managed_instruction_block(self):
        (self.target / "AGENTS.md").write_text(
            "<!-- BEGIN CODECRAFT -->\nLocal block\n<!-- END CODECRAFT -->\n"
        )

        with self.assertRaisesRegex(ValueError, "managed-block conflict"):
            self.distribution.install(self.target, "Sample Service")

        self.assertIn("Local block", (self.target / "AGENTS.md").read_text())

    def test_should_render_quoted_project_names_as_valid_json(self):
        self.distribution.install(self.target, 'A "Quoted" Service')

        project = json.loads((self.target / ".codecraft/project.json").read_text())

        self.assertEqual('A "Quoted" Service', project["projectName"])

    def test_should_validate_append_targets_as_part_of_package_integrity(self):
        unsafe_package = Path(self.temporary_directory.name) / "unsafe-append-package"
        shutil.copytree(PACKAGE, unsafe_package)
        manifest = unsafe_package / "payload/manifest.json"
        definition = json.loads(manifest.read_text())
        definition["appendLines"][0]["target"] = "../outside-ignore"
        manifest.write_text(json.dumps(definition))

        problems = StarterDistribution(unsafe_package).package_problems()

        self.assertTrue(any("target is unsafe" in problem for problem in problems))

    def test_should_protect_non_shell_write_tools(self):
        self.distribution.install(self.target, "Sample Service")
        protected = "src/test/java/Behavior_" + "bdd.java"
        source = self.target / protected
        source.parent.mkdir(parents=True, exist_ok=True)
        source.write_text("original\n")
        (self.target / ".codecraft/protected-assets.json").write_text(json.dumps([protected]))
        guard = self.target / ".codecraft/hooks/protect_assets.py"
        event = {
            "hook_event_name": "PreToolUse",
            "tool_name": "Write",
            "tool_input": {"file_path": str(source), "content": "changed\n"},
            "tool_use_id": "write-1",
            "cwd": str(self.target),
        }

        denied = self.run_guard(guard, event)

        self.assertEqual("deny", denied["hookSpecificOutput"]["permissionDecision"])

    def test_should_atomically_reserve_a_single_approval(self):
        self.distribution.install(self.target, "Sample Service")
        protected = "src/test/java/Behavior_" + "bdd.java"
        source = self.target / protected
        source.parent.mkdir(parents=True, exist_ok=True)
        source.write_text("original\n")
        (self.target / ".codecraft/protected-assets.json").write_text(json.dumps([protected]))
        guard = self.target / ".codecraft/hooks/protect_assets.py"
        patch = "*** Begin Patch\n*** Update File: " + protected + "\n@@\n-original\n+changed\n*** End Patch"
        event = {
            "hook_event_name": "PreToolUse",
            "tool_name": "apply_patch",
            "tool_input": {"command": patch},
            "tool_use_id": "change-1",
            "session_id": "session-1",
            "cwd": str(self.target),
        }
        self.run_guard(guard, event)
        self.run_guard(
            guard,
            {"hook_event_name": "UserPromptSubmit", "prompt": "approve", "session_id": "session-1", "cwd": str(self.target)},
        )

        first = self.run_guard(guard, event)
        second = self.run_guard(guard, {**event, "tool_use_id": "change-2"})

        self.assertEqual({}, first)
        self.assertEqual("deny", second["hookSpecificOutput"]["permissionDecision"])

    def test_should_not_reuse_an_approval_from_another_session(self):
        self.distribution.install(self.target, "Sample Service")
        protected = "src/test/java/Behavior_" + "bdd.java"
        source = self.target / protected
        source.parent.mkdir(parents=True, exist_ok=True)
        source.write_text("original\n")
        (self.target / ".codecraft/protected-assets.json").write_text(json.dumps([protected]))
        guard = self.target / ".codecraft/hooks/protect_assets.py"
        event = {
            "hook_event_name": "PreToolUse",
            "tool_name": "Write",
            "tool_input": {"file_path": str(source), "content": "changed\n"},
            "tool_use_id": "write-1",
            "session_id": "session-1",
            "cwd": str(self.target),
        }
        self.run_guard(guard, event)
        self.run_guard(
            guard,
            {"hook_event_name": "UserPromptSubmit", "prompt": "y", "session_id": "session-1", "cwd": str(self.target)},
        )

        denied = self.run_guard(guard, {**event, "session_id": "session-2"})

        self.assertEqual("deny", denied["hookSpecificOutput"]["permissionDecision"])

    def test_should_retain_approval_after_a_harmless_tool_failure(self):
        self.distribution.install(self.target, "Sample Service")
        protected = "src/test/java/Behavior_" + "bdd.java"
        source = self.target / protected
        source.parent.mkdir(parents=True, exist_ok=True)
        source.write_text("original\n")
        (self.target / ".codecraft/protected-assets.json").write_text(json.dumps([protected]))
        guard = self.target / ".codecraft/hooks/protect_assets.py"
        event = {
            "hook_event_name": "PreToolUse",
            "tool_name": "Write",
            "tool_input": {"file_path": str(source), "content": "changed\n"},
            "tool_use_id": "write-1",
            "session_id": "session-1",
            "cwd": str(self.target),
        }
        self.run_guard(guard, event)
        self.run_guard(
            guard,
            {"hook_event_name": "UserPromptSubmit", "prompt": "a", "session_id": "session-1", "cwd": str(self.target)},
        )
        self.run_guard(guard, event)
        self.run_guard(guard, {**event, "hook_event_name": "PostToolUse", "tool_response": {"success": False}})

        retry = self.run_guard(guard, {**event, "tool_use_id": "write-2"})

        self.assertEqual({}, retry)

    def test_should_detect_glob_and_dynamic_shell_targets(self):
        self.distribution.install(self.target, "Sample Service")
        protected = "src/test/java/Behavior_" + "bdd.java"
        source = self.target / protected
        source.parent.mkdir(parents=True, exist_ok=True)
        source.write_text("original\n")
        (self.target / ".codecraft/protected-assets.json").write_text(json.dumps([protected]))
        guard = self.target / ".codecraft/hooks/protect_assets.py"

        glob = self.run_guard(
            guard,
            {
                "hook_event_name": "PreToolUse",
                "tool_name": "Bash",
                "tool_input": {"command": "rm src/test/java/*_bdd.java"},
                "tool_use_id": "shell-1",
                "cwd": str(self.target),
            },
        )
        dynamic = self.run_guard(
            guard,
            {
                "hook_event_name": "PreToolUse",
                "tool_name": "Bash",
                "tool_input": {"command": "python3 -c 'mutate_a_computed_path()'"},
                "tool_use_id": "shell-2",
                "cwd": str(self.target),
            },
        )

        self.assertEqual("deny", glob["hookSpecificOutput"]["permissionDecision"])
        self.assertEqual("deny", dynamic["hookSpecificOutput"]["permissionDecision"])

    def test_should_enroll_existing_approval_companions(self):
        companion = self.target / "src/test/resources/combat.approved.txt"
        companion.parent.mkdir(parents=True, exist_ok=True)
        companion.write_text("approved output\n")

        self.distribution.install(self.target, "Sample Service")

        registered = json.loads((self.target / ".codecraft/protected-assets.json").read_text())
        self.assertIn("src/test/resources/combat.approved.txt", registered)

    def test_should_detect_a_missing_managed_instruction_block(self):
        self.distribution.install(self.target, "Sample Service")
        (self.target / "AGENTS.md").write_text("# Existing project instructions\n")

        problems = Doctor(self.target).problems()

        self.assertTrue(any("managed block" in problem for problem in problems))

    def test_should_not_issue_a_receipt_when_candidate_changes_during_verification(self):
        note = self.target / "notes.md"
        note.write_text("verified version\n")
        mutation = f"from pathlib import Path; Path({str(note)!r}).write_text('raced version\\n')"
        self.distribution.install(self.target, "Sample Service", verify_command=f"python3 -c {mutation!r}")
        subprocess.run(["git", "add", "."], cwd=self.target, check=True)
        subprocess.run(["git", "config", "user.name", "CodeCraft Test"], cwd=self.target, check=True)
        subprocess.run(["git", "config", "user.email", "codecraft@example.invalid"], cwd=self.target, check=True)
        subprocess.run(["git", "commit", "--quiet", "-m", "baseline"], cwd=self.target, check=True)
        note.write_text("verified version\n")
        candidate = self.target.parent / "candidate-race.paths"
        candidate.write_text("notes.md\n")
        verifier = self.target / ".codecraft/bin/verify_increment.py"

        result = subprocess.run(
            [str(verifier), "behavior", "--candidate-file", str(candidate)],
            cwd=self.target,
            capture_output=True,
            text=True,
        )

        self.assertNotEqual(0, result.returncode)
        self.assertFalse((self.target / ".codecraft/state/behavior-verification.json").exists())

    def test_should_reject_a_symlink_candidate_from_isolated_verification(self):
        self.distribution.install(self.target, "Sample Service", verify_command="true")
        subprocess.run(["git", "add", "."], cwd=self.target, check=True)
        subprocess.run(["git", "config", "user.name", "CodeCraft Test"], cwd=self.target, check=True)
        subprocess.run(["git", "config", "user.email", "codecraft@example.invalid"], cwd=self.target, check=True)
        subprocess.run(["git", "commit", "--quiet", "-m", "baseline"], cwd=self.target, check=True)
        outside = self.target.parent / "outside-note.md"
        outside.write_text("outside\n")
        (self.target / "notes.md").symlink_to(outside)
        candidate = self.target.parent / "candidate-symlink.paths"
        candidate.write_text("notes.md\n")
        verifier = self.target / ".codecraft/bin/verify_increment.py"

        result = subprocess.run(
            [str(verifier), "behavior", "--candidate-file", str(candidate)],
            cwd=self.target,
            capture_output=True,
            text=True,
        )

        self.assertNotEqual(0, result.returncode)

    def test_should_reject_governing_automation_from_the_documentation_lane(self):
        self.distribution.install(self.target, "Sample Service")
        governing = self.target / "automation/local-policy.md"
        governing.write_text("policy\n")
        candidate = self.target.parent / "governing.paths"
        candidate.write_text("automation/local-policy.md\n")
        verifier = self.target / ".codecraft/bin/verify_increment.py"

        result = subprocess.run(
            [str(verifier), "documentation", "--candidate-file", str(candidate)],
            cwd=self.target,
            capture_output=True,
            text=True,
        )

        self.assertNotEqual(0, result.returncode)
        self.assertIn("documentation lane", result.stderr)

    def run_guard(self, guard, event):
        result = subprocess.run(
            [sys.executable, str(guard)],
            input=json.dumps(event),
            cwd=self.target,
            capture_output=True,
            text=True,
            check=True,
        )
        return json.loads(result.stdout) if result.stdout else {}


if __name__ == "__main__":
    unittest.main()
