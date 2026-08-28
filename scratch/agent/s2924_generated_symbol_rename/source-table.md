# Session 2924 generated-symbol reconciliation

Interval: `0x80065A5C..0x80065A60` (end exclusive)

| Address | Size | Generated body | Companion evidence | Callers/lookups | Decision |
|---|---:|---|---|---|---|
| `0x80065A5C` | `0x4` | `addu $v1,$v1,$v0`; no return or standalone prologue | Immediately precedes complete `buildPositionAndCallTransformHelper` at `0x80065A60`; companion map had only `fake_func_80065A5C` and no semantic source-backed name | No generated call or lookup references beyond definition and overlay registration | Rename `fake_func_80065A5C` to `data_gap_80065A5C` |

The generated snapshot and regeneration-safe rename table already used
`data_gap_80065A5C`; this run synchronized the stale project and companion
maps. The old placeholder has no remaining hits in the reconciled maps or
generated snapshot.
