# NEXT work unit (s1866)

HYPOTHESIS-ID: generated-symbol-renaming-sweep

Resume the leftover census at `func_800F1310` (`0x800F1310`,
size `0x2A8`). s1865 synchronized leftover `func_800F1198` to
`quicksortFloatKeysWithValues` (`0x800F1198`, `0x178`, H2). Last-15
after s1865 still include s1856's M4 REVISIT, so this is not
another REVISIT. Do not re-confirm `quicksortFloatKeysWithValues`,
re-run the `0x8000` Y census, or re-walk `L_17F0`.

Competing hypotheses:

- H1 already-named: companion `mission_overlay.txt`, generated
  headers/body/INL, and TOML already agree on
  `gatherAndSortNearbyNpcViewPoints` at `0x800F1310` size `0x2A8`.
  Confirm and advance the cursor.
- H2 rename: at least one of TOML / generated / companion still
  carries `func_800F1310` or a stale name; synchronize to the
  companion sequential listing.
- H3 leave leftover: the `0x2A8` span has no recoverable
  semantics; leave the placeholder and move on.

Exact commands:

```
# Companion, generated, TOML, and the 0x2A8 body at 0x800F1310.
# Neighbor leftover after this one is func_800F15B8 (0x800F15B8,
# 0x2B8; companion/generated acquireNpcTargetsInAimCone; TOML leftover).
# The tickProgressChannel comment still calls func_800F1310 a
# "heavy actor-state updater"; trust the sequential listing and
# the generated body, not that stale comment.
```

Expected splits:

- H1: all three sources already name the same symbol; no rename
  diff; cursor advances.
- H2: a real rename lands in TOML and/or generated fixup
  (peek: TOML is still `func_800F1310`; companion/generated
  already `gatherAndSortNearbyNpcViewPoints`).
- H3: document why the span is unnameable; cursor advances.

Parked (not this iteration): hangar/512 check of live `0x8000` Y
(s1856 window was attribution 640 only).
