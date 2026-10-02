# Workflow Status and Evidence

Date: 2026/10/01

Automation: CodeCraft 0.8.0

## Intent

Make current workflow state, completion evidence, and contextual coaching decisions explicit without automating semantic decisions or protected mutations.

## Approved Behaviors

| Element Number | Behavior | Arrange | Act | Assert |
|---:|---|---|---|---|
| 1 | Report current workflow status | Roadmap, batch state, artifacts, and Git state exist | Run one project-local status command | Reports completed count, next item, active batch, pending reviews, and dirty-state summary without mutation |
| 2 | Draft evidence artifacts | A green increment has test and verification evidence | Run the artifact-drafting command | Produces a reviewable draft without inventing evidence or marking work complete |
| 3 | Validate completion evidence | Roadmap and artifact claim completion | Run the completion validator | Missing, stale, or inconsistent evidence blocks commit readiness |
| 4 | Handle contextual coaching explicitly | Habit Hooks or structural review produces a suggestion | Record accept, defer, or reject with rationale | Suggestions cannot disappear silently or trigger automatic refactoring |
| 5 | Preserve human checkpoints | Status and drafting automation encounter protected assets or roadmap decisions | Run the automation | Reads evidence only; protected mutations and semantic decisions still require human approval |

## Responsibility Design

- `WorkflowStatus` owns read-only aggregation and reporting; its source readers do not mutate the repository.
- `ArtifactDraft` renders explicit evidence, while `EvidenceFingerprint` owns freshness calculation for declared paths.
- `CompletionValidator` owns consistency checks and blocks readiness rather than repairing evidence.
- `ReviewLedger` owns suggestion history and explicit dispositions; it never performs the suggested change.
- Command-line entry points are composition boundaries that choose repository paths and concrete filesystem or Git access.

## Test-First Evidence

The first workflow run failed with three import errors because status, drafting/validation, and review-decision commands did not exist. The focused suite became green after the four small command modules were introduced. Independent review then found eleven fail-closed and edge-case gaps; each was reproduced with regression coverage before its fix. The workflow suite now has 76 passing tests.

## Implementation

- `.codecraft/bin/codecraft_status.py` reports roadmap, approved-batch, review, and Git state without writing.
- `.codecraft/bin/draft_feature_artifact.py` renders only supplied JSON evidence, leaves omissions visible, hard-codes human review as required, fingerprints content and modes, and writes only a new feature artifact.
- `.codecraft/bin/validate_completion.py` rejects artifacts outside the feature boundary and incomplete, duplicated, missing, stale, noncanonical, or roadmap-inconsistent evidence.
- `.codecraft/bin/record_review_decision.py` maintains a validated contextual-coaching ledger with `pending`, `accept`, `defer`, and `reject` states.
- Status detects out-of-order batch consumption and invalid persisted review entries instead of presenting corrupted state as plausible progress.
- Git inspection disables optional locks so the status command does not refresh the index.
- CodeCraft 0.8.0 documents the commands and keeps roadmap edits, completion status, protected mutations, and design decisions behind human checkpoints.

## Independent Review

The human approved one read-only reviewer sub-agent after Habit Hooks suggested it. The first review identified seven issues: an inexact completion-status check, incomplete schema validation, an arbitrary canonical command, unrestricted draft output, permissive batch-state parsing, optional Git index refresh, and fingerprints that ignored executable mode. A closure review confirmed those fixes and identified four more: unrestricted validator input, invalid ledger entries disappearing from status, empty duplicate fields bypassing uniqueness, and blank proposals. All eleven findings now have regression coverage and are resolved.

## Verification

- Focused workflow suite: 76 tests passed
- Complete suite: 95 Java tests and 76 workflow tests passed through `./mvnw verify`
- Quality checks: Java structure review current; all enforced Habit Hooks checks passed; both contextual suggestions explicitly resolved in the review ledger
- Canonical command: `./mvnw verify`

## Decisions and Challenges

- Fingerprints detect changes only within declared evidence paths. This keeps the mechanism understandable; completeness of that path list remains a visible human review responsibility.
- The validator does not treat a green result as permission to commit. The committer workflow and explicit human collaboration remain separate gates.
- Existing Python-specific Habit Hooks coaching remains deferred in the review ledger for its own responsibility-driven batch rather than being silently ignored or bundled here.
- Artifact-schema duplication across the template, renderer, and validator is recorded and deferred to its own representation-design batch; full-schema regression coverage protects the current contract.
