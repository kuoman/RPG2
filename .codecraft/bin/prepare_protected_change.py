#!/usr/bin/env python3
import argparse
import json
import re
from pathlib import Path


def repository_root(start):
    candidate = Path(start).resolve()
    return next((path for path in (candidate, *candidate.parents) if (path / ".git").exists()), candidate)


def main():
    parser = argparse.ArgumentParser(description="Prepare one exact protected CodeCraft change")
    parser.add_argument("--tool", required=True)
    parser.add_argument("--digest", required=True)
    parser.add_argument("--description", required=True)
    arguments = parser.parse_args()
    if not re.fullmatch(r"[0-9a-f]{64}", arguments.digest):
        parser.error("--digest must be a lowercase SHA-256 digest")
    repository = repository_root(Path.cwd())
    state = repository / ".codecraft/state"
    state.mkdir(parents=True, exist_ok=True)
    pending = {
        "tool": arguments.tool,
        "digest": arguments.digest,
        "description": arguments.description.strip(),
    }
    (state / "pending-protected-change.json").write_text(json.dumps(pending, indent=2) + "\n")
    print("Protected change prepared; describe it to the human and request a standalone approval.")


if __name__ == "__main__":
    main()
