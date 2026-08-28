# Session 2922 generated-symbol reconciliation

Interval: `0x80064294..0x800642A0` (end exclusive)

| Address | Size | Generated body | Companion evidence | Callers/lookups | Decision |
|---|---:|---|---|---|---|
| `0x80064294` | `0xC` | `sh $v1,0x28($v0)`; `lw $v0,0x1C($fp)`; `addiu $v1,$zero,0x20`; no return | Immediately precedes complete `findLookupEntryByKey` at `0x800642A0`; companion map has no semantic name for the fragment | No generated call or lookup references beyond definition and overlay registration | Rename `fake_func_80064294` to `data_gap_80064294` |

The generated snapshot and regeneration-safe rename table were already
synchronized before this run, including existing diagnostic instrumentation.
The project and companion maps were stale and were reconciled. The old
placeholder has zero remaining hits in the reconciled maps or generated
snapshot.
