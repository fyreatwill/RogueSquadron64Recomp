# NEXT work unit (s1857)

HYPOTHESIS-ID: generated-symbol-renaming-sweep

Resume the leftover census at `fake_func_800EFDDC` (`0x800EFDDC`,
size `0x4`). s1856 closed the 15-title M4 REVISIT (H-never-live on
VI 640 attribution LLE). Last-15 after s1856 include that revisit,
so this is not another REVISIT. Do not re-run the `0x8000` Y
census, re-watch `0x688:0x710`, or re-walk `L_17F0`.

Competing hypotheses:

- H1 already-named: companion `mission_overlay.txt`, generated
  headers/body/INL, and TOML already agree on `fake_func_800EFDDC`
  (or another single name) at `0x800EFDDC` size `0x4`. Confirm and
  advance the cursor.
- H2 rename: at least one of TOML / generated / companion still
  carries `func_800EFDDC` or a stale name; synchronize to the
  companion semantics.
- H3 leave leftover: the 4-byte span has no recoverable semantics;
  leave the placeholder and move on.

Exact commands:

```
# Companion, generated, TOML, and the 4-byte body at 0x800EFDDC.
# Neighbor leftover after this one is func_800EFDE0 (0x800EFDE0,
# 0x8DC; companion/generated updateNpcEventTimer; TOML leftover).
```

Expected splits:

- H1: all three sources already name the same symbol; no rename
  diff; cursor advances.
- H2: a real rename lands in TOML and/or generated fixup.
- H3: document why the span is unnameable; cursor advances.

Parked (not this iteration): hangar/512 check of live `0x8000` Y
(s1856 window was attribution 640 only).
