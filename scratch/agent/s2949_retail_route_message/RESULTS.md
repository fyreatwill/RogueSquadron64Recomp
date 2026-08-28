# s2949 retail route message/branch ground truth

The prescribed oracle command used `--pc-phase-log` and therefore sampled only
640-width phases. Its positive control still reached 10,000 whole-RDRAM writes
and the route PC watch fired 29,860 times, but it produced no requested target
phase rows. The corrected rerun used explicit width buckets
`1024:0x00790400` and `512:0x006AB400`; it completed with rc 0 and retained the
same positive-control threshold.

The field-enabled corrected run also completed with rc 0. Controls and target
coverage:

- whole-RDRAM watch: 10,000 writes
- `0x80019CD8` execution watch: 29,874 hits
- title target rows: 2,312
- hangar target rows: 6,558
- field table: 3 unique rows, 9,508 hits, zero overflow
- target field families: `source_word=0x02000612` (2,312),
  `0x00000400` (638), and `0x02000800` (6,558)
- all field rows: `branch_selector=0`, `branch_state=0x0010`
- execution callers: `0x80033300` (29,872), `0x8002BEEC` (2)

This selects H-RoutePreTitle for the port recipe: the retail route handler is
live in both target phases, while s2948's port route stopped at pre-title 640.
It rules out H-RouteAbsent and an oracle-instrument failure. It does not select
H-PrepareFieldBad, H-PrepareTimingBad, or H-PrepareLogicBad, because the port
has not produced a target-phase tuple. The field table is the independent
retail reference for the next port probe; `branch_state` is a sampled field,
not proof of the route's complete branch outcome.

Artifacts: `oracle.log`, `oracle-fixed.log`, `oracle-fields.log`, and their
corresponding `.rc` files.
