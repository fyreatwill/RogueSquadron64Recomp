# NEXT work unit (s1865)

HYPOTHESIS-ID: generated-symbol-renaming-sweep

Resume the leftover census at `func_800F1198` (`0x800F1198`,
size `0x178`). s1864 synchronized leftover `func_800F0F94` to
`resolveNpcAttachmentPos` (`0x800F0F94`, `0x204`, H2). Last-15
after s1864 still include s1856's M4 REVISIT, so this is not
another REVISIT. Do not re-confirm `resolveNpcAttachmentPos`,
re-run the `0x8000` Y census, or re-walk `L_17F0`.

Competing hypotheses:

- H1 already-named: companion `mission_overlay.txt`, generated
  headers/body/INL, and TOML already agree on
  `quicksortFloatKeysWithValues` at `0x800F1198` size `0x178`.
  Confirm and advance the cursor.
- H2 rename: at least one of TOML / generated / companion still
  carries `func_800F1198` or a stale name; synchronize to the
  companion semantics.
- H3 leave leftover: the `0x178` span has no recoverable
  semantics; leave the placeholder and move on.

Exact commands:

```
# Companion, generated, TOML, and the 0x178 body at 0x800F1198.
# Neighbor leftover after this one is func_800F1310 (0x800F1310,
# 0x2A8; companion/generated gatherAndSortNearbyNpcViewPoints; TOML leftover).
```

Expected splits:

- H1: all three sources already name the same symbol; no rename
  diff; cursor advances.
- H2: a real rename lands in TOML and/or generated fixup
  (peek: TOML is still `func_800F1198`; companion/generated
  already `quicksortFloatKeysWithValues`).
- H3: document why the span is unnameable; cursor advances.

Parked (not this iteration): hangar/512 check of live `0x8000` Y
(s1856 window was attribution 640 only).
