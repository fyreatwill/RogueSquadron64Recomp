# NEXT work unit (s1867)

HYPOTHESIS-ID: generated-symbol-renaming-sweep

Resume the leftover census at `func_800F15B8` (`0x800F15B8`,
size `0x2B8`). s1866 synchronized leftover `func_800F1310` to
`gatherAndSortNearbyNpcViewPoints` (`0x800F1310`, `0x2A8`, H2). Last-15
after s1866 still include s1856's M4 REVISIT, so this is not
another REVISIT. Do not re-confirm `gatherAndSortNearbyNpcViewPoints`,
re-run the `0x8000` Y census, or re-walk `L_17F0`.

Competing hypotheses:

- H1 already-named: companion `mission_overlay.txt`, generated
  headers/body/INL, and TOML already agree on
  `acquireNpcTargetsInAimCone` at `0x800F15B8` size `0x2B8`.
  Confirm and advance the cursor.
- H2 rename: at least one of TOML / generated / companion still
  carries `func_800F15B8` or a stale name; synchronize to the
  companion sequential listing.
- H3 leave leftover: the `0x2B8` span has no recoverable
  semantics; leave the placeholder and move on.

Exact commands:

```
# Companion, generated, TOML, and the 0x2B8 body at 0x800F15B8.
# Neighbor leftover after this one is func_800F1870 (0x800F1870,
# 0x2D0; companion/generated tickProgressChannel; TOML leftover).
# 2 generated jal 0x800F15B8 sites: funcs_37.c already
# acquireNpcTargetsInAimCone; funcs_13.c still LOOKUP_FUNC(0x800F15B8).
# First insn addiu $sp, $sp, -0xE8; last jr $ra / addiu $sp, $sp, 0xE8
# at 0x800F1868 / 0x800F186C.
```

Expected splits:

- H1: all three sources already name the same symbol; no rename
  diff; cursor advances.
- H2: a real rename lands in TOML and/or generated fixup
  (peek: TOML is still `func_800F15B8`; companion/generated
  already `acquireNpcTargetsInAimCone`).
- H3: document why the span is unnameable; cursor advances.

Parked (not this iteration): hangar/512 check of live `0x8000` Y
(s1856 window was attribution 640 only).
