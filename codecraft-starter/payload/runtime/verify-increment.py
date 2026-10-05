#!/usr/bin/env python3
import argparse
import hashlib
import hmac
import json
import os
import shutil
import subprocess
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path, PurePosixPath


def repository_root(start):
    candidate = Path(start).resolve()
    return next((path for path in (candidate, *candidate.parents) if (path / ".git").exists()), candidate)


def git(repository, *arguments, text=True):
    return subprocess.run(["git", *arguments], cwd=repository, capture_output=True, check=True, text=text).stdout


def load_paths(path):
    values = []
    for raw in Path(path).read_text().splitlines():
        raw = raw.strip()
        if not raw or raw.startswith("#"):
            continue
        candidate = PurePosixPath(raw)
        if candidate.is_absolute() or ".." in candidate.parts or str(candidate) in {"", "."}:
            raise ValueError(f"path must be repository-relative: {raw}")
        values.append(candidate.as_posix())
    values = sorted(set(values))
    if not values:
        raise ValueError("path list is empty")
    return values


def mode_and_content(repository, path, source, reference=None):
    if source == "workspace":
        candidate = safe_path(repository, path)
        if candidate.is_symlink():
            raise ValueError(f"candidate path may not be a symlink: {path}")
        return ((candidate.stat().st_mode & 0o777), candidate.read_bytes()) if candidate.is_file() else (None, None)
    if source == "staged":
        content = subprocess.run(["git", "show", f":{path}"], cwd=repository, capture_output=True)
        listing = git(repository, "ls-files", "-s", "--", path).strip()
    else:
        content = subprocess.run(["git", "show", f"{reference}:{path}"], cwd=repository, capture_output=True)
        listing = git(repository, "ls-tree", reference, "--", path).strip()
    if content.returncode != 0 or not listing:
        return None, None
    git_mode = listing.split()[0]
    if git_mode == "120000":
        raise ValueError(f"candidate path may not be a symlink: {path}")
    return int(git_mode, 8) & 0o777, content.stdout


def safe_path(repository, relative):
    repository = Path(repository).resolve()
    path = repository
    for part in PurePosixPath(relative).parts:
        path = path / part
        if path.is_symlink():
            raise ValueError(f"path contains a symlink: {relative}")
    resolved = path.resolve()
    if not resolved.is_relative_to(repository):
        raise ValueError(f"path escapes repository: {relative}")
    return path


def digest_paths(repository, paths, source="workspace", reference=None):
    digest = hashlib.sha256()
    for path in paths:
        mode, content = mode_and_content(repository, path, source, reference)
        digest.update(path.encode() + b"\0")
        digest.update((b"deleted" if content is None else str(mode).encode()) + b"\0")
        if content is not None:
            digest.update(content)
        digest.update(b"\0")
    return f"sha256:{digest.hexdigest()}"


def ignored(path, repository):
    relative = path.relative_to(repository)
    ignored_parts = {".git", ".uv-cache", ".venv", "target", "__pycache__"}
    return any(part in ignored_parts for part in relative.parts) or relative.parts[:2] == (".codecraft", "state")


def fingerprint(repository, patterns):
    repository = Path(repository).resolve()
    digest = hashlib.sha256()
    required = {".codecraft/completion-lanes.json", ".codecraft/bin/verify_increment.py"}
    for pattern in sorted(set(patterns) | required):
        digest.update(pattern.encode() + b"\0")
        for path in sorted(repository.glob(pattern)):
            if path.is_symlink():
                raise ValueError(f"material input may not be a symlink: {path.relative_to(repository)}")
            if not path.is_file() or ignored(path.resolve(), repository):
                continue
            relative = path.relative_to(repository).as_posix()
            digest.update(relative.encode() + b"\0")
            digest.update(oct(path.stat().st_mode & 0o777).encode() + b"\0")
            digest.update(path.read_bytes() + b"\0")
    return f"sha256:{digest.hexdigest()}"


def key_path(repository):
    common = Path(git(repository, "rev-parse", "--git-common-dir").strip())
    common = common if common.is_absolute() else repository / common
    return common.resolve() / "codecraft-verification-key"


def repository_identity(repository):
    common = Path(git(repository, "rev-parse", "--git-common-dir").strip())
    common = common if common.is_absolute() else repository / common
    return f"sha256:{hashlib.sha256(str(common.resolve()).encode()).hexdigest()}"


def signing_key(repository):
    path = key_path(repository)
    if not path.exists():
        descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(os.urandom(32))
    return path.read_bytes()


def sign(repository, receipt):
    payload = json.dumps(receipt, sort_keys=True, separators=(",", ":")).encode()
    return hmac.new(signing_key(repository), payload, hashlib.sha256).hexdigest()


def receipt_path(repository, lane):
    return repository / ".codecraft/state" / f"{lane}-verification.json"


def load_configuration(repository):
    return json.loads((repository / ".codecraft/completion-lanes.json").read_text())


def overlay_candidate(repository, worktree, paths):
    for relative in paths:
        source = safe_path(repository, relative)
        target = safe_path(worktree, relative)
        if source.is_symlink():
            raise ValueError(f"candidate path may not be a symlink: {relative}")
        if source.is_file():
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target, follow_symlinks=False)
        elif target.exists() or target.is_symlink():
            target.unlink()


def overlay_source(repository, worktree, paths, source, reference=None):
    for relative in paths:
        mode, content = mode_and_content(repository, relative, source, reference)
        target = safe_path(worktree, relative)
        if content is None:
            if target.exists() or target.is_symlink():
                target.unlink()
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)
        os.chmod(target, mode)


def isolated_fingerprint(repository, base, paths, source, patterns, reference=None):
    temporary = tempfile.TemporaryDirectory(prefix="codecraft-fingerprint-")
    worktree = Path(temporary.name) / "repository"
    checkout = base
    try:
        subprocess.run(["git", "worktree", "add", "--detach", str(worktree), checkout], cwd=repository, check=True, capture_output=True)
        overlay_source(repository, worktree, paths, source, reference)
        return fingerprint(worktree, patterns)
    finally:
        if worktree.exists():
            subprocess.run(["git", "worktree", "remove", "--force", str(worktree)], cwd=repository, capture_output=True)
        temporary.cleanup()


def run_lane(repository, lane, candidate, configuration):
    settings = configuration["lanes"][lane]
    base_commit = git(repository, "rev-parse", "HEAD").strip()
    candidate_digest = digest_paths(repository, candidate)
    configuration_digest = f"sha256:{hashlib.sha256(json.dumps(configuration, sort_keys=True).encode()).hexdigest()}"
    temporary = tempfile.TemporaryDirectory(prefix="codecraft-candidate-")
    worktree = Path(temporary.name) / "repository"
    try:
        subprocess.run(["git", "worktree", "add", "--detach", str(worktree), base_commit], cwd=repository, check=True)
        overlay_candidate(repository, worktree, candidate)
        verified_fingerprint = fingerprint(worktree, settings["inputs"])
        for command in settings["commands"]:
            subprocess.run(command, cwd=worktree, check=True)
    finally:
        if worktree.exists():
            subprocess.run(["git", "worktree", "remove", "--force", str(worktree)], cwd=repository, capture_output=True)
        temporary.cleanup()
    if git(repository, "rev-parse", "HEAD").strip() != base_commit or digest_paths(repository, candidate) != candidate_digest:
        raise ValueError("candidate or base commit changed during verification")
    receipt = {
        "version": 1,
        "lane": lane,
        "verifiedAt": datetime.now(timezone.utc).isoformat(),
        "repository": repository_identity(repository),
        "baseCommit": base_commit,
        "paths": candidate,
        "candidateDigest": candidate_digest,
        "fingerprint": verified_fingerprint,
        "configurationDigest": configuration_digest,
        "commands": settings["commands"],
        "inputs": settings["inputs"],
    }
    receipt["signature"] = sign(repository, receipt)
    path = receipt_path(repository, lane)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(f"Verification receipt: {lane} {receipt['candidateDigest']}")


def valid_evidence(path, configuration):
    candidate = PurePosixPath(path)
    return path in configuration.get("evidencePaths", []) or (
        candidate.parent == PurePosixPath("emergent/features") and candidate.suffix == ".md"
    ) or (
        candidate.parent == PurePosixPath("automation") and candidate.name.endswith("-evidence.md")
    )


def validate_documentation_scope(paths):
    prose = {".md", ".rst", ".txt"}
    governing_prefixes = (".agents/", ".claude/", ".codecraft/", ".codex/", ".github/", "automation/")
    governing_names = {"AGENTS.md", "CLAUDE.md", "SKILL.md"}
    invalid = [
        path
        for path in paths
        if PurePosixPath(path).suffix.lower() not in prose
        or PurePosixPath(path).name in governing_names
        or path.startswith(governing_prefixes)
    ]
    if invalid:
        raise ValueError("documentation lane contains executable or governing paths: " + ", ".join(invalid))


def check_receipt(repository, lane, candidate, evidence, configuration, source, reference=None):
    path = receipt_path(repository, lane)
    if not path.exists():
        raise ValueError("verification receipt is missing")
    receipt = json.loads(path.read_text())
    signature = receipt.pop("signature", "")
    if not signature or not hmac.compare_digest(signature, sign(repository, receipt)):
        raise ValueError("verification receipt signature is invalid")
    receipt["signature"] = signature
    settings = configuration["lanes"][lane]
    configuration_digest = f"sha256:{hashlib.sha256(json.dumps(configuration, sort_keys=True).encode()).hexdigest()}"
    if (
        receipt.get("version") != 1
        or receipt.get("lane") != lane
        or receipt.get("repository") != repository_identity(repository)
        or receipt.get("commands") != settings["commands"]
        or receipt.get("inputs") != settings["inputs"]
        or receipt.get("configurationDigest") != configuration_digest
    ):
        raise ValueError("verification receipt contract differs from current configuration")
    age = datetime.now(timezone.utc) - datetime.fromisoformat(receipt["verifiedAt"])
    if age > timedelta(minutes=configuration["receiptMaxAgeMinutes"]):
        raise ValueError("verification receipt has expired")
    expected_base = git(repository, "rev-parse", "HEAD" if source == "staged" else f"{reference}^").strip()
    if receipt["baseCommit"] != expected_base or receipt["paths"] != candidate:
        raise ValueError("verification receipt belongs to another candidate")
    if receipt["candidateDigest"] != digest_paths(repository, candidate, source, reference):
        raise ValueError("candidate content differs from verification receipt")
    current_fingerprint = isolated_fingerprint(
        repository,
        receipt["baseCommit"],
        candidate,
        source,
        settings["inputs"],
        reference,
    )
    if receipt["fingerprint"] != current_fingerprint:
        raise ValueError("material verification inputs changed")
    if any(not valid_evidence(item, configuration) for item in evidence):
        raise ValueError("unsupported evidence-only path")
    if source == "committed":
        committed = sorted(filter(None, git(repository, "diff-tree", "--no-commit-id", "--name-only", "-r", reference).splitlines()))
        if committed != sorted(candidate + evidence):
            raise ValueError("commit paths differ from candidate plus evidence")
    print("verification receipt is current")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("lane")
    parser.add_argument("--candidate-file", required=True)
    parser.add_argument("--evidence-file")
    parser.add_argument("--check", action="store_true")
    check = parser.add_mutually_exclusive_group()
    check.add_argument("--staged", action="store_true")
    check.add_argument("--check-commit")
    arguments = parser.parse_args()
    repository = repository_root(Path.cwd())
    configuration = load_configuration(repository)
    if arguments.lane not in configuration["lanes"]:
        parser.error(f"unknown lane: {arguments.lane}")
    candidate = load_paths(arguments.candidate_file)
    evidence = load_paths(arguments.evidence_file) if arguments.evidence_file else []
    if arguments.lane == "documentation":
        validate_documentation_scope(candidate)
    if arguments.check:
        if arguments.check_commit:
            check_receipt(repository, arguments.lane, candidate, evidence, configuration, "committed", arguments.check_commit)
        elif arguments.staged:
            check_receipt(repository, arguments.lane, candidate, evidence, configuration, "staged")
        else:
            parser.error("--check requires --staged or --check-commit")
    else:
        if arguments.staged or arguments.check_commit:
            parser.error("--staged and --check-commit require --check")
        run_lane(repository, arguments.lane, candidate, configuration)


if __name__ == "__main__":
    main()
