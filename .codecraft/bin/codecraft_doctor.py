#!/usr/bin/env python3
import hashlib
import hmac
import json
import os
import subprocess
import sys
from pathlib import Path


def repository_root(start):
    candidate = Path(start).resolve()
    return next((path for path in (candidate, *candidate.parents) if (path / ".git").exists()), candidate)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def installation_signature(repository, installation):
    common = subprocess.run(
        ["git", "rev-parse", "--git-common-dir"],
        cwd=repository,
        capture_output=True,
        check=True,
        text=True,
    ).stdout.strip()
    common = Path(common) if Path(common).is_absolute() else repository / common
    key = (common.resolve() / "codecraft-installation-key").read_bytes()
    unsigned = {name: value for name, value in installation.items() if name != "signature"}
    payload = json.dumps(unsigned, sort_keys=True, separators=(",", ":")).encode()
    return hmac.new(key, payload, hashlib.sha256).hexdigest()


def command_exists(repository, executable):
    path = Path(executable)
    if path.is_absolute():
        return path.exists()
    if "/" in executable:
        return (repository / path).exists()
    return any((Path(directory) / executable).exists() for directory in os.environ.get("PATH", "").split(os.pathsep))


def problems(repository):
    installation_path = repository / ".codecraft/installation.json"
    if not installation_path.exists():
        return ["CodeCraft installation manifest is missing"]
    installation = json.loads(installation_path.read_text())
    found = []
    try:
        signature = installation.get("signature", "")
        if not signature or not hmac.compare_digest(signature, installation_signature(repository, installation)):
            found.append("CodeCraft installation manifest signature is invalid")
    except (OSError, subprocess.CalledProcessError):
        found.append("CodeCraft installation signing key is missing")
    for relative, expected in installation["managed"].items():
        path = repository / relative
        if not path.is_file():
            found.append(f"managed file is missing: {relative}")
        elif digest(path) != expected:
            found.append(f"managed file has locally evolved: {relative}")
        elif (path.stat().st_mode & 0o777) != installation.get("managedModes", {}).get(relative, path.stat().st_mode & 0o777):
            found.append(f"managed file mode changed: {relative}")
    for relative, expected in installation.get("mergeBlocks", {}).items():
        path = repository / relative
        name = installation.get("mergeBlockNames", {}).get(relative)
        if not path.is_file() or not name:
            found.append(f"managed block is missing: {relative}")
            continue
        begin = f"<!-- BEGIN {name} -->"
        end = f"<!-- END {name} -->"
        content = path.read_text()
        if content.count(begin) != 1 or content.count(end) != 1:
            found.append(f"managed block is missing or duplicated: {relative}")
            continue
        body = content.split(begin, 1)[1].split(end, 1)[0]
        if hashlib.sha256(f"{begin}{body}{end}".encode()).hexdigest() != expected:
            found.append(f"managed block has locally evolved: {relative}")
    for relative in installation.get("projectOwned", []):
        if not (repository / relative).is_file():
            found.append(f"project-owned file is missing: {relative}")
    project_path = repository / ".codecraft/project.json"
    if not project_path.is_file():
        found.append("project configuration is missing")
    else:
        project = json.loads(project_path.read_text())
        command = project.get("verifyCommand", [])
        if not command or not command_exists(repository, command[0]):
            found.append("verification command is unavailable")
        for key in ("projectName", "sourceRoot", "testRoot", "planPath", "responsibilityMapPath"):
            if not project.get(key):
                found.append(f"project configuration is missing {key}")
    git = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=repository, capture_output=True, text=True)
    if git.returncode != 0 or Path(git.stdout.strip()).resolve() != repository:
        found.append("repository is not a Git worktree")
    return found


def main():
    repository = repository_root(Path.cwd())
    found = problems(repository)
    if found:
        print("CodeCraft doctor found problems:")
        for problem in found:
            print(f"- {problem}")
        raise SystemExit(1)
    installation = json.loads((repository / ".codecraft/installation.json").read_text())
    print(f"CodeCraft Starter {installation['version']}: healthy")


if __name__ == "__main__":
    main()
