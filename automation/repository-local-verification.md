# Repository-Local Verification

Date: 2026/10/01

Automation: CodeCraft 0.7.1

## Intent

Make the documented verification commands self-contained, deterministic, and usable when the agent cannot write to a home-directory cache. Align the expected-red runner's actual file mode with its documented direct invocation, and evaluate Python-specific Habit Hooks coaching without silently expanding the quality architecture.

## Approved Behaviors

| Element Number | Behavior | Arrange | Act | Assert |
|---:|---|---|---|---|
| 1 | Make verification cache repository-local | The home uv cache is unavailable | Run bare `./mvnw verify` | Every gate succeeds without an environment prefix |
| 2 | Keep verification deterministic | Locked dependencies and a warm local cache | Run verification with uv offline | Workflow checks remain reproducible |
| 3 | Align expected-red runner invocation | The project-local runner and documented workflow | Invoke the documented command | Executable permissions and documentation agree |
| 4 | Validate project skills locally | The repository-managed Python environment | Run the skill validator | Validation succeeds without ad hoc package installation |
| 5 | Evaluate Python Habit Hooks coaching | Python workflow automation exists | Run the canonical quality gate | Python coaching is integrated or explicitly rejected with rationale |

## Test-First Evidence

The environment suite began with four failures: no project cache setting, no ignored cache path, no locked PyYAML dependency, no Python coaching integration, and a non-executable expected-red runner. The accepted design made the first four repository invariants executable tests. Python coaching was evaluated through a real plugin run and resolved as an explicit design decision rather than a permanent configuration assertion.

The focused suite now has three passing tests covering cache locality, skill-validator dependency, and runner executability. The complete workflow suite has 45 passing tests.

## Implementation

- `pyproject.toml` sets `[tool.uv].cache-dir = ".uv-cache"`, and `.gitignore` excludes that disposable repository-local cache.
- `pyyaml==6.0.3` is a direct locked project dependency, so the project-local skill validator runs through ordinary `uv run --frozen`.
- `.codecraft/bin/run_bdd_red.py` is tracked executable, matching every direct invocation in the CodeCraft workflow.
- Existing Maven uv executions retain `--frozen`, and a warm-cache verification passes with `UV_OFFLINE=true`.
- CodeCraft 0.7.1 documents bootstrap, normal, offline, validator, and expected-red commands.

The cache configuration follows uv's documented `tool.uv.cache-dir` setting and keeps the cache on the same filesystem as the project environment: <https://docs.astral.sh/uv/concepts/cache/>.

## Python Coaching Decision

The `habit-hooks[python]` extra and Python plugin were installed and run as an evaluation. That run required undeclared `ruff` and `deptry` detector tools and surfaced five oversized-file design suggestions across the protection policy, its tests, and imported skill-creator scripts.

Enabling the plugin responsibly therefore requires a separate responsibility-driven batch: decide the authored-Python scope, add and lock both detector toolchains, split the protection policy along cohesive jobs, and separate shared test fixtures without weakening protected assets. Folding that refactor into a cache portability patch would violate the approved slice and obscure its design. CodeCraft 0.7.1 keeps the established Java/generic gate and records Python coaching as a proposed follow-on rather than pretending the incomplete plugin run was clean.

## Verification

- Bare canonical build: `./mvnw verify` succeeded
- Warm-cache offline build: `UV_OFFLINE=true ./mvnw verify` succeeded
- Java suite: 95 passing tests
- Workflow suite: 45 passing tests
- Focused verification-environment suite: 3 passing tests
- Project-local skill validator: valid through locked uv environment
- Java structure review: current at 51 completed and reviewed behaviors
- Habit Hooks: all established Java/generic enforced checks passing; Python-plugin suggestion evaluated as described above

## Decisions and Challenges

- A repository-local cache is disposable and ignored; `uv.lock`, not the cache, is the reproducibility contract.
- `--offline` is an acceptance check for a warm cache, not the default first-run behavior. An empty cache still needs one locked bootstrap download.
- The runner's shebang already selected Python correctly; only its Git executable bit was inconsistent.
- The system Python is older than the project's declared Python requirement, so automation tests and skill validation intentionally use the locked uv environment.
