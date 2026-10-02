# Active Run State

Date: 2026/10/02

Automation: CodeCraft 0.12.0; CodeCraft Starter 0.3.0

## Intent

Reduce repeated repository scanning and conversational memory by giving one coherent development increment a deterministic, resumable system of record.

## Approved Behavior

- One ignored run record stores the workflow stage, scope, deterministic checkpoints, typed attention, and next action.
- A compact `resume` view tells an AI which context is relevant without replaying full logs or rediscovering completed steps.
- Only the CLI mutates run state, transitions are ordered, and pending attention blocks advancement.
- The record cannot authorize protected changes or replace Git, approved batch manifests, signed verification receipts, or committed evidence.
- The portable CodeCraft Starter installs the same run-state capability.

## Responsibility Design

- `RunStore` owns persisted active-run state, validation, atomic updates, and stage transitions.
- `ResumeView` owns compact text and JSON presentation of the active run.
- Existing batch state owns consumed approved BDD entries.
- Existing verification receipts own isolated green-gate evidence.
- Git owns source and commit truth.
- Humans and AI own semantic decisions, which are referenced as resolved attention rather than inferred by the state machine.
- The CLI entry point is the composition boundary for the repository, clock, and Git HEAD reader.

## Test-First Evidence

The focused run-state suite first failed because `codecraft_run` did not exist. It now covers compact resumption, single-active-run enforcement, safe identifiers, ordered transitions, blocking attention, non-authoritative checkpoints, malformed and symlinked state, and completion after commit.

The starter clean-room test first failed because the new runtime was an unexpected, unmanifested package file. The versioned package now installs and exercises the active-run CLI in a disposable Git repository.

## Decisions

- Run state is local and ignored; durable conclusions continue to live in committed artifacts.
- The active pointer contains only a version and run identifier. Each run has its own versioned record.
- Successful command output is intentionally compact; `resume --json` supplies structured context when another deterministic process needs it.
- A changed base commit is surfaced for reassessment rather than silently rewriting the run's origin.

## Verification

- Repository workflow contracts: 112 tests passed.
- Starter clean-room contracts: 37 tests passed and package integrity was healthy.
- The CodeCraft skill validated through the locked project environment.
- An independent fresh-model exercise installed version 0.3.0 into a disposable repository, discovered the active-run reference from `AGENTS.md`, and exercised start, compact resume, typed attention, blocked advancement, resolution, text resume, and JSON resume without source-repository changes.
- The rejected advance returned failure without changing the stage; the final record retained the resolved judgment and reported a current base commit.
