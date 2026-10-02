#!/usr/bin/env python3
import argparse
import json
import os
import re
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path


RUN_KINDS = {"behavior", "refactoring", "automation", "documentation"}
STAGES = {
    "design",
    "outside-red",
    "implementation",
    "review",
    "verification",
    "commit",
    "complete",
}
TRANSITIONS = {
    "design": {"outside-red", "implementation"},
    "outside-red": {"implementation"},
    "implementation": {"review"},
    "review": {"implementation", "verification"},
    "verification": {"implementation", "review", "commit"},
    "commit": {"complete"},
    "complete": set(),
}
ACTORS = {"cli", "ai", "human", "ai-human"}
ATTENTION_KINDS = {"ai-judgment", "human-approval", "unexpected-failure"}
CHECKPOINT_STATUSES = {"pending", "passed", "failed", "accepted", "skipped"}
IDENTIFIER = re.compile(r"^[a-z0-9][a-z0-9-]{0,79}$")


class RunStateError(ValueError):
    pass


class RunStore:
    def __init__(self, repository, clock=None, head_reader=None):
        self.repository = Path(repository).resolve()
        self.clock = clock or (lambda: datetime.now(timezone.utc))
        self.head_reader = head_reader or self._read_head
        self.state = self.repository / ".codecraft/state"
        self.runs = self.state / "runs"
        self.pointer = self.state / "active-run.json"

    def start(self, identifier, kind, objective, scope=None, next_action=None):
        self._validate_identifier(identifier, "run id")
        if kind not in RUN_KINDS:
            raise RunStateError(f"invalid run kind: {kind}")
        self._require_text(objective, "objective")
        self._ensure_storage()
        if self.pointer.exists() or self.pointer.is_symlink():
            active = self.active()
            raise RunStateError(f"active run already exists: {active['id']}")
        run_path = self._run_path(identifier)
        if run_path.exists() or run_path.is_symlink():
            raise RunStateError(f"run already exists: {identifier}")
        timestamp = self._timestamp()
        record = {
            "version": 1,
            "revision": 1,
            "id": identifier,
            "kind": kind,
            "objective": objective.strip(),
            "stage": "design",
            "scope": self._string_map(scope or {}, "scope"),
            "baseCommit": self._require_text(self.head_reader(), "base commit"),
            "createdAt": timestamp,
            "updatedAt": timestamp,
            "checkpoints": {},
            "attention": [],
            "nextAction": self._next_action(
                next_action
                or {
                    "actor": "ai-human",
                    "action": "Define and approve the run design",
                    "context": [],
                }
            ),
        }
        self._validate_record(record)
        self._atomic_write(run_path, record)
        self._atomic_write(self.pointer, {"version": 1, "runId": identifier})
        return record

    def active(self):
        if not self.pointer.exists() and not self.pointer.is_symlink():
            raise RunStateError("no active CodeCraft run")
        pointer = self._load_json(self.pointer, "active run pointer")
        if pointer.get("version") != 1 or set(pointer) != {"version", "runId"}:
            raise RunStateError("invalid active run pointer")
        self._validate_identifier(pointer.get("runId"), "run id")
        record = self._load_json(self._run_path(pointer["runId"]), "run record")
        self._validate_record(record)
        if record["id"] != pointer["runId"] or record["stage"] == "complete":
            raise RunStateError("invalid active run record")
        return record

    def advance(self, stage, actor, action, context=None, command=None):
        record = self.active()
        if stage not in TRANSITIONS[record["stage"]]:
            raise RunStateError(
                f"invalid stage transition: {record['stage']} -> {stage}"
            )
        self._require_no_pending_attention(record)
        record["stage"] = stage
        record["nextAction"] = self._next_action(
            {
                "actor": actor,
                "action": action,
                "context": context or [],
                "command": command,
            }
        )
        return self._save(record)

    def record_checkpoint(self, name, status, summary, evidence=None):
        self._validate_identifier(name, "checkpoint id")
        if status not in CHECKPOINT_STATUSES:
            raise RunStateError(f"invalid checkpoint status: {status}")
        record = self.active()
        record["checkpoints"][name] = {
            "status": status,
            "summary": self._require_text(summary, "checkpoint summary"),
            "evidence": self._string_list(evidence or [], "checkpoint evidence"),
            "recordedAt": self._timestamp(),
        }
        return self._save(record)

    def add_attention(self, identifier, kind, reason, context=None):
        self._validate_identifier(identifier, "attention id")
        if kind not in ATTENTION_KINDS:
            raise RunStateError(f"invalid attention kind: {kind}")
        record = self.active()
        if any(item["id"] == identifier for item in record["attention"]):
            raise RunStateError(f"attention already exists: {identifier}")
        record["attention"].append(
            {
                "id": identifier,
                "kind": kind,
                "reason": self._require_text(reason, "attention reason"),
                "context": self._string_list(context or [], "attention context"),
                "status": "pending",
                "createdAt": self._timestamp(),
            }
        )
        return self._save(record)

    def resolve_attention(self, identifier, resolution):
        record = self.active()
        item = next(
            (item for item in record["attention"] if item["id"] == identifier),
            None,
        )
        if item is None:
            raise RunStateError(f"attention does not exist: {identifier}")
        if item["status"] != "pending":
            raise RunStateError(f"attention is already resolved: {identifier}")
        item["status"] = "resolved"
        item["resolution"] = self._require_text(resolution, "attention resolution")
        item["resolvedAt"] = self._timestamp()
        return self._save(record)

    def finish(self, summary, commit):
        record = self.active()
        if record["stage"] != "commit":
            raise RunStateError("run can finish only from the commit stage")
        self._require_no_pending_attention(record)
        record["stage"] = "complete"
        record["summary"] = self._require_text(summary, "completion summary")
        record["completedCommit"] = self._require_text(commit, "completed commit")
        record["nextAction"] = None
        completed = self._save(record)
        self.pointer.unlink()
        return completed

    def repository_state(self, record):
        return "current" if self.head_reader() == record["baseCommit"] else "base-commit-changed"
    def _save(self, record):
        record["revision"] += 1
        record["updatedAt"] = self._timestamp()
        self._validate_record(record)
        self._atomic_write(self._run_path(record["id"]), record)
        return record

    def _validate_record(self, record):
        required = {
            "version",
            "revision",
            "id",
            "kind",
            "objective",
            "stage",
            "scope",
            "baseCommit",
            "createdAt",
            "updatedAt",
            "checkpoints",
            "attention",
            "nextAction",
        }
        if not isinstance(record, dict) or not required.issubset(record):
            raise RunStateError("invalid run record")
        try:
            self._validate_identifier(record["id"], "run id")
            if record["version"] != 1 or not isinstance(record["revision"], int):
                raise RunStateError("invalid run record")
            if record["kind"] not in RUN_KINDS or record["stage"] not in STAGES:
                raise RunStateError("invalid run record")
            self._require_text(record["objective"], "objective")
            self._require_text(record["baseCommit"], "base commit")
            self._string_map(record["scope"], "scope")
            self._validate_checkpoints(record["checkpoints"])
            self._validate_attention(record["attention"])
            if record["stage"] != "complete":
                self._next_action(record["nextAction"])
        except (KeyError, TypeError, RunStateError) as error:
            raise RunStateError("invalid run record") from error

    def _ensure_storage(self):
        for path in (self.repository / ".codecraft", self.state, self.runs):
            if path.is_symlink():
                raise RunStateError(f"state path may not be a symlink: {path}")
            path.mkdir(exist_ok=True)

    def _run_path(self, identifier):
        self._validate_identifier(identifier, "run id")
        return self.runs / f"{identifier}.json"

    def _atomic_write(self, path, value):
        if path.is_symlink():
            raise RunStateError(f"state file may not be a symlink: {path}")
        path.parent.mkdir(parents=True, exist_ok=True)
        descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
        try:
            with os.fdopen(descriptor, "w") as stream:
                json.dump(value, stream, indent=2, sort_keys=True)
                stream.write("\n")
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temporary, path)
        finally:
            if os.path.exists(temporary):
                os.unlink(temporary)

    def _load_json(self, path, label):
        if path.is_symlink():
            raise RunStateError(f"{label} may not be a symlink")
        try:
            return json.loads(path.read_text())
        except (OSError, json.JSONDecodeError) as error:
            raise RunStateError(f"invalid {label}") from error

    def _read_head(self):
        return subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=self.repository,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()

    def _next_action(self, value):
        if not isinstance(value, dict) or value.get("actor") not in ACTORS:
            raise RunStateError("invalid next action")
        result = {
            "actor": value["actor"],
            "action": self._require_text(value.get("action"), "next action"),
            "context": self._string_list(value.get("context", []), "next action context"),
        }
        command = value.get("command")
        if command is not None:
            result["command"] = self._require_text(command, "next action command")
        return result

    def _validate_checkpoints(self, checkpoints):
        if not isinstance(checkpoints, dict):
            raise RunStateError("invalid checkpoints")
        for identifier, checkpoint in checkpoints.items():
            self._validate_identifier(identifier, "checkpoint id")
            if not isinstance(checkpoint, dict) or set(checkpoint) != {
                "status",
                "summary",
                "evidence",
                "recordedAt",
            }:
                raise RunStateError("invalid checkpoint")
            if checkpoint["status"] not in CHECKPOINT_STATUSES:
                raise RunStateError("invalid checkpoint")
            self._require_text(checkpoint["summary"], "checkpoint summary")
            self._string_list(checkpoint["evidence"], "checkpoint evidence")
            self._require_text(checkpoint["recordedAt"], "checkpoint timestamp")

    def _validate_attention(self, attention):
        if not isinstance(attention, list):
            raise RunStateError("invalid attention")
        identifiers = set()
        for item in attention:
            required = {"id", "kind", "reason", "context", "status", "createdAt"}
            if not isinstance(item, dict) or not required.issubset(item):
                raise RunStateError("invalid attention")
            self._validate_identifier(item["id"], "attention id")
            if item["id"] in identifiers or item["kind"] not in ATTENTION_KINDS:
                raise RunStateError("invalid attention")
            identifiers.add(item["id"])
            self._require_text(item["reason"], "attention reason")
            self._string_list(item["context"], "attention context")
            self._require_text(item["createdAt"], "attention timestamp")
            if item["status"] == "pending" and set(item) != required:
                raise RunStateError("invalid attention")
            if item["status"] == "resolved":
                if set(item) != required | {"resolution", "resolvedAt"}:
                    raise RunStateError("invalid attention")
                self._require_text(item["resolution"], "attention resolution")
                self._require_text(item["resolvedAt"], "attention timestamp")
            elif item["status"] != "pending":
                raise RunStateError("invalid attention")

    def _require_no_pending_attention(self, record):
        pending = self._pending_attention(record)
        if pending:
            raise RunStateError(
                "pending attention must be resolved: "
                + ", ".join(item["id"] for item in pending)
            )

    @staticmethod
    def _pending_attention(record):
        return [item for item in record["attention"] if item.get("status") == "pending"]

    @staticmethod
    def _validate_identifier(value, label):
        if not isinstance(value, str) or not IDENTIFIER.fullmatch(value):
            raise RunStateError(f"invalid {label}: {value}")

    @staticmethod
    def _require_text(value, label):
        if not isinstance(value, str) or not value.strip():
            raise RunStateError(f"invalid {label}")
        return value.strip()

    def _string_map(self, value, label):
        if not isinstance(value, dict):
            raise RunStateError(f"invalid {label}")
        return {
            self._require_text(key, f"{label} key"): self._require_text(item, label)
            for key, item in value.items()
        }

    def _string_list(self, value, label):
        if not isinstance(value, list):
            raise RunStateError(f"invalid {label}")
        return [self._require_text(item, label) for item in value]

    def _timestamp(self):
        return self.clock().astimezone(timezone.utc).isoformat()


class ResumeView:
    def __init__(self, store):
        self.store = store

    def render(self, as_json=False):
        try:
            record = self.store.active()
        except RunStateError as error:
            if str(error) == "no active CodeCraft run":
                return json.dumps({"active": False}) if as_json else "No active CodeCraft run"
            raise
        repository_state = self.store.repository_state(record)
        if as_json:
            snapshot = dict(record)
            snapshot["repositoryState"] = repository_state
            return json.dumps(snapshot, indent=2, sort_keys=True)
        lines = [
            f"RUN: {record['id']} ({record['kind']})",
            f"OBJECTIVE: {record['objective']}",
            f"STAGE: {record['stage']}",
        ]
        if repository_state != "current":
            lines.append("REPOSITORY: base commit changed; reassess the run before continuing")
        next_action = record["nextAction"]
        lines.append(f"NEXT [{next_action['actor']}]: {next_action['action']}")
        if next_action.get("command"):
            lines.append(f"COMMAND: {next_action['command']}")
        if next_action["context"]:
            lines.append("READ: " + ", ".join(next_action["context"]))
        for item in RunStore._pending_attention(record):
            lines.append(f"ATTENTION [{item['kind']}] {item['id']}: {item['reason']}")
            if item["context"]:
                lines.append("  READ: " + ", ".join(item["context"]))
        return "\n".join(lines)


def repository_root(start):
    candidate = Path(start).resolve()
    return next(
        (path for path in (candidate, *candidate.parents) if (path / ".git").exists()),
        candidate,
    )


def parser():
    result = argparse.ArgumentParser(description="Manage one active CodeCraft run")
    commands = result.add_subparsers(dest="operation", required=True)
    start = commands.add_parser("start")
    start.add_argument("identifier")
    start.add_argument("--kind", choices=sorted(RUN_KINDS), required=True)
    start.add_argument("--objective", required=True)
    start.add_argument("--scope", action="append", default=[])
    start.add_argument("--next-actor", choices=sorted(ACTORS), default="ai-human")
    start.add_argument("--next-action", default="Define and approve the run design")
    start.add_argument("--context", action="append", default=[])
    resume = commands.add_parser("resume")
    resume.add_argument("--json", action="store_true")
    advance = commands.add_parser("advance")
    advance.add_argument("stage", choices=sorted(STAGES - {"design", "complete"}))
    advance.add_argument("--actor", choices=sorted(ACTORS), required=True)
    advance.add_argument("--next-action", required=True)
    advance.add_argument("--context", action="append", default=[])
    advance.add_argument("--command")
    checkpoint = commands.add_parser("checkpoint")
    checkpoint.add_argument("identifier")
    checkpoint.add_argument("status", choices=sorted(CHECKPOINT_STATUSES))
    checkpoint.add_argument("--summary", required=True)
    checkpoint.add_argument("--evidence", action="append", default=[])
    add_attention = commands.add_parser("attention-add")
    add_attention.add_argument("identifier")
    add_attention.add_argument("kind", choices=sorted(ATTENTION_KINDS))
    add_attention.add_argument("--reason", required=True)
    add_attention.add_argument("--context", action="append", default=[])
    resolve = commands.add_parser("attention-resolve")
    resolve.add_argument("identifier")
    resolve.add_argument("--resolution", required=True)
    finish = commands.add_parser("finish")
    finish.add_argument("--summary", required=True)
    finish.add_argument("--commit", required=True)
    return result


def parse_scope(values):
    scope = {}
    for value in values:
        if "=" not in value:
            raise RunStateError(f"scope must use key=value: {value}")
        key, item = value.split("=", 1)
        scope[key] = item
    return scope


def main(arguments=None):
    arguments = parser().parse_args(arguments)
    store = RunStore(repository_root(Path.cwd()))
    if arguments.operation == "start":
        store.start(
            arguments.identifier,
            arguments.kind,
            arguments.objective,
            scope=parse_scope(arguments.scope),
            next_action={
                "actor": arguments.next_actor,
                "action": arguments.next_action,
                "context": arguments.context,
            },
        )
    elif arguments.operation == "advance":
        store.advance(
            arguments.stage,
            arguments.actor,
            arguments.next_action,
            arguments.context,
            arguments.command,
        )
    elif arguments.operation == "checkpoint":
        store.record_checkpoint(
            arguments.identifier,
            arguments.status,
            arguments.summary,
            arguments.evidence,
        )
    elif arguments.operation == "attention-add":
        store.add_attention(
            arguments.identifier,
            arguments.kind,
            arguments.reason,
            arguments.context,
        )
    elif arguments.operation == "attention-resolve":
        store.resolve_attention(arguments.identifier, arguments.resolution)
    elif arguments.operation == "finish":
        store.finish(arguments.summary, arguments.commit)
    print(ResumeView(store).render(getattr(arguments, "json", False)))


if __name__ == "__main__":
    try:
        main()
    except (RunStateError, subprocess.CalledProcessError) as error:
        raise SystemExit(f"CodeCraft run error: {error}") from error
