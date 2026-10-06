# CodeCraft Interaction Log

Purpose: preserve the interaction and interruption evidence needed to identify safer automation opportunities that reduce human round trips.

## Fields

- **Point**: stable chronological identifier.
- **Type**: human checkpoint, human instruction, or tool interruption.
- **Stage**: CodeCraft stage when the interaction occurred.
- **Trigger**: fact or rule that caused the interaction.
- **Request or event**: the exact decision requested or interruption observed.
- **Response**: the human or tool response.
- **Resulting authorization or action**: what became permitted or what changed.
- **Automation evidence**: data useful when considering future automation.

## Interaction points

### IP-001 — Workflow kickoff

- **Type:** Human instruction
- **Stage:** Before run creation
- **Trigger:** The repository was presented with explicit `AGENTS.md` instructions to use project-local CodeCraft and stop before implementation at the required checkpoint.
- **Request or event:** Assess the next planned behavior without implementing it.
- **Response:** The assistant loaded the working agreement, CodeCraft skill, project configuration, response conventions, active-run guidance, feature-cycle guidance, plan, and responsibility map. `codecraft_run.py resume --json` returned `{"active": false}`.
- **Resulting authorization or action:** Read-only assessment was authorized; implementation was not.
- **Automation evidence:** A single assessment/bootstrap command could load the mandatory files, resume state, validate configuration, and summarize the next checkpoint.

### IP-002 — Application-module boundary

- **Type:** Human checkpoint
- **Stage:** Before run creation
- **Trigger:** `.codecraft/project.json` targeted root `src/...` and root `./mvnw verify`, while the only RPG production and test code lived under `java/src/...` with `java/pom.xml`.
- **Request or event:** “Should CodeCraft target the existing `java/` module?”
- **Response:** `yes`
- **Resulting authorization or action:** The `java/` module became the selected application boundary. No behavior implementation was authorized by this response.
- **Automation evidence:** CodeCraft Doctor reported healthy despite configured source/test roots containing no application code. A project-content alignment check could detect this mismatch and propose the sole populated Maven module.

### IP-003 — First behavior design

- **Type:** Human checkpoint
- **Stage:** Design
- **Trigger:** The feature cycle requires approval of an exact public BDD design before creating a new protected BDD test. The smallest prerequisite behavior was character creation rather than damage.
- **Request or event:** Approve Element 1: a newly created character starts with 1000 health and is alive, observed through `PlayerCharacterPrinter`, plus the `java/` module configuration prerequisite.
- **Response:** `a`
- **Resulting authorization or action:** Authorized configuration alignment, creation of `CharacterCreation_bdd.java`, creation of its exact approved output, and execution to the expected outside red. Damage behavior and production implementation remained unauthorized until later checkpoints.
- **Automation evidence:** The approval carried a stable element number, exact test source, expected output, expected failure, candidate paths, and explicit exclusions. These fields are suitable for a machine-readable approval manifest.

### IP-004 — Run-start scope format rejection

- **Type:** Tool interruption
- **Stage:** Design
- **Trigger:** `codecraft_run.py start --scope` accepts repeatable `key=value` entries, but its help output labels the option only as `--scope SCOPE`.
- **Request or event:** The first start command supplied a prose scope.
- **Response:** `CodeCraft run error: scope must use key=value`
- **Resulting authorization or action:** No run was created. The command was retried with `element=1`, `module=java`, and `behavior=character-creation`, after which the run started.
- **Automation evidence:** Improve CLI help and argument validation examples; a structured wrapper could translate a prose scope into explicit keys.

### IP-005 — Protected read-only inspection blocked

- **Type:** Tool interruption
- **Stage:** Design
- **Trigger:** After new BDD assets were automatically enrolled, a shell command chained Doctor, `git diff --check`, `git diff`, and `sed` with `&&`. The protection hook treats chained commands as non-read-only.
- **Request or event:** Inspect the approved changes and protected registry.
- **Response:** The hook blocked the combined command and requested standalone approval.
- **Resulting authorization or action:** No files changed. The checks were split into separate read-only commands and all passed.
- **Automation evidence:** The workflow could provide a protected-safe inspection command or teach orchestration to split read-only checks before invoking the shell.

### IP-006 — Interaction-log request

- **Type:** Human instruction
- **Stage:** Design, before outside-red execution
- **Trigger:** The human wants evidence for mining automation opportunities and reducing future interaction count.
- **Request or event:** Track all interaction points, triggers, responses, and relevant supporting data in a separate `interations.md` file throughout the process.
- **Response:** Accepted; the exact requested filename is used.
- **Resulting authorization or action:** This log was created and will be updated at each subsequent human checkpoint or material workflow interruption.
- **Automation evidence:** Interaction logging itself may be automated from run-state transitions, approval manifests, CLI failures, and hook events; human intent and decision rationale still need concise capture.

### IP-007 — Protected paths blocked in run metadata

- **Type:** Tool interruption
- **Stage:** Design to outside-red transition
- **Trigger:** `codecraft_run.py advance` included the protected BDD test and approval-output paths as read-only context metadata. The protection hook treats path mentions supplied to tools other than its recognized read-only shell commands as potential protected changes.
- **Request or event:** Advance the ignored run record to `outside-red` while referencing the approved test assets as context.
- **Response:** The hook blocked the command and requested standalone approval.
- **Resulting authorization or action:** No run state or repository file changed. The transition will be retried without protected paths in run metadata; the already-approved files remain unchanged.
- **Automation evidence:** Protection should distinguish path metadata from mutation targets, or the run CLI should accept protected asset identifiers through a hook-recognized read-only channel.

### IP-008 — Java release mismatch before outside red

- **Type:** Tool interruption requiring human direction
- **Stage:** Outside-red
- **Trigger:** The selected `java/pom.xml` compiles for Java 22, while the available command-line JDK is OpenJDK 21.0.10. `/usr/libexec/java_home -V` found no additional macOS-registered JDK.
- **Request or event:** `./mvnw -f java/pom.xml -Dtest=CharacterCreation_bdd test`
- **Response:** Maven failed before test compilation with `invalid target release: 22`; therefore the expected missing-`PlayerCharacterPrinter` red was not reached.
- **Human response:** `yes`
- **Resulting authorization or action:** The response authorized changing only the Maven compiler source and target from 22 to 21 and retrying the same outside-red command. The run remains at `outside-red` until that retry produces valid behavior evidence. No production code changed.
- **Automation evidence:** CodeCraft Doctor could compare Maven compiler source/target/release with the active JDK before approving or executing a behavior cycle. The likely narrow correction is changing the module compiler source and target from 22 to 21, consistent with the repository root POM.

### IP-009 — Approval-alias requirement

- **Type:** Human instruction
- **Stage:** Outside-red
- **Trigger:** The human wants low-friction checkpoint responses.
- **Request or event:** Ensure prepared approval and confirmation checkpoints accept `approve`, `a`, `yes`, and `y`.
- **Response:** Accepted. The project working agreement already defines exactly these aliases.
- **Resulting authorization or action:** Every subsequent prepared checkpoint in this run will explicitly advertise and accept all four aliases.
- **Automation evidence:** Approval prompts can be generated from a shared alias set in project configuration so every host and checkpoint presents identical accepted responses.

### IP-010 — Expected outside-red confirmation

- **Type:** Human checkpoint
- **Stage:** Outside-red
- **Trigger:** After the approved Java 21 correction, the BDD test reached the predicted failure: test compilation cannot find `PlayerCharacterPrinter`. CodeCraft requires human review of this outside red before focused tests or production implementation.
- **Request or event:** Confirm that `cannot find symbol: class PlayerCharacterPrinter` is the expected red for Element 1.
- **Response:** `a`
- **Resulting authorization or action:** The expected outside red was confirmed. Run attention `confirm-outside-red` may be resolved and the approved Element 1 slice may advance to focused-test-driven implementation.
- **Automation evidence:** Expected-red signatures from the approved design can be compared mechanically with build output; the human checkpoint could then show only the matched signature and any deviations.

### IP-011 — Pre-existing failing damage seed blocks completion

- **Type:** Human checkpoint
- **Stage:** Implementation, after Element 1 became green
- **Trigger:** The focused `PlayerCharacterStateTest` and protected `CharacterCreation_bdd` pass, but full `./mvnw -f java/pom.xml verify` fails on the repository's pre-existing `PlayerCharacterTest.dealDamage` approval seed. That behavior is outside Element 1 and has no approved output. The failed approval also attempted to launch IntelliJ, generated an empty protected `.approved.txt`, and generated a `.received.txt`. Default Surefire discovery skipped `*_bdd.java` in the full run.
- **Request or event:** Approve a consolidated baseline-hygiene patch: explicitly disable the future damage seed with a reason; configure ApprovalTests to use `JunitReporter`; configure Surefire to include standard tests and `*_bdd.java`; delete only the two failure-generated damage approval artifacts.
- **Response:** `a`
- **Resulting authorization or action:** Authorized the exact four-part baseline-hygiene patch: disable the future damage seed with an explicit reason, use `JunitReporter`, include standard and `*_bdd.java` tests in Surefire, and delete only the two failure-generated damage approval artifacts.
- **Automation evidence:** A bootstrap baseline lane could detect intentionally failing seed tests, GUI-capable reporters, generated approval artifacts, and BDD discovery mismatch before the first behavior approval. Presenting one exact hygiene manifest avoids four separate interactions.

### IP-012 — Exact protected-patch digest confirmation

- **Type:** Human checkpoint caused by protection machinery
- **Stage:** Implementation, baseline hygiene
- **Trigger:** The human approved the four-part hygiene manifest, but the protection hook could not bind that approval until the exact `apply_patch` payload attempted to delete the empty protected approval file and generated a digest.
- **Request or event:** Confirm the same exact patch a second time after its digest was prepared.
- **Response:** `a`
- **Resulting authorization or action:** The exact patch was applied once. No BDD test or approved Element 1 output was modified.
- **Automation evidence:** Preparing an exact protected-change digest before the first human approval would collapse the descriptive approval and digest-binding approval into one interaction.

### IP-013 — Isolated worktree sandbox escalation

- **Type:** Tool/environment interruption
- **Stage:** Verification
- **Trigger:** The completion lane creates a temporary detached Git worktree. The initial sandboxed execution could not create `.git/worktrees/repository` and failed with `Operation not permitted`.
- **Request or event:** Rerun the same completion command with permission to create and remove the temporary isolated worktree.
- **Response:** The managed escalation was approved.
- **Resulting authorization or action:** The isolated behavior lane ran successfully and issued a signed receipt. Because this log is itself a candidate path, verification is rerun after recording this entry so the final receipt binds the complete log.
- **Automation evidence:** The CodeCraft completion command could declare its temporary-worktree permission requirement up front, avoiding one failed attempt and escalation round trip.

### IP-014 — Interaction-log changes invalidated verification

- **Type:** Workflow interruption resolved without human direction
- **Stage:** Verification
- **Trigger:** `interations.md` was initially an executable candidate path, so recording IP-013 changed the candidate digest after a successful completion run and required another verification.
- **Request or event:** Preserve ongoing interaction logging without repeatedly invalidating executable verification.
- **Response:** Classify `interations.md` as an allowed evidence-only path, matching the existing treatment of the development plan and feature evidence.
- **Resulting authorization or action:** The interaction log remains part of commit evidence but no longer changes the verified Java/build candidate digest. The completion lane is rerun once for the revised configuration and candidate manifest.
- **Automation evidence:** Workflow-generated narrative logs should default to evidence-only classification; executable candidate manifests should contain only behavior, tests, and material build/workflow inputs.

### IP-015 — Verified increment commit handoff

- **Type:** Human checkpoint
- **Stage:** Commit
- **Trigger:** The final isolated behavior lane passed and issued candidate digest `sha256:eb189942251bc9dfcbd4afd86f4639fd163b8211c6c3eecc66163d44d92581a6`. CodeCraft keeps the run active until a coherent commit exists, and committing requires explicit human authorization.
- **Request or event:** Decide whether to create a path-limited commit for the verified candidate plus its evidence, without pushing.
- **Response:** `a`
- **Resulting authorization or action:** Authorized a path-limited Arlo-formatted commit containing exactly the verified candidate and allowed evidence manifests. Push remains unauthorized.
- **Automation evidence:** Exact candidate/evidence manifests and a current signed receipt allow commit review to omit repeated build output while preserving path isolation in a dirty worktree.

### IP-016 — Protected assets blocked during staging

- **Type:** Human checkpoint caused by protection machinery
- **Stage:** Commit
- **Trigger:** The exact path-limited `git add` includes the already-approved protected BDD test and its approved output. Although staging does not change their working-tree content and the commit was approved, the protection hook requires a digest-bound standalone confirmation for the staging command.
- **Request or event:** Confirm the exact prepared `git add` command for the 16 candidate paths and three evidence paths.
- **Response:** `a`
- **Resulting authorization or action:** Authorized the exact prepared `git add` command for the verified candidate and evidence manifests. Push remains unauthorized.
- **Automation evidence:** Protected-change authorization could distinguish content mutation from staging already-approved bytes, or the commit approval manifest could pre-authorize its exact staging command.

### IP-017 — Staging approval lost across sandbox escalation

- **Type:** Human checkpoint caused by interacting guardrails
- **Stage:** Commit
- **Trigger:** After IP-016 approval, the exact staging command passed protection but Git could not create `.git/index.lock` inside the sandbox. Retrying with required filesystem escalation changed the protected tool-call digest, so the single-use protected approval no longer matched.
- **Request or event:** Confirm the exact escalated staging command after three failed staging attempts: initial protection block, sandbox denial, and escalated protection block.
- **Response:** `a`
- **Resulting authorization or action:** Authorized retrying the unchanged path-limited staging command with the required filesystem escalation. Push remains unauthorized.
- **Automation evidence:** Protected authorization should bind to the semantic Git command independently of sandbox metadata, or permission escalation should preserve a valid reservation for an unchanged command.

### IP-018 — Commit refused for unrelated workflow migration

- **Type:** Human checkpoint raised by commit review
- **Stage:** Commit
- **Trigger:** Exact staged-diff review showed that the verified manifest would replace the repository's existing 281-line working agreement with the new 70-line agreement and commit only a partial subset of the larger pre-existing CodeCraft migration. The resulting commit would mix behavior with unrelated workflow replacement and would not contain all repository-local workflow dependencies.
- **Request or event:** Authorize unstaging exactly the candidate and evidence manifest paths so the index returns to its pre-commit-review state; preserve all working-tree files and all unrelated staged changes.
- **Response:** `a`
- **Resulting authorization or action:** Authorized restoring exactly the candidate and evidence manifest paths to their pre-review index state while preserving all working-tree files and unrelated staged work. No commit or push is authorized by this recovery approval.
- **Automation evidence:** Completion-lane candidate construction should compare every path with both `HEAD` and the pre-run index, rejecting files that contain substantial pre-existing changes or belong to an uncommitted workflow foundation.

### IP-019 — Index-recovery digest confirmation

- **Type:** Human checkpoint caused by protection machinery
- **Stage:** Commit recovery
- **Trigger:** The human approved returning the manifest to its pre-review index state, but the protection hook requires a second confirmation after seeing the exact escalated `git restore --staged` command. The hook also reports the stale registry entry for the already-deleted damage approval file even though that file is not a command path.
- **Request or event:** Confirm the exact escalated index-only recovery command.
- **Response:** `a`
- **Resulting authorization or action:** The exact escalated recovery completed. Candidate and evidence paths returned to their pre-review index states, the working agreement's original staged deletion was restored, all working-tree files were preserved, and unrelated staged work was unchanged.
- **Automation evidence:** Exact recovery commands should be prepared before the descriptive approval, and stale protected registry entries should not broaden unrelated index-only command authorization.

### IP-020 — Workflow-foundation ordering decision

- **Type:** Human checkpoint
- **Stage:** Commit
- **Trigger:** The behavior increment is verified but cannot be committed cleanly while the pre-existing CodeCraft migration is uncommitted. Committing the behavior first would either absorb unrelated migration content or leave repository-local workflow dependencies incomplete.
- **Request or event:** Decide whether to review, verify, and commit the CodeCraft migration as a separate prerequisite increment before regenerating the behavior receipt and commit manifest.
- **Response:** `a`
- **Resulting authorization or action:** Authorized reviewing, verifying, and—only if coherent—committing the pre-existing CodeCraft migration as a separate prerequisite increment without pushing. The behavior run remains intact and must be reverified after any prerequisite commit changes its base.
- **Automation evidence:** Run startup should reject behavior work when its workflow foundation is not committed, or automatically establish a separately approved prerequisite run before behavior design begins.

### IP-021 — Migration commit review refused

- **Type:** Human checkpoint raised by commit review
- **Stage:** Prerequisite migration review
- **Trigger:** The migration is not a coherent staged increment: it spans staged deletions and renames, unstaged starter modifications, and untracked installed files. Required project-owned migration files now also contain Element 1 state, including the development plan, responsibility map, protected registry, and Java-module configuration. No migration-only automation receipt exists, and the active run belongs to the behavior increment.
- **Request or event:** Decide whether to leave commit review and prepare a clean pre-behavior CodeCraft bootstrap snapshot in isolation, preserving the current behavior workspace for later reverification.
- **Response:** `a`
- **Resulting authorization or action:** Authorized leaving commit review and preparing a clean pre-behavior CodeCraft bootstrap snapshot in an isolated worktree. The current behavior workspace and index must remain untouched; no push is authorized.
- **Automation evidence:** Bootstrap installation needs a first-class transactional workflow that snapshots pre-feature project-owned files, verifies the complete installed system, commits it, and only then opens the first behavior run.

### IP-022 — Main-workspace protection leaked into isolated bootstrap

- **Type:** Human checkpoint caused by protection machinery
- **Stage:** Isolated bootstrap preparation
- **Trigger:** The exact bootstrap command targets a detached temporary worktree that contains no protected behavior assets, but the active session hook imported the main workspace's protected registry and treats every Python command as potentially mutating every registered path.
- **Request or event:** Confirm the exact isolated `codecraft_starter.py bootstrap` command after its digest was prepared.
- **Response:** `a`
- **Resulting authorization or action:** Authorized the exact isolated bootstrap command. The main workspace and index remain out of scope, and no push is authorized.
- **Automation evidence:** Protection should resolve registry and paths against the tool call's actual worktree, and isolated commands should not inherit protected paths from another checkout sharing the same Git directory.

### IP-023 — Isolated bootstrap selected macOS Java stub

- **Type:** Human checkpoint caused by environment and protection interaction
- **Stage:** Isolated bootstrap preparation
- **Trigger:** The approved bootstrap ran its preflight but selected the macOS `javac` stub, which reported no Java runtime, even though Homebrew OpenJDK 21 is installed. The bootstrap rolled back its owned writes. Adding explicit `JAVA_HOME` and `PATH` changes the exact command digest and triggers protection again.
- **Request or event:** Confirm the corrected isolated bootstrap command pinned to `/opt/homebrew/opt/openjdk@21`.
- **Response:** `a`
- **Resulting authorization or action:** Authorized the exact JDK-pinned isolated bootstrap command. The main workspace and index remain out of scope; no push is authorized.
- **Automation evidence:** Bootstrap preflight should resolve a working JDK consistently with project verification, or accept a recorded project JDK path so environment correction does not require a new protected-command approval.

### IP-024 — JDK path correction selected legacy Python

- **Type:** Human checkpoint caused by environment and protection interaction
- **Stage:** Isolated bootstrap preparation
- **Trigger:** The IP-023 command narrowed `PATH` enough that `python3` resolved to Apple's legacy interpreter, which lacks the standard-library `tomllib` module required by the starter. The command failed before bootstrap activity. Even a read-only Python version probe was blocked because the main workspace's protected registry leaked into the isolated worktree.
- **Request or event:** Confirm the exact corrected command using `/opt/homebrew/bin/python3` while retaining the approved Homebrew JDK 21 environment.
- **Response:** `a`
- **Resulting authorization or action:** Authorized the exact corrected bootstrap command using `/opt/homebrew/bin/python3` and Homebrew JDK 21. The main workspace and index remain out of scope; no push is authorized.
- **Automation evidence:** Bootstrap should validate and record compatible Java and Python executables before protected execution, while worktree-scoped protection should allow read-only interpreter probes without unrelated behavior approval.

### IP-025 — Corrected bootstrap command required digest preparation

- **Type:** Human checkpoint caused by protection machinery
- **Stage:** Isolated bootstrap preparation
- **Trigger:** IP-024 approved the fully described corrected command, but the protection hook had not first observed that exact command and therefore had no prepared digest to match. The first exact invocation was blocked before execution. This is the third failed bootstrap attempt, so the workflow pauses for direction.
- **Request or event:** Confirm retrying the now-prepared exact command using `/opt/homebrew/bin/python3` and Homebrew JDK 21.
- **Response:** `a`
- **Resulting authorization or action:** The exact command passed protection and ran, but bootstrap preflight stopped because the narrowed `PATH` hid Maven. No bootstrap-owned installation was written. The isolated worktree still contains only the prepared distribution move and legacy removals; the main workspace and index remain untouched, and no push is authorized.
- **Automation evidence:** The protection layer should expose a non-executing prepare operation, or accept an exact command presented at a human checkpoint without requiring a deliberately blocked execution first.

### IP-026 — Bootstrap environment omitted Maven

- **Type:** Human checkpoint caused by environment and protection interaction
- **Stage:** Isolated bootstrap preparation
- **Trigger:** The IP-025 command passed protection and reached preflight, but its narrowed `PATH` omitted Homebrew Maven. A read-only probe confirmed Maven 3.9.12 at `/opt/homebrew/bin/mvn` running on Homebrew JDK 21. Adding `/opt/homebrew/bin` changes the protected command digest; the exact corrected invocation has now been presented to and blocked by the hook, preparing that digest.
- **Request or event:** Confirm retrying the now-prepared exact bootstrap command with Homebrew Java, Python, and Maven all visible.
- **Response:** `a`
- **Resulting authorization or action:** The exact corrected command passed protection and began transaction setup, but sandboxing denied creation of a temporary backup beside the shared Git installation key. The required escalated retry changed the tool-call digest and was blocked by protection before execution. No bootstrap files were installed; the main workspace and index remain untouched, and no push is authorized.
- **Automation evidence:** Bootstrap should discover or accept a coherent toolchain environment once, validate Java, Python, and Maven together, and bind protection approval after preflight normalization rather than once per environment correction.

### IP-027 — Isolated bootstrap needs shared-Git-directory access

- **Type:** Human checkpoint caused by interacting sandbox and protection guardrails
- **Stage:** Isolated bootstrap preparation
- **Trigger:** Bootstrap transaction setup snapshots `.git/.codecraft-installation-key`, which resolves to the main repository's shared Git directory outside the temporary worktree. The sandbox denied that write. The policy-required escalated retry was then blocked because escalation metadata changed the protection digest; that exact escalated invocation has now prepared the new digest.
- **Request or event:** Confirm the now-prepared escalated retry of the otherwise unchanged isolated bootstrap command.
- **Response:** `a`
- **Resulting authorization or action:** The exact escalated command completed successfully. The temporary worktree now contains a CodeCraft Starter 0.4.0 bootstrap snapshot for RPG2, and the shared Git installation key was updated transactionally. The main working tree and index remain otherwise untouched; no push is authorized.
- **Automation evidence:** Worktree bootstrap should use worktree-local transaction metadata or receive sandbox access up front, and protection authorization should remain valid when an unchanged semantic command gains required sandbox permission.

### IP-028 — Read-only doctor inherited behavior protection

- **Type:** Human checkpoint caused by protection machinery
- **Stage:** Isolated migration verification
- **Trigger:** The evolution guide requires a package doctor run before adapting project-owned workflow configuration. The isolated checkout has an empty protected registry, but the session hook imported the main worktree's behavior registry and blocked the read-only `.codecraft/bin/codecraft_doctor.py .` command. Its exact digest is now prepared.
- **Request or event:** Confirm running the prepared read-only doctor in the isolated worktree.
- **Response:** `ma` (not a configured confirmation alias), followed by `a`.
- **Resulting authorization or action:** The prepared read-only doctor ran successfully and reported `CodeCraft Starter 0.4.0: healthy`. The main workspace and index remain untouched; no push is authorized.
- **Automation evidence:** Protection should resolve the worktree-local registry and classify doctor/validation commands as read-only so verification does not require behavior-change approval.

### IP-029 — Post-adaptation doctor inherited behavior protection

- **Type:** Human checkpoint caused by protection machinery
- **Stage:** Isolated migration verification
- **Trigger:** After adapting four project-owned files to the existing `java/` module, the evolution guide requires the same read-only doctor check. The prior authorization was exact and single-use, so the session hook again imported the main worktree's unrelated protected behavior registry and blocked the post-change doctor. Its exact digest is now prepared.
- **Request or event:** Confirm running the prepared read-only post-change doctor in the isolated worktree.
- **Response:** `a`
- **Resulting authorization or action:** The prepared post-change doctor ran successfully and reported `CodeCraft Starter 0.4.0: healthy`. The isolated edits affect only project configuration, completion lanes, the working agreement, and CI verification command; no behavior file, main-worktree file, commit, or push is authorized.
- **Automation evidence:** A single workflow-change verification session should authorize repeated read-only doctor checks, or protection should categorically exempt verified read-only commands in an isolated worktree.

### IP-030 — Bootstrap snapshot exposed an incoherent build adapter

- **Type:** Human design and scope checkpoint
- **Stage:** Isolated migration verification
- **Trigger:** The configured RPG2 verification command failed because `java/pom.xml` targets Java 22 while the approved/bootstrap toolchain is Java 21. Independently, the Starter clean-room suite ran 53 tests with 52 passing and one error: moving the package from `automation/codecraft-starter/` to root made its repository lookup climb one directory too far. That test also specifies a `verify-codecraft-starter` Maven execution and automation-lane package fingerprint that the candidate does not contain.
- **Request or event:** Approve a narrow CodeCraft Starter 0.4.1 repair slice in the isolated snapshot: update the moved-package integration test and version metadata; adapt `java/pom.xml` to Java 21, BDD discovery, and the Starter self-test execution; fingerprint `codecraft-starter/**/*` in the automation lane; then upgrade the isolated installation and rerun all gates.
- **Response:** `a`
- **Resulting authorization or action:** Authorized the narrow CodeCraft Starter 0.4.1 repair slice in the isolated snapshot. Behavior files remain out of scope; no commit or push is authorized by this design approval.
- **Automation evidence:** Bootstrap/install should validate the target's configured verification command and distribution-location integration before declaring success, and a package move should carry a tested migration that updates repository-relative contracts atomically.

### IP-031 — Isolated 0.4.1 upgrade inherited behavior protection

- **Type:** Human checkpoint caused by protection machinery
- **Stage:** Isolated migration implementation
- **Trigger:** The approved 0.4.1 repair is green in all 53 clean-room tests and package integrity is healthy. The exact upgrade must update the installed CodeCraft skill metadata and signed installation record, but the session hook imported unrelated protected behavior paths from the main worktree and blocked it before execution. The exact digest is now prepared.
- **Request or event:** Confirm the prepared isolated upgrade from CodeCraft Starter 0.4.0 to 0.4.1.
- **Response:** `a`
- **Resulting authorization or action:** The prepared upgrade completed successfully. The signed installation record and installed CodeCraft skill now both report 0.4.1. Distribution changes remain isolated; behavior files, commits, and pushes remain out of scope.
- **Automation evidence:** Distribution upgrades in an isolated worktree should resolve protection locally, and approval for an already-approved workflow slice should not be broadened by unrelated main-worktree behavior assets.

### IP-032 — Maven cache required sandbox escalation

- **Type:** Automated permission interaction
- **Stage:** Isolated migration verification
- **Trigger:** The first canonical Maven verification could not create the new `exec-maven-plugin` cache directory under the home Maven repository. Policy-required escalation was requested for the unchanged verification command.
- **Request or event:** Allow isolated canonical verification to download the approved Maven plugin and run Java and Starter tests.
- **Response:** Automatically reviewed and permitted by the sandbox approval policy.
- **Resulting authorization or action:** Maven downloaded `exec-maven-plugin` 3.5.0 and reached the Java test suite. Verification then stopped on the pre-existing nondeterministic `PlayerCharacterTest.dealDamage` approval comparison; Starter self-tests had not yet run through Maven.
- **Automation evidence:** Canonical verification should use a repository-local dependency cache or declare its cache-write requirement before the gate begins, avoiding a mid-run sandbox escalation.

### IP-033 — Unapproved damage test blocks the workflow baseline

- **Type:** Human behavior-boundary checkpoint
- **Stage:** Isolated migration verification
- **Trigger:** Enabling modern Surefire correctly discovered the existing `PlayerCharacterTest.dealDamage` test, which compares default object-identity text and fails nondeterministically. The preserved workspace already contains the narrow quarantine: `@Disabled("Pending approved damage behavior")`. Damage is not the approved behavior slice.
- **Request or event:** Confirm applying only that `@Disabled` annotation and import in the isolated prerequisite snapshot, while preserving the protected approval output and making no production or BDD change.
- **Response:** `a`
- **Resulting authorization or action:** Authorized adding only `@Disabled("Pending approved damage behavior")` and its import to the isolated `PlayerCharacterTest`. The protected approval output remains unchanged; no production code, BDD behavior, commit, or push is authorized.
- **Automation evidence:** Bootstrap assessment should identify unstable or unapproved discovered tests before build-adapter implementation and present one baseline-quarantine decision alongside the adapter proposal.

### IP-034 — Maven plugin dependency required a second cache escalation

- **Type:** Automated permission interaction
- **Stage:** Isolated migration verification
- **Trigger:** After the approved damage-test quarantine, canonical verification reached the Starter self-test execution but could not cache `commons-exec` and ASM dependencies under the home Maven repository. Policy-required escalation was requested for the unchanged verification command.
- **Request or event:** Allow canonical verification to finish downloading the approved plugin dependencies and run both suites.
- **Response:** Automatically reviewed and permitted by the sandbox approval policy.
- **Resulting authorization or action:** Canonical verification completed successfully: one unapproved damage test was explicitly skipped and all 53 Starter clean-room tests passed through Maven.
- **Automation evidence:** Resolve and declare the complete plugin dependency graph before the first gate, or use a repository-local cache so one plugin does not produce multiple permission interruptions.

### IP-035 — Final 0.4.1 doctor inherited behavior protection

- **Type:** Human checkpoint caused by protection machinery
- **Stage:** Isolated migration verification
- **Trigger:** After the repaired 0.4.1 distribution and canonical Maven verification became green, the evolution guide requires a final installed doctor. The session hook again imported the main worktree's protected behavior registry and blocked this read-only command. Its exact digest is now prepared.
- **Request or event:** Confirm running the prepared read-only final doctor in the isolated worktree.
- **Response:** `a`
- **Resulting authorization or action:** The prepared final doctor ran successfully and reported `CodeCraft Starter 0.4.1: healthy`. The candidate remains isolated and uncommitted; no push is authorized.
- **Automation evidence:** Read-only health checks should be reusable throughout one verification session without repeated behavior confirmations, especially when the checked worktree has no protected assets.

### IP-036 — Failed baseline test generated protected-pattern debris

- **Type:** Human protected-file checkpoint
- **Stage:** Candidate construction
- **Trigger:** The failed pre-quarantine ApprovalTests run generated two untracked files in the isolated worktree: an empty `PlayerCharacterTest.dealDamage.approved.txt` and a `.received.txt` containing nondeterministic object identity strings. Neither path exists in the base commit, and neither belongs in the workflow-foundation candidate. The `.approved.txt` name matches protected behavior patterns.
- **Request or event:** Confirm deleting exactly those two untracked generated files from the isolated worktree.
- **Response:** `a`
- **Resulting authorization or action:** Deleted exactly the two untracked generated files from the isolated worktree. No tracked file, commit, or push was changed.
- **Automation evidence:** Verification should write ApprovalTests received/empty-approved artifacts under ignored derived-output storage or clean operation-owned debris transactionally after a failed isolated run.

### IP-037 — Automation verifier required shared-Git-directory escalation

- **Type:** Automated permission interaction
- **Stage:** Automation completion lane
- **Trigger:** The exact candidate manifest matched every isolated Git status path, but the verifier could not create its temporary worktree under the shared main Git directory inside the sandbox. Policy-required escalation was requested for the unchanged verifier command.
- **Request or event:** Allow the automation verifier to create its isolated worktree and signed receipt for the exact candidate.
- **Response:** Automatically reviewed and permitted by the sandbox approval policy.
- **Resulting authorization or action:** The verifier emitted a signed receipt, but review of its output showed the Java command invoked the host's Java guidance shim and exited successfully without Maven. The receipt is rejected as false-green and must be replaced after correction.
- **Automation evidence:** The verifier should detect commands that return success without producing an expected build marker, and worktree receipt storage should declare its shared-Git permission requirement before execution.

### IP-038 — Bare Maven wrapper can false-green through host Java shim

- **Type:** Human design and scope checkpoint
- **Stage:** Automation completion lane
- **Trigger:** Direct verification is green when JDK 21 is pinned, but the mandatory bare completion lane inherits no `JAVA_HOME`; on this host, `java` resolves to a guidance shim that prints a message and exits zero. The verifier therefore signed a receipt without running Maven.
- **Request or event:** Confirm a project-local `mvnw` fallback: only when `JAVA_HOME` is unset on macOS, select Homebrew OpenJDK 21 from `/opt/homebrew/opt/openjdk@21` or `/usr/local/opt/openjdk@21`; preserve ordinary wrapper behavior everywhere else.
- **Response:** `a`
- **Resulting authorization or action:** Authorized the project-local macOS fallback to Homebrew OpenJDK 21 only when `JAVA_HOME` is unset. The false-green receipt remains invalid until replaced; no commit or push is authorized.
- **Automation evidence:** Bootstrap should verify the final bare configured command in the same environment used by completion lanes, persist a portable project toolchain selection, and refuse success when the expected build process never starts.

### IP-039 — Post-wrapper doctor inherited behavior protection

- **Type:** Human checkpoint caused by protection machinery
- **Stage:** Automation completion lane
- **Trigger:** After the approved wrapper fix, bare Maven verification ran genuinely and the isolated automation lane completed with Java compilation, one explicitly skipped unapproved damage test, 53 passing Starter tests, two valid skills, and a replacement signed receipt. The evolution guide still requires a post-change doctor, but the session hook again imported unrelated main-worktree behavior protection and blocked the read-only command. Its exact digest is now prepared.
- **Request or event:** Confirm running the prepared read-only final doctor after the wrapper correction.
- **Response:** `a`
- **Resulting authorization or action:** The prepared post-wrapper doctor ran successfully and reported `CodeCraft Starter 0.4.1: healthy`. The verified candidate remains isolated and uncommitted; no push is authorized.
- **Automation evidence:** Doctor authorization should be session-scoped and reusable for unchanged read-only health checks, and isolated worktrees must not inherit another worktree's protected registry.

### IP-040 — Exact-manifest staging encountered Git and sandbox constraints

- **Type:** Automated tooling interaction
- **Stage:** Commit review
- **Trigger:** Path-limited staging first failed because the isolated worktree index lives under the shared Git directory outside the sandbox. The escalated retry then failed because already-staged deletions no longer matched literal pathspecs. Immediately beforehand, the complete isolated status was mechanically proven identical to the verified manifest.
- **Request or event:** Allow staging the entire isolated status, whose path set exactly equaled the candidate manifest.
- **Response:** Automatically reviewed and permitted by the sandbox approval policy.
- **Resulting authorization or action:** `git add --all` staged exactly the verified 94-path manifest; a subsequent staged-name comparison reported no omissions or extras.
- **Automation evidence:** The committer should stage manifests through a helper that handles absent already-staged deletions and shared-worktree Git permissions without falling back to a broader-looking command.

### IP-041 — Commit review rejected generated Windows wrapper whitespace

- **Type:** Committer refusal and implementation-loop interaction
- **Stage:** Commit review
- **Trigger:** `git diff --cached --check` reported carriage returns as trailing whitespace on all 189 lines of bootstrap-generated `mvnw.cmd`. The committer workflow prohibits repairing code during commit review.
- **Request or event:** Leave commit review, normalize only `mvnw.cmd` line endings from CRLF to LF, invalidate the current receipt, and rerun the automation completion lane before restaging.
- **Response:** No human response required; this is an enforced mechanical formatting correction within the approved workflow-foundation slice.
- **Resulting authorization or action:** Commit review stopped without committing. The formatting correction and new verification are pending; no push is authorized.
- **Automation evidence:** Bootstrap should normalize generated wrapper line endings or install an accompanying `.gitattributes` rule, and should run staged-equivalent whitespace validation before declaring success.

### IP-042 — Wrapper line-ending formatter inherited behavior protection

- **Type:** Human checkpoint caused by protection machinery
- **Stage:** Formatting correction
- **Trigger:** The exact command to remove only carriage returns at line ends in isolated `mvnw.cmd` was blocked because the session hook imported the main worktree's unrelated protected behavior registry. Its exact digest is now prepared.
- **Request or event:** Confirm the prepared one-file CRLF-to-LF normalization command.
- **Response:** `a`
- **Resulting authorization or action:** Converted only isolated `mvnw.cmd` from CRLF to LF. Commit review remains stopped until fresh verification; no commit or push is authorized.
- **Automation evidence:** Protection should classify path-specific formatters against their actual targets and avoid requiring behavior approval when no protected path can be reached.

### IP-043 — Workflow foundation committed in isolation

- **Type:** Commit outcome
- **Stage:** Commit
- **Trigger:** After newline normalization, the corrected candidate/evidence split passed the full automation lane, staged-path equality, staged whitespace validation, the signed staged-receipt check, and the post-commit receipt check.
- **Request or event:** Create the previously authorized coherent prerequisite commit without pushing.
- **Response:** Authorization carried from IP-020 and all narrower implementation checkpoints.
- **Resulting authorization or action:** Created detached commit `571602f` with Arlo message `e establish repository-local CodeCraft workflow`; 94 paths changed. The isolated worktree is clean, `main` still points to `d899824`, and nothing was pushed.
- **Automation evidence:** The committer should understand candidate/evidence splitting before the first receipt and perform staged-equivalent CRLF checks before full verification to avoid repeated complete lanes.

### IP-044 — Integrate isolated prerequisite while preserving dirty main worktree

- **Type:** Human state-transition checkpoint
- **Stage:** Prerequisite integration
- **Trigger:** The verified commit exists on detached HEAD, while `main` remains at its parent and contains the preserved Element 1 worktree plus the superseded pre-foundation staged index. A normal fast-forward cannot safely reconcile that dirty index implicitly.
- **Request or event:** Confirm a reversible index-only integration: save the current main index under a repository-local backup ref, fast-forward `main` from `d899824` to `571602f`, reset only the main index to the new commit, and leave every working-tree and untracked byte untouched. Inspect the resulting diff before reconciling any foundation files.
- **Response:** `a`
- **Resulting authorization or action:** Saved the original index at `refs/codecraft/backups/pre-foundation-index-ip044` (`eb3ce6f`), fast-forwarded `main` to `571602f` with an expected-old-value guard, and reset only the index to the new commit. The index is clean and every working-tree/untracked byte was left untouched. No push was performed or authorized.
- **Automation evidence:** The workflow needs a first-class isolated-prerequisite integration command that snapshots index state, advances the branch, rebases the index without touching the worktree, and emits a reconciliation manifest.

### IP-045 — Reconcile superseded foundation bytes in main worktree

- **Type:** Human state-reconciliation checkpoint
- **Stage:** Prerequisite integration
- **Trigger:** After the index-only integration, exact diff review separates stale pre-foundation bytes from preserved user/Element 1 work. Eleven files revert verified foundation behavior or version state; `.codecraft/completion-lanes.json` correctly adds `interations.md` evidence but accidentally drops the verified `codecraft-starter/**/*` fingerprint.
- **Request or event:** Confirm restoring these eleven paths exactly from verified `HEAD`: `.agents/skills/codecraft/SKILL.md`, `.codecraft/installation.json`, `.github/workflows/codecraft.yml`, `AGENTS.md`, `codecraft-starter/README.md`, `codecraft-starter/VERSION`, `codecraft-starter/payload/agents/codecraft-skill.md`, `codecraft-starter/tests/test_starter.py`, `java/pom.xml`, `mvnw`, and `mvnw.cmd`; also restore only the missing Starter fingerprint in `.codecraft/completion-lanes.json` while retaining `interations.md` evidence.
- **Response:** `a`
- **Resulting authorization or action:** Authorized the exact eleven-path restore and one-field completion-lane merge, but the first restore invocation was blocked before execution because protection imported unrelated behavior paths. No reconciliation has occurred; preserved files remain untouched and no push is authorized.
- **Automation evidence:** Integration should classify project-owned merges separately from distribution-managed restores and produce a human-readable keep/restore manifest before changing the worktree.

### IP-046 — Exact foundation restore inherited behavior protection

- **Type:** Human checkpoint caused by protection machinery
- **Stage:** Prerequisite integration
- **Trigger:** IP-045 approved an exact `git restore --worktree` command containing only eleven non-behavior foundation paths. The session hook nevertheless imported the main protected registry and blocked it before execution. The command digest is now prepared.
- **Request or event:** Confirm retrying the now-prepared exact eleven-path foundation restore.
- **Response:** `a`
- **Resulting authorization or action:** The prepared command passed protection, then Git failed because sandboxing denied `.git/index.lock`. The policy-required escalated retry changed the protection digest and was blocked before execution. No file changed; the separate completion-lane merge has not begun and no push is authorized.
- **Automation evidence:** Protection should authorize commands from their resolved target paths rather than every registry entry, and a prepared human-approved restore should not require a second interaction solely to bind a digest.

### IP-047 — Foundation restore escalation changed protection digest

- **Type:** Human checkpoint caused by interacting sandbox and protection guardrails
- **Stage:** Prerequisite integration
- **Trigger:** The exact approved worktree-only restore still asks Git to create `index.lock`, which the sandbox denied. Retrying the unchanged semantic command with required escalation changed the tool-call digest, so protection blocked it before execution. That escalated digest is now prepared.
- **Request or event:** Confirm the now-prepared escalated retry of the exact eleven-path foundation restore.
- **Response:** `a`
- **Resulting authorization or action:** The escalated exact restore completed for the eleven approved foundation paths. Behavior/user work remained untouched and no push was performed or authorized.
- **Automation evidence:** Protection reservations should bind to semantic commands independently of sandbox metadata, or filesystem escalation should preserve authorization for an unchanged path set.

### IP-048 — Reconcile the active behavior run with the committed foundation

- **Type:** Human workflow checkpoint
- **Stage:** Behavior commit preparation
- **Trigger:** The separately verified workflow foundation was integrated into `main` as commit `571602f`, so the resumable behavior run correctly reported that its original base commit had changed and retained a pending `workflow-foundation` attention item.
- **Request or event:** Confirm treating `571602f` as the approved prerequisite, resolving the foundation attention, and rebuilding and re-verifying the behavior-only candidate against the new `HEAD` before any behavior commit.
- **Response:** `a`
- **Resulting authorization or action:** Resolved the active run's `workflow-foundation` attention with the prerequisite commit recorded. The behavior run remains at commit review; its old receipt and manifest will not be reused, and no behavior commit or push is authorized by this checkpoint.
- **Automation evidence:** Resumable runs need a first-class rebase/update-base operation that invalidates stale receipts, preserves completed development checkpoints, and emits the exact candidate-diff review required after an approved prerequisite lands.

### IP-049 — Read-only candidate inspection inherited write protection

- **Type:** Tooling interaction avoided without human interruption
- **Stage:** Behavior candidate reconstruction
- **Trigger:** A combined read-only inspection command named the protected BDD source and approved-output file. The protection hook classified the command as a protected change and blocked the entire parallel inspection before any subcommand ran.
- **Request or event:** Inspect current behavior artifacts before reconstructing the post-foundation candidate manifest.
- **Response:** No human response requested; the optional protected-file reread was abandoned because those artifacts were already reviewed in the approved implementation loop.
- **Resulting authorization or action:** No file changed. Candidate reconstruction continues from Git status, existing run evidence, and non-protected diffs; the mandatory verifier will provide the next exact protected checkpoint if one is required.
- **Automation evidence:** Protection should distinguish read-only file inspection from mutation and should not cancel unrelated parallel read operations when one target is protected.

### IP-050 — Behavior verifier required shared-Git-directory escalation

- **Type:** Automated permission interaction
- **Stage:** Behavior completion lane
- **Trigger:** The rebuilt behavior-only manifest was complete and excluded unrelated `README.md` and `.idea` work, but the first verifier attempt could not create its isolated worktree under the shared Git directory inside the sandbox.
- **Request or event:** Allow the unchanged behavior verifier to create its isolated worktree and signed receipt for the exact candidate and evidence manifests.
- **Response:** Automatically reviewed and permitted by the sandbox approval policy.
- **Resulting authorization or action:** The isolated behavior lane passed against foundation commit `571602f`: 2 tests passed, the explicitly deferred damage seed was skipped, all 53 Starter self-tests passed, and receipt `sha256:2108892a4139ccf2d4ead58a3de36ca8924bae44b90b21e4975c2b99b58581b9` was issued. No commit or push occurred.
- **Automation evidence:** Completion-lane tools that necessarily create Git worktrees should declare or acquire their narrow shared-Git permission without a guaranteed failed first attempt.

### IP-051 — Commit the verified Element 1 behavior slice

- **Type:** Human protected-file and commit checkpoint
- **Stage:** Commit review
- **Trigger:** The post-foundation behavior-only candidate passed its completion lane with receipt `sha256:2108892a4139ccf2d4ead58a3de36ca8924bae44b90b21e4975c2b99b58581b9`. Preparing exact path-limited staging was blocked, as designed, because the manifest includes the protected BDD source and approved output.
- **Request or event:** Confirm staging exactly the 12 candidate/evidence paths listed in the behavior manifests, validating staged-path equality, whitespace, and the signed staged receipt, then creating one Arlo `F` commit for “a newly created character starts with 1000 health and is alive.” Keep unrelated `README.md` and `.idea` work unstaged; do not push.
- **Response:** `a`
- **Resulting authorization or action:** Authorized exact path-limited staging, staged validation, and one Arlo `F` commit for the verified Element 1 behavior. Unrelated `README.md` and `.idea` work remains excluded; no push is authorized.
- **Automation evidence:** A verified run should be able to bind its human commit approval directly to the receipt and exact manifest, avoiding a separate guard interaction solely for staging already-approved protected behavior artifacts.

### IP-052 — Approved behavior staging requires sandbox escalation

- **Type:** Human checkpoint caused by interacting sandbox and protection guardrails
- **Stage:** Commit review
- **Trigger:** The exact staging command approved in IP-051 passed protection but Git could not create `.git/index.lock` inside the sandbox. The policy-required escalated retry has the identical path list and semantics, but escalation changed the tool-call digest, so the protection hook blocked it before execution.
- **Request or event:** Confirm the now-prepared escalated retry of the exact 12-path staging command already approved in IP-051. Continue with staged validation and the authorized Arlo `F` commit only if those checks pass; do not push.
- **Response:** `a`
- **Resulting authorization or action:** Authorized the escalated retry of the identical 12-path staging command, followed by staged validation and the already-authorized Arlo `F` commit if all checks pass. No push is authorized.
- **Automation evidence:** Protected-action approval should survive a required sandbox escalation when the executable, arguments, and resolved path set are unchanged.

### IP-053 — Staged receipt check required shared-Git-directory escalation

- **Type:** Automated permission interaction
- **Stage:** Commit review
- **Trigger:** Exact staged-path equality and whitespace validation passed, but the staged-receipt checker could not create its temporary fingerprint worktree under the shared Git directory inside the sandbox.
- **Request or event:** Allow the unchanged staged-receipt check to create its isolated worktree.
- **Response:** Automatically reviewed and permitted by the sandbox approval policy.
- **Resulting authorization or action:** The staged receipt check reported `verification receipt is current`. This interaction record remains within the already-approved evidence path and will be restaged and rechecked before commit; no push is authorized.
- **Automation evidence:** Receipt validation should declare its isolated-worktree permission need up front, just like full completion-lane verification.

### IP-054 — Authorized commit required shared-Git-directory escalation

- **Type:** Automated permission interaction
- **Stage:** Commit
- **Trigger:** All commit-review checks passed, but the first authorized `git commit` attempt could not create `.git/index.lock` inside the sandbox.
- **Request or event:** Allow Git to create the already-authorized Element 1 commit from the exact verified staged manifest.
- **Response:** Automatically reviewed and permitted by the sandbox approval policy.
- **Resulting authorization or action:** Git created the single Arlo `F` commit. This interaction entry is being folded into that same authorized evidence path before the final post-commit receipt check; unrelated files remain outside the commit and nothing is pushed.
- **Automation evidence:** The committer lane should declare its narrow Git-metadata write permission before the first commit attempt instead of relying on a predictable sandbox failure and retry.

### IP-055 — Post-commit evidence logging changed receipt-check mode

- **Type:** Automated workflow interaction
- **Stage:** Post-commit verification
- **Trigger:** After the authorized commit existed, recording IP-054 changed only the approved interaction evidence. Reusing pre-commit `--staged` receipt mode then correctly rejected the now-committed candidate because `HEAD` had advanced.
- **Request or event:** Fold the interaction evidence into the same authorized commit and use the verifier's dedicated `--check-commit` mode against the amended commit.
- **Response:** No additional human response required; IP-051 and IP-052 already authorized the exact evidence path and single commit, while automated sandbox policy permitted the narrow Git metadata operations.
- **Resulting authorization or action:** The evidence-only amendment retained the Arlo message and exact 12-path scope, and the dedicated post-commit receipt check reported `verification receipt is current`. This final interaction entry will be folded into the same commit and the post-commit check repeated before the run is finished; no push is authorized.
- **Automation evidence:** Interaction logging that is itself commit evidence needs a transaction boundary or post-run sidecar so recording commit-time tool interactions does not force iterative amend-and-reverify cycles.

### IP-056 — Next-behavior assessment kickoff

- **Type:** Human instruction
- **Stage:** Before run creation
- **Trigger:** The human requested that the project-local CodeCraft workflow assess the next planned behavior without implementing until the required checkpoint.
- **Request or event:** Read repository instructions, resume durable run state, inspect the plan, responsibility map, current implementation, and tests, and prepare the next BDD design checkpoint.
- **Response:** The assistant loaded the required CodeCraft sources. `codecraft_run.py resume --json` returned `{"active": false}`; `main` is synchronized with `origin/main`. Unrelated local `README.md` and `.idea` work remains untouched.
- **Resulting authorization or action:** Assessment only. No run, test, protected asset, or production behavior has been created or changed.
- **Automation evidence:** A behavior preflight should summarize active-run, branch, baseline, and unrelated-work state in one command before design begins.

### IP-057 — Damage-reduces-target-health design checkpoint

- **Type:** Human BDD design checkpoint
- **Stage:** Design
- **Trigger:** The next provisional plan item is damage behavior. The current `PlayerCharacter` owns health and life state and already receives `receiveDamage(attacker, damagePoints)`, but the method is a no-op.
- **Request or event:** Approve Element 2: an Orc dealing 100 damage to a newly created Hero changes the Hero from 1000 health/alive to 900 health/alive. Use a new `CharacterDamage_bdd` approval test and leave death, overkill clamping, self-damage, healing, and levels outside this slice.
- **Response:** `a`
- **Resulting authorization or action:** Approved Element 2 exactly as proposed: create the new public BDD source and expected output, run to the predicted no-op outside red, and pause for confirmation before any focused test or production implementation.
- **Automation evidence:** A future design-checkpoint command could render the approval grid, persist its stable element number, and initialize run state only after a configured alias approves it.

### IP-058 — Confirm the Element 2 outside red

- **Type:** Human outside-red and protected-metadata checkpoint
- **Stage:** Outside red
- **Trigger:** The approved `CharacterDamage_bdd` was created and run without changing production code. It failed exactly as predicted: expected Hero at 900 health after 100 damage, but received Hero at 1000 health because `receiveDamage` remains a no-op. The run checkpoint was recorded, but advancing run metadata while naming the protected BDD paths was blocked by the protection hook and prepared an exact digest.
- **Request or event:** Confirm that this is the expected outside red and authorize the prepared run-state transition. After confirmation, proceed to the smallest focused test and production implementation for Element 2 only.
- **Response:** `a`
- **Resulting authorization or action:** Confirmed the exact expected outside red and authorized the prepared run-state transition plus focused implementation of Element 2 only.
- **Automation evidence:** Run-state commands that only reference protected paths as context should be classified as metadata operations, not protected-file mutations; the required outside-red confirmation can otherwise be needlessly duplicated.

### IP-059 — Completion-lane permission review timed out once

- **Type:** Automated permission interaction
- **Stage:** Verification
- **Trigger:** The exact Element 2 verifier requested its known narrow permission to create an isolated Git worktree, but the automatic approval review did not finish before its deadline. The command did not run during the timed-out attempt.
- **Request or event:** Retry the unchanged verifier once, as permitted by the tool response.
- **Response:** The automatic sandbox reviewer permitted the retry; no human response was required.
- **Resulting authorization or action:** The isolated lane passed with four active Java tests, one explicitly deferred legacy seed skipped, and all 53 Starter tests passing. Initial receipt: `sha256:39b7a471b3364b937498797166fa4259b2bf740caad647288c9f3df1733e7e48`.
- **Automation evidence:** Permission-review timeouts should return a resumable request identifier or automatically retry idempotent, exact worktree verification once.

### IP-060 — Commit the verified Element 2 behavior slice

- **Type:** Human protected-file and commit checkpoint
- **Stage:** Commit review
- **Trigger:** The exact six-path behavior candidate plus three allowed evidence paths passed the isolated behavior lane with receipt `sha256:da7a712ed851eb2ebbdd884267d9f0e7ee48cacbf723327ba4d3a2801a128c03`. The complete status contains only those nine relevant paths plus unrelated `README.md` and `.idea` work. The exact staging command was prepared with required Git-metadata escalation up front and blocked, as designed, on the new protected BDD source and approved output.
- **Request or event:** Confirm staging exactly the nine manifest paths, validating path equality, whitespace, and the signed staged receipt, then creating one Arlo `F` commit for damage reducing the target's health. Keep `README.md` and `.idea` unstaged; do not push.
- **Response:** `a`
- **Resulting authorization or action:** Authorized exact nine-path staging, staged validation, and one Arlo `F` commit for verified Element 2. Unrelated `README.md` and `.idea` work remains excluded; no push is authorized.
- **Automation evidence:** Preparing the escalated semantic staging transaction before the human checkpoint avoids the prior duplicate approval caused solely by `.git/index.lock` sandbox escalation.

### IP-061 — Path-limited commit consumed a second protected operation

- **Type:** Human checkpoint caused by protection machinery
- **Stage:** Commit
- **Trigger:** IP-060 authorized both staging and committing the exact verified manifest. Exact staging and the staged-receipt check succeeded, but the committer contract requires `git commit --only -- <exact paths>`. Because that separate Git operation names the protected BDD source and approved output, the single-use staging authorization cannot cover it and the protection hook blocked the prepared commit command.
- **Request or event:** Confirm the now-prepared escalated `git commit --only` command for exactly the same nine verified paths with Arlo message `F reduce target health when damaged`. Refresh the already-approved interaction evidence and staged receipt first; do not push.
- **Response:** `a`
- **Resulting authorization or action:** Authorized the prepared exact nine-path `git commit --only` command with Arlo message `F reduce target health when damaged`, after refreshing interaction evidence and the staged receipt. No push is authorized.
- **Automation evidence:** One human commit checkpoint should mint a transaction capability covering both exact staging and exact path-limited commit, rather than requiring one single-use protected approval per internal Git operation.

### IP-062 — Continue to the next planned behavior

- **Type:** Human instruction
- **Stage:** Before run creation
- **Trigger:** After Element 2 was committed and its run completed, the human requested `continue`.
- **Request or event:** Resume CodeCraft state and assess the next provisional plan item without creating tests or production behavior before its design checkpoint.
- **Response:** `codecraft_run.py resume --json` returned `{"active": false}`. The plan names lethal damage and death next; `main` is one committed Element 2 change ahead of `origin/main`, while unrelated `README.md` and `.idea` work remains untouched.
- **Resulting authorization or action:** Assessment only. No new run, test, protected asset, or production code has been created or changed.
- **Automation evidence:** A completed-run continuation command could select the next provisional plan row and generate its design assessment while preserving the human approval boundary.

### IP-063 — Overkill damage clamps health and kills the target

- **Type:** Human BDD design checkpoint
- **Stage:** Design
- **Trigger:** The next provisional behavior is lethal damage and death. `PlayerCharacter` already owns health and life state, but subtracting 1500 damage from a new character currently produces -500 health while leaving it alive.
- **Request or event:** Approve Element 3: an Orc dealing 1500 damage to a newly created Hero clamps Hero's health to 0 and marks Hero dead. Use a new `LethalDamage_bdd` approval test; leave exact-health depletion, self-damage, already-dead targets, and invalid damage amounts outside this slice.
- **Response:** `a`
- **Resulting authorization or action:** Approved Element 3 exactly as proposed: create the new public BDD source and expected output, run to the predicted `-500` health/alive outside red, and pause before focused testing or production implementation.
- **Automation evidence:** Stable element numbering and explicit excluded cases keep a broad requirement such as “death” decomposed into reviewable, independently verified behavior slices.

### IP-064 — Confirm the Element 3 outside red

- **Type:** Human outside-red checkpoint
- **Stage:** Outside red
- **Trigger:** The approved `LethalDamage_bdd` was created and run without changing production code. It failed exactly as predicted: expected Hero at 0 health/dead after 1500 damage, but received Hero at -500 health/alive.
- **Request or event:** Confirm that this is the expected outside red. After confirmation, proceed to the smallest focused test and production implementation for Element 3 only.
- **Response:** `a`
- **Resulting authorization or action:** Confirmed the exact expected `-500` health/alive outside red and authorized focused implementation of Element 3 only.
- **Automation evidence:** Using the plan rather than protected file paths as run context avoided the redundant protected-metadata checkpoint observed in Element 2 while preserving complete operational routing.

### IP-065 — Commit the verified Element 3 behavior slice

- **Type:** Human protected-file and commit checkpoint
- **Stage:** Commit review
- **Trigger:** The exact six-path behavior candidate plus three allowed evidence paths passed the isolated behavior lane with receipt `sha256:747c918c194687b7fc448fb2fef8e2b29057212363bc2f4bd148a684199f2302`. Complete status contains only those nine relevant paths plus unrelated `README.md` and `.idea` work. The exact staging command was prepared with required Git-metadata escalation and blocked, as designed, on the new protected BDD source and approved output.
- **Request or event:** Confirm staging exactly the nine manifest paths, validating path equality, whitespace, and the signed staged receipt, then creating one Arlo `F` commit for overkill damage clamping health and killing the target. Keep `README.md` and `.idea` unstaged; do not push.
- **Response:** `a`
- **Resulting authorization or action:** Authorized exact nine-path staging, staged validation, and one Arlo `F` commit for verified Element 3. Unrelated `README.md` and `.idea` work remains excluded; no push is authorized.
- **Automation evidence:** Element 3 reused the improved pre-escalated staging checkpoint, avoiding the earlier separate sandbox retry approval.

### IP-066 — Element 3 commit requires its separate protected operation

- **Type:** Human checkpoint caused by protection machinery
- **Stage:** Commit
- **Trigger:** IP-065 authorized staging and committing the exact verified manifest. Exact staging and the staged-receipt check succeeded, but the committer contract's separate `git commit --only -- <exact paths>` operation names the protected BDD source and approved output, so the single-use staging authorization cannot cover it.
- **Request or event:** Confirm the prepared escalated `git commit --only` command for exactly the same nine paths with Arlo message `F kill targets on overkill damage`. Refresh interaction evidence and the staged receipt first; do not push.
- **Response:** `a`
- **Resulting authorization or action:** Authorized the prepared exact nine-path `git commit --only` command with Arlo message `F kill targets on overkill damage`, after refreshing interaction evidence and the staged receipt. No push is authorized.
- **Automation evidence:** This is the second consecutive behavior increment proving the need for one transaction-scoped capability covering verified staging plus exact commit.

### IP-067 — Continue to exact-health depletion

- **Type:** Human instruction
- **Stage:** Before run creation
- **Trigger:** After Element 3 was committed and its run completed, the human requested `continue`.
- **Request or event:** Resume CodeCraft state and assess the next provisional plan item without creating tests or production behavior before its design checkpoint.
- **Response:** `codecraft_run.py resume --json` returned `{"active": false}`. The plan names exact-health depletion next; `main` is two committed behavior changes ahead of `origin/main`, while unrelated `README.md` and `.idea` work remains untouched.
- **Resulting authorization or action:** Assessment only. No new run, test, protected asset, or production code has been created or changed.
- **Automation evidence:** Successive completed behaviors can reuse the same narrow continuation preflight without rediscovering unrelated repository state.

### IP-068 — Exact-health damage kills the target

- **Type:** Human BDD design checkpoint
- **Stage:** Design
- **Trigger:** The next provisional behavior is exact-health depletion. `PlayerCharacter` currently treats only damage greater than current health as lethal, so 1000 damage leaves a newly created Hero at 0 health but still alive.
- **Request or event:** Approve Element 4: an Orc dealing exactly 1000 damage to a newly created Hero leaves Hero at 0 health and dead. Use a new `DepletingDamage_bdd` approval test; leave self-damage, already-dead targets, and invalid damage amounts outside this slice.
- **Response:** `a`
- **Resulting authorization or action:** Approved Element 4 exactly as proposed: create the new public BDD source and expected output, run to the predicted 0 health/alive outside red, and pause before focused testing or production implementation.
- **Automation evidence:** Boundary-value behavior deserves its own public example even when the eventual production change is a one-character comparison adjustment.

### IP-069 — Confirm the Element 4 outside red

- **Type:** Human outside-red checkpoint
- **Stage:** Outside red
- **Trigger:** The approved `DepletingDamage_bdd` was created and run without changing production code. It failed exactly as predicted: expected Hero at 0 health/dead after exactly 1000 damage, but received Hero at 0 health/alive.
- **Request or event:** Confirm that this is the expected outside red. After confirmation, proceed to the smallest focused boundary test and production implementation for Element 4 only.
- **Response:** `a`
- **Resulting authorization or action:** Confirmed the exact expected 0 health/alive outside red and authorized focused implementation of Element 4 only.
- **Automation evidence:** Non-protected plan context again preserved run routing without triggering a redundant protected-metadata approval.

### IP-070 — Commit the verified Element 4 behavior slice

- **Type:** Human protected-file and commit checkpoint
- **Stage:** Commit review
- **Trigger:** The exact six-path behavior candidate plus three allowed evidence paths passed the isolated behavior lane with receipt `sha256:bad988e1104b831cc42ad871ceb2d62500290adb2cd2470341546690159a3a03`. Complete status contains only those nine relevant paths plus unrelated `README.md` and `.idea` work. The pre-escalated exact staging command was blocked, as designed, on the protected BDD source and approved output.
- **Request or event:** Confirm staging exactly the nine manifest paths, validating path equality, whitespace, and the signed staged receipt, then creating one Arlo `F` commit for exact-health damage killing the target. Keep `README.md` and `.idea` unstaged; do not push.
- **Response:** `a`
- **Resulting authorization or action:** Authorized exact nine-path staging, staged validation, and one Arlo `F` commit for verified Element 4. Unrelated `README.md` and `.idea` work remains excluded; no push is authorized.
- **Automation evidence:** The repeatable pre-escalated checkpoint continues to eliminate sandbox-only approval retries, leaving the known stage-versus-commit capability split as the remaining friction.

### IP-071 — Element 4 commit requires its separate protected operation

- **Type:** Human checkpoint caused by protection machinery
- **Stage:** Commit
- **Trigger:** IP-070 authorized staging and committing the exact verified manifest. Exact staging and the staged-receipt check succeeded, but the committer contract's separate `git commit --only -- <exact paths>` operation names the protected BDD source and approved output, so the single-use staging authorization cannot cover it.
- **Request or event:** Confirm the prepared escalated `git commit --only` command for exactly the same nine paths with Arlo message `F kill targets when health is depleted`. Refresh interaction evidence and the staged receipt first; do not push.
- **Response:** `a`
- **Resulting authorization or action:** Authorized the prepared exact nine-path `git commit --only` command with Arlo message `F kill targets when health is depleted`, after refreshing interaction evidence and the staged receipt. No push is authorized.
- **Automation evidence:** This third consecutive identical stage-versus-commit checkpoint satisfies the working agreement's threshold for proposing versioned automation of a transaction-scoped commit capability.

### IP-072 — Third occurrence triggers workflow-learning assessment

- **Type:** Human continuation and workflow-learning trigger
- **Stage:** Assessment
- **Trigger:** After Element 4 was committed, the human requested `continue`. IP-061, IP-066, and IP-071 record three consecutive cases where one approved commit checkpoint was split into two human interactions because protected staging consumed the single-use authorization before `git commit --only`.
- **Request or event:** Compare the three occurrences, inspect the protection and committer contracts, and assess versioned automation before beginning the next planned behavior.
- **Response:** `continue`
- **Resulting authorization or action:** Assessment only. `codecraft_run.py resume --json` returned `{"active": false}`; no feature run, self-damage behavior, workflow machinery, or protected asset was changed.
- **Automation evidence:** The duplicated checkpoint is deterministic: the guard binds approval to one tool-input digest, while the committer skill requires separate protected staging and path-limited commit operations over the same verified manifest.

### IP-073 — Approve a verified commit transaction capability

- **Type:** Human workflow-design checkpoint
- **Stage:** Design
- **Trigger:** The third repeated stage-versus-commit interaction meets the working agreement's automation threshold. Review found that merely hiding internal Git operations in a wrapper would weaken protection; the safe boundary is one guard-visible, receipt-bound transaction that fails closed if its approved identity changes.
- **Request or event:** Approve CodeCraft Starter 0.5.0's proposed verified commit transaction: one single-use human approval covers exact manifest staging, staged receipt validation, one exact Arlo commit, and committed receipt validation. Bind the transaction identity to lane, base commit, current receipt, candidate and evidence paths and contents, and commit message; reject changes, extra paths, stale receipts, reuse, or push. Keep feature behavior outside this automation slice.
- **Response:** `a`
- **Resulting authorization or action:** Authorized implementation and verification of the CodeCraft Starter 0.5.0 verified commit transaction as an automation-only slice. Self-damage behavior and pushing remain unauthorized.
- **Automation evidence:** The proposal removes one interaction per verified increment while retaining exact-path protection, single use, signed-receipt enforcement, unrelated-work exclusion, and the separate explicit authorization required for pushing.

### IP-074 — Install the approved 0.5.0 machinery through its distribution

- **Type:** Human protected-workflow checkpoint
- **Stage:** Implementation
- **Trigger:** The approved CodeCraft Starter 0.5.0 package and its 55 clean-room tests are green. The required distribution upgrade command, `codecraft-starter/bin/codecraft_starter.py upgrade --target .`, was blocked by the installed 0.4.1 guard because the repository-root target conservatively resolves to all registered protected assets.
- **Request or event:** Confirm rerunning that exact versioned upgrade command. It will update distribution-managed CodeCraft files and the installation record from 0.4.1 to 0.5.0; it will not modify feature behavior, stage or commit files, or push.
- **Response:** `a`
- **Resulting authorization or action:** Authorized the exact distribution upgrade. Its first execution reached the host sandbox and failed before changing installed files because `.agents` requires escalated filesystem access.
- **Automation evidence:** This is a one-time bootstrap checkpoint imposed by the pre-transaction guard. Avoiding it by changing the target spelling would bypass the prepared protected-operation identity rather than improve the workflow.

### IP-075 — Retry the approved upgrade with host filesystem permission

- **Type:** Human checkpoint caused by sandbox metadata
- **Stage:** Implementation
- **Trigger:** IP-074 approved the exact upgrade, but its non-escalated execution failed on `.agents/skills/codecraft/.SKILL.md.*`. The retry requires `sandbox_permissions=require_escalated`; because the 0.4.1 guard hashes the entire tool input, that host-only metadata changed the protected-operation identity and the guard blocked the retry. Status confirms no installed `.agents` or `.codecraft` file was changed.
- **Request or event:** Confirm the prepared escalated retry of the same command, `codecraft-starter/bin/codecraft_starter.py upgrade --target .`. The semantic target and authorized upgrade are unchanged.
- **Response:** `a`
- **Resulting authorization or action:** Authorized and completed the identical escalated upgrade. The installed workflow now reports CodeCraft Starter 0.5.0 healthy; no feature behavior, commit, or push was changed.
- **Automation evidence:** This interaction was avoidable: the upgrade should have been prepared with known `.agents` filesystem escalation before IP-074. Future protected operations should bind semantic command identity independently of host sandbox metadata.

### IP-076 — Install the reviewed 0.5.1 guard hardening

- **Type:** Human protected-workflow checkpoint
- **Stage:** Review
- **Trigger:** Review of the installed 0.5.0 helper found that a compound shell command beginning with the read-only `prepare` action could bypass manifest inspection. CodeCraft Starter 0.5.1 fails closed for compound and environment-wrapped helper commands. The package is healthy and all 55 clean-room tests pass. The exact escalated upgrade was prepared before this checkpoint and blocked by the installed guard as designed.
- **Request or event:** Confirm `codecraft-starter/bin/codecraft_starter.py upgrade --target .` with the already-prepared filesystem escalation. This installs only the reviewed 0.5.1 guard hardening and corresponding signed installation record; it does not change feature behavior, commit, or push.
- **Response:** `a`
- **Resulting authorization or action:** Authorized and completed the prepared upgrade. The installed workflow is now CodeCraft Starter 0.5.1; feature behavior remains unchanged and no commit or push occurred.
- **Automation evidence:** The review caught and pinned a real executable-boundary bypass before completion. Preparing the escalation before the checkpoint avoids repeating IP-075.

### IP-077 — Commit the verified transaction automation

- **Type:** Human protected-file and commit checkpoint
- **Stage:** Commit preparation
- **Trigger:** CodeCraft Starter 0.5.1, its installed machinery, package integrity, post-upgrade doctor, and 55 clean-room tests are green. The exact automation candidate excludes the user's unrelated `README.md` and `.idea` work. The isolated automation completion lane and read-only transaction preparation are the remaining prerequisites.
- **Request or event:** If those prerequisites pass, confirm one receipt-bound transaction that stages and commits only the exact automation candidate and allowed evidence with Arlo message `e add verified commit transaction`. The transaction will validate before and after the path-limited commit; it will not push. The exact receipt and transaction identities will be presented in the human prompt.
- **Response:** `a`
- **Resulting authorization or action:** Authorized and completed transaction `sha256:550fae65d4d1501ad449109e0f3002b00215e96834bfef1b10fc10d257d518d5`. Commit `70cba642f0a726cd68ae3e99ae3bc4aad0e46d8c` contains exactly the 11 automation candidate paths and two evidence paths with Arlo message `e add verified commit transaction`. Both staged and committed receipt checks passed; no push occurred.
- **Automation evidence:** The first live use completed staging, staged verification, path-limited commit, and committed verification in one 14.7-second protected operation after one human approval. This response was recorded after execution so it could not invalidate the approved evidence-content identity; the updated interaction record remains for the next increment.

### IP-078 — Continue to the next planned behavior

- **Type:** Human continuation
- **Stage:** Assessment
- **Trigger:** The verified commit transaction automation was completed and its run closed. The human requested `continue`.
- **Request or event:** Resume CodeCraft state and assess the next provisional plan item without creating a public test or production behavior before its design checkpoint.
- **Response:** `continue`
- **Resulting authorization or action:** Assessment only. `codecraft_run.py resume --json` returned `{"active": false}`. The next plan item is collaborative self-damage prevention; no new run, test, protected asset, or production code was created or changed.
- **Automation evidence:** A read-only assessment search using regex alternation was falsely blocked because the guard treated the pattern's `|` characters as shell pipes. Reissuing the same search with separate `-e` patterns avoided a human checkpoint and produced the needed evidence.

### IP-079 — Define self-damage prevention

- **Type:** Human BDD design checkpoint
- **Stage:** Design
- **Trigger:** `PlayerCharacter` owns its health, life state, and incoming-damage mutation. Its `receiveDamage(attacker, amount)` message currently applies damage even when `attacker` is the same object as the receiver. The provisional plan leaves the desired self-damage rule undecided.
- **Request or event:** Approve Element 5: a newly created Hero attempting to deal 100 damage to itself remains at 1000 health and alive. Add one new `SelfDamage_bdd` approval test whose story says `Hero attempts to deal 100 damage to itself.` and whose before and after observations are both `Hero has 1000 health and is alive.` The predicted outside red is 900 health/alive. Use object identity for “itself”; leave same-named distinct characters, already-dead targets, and invalid amounts outside this slice.
- **Response:** `a`
- **Resulting authorization or action:** Approved Element 5 exactly as proposed: add the new `SelfDamage_bdd` public approval test, run it against unchanged production code to the predicted 900 health/alive outside red, and pause before focused testing or production implementation.
- **Automation evidence:** The state owner can enforce this invariant with no new collaborator or dependency direction: the receiver compares the attacker reference with itself before applying incoming damage.

### IP-080 — Confirm the Element 5 outside red

- **Type:** Human outside-red checkpoint
- **Stage:** Outside red
- **Trigger:** The approved `SelfDamage_bdd` and expected output were created without changing production code. Its focused Maven run failed exactly as predicted: expected Hero at 1000 health/alive after attempting self-damage, but received Hero at 900 health/alive.
- **Request or event:** Confirm that this is the expected outside red. After confirmation, remove the generated received output, add the smallest focused self-damage test, and implement Element 5 only.
- **Response:** `a`
- **Resulting authorization or action:** Confirmed the exact expected 900 health/alive outside red and authorized the smallest focused identity test plus production implementation of Element 5 only.
- **Automation evidence:** The BDD failure isolates the missing identity guard. A run-state update that named the newly enrolled protected BDD paths was falsely blocked, so routing was recorded with `interations.md` as its unprotected context instead of adding a redundant human checkpoint.

### IP-081 — Commit the verified Element 5 behavior slice

- **Type:** Human protected-file and commit checkpoint
- **Stage:** Commit preparation
- **Trigger:** The exact seven-path behavior candidate plus two allowed evidence paths passed the isolated behavior lane with receipt `sha256:880b13cc62f84293f1ae11f8f41ce0962668b26c980a420182cc5197c830b282`. Ten active Java tests and all 55 Starter tests pass; one deferred legacy seed is skipped. Complete status contains only those nine relevant paths plus the user's unrelated `README.md` and `.idea` work.
- **Request or event:** Confirm one receipt-bound transaction that stages and commits only the exact candidate and evidence paths with Arlo message `F prevent self-damage`. Validate before and after the path-limited commit; keep `README.md` and `.idea` unstaged and do not push. The exact transaction identity will be presented in the human prompt.
- **Response:** `a`
- **Resulting authorization or action:** Authorized and completed transaction `sha256:72b220b1ddf4313de1864045365be2b0155956a87ca5ca2d1150906efe91311f`. Commit `422a302357859f9b57b1c904b9b72719735e4b24` contains exactly the seven behavior candidate paths and two evidence paths with Arlo message `F prevent self-damage`. Both staged and committed receipt checks passed; no push occurred.
- **Automation evidence:** The behavior commit completed staging, staged verification, path-limited commit, and committed verification in one 12.1-second protected operation after one human approval. The response was recorded after execution so it could not invalidate the approved evidence-content identity; this updated interaction record remains for the next increment.

### IP-082 — Review the completeness of the development plan

- **Type:** Human roadmap question
- **Stage:** Planning assessment
- **Trigger:** After all five listed plan items were completed, the human observed that `emergent/design/development-plan.md` is very short and asked for the complete plan.
- **Request or event:** Compare the development plan with the repository's full RPG Combat requirements and identify the missing roadmap without changing behavior or documentation yet.
- **Response:** `What's the complete plan? The Development plan is really short and does`
- **Resulting authorization or action:** Assessment only. The current plan covers creation and core damage through self-damage prevention, but omits healing, levels, factions, magical objects, and progression. No plan or code change is authorized by the question alone.
- **Automation evidence:** `README.md` contains an original ruleset followed by a revised ruleset. The revised sections change maximum-health growth, level-based damage scaling, and maximum/temporary level rules, so a complete executable roadmap needs a human decision about whether the later block supersedes the earlier one.

### IP-083 — Expand the complete provisional roadmap

- **Type:** Human documentation authorization
- **Stage:** Planning
- **Trigger:** The roadmap review showed that the five-item development plan covered only completed core damage behavior. The assistant recommended treating the later README rules as authoritative where they modify the original and outlined the missing healing, levels, factions, magical objects, and progression phases.
- **Request or event:** Authorize expanding the project-owned development plan into that complete provisional roadmap without implementing any new behavior.
- **Response:** `sounds good, make it so`
- **Resulting authorization or action:** Authorized a documentation-only plan expansion. The later rules govern revised Levels and Changing level behavior; unchanged sections retain their original requirements. Every unchecked item remains provisional and still requires its own BDD design checkpoint.
- **Automation evidence:** Ambiguous requirements are represented as explicit collaborative decision items rather than silently resolved: integer damage rounding, healing-object resource consumption, and whether one attack can cross multiple survival thresholds.

### IP-084 — Continue the roadmap documentation slice

- **Type:** Human continuation
- **Stage:** Documentation review
- **Trigger:** The complete provisional roadmap had been written and was awaiting consistency review and documentation-lane verification when the human requested `continue`.
- **Request or event:** Continue the authorized documentation-only slice without beginning any unchecked behavior.
- **Response:** `continue`
- **Resulting authorization or action:** Continue roadmap review, verification, and commit preparation only. No Java behavior or workflow machinery is authorized.
- **Automation evidence:** Mid-slice continuation preserved the existing narrow scope and active CodeCraft run instead of restarting discovery.

### IP-085 — Commit the complete provisional roadmap

- **Type:** Human commit checkpoint
- **Stage:** Commit preparation
- **Trigger:** The documentation-only roadmap candidate passed the isolated documentation lane with receipt `sha256:67174e63a00dce2a40ffa2b53affbf9ef1398f5b3136440ba7c8a0f2fa569a7c`. The exact candidate is `emergent/design/development-plan.md`; `interations.md` is allowed evidence. The user's unrelated `README.md` and `.idea` work remains excluded.
- **Request or event:** Confirm one receipt-bound transaction for those two exact paths with Arlo message `d expand development roadmap`. Validate before and after the path-limited commit; do not push. The exact transaction identity will be presented in the human prompt.
- **Response:** `a`
- **Resulting authorization or action:** Authorized transaction `sha256:396827ab1ebba3102204cbfd5a2957ef9b62440eb7334b2001b81141861741cc`. It created exact two-path commit `3e5619b`, and the staged receipt check passed. The helper then stopped because the post-commit material-input fingerprint unexpectedly included the Markdown evidence path. No push occurred; the commit was not reset, amended, or otherwise rewritten.
- **Automation evidence:** The documentation lane exposed an inconsistency in the new transaction boundary: staged fingerprinting checks the base plus candidate, while committed fingerprinting checks the full commit and therefore treats Markdown evidence as material only after commit.

### IP-086 — Repair documentation evidence fingerprinting

- **Type:** Human workflow-design checkpoint
- **Stage:** Recovery
- **Trigger:** Commit `3e5619b` contains exactly the approved roadmap and interaction paths, but its required post-commit receipt check failed after the commit because `isolated_fingerprint` checks out the whole committed reference instead of the receipt base before overlaying candidate content. This makes documentation evidence affect only the committed fingerprint.
- **Request or event:** Approve CodeCraft Starter 0.5.2 as a patch release: add a clean-room regression test for Markdown evidence, make committed fingerprinting use the receipt base plus committed candidate content just like staged fingerprinting, upgrade installed machinery through the distribution, and rerun the original receipt check against existing commit `3e5619b`. Do not reset, amend, recommit, implement behavior, or push.
- **Response:** `a`
- **Resulting authorization or action:** Authorized the CodeCraft Starter 0.5.2 regression test, verifier patch, distribution upgrade, and recheck of existing commit `3e5619b`. Resetting, amending, recommitting the roadmap, behavior changes, and pushing remain unauthorized.
- **Automation evidence:** A successful patch will make staged and committed fingerprint semantics identical while preserving exact commit-path checks and evidence allowlisting.

### IP-087 — Install CodeCraft Starter 0.5.2 into this repository

- **Type:** Human protected-workflow checkpoint
- **Stage:** Distribution upgrade
- **Trigger:** The 0.5.2 distribution package is healthy. Its clean-room regression reproduces the post-commit Markdown-evidence failure and passes with the approved base-plus-candidate fingerprint repair; the full lane passes 11 Java tests with one intentional skip and all 55 Starter tests.
- **Request or event:** Confirm the exact project-local upgrade command `codecraft-starter/bin/codecraft_starter.py upgrade --target .`. The distribution may update only signed, unchanged managed files and the installation record; it must preserve project-owned files, behavior, history, and unrelated `README.md` and `.idea` work. Afterward, rerun the original receipt check against existing commit `3e5619b`; do not push.
- **Response:** `a`
- **Resulting authorization or action:** Completed the exact project-local 0.5.2 distribution upgrade. It updated the managed verifier and installation record without changing roadmap history, RPG behavior, or unrelated work. The existing commit `3e5619b` was rechecked in place; no amend, recommit, reset, or push occurred.
- **Automation evidence:** Package check and the complete Maven verification lane pass for distribution version 0.5.2. The installed doctor reports `CodeCraft Starter 0.5.2: healthy`, and the original signed roadmap receipt reports `verification receipt is current` against exact two-path commit `3e5619b`.

### IP-088 — Commit the CodeCraft Starter 0.5.2 repair

- **Type:** Human commit checkpoint
- **Stage:** Commit preparation
- **Trigger:** The isolated automation lane passed for the exact six-file workflow candidate with receipt candidate digest `sha256:d8634b5c5146fbb0cd6b1671d8813a89f8a21fd6b1c026e86b103c25054eb741`. Eleven Java tests pass with one intentional skip, all 55 Starter tests pass, both packaged skills validate, and the installed verifier matches the distribution payload. The two evidence paths document the failure and interactions; unrelated `README.md` and `.idea` work remains excluded.
- **Request or event:** Confirm one receipt-bound transaction that stages and commits only the six candidate paths and two evidence paths with Arlo message `B fix documentation evidence fingerprints`. Validate before and after the path-limited commit; do not push. The exact transaction identity will be presented in the human prompt.
- **Response:** `a`
- **Resulting authorization or action:** Authorized transaction `sha256:10623c6e69ba55292ac45565fa70a3788495f996e538343639bde7f61c8b49bc`. The exact execute command was then blocked before staging because the protection hook independently requires a standalone checkpoint for `.codecraft/installation.json`. No commit or push occurred.
- **Automation evidence:** The 0.5.2 package and installed workflow are healthy, and the unchanged roadmap commit now passes its original post-commit receipt check.

### IP-089 — Confirm the protected installation-record commit

- **Type:** Human redundant protected-command checkpoint
- **Stage:** Commit execution
- **Trigger:** The human approved the exact eight-path receipt-bound workflow transaction, but its first execute attempt was blocked before staging because `.codecraft/installation.json` is protected. The transaction helper already binds that path, its content, the signed receipt, the other seven paths, and the commit message.
- **Request or event:** Reconfirm the recalculated exact transaction after this interaction evidence is included. Execute the same path-limited `B fix documentation evidence fingerprints` commit; leave unrelated work unstaged and do not push.
- **Response:** `a`
- **Resulting authorization or action:** Authorized recalculated transaction `sha256:de4bc79082448a369df19534aa2eb5eb5e4fba6c5d7bf718d3b5e5ee6c9b2b27`, but the hook applied the response to the prior pending command identity. The first attempt of the recalculated transaction therefore created a new pending authorization and was blocked before staging. No commit or push occurred at this interaction.
- **Automation evidence:** This checkpoint is caused by overlapping transaction approval and protected-path approval mechanisms; it is a concrete candidate for reducing duplicate interactions while preserving an exact single-use boundary.

### IP-090 — Align approval with the unchanged pending transaction

- **Type:** Human protected-command retry
- **Stage:** Commit execution
- **Trigger:** Interaction evidence changed the receipt-bound transaction after the first protected-command attempt. The subsequent approval was consumed by that earlier pending digest, so the first exact attempt of transaction `sha256:de4bc79082448a369df19534aa2eb5eb5e4fba6c5d7bf718d3b5e5ee6c9b2b27` created a new pending hook record instead of executing. The assistant diagnosed the two-step hook protocol and promised not to change evidence again before retrying.
- **Request or event:** Approve the already-attempted, unchanged transaction once more so the hook's pending command digest and the human response align.
- **Response:** `a`
- **Resulting authorization or action:** The identical command consumed the pending approval and created commit `867813911afa13cd194be06255a2ac087c6b38d9` with exactly the six candidate paths and two evidence paths. Both staged and committed receipt checks passed. Unrelated `README.md` and `.idea` work remained outside the commit; no push occurred.
- **Automation evidence:** The successful retry confirms that the hook requires this order: first attempt creates a pending digest, the next affirmative prompt authorizes that digest, and then an identical tool input executes. Logging a checkpoint between those steps changes evidence and therefore the transaction identity, producing an avoidable approval loop.

### IP-091 — Continue to the next roadmap behavior

- **Type:** Human continuation
- **Stage:** Planning assessment
- **Trigger:** CodeCraft Starter 0.5.2 was installed and committed, both prior runs were complete, and the human requested continuation.
- **Request or event:** Assess the first unchecked roadmap behavior under the project-local CodeCraft workflow without implementing before its required human checkpoint.
- **Response:** `continue`
- **Resulting authorization or action:** Opened behavior run `heal-damaged-character` and assessed Element 6 only. No Java, BDD, expected-output, roadmap, or responsibility-map change is authorized by this continuation alone.
- **Automation evidence:** The development plan identifies self-healing for a living damaged character as the first unchecked item. `PlayerCharacter` already owns health and life state, so the slice introduces no collaborator or dependency direction.

### IP-092 — Define self-healing for a damaged living character

- **Type:** Human BDD design checkpoint
- **Stage:** Design
- **Trigger:** A new Hero starts at 1000 health. Existing damage behavior can arrange Hero at 900 health while alive, and `PlayerCharacter` owns the state that healing changes. The requirements say a character can heal itself but do not prescribe a sample amount or method name.
- **Request or event:** Approve Element 6: Orc deals 100 damage to Hero during Arrange; Hero then heals itself for 50 health as the single Act; Hero changes from 900 health/alive to 950 health/alive. Add `CharacterHealing_bdd.damagedLivingCharacterHealsItself` and its approved output, call a minimal `hero.heal(50)` protocol, and run the BDD against unchanged production code. The predicted outside red is test-compilation failure because `PlayerCharacter.heal(int)` does not exist. Stop for confirmation before adding a focused test or production implementation. Maximum-health capping, healing while dead, healing others, magical objects, and zero or negative amounts remain outside this slice.
- **Response:** `a`
- **Resulting authorization or action:** Approved the exact Element 6 BDD scenario, expected output, minimal `heal(int)` protocol used by the test, and focused outside-red run against unchanged production code. Focused tests and production implementation remain unauthorized until the expected outside red is confirmed.
- **Automation evidence:** The smallest responsibility-aligned design places self-healing on the health-owning `PlayerCharacter`; later ally and magical-object rules can introduce their own sender-aware protocols only when those behaviors create design pressure.

### IP-093 — Confirm the Element 6 outside red

- **Type:** Human outside-red checkpoint
- **Stage:** Outside red
- **Trigger:** The approved `CharacterHealing_bdd` and expected output were created without changing production code. Its focused Maven run failed at test compilation exactly as predicted: `PlayerCharacter` has no `heal(int)` method.
- **Request or event:** Confirm that the missing `heal(int)` compilation failure is the expected outside red. After confirmation, add the smallest focused self-healing test, implement Element 6 only, and leave maximum-health capping, dead-character healing, allies, magical objects, and invalid amounts for later slices.
- **Response:** `a`
- **Resulting authorization or action:** Confirmed the exact missing `heal(int)` outside red and authorized the smallest focused self-healing test plus production implementation of Element 6 only. Maximum-health capping, dead-character healing, allies, magical objects, and invalid amounts remain unauthorized.
- **Automation evidence:** The failure isolates the missing self-healing protocol before implementation. A compound run-state update that named the newly enrolled protected BDD path was falsely blocked, so the outside-red checkpoint and attention were recorded separately with `interations.md` as the unprotected routing context.

### IP-094 — Commit the verified Element 6 behavior slice

- **Type:** Human protected-file and commit checkpoint
- **Stage:** Commit preparation
- **Trigger:** The exact seven-path behavior candidate plus two allowed evidence paths passed the isolated behavior lane with receipt candidate digest `sha256:bfc57486ba72de43b5ab3bdc128050d9cb088c33fef0967b2a535991e3f29b50`. Twelve active Java tests and all 55 Starter tests pass; one deferred legacy seed is skipped. Complete status contains only those nine relevant paths plus the human's unrelated `README.md` and `.idea` work.
- **Request or event:** Confirm one receipt-bound transaction that stages and commits only the exact candidate and evidence paths with Arlo message `F allow damaged characters to heal`. Validate before and after the path-limited commit; keep `README.md` and `.idea` unstaged and do not push. The exact transaction identity will be presented in the human prompt.
- **Response:** `a`
- **Resulting authorization or action:** Authorized and completed transaction `sha256:450d10e5a416605d0c4da47656bc67b14fd526c282b831de3594dcf02d648484`. Commit `7c7b450894b996939958a2451947746e42142703` contains exactly the seven behavior candidate paths and two evidence paths with Arlo message `F allow damaged characters to heal`. Both staged and committed receipt checks passed; no push occurred.
- **Automation evidence:** The behavior lane proves the final source, protected BDD assets, focused test, protected registry, plan, and responsibility-map candidate together. Performing the exact non-mutating protected-command preflight after logging the pending checkpoint and before asking for approval allowed the one human response to authorize both the transaction and guard digest without an approval loop.

### IP-095 — Continue to the maximum-health healing rule

- **Type:** Human continuation
- **Stage:** Planning assessment
- **Trigger:** Element 6 self-healing was committed and its CodeCraft run completed. The human requested continuation to the next provisional roadmap item.
- **Request or event:** Assess the maximum-health healing rule under the project-local CodeCraft workflow without implementing before its required human checkpoint.
- **Response:** `continue`
- **Resulting authorization or action:** Opened behavior run `cap-healing-at-maximum` and assessed Element 7 only. No Java, BDD, expected-output, roadmap, or responsibility-map change is authorized by this continuation alone.
- **Automation evidence:** Current `heal(int)` adds the requested amount without a boundary, while `PlayerCharacter` already owns health. A living Hero at 900 health healing 200 therefore exposes the missing maximum-health rule as 1100 instead of 1000.

### IP-096 — Define healing capped at current maximum health

- **Type:** Human BDD design checkpoint
- **Stage:** Design
- **Trigger:** Element 6 established self-healing for a living damaged character. The next roadmap rule requires healing to stop at current maximum health; before levels exist, a new Hero's current maximum is 1000.
- **Request or event:** Approve Element 7: Orc deals 100 damage to Hero during Arrange; Hero then attempts to heal itself for 200 health as the single Act; Hero changes from 900 health/alive to exactly 1000 health/alive. Add `MaximumHealing_bdd.healingStopsAtMaximumHealth` and its approved output, reuse `hero.heal(200)`, and run the BDD against unchanged production code. The predicted outside red is an approval mismatch whose received result reports Hero at 1100 health/alive. Stop for confirmation before adding a focused test or production implementation. Dead-character healing, levels and level-based maximum growth, allies, magical objects, and zero or negative amounts remain outside this slice.
- **Response:** `a` after the rejected `1a` response recorded in IP-097.
- **Resulting authorization or action:** Approved the exact Element 7 BDD scenario, expected output, reuse of `heal(int)`, and focused outside-red run against unchanged production code. Focused tests and production implementation remain unauthorized until the expected 1100-health outside red is confirmed.
- **Automation evidence:** The health-owning `PlayerCharacter` remains the receiver, decision owner, and state owner. The observable rule requires a current maximum-health boundary but does not yet require a public level protocol or a separate policy object.

### IP-097 — Reject an unrecognized approval response

- **Type:** Human checkpoint response validation
- **Stage:** Design
- **Trigger:** Element 7 was awaiting one of the configured approval aliases: `approve`, `a`, `yes`, or `y`.
- **Request or event:** Interpret the human response to the pending Element 7 BDD design checkpoint.
- **Response:** `1a`
- **Resulting authorization or action:** No authorization was granted because `1a` is not an accepted exact alias. The Element 7 checkpoint remains pending; no protected BDD asset or Java source changed.
- **Automation evidence:** Exact alias validation prevents accidental implementation from a malformed or ambiguous response while allowing an immediate corrected reply.

### IP-098 — Confirm the Element 7 outside red

- **Type:** Human outside-red checkpoint
- **Stage:** Outside red
- **Trigger:** The approved `MaximumHealing_bdd` and expected output were created without changing production code. Its focused Maven run failed exactly as predicted: expected Hero at 1000 health/alive after healing, but received Hero at 1100 health/alive.
- **Request or event:** Confirm that the 1100-health approval mismatch is the expected outside red. After confirmation, remove the generated received output, add the smallest focused maximum-health test, and implement Element 7 only. Dead-character healing, levels and level-based maximum growth, allies, magical objects, and invalid amounts remain later slices.
- **Response:** `a`
- **Resulting authorization or action:** Confirmed the exact 1100-health outside red and authorized removal of its generated received output, the smallest focused maximum-health test, and production implementation of Element 7 only. Dead-character healing, levels, allies, magical objects, and invalid amounts remain unauthorized.
- **Automation evidence:** The public behavior failure isolates the missing maximum-health boundary while preserving the existing successful self-healing behavior below that boundary.

### IP-099 — Commit the verified Element 7 behavior slice

- **Type:** Human protected-file and commit checkpoint
- **Stage:** Commit preparation
- **Trigger:** The exact seven-path behavior candidate plus two allowed evidence paths passed the isolated behavior lane with receipt candidate digest `sha256:1bf937c3e85d3a6a79754c8e9ce8610a69489607eb5da7a5fb4bd94a26b2963d`. Fourteen active Java tests and all 55 Starter tests pass; one deferred legacy seed is skipped. No generated received output remains. Complete status contains only those nine relevant paths plus the human's unrelated `README.md` and `.idea` work.
- **Request or event:** Confirm one receipt-bound transaction that stages and commits only the exact candidate and evidence paths with Arlo message `F cap healing at maximum health`. Validate before and after the path-limited commit; keep `README.md` and `.idea` unstaged and do not push. The exact transaction identity will be presented after the non-mutating protected-command preflight has registered its digest.
- **Response:** `a`
- **Resulting authorization or action:** Authorized and completed transaction `sha256:d5581fd48a5e92ace5e040d0d983e872a596e77c0b82c482492b94a0d4db5840`. Commit `04a33a67224b2b36b70080142321166783c267cc` contains exactly the seven behavior candidate paths and two evidence paths with Arlo message `F cap healing at maximum health`. Both staged and committed receipt checks passed; no push occurred.
- **Automation evidence:** The final candidate includes source, protected BDD assets, focused test, registry, plan, and responsibility-map changes. Feature evidence and `interations.md` are evidence-only paths. As intended, the exact preflight-before-prompt ordering let one human response authorize both the receipt-bound transaction and the pending protected-command digest.

### IP-100 — Continue to dead-character healing prevention

- **Type:** Human continuation
- **Stage:** Planning assessment
- **Trigger:** Element 7 maximum-health capping was committed and its CodeCraft run completed. The human requested continuation to the next provisional roadmap item.
- **Request or event:** Assess the dead-character healing rule under the project-local CodeCraft workflow without implementing before its required human checkpoint.
- **Response:** `continue`
- **Resulting authorization or action:** Opened behavior run `prevent-dead-character-healing` and assessed Element 8 only. No Java, BDD, expected-output, roadmap, or responsibility-map change is authorized by this continuation alone.
- **Automation evidence:** Current `heal(int)` clamps to maximum health but does not inspect life state. A dead Hero at 0 health attempting to heal 100 would therefore become 100 health while remaining dead.

### IP-101 — Define dead-character healing prevention

- **Type:** Human BDD design checkpoint
- **Stage:** Design
- **Trigger:** The final Healing roadmap rule says dead characters cannot heal. Existing lethal behavior can arrange Hero at 0 health and dead, and `PlayerCharacter` owns both health and life state.
- **Request or event:** Approve Element 8: Orc deals 1000 damage to Hero during Arrange; Hero then attempts to heal itself for 100 health as the single Act; Hero remains at 0 health and dead. Add `DeadCharacterHealing_bdd.deadCharacterCannotHealItself` and its approved output, reuse `hero.heal(100)`, and run the BDD against unchanged production code. The predicted outside red is an approval mismatch whose received result reports Hero at 100 health and dead. Stop for confirmation before adding a focused test or production implementation. Resurrection, healing others, damage after death, levels, magical objects, and zero or negative amounts remain outside this slice.
- **Response:** `a`
- **Resulting authorization or action:** Approved the exact Element 8 BDD scenario, expected output, reuse of `heal(int)`, and focused outside-red run against unchanged production code. Focused tests and production implementation remain unauthorized until the expected 100-health-while-dead outside red is confirmed.
- **Automation evidence:** The state-owning `PlayerCharacter` remains receiver, decision owner, and state owner; the missing rule is a life-state guard on the existing self-healing protocol, with no new collaborator or abstraction pressure.

### IP-102 — Confirm the Element 8 outside red

- **Type:** Human outside-red checkpoint
- **Stage:** Outside red
- **Trigger:** The approved `DeadCharacterHealing_bdd` and expected output were created without changing production code. Its focused Maven run failed exactly as predicted: expected Hero at 0 health/dead after attempting to heal, but received Hero at 100 health/dead.
- **Request or event:** Confirm that the 100-health-while-dead approval mismatch is the expected outside red. After confirmation, remove the generated received output, add the smallest focused dead-character healing test, and implement Element 8 only. Resurrection, healing others, damage after death, levels, magical objects, and invalid amounts remain later slices.
- **Response:** `a`
- **Resulting authorization or action:** Confirmed the exact 100-health-while-dead outside red and authorized removal of its generated received output, the smallest focused dead-character healing test, and production implementation of Element 8 only. Resurrection, healing others, damage after death, levels, magical objects, and invalid amounts remain unauthorized.
- **Automation evidence:** The public behavior failure isolates the missing life-state guard on healing while preserving living-character healing and maximum-health capping.

### IP-103 — Commit the verified Element 8 behavior slice

- **Type:** Human protected-file and commit checkpoint
- **Stage:** Commit preparation
- **Trigger:** The exact seven-path behavior candidate plus two allowed evidence paths passed the isolated behavior lane with receipt candidate digest `sha256:1eafd15afed1cab2eb52832ee6d2509df6d8ca2e65260fdf02cc2a1322cc7037`. Sixteen active Java tests and all 55 Starter tests pass; one deferred legacy seed is skipped. No generated received output remains. Complete status contains only those nine relevant paths plus the human's unrelated `README.md` and `.idea` work.
- **Request or event:** Confirm one receipt-bound transaction that stages and commits only the exact candidate and evidence paths with Arlo message `F prevent dead characters from healing`. Validate before and after the path-limited commit; keep `README.md` and `.idea` unstaged and do not push. The exact transaction identity will be presented after the non-mutating protected-command preflight has registered its digest.
- **Response:** `a`
- **Resulting authorization or action:** Authorized and completed transaction `sha256:6ba026f69de706027c8d9086621cd65a5b3a04b2c4e8764ccbadce98f4477c2f`. Commit `5090dc4f7cd8512a510022d2649e0a2c9208e64e` contains exactly the seven behavior candidate paths and two evidence paths with Arlo message `F prevent dead characters from healing`. Both staged and committed receipt checks passed; no push occurred.
- **Automation evidence:** The final candidate includes source, protected BDD assets, focused test, registry, plan, and responsibility-map changes. Feature evidence and `interations.md` are evidence-only paths. The exact preflight-before-prompt ordering again let one human response authorize both transaction and protected-command digest.

### IP-104 — Continue to starting level and maximum health

- **Type:** Human continuation
- **Stage:** Planning assessment
- **Trigger:** The complete Healing phase was committed and its CodeCraft run completed. The human requested continuation to the first Levels roadmap item.
- **Request or event:** Assess starting level and maximum health under the project-local CodeCraft workflow without implementing before its required human checkpoint.
- **Response:** `continue`
- **Resulting authorization or action:** Opened behavior run `initialize-character-level` and assessed Element 9 only. No Java, BDD, expected-output, roadmap, or responsibility-map change is authorized by this continuation alone.
- **Automation evidence:** `PlayerCharacter` already owns a 1000 maximum-health value but owns no level, and the existing printer output is shared by protected approval tests. A separate progression rendering method can expose the new behavior without rewriting earlier approved stories.

### IP-105 — Define a new character's starting progression state

- **Type:** Human BDD design checkpoint
- **Stage:** Design
- **Trigger:** The revised requirements say a new character starts at level 1 with maximum health 1000. Existing health/life approval output must remain stable, while `PlayerCharacter.Status` is the established immutable observation boundary consumed by `PlayerCharacterPrinter`.
- **Request or event:** Approve Element 9: create Hero during Arrange; render Hero's progression state as the single Act using `printer.printProgression(hero)`; assert `Hero is level 1 with maximum health 1000.` Add `CharacterLevel_bdd.newCharacterStartsAtLevelOneWithMaximumHealth` and its approved output, then run the BDD against unchanged production code. The predicted outside red is test-compilation failure because `PlayerCharacterPrinter.printProgression(PlayerCharacter)` does not exist. Stop for confirmation before adding focused tests or production implementation. Level gain, maximum-health growth, damage scaling, progression counters, and temporary level loss remain outside this slice.
- **Response:** `a`
- **Resulting authorization or action:** Approved the exact Element 9 BDD scenario, expected output, separate `printProgression` observation protocol, and focused outside-red run against unchanged production code. Focused tests and production implementation remain unauthorized until the expected missing-method outside red is confirmed.
- **Automation evidence:** A separate rendering method preserves all prior protected approval output. The later focused design can add level and maximum health to the existing immutable status snapshot without exposing mutable domain state or introducing a new policy abstraction.

### IP-106 — Confirm the Element 9 outside red

- **Type:** Human outside-red checkpoint
- **Stage:** Outside red
- **Trigger:** The approved `CharacterLevel_bdd` and expected output were created without changing production code. Its focused Maven run failed at test compilation exactly as predicted: `PlayerCharacterPrinter` has no `printProgression(PlayerCharacter)` method.
- **Request or event:** Confirm that the missing progression-rendering method is the expected outside red. After confirmation, add the smallest focused starting-level test and implement Element 9 only while preserving all existing health/life approval output. Level gain, maximum-health growth, damage scaling, progression counters, and temporary level loss remain later slices.
- **Response:** `a`
- **Resulting authorization or action:** Confirmed the exact missing `printProgression` outside red and authorized the smallest focused starting-level test plus production implementation of Element 9 only: level 1, maximum health 1000 in the immutable status snapshot, and separate progression rendering. Later level behavior remains unauthorized.
- **Automation evidence:** The failure isolates the missing public observation protocol without requiring changes to any earlier protected approval asset.

### IP-107 — Commit the verified Element 9 behavior slice

- **Type:** Human protected-file and commit checkpoint
- **Stage:** Commit preparation
- **Trigger:** The exact nine-path behavior candidate plus two allowed evidence paths passed the isolated behavior lane with receipt candidate digest `sha256:0021e80f385b0b145c720d15e34ad2d83fae55aa0c2a8de4fc396a6e7f49700a`. Eighteen active Java tests and all 55 Starter tests pass; one deferred legacy seed is skipped. Existing protected health/life approval output remains unchanged. Complete status contains only those eleven relevant paths plus the human's unrelated `README.md` and `.idea` work.
- **Request or event:** Confirm one receipt-bound transaction that stages and commits only the exact candidate and evidence paths with Arlo message `F initialize character progression`. Validate before and after the path-limited commit; keep `README.md` and `.idea` unstaged and do not push. The exact transaction identity will be presented after the non-mutating protected-command preflight has registered its digest.
- **Response:** `a`
- **Resulting authorization or action:** Authorized and completed transaction `sha256:452bc3a664c00ab331ea39fb8d0c08fcef9e0be3739902b32b765187ba326b56`. Commit `2f2e5b8ce6ece8f8e0fe6231f94ed14465682655` contains exactly the nine behavior candidate paths and two evidence paths with Arlo message `F initialize character progression`. Both staged and committed receipt checks passed; no push occurred.
- **Automation evidence:** The candidate includes progression source and rendering, the expanded focused state test, new protected BDD assets, registry, plan, and responsibility-map changes. Feature evidence and `interations.md` are evidence-only paths. The exact preflight-before-prompt ordering again completed with one human approval.

### IP-108 — Continue to maximum-health growth by level

- **Type:** Human continuation
- **Stage:** Planning assessment
- **Trigger:** Element 9 starting progression was committed and its CodeCraft run completed. The human requested continuation to the next Levels roadmap item.
- **Request or event:** Assess level-driven maximum-health growth without prematurely implementing the later damage- or faction-based level-gain rules.
- **Response:** `continue`
- **Resulting authorization or action:** Opened behavior run `grow-maximum-health-with-level` and assessed Element 10 only. No Java, BDD, expected-output, roadmap, or responsibility-map change is authorized by this continuation alone.
- **Automation evidence:** The rule requires observing a higher-level character, but all eligibility mechanisms are later roadmap items. A narrow package-private `gainLevel()` domain transition can model the event without allowing arbitrary public leveling or choosing an eligibility policy early.

### IP-109 — Define maximum-health growth when a level is gained

- **Type:** Human BDD design checkpoint
- **Stage:** Design
- **Trigger:** A new Hero now exposes level 1 and maximum health 1000. The next rule says each additional level increases maximum health by 100, while the reasons a character earns a level are deliberately deferred.
- **Request or event:** Approve Element 10: create Hero and capture its progression state during Arrange; invoke package-private `hero.gainLevel()` as the single Act representing an already-decided level-gain event; assert Hero changes from level 1/maximum health 1000 to level 2/maximum health 1100. Add `MaximumHealthGrowth_bdd.gainingALevelIncreasesMaximumHealth` and its approved output, then run the BDD against unchanged production code. The predicted outside red is test-compilation failure because `PlayerCharacter.gainLevel()` does not exist. Stop for confirmation before focused tests or implementation. Level eligibility, damage/faction progression, current-health refill on level gain, damage scaling, and temporary level loss remain outside this slice.
- **Response:** `a`
- **Resulting authorization or action:** Approved the exact Element 10 BDD scenario, expected output, package-private `gainLevel()` protocol used by the test, and focused outside-red run against unchanged production code. Focused tests and production implementation remain unauthorized until the expected missing-method outside red is confirmed.
- **Automation evidence:** `PlayerCharacter` already owns level and maximum health, so it owns their synchronized transition. Package-private visibility supports later internal progression rules without publishing a client-controlled leveling command.

### IP-110 — Confirm the Element 10 outside red

- **Type:** Human outside-red checkpoint
- **Stage:** Outside red
- **Trigger:** The approved `MaximumHealthGrowth_bdd` and expected output were created without changing production code. Its focused Maven run failed at test compilation exactly as predicted: `PlayerCharacter` has no `gainLevel()` method.
- **Request or event:** Confirm that the missing `gainLevel()` method is the expected outside red. After confirmation, add the smallest focused level-growth test and implement Element 10 only: one gained level changes level 1/maximum health 1000 to level 2/maximum health 1100. Level eligibility, damage/faction progression, current-health refill, damage scaling, and temporary level loss remain later slices.
- **Response:** `a`
- **Resulting authorization or action:** Confirmed the exact missing `gainLevel()` outside red and authorized the smallest focused maximum-health-growth test plus production implementation of Element 10 only: one gained level changes level 1/maximum health 1000 to level 2/maximum health 1100. Level eligibility, damage/faction progression, current-health refill, damage scaling, and temporary level loss remain unauthorized.
- **Automation evidence:** The public behavior failure isolates the missing synchronized level/maximum-health transition. During verification, a compound read-only inspection command was incorrectly treated as a protected write after automatic BDD enrollment; using single-purpose read commands avoids that guard false positive, and the event is useful input for improving protected-command classification.

### IP-111 — Permit the isolated Element 10 verification worktree

- **Type:** Host filesystem permission checkpoint
- **Stage:** Verification
- **Trigger:** The first isolated behavior-lane attempt passed its repository checks but the sandbox denied Git's write under `.git/worktrees`, which the verifier needs for its temporary detached worktree.
- **Request or event:** Allow the project-local verifier to create and remove its temporary Git worktree for the already-approved Element 10 candidate.
- **Response:** Approved through the host permission prompt.
- **Resulting authorization or action:** Reran the unchanged verifier command with the required filesystem permission. The preliminary behavior lane passed with candidate digest `sha256:1883a23cbe09b440b11d384ef4aa37ae887b3a54a9f47e9181e03c58d1798f75`; no source scope or push authorization was added.
- **Automation evidence:** The verifier's temporary-worktree requirement is deterministic and recurring. Persisting the narrowly scoped `verify_increment.py behavior` permission avoids repeating this host-only interaction while retaining CodeCraft's human behavior checkpoints.

### IP-112 — Commit the verified Element 10 behavior slice

- **Type:** Human protected-file and commit checkpoint
- **Stage:** Commit preparation
- **Trigger:** The exact seven-path behavior candidate plus two allowed evidence paths passed the isolated behavior lane with receipt candidate digest `sha256:081f07821b4e77204524da63eb3f712273b36d3e08e5263126f793d4d85a2452`. Twenty active Java tests and all 55 Starter tests pass; one deferred legacy seed is skipped. Current health remains unchanged during level gain. Complete status contains only those nine relevant paths plus the human's unrelated `README.md` and `.idea` work.
- **Request or event:** Confirm one receipt-bound transaction that stages and commits only the exact candidate and evidence paths with Arlo message `F grow maximum health with level`. Validate before and after the path-limited commit; keep `README.md` and `.idea` unstaged and do not push. The exact transaction identity will be presented after the non-mutating protected-command preflight has registered its digest.
- **Response:** `a`
- **Resulting authorization or action:** Authorized and completed transaction `sha256:0f4a4f5edb19c683b76de4b4593c42cd5014b97a044b41568247d8f78f30dd26`. Commit `f219e4db63e9de38285c4ce807f3b3c7da233628` contains exactly the seven behavior candidate paths and two evidence paths with Arlo message `F grow maximum health with level`. Both staged and committed receipt checks passed; no push occurred.
- **Automation evidence:** The exact candidate includes source, protected BDD assets, focused test, protected registry, plan, and responsibility-map changes. Feature evidence and `interations.md` are evidence-only paths. Read-only guard classification was also observed to reject directory `ls` and an `execute --help` query, suggesting the allowlist should recognize common read-only discovery commands and help invocations without weakening mutation protection.

### IP-113 — Continue to higher-level target damage reduction

- **Type:** Human continuation
- **Stage:** Planning assessment
- **Trigger:** Element 10 maximum-health growth was committed and its CodeCraft run completed. The human requested continuation to the next provisional roadmap item.
- **Request or event:** Assess damage reduction when the target is above the attacker in level, including the 50% cap and the unresolved integer-rounding rule, without implementing before the required human checkpoint.
- **Response:** `continue`
- **Resulting authorization or action:** Opened behavior run `reduce-damage-for-higher-level-target` and assessed Element 11 only. No BDD, expected output, focused test, production code, roadmap, or responsibility-map change is authorized by this continuation alone.
- **Automation evidence:** The next roadmap item and its rounding dependency were deterministically identifiable from the first unchecked plan entries. Bundling the rounding choice into the BDD design checkpoint avoids a separate interaction.

### IP-114 — Define capped damage reduction against a higher-level target

- **Type:** Human BDD design and specification checkpoint
- **Stage:** Design
- **Trigger:** `receiveDamage` currently subtracts the requested integer damage unchanged. The later requirements specify 10% reduction per level the target is above the attacker, capped at 50%, while the roadmap deliberately leaves fractional integer rounding for collaboration.
- **Request or event:** Approve Element 11 and the round-down policy: create level 1 Attacker and level 7 Target during Arrange; invoke `target.receiveDamage(attacker, 95)` as the single Act; cap the six-level reduction at 50%; round the resulting 47.5 damage down to 47; assert Target changes from 1000 to 953 health and remains alive. Add `HigherLevelDamageReduction_bdd.higherLevelTargetTakesCappedReducedDamage` and its approved output, then run it against unchanged production code. The predicted outside red is an approval mismatch whose received result reports Target at 905 health because all 95 requested damage is currently applied. Stop for confirmation before focused tests or implementation. Increased damage against lower-level targets, level eligibility, damage/faction progression, current-health refill, temporary level loss, and invalid damage amounts remain outside this slice.
- **Response:** `a`
- **Resulting authorization or action:** Approved the exact Element 11 cap-boundary BDD, round-down policy for fractional modified damage, approved output, and focused outside-red run against unchanged production code. Focused tests and production implementation remain unauthorized until the expected 905-health approval mismatch is confirmed.
- **Automation evidence:** The proposed cap-boundary story covers the cap and fractional rounding with one domain Act. Focused tests after outside-red confirmation can drive sub-cap 10%-per-level calculation without adding another public behavior Act or prematurely extracting a policy abstraction.

### IP-115 — Confirm the Element 11 outside red

- **Type:** Human outside-red checkpoint
- **Stage:** Outside red
- **Trigger:** The approved `HigherLevelDamageReduction_bdd` and expected output were created without changing production code. Its focused Maven run failed exactly as predicted: expected Target at 953 health/alive after capped and rounded damage, but received Target at 905 health/alive because all 95 requested damage was applied.
- **Request or event:** Confirm that the 905-health approval mismatch is the expected outside red. After confirmation, remove the generated received output, add the smallest focused tests for 10%-per-level reduction, the 50% cap, and round-down behavior, then implement Element 11 only. Increased damage against lower-level targets, level eligibility, damage/faction progression, current-health refill, temporary level loss, and invalid damage amounts remain later slices.
- **Response:** `a`
- **Resulting authorization or action:** Confirmed the exact 905-health outside red and authorized removal of its generated received output, the smallest focused tests for per-level reduction, the 50% cap, and round-down behavior, plus production implementation of Element 11 only. Increased damage against lower-level targets, level eligibility, damage/faction progression, current-health refill, temporary level loss, and invalid damage amounts remain unauthorized.
- **Automation evidence:** The public behavior failure isolates the absent higher-level target modifier while preserving the previously established level and maximum-health state. The exact expected and received values make this checkpoint mechanically recognizable.

### IP-116 — Commit the verified Element 11 behavior slice

- **Type:** Human protected-file and commit checkpoint
- **Stage:** Commit preparation
- **Trigger:** The exact seven-path behavior candidate plus two allowed evidence paths passed the isolated behavior lane with receipt candidate digest `sha256:54f037c42562825aa6fdf3db2f183eee4aee561b34e4f42bd5b2605751d72c5c`. Twenty-three active Java tests and all 55 Starter tests pass; one deferred legacy seed is skipped. No generated received output remains. Complete status contains only those nine relevant paths plus the human's unrelated `README.md` and `.idea` work.
- **Request or event:** Confirm one receipt-bound transaction that stages and commits only the exact candidate and evidence paths with Arlo message `F reduce damage against higher-level targets`. Validate before and after the path-limited commit; keep `README.md` and `.idea` unstaged and do not push. The exact transaction identity will be presented after the non-mutating protected-command preflight has registered its digest.
- **Response:** `a`
- **Resulting authorization or action:** Authorized and completed transaction `sha256:37f3182198160a1a0b10c7f99cbf6d3289297dfe96fdcd6c84dd1af645214427`. Commit `70478189adf65ebb1ed92416b86e56479b91657c` contains exactly the seven behavior candidate paths and two evidence paths with Arlo message `F reduce damage against higher-level targets`. Both staged and committed receipt checks passed; no push occurred.
- **Automation evidence:** The exact candidate includes source, protected BDD assets, focused test, protected registry, plan, and responsibility-map changes. Feature evidence and `interations.md` are evidence-only paths. The persistent verifier permission avoided another host-filesystem interaction for both isolated lanes.

### IP-117 — Continue to lower-level target damage increase

- **Type:** Human continuation
- **Stage:** Planning assessment
- **Trigger:** Element 11 higher-level target damage reduction was committed and its CodeCraft run completed. The human requested continuation to the next provisional roadmap item.
- **Request or event:** Assess increased damage when the target is below the attacker in level, reusing the already-approved 50% cap and round-down integer policy, without implementing before the required human checkpoint.
- **Response:** `continue`
- **Resulting authorization or action:** Opened behavior run `increase-damage-against-lower-level-target` and assessed Element 12 only. No BDD, expected output, focused test, production code, roadmap, or responsibility-map change is authorized by this continuation alone.
- **Automation evidence:** The next roadmap item, existing round-down decision, and symmetric cap example were deterministically identifiable, so no separate specification question was needed.

### IP-118 — Define capped damage increase against a lower-level target

- **Type:** Human BDD design checkpoint
- **Stage:** Design
- **Trigger:** `receiveDamage` now reduces damage only when the target is above the attacker; a target below the attacker still receives the unchanged requested amount. The remaining Levels rule requires a 10% increase per attacker level advantage, capped at 50%, using the established round-down policy.
- **Request or event:** Approve Element 12: create level 7 Attacker and level 1 Target during Arrange; invoke `target.receiveDamage(attacker, 95)` as the single Act; cap the six-level increase at 50%; round the resulting 142.5 damage down to 142; assert Target changes from 1000 to 858 health and remains alive. Add `LowerLevelDamageIncrease_bdd.lowerLevelTargetTakesCappedIncreasedDamage` and its approved output, then run it against unchanged production code. The predicted outside red is an approval mismatch whose received result reports Target at 905 health because only the requested 95 damage is currently applied. Stop for confirmation before focused tests or implementation. Factions, level eligibility, damage/faction progression, current-health refill, temporary level loss, and invalid damage amounts remain outside this slice.
- **Response:** `a`
- **Resulting authorization or action:** Approved the exact Element 12 cap-boundary BDD, reuse of the established round-down policy, approved output, and focused outside-red run against unchanged production code. Focused tests, production implementation, and any private calculation refactoring remain unauthorized until the expected 905-health approval mismatch is confirmed.
- **Automation evidence:** The cap-boundary story reuses the approved rounding policy and one domain Act. This second symmetric modifier creates concrete pressure for one cohesive private level-modifier calculation, but no collaborator, interface, or public API is warranted.

### IP-119 — Confirm the Element 12 outside red

- **Type:** Human outside-red checkpoint
- **Stage:** Outside red
- **Trigger:** The approved `LowerLevelDamageIncrease_bdd` and expected output were created without changing production code. Its focused Maven run failed exactly as predicted: expected Target at 858 health/alive after capped and rounded increased damage, but received Target at 905 health/alive because only the requested 95 damage was applied.
- **Request or event:** Confirm that the 905-health approval mismatch is the expected outside red. After confirmation, remove the generated received output, add the smallest focused tests for 10%-per-level increase, the 50% cap, and round-down behavior, then implement Element 12 and consolidate the now-symmetric calculation privately while green. Factions, level eligibility, damage/faction progression, current-health refill, temporary level loss, and invalid damage amounts remain later slices.
- **Response:** `a`
- **Resulting authorization or action:** Confirmed the exact 905-health outside red and authorized removal of its generated received output, the smallest focused tests for per-level increase, the 50% cap, and round-down behavior, production implementation of Element 12, and private consolidation of the symmetric level modifier while green. Factions, level eligibility, damage/faction progression, current-health refill, temporary level loss, and invalid damage amounts remain unauthorized.
- **Automation evidence:** The public behavior failure isolates the missing lower-level target modifier while the matching higher-level reduction remains intact. The exact expected and received values make this checkpoint mechanically recognizable.

### IP-120 — Commit the verified Element 12 behavior slice

- **Type:** Human protected-file and commit checkpoint
- **Stage:** Commit preparation
- **Trigger:** The exact seven-path behavior candidate plus two allowed evidence paths passed the isolated behavior lane with receipt candidate digest `sha256:3bf3f5b5ef2b085943e299b4c47667d0300c87a513beb127c4744f49314043fc`. Twenty-six active Java tests and all 55 Starter tests pass; one deferred legacy seed is skipped. Both level modifiers share one private signed calculation, and no generated received output remains. Complete status contains only those nine relevant paths plus the human's unrelated `README.md` and `.idea` work.
- **Request or event:** Confirm one receipt-bound transaction that stages and commits only the exact candidate and evidence paths with Arlo message `F increase damage against lower-level targets`. Validate before and after the path-limited commit; keep `README.md` and `.idea` unstaged and do not push. The exact transaction identity will be presented after the non-mutating protected-command preflight has registered its digest.
- **Response:** `a`
- **Resulting authorization or action:** Authorized and completed transaction `sha256:1450b296ef53fab9c12343a70b2b4e473b1d4c62daa49f680aea1b5195098f6e`. Commit `bc4fb274ebe84b5d7ebc7a86d677689916bdf3c8` contains exactly the seven behavior candidate paths and two evidence paths with Arlo message `F increase damage against lower-level targets`. Both staged and committed receipt checks passed; no push occurred.
- **Automation evidence:** The exact candidate includes source, protected BDD assets, focused test, protected registry, plan, and responsibility-map changes. Feature evidence and `interations.md` are evidence-only paths. The same candidate/evidence shape and preflight ordering continue to avoid separate protected-file and commit approvals.

### IP-121 — Continue to empty initial faction membership

- **Type:** Human continuation
- **Stage:** Planning assessment
- **Trigger:** Element 12 lower-level target damage increase was committed and its CodeCraft run completed, finishing the current Levels and damage-scaling phase. The human requested continuation to the first provisional Factions item.
- **Request or event:** Assess the rule that a newly created character belongs to no faction without implementing before the required human checkpoint.
- **Response:** `continue`
- **Resulting authorization or action:** Opened behavior run `initialize-character-factions` and assessed Element 13 only. No domain type, BDD, expected output, focused test, production code, roadmap, or responsibility-map change is authorized by this continuation alone.
- **Automation evidence:** The next unchecked roadmap item was deterministically identifiable. A named `Faction` object plus a read-only membership query establishes the smallest domain protocol needed for this behavior and the immediately following join/leave rules.

### IP-122 — Define a new character's empty faction membership

- **Type:** Human BDD design checkpoint
- **Stage:** Design
- **Trigger:** `PlayerCharacter` currently has no faction concept. The requirements say a new character belongs to no faction, and later rules need characters to join, leave, and compare faction memberships.
- **Request or event:** Approve Element 13: create Hero and a named Knights faction during Arrange; invoke `hero.belongsTo(knights)` as the single Act; assert `Hero belongs to Knights: false.` Add `NewCharacterFaction_bdd.newCharacterBelongsToNoFaction` and its approved output, then run it against unchanged production code. The predicted outside red is test-compilation failure because `Faction` and the `PlayerCharacter.belongsTo(Faction)` protocol do not exist. Stop for confirmation before focused tests or implementation. Joining, leaving, equality between separately constructed same-name factions, allies, ally damage/healing, faction-based progression, and magical objects remain outside this slice.
- **Response:** `a`
- **Resulting authorization or action:** Approved the exact BDD, expected output, named `Faction` object, and `belongsTo` query for the outside-red run only. Focused tests and production implementation remain unauthorized until the human confirms the observed red.
- **Automation evidence:** `PlayerCharacter` is the membership information, decision, and state owner; `Faction` supplies domain identity and a name. A query preserves encapsulation instead of exposing a mutable membership collection, while faction equality semantics remain deferred until a behavior depends on them.

### IP-123 — Confirm empty faction membership outside red

- **Type:** Human outside-red checkpoint
- **Stage:** Outside red
- **Trigger:** The approved `NewCharacterFaction_bdd.newCharacterBelongsToNoFaction` scenario was added with its exact approved output and run against unchanged production code.
- **Request or event:** Confirm that Maven's test-compilation failure is the expected outside red: `NewCharacterFaction_bdd.java:11` cannot find symbol `Faction`. Compilation stops at the missing domain type before it can resolve the planned `PlayerCharacter.belongsTo(Faction)` query. Authorize the next slice: add one focused empty-membership test, observe its red, then implement only the named `Faction` domain object and read-only membership query needed to make the focused and BDD tests green.
- **Response:** `a`
- **Resulting authorization or action:** Confirmed the expected missing-`Faction` outside red and authorized the complete next slice: add one focused empty-membership test, record its red, then implement only the named `Faction` domain object and read-only membership query needed to make the focused and BDD tests green.
- **Automation evidence:** The failure is at the intended domain boundary, not in test infrastructure or approved-output comparison. Production sources remain unchanged.

### IP-124 — Commit the verified empty initial faction behavior

- **Type:** Human protected-file and commit checkpoint
- **Stage:** Commit preparation
- **Trigger:** The exact eight-path behavior candidate plus two evidence paths passed the isolated behavior lane with receipt candidate digest `sha256:5d75a246a5b572f19f401d4b7e116d9274a17aa8a9d4431049a8f84e2c757b18`. Twenty-eight active Java tests and all 55 Starter tests pass; one deferred legacy seed is skipped. Complete status contains only those ten relevant paths plus the human's unrelated `README.md` and `.idea` work.
- **Request or event:** Confirm one receipt-bound transaction that stages and commits only the exact candidate and evidence paths with Arlo message `F start characters without factions`. Validate before and after the path-limited commit; keep `README.md` and `.idea` unstaged and do not push. The exact transaction identity will be presented after the non-mutating protected-command preflight has registered its digest.
- **Response:** `a`
- **Resulting authorization or action:** Authorized and completed transaction `sha256:0910274194d0e8a5d7861ddb5de60adb97e5ddfc7e84cebdb121c6b08713e766`. Commit `812ac03f1d7e914237929724033fee9fb9674e0d` contains exactly the eight behavior candidate paths and two evidence paths with Arlo message `F start characters without factions`. Both staged and committed receipt checks passed; no push occurred.
- **Automation evidence:** The executable/design candidate contains the protected registry, roadmap, responsibility map, two production paths, two protected BDD assets, and the focused test. The feature artifact and `interations.md` are evidence-only so recording the receipt cannot invalidate the verified candidate digest.

### IP-125 — Continue to joining factions

- **Type:** Human continuation
- **Stage:** Planning assessment
- **Trigger:** Element 13 empty initial faction membership was committed and its CodeCraft run completed. The human requested continuation to the next provisional Factions item.
- **Request or event:** Assess the rule that a character can join one or more factions without implementing before the required human checkpoint.
- **Response:** `continue`
- **Resulting authorization or action:** Opened behavior run `join-character-factions` and assessed Element 14 only. No BDD, expected output, focused test, production method, roadmap, or responsibility-map change is authorized by this continuation alone.
- **Automation evidence:** The next unchecked roadmap item is deterministic. The existing identity-based `Faction` objects and encapsulated `PlayerCharacter` membership set provide the required state boundary; only a joining command is missing.

### IP-126 — Define joining more than one faction

- **Type:** Human BDD design checkpoint
- **Stage:** Design
- **Trigger:** `PlayerCharacter` owns an initially empty membership set and can answer `belongsTo`, but exposes no command that changes membership. The requirements allow one character to belong to one or more factions.
- **Request or event:** Approve Element 14: create Hero plus named Knights and Mages factions; join Knights during Arrange; invoke `hero.join(mages)` as the single Act; assert Hero still belongs to Knights and now belongs to Mages. Add `CharacterJoinsFactions_bdd.characterCanJoinMoreThanOneFaction` and its approved output, then run it against unchanged production code. The predicted outside red is test-compilation failure because `PlayerCharacter.join(Faction)` does not exist. Stop for confirmation before focused tests or implementation. Leaving, equality between separately constructed same-name factions, allies, ally damage/healing, non-ally healing, faction-based progression, and magical objects remain outside this slice.
- **Response:** `a`
- **Resulting authorization or action:** Approved the exact multiple-membership BDD, expected output, and `join(Faction)` protocol for the outside-red run only. Focused tests and production implementation remain unauthorized until the human confirms the observed red.
- **Automation evidence:** `PlayerCharacter` remains the receiver, membership information owner, decision owner, and state owner. `Faction` supplies identity and name. The public protocols are `join(Faction)` for the state change and `belongsTo(Faction)` for observation; no dependency abstraction, injection point, or composition root is required.

### IP-127 — Confirm joining-factions outside red

- **Type:** Human outside-red checkpoint
- **Stage:** Outside red
- **Trigger:** The approved `CharacterJoinsFactions_bdd.characterCanJoinMoreThanOneFaction` scenario was added with its exact approved output and run against unchanged production code.
- **Request or event:** Confirm that Maven's test-compilation failures are the expected outside red: `CharacterJoinsFactions_bdd.java:13` and `:16` cannot find `PlayerCharacter.join(Faction)`. Authorize the next slice: add one focused test showing an existing membership survives a second join, record its red, then implement only `PlayerCharacter.join(Faction)` by adding the supplied faction to the character's existing membership set.
- **Response:** `a`
- **Resulting authorization or action:** Confirmed the expected missing-`join(Faction)` outside red and authorized the complete next slice: add one focused multiple-membership test, record its red, then implement only `PlayerCharacter.join(Faction)` by adding the supplied faction to the existing membership set.
- **Automation evidence:** Both compilation errors identify the same intended missing command, while the existing `Faction` identity and `belongsTo` observation protocols compile. Production sources remain unchanged.

### IP-128 — Commit the verified faction-joining behavior

- **Type:** Human protected-file and commit checkpoint
- **Stage:** Commit preparation
- **Trigger:** The exact seven-path behavior candidate plus two evidence paths passed the isolated behavior lane with receipt candidate digest `sha256:ff238c9f9cd90f2d0d86b5bfaeeabb4105adc5478dfd073e38afb78265f02c53`. Thirty active Java tests and all 55 Starter tests pass; one deferred legacy seed is skipped. Complete status contains only those nine relevant paths plus the human's unrelated `README.md` and `.idea` work.
- **Request or event:** Confirm one receipt-bound transaction that stages and commits only the exact candidate and evidence paths with Arlo message `F allow characters to join factions`. Validate before and after the path-limited commit; keep `README.md` and `.idea` unstaged and do not push. The exact transaction identity will be presented after the non-mutating protected-command preflight has registered its digest.
- **Response:** `a`
- **Resulting authorization or action:** Authorized and completed transaction `sha256:4e6c9388ffc1f7bda5030368b6fffaa328db615952929fac86e20b8282893cb1`. Commit `b8702ccb309e3501137187f6452020d99b6e6179` contains exactly the seven behavior candidate paths and two evidence paths with Arlo message `F allow characters to join factions`. Both staged and committed receipt checks passed; no push occurred.
- **Automation evidence:** The executable/design candidate contains the protected registry, roadmap, responsibility map, production command, two protected BDD assets, and focused test. The feature artifact and `interations.md` are evidence-only, preserving receipt stability while still committing the full audit trail.

### IP-133 — Continue to shared-faction allies

- **Type:** Human continuation
- **Stage:** Planning assessment
- **Trigger:** Element 15 faction leaving was committed and its CodeCraft run completed. The human requested continuation to the next provisional Factions item.
- **Request or event:** Assess the rule that two characters sharing at least one faction are allies, without implementing before the required human checkpoint.
- **Response:** `continue`
- **Resulting authorization or action:** Opened behavior run `recognize-shared-faction-allies` and assessed Element 16 only. No BDD, expected output, focused test, production query, roadmap, or responsibility-map change is authorized by this continuation alone.
- **Automation evidence:** The next unchecked roadmap item is deterministic. Each `PlayerCharacter` already owns an encapsulated identity-based membership set, so alliance can be answered by one character comparing memberships with another without exposing either collection.

### IP-134 — Define shared-faction alliance

- **Type:** Human BDD design checkpoint
- **Stage:** Design
- **Trigger:** Characters can join, leave, and query faction membership, but there is no domain query that identifies allies. The requirements define characters sharing a faction as allies.
- **Request or event:** Approve Element 16: create Hero, Companion, and named Knights; join both characters to the same Knights object during Arrange; invoke `hero.isAlliedWith(companion)` as the single Act; assert the result is true. Add `SharedFactionAlliance_bdd.charactersSharingAFactionAreAllies` and its approved output, then run it against unchanged production code. The predicted outside red is test-compilation failure because `PlayerCharacter.isAlliedWith(PlayerCharacter)` does not exist. Stop for confirmation before focused tests or implementation. Self-alliance, equality between separately constructed same-name factions, explicit no-shared-faction characterization, ally damage/healing, non-ally healing, lifetime faction history/progression, and magical objects remain outside this slice.
- **Response:** `a`
- **Resulting authorization or action:** Approved the exact shared-faction ally BDD, expected output, and `isAlliedWith(PlayerCharacter)` protocol for the outside-red run only. Focused tests and production implementation remain unauthorized until the human confirms the observed red.
- **Automation evidence:** The receiver `PlayerCharacter` owns its memberships and the alliance decision; the other `PlayerCharacter` owns the comparison memberships. `Faction` supplies shared identity. The public protocol is `isAlliedWith(PlayerCharacter)`; no collection exposure, dependency abstraction, injection point, or composition root is required.

### IP-135 — Confirm shared-faction alliance outside red

- **Type:** Human outside-red checkpoint
- **Stage:** Outside red
- **Trigger:** The approved `SharedFactionAlliance_bdd.charactersSharingAFactionAreAllies` scenario was added with its exact approved output and run against unchanged production code.
- **Request or event:** Confirm that Maven's test-compilation failure is the expected outside red: `SharedFactionAlliance_bdd.java:17` cannot find `PlayerCharacter.isAlliedWith(PlayerCharacter)`. Authorize the next slice: add one focused shared-faction test, record its red, then implement only `isAlliedWith` by checking whether the two characters' encapsulated membership sets share at least one exact `Faction` identity.
- **Response:** `a`
- **Resulting authorization or action:** Confirmed the expected missing-`isAlliedWith` outside red and authorized the complete next slice: add one focused shared-faction test, record its red, then implement only the membership-intersection query over the two characters' encapsulated faction sets.
- **Automation evidence:** The compilation failure identifies the intended missing query, while the established faction join protocol compiles. Production sources remain unchanged.

### IP-136 — Commit the verified shared-faction alliance behavior

- **Type:** Human protected-file and commit checkpoint
- **Stage:** Commit preparation
- **Trigger:** The exact seven-path behavior candidate plus two evidence paths passed the isolated behavior lane with receipt candidate digest `sha256:254f62c9acda9af055d701b69dc136ac2b8d4ba66f4046275c7563150bf2515d`. Thirty-four active Java tests and all 55 Starter tests pass; one deferred legacy seed is skipped. Complete status contains only those nine relevant paths plus the human's unrelated `README.md` and `.idea` work.
- **Request or event:** Confirm one receipt-bound transaction that stages and commits only the exact candidate and evidence paths with Arlo message `F recognize shared-faction allies`. Validate before and after the path-limited commit; keep `README.md` and `.idea` unstaged and do not push. The exact transaction identity will be presented after the non-mutating protected-command preflight has registered its digest.
- **Response:** `a`
- **Resulting authorization or action:** Authorized and completed transaction `sha256:d1acf0edb6197fbb2d8e3ce644796ddf4c233b98f6d8ef8cd440f80ccb8012a8`. Commit `11bd3f8f261c842456a4ada58d41b3cab3bd9da6` contains exactly the seven behavior candidate paths and two evidence paths with Arlo message `F recognize shared-faction allies`. Both staged and committed receipt checks passed; no push occurred.
- **Automation evidence:** The executable/design candidate contains the protected registry, roadmap, responsibility map, production query, two protected BDD assets, and focused test. The feature artifact and `interations.md` are evidence-only, preserving receipt stability while still committing the full audit trail.

### IP-137 — Continue to preventing ally damage

- **Type:** Human continuation
- **Stage:** Planning assessment
- **Trigger:** Element 16 shared-faction alliance recognition was committed and its CodeCraft run completed. The human requested continuation to the next provisional Factions item.
- **Request or event:** Assess the rule that allies cannot damage one another, without implementing before the required human checkpoint.
- **Response:** `continue`
- **Resulting authorization or action:** Opened behavior run `prevent-ally-damage` and assessed Element 17 only. No BDD, expected output, focused test, production guard, roadmap, or responsibility-map change is authorized by this continuation alone.
- **Automation evidence:** The next unchecked roadmap item is deterministic. The target `PlayerCharacter` already owns health, received-damage decisions, and the ally query, so it can reject ally damage without a new collaborator. The first run-start command was falsely blocked because its read-only context named an existing protected BDD file; removing that path from operational context allowed the unchanged start request, identifying another avoidable guard interaction pattern.

### IP-138 — Define the ally-damage guard

- **Type:** Human BDD design checkpoint
- **Stage:** Design
- **Trigger:** Shared-faction characters are recognized as allies, but `receiveDamage` currently guards only self-damage and otherwise applies level-adjusted damage. The requirements prohibit allies from damaging one another.
- **Request or event:** Approve Element 17: create Hero and Companion, join both to the same Knights identity, and capture Hero's initial printed state during Arrange; invoke `hero.receiveDamage(companion, 100)` as the single Act; assert Hero remains at 1000 health and alive. Add `AllyDamage_bdd.allyDamageIsIgnored` and its approved output, then run it against unchanged production code. The predicted outside red is an approval mismatch: production reports Hero at 900 health rather than the approved unchanged 1000. Stop for confirmation before focused tests or implementation. Self-alliance, same-name faction equality, changes to non-allied damage, ally healing, non-ally healing, lifetime faction history/progression, and magical objects remain outside this slice.
- **Response:** `a`
- **Resulting authorization or action:** Approved the exact ally-damage BDD, unchanged-health output, and predicted 900-health approval mismatch for the outside-red run only. Focused tests and production implementation remain unauthorized until the human confirms the observed red.
- **Automation evidence:** The target `PlayerCharacter` is the receiver, health state owner, and damage-admission decision owner; the attacker supplies its membership identity through the established `isAlliedWith` protocol. No new dependency abstraction, injection point, or composition root is required.

### IP-139 — Confirm ally-damage outside red

- **Type:** Human outside-red checkpoint
- **Stage:** Outside red
- **Trigger:** The approved `AllyDamage_bdd.allyDamageIsIgnored` scenario was added with its exact approved output and run against unchanged production code.
- **Request or event:** Confirm the expected approval mismatch: the approved output keeps Hero alive at 1000 health, while the received output shows allied Companion's 100 damage reduced Hero to 900 health. Authorize the next slice: remove the generated received output, add one focused ally-damage test, record its 900-versus-1000 red, then implement only an ally guard in `PlayerCharacter.receiveDamage` before damage scaling and health mutation.
- **Response:** `a`
- **Resulting authorization or action:** Confirmed the expected 900-versus-1000 approval mismatch and authorized the complete next slice: remove the generated received output, add one focused ally-damage test, record its red, then implement only an ally guard in `PlayerCharacter.receiveDamage` before damage scaling and health mutation.
- **Automation evidence:** The mismatch is the exact predicted domain failure rather than a compilation or test-infrastructure problem. Production sources remain unchanged.

### IP-129 — Continue to leaving a faction

- **Type:** Human continuation
- **Stage:** Planning assessment
- **Trigger:** Element 14 faction joining was committed and its CodeCraft run completed. The human requested continuation to the next provisional Factions item.
- **Request or event:** Assess the rule that a character can leave one faction without affecting membership in other factions, without implementing before the required human checkpoint.
- **Response:** `continue`
- **Resulting authorization or action:** Opened behavior run `leave-character-faction` and assessed Element 15 only. No BDD, expected output, focused test, production method, roadmap, or responsibility-map change is authorized by this continuation alone.
- **Automation evidence:** The next unchecked roadmap item is deterministic. `PlayerCharacter` already owns the identity-based membership set and its join/query protocols, so leaving can remain an encapsulated character command.

### IP-130 — Define leaving one faction while preserving another

- **Type:** Human BDD design checkpoint
- **Stage:** Design
- **Trigger:** `PlayerCharacter` can join and query multiple memberships but exposes no command to remove one. The requirements allow leaving factions, and the roadmap makes preservation of other memberships explicit.
- **Request or event:** Approve Element 15: create Hero plus named Knights and Mages factions and join Hero to both during Arrange; invoke `hero.leave(knights)` as the single Act; assert Hero no longer belongs to Knights and still belongs to Mages. Add `CharacterLeavesFaction_bdd.leavingOneFactionPreservesOtherMemberships` and its approved output, then run it against unchanged production code. The predicted outside red is test-compilation failure because `PlayerCharacter.leave(Faction)` does not exist. Stop for confirmation before focused tests or implementation. Leaving an unjoined faction, equality between separately constructed same-name factions, allies, ally damage/healing, non-ally healing, lifetime faction history/progression, and magical objects remain outside this slice.
- **Response:** `a`
- **Resulting authorization or action:** Approved the exact leave-one-preserve-one BDD, expected output, and `leave(Faction)` protocol for the outside-red run only. Focused tests and production implementation remain unauthorized until the human confirms the observed red.
- **Automation evidence:** `PlayerCharacter` remains the receiver, membership information owner, decision owner, and state owner. `Faction` supplies identity and name. The public protocols are `leave(Faction)` for the state change and `belongsTo(Faction)` for observation; no dependency abstraction, injection point, or composition root is required.

### IP-131 — Confirm leaving-faction outside red

- **Type:** Human outside-red checkpoint
- **Stage:** Outside red
- **Trigger:** The approved `CharacterLeavesFaction_bdd.leavingOneFactionPreservesOtherMemberships` scenario was added with its exact approved output and run against unchanged production code.
- **Request or event:** Confirm that Maven's test-compilation failure is the expected outside red: `CharacterLeavesFaction_bdd.java:17` cannot find `PlayerCharacter.leave(Faction)`. Authorize the next slice: add one focused test showing removal of Knights preserves Mages, record its red, then implement only `PlayerCharacter.leave(Faction)` by removing the supplied faction from the character's existing membership set.
- **Response:** `a`
- **Resulting authorization or action:** Confirmed the expected missing-`leave(Faction)` outside red and authorized the complete next slice: add one focused preservation test, record its red, then implement only `PlayerCharacter.leave(Faction)` by removing the supplied faction from the existing membership set.
- **Automation evidence:** The compilation failure identifies the intended missing command, while the established join and membership-query protocols compile. Production sources remain unchanged.

### IP-132 — Commit the verified faction-leaving behavior

- **Type:** Human protected-file and commit checkpoint
- **Stage:** Commit preparation
- **Trigger:** The exact seven-path behavior candidate plus two evidence paths passed the isolated behavior lane with receipt candidate digest `sha256:e52d5d9cfde75f48a9b2af3fd56267098d7203b978c757688b5abad581ab193b`. Thirty-two active Java tests and all 55 Starter tests pass; one deferred legacy seed is skipped. Complete status contains only those nine relevant paths plus the human's unrelated `README.md` and `.idea` work.
- **Request or event:** Confirm one receipt-bound transaction that stages and commits only the exact candidate and evidence paths with Arlo message `F allow characters to leave factions`. Validate before and after the path-limited commit; keep `README.md` and `.idea` unstaged and do not push. The exact transaction identity will be presented after the non-mutating protected-command preflight has registered its digest.
- **Response:** `a`
- **Resulting authorization or action:** Authorized and completed transaction `sha256:63bdf2406c1daad22adc3ce442fae7502553ef1941fcc78f595055f50e242aef`. Commit `5e4400fbff194540bdbf90e17601c1faf3eaf1af` contains exactly the seven behavior candidate paths and two evidence paths with Arlo message `F allow characters to leave factions`. Both staged and committed receipt checks passed; no push occurred.
- **Automation evidence:** The executable/design candidate contains the protected registry, roadmap, responsibility map, production command, two protected BDD assets, and focused test. The feature artifact and `interations.md` are evidence-only, preserving receipt stability while still committing the full audit trail.

### IP-140 — Commit the verified ally-damage guard

- **Type:** Human protected-file and commit checkpoint
- **Stage:** Commit preparation
- **Trigger:** The exact seven-path behavior candidate plus two evidence paths passed the isolated behavior lane with receipt candidate digest `sha256:b73eef2eaa8fe139d733ced234400a9a08f7d52fb704483c053b25dad0278c5e`. Thirty-six active Java tests and all 55 Starter tests pass; one deferred legacy seed is skipped. Complete status contains only those nine relevant paths plus the human's unrelated `README.md` and `.idea` work.
- **Request or event:** Confirm one receipt-bound transaction that stages and commits only the exact candidate and evidence paths with Arlo message `F prevent allies from damaging one another`. Validate before and after the path-limited commit; keep `README.md` and `.idea` unstaged and do not push. The exact transaction identity will be presented after the non-mutating protected-command preflight has registered its digest.
- **Response:** `a`
- **Resulting authorization or action:** Authorized and completed transaction `sha256:52e59804e8a92509979f9155d620cbe61e1de4a757f60a8db360b7bab5c02fa5`. Commit `65c970750b57347ac6d26b970ade2cf7e1f5d344` contains exactly the seven behavior candidate paths and two evidence paths with Arlo message `F prevent allies from damaging one another`. Both staged and committed receipt checks passed; no push occurred.
- **Automation evidence:** The executable/design candidate contains the protected registry, roadmap, responsibility map, production guard, two protected BDD assets, and focused test. The feature artifact and `interations.md` are evidence-only, preserving receipt stability while still committing the full audit trail. A combined read-only status/generated-output inspection was falsely blocked because its scan surfaced protected paths; retrying status and diff inspection without that protected scan succeeded and changed no repository state.

### IP-141 — Continue to allied healing

- **Type:** Human continuation
- **Stage:** Planning assessment
- **Trigger:** Element 17 preventing allied damage was committed and its CodeCraft run completed. The human requested continuation to the next provisional Factions item.
- **Request or event:** Assess the rule that allies can heal one another, without implementing before the required human checkpoint.
- **Response:** `continue`
- **Resulting authorization or action:** Opened behavior run `heal-allied-character` and assessed Element 18 only. No BDD, expected output, focused test, production overload, roadmap, or responsibility-map change is authorized by this continuation alone.
- **Automation evidence:** The next unchecked roadmap item is deterministic. `PlayerCharacter` already owns alliance recognition and living-health restoration. An ally-healing command can tell the target to use its existing health-restoration behavior without exposing health state or adding a collaborator. A combined read-only discovery command was falsely blocked because its test-directory scan surfaced protected assets; retrying with explicit non-protected paths succeeded and changed no repository state.

### IP-142 — Define allied healing

- **Type:** Human BDD design checkpoint
- **Stage:** Design
- **Trigger:** Shared-faction characters are recognized as allies, and a living damaged character can restore its own health, but no character-to-character healing protocol exists.
- **Request or event:** Approve Element 18: create Hero, Companion, Orc, and a named Knights faction; damage Hero from 1000 to 900 through Orc, join Hero and Companion to the same Knights identity, and capture Hero's printed state during Arrange; invoke `companion.heal(hero, 50)` as the single Act; assert Hero becomes 950 health and remains alive. Add `AllyHealing_bdd.allyCanHealADamagedCharacter` and its approved output, then run it against unchanged production code. The predicted outside red is test-compilation failure because `PlayerCharacter.heal(PlayerCharacter, int)` does not exist. Stop for confirmation before focused tests or implementation. Non-ally healing denial, changes to self-healing, dead-target healing changes, faction equality, faction progression, damage behavior, and magical objects remain outside this slice.
- **Response:** `a`
- **Resulting authorization or action:** Approved the exact allied-healing BDD, expected output, `heal(PlayerCharacter, int)` protocol, and predicted missing-overload compilation failure for the outside-red run only. Focused tests and production implementation remain unauthorized until the human confirms the observed red.
- **Automation evidence:** The healer receives the public command and coordinates with the target; the target remains the health and life-state owner and can apply its existing bounded living-character restoration behavior. The positive shared-faction example establishes the new protocol without preempting the separately planned non-ally rejection rule. No interface, injection point, or composition root is required.

### IP-143 — Confirm allied-healing outside red

- **Type:** Human outside-red checkpoint
- **Stage:** Outside red
- **Trigger:** The approved `AllyHealing_bdd.allyCanHealADamagedCharacter` scenario was added with its exact approved output and run against unchanged production code.
- **Request or event:** Confirm that Maven's test-compilation failure is the expected outside red: `AllyHealing_bdd.java:21` cannot apply `PlayerCharacter.heal` to `(PlayerCharacter, int)` because only `heal(int)` exists. Authorize the next slice: add one focused allied-healing test, record the same missing-overload red, then implement only `PlayerCharacter.heal(PlayerCharacter, int)` by telling the target to apply its existing `heal(int)` behavior. Do not add the non-ally rejection guard in Element 18; that remains the next separately approved behavior.
- **Response:** `a`
- **Resulting authorization or action:** Confirmed the expected missing-overload outside red and authorized the complete Element 18 slice: add one focused allied-healing test, record its compilation red, then add only `PlayerCharacter.heal(PlayerCharacter, int)` delegating restoration to the target's existing `heal(int)` behavior. The Element 19 non-ally rejection guard remains unauthorized.
- **Automation evidence:** The compilation failure identifies the intended missing character-to-character protocol while the existing self-healing behavior remains unchanged. The target can retain all living-state and maximum-health decisions through delegation; an alliance-admission guard would prematurely implement Element 19 and is therefore excluded from this slice.

### IP-144 — Commit the verified allied-healing behavior

- **Type:** Human protected-file and commit checkpoint
- **Stage:** Commit preparation
- **Trigger:** The exact seven-path behavior candidate plus two evidence paths passed the isolated behavior lane with receipt candidate digest `sha256:4d8645e6364e69341ab6cfa4b5b77eeb00c9d07c15806d97d66c0849ae0f7621`. Thirty-eight active Java tests and all 55 Starter tests pass; one deferred legacy seed is skipped. Complete status contains only those nine relevant paths plus the human's unrelated `README.md` and `.idea` work.
- **Request or event:** Confirm one receipt-bound transaction that stages and commits only the exact candidate and evidence paths with Arlo message `F allow allies to heal one another`. Validate before and after the path-limited commit; keep `README.md` and `.idea` unstaged and do not push. The exact transaction identity will be presented after the non-mutating protected-command preflight has registered its digest.
- **Response:** `a`
- **Resulting authorization or action:** Authorized and completed transaction `sha256:8625965a4c5c48dfa562dabb995f9153b6beecf570edb29e43b2f6ef05b96c1c`. Commit `d1d9bfe25680b0a39d2b3de1de0ff0fd98cc1960` contains exactly the seven behavior candidate paths and two evidence paths with Arlo message `F allow allies to heal one another`. Both staged and committed receipt checks passed; no push occurred.
- **Automation evidence:** The executable/design candidate contains the protected registry, roadmap, responsibility map, production overload, two protected BDD assets, and focused test. The feature artifact and `interations.md` are evidence-only, preserving receipt stability while still committing the full audit trail.

### IP-145 — Continue to rejecting non-ally healing

- **Type:** Human continuation
- **Stage:** Planning assessment
- **Trigger:** Element 18 allied healing was committed and its CodeCraft run completed. The human requested continuation to the next provisional Factions item.
- **Request or event:** Assess the rule that a character cannot heal a non-ally, without implementing before the required human checkpoint.
- **Response:** `continue`
- **Resulting authorization or action:** Opened behavior run `prevent-non-ally-healing` and assessed Element 19 only. No BDD, expected output, focused test, production guard, roadmap, or responsibility-map change is authorized by this continuation alone.
- **Automation evidence:** The next unchecked roadmap item is deterministic. The healing `PlayerCharacter` already owns the character-to-character command and alliance query, so it can decide admission before delegating restoration to the target. The target remains the sole health-state owner; no new collaborator is needed.

### IP-146 — Define non-ally healing rejection

- **Type:** Human BDD design checkpoint
- **Stage:** Design
- **Trigger:** Character-to-character healing delegates directly to the target's restoration behavior, so a character with no shared faction can currently heal the target. The requirements prohibit non-allies from healing one another.
- **Request or event:** Approve Element 19: create Hero, Stranger, and Orc with no faction memberships; damage Hero from 1000 to 900 through Orc and capture Hero's printed state during Arrange; invoke `stranger.heal(hero, 50)` as the single Act; assert Hero remains at 900 health and alive. Add `NonAllyHealing_bdd.nonAllyHealingIsIgnored` and its approved output, then run it against unchanged production code. The predicted outside red is an approval mismatch: production reports Hero at 950 health rather than the approved unchanged 900. Stop for confirmation before focused tests or implementation. Changes to allied or self-healing, dead-target healing, self-alliance, faction equality, faction progression, damage behavior, and magical objects remain outside this slice.
- **Response:** `a`
- **Resulting authorization or action:** Approved the exact non-ally-healing BDD, unchanged-health output, and predicted 950-versus-900 approval mismatch for the outside-red run only. Focused tests and production implementation remain unauthorized until the human confirms the observed red.
- **Automation evidence:** The healer receives the command, owns the admission decision, and can reuse `isAlliedWith(target)` without exposing either membership collection. The target remains the health and life-state owner and receives no restoration command when admission fails. No interface, injection point, or composition root is required.

### IP-147 — Confirm non-ally-healing outside red

- **Type:** Human outside-red checkpoint
- **Stage:** Outside red
- **Trigger:** The approved `NonAllyHealing_bdd.nonAllyHealingIsIgnored` scenario was added with its exact approved output and run against unchanged production code.
- **Request or event:** Confirm the expected approval mismatch: the approved output keeps Hero alive at 900 health, while the received output shows Stranger's 50 healing raised Hero to 950 health. Authorize the next slice: remove the generated received output, add one focused non-ally-healing test, record its 950-versus-900 red, then implement only an alliance-admission guard in `PlayerCharacter.heal(PlayerCharacter, int)` before delegating restoration to the target.
- **Response:** Pending human response.
- **Resulting authorization or action:** The protected BDD assets and generated received evidence exist, and the expected outside red is recorded. No focused test, generated-output cleanup, or production implementation is authorized until confirmation.
- **Automation evidence:** The mismatch is the exact predicted domain failure rather than a compilation or test-infrastructure problem. Production sources remain unchanged, and existing allied and self-healing protocols still compile.
