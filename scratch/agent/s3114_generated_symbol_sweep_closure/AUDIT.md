# Session 3114 — generated-symbol sweep closure

## Discriminating check

The live project TOML was enumerated for every remaining `fake_func_*` entry,
then each entry was checked against the generated definition, companion map,
callers, header/registration, and regeneration rename surfaces.

Command:

```sh
awk '/fake_func_/ {print NR ":" $0}' syms/rogue_squadron.syms.toml
python3 tools/sweep_scan_candidates.py fake_func_800AE3E4
```

## Result

The TOML contains exactly two remaining placeholders:

| Entry | Existing disposition | Evidence |
|---|---|---|
| `fake_func_800AE3E4` | Preserve | Session 3100: instruction-only 12-byte fragment; no callable boundary or exact identity; final word overlaps menu entry `tickEasedCameraKeyframeBlend` at `0x800AE3EC`. |
| `fake_func_800B75C4` | Preserve | Session 3103: executable branch-target fragment inside `findLockOnTarget`; no standalone callable boundary or exact identity. |

The scanner stopped at `fake_func_800AE3E4` because its generated definition
is still a placeholder, after reporting zero auto-resolvable entries. No
remaining placeholder has an unperformed rename audit. The sweep is closed
without changing generated code or symbol names.

This selects H-ClosedInventory and rules out an unaudited generated-symbol
candidate in the current project map. It does not prove either preserved
fragment is unreachable at runtime.

ORIGIN: naming-only inventory closure; no runtime, route, audio, mitigation,
or generated instruction behavior changed.
