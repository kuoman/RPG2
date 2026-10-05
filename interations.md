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
