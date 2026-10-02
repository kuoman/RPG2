# Active Run State

Use `.codecraft/bin/codecraft_run.py` as durable operational memory for one coherent increment or one BDD batch entry. State lives under the ignored `.codecraft/state/runs/` directory and remains separate from authorization and committed evidence.

Run `resume` before rediscovering task state and use `resume --json` when a deterministic process needs the complete structured record. Use `start` to create a scoped run; `advance` to move through `design`, optional `outside-red`, `implementation`, `review`, `verification`, and `commit`; `checkpoint` for deterministic facts; and `attention-add` or `attention-resolve` for explicit judgment boundaries. Run `finish` only after the coherent commit exists.

Use `--help` on each command for its exact machine contract. Never edit run JSON directly. Pending attention blocks stage advancement, and the run record never grants protected-change approval or replaces Git, approved manifests, signed receipts, or durable feature evidence.
