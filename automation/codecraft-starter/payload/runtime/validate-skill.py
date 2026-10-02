#!/usr/bin/env python3
import re
import sys
from pathlib import Path


def validate(skill):
    skill = Path(skill)
    entry = skill / "SKILL.md"
    problems = []
    if not entry.is_file():
        return ["SKILL.md is missing"]
    content = entry.read_text()
    match = re.match(r"^---\n(.*?)\n---\n", content, re.DOTALL)
    if not match:
        return ["SKILL.md YAML frontmatter is missing"]
    fields = {}
    for line in match.group(1).splitlines():
        if ":" in line and not line.startswith((" ", "\t")):
            key, value = line.split(":", 1)
            fields[key.strip()] = value.strip()
    name = fields.get("name", "")
    if name != skill.name:
        problems.append(f"skill name must match directory: expected {skill.name}, found {name or 'missing'}")
    if not fields.get("description"):
        problems.append("skill description is missing")
    if re.search(r"\b(TODO|TBD|PLACEHOLDER)\b", content, re.IGNORECASE):
        problems.append("skill contains an unfinished scaffold marker")
    return problems


def main():
    if len(sys.argv) != 2:
        raise SystemExit("usage: validate_skill.py <skill-directory>")
    problems = validate(sys.argv[1])
    if problems:
        for problem in problems:
            print(problem, file=sys.stderr)
        raise SystemExit(1)
    print("Skill is valid!")


if __name__ == "__main__":
    main()
