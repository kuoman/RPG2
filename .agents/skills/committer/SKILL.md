---
name: committer
description: Review and commit a green CodeCraft increment using Arlo notation. Use when the human asks to commit.
---

# Committer

Read `automation/codecraft-working-agreement.md` before acting. Do not repair code during commit review.

1. Inspect complete status and relevant staged and unstaged diffs.
2. Refuse secrets, generated output, unrelated work, or an increment without a current completion receipt.
3. Prepare `.codecraft/bin/commit_verified_increment.py prepare <lane> --candidate-file <file> --evidence-file <file> --message '<Arlo message>'` and present its exact paths, receipt identity, message, and transaction identity for one human approval.
4. After approval, run the same arguments with `execute` and `--transaction <approved identity>`. This single-use protected operation stages only the exact paths, checks the staged receipt, creates one path-limited commit, and checks the committed receipt.
5. Use an imperative Arlo prefix: `F`, `B`, `r`, `R`, `t`, `d`, or `e`.
6. Show the last ten commits after the transaction succeeds.
7. Never push without explicit human authorization.
