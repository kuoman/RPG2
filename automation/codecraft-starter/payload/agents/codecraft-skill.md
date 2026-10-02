---
name: codecraft
description: Develop, test, refactor, review, or automate this Java project through its collaborative outside-in CodeCraft workflow. Use for Java behavior, tests, design, build, quality, or workflow changes in this repository.
metadata:
  version: 0.3.0
---

# CodeCraft

Read `automation/codecraft-working-agreement.md`, `.codecraft/project.json`, and the project-owned `.claude/rules/always.md` when it exists before acting. They define the human checkpoints, project paths and commands, and response conventions.

## Active run state

For implementation, refactoring, or workflow-automation work, run `.codecraft/bin/codecraft_run.py resume` before reconstructing task state. An active record supplies the stage, next action, attention items, and narrow context paths. It cannot authorize protected changes, approve design, or replace repository evidence.

Read [the active-run reference](references/active-run-state.md) when starting, advancing, recording, resuming, or completing a run. Mutate run state only through its CLI. One run represents one coherent increment or one BDD batch entry and finishes only after its commit exists.

## Behavior and design

Read [the feature cycle](references/feature-cycle.md) for behavior changes and defect fixes. Do not implement behavior beyond the human-approved slice.

Before proposing public design, ask what job each object has, who owns the information, who decides the rule, and who changes the state. Apply SOLID and dependency direction explicitly. Policy objects receive collaborators with separate jobs; composition roots choose concrete implementations.

Present proposed BDD tests using [the approval grid](assets/bdd-approval-grid.md). Element Numbers remain stable references until a revised grid supersedes them.

## Protected behavior

Existing protected BDD tests, their expected outputs and fixtures, the protected registry, and protection hooks require narrow human approval before modification or deletion. New BDD tests require approved design and are enrolled after creation. Never treat general permission as protected-file approval.

## Verification and commits

Use `.codecraft/bin/verify_increment.py <lane> --candidate-file <file>` with an exact repository-relative candidate list. Select `behavior`, `refactoring`, `automation`, or `documentation`; mixed increments use the stronger lane. Commit only the verified candidate and supported evidence, use Arlo notation, and never push without explicit authorization.

Quality and coverage output is coaching. Resolve enforced findings. Classify contextual findings with the human before changing design, and never add a test solely to improve a metric.

Record contextual suggestions with `.codecraft/bin/record_review_decision.py propose`, present compatible pending items in one numbered grid, and apply the human's dispositions with `decide` or `decide-batch`. A recorded decision does not authorize the suggested code change.

## Learning and evolution

Read [the evolution guide](references/evolution.md) when changing the workflow, recording a repeated pattern, or upgrading CodeCraft. Keep reusable machinery distinct from project-owned agreements and evidence.

Use [the feature artifact template](assets/feature-artifact-template.md) to document completed behavior without inventing missing evidence.
