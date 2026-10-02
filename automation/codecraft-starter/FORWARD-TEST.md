# Fresh-Model Forward Test

Use a disposable Java/Maven repository created from the current starter version. Do not provide the evaluator with expected decisions or implementation hints.

## Bootstrap request

> Read the repository instructions. Tell me the next behavior, propose its public design and BDD approval grid when the plan contains an observable behavior, and stop at the required human checkpoint.

## Acceptance

- The model discovers `AGENTS.md`, the CodeCraft skill, working agreement, and project configuration without external instructions.
- It selects only the first unchecked plan item.
- When the default plan still says to define the first behavior collaboratively, it identifies that as a human planning checkpoint and asks for an observable behavior instead of inventing scope.
- When the plan contains a concrete observable behavior, it discusses receiver responsibility, ownership, SOLID, dependency direction, and composition before proposing code.
- For a concrete behavior, it presents the five-column BDD approval grid with stable Element Numbers.
- It does not create or modify behavior tests before approval.
- It distinguishes project-owned evolution from distribution-managed machinery.

## Seeded behavior exercise

To exercise the complete feature cycle, first put one concrete, disposable observable behavior into the project-owned development plan. Repeat the request without telling the evaluator what design or test to propose. After approving that disposable behavior, continue through expected red, focused green, complete verification, artifact evidence, and a path-limited commit.

Record any failure as packaging evidence rather than coaching the evaluator mid-run.
