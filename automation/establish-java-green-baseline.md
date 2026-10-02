# Establish Java Green Baseline

Date: 2026/09/29

## Intent

Establish a repeatable Java 25 workflow that protects human-approved behavior, runs from one root command, provides actionable structural coaching, and demonstrates the outside-in test-first cycle with the smallest RPG Combat behavior.

## Approach

- Made the root Maven project an aggregator for the active Java module.
- Generated a Maven 3.9.15 Wrapper and enforced Java 25 and Maven 3.9.12 or newer.
- Added GitHub Actions verification for pushes, pull requests, and manual runs.
- Added project-local CodeCraft instructions, a reusable Java workflow skill, and a technical BDD protection hook.
- Added exact-change, single-use approval for protected assets, including `y` as a short human confirmation.
- Pinned Habit Hooks 1.5.0 with uv and connected its Java PMD sensor to the Maven lifecycle.
- Replaced the unstable identity-based starter ApprovalTest with focused JUnit tests.
- Created and protected the approved `CharacterCreation_bdd.java` characterization test.
- Implemented only the initial health and alive state needed by the approved behavior.

## Test-First Sequence

1. Protection tests failed because the protection hook did not exist.
2. The protection implementation made all seven initial hook tests pass.
3. A new hook test failed because `y` was not accepted as confirmation.
4. Adding `y` made all eight hook tests pass.
5. The approved BDD failed to compile because `health()` and `isAlive()` did not exist.
6. Focused character tests failed for the same missing public behavior.
7. The minimum `PlayerCharacter` implementation made focused tests and the BDD pass.
8. The complete verification passed with Habit Hooks enabled.

## Commands

```text
python3 -m unittest discover -s .codecraft/tests -p 'test_*.py'
./mvnw --batch-mode --no-transfer-progress -pl java -Dtest=CharacterCreation_bdd test
./mvnw --batch-mode --no-transfer-progress -pl java -Dtest=PlayerCharacterTest test
./mvnw --batch-mode --no-transfer-progress verify
```

## Result

- Java tests: 3 passing
- Protected BDD tests: 1 passing
- Protection tests: 8 passing
- Habit Hooks: passing
- Root Maven verification: passing
- Canonical command: `./mvnw verify`

## Decisions

- JUnit assertions describe initial health and life state more precisely than a snapshot and do not protect incidental text formatting.
- `isAlive()` derives life from health instead of storing duplicate mutable state.
- PMD is resolved as pinned Maven dependencies and exposed through a project-local launcher, so no global PMD installation is required.
- Habit Hooks configuration, PMD rules, hook code, and agent workflow instructions live in the repository.
- Existing unrelated staged changes remain outside this task's commit scope.

## Challenges

- The original ApprovalTest compared default object identity text, making its approved output unstable.
- The ordinary local Java command selected Java 21 even though Java 25 was installed. The wrapper now discovers the installed Homebrew Java 25 when `JAVA_HOME` is absent.
- Maven and uv caches require explicit sandbox approval on first dependency resolution.
- PMD's distribution archive was unavailable from Maven Central. The supported CLI and Java artifacts were used instead.
- Codex project hooks load at session startup and require trust for their exact configuration. The protection policy is unit-tested and will become active when the project session reloads.

## Sources

- [Apache Maven plugins](https://maven.apache.org/plugins/)
- [Maven Enforcer version rules](https://maven.apache.org/enforcer/enforcer-rules/versionRanges.html)
- [Habit Hooks](https://github.com/habit-hooks/habit-hooks)
- [GitHub setup-java](https://github.com/actions/setup-java)
