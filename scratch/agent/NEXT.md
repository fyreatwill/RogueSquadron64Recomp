# NEXT work unit (s1869)

HYPOTHESIS-ID: generated-symbol-renaming-sweep

Resume the leftover census at `func_800F1B40` (`0x800F1B40`,
size `0x33C`). s1868 synchronized leftover `func_800F1870` to
`tickProgressChannel` (`0x800F1870`, `0x2D0`, H2). Last-15
after s1868 still include s1856's M4 REVISIT, so this is not
another REVISIT. Do not re-confirm `tickProgressChannel` or
re-run the `0x8000` Y census.

Competing hypotheses:

- H1 already-named: companion `mission_overlay.txt`, generated
  headers/body/INL, and TOML already agree on
  `raycastTerrainAndNpcs` at `0x800F1B40` size `0x33C`.
  Confirm and advance the cursor.
- H2 rename: at least one of TOML / generated / companion still
  carries `func_800F1B40` or a stale name; synchronize to the
  companion sequential listing.
- H3 leave leftover: the `0x33C` span has no recoverable
  semantics; leave the placeholder and move on.

Exact commands:

```
# Companion, generated, TOML, and the 0x33C body at 0x800F1B40.
# Neighbor leftover after this one is func_800F1E7C (0x800F1E7C,
# 0x178; companion/generated initActorRenderDescriptorIfUninit;
# TOML leftover).
# 11 generated jal 0x800F1B40 sites (funcs_41.c only) already
# raycastTerrainAndNpcs; no LOOKUP_FUNC(0x800F1B40).
# First insn addiu $sp, $sp, -0x90; last jr $ra / addiu $sp, $sp, 0x90
# at 0x800F1E74 / 0x800F1E78.
```

Expected splits:

- H1: all three sources already name the same symbol; no rename
  diff; cursor advances.
- H2: a real rename lands in TOML and/or generated fixup
  (peek: TOML is still `func_800F1B40`; companion/generated
  already `raycastTerrainAndNpcs`).
- H3: document why the span is unnameable; cursor advances.

Parked (not this iteration): hangar/512 check of live `0x8000` Y
(s1856 window was attribution 640 only).
