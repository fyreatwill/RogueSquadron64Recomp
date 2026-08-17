# NEXT work unit (s1862)

HYPOTHESIS-ID: generated-symbol-renaming-sweep

Resume the leftover census at `func_800F0BA4` (`0x800F0BA4`,
size `0x220`). s1861 synchronized leftover `func_800F09A8` to
`computeActorAnchorDeltaAfterLOS` (`0x800F09A8`, `0x1FC`, H2). Last-15
after s1861 still include s1856's M4 REVISIT, so this is not
another REVISIT. Do not re-confirm `computeActorAnchorDeltaAfterLOS`,
re-run the `0x8000` Y census, or re-walk `L_17F0`.

Competing hypotheses:

- H1 already-named: companion `mission_overlay.txt`, generated
  headers/body/INL, and TOML already agree on
  `evaluateTargetTrackingVisibility` at `0x800F0BA4` size `0x220`.
  Confirm and advance the cursor.
- H2 rename: at least one of TOML / generated / companion still
  carries `func_800F0BA4` or a stale name; synchronize to the
  companion semantics.
- H3 leave leftover: the `0x220` span has no recoverable
  semantics; leave the placeholder and move on.

Exact commands:

```
# Companion, generated, TOML, and the 0x220 body at 0x800F0BA4.
# Neighbor leftover after this one is func_800F0DC4 (0x800F0DC4,
# 0x1D0; companion/generated tickObjectAnimSubstruct; TOML leftover).
```

Expected splits:

- H1: all three sources already name the same symbol; no rename
  diff; cursor advances.
- H2: a real rename lands in TOML and/or generated fixup
  (peek: TOML is still `func_800F0BA4`; companion/generated
  already `evaluateTargetTrackingVisibility`).
- H3: document why the span is unnameable; cursor advances.

Parked (not this iteration): hangar/512 check of live `0x8000` Y
(s1856 window was attribution 640 only).
