# NEXT work unit (s1868)

HYPOTHESIS-ID: generated-symbol-renaming-sweep

Resume the leftover census at `func_800F1870` (`0x800F1870`,
size `0x2D0`). s1867 synchronized leftover `func_800F15B8` to
`acquireNpcTargetsInAimCone` (`0x800F15B8`, `0x2B8`, H2). Last-15
after s1867 still include s1856's M4 REVISIT, so this is not
another REVISIT. Do not re-confirm `acquireNpcTargetsInAimCone`,
re-run the `0x8000` Y census, or re-walk `L_17F0`.

Competing hypotheses:

- H1 already-named: companion `mission_overlay.txt`, generated
  headers/body/INL, and TOML already agree on
  `tickProgressChannel` at `0x800F1870` size `0x2D0`.
  Confirm and advance the cursor.
- H2 rename: at least one of TOML / generated / companion still
  carries `func_800F1870` or a stale name; synchronize to the
  companion sequential listing.
- H3 leave leftover: the `0x2D0` span has no recoverable
  semantics; leave the placeholder and move on.

Exact commands:

```
# Companion, generated, TOML, and the 0x2D0 body at 0x800F1870.
# Neighbor leftover after this one is func_800F1B40 (0x800F1B40,
# 0x33C; companion/generated raycastTerrainAndNpcs; TOML leftover).
# 45 generated jal 0x800F1870 sites (funcs_36.c 14, funcs_37.c 5,
# funcs_38.c 10, funcs_39.c 15, funcs_41.c 1) already
# tickProgressChannel; no LOOKUP_FUNC(0x800F1870).
# First insn addiu $sp, $sp, -0x90; last jr $ra / addiu $sp, $sp, 0x90
# at 0x800F1B38 / 0x800F1B3C.
```

Expected splits:

- H1: all three sources already name the same symbol; no rename
  diff; cursor advances.
- H2: a real rename lands in TOML and/or generated fixup
  (peek: TOML is still `func_800F1870`; companion/generated
  already `tickProgressChannel`).
- H3: document why the span is unnameable; cursor advances.

Parked (not this iteration): hangar/512 check of live `0x8000` Y
(s1856 window was attribution 640 only).
