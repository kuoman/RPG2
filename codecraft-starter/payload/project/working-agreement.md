# CodeCraft Working Agreement

Project: {{PROJECT_NAME}}

This file is project-owned. Adapt it through explicit collaboration and preserve local decisions during distribution upgrades.

## Collaboration

- Work in small human-approved slices and raise ambiguity or mistakes early.
- Approval to implement one slice does not authorize unrelated behavior or protected-file changes.
- Present BDD proposals as a grid with `Element Number`, `Behavior`, `Arrange`, `Act`, and `Assert`.
- Accept `approve`, `a`, `yes`, and `y` only where the active workflow has prepared an approval checkpoint.

## Outside-in development

- Behavior changes and defect fixes start with a failing public behavior test.
- After the expected outside red is reviewed, use focused tests to drive the smallest production steps.
- Pure refactoring starts green, preserves behavior, and ends green.
- Tests use Arrange, Act, Assert with one behavioral Act.
- Public behavior tests use real domain objects and avoid mocking frameworks.

## Responsibility-driven design

- Every object has one job expressible in domain language.
- Ask who owns the information, who decides the rule, who changes state, and which object coordinates.
- Encapsulate state; prefer behavior, delegation, polymorphism, cohesive protocols, and Tell, Don't Ask.
- Apply all SOLID principles. A policy object receives collaborators with separate jobs; a composition root chooses concrete implementations.
- Do not add an interface, extension point, or abstraction without current design pressure.
- Reassess responsibilities after every green behavior.

## Protected behavior assets

- Existing BDD tests, expected output, fixtures, the protected registry, and protection machinery require narrow human approval before modification or deletion.
- New BDD tests require approved design and are automatically enrolled after creation.
- Approval is exact and single-use. A changed command or patch requires new approval.
- Protection hooks are guardrails and do not replace the model's responsibility to respect authorization boundaries.

## Quality coaching

- Enforced findings block completion and must be resolved.
- Contextual findings are recorded, discussed, and assigned `accept`, `defer`, or `reject` by the human.
- Coverage is advisory. Distinguish missing behavior from unnecessary API or an overly broad protocol; never add tests solely to increase a percentage.

## Evidence and evolution

- Store feature evidence under `emergent/features/`, design records under `emergent/design/`, workflow evidence under `automation/`, and resumable handoffs under `emergent/sessions/`.
- First and second occurrences of a workflow task are performed and documented independently.
- On the third similar occurrence, compare evidence and propose versioned automation.
- Test executable safety boundaries and machine-consumed contracts, not prose or human judgment.
- Distribution-managed machinery may be locally forked only deliberately; project-owned configuration, agreements, and evidence evolve normally.

## Active run state

- One ignored CLI-managed run record provides operational memory for one coherent increment or BDD batch entry.
- It records stage, deterministic checkpoints, typed attention, next actor, next action, and narrow context paths.
- Pending attention blocks advancement. Only the run CLI mutates its JSON state.
- Run state routes work but never grants approval or replaces Git, protected-change state, signed receipts, or committed evidence.

## Completion

- Use the configured completion lane with an exact candidate path list.
- Behavior, refactoring, and automation lanes run the project's complete verification command: `{{VERIFY_COMMAND_JSON}}`.
- Verification occurs in an isolated Git worktree and creates a short-lived receipt bound to candidate content.
- Commits are green, path-limited, use Arlo notation, and preserve unrelated work.
- Never push without explicit human authorization.

## Locality

- All authored instructions, skills, hooks, rules, and automation required by this workflow live in this repository.
- Runtime metadata may live in Git's internal directory, but no home-directory instruction file is a source of truth.
