# CodeCraft Working Agreement

Date: 2026/09/29

Last revised: 2026/10/02

## Purpose

This artifact records the collaboration agreements for developing the Java version of the RPG Combat kata. It does not authorize planning or implementing kata behavior.

## Collaboration

- We work collaboratively and revise this agreement together as experience reveals better practices.
- Codex challenges assumptions, identifies ambiguity, and raises mistakes early.
- We explicitly authorize transitions from discussion to planning and from planning to implementation.
- An approved implementation slice may be completed and verified without repeated permission, except where this agreement defines a human checkpoint.

## Outside-In Test-Driven Development

- Every behavior change and defect fix starts with a failing test.
- Development proceeds outside-in: begin with high-level behavior, then use focused tests to drive the implementation.
- Pure refactoring begins green, preserves behavior, and ends green; it does not require an invented failing test.
- Tests follow Arrange, Act, Assert, separated structurally with blank lines rather than comments.
- Every test has exactly one behavioral Act.
- Multiple assertions are permitted when they describe one cohesive observable outcome.
- Test method names use Java camel case and begin with `should`, such as `shouldReduceHealthWhenAttacked`.

## BDD Characterization Tests

- High-level behavior tests have `_bdd` at the end of their filename.
- BDD tests exercise public behavior and avoid implementation details.
- BDD tests use real domain objects and never use mocking frameworks.
- BDD tests may use ApprovalTests, JUnit assertions, or a mixture, according to which most clearly expresses the behavior.
- ApprovalTests are suitable for rich state, narrative output, and related observations. JUnit assertions are suitable for concise behavioral outcomes.
- A negative capability requirement already made impossible by segregated public protocols is recorded as a type-level design constraint rather than forcing a no-op API or reflection-based BDD. Reclassifying an item this way requires human agreement and an explicit roadmap annotation.
- Before creating a BDD test, Codex presents every proposed test in a grid whose columns are `Element Number`, `Behavior`, `Arrange`, `Act`, and `Assert`.
- Element Numbers begin at 1 in proposed execution order and remain the human's row references until a revised grid explicitly supersedes the proposal.
- The grid contains exact enough setup, message, and observation details to assess the public design. Exact Java source and expected-red evidence are shown below it, keyed by Element Number.
- When the human requests a change by Element Number, Codex revises the proposal and re-presents the complete grid before seeking approval.
- Human confirmation is not required for the act of creating a new BDD test after its design is approved.
- After creating the BDD test, Codex runs it, shows the expected red failure, and pauses for human review before writing focused tests or production code.
- The human may instead approve a finite ordered batch containing each test's exact source and expected red evidence.
- Within an approved batch, Codex may continue past an outside red only when the source and failure match the manifest exactly.
- Batch features remain sequential: complete one feature and restore the full green suite before creating the next BDD test.
- A responsibility review follows every green batch entry. If learning invalidates a later entry's receiver, ownership, API, source, or assertion, Codex stops and collaborates on a revised batch rather than continuing mechanically.
- Codex pauses when a batch test is unexpectedly green, has a different red, differs from its approved source, or would change the API, assertion, or order.
- Modifying or deleting an existing protected BDD asset requires explicit human approval.

Protected BDD assets include:

- Existing `*_bdd.java` files
- Approval, golden, snapshot, and expected-output files used by BDD tests
- BDD-specific fixtures and test resources
- The protection hook, protected-file registry, and their configuration

## Test Doubles and Nullables

- Mocking frameworks are prohibited.
- Handwritten test doubles are allowed when they improve a test without coupling it to implementation details.
- Prefer sociable, state-based tests over interaction verification.
- James Shore's Nullable pattern applies when production code reaches infrastructure or external state.
- A Nullable is a real production object whose external communication can be disabled while its other behavior remains normal.
- Configurable responses and output tracking may make Nullable collaborators observable in tests.
- Nullable behavior is not added preemptively to pure RPG domain objects.

## Human Protection for Existing BDD Assets

- Protection must be technical as well as instructional.
- Existing protected assets are read-only to the normal agent sandbox.
- A trusted project-local pre-tool hook guards edits made through patch and shell tools, distinguishes creation from modification, and protects its own configuration.
- Recognized read-only `sed`, `rg`, and `git diff` inspection proceeds without approval and does not create or replace pending authorization state.
- Newly created BDD assets are automatically enrolled in protection.
- Changing an existing protected asset requires a visible native approval from the human.
- Approval is narrow, change-specific, and single-use. Blanket approval is not permitted.
- Before the first protected mutation attempt, Codex records the exact normalized tool-name and tool-input digest with the project-local preparation command. Preparation alone grants no permission.
- A standalone `approve`, `a`, `yes`, or `y` authorizes only that prepared digest.
- PreToolUse reserves matching authorization. PostToolUse consumes it after success, releases the reservation while retaining approval after a harmless failure, and consumes it with visible feedback after a partial protected mutation.
- A batch approval is finite, ordered, exact-source, and single-use rather than blanket permission.
- Project-local manifests under `.codecraft/bdd-batches/` record approved batches and are themselves protected assets.
- Unapproved, altered, replayed, or out-of-order BDD creation is denied by the protection hook.
- The exact expected-red verifier and Git staging or commit of unchanged consumed batch assets proceed without redundant approval. Any source, order, registry, batch-state, or staged-path mismatch remains blocked.
- The human approves or denies through the Codex interface and does not need to run an authorization command.
- Hooks are treated as guardrails rather than the sole security boundary; sandbox permissions provide the stronger enforcement layer.

## Definition of Done

A feature is done only when:

- Its relevant BDD characterization test passes.
- The entire test suite passes.
- All applicable quality checks pass.
- No previously working behavior is broken.

## Smalltalk-Style Object-Oriented Design

- Encapsulate state and expose behavior.
- Follow Tell, Don't Ask.
- Use small, cohesive methods and classes.
- Name messages in the language of the domain.
- Prefer polymorphism to type checks and large conditionals.
- Prefer composition and delegation to inheritance.
- Avoid getters and setters that merely expose internal state.
- Follow the Law of Demeter and communicate with immediate collaborators.
- Replace meaningful primitives with value objects when they carry domain meaning.
- Avoid global services and static mutable state.
- Prefer immutable value objects where mutation is unnecessary.
- Separate object construction from domain behavior when construction becomes complicated.
- Domain query methods are permitted when they express genuine domain concepts.

## Responsibility-Driven Design

- Every object has a job that can be stated in one sentence using domain language.
- Before approving a public design, ask: What is the receiver's job? Who owns the information? Who decides the rule? Who changes the state?
- Put behavior with the object that owns the knowledge needed to perform it.
- A coordinating object may preserve expressive public messages while delegating the decision and state change to the responsible collaborator.
- Do not duplicate ownership merely to make a message convenient. Introduce an explicit collaborator when no existing object can own the relationship coherently.
- After every green feature, ask whether the change added a second job, a new category of state, or knowledge belonging to another object.
- Record learned responsibilities and unresolved ownership questions in `emergent/design/responsibility-map.md`. The map is provisional and changes only from observed design pressure or explicit collaboration.
- Static quality checks may coach about structural symptoms, but the human and Codex make semantic responsibility decisions together.

## SOLID and Dependency Direction

- Apply all five SOLID principles during design and after every green change.
- Single Responsibility: each object has one job and one primary reason to change.
- Open/Closed: place expected variation behind domain messages rather than conditionals in a coordinating object.
- Liskov Substitution: every implementation honors the behavioral promises of its protocol.
- Interface Segregation: a client depends only on the cohesive messages it needs.
- Dependency Inversion: policy objects depend on protocols, while concrete construction occurs at an external composition boundary.
- An object does not instantiate a collaborator with a separate domain job. That collaborator is supplied through construction or another explicit injection boundary.
- A factory or composition root may choose concrete implementations and configuration values; it does not own their domain behavior.
- Constructing an internally owned value, immutable detail, or private collection is not by itself a dependency-inversion violation.
- Before accepting a design, identify the dependency abstraction, concrete implementation, injection point, and composition root.
- Do not introduce an interface merely to satisfy a shape rule. Its messages must form a cohesive protocol used by a client, and observed design pressure must justify the dependency boundary.

## Simplest Design and Emergent Design

- Implement one approved observable behavior at a time.
- Make the smallest production change that passes the current test while preserving the entire green suite.
- "Simplest" means easiest to understand and change for the behavior that exists, not merely the fewest lines of code.
- Apply the four rules of simple design in priority order:
  1. Passes all tests.
  2. Reveals intent.
  3. Contains no knowledge duplication.
  4. Uses the fewest necessary design elements.
- Let design emerge through repeated red, green, and refactor cycles.
- Refactor only while green and keep every refactoring behavior-preserving.
- Introduce an abstraction, value object, collaborator, configuration option, or extension point only when current behavior or observed duplication creates evidence for it.
- Do not design for hypothetical future kata requirements.
- Temporary duplication may remain while a pattern is still uncertain; remove it when the shared concept becomes clear.
- Reassess the design after every green step and make the smallest justified refactoring before starting the next behavior.

## Comment Policy

- Handwritten Java should be self-documenting.
- Comments are permitted only as explicit apologies for a design that could not be made clear in code.
- The apology must identify the specific clarity problem, use a `YYYY/MM/DD` date, and identify its author.
- Codex-authored comments use this exact form:

```java
// I'm sorry that I could not make this clearer: <specific reason>. 2026/09/29 — Codex, unworthy.
```

- The date in a new apology reflects the date it is written.
- An apology comment is visible design debt and triggers coaching toward a clearer design.
- The word `unworthy` is not attached to a human contributor's name by Codex.

## Habit Hooks and Quality Coaching

- Habit Hooks provide localized, actionable coaching rather than bare linter errors.
- Project-local coverage coaching reads the current JaCoCo report after tests, lists changed-code findings before existing baseline findings, and emits a numbered review grid.
- Missing coverage is contextual coaching rather than a completion gate. A finding may indicate missing observable behavior, a focused test gap, unnecessary API, an overly broad protocol, or an intentional deferral.
- Never add a test solely to increase a coverage percentage. Classify the finding collaboratively and follow the applicable behavior, focused-test, refactoring, or review-decision workflow.
- Objective rules may block completion; contextual design judgments begin as coaching.
- Methods may contain at most seven executable lines. Signatures, annotations, braces, blank lines, and formatting do not count.
- Non-apology comments in handwritten Java are prohibited.
- Objective checks also guard against deep nesting, public mutable fields, and static mutable state.
- Coaching highlights excessive parameters, excessive class size, state-exposing accessors, domain `instanceof` or `switch` selection, long message chains, primitive obsession, and weak cohesion.
- Thresholds not explicitly settled by this agreement remain coaching checks until collaboratively promoted to blocking rules.

## Workflow Automation Testing Boundary

- Test executable safety boundaries, state transitions, fail-closed behavior, and machine-consumed contracts.
- Do not add tests merely to pin explanatory prose, formatting preferences, conversational wording, or human judgment.
- A schema, command-line contract, protected-path rule, or persisted state format is machine-consumed and may warrant focused tests.
- Prefer one contract test over several wording-level assertions that protect the same risk.
- Human approval, responsibility ownership, design quality, and coaching dispositions remain collaborative judgments rather than automated assertions.

## Visual Diff Feedback

- Beyond Compare is an optional review surface for proposed modifications to existing code or tests.
- When the human and Codex agree to use it, Codex may open the current and proposed versions after obtaining the required native application permission.
- The human may communicate feedback in conversation or save edits into the workspace; Codex reinspects saved edits before continuing.
- A Beyond Compare review is not approval to alter a protected BDD asset and never replaces the exact, single-use protection workflow.

## Emergent Automation

- The first time we perform a task, we do it and save an artifact describing the intent, approach, commands, result, decisions, and challenges.
- The second similar task is performed and documented independently.
- Artifact names are not reused. Similar artifacts add a numeric suffix, such as `task-name.md`, `task-name-2.md`, and `task-name-3.md`.
- Artifacts live under the project-local path that owns their purpose: workflow, programming-process, and skill-evolution work in the repository-root `automation/` directory; behavior work in `emergent/features/`; architecture and responsibility records in `emergent/design/`; and resumable handoffs in `emergent/sessions/`.
- On the third similar task, Codex recognizes the pattern, compares the artifacts, and proposes versioned automation.
- We collaborate on the automation, then complete the third task using that automation.
- Emergent automation uses Semantic Versioning beginning at `0.1.0`.
- Fixes increment the patch version. Behavioral expansions increment the minor version.

## Workflow Status, Evidence, and Review Decisions

- The project-local status command is read-only and reports roadmap progress, active approved batches, pending contextual reviews, and Git dirty-state counts.
- Artifact drafting combines human-owned evidence with exact approved batch facts and a current verification receipt. It never runs verification, invents semantic conclusions, checks a roadmap item, or marks an artifact complete.
- Draft output is create-only, limited to Markdown files under `emergent/features/`, and cannot overwrite existing artifacts or other repository content.
- One canonical schema owns the feature-artifact template, renderer, and validation shape.
- Completion validation fails closed when required evidence is missing, the receipt is missing, expired, stale, or mismatched, the exact roadmap item is unchecked, or the artifact has not been human-reviewed as complete.
- Contextual Habit Hooks and structural-review coaching is recorded as pending before completion. Compatible suggestions are presented in one numbered grid and their approved dispositions are recorded atomically.
- Accepting coaching records direction only. It never triggers a refactor, modifies protected assets, or bypasses the feature-cycle checkpoints.

## Active Run State

- One CLI-managed active run provides durable operational memory for one coherent increment or one BDD batch entry.
- The ignored run record owns the current workflow stage, deterministic checkpoints, typed attention items, next actor, next action, and the narrow context paths needed for that action.
- AI and deterministic processes mutate run state only through `.codecraft/bin/codecraft_run.py`; they do not edit its JSON files directly.
- Pending `ai-judgment`, `human-approval`, and `unexpected-failure` attention blocks stage advancement until its resolution is recorded.
- A run record is a routing and resumption aid. It cannot grant protected-change authorization, approve a design, replace a batch manifest, replace a signed verification receipt, or overrule Git and committed evidence.
- Run state fails closed when malformed or symlinked and reports a changed base commit so the task can be reassessed rather than continued from stale context.
- Active state remains local and ignored. Durable outcomes are promoted into the normal committed feature or automation evidence, and the run completes only after its coherent commit exists.

## Completion Lanes and Verification Receipts

- Every increment explicitly selects the `behavior`, `refactoring`, `automation`, or `documentation` completion lane.
- Mixed increments use the lane with the stronger applicable gates; lane selection never justifies splitting a coherent change or skipping a material check.
- Behavior, refactoring, and automation lanes run the full Maven verification gate. Automation also validates affected project skills. Documentation is limited to prose with no executable, test, skill, rule, or build effect.
- A successful lane verifies an isolated `HEAD` plus an explicit list of coherent candidate paths and writes an ignored, signed, short-lived receipt containing the repository and base commit, exact candidate identity, configured commands and inputs, completion time, and material-input fingerprint.
- The committer checks the receipt against the exact staged material blobs, uses a path-limited commit so unrelated staged work cannot enter, and verifies the resulting commit tree. Verification reruns when the receipt is absent, expired, invalid, or mismatched.
- Feature artifacts, roadmap checkmarks, review dispositions, and narrowly named `automation/*-evidence.md` records are the only evidence-only outputs allowed beside a verified candidate. The existing completion-flow optimization record is an explicit legacy exception. Governing automation remains material. Evidence paths use a separate validated list and do not require another build when material inputs remain unchanged.

## Structural Review

- `./mvnw verify` runs the project-local Java structure review.
- A structural review becomes due after three newly completed roadmap behaviors, when a Java package exceeds its configured file limit, or when production packages form a dependency cycle.
- The analyzer inventories declared Java packages and their dependencies; it does not move files or choose architectural boundaries.
- A due review blocks completion until the human and Codex assess responsibilities, dependency direction, and the smallest justified organization change.
- Reorganization is a green, behavior-preserving refactor and follows the protected-BDD and visual-diff agreements.
- After an approved review, the project-local baseline records the reviewed behavior count. File limits may be tightened collaboratively as the design becomes clearer.

## Git

- Commits use Arlo notation.
- Work is committed in small, coherent increments.
- We commit only when the full required test and quality gates are green.
- Red tests are never committed.
- Feature tests and the implementation that makes them pass therefore belong to the same green increment.
- Refactoring is committed separately when doing so preserves a coherent green history.
- The committer skill must be project-local and self-contained before it is used.
- Commit review checks the applicable verification receipt rather than repeating an unchanged green gate.

## Build and Continuous Integration

- Java 25 is the project and CI contract.
- Maven Wrapper is the canonical build entry point.
- Behavior, refactoring, and automation completion lanes invoke `./mvnw verify`; CI continues to invoke the complete gate directly.
- uv uses the ignored repository-local `.uv-cache` configured in `pyproject.toml`; verification must not require access to a home-directory cache.
- Python verification dependencies are locked in `uv.lock`. Bootstrap an empty local cache with `uv sync --frozen`; a warm cache must support `UV_OFFLINE=true ./mvnw verify`.
- Project-local skill validation runs through the locked uv environment rather than undeclared system Python packages.
- GitHub Actions configuration lives at `.github/workflows/Build-and-test.yml`.
- The workflow runs on every push, every pull request, and manual `workflow_dispatch` invocation.
- CI runs the complete Java test suite and all applicable quality gates.

## Locality

- All authored skills, hooks, rules, automation, and supporting instructions live inside this project.
- Project automation must not depend on a system-level, home-directory, or root-level instruction file.
- If a required authored resource exists outside the project, it is copied into the project and made self-contained before use.
- Codex may maintain unavoidable runtime and trust metadata outside the project, but project automation does not use those files as its source of truth.

## Portable Distribution

- The reusable Java/Maven workflow distribution lives under `automation/codecraft-starter/` and remains independent of RPG Combat behavior, manifests, protected paths, and evidence.
- Distribution-managed files contain reusable machinery and shared AI instructions. Project-owned files contain local configuration, agreements, plans, responsibility maps, review decisions, and protected-asset state.
- Installation and upgrade are conflict-safe: they may append a named instruction block and missing ignore entries, but they never silently replace an existing managed file or overwrite project-owned evolution.
- Every distribution change runs package integrity checks, clean-room installation and upgrade tests, installed-skill validation, protected-approval tests, and isolated receipt-to-commit verification.
- Build-specific Java quality integrations are supplied as an adapter for explicit reconciliation with an existing POM; the installer does not rewrite an unknown build automatically.
- A release is not considered generally proven until the documented fresh-model forward test has been performed in a disposable repository.
