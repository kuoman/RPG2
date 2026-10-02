# Emergent Artifact Organization

Date: 2026/10/01

Automation: CodeCraft 0.6.1

## Intent

Keep accumulated learning discoverable by organizing artifacts according to their job rather than leaving every document in one flat directory.

## Organization

- The repository-root `automation/` directory owns workflow agreements, programming-process improvements, quality automation records, and skill evolution.
- `emergent/design/` owns the behavior plan, responsibility map, architecture decisions, and behavior-preserving design refactors.
- `emergent/features/` owns implemented-behavior artifacts and their numbered repetitions.
- `emergent/sessions/` owns resumable handoffs and time-specific continuity notes.
- `emergent/README.md` is the entry point and placement guide for emergent feature, design, and session records.

Files already owned by `.agents`, `.codex`, or `.claude` remain there. Executable machinery also remains at conventional discovery paths such as `.codecraft` and `.github/workflows`; the automation folder contains the emergent evidence and decisions about that machinery.

## Implementation

- Moved workflow, programming-process, and skill-evolution records to the repository-root `automation/` directory and organized the remaining emergent artifacts by responsibility.
- Updated the working agreement, CodeCraft and committer skills, structural analyzer, workflow tests, plan, and session handoff to use the new paths.
- Advanced CodeCraft from 0.5.0 to 0.6.0 for artifact routing, then to 0.6.1 to correct the automation directory to the repository root.

## Verification

- No stale references to the former root-level agreement, plan, responsibility map, or feature paths remain.
- The structural-review tests exercise the relocated plan path.
- The project-local skill validator checks the updated CodeCraft skill.
- `./mvnw verify` remains the canonical completion gate.
