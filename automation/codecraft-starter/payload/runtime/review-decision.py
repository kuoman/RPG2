#!/usr/bin/env python3
import argparse
import json
from pathlib import Path


DECISIONS = {"accept", "defer", "reject"}


def repository_root(start):
    candidate = Path(start).resolve()
    return next((path for path in (candidate, *candidate.parents) if (path / ".git").exists()), candidate)


class ReviewLedger:
    def __init__(self, path):
        self.path = Path(path)

    def read(self):
        if not self.path.exists():
            return []
        entries = json.loads(self.path.read_text())
        if not isinstance(entries, list):
            raise ValueError("review ledger must be a JSON array")
        return entries

    def write(self, entries):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(entries, indent=2) + "\n")

    def propose(self, identifier, source, summary):
        values = (identifier.strip(), source.strip(), summary.strip())
        if not all(values):
            raise ValueError("review identifier, source, and summary must be nonblank")
        entries = self.read()
        if any(entry.get("id") == values[0] for entry in entries):
            raise ValueError(f"review already exists: {values[0]}")
        entries.append({"id": values[0], "source": values[1], "summary": values[2], "decision": "pending"})
        self.write(entries)

    def decide(self, identifier, decision, rationale):
        if decision not in DECISIONS or not rationale.strip():
            raise ValueError("decision must be accept, defer, or reject with a rationale")
        entries = self.read()
        matches = [entry for entry in entries if entry.get("id") == identifier]
        if len(matches) != 1 or matches[0].get("decision") != "pending":
            raise ValueError(f"pending review not found: {identifier}")
        matches[0]["decision"] = decision
        matches[0]["rationale"] = rationale.strip()
        self.write(entries)

    def decide_batch(self, path):
        decisions = json.loads(Path(path).read_text())
        entries = self.read()
        working = json.loads(json.dumps(entries))
        by_id = {entry.get("id"): entry for entry in working}
        for item in decisions:
            identifier = item.get("id", "")
            decision = item.get("decision", "")
            rationale = item.get("rationale", "")
            if identifier not in by_id or by_id[identifier].get("decision") != "pending":
                raise ValueError(f"pending review not found: {identifier}")
            if decision not in DECISIONS or not rationale.strip():
                raise ValueError(f"invalid decision: {identifier}")
            by_id[identifier]["decision"] = decision
            by_id[identifier]["rationale"] = rationale.strip()
        self.write(working)


def main():
    parser = argparse.ArgumentParser()
    commands = parser.add_subparsers(dest="command", required=True)
    propose = commands.add_parser("propose")
    propose.add_argument("id")
    propose.add_argument("source")
    propose.add_argument("summary")
    decide = commands.add_parser("decide")
    decide.add_argument("id")
    decide.add_argument("decision", choices=sorted(DECISIONS))
    decide.add_argument("rationale")
    batch = commands.add_parser("decide-batch")
    batch.add_argument("path")
    arguments = parser.parse_args()
    ledger = ReviewLedger(repository_root(Path.cwd()) / "automation/review-decisions.json")
    if arguments.command == "propose":
        ledger.propose(arguments.id, arguments.source, arguments.summary)
    elif arguments.command == "decide":
        ledger.decide(arguments.id, arguments.decision, arguments.rationale)
    else:
        ledger.decide_batch(arguments.path)


if __name__ == "__main__":
    main()
