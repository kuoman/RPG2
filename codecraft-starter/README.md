# CodeCraft Starter

Version: 0.4.1

CodeCraft Starter can create a minimal Java/Maven build in a build-less directory or install a repository-local collaborative development workflow into an existing Maven project. The target repository receives its own AI instructions, project agreement, skills, protection hook, active-run state, review ledger, and isolated completion verifier. It does not depend on this RPG Combat repository after installation.

## Support boundary

- Profile: Java with Maven Wrapper
- Host: macOS or Linux with Git and Python 3.11 or newer
- Required project command: a working Maven verification command, normally `./mvnw verify`
- Codex: instructions, protected-asset guard hooks, and repository permission guidance; the host sandbox remains the stronger enforcement boundary
- Claude: compatible instructions; technical enforcement depends on the host's hook support
- Existing instruction or hook files: installation stops on managed-file conflicts instead of overwriting them
- Build-specific quality integration: supplied as a reviewed adapter under `.codecraft/profiles/java-maven/`; it is not silently merged into an existing POM

## Bootstrap a new project

From an existing, build-less project directory, run the starter directly from wherever you copied it:

```shell
python3 /path/to/codecraft-starter/bin/codecraft_starter.py bootstrap \
  --target . \
  --project-name "My Project" \
  --group-id com.example \
  --artifact-id my-project \
  --java-version 21
```

Only `--target` is needed. Project name and artifact ID default from the target directory; group ID defaults to `com.example`, and Java defaults to 21.

Bootstrap checks Git, Java, `javac --release`, Maven, and Python before writing. It refuses an existing Maven or Gradle build, malformed Git metadata, and symlinked destinations; initializes Git when needed; creates a minimal JUnit-capable POM and source roots; generates a pinned Maven 3.9.12 Wrapper; compiles a temporary smoke source through `./mvnw verify`; installs CodeCraft; and runs the installed health checks. If a later step fails, only operation-owned paths and files demonstrably changed by the operation are rolled back; unrelated project files and filesystem nodes are left untouched.

Bootstrap requires exclusive write access to the target for the duration of the command. A root `.codecraft-bootstrap.lock` prevents overlapping bootstrap runs and is removed after success, failure, or a normal keyboard interrupt; do not edit the target from another process until the command finishes. If the host or process is terminated without an opportunity to clean up, inspect the target and remove the stale lock before retrying.

## Install into an existing Maven project

Copy this `codecraft-starter` directory anywhere accessible, then run:

```shell
python3 codecraft-starter/bin/codecraft_starter.py install \
  --target /path/to/project \
  --project-name "My Project" \
  --verify-command "./mvnw verify"
```

The installer appends a managed CodeCraft block to an existing `AGENTS.md`, adds only missing ignore entries, and refuses conflicting distribution-managed files. It rejects symlinked destinations and rolls back repository-file writes after an installation error. Agreements, plans, configuration, review decisions, protected-asset state, and emoji response conventions become project-owned immediately.

Run the package and installed health checks:

```shell
python3 codecraft-starter/bin/codecraft_starter.py package-check
python3 codecraft-starter/bin/codecraft_starter.py doctor --target /path/to/project
cd /path/to/project
.codecraft/bin/codecraft_doctor.py
```

## Use with an AI

Start a fresh model in the target repository and say:

> Read AGENTS.md and use the project-local CodeCraft workflow. Assess the next planned behavior, but do not implement until the required human checkpoint.

The installed entrypoint routes the model to the working agreement, skill, project configuration, feature cycle, evolution guide, and completion lanes. The model should adapt the Java/Maven profile through an explicit reviewed automation slice when the existing build lacks the optional quality integrations.

For an active implementation increment, `.codecraft/bin/codecraft_run.py resume` provides its current stage, next action, pending attention, and narrow context paths. Run records are ignored operational state and never replace approval or committed evidence.

## Upgrade

Run the newer distribution against the target:

```shell
python3 codecraft-starter/bin/codecraft_starter.py upgrade --target /path/to/project
```

Managed files upgrade only when they still match the signed installation record. Project-owned files are never overwritten. Same-version content changes and downgrades are rejected. A locally changed managed file produces a conflict that must be reviewed and merged explicitly; managed removal requires a versioned migration, and there is deliberately no force flag.

## Evolve

Project-specific learning belongs in the project-owned agreement and `automation/` evidence. Reusable learning should be promoted into a new starter version with executable boundary tests. See the installed `.agents/skills/codecraft/references/evolution.md`.

## Release acceptance

Before publishing a starter version:

1. Run `python3 bin/codecraft_starter.py package-check`.
2. Run the clean-room test suite in `tests/`.
3. Validate the packaged skills.
4. Install into a disposable conventional Maven repository and run both doctors.
5. Perform the fresh-model exercise in `FORWARD-TEST.md`.
6. Exercise an upgrade with one project-owned edit and one managed-file conflict.
