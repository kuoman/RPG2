---
name: committer
description: Review and commit a green CodeCraft increment using Arlo notation. Use when the human asks to commit.
---

# Committer

Read `automation/codecraft-working-agreement.md` before acting. Do not repair code during commit review.

1. Inspect complete status and relevant staged and unstaged diffs.
2. Refuse secrets, generated output, unrelated work, or an increment without a current completion receipt.
3. Stage only the exact candidate and allowed evidence paths.
4. Require `.codecraft/bin/verify_increment.py <lane> --candidate-file <file> --evidence-file <file> --check --staged`.
5. Commit with `git commit --only -- <exact paths>` and an imperative Arlo prefix: `F`, `B`, `r`, `R`, `t`, `d`, or `e`.
6. Require the same check with `--check-commit HEAD` and show the last ten commits.
7. Never push without explicit human authorization.
