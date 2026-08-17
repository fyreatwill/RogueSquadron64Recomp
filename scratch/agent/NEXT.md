# NEXT work unit (s1856)

HYPOTHESIS-ID: m4-accumulator-boundary-revisit

Mandatory 15-title REVISIT. After s1855 the last-15 titles are
s1841–s1855, all sweep ("synchronized" / "confirmed the leftover …
symbol"). Do not resume the leftover census this iteration. Do not
re-watch `0x688:0x710`, recapture VMADH/VGE, watch `0x4B7800`,
re-walk the ovl20 consumer table, or re-map the 32-byte `0xD60`
stores. Do not repeat any `submitGfxFrame` entry/jal/`prev_pc`
recipe. Do not do another static walk of `L_17F0` command shape
(s1840 H-standard-edge closed that).

Parked M4 remainder (`docs/M4-ACCUMULATOR-GROUND-TRUTH.md`): whether
a live `0x8000` Y is clip-rejected at `L_17F0` entry, emitted as a
zero-height command, or emitted on-screen. Discriminator is a
phase-gated dump of a flushed `0xD60` command whose YL/YM/YH
halfwords are `0x8000`, plus same-run clip-reject counts.

Competing hypotheses:

- H-clip-reject: whenever a vertex `+0x1A` Y is `0x8000`, `+0x24` is
  `0x7070` (all-out → `L_1DA8`) or `0x4343` (partial → `L_1268`), so
  `L_17F0` never stores a `0xD60` command with YL/YM/YH = `0x8000`.
- H-zero-height-emit: at least one flushed `0xD60` Fill Triangle has
  YL = YM = YH = `0x8000` (zero-height; RDP no pixels).
- H-on-screen-emit: at least one flushed command has one or two of
  YL/YM/YH = `0x8000` and the three Ys are not equal (nonzero height
  after s11.2 decode).
- H-never-live: no `L_17F0` entry in the gated window sees
  `+0x1A == 0x8000` at all (the sentinel is producer-only / unused).

Exact commands (one build, one run; put new counters in
`tools/fixup_factor5_ucode.py`, not a hand-edit of
`build/factor5_ucode/*.c`):

```
# 1. Add ovl20 counters at:
#    - L_17F0 entry: if any of the three vertex +0x1A halfwords is
#      0x8000, classify +0x24 as all-out 0x7070 / partial 0x4343 /
#      fallthrough. n_y8000_entry is the positive control for "the
#      sentinel Y reached L_17F0".
#    - L_112C SP_WR_LEN flush from 0xD60: n_flush is the positive
#      control for "the instrument sees flushes". Walk 0xD60..(r16)
#      for 0xC8|flags headers; read YL/YM/YH at +2/+4/+6. Count
#      n_y8000_any / n_y8000_equal / n_y8000_mixed.
# 2. Rebuild Debug, run from build/ with the ROM present, phase-gate
#    after the first VI 640 (PROBE_PHASE_WIDTH / existing VI gate).
#    SIGKILL. Scope every counter to that phase.
```

Expected splits:

- H-clip-reject: `n_y8000_entry > 0` AND `n_y8000_any == 0` AND
  every `0x8000` entry took `L_1DA8` or `L_1268`.
- H-zero-height-emit: `n_y8000_equal > 0` and `n_y8000_mixed == 0`.
- H-on-screen-emit: `n_y8000_mixed > 0`.
- H-never-live: `n_flush > 0` (control) AND `n_y8000_entry == 0`.

A zero `n_flush` with no same-run control fire is unevaluable.

Sweep cursor parked (do not start this iteration): leftover
`fake_func_800EFDDC` (`0x800EFDDC`, `0x4`). Companion, generated
headers/body/INL, and TOML already that leftover. Next leftover
`func_800EFDE0` (`0x800EFDE0`, `0x8DC`; companion/generated
`updateNpcEventTimer`; TOML still leftover).
