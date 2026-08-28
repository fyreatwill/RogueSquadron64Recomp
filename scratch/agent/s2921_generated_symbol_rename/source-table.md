# Session 2921 generated-symbol reconciliation

Interval: `0x800613B8..0x800613C0` (end exclusive)

| Address | Size | Generated body | Companion evidence | Callers/lookups | Decision |
|---|---:|---|---|---|---|
| `0x800613B8` | `0x8` | `lwc1 $f2,0x60($fp)`; `c.lt.s $f2,$f0` | Immediately precedes complete `loadCharTextureSet` at `0x800613C0`; adjacent body and preamble mapping are source-backed | No generated call or lookup references beyond definition and overlay registration | Rename `fake_func_800613B8` to `loadCharTextureSetPreamble` |

The generated snapshot was already synchronized before this run, so the
bounded rename tool changed no generated references. The companion map and
project symbol map were reconciled to the existing regeneration-safe mapping.
