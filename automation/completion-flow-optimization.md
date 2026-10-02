# Completion Flow Optimization

Date: 2026/10/01

Automation: CodeCraft 0.9.0

## Intent

Reduce repeated verification, evidence entry, approval churn, and process-level test noise while preserving every semantic and protected-change checkpoint.

## Approved Behaviors

| Element Number | Behavior | Arrange | Act | Assert |
|---:|---|---|---|---|
| 1 | Verify an unchanged code state once | An exact coherent candidate is listed separately from unrelated workspace changes | Verify isolated `HEAD` plus that candidate, then compare the receipt with its staged blobs | The green result is reused only for the signed repository, base commit, configuration, and exact candidate |
| 2 | Consolidate compatible approvals | Several contextual suggestions await disposition | Approve one numbered decision grid and apply its decision file | All decisions are recorded atomically without weakening protected-change approval |
| 3 | Use completion lanes | An increment is behavior, refactoring, automation, or prose-only documentation | Run its explicit lane | The increment receives relevant gates without unrelated work |
| 4 | Reduce artifact duplication | Approved manifests and verification receipts contain objective evidence | Draft a feature artifact | Objective fields are prefilled while human-owned design evidence remains explicit |
| 5 | Keep process tests risk-focused | Workflow prose and executable safety contracts coexist | Select workflow test coverage | Tests protect state, side effects, fail-closed behavior, and machine contracts rather than wording or judgment |
| 6 | Reuse short-lived verification evidence | A lane completes successfully | Record and later check its signed receipt | The receipt is accepted only for the same repository, base commit, configured gates, and candidate within its lifetime |
| 7 | Centralize the artifact schema | Template, renderer, and validator require one shape | Change the canonical schema | The generated template and executable consumers share one source of truth |

## Responsibility Design

- `CompletionLanes` owns lane configuration; it does not run commands.
- `IncrementVerifier` sequences an injected command runner and records a receipt only after every gate succeeds.
- `InputFingerprint` owns deterministic content-and-mode fingerprints for declared material inputs.
- `VerificationReceipts` owns receipt persistence, freshness, and staleness decisions.
- `FeatureArtifactSchema` owns feature-artifact structure and renders both templates and evidence.
- `EvidenceAssembler` combines human input with exact facts from a consumed entry in a registered protected batch and an authenticated verification receipt.
- `CompletionValidator` checks schema, roadmap, human-completion status, and the injected receipt store without repairing evidence.
- `ReviewLedger` validates every grouped disposition before changing any entry.
- CLI entry points remain composition roots for filesystem, subprocess, clock, schema, and configuration dependencies.

## Test-First Evidence

The first focused runs failed because completion receipts, schema-driven rendering, manifest assembly, and grouped decisions did not exist. Safety-focused tests now cover lane selection, receipt freshness and expiration, content and mode changes, evidence-only changes, schema/template consistency, objective evidence assembly, atomic decisions, output containment, and fail-closed completion validation.

## Implementation

- `.codecraft/bin/verify_increment.py` verifies an explicit candidate in an isolated worktree and checks its signed receipt against the exact staged blobs before commit.
- `.codecraft/completion-lanes.json` declares gates and complete material-input families for behavior, refactoring, automation, and documentation increments; documentation also rejects executable or governing dirty paths.
- Feature artifacts derive from `feature-artifact-schema.json`; only consumed entries in registered protected batches and authenticated current receipts may prefill objective evidence.
- Completion validation rejects structural placeholders, and grouped review decisions reject duplicate identities and replace the ledger atomically.
- Compatible contextual suggestions can be resolved through one atomic `decide-batch` operation.
- The working agreement limits workflow tests to executable risk and machine contracts.

## Verification

- Focused workflow suite: 89 tests passed
- Independent review: seven initial and five follow-up candidate, commit-scope, evidence-integrity, input-coverage, receipt-integrity, schema-validation, linked-worktree, and atomicity findings were fixed before completion
- Automation completion lane: 95 Java tests and 89 workflow tests passed; Java structure review current; enforced Habit Hooks checks passed; CodeCraft and committer skills valid
- Candidate receipt: signed and bound to the repository, base commit, configured gates, and exact isolated material paths; staged and committed-tree checks are enforced by the committer workflow
- Canonical integration command: `./mvnw verify` through the automation lane

## Decisions and Challenges

- Receipt fingerprints intentionally exclude evidence-only automation records and feature completion outputs, so recording results does not invalidate the result being recorded.
- Governing skills, rules, build files, executable automation, tests, and source remain material inputs and invalidate the applicable receipt.
- The documentation lane is unavailable for Markdown skills or rules because those files change executable agent behavior.
- The earlier schema-centralization deferral remains historical; a follow-up accepted entry records the human's explicit decision to implement it now.
