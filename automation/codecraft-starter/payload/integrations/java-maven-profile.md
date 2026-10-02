# Java/Maven Adapter

The CodeCraft core is active through the configured Maven verification command. Before adding optional quality integrations, read the distribution's Java/Maven profile guidance and inspect the existing build.

The supplied reference fragment enables a JaCoCo report without a coverage gate. The following source-workflow patterns can be ported as separately reviewed adapter increments when the target needs them:

- line, branch, and cyclomatic-complexity summaries
- changed-code-first coverage coaching
- Habit Hooks with PMD-backed Java sensors
- workflow automation self-tests
- package-structure coaching

Do not merge the reference POM fragment mechanically. Reconcile it with existing plugin management, modules, lifecycle phases, Java version, and CI through an approved automation slice.
