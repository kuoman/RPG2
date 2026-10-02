# Protected Change Lifecycle

Date: 2026/10/01

Automation: CodeCraft 0.7.0

## Intent

Remove redundant protected-asset interruptions while preserving exact human control over real mutations. Read-only inspection, deterministic batch verification, and Git metadata should not look like content changes, and an approved mutation should not lose authorization merely because its tool failed before changing anything.

## Approved Behaviors

| Element Number | Behavior | Arrange | Act | Assert |
|---:|---|---|---|---|
| 1 | Permit read-only inspection of protected assets | An enrolled BDD, manifest, hook, or configuration path | Evaluate recognized read-only `sed`, `rg`, or `git diff` | Proceeds without approval or pending-state mutation |
| 2 | Permit the exact expected-red verifier | The next unconsumed manifest entry matches its source | Run the documented verifier | Proceeds without extra protected-change approval |
| 3 | Carry an approved batch entry through Git metadata | BDD, registry, batch state, and staged paths match consumed approval | Stage or commit unchanged files | Proceeds without new approval |
| 4 | Prepare authorization before the first mutation | An exact normalized tool-input digest is recorded without permission | Human approves and the matching tool runs | The first real attempt is authorized |
| 5 | Reserve approval until completion | An exact mutation is approved and begins | PreToolUse reserves and PostToolUse reports success | Authorization is consumed once after success |
| 6 | Preserve approval after harmless failure | An approved mutation fails without protected content change | PostToolUse compares the pre-state | Reservation is released and the identical retry remains authorized |
| 7 | Consume approval after partial mutation | An approved command fails after changing protected content | PostToolUse compares the pre-state | Authorization is consumed and partial-change feedback is surfaced |
| 8 | Continue blocking altered mutations | Tool input, source, order, assertion, registry, or staged paths differ | Evaluate the attempt | The mutation is denied and protected content remains unchanged |

## Test-First Evidence

The focused lifecycle suite initially failed for read-only access, exact verification, approved Git metadata, preauthorization, harmless failure, and partial mutation. A second red pass exposed two Git-specific gaps: legacy registry entries were incorrectly treated as new batch entries, and staged protected changes were invisible when a commit message did not mention a protected filename.

The regression suite now covers all eight approved elements, conservative rejection of mutating `sed`, legacy registry preservation, staged-path inspection for commits, and Codex's string-form `fatal:` failure response. The complete workflow suite contains 42 passing tests.

## Implementation

- `.codecraft/hooks/protect_bdd.py` classifies recognized read-only commands before creating pending state.
- The hook validates exact next-entry source and order before allowing the expected-red runner.
- Git staging validates consumed batch sources, registry additions, and batch state. Git commits inspect their actual staged protected paths.
- `.codecraft/bin/prepare_protected_change.py` validates a proposed SHA-256 digest while the PreToolUse hook associates it with the active session. The command does not authorize anything itself.
- Matching authorization becomes a tool-use reservation with protected pre-state hashes. PostToolUse settles that reservation from the tool result and observed content.
- `.codex/hooks.json` already contained synchronous PreToolUse, PostToolUse, and UserPromptSubmit wiring, so no configuration mutation was necessary.

## Decisions and Challenges

- Read-only recognition is intentionally conservative. Shell composition, redirection, mutating `sed -i`, and unrecognized commands still take the protected path.
- Legacy registry members are compared with the repository version; only newly added paths must correspond to consumed batch entries.
- A staged commit is checked even when its message contains no protected naming pattern.
- The tool outcome alone cannot reveal partial side effects, so the reservation also records protected pre-state hashes.
- PostToolUse cannot undo a completed mutation; its responsibility is to settle authorization and surface a partial-change condition. This matches the documented Codex hook lifecycle.

## Verification

- Focused protected-lifecycle suite: 15 passing tests
- Complete workflow-automation suite: 42 passing tests
- Complete Java suite: 95 passing tests
- Project-local skill validator: valid
- Java structure review: current at 51 completed and reviewed behaviors
- Habit Hooks: all enforced checks passing
- Canonical build: `UV_CACHE_DIR=/tmp/rpg-codecraft-uv-cache ./mvnw verify` succeeded

The first bare `./mvnw verify` reached the quality phase but could not write uv's home-directory cache in the sandbox. Repository-owned cache configuration remains the separately approved CodeCraft 0.7.1 increment rather than being folded into this lifecycle change.

Habit Hooks suggested installing its Python plugin now that repository automation contains substantial Python. That changes the quality dependency and configuration design, so it is recorded for explicit consideration in the verification/cache increment. Reviewer-subagent coaching was handled by a direct scoped diff review because this session does not authorize sub-agent delegation.
