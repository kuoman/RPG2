#!/usr/bin/env python3
import fnmatch
import hashlib
import json
import re
import shlex
import sys
import os
from pathlib import Path


AFFIRMATIONS = {"a", "approve", "approved", "y", "yes"}


def repository_root(start):
    candidate = Path(start).resolve()
    return next((path for path in (candidate, *candidate.parents) if (path / ".git").exists()), candidate)


class AssetProtection:
    def __init__(self, repository):
        self.repository = Path(repository)
        self.state = self.repository / ".codecraft/state"
        self.registry = self.repository / ".codecraft/protected-assets.json"
        self.project = self.load_json(self.repository / ".codecraft/project.json", {})

    @staticmethod
    def load_json(path, default):
        return json.loads(path.read_text()) if path.exists() else default

    def handle(self, event):
        name = event.get("hook_event_name")
        if name == "UserPromptSubmit":
            self.authorize(event)
            return None
        if name == "PreToolUse":
            return self.before(event)
        if name == "PostToolUse":
            self.after(event)
        return None

    def before(self, event):
        command = event.get("tool_input", {}).get("command", "")
        protected = self.protected_paths(event.get("tool_name", ""), event.get("tool_input", {}))
        if not protected or self.read_only(command):
            return None
        digest = self.digest(event.get("tool_name", ""), event.get("tool_input", {}))
        approved_path = self.state / "approved-protected-change.json"
        approved = self.load_json(approved_path, {})
        session = self.session(event)
        if (
            approved.get("digest") == digest
            and approved.get("tool") == event.get("tool_name")
            and approved.get("session") == session
        ):
            self.state.mkdir(parents=True, exist_ok=True)
            reservation_path = self.reservation(event)
            try:
                os.replace(approved_path, reservation_path)
            except FileNotFoundError:
                pass
            else:
                reservation = {**approved, "paths": protected, "before": self.snapshots(protected)}
                reservation_path.write_text(json.dumps(reservation, indent=2) + "\n")
                return None
        self.state.mkdir(parents=True, exist_ok=True)
        pending = {"tool": event.get("tool_name"), "digest": digest, "paths": protected, "session": session}
        (self.state / "pending-protected-change.json").write_text(json.dumps(pending, indent=2) + "\n")
        return {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": "Protected CodeCraft change blocked for " + ", ".join(protected) + ". Describe the exact change and request standalone approval.",
            }
        }

    def after(self, event):
        reservation = self.reservation(event)
        if reservation.exists():
            reserved = self.load_json(reservation, {})
            unchanged = reserved.get("before") == self.snapshots(reserved.get("paths", []))
            if unchanged and self.failed(event):
                os.replace(reservation, self.state / "approved-protected-change.json")
            else:
                reservation.unlink()
        self.enroll_existing_assets()

    def enroll_existing_assets(self):
        registered = set(self.load_json(self.registry, []))
        patterns = self.project.get("protectedPatterns", [self.project.get("bddPattern", "*_bdd.java")])
        if self.repository.exists():
            registered.update(
                path.relative_to(self.repository).as_posix()
                for path in self.repository.rglob("*")
                if path.is_file()
                and not any(part in {".git", ".codecraft"} for part in path.relative_to(self.repository).parts)
                and any(
                    fnmatch.fnmatch(path.relative_to(self.repository).as_posix(), pattern)
                    or fnmatch.fnmatch(path.name, pattern)
                    for pattern in patterns
                )
            )
        self.registry.write_text(json.dumps(sorted(registered), indent=2) + "\n")

    def authorize(self, event):
        prompt = event.get("prompt", "").strip().lower()
        pending_path = self.state / "pending-protected-change.json"
        if prompt not in AFFIRMATIONS or not pending_path.exists():
            return
        pending = json.loads(pending_path.read_text())
        session = self.session(event)
        if pending.get("session") not in {None, session}:
            return
        pending["session"] = session
        self.state.mkdir(parents=True, exist_ok=True)
        (self.state / "approved-protected-change.json").write_text(json.dumps(pending, indent=2) + "\n")
        pending_path.unlink()

    def protected_paths(self, tool_name, tool_input):
        paths = []
        command = tool_input.get("command", "")
        if tool_name == "apply_patch":
            candidates = self.patch_operations(command)
        elif tool_name == "Bash":
            candidates = [("Mention", value) for value in self.shell_paths(command)]
        else:
            serialized = json.dumps(tool_input, sort_keys=True)
            candidates = [("Mention", value) for value in self.registered() if value in serialized]
            candidates.extend(("Mention", value) for value in self.path_values(tool_input))
        for operation, raw_path in candidates:
            path = self.normalize(raw_path)
            if operation == "Add" and not (self.repository / path).exists():
                continue
            if path in self.registered() or self.matches_behavior_pattern(path) or self.is_guard(path):
                paths.append(path)
        return sorted(set(paths))

    @classmethod
    def path_values(cls, value):
        if isinstance(value, dict):
            paths = []
            for key, nested in value.items():
                if key in {"path", "file_path", "target", "filename"} and isinstance(nested, str):
                    paths.append(nested)
                else:
                    paths.extend(cls.path_values(nested))
            return paths
        if isinstance(value, list):
            return [path for nested in value for path in cls.path_values(nested)]
        return []

    def registered(self):
        return set(self.load_json(self.registry, []))

    def matches_behavior_pattern(self, path):
        return any(
            fnmatch.fnmatch(path, pattern) or fnmatch.fnmatch(Path(path).name, pattern)
            for pattern in self.project.get("protectedPatterns", [self.project.get("bddPattern", "*_bdd.java")])
        )

    @staticmethod
    def is_guard(path):
        codex_config = str(Path(".codex") / "config.toml")
        codex_hooks = str(Path(".codex") / "hooks.json")
        guards = {
            ".codecraft/hooks",
            ".codecraft/state",
            ".codecraft/installation.json",
            ".codecraft/protected-assets.json",
            codex_config,
            codex_hooks,
        }
        return any(path == guard or path.startswith(guard + "/") for guard in guards)

    def shell_paths(self, command):
        registered = self.registered()
        try:
            tokens = shlex.split(command)
        except ValueError:
            return registered
        if not tokens:
            return []
        executable = Path(tokens[0]).name
        if executable == "commit_verified_increment.py":
            if any(token in command for token in (";", "&&", "||", "|", ">", "`", "$(", "\n")):
                return registered
            return self.commit_transaction_paths(tokens, registered)
        uncertain = executable in {"env", "python", "python3", "perl", "ruby", "sh", "bash", "zsh"}
        uncertain = uncertain or (executable == "git" and len(tokens) > 1 and tokens[1] in {"checkout", "clean", "reset", "restore"})
        if uncertain:
            return registered
        found = set()
        for token in tokens[1:]:
            normalized = token.lstrip("-").replace(str(self.repository) + "/", "")
            for protected in registered:
                parents = {parent.as_posix() for parent in Path(protected).parents}
                if fnmatch.fnmatch(protected, normalized) or normalized.rstrip("/") in parents:
                    found.add(protected)
        return found

    def commit_transaction_paths(self, tokens, registered):
        if len(tokens) < 2 or tokens[1] != "execute":
            return []
        try:
            candidate_file = self.option(tokens, "--candidate-file")
            evidence_file = self.option(tokens, "--evidence-file", required=False)
            paths = self.manifest_paths(candidate_file)
            if evidence_file:
                paths.extend(self.manifest_paths(evidence_file))
            return paths
        except (OSError, ValueError):
            return registered

    @staticmethod
    def option(tokens, name, required=True):
        for index, token in enumerate(tokens):
            if token == name and index + 1 < len(tokens):
                return tokens[index + 1]
            if token.startswith(name + "="):
                return token.split("=", 1)[1]
        if required:
            raise ValueError(f"missing {name}")
        return None

    @staticmethod
    def manifest_paths(path):
        values = []
        for raw in Path(path).read_text().splitlines():
            value = raw.strip()
            if value and not value.startswith("#"):
                values.append(value)
        if not values:
            raise ValueError("path manifest is empty")
        return values

    @staticmethod
    def patch_operations(command):
        return re.findall(r"^\*\*\* (Add|Update|Delete) File: (.+)$", command, re.MULTILINE)

    def normalize(self, raw_path):
        path = Path(raw_path.strip())
        if path.is_absolute():
            path = path.resolve().relative_to(self.repository)
        return path.as_posix()

    def snapshots(self, paths):
        snapshots = {}
        for relative in paths:
            path = self.repository / relative
            if path.is_symlink():
                snapshots[relative] = "symlink:" + os.readlink(path)
            elif path.is_file():
                snapshots[relative] = hashlib.sha256(path.read_bytes()).hexdigest()
            else:
                snapshots[relative] = "missing"
        return snapshots

    @staticmethod
    def session(event):
        return event.get("session_id") or event.get("conversation_id") or "local-session"

    @staticmethod
    def failed(event):
        response = event.get("tool_response", {})
        return bool(event.get("is_error") or event.get("error") or response.get("is_error") or response.get("success") is False)

    @staticmethod
    def read_only(command):
        if any(token in command for token in (";", "&&", "||", "|", ">", "`", "$(", "\n")):
            return False
        try:
            tokens = shlex.split(command)
        except ValueError:
            return False
        if not tokens:
            return False
        executable = Path(tokens[0]).name
        if executable == "sed":
            return not any(token == "-i" or token.startswith("-i") for token in tokens[1:])
        return executable == "rg" or (executable == "git" and len(tokens) > 1 and tokens[1] == "diff")

    @staticmethod
    def digest(tool, tool_input):
        normalized = json.dumps({"tool_name": tool, "tool_input": tool_input}, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(normalized.encode()).hexdigest()

    def reservation(self, event):
        identifier = re.sub(r"[^A-Za-z0-9_.-]", "_", event.get("tool_use_id", "unknown"))
        self.state.mkdir(parents=True, exist_ok=True)
        return self.state / f"{identifier}.reservation.json"


def main():
    event = json.load(sys.stdin)
    protection = AssetProtection(repository_root(event.get("cwd", Path.cwd())))
    result = protection.handle(event)
    if result is not None:
        json.dump(result, sys.stdout)


if __name__ == "__main__":
    main()
