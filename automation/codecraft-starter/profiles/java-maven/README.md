# Java/Maven Profile

The installed core uses the target project's existing Maven verification command immediately. Optional CodeCraft quality integrations—Habit Hooks, PMD, JaCoCo visibility, coverage coaching, workflow self-tests, and structural review—must be reconciled with the target's existing POM rather than inserted blindly.

The installer places the reviewed reference fragment at `.codecraft/profiles/java-maven/pom-fragment.xml`. A model adapting a project must:

1. Inspect existing parent, module, plugin-management, JaCoCo, Surefire, PMD, and exec-plugin configuration.
2. Present the exact build changes and dependency versions for approval.
3. Begin from the project's green verification command.
4. Add integrations one at a time with focused configuration tests.
5. Keep coverage advisory unless the human separately approves a threshold.
6. Finish through the automation completion lane.

This boundary prevents an installer from rewriting a mature POM or duplicating plugins with incompatible lifecycle executions.
