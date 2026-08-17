# NEXT work unit (s1860)

HYPOTHESIS-ID: generated-symbol-renaming-sweep

Resume the leftover census at `func_800F07AC` (`0x800F07AC`,
size `0x1FC`). s1859 synchronized leftover `func_800F06BC` to
`isPendingChildNpcActive` (`0x800F06BC`, `0xF0`, H2). Last-15
after s1859 still include s1856's M4 REVISIT, so this is not
another REVISIT. Do not re-confirm `isPendingChildNpcActive`,
re-run the `0x8000` Y census, or re-walk `L_17F0`.

Competing hypotheses:

- H1 already-named: companion `mission_overlay.txt`, generated
  headers/body/INL, and TOML already agree on
  `validateActorTargetLOS` at `0x800F07AC` size `0x1FC`. Confirm
  and advance the cursor.
- H2 rename: at least one of TOML / generated / companion still
  carries `func_800F07AC` or a stale name; synchronize to the
  companion semantics.
- H3 leave leftover: the `0x1FC` span has no recoverable
  semantics; leave the placeholder and move on.

Exact commands:

```
# Companion, generated, TOML, and the 0x1FC body at 0x800F07AC.
# Neighbor leftover after this one is func_800F09A8 (0x800F09A8,
# 0x1FC; companion/generated computeActorAnchorDeltaAfterLOS; TOML leftover).
```

Expected splits:

- H1: all three sources already name the same symbol; no rename
  diff; cursor advances.
- H2: a real rename lands in TOML and/or generated fixup
  (peek: TOML is still `func_800F07AC`; companion/generated
  already `validateActorTargetLOS`).
- H3: document why the span is unnameable; cursor advances.

Parked (not this iteration): hangar/512 check of live `0x8000` Y
(s1856 window was attribution 640 only).
