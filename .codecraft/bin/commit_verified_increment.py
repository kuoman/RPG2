#!/usr/bin/env python3
import argparse
import hashlib
import hmac
import json
import re
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path

from verify_increment import (
    check_receipt,
    digest_paths,
    git,
    load_configuration,
    load_paths,
    receipt_path,
    repository_identity,
    repository_root,
    sign,
    valid_evidence,
    validate_documentation_scope,
)


ARLO_MESSAGE = re.compile(r"^(?:F|B|r|R|t|d|e) [^\r\n]+$")
TRANSACTION = re.compile(r"^sha256:[0-9a-f]{64}$")


def configuration_digest(configuration):
    content = json.dumps(configuration, sort_keys=True).encode()
    return f"sha256:{hashlib.sha256(content).hexdigest()}"


def file_digest(path):
    return f"sha256:{hashlib.sha256(Path(path).read_bytes()).hexdigest()}"


def current_receipt(repository, lane, candidate, configuration):
    path = receipt_path(repository, lane)
    if not path.is_file():
        raise ValueError("verification receipt is missing")
    receipt = json.loads(path.read_text())
    unsigned = dict(receipt)
    signature = unsigned.pop("signature", "")
    if not signature or not hmac.compare_digest(signature, sign(repository, unsigned)):
        raise ValueError("verification receipt signature is invalid")
    settings = configuration["lanes"][lane]
    if (
        receipt.get("version") != 1
        or receipt.get("lane") != lane
        or receipt.get("repository") != repository_identity(repository)
        or receipt.get("commands") != settings["commands"]
        or receipt.get("inputs") != settings["inputs"]
        or receipt.get("configurationDigest") != configuration_digest(configuration)
    ):
        raise ValueError("verification receipt contract differs from current configuration")
    age = datetime.now(timezone.utc) - datetime.fromisoformat(receipt["verifiedAt"])
    if age > timedelta(minutes=configuration["receiptMaxAgeMinutes"]):
        raise ValueError("verification receipt has expired")
    head = git(repository, "rev-parse", "HEAD").strip()
    if receipt.get("baseCommit") != head or receipt.get("paths") != candidate:
        raise ValueError("verification receipt belongs to another candidate")
    if receipt.get("candidateDigest") != digest_paths(repository, candidate):
        raise ValueError("candidate content differs from verification receipt")
    return receipt, file_digest(path)


def transaction_spec(repository, lane, candidate_file, evidence_file, message):
    configuration = load_configuration(repository)
    if lane not in configuration["lanes"]:
        raise ValueError(f"unknown lane: {lane}")
    if not ARLO_MESSAGE.fullmatch(message):
        raise ValueError("commit message must be one line with an Arlo prefix")
    candidate = load_paths(candidate_file)
    evidence = load_paths(evidence_file) if evidence_file else []
    if set(candidate) & set(evidence):
        raise ValueError("candidate and evidence paths must be disjoint")
    unsupported = [path for path in evidence if not valid_evidence(path, configuration)]
    if unsupported:
        raise ValueError("unsupported evidence-only path: " + ", ".join(unsupported))
    if lane == "documentation":
        validate_documentation_scope(candidate)
    receipt, receipt_digest = current_receipt(repository, lane, candidate, configuration)
    paths = sorted(candidate + evidence)
    payload = {
        "version": 1,
        "repository": repository_identity(repository),
        "lane": lane,
        "baseCommit": receipt["baseCommit"],
        "receiptDigest": receipt_digest,
        "candidatePaths": candidate,
        "candidateDigest": receipt["candidateDigest"],
        "evidencePaths": evidence,
        "evidenceDigest": digest_paths(repository, evidence),
        "commitPaths": paths,
        "message": message,
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    payload["transaction"] = f"sha256:{hashlib.sha256(encoded).hexdigest()}"
    return payload


def stage(repository, paths):
    subprocess.run(["git", "add", "-A", "--", *paths], cwd=repository, check=True)
    staged = sorted(
        filter(
            None,
            git(repository, "diff", "--cached", "--name-only", "--diff-filter=ACDMRTUXB", "HEAD", "--", *paths).splitlines(),
        )
    )
    if staged != paths:
        raise ValueError("staged paths differ from the exact transaction paths")
    subprocess.run(["git", "diff", "--cached", "--check", "--", *paths], cwd=repository, check=True)


def execute(repository, arguments):
    if not TRANSACTION.fullmatch(arguments.transaction):
        raise ValueError("transaction must be a SHA-256 identity")
    spec = transaction_spec(
        repository,
        arguments.lane,
        arguments.candidate_file,
        arguments.evidence_file,
        arguments.message,
    )
    if not hmac.compare_digest(spec["transaction"], arguments.transaction):
        raise ValueError("transaction identity changed; prepare and approve a new transaction")
    stage(repository, spec["commitPaths"])
    candidate = spec["candidatePaths"]
    evidence = spec["evidencePaths"]
    configuration = load_configuration(repository)
    check_receipt(repository, arguments.lane, candidate, evidence, configuration, "staged")
    current = transaction_spec(
        repository,
        arguments.lane,
        arguments.candidate_file,
        arguments.evidence_file,
        arguments.message,
    )
    if not hmac.compare_digest(current["transaction"], arguments.transaction):
        raise ValueError("transaction identity changed after staging")
    subprocess.run(
        ["git", "commit", "--only", "-m", arguments.message, "--", *spec["commitPaths"]],
        cwd=repository,
        check=True,
    )
    check_receipt(repository, arguments.lane, candidate, evidence, configuration, "committed", "HEAD")
    if digest_paths(repository, evidence, "committed", "HEAD") != spec["evidenceDigest"]:
        raise ValueError("committed evidence differs from the approved transaction")
    committed_message = git(repository, "log", "-1", "--format=%B").strip()
    if committed_message != arguments.message:
        raise ValueError("committed message differs from the approved transaction")
    print(f"verified transaction committed: {git(repository, 'rev-parse', 'HEAD').strip()}")


def add_common_arguments(command):
    command.add_argument("lane")
    command.add_argument("--candidate-file", required=True)
    command.add_argument("--evidence-file")
    command.add_argument("--message", required=True)


def main():
    parser = argparse.ArgumentParser(description="Prepare or execute one exact verified CodeCraft commit transaction")
    commands = parser.add_subparsers(dest="operation", required=True)
    prepare = commands.add_parser("prepare")
    add_common_arguments(prepare)
    execute_command = commands.add_parser("execute")
    add_common_arguments(execute_command)
    execute_command.add_argument("--transaction", required=True)
    arguments = parser.parse_args()
    repository = repository_root(Path.cwd())
    try:
        if arguments.operation == "prepare":
            print(json.dumps(transaction_spec(repository, arguments.lane, arguments.candidate_file, arguments.evidence_file, arguments.message), indent=2))
        else:
            execute(repository, arguments)
    except (ValueError, OSError, subprocess.CalledProcessError, json.JSONDecodeError) as error:
        parser.exit(1, f"verified commit transaction failed: {error}\n")


if __name__ == "__main__":
    main()
