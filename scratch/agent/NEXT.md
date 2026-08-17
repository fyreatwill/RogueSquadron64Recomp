# NEXT work unit (s1858)

HYPOTHESIS-ID: generated-symbol-renaming-sweep

Resume the leftover census at `func_800EFDE0` (`0x800EFDE0`,
size `0x8DC`). s1857 confirmed leftover `fake_func_800EFDDC`
(`0x800EFDDC`, `0x4`, H1). Last-15 after s1857 still include
s1856's M4 REVISIT, so this is not another REVISIT. Do not
re-confirm `fake_func_800EFDDC`, re-run the `0x8000` Y census,
or re-walk `L_17F0`.

Competing hypotheses:

- H1 already-named: companion `mission_overlay.txt`, generated
  headers/body/INL, and TOML already agree on
  `updateNpcEventTimer` at `0x800EFDE0` size `0x8DC`. Confirm
  and advance the cursor.
- H2 rename: at least one of TOML / generated / companion still
  carries `func_800EFDE0` or a stale name; synchronize to the
  companion semantics.
- H3 leave leftover: the `0x8DC` span has no recoverable
  semantics; leave the placeholder and move on.

Exact commands:

```
# Companion, generated, TOML, and the 0x8DC body at 0x800EFDE0.
# Neighbor leftover after this one is func_800F06BC (0x800F06BC,
# 0xF0; companion/generated isPendingChildNpcActive; TOML leftover).
```

Expected splits:

- H1: all three sources already name the same symbol; no rename
  diff; cursor advances.
- H2: a real rename lands in TOML and/or generated fixup
  (peek: TOML is still `func_800EFDE0`; companion/generated
  already `updateNpcEventTimer`).
- H3: document why the span is unnameable; cursor advances.

Parked (not this iteration): hangar/512 check of live `0x8000` Y
(s1856 window was attribution 640 only).
