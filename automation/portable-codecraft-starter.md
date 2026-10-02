# Portable CodeCraft Starter

Date: 2026/10/01

Automation: CodeCraft Starter 0.3.0; CodeCraft Java 0.12.0

## Intent

Package the proven AI development process—not RPG Combat behavior—so another conventional Java/Maven repository can install repository-local instructions, workflow machinery, protection, evidence practices, and evolution rules.

## Boundaries

- Reusable distribution: `automation/codecraft-starter/`
- Distribution-managed: shared skills, verifier, doctor, protection hook, AI adapters, CI template, and Java/Maven adapter references
- Project-owned after creation: working agreement, project configuration, plans, responsibility map, review decisions, and protected-asset registry
- Excluded: RPG roadmap content, domain artifacts, BDD batches, registered RPG paths, feature evidence, and current project state

## Red Evidence

- The first clean-room test run failed because the starter implementation did not exist.
- The first implementation run exposed target paths resolving against the source repository rather than the installation target; all five initial tests failed before the boundary was corrected.
- The Maven integration contract then failed because starter tests were absent from canonical verification and the package directory was absent from automation-lane fingerprints.
- Independent security review found release blockers in approval reservation, path confinement, installation rollback, receipt snapshot timing, version integrity, template rendering, health checks, and companion-asset enrollment.
- The first final isolated gate rejected Python bytecode generated inside the release tree; the canonical Maven invocation now runs starter tests in no-bytecode mode.

## Implementation

- A versioned payload manifest renders conventional Java/Maven defaults without retaining RPG names or paths.
- Installation merges a named `AGENTS.md` block, appends only missing ignore entries, enrolls behavior tests and companion assets, rejects symlinked destinations, rolls back partial writes, refuses managed-file conflicts, and signs installed state in Git metadata.
- Upgrade replaces only unchanged managed files and never overwrites project-owned files. It rejects same-version content changes and downgrades; versioned migrations can remove only unchanged managed files. Local managed changes become explicit merge conflicts, and no force option exists.
- The installed doctor checks signed manifest integrity, managed contents and modes, managed instruction blocks, project configuration, Git locality, and the configured verification command.
- Installed CodeCraft and committer skills teach a fresh model how to collaborate, use approval grids, protect existing behavior, verify exact increments, commit safely, document learning, and evolve the workflow.
- The installed protection hook atomically reserves session-bound, exact single-use approval, retains it after a harmless failure, consumes it after success or mutation, detects indirect shell targeting, and automatically enrolls behavior tests and configured companions. It remains a guardrail backed by host sandbox permissions.
- The installed verifier snapshots the base, candidate, configuration, commands, inputs, and repository before testing an exact candidate in a temporary worktree. It rejects symlink candidates and concurrent source changes, then signs a short-lived receipt in Git metadata and binds staged or committed content to that receipt.
- Codex and Claude instruction adapters are included. Codex receives technical hook configuration; Claude compatibility remains instruction-level unless its host supplies equivalent hook enforcement.
- The Java/Maven adapter is a reviewed reference rather than an automatic POM rewrite.
- Project-owned emoji response conventions are installed at `.claude/rules/always.md` and discovered through the shared instruction block, so each target can evolve its presentation preferences without forking managed workflow machinery.
- A CLI-managed active-run record provides compact resumable context for one coherent increment, ordered workflow stages, deterministic checkpoints, and typed attention without granting approval or replacing durable evidence.

## Verification

- Clean-room starter tests: 36 passed through canonical verification.
- Installed CodeCraft and committer skills validate with both the starter's self-contained validator and the project-local skill validator.
- Disposable repositories demonstrated installation, both doctors, protected approval state transitions, isolated verification, staged and committed receipt checks, transactional rollback, and conflict-safe upgrades.
- Version-to-version upgrade coverage preserves project-owned evolution, updates unchanged managed files, rejects downgrades and same-version mutation, and applies explicit safe removal migrations.
- An independent fresh model installed the package, discovered `AGENTS.md`, both project guidance sources, configuration, plan, responsibility map, feature cycle, and BDD grid without external path hints. With the default meta-plan it correctly stopped for a human-defined observable behavior instead of inventing scope; the forward-test acceptance now distinguishes that bootstrap outcome from a seeded concrete-behavior exercise.
- A fresh-model 0.3.0 exercise independently discovered the active-run reference, preserved a blocked judgment without partial state advancement, and resumed the exact next action in compact text and complete JSON forms.
- Independent security and portability review identified seven finding groups. The executable boundaries above were hardened; support language now identifies hooks as guardrails rather than the sole security boundary.
- The active-run focused suite and starter clean-room exercise pass locally; the final isolated automation-lane receipt remains the authoritative completion result for this version.
- The current signed automation receipt is stored under the repository's ignored `.codecraft/state/` directory and is checked against staged and committed content by the committer workflow.

## Decisions

- The first distribution supports conventional Java/Maven repositories on macOS and Linux.
- The package vendors all runtime instructions and machinery into the target; it has no runtime dependency on this repository.
- Build mutation is deliberately not automatic because unknown POM ownership and plugin configuration require project-specific review.

## Challenges

- Portability does not mean pretending every Maven build is identical. The core can install deterministically, while quality-plugin reconciliation remains an explicit automation slice in the target project.
- Project evolution and distribution upgrades pull in opposite directions; the managed/project-owned boundary and hash-based conflicts preserve both without silent replacement.
