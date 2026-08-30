# Session 3300 — type-1 19D34 leaves 0x8011A89C==1 for first yield

HYPOTHESIS-ID: m5-osvimode-viewer-frame-exit

## Competing hypotheses

- `H-Type1StartsSp`: the type-1 handler after last 19ED0
  idle-starts SP (or equivalent) and leaves `89C==1` for
  the next type-2.
- `H-IdleStartUncleared`: last 19DCC n=82's `0x80019DD4`
  store of 1 is still live; `0x80019FE4` does not run in
  the gap.
- `H-Other89CWriter`: some other PC writes 1 into
  `0x8011A89C` in the gap (not 19DD4 / not type-1).
- `H-BusyCoverageInvalid`: viewer `[m5-postwait]` entry,
  `[phase]` `640 @ 0x0066A500`, SENT n=3, last 19ED0, first
  19DC0, or the new 19DD4 / 19FE4 / type-1 probes are
  silent at width 640.

## What ran

Fixup probe at type-1 `0x80019CF0` taken / `L_80019D10` /
`0x80019D58` (`osSpTaskLoad`) / `L_80019D78` (busy skip) /
idle-start `0x80019DD4` / clearer `0x80019FE4`
(`tools/apply_s3300_sp_busy_writer.py`, also hooked from
`fixup_game_funcs.py`). Kept s3288 fade / s3289 SENT /
s3290 inner / s3293 gate / s3294 loop / s3295 dispatch /
s3299 type-2. Debug rebuild. One 30 s run from `build/`
with `ROGUESQ_LOG_M5_POSTWAIT=1`, SIGKILL.

Log: `scratch/agent/s3300_port_sp_busy_writer.log`.

No skip, allow, restore, wait bypass, or M5 Step 3.

## Same-run positive controls

- `[phase] vi_width=640 (was 320) origin=0x0066A500 at 3.0s`
- `[m5-postwait]` viewer `entry` `pc=0x800C28F0` `width=640 origin=0x66A500` `thr=3`
- `[s3288-fade] site=2D50 n=3 taken=0`
- `[s3289-stall] site=SENT n=3` with `SRET` max n=2
- `[s3290-stall]` `E0B4` n=41 without `R0B4` n=41 (max 40)
- last 19ED0 n=123 (`s2b0=0x02`) at width 640
- last 19DCC n=82 (`sp89c=0`) then first 19DC0 n=1 (`sp89c=1`)
- new probes live at width 640 (19DD4 n=81/82, 19FE4 n=121–123,
  19D10 n=41/42)

Failed instrument would have been a silent viewer entry,
no 640 phase, missing `2D50` n=3, `SRET` n=3, silent last
19ED0, silent first 19DC0, or silent new probes at width
640. Zero crash/abort/Bus-error/last-guest-pc.

## Lifetime (last printed `n`)

| site | last n | notes |
|---|---:|---|
| 19CF0T | 42 | 1:1 with 19D10 |
| 19D10 | 42 | every visit `s4_0=0` `s4_4=0` `sp89c=0` |
| 19D58 | 42 | every visit `a0=0x800377C8` (`gspTask`); `s4_0=1` `sp89c=1` |
| 19D78 | 0 | type-1 never busy-skips |
| 19DD4 | 82 | 1:1 with 19DCC; last is before last 19ED0 |
| 19FE4 | 123 | 1:1 with 19ED0; last is after last 19ED0, before type-1 |

After first 19DC0: 19DD4=0, 19FE4=0, 19D10=0.

`$s4` is initialized `lui 0x8012; addiu -0x5764` =
`0x8011A89C`; `$s3 = $s4+4` = `0x8011A8A0`. Type-1
`0x80019D34` `sb $s1, 0($s4)` is therefore the 89C=1 store.

## Join around last 19ED0 n=123 / first 19DC0 n=1

| line | site | n | notes |
|---:|---|---:|---|
| 844-845 | 19D90/19DCC | 82 | last idle type-2; `sp89c=0` |
| 846 | 19DD4 | 82 | stores 1; `sp89c=0` before store |
| 855 | 19ED0 | 123 | last gate; `s2b0=0x02` |
| 858 | 19FE4 | 123 | **clears 89C**; `sp89c=1` before store |
| 879 | 19CDC | 247 | type `0x01` `a0=0x80128CE0` |
| 880-881 | 19CF0T/19D10 | 42 | `sp89c=0` (clearer held) |
| 882 | 19D58 | 42 | `a0=0x800377C8`; `s4_0=1` `sp89c=1` |
| 887-889 | 19D90/19DAC/19DC0 | 83/1/1 | `sp89c=1`; store `0x80149470` |
| 901 | SENT | 3 | submitGfxFrame blocked after this |

## Classification

- `H-BusyCoverageInvalid` is refuted: viewer, 640 /
  `0x0066A500`, `2D50` n=3, SENT n=3 without SRET n=3,
  E0B4 n=41 without R0B4, last 19ED0, first 19DC0, and
  live new probes at width 640 all fired. 19D10 n=42
  `sp89c=0` after 19FE4 n=123 is a same-run positive
  control that the clearer prints.
- `H-IdleStartUncleared` is refuted: 19FE4 n=123 runs
  after last 19DD4 n=82 and before type-1; 19D10 still
  sees `sp89c=0`.
- `H-Other89CWriter` is refuted: 89C becomes 1 inside
  the type-1 start path (`19D10` `sp89c=0` → `19D58`
  `sp89c=1`) with no 19DD4. The store is type-1's own
  `0x80019D34` `sb $s1, 0($s4)` (`$s4=0x8011A89C`).
- Selected `H-Type1StartsSp`: after last 19ED0, type-1
  `19CDC n=247` (`$a0=0x80128CE0`) takes 19D10, starts
  `gspTask` `0x800377C8` at 19D58, and leaves `89C==1`
  for the next type-2. Combined with s3298, retail
  type-2 never sees this busy byte. Combined with
  s3293–s3295, 19FE4 never runs again because 19ED0
  is abandoned, so the byte stays 1.

Single-source port census plus the scheduler's `$s4`
init (two-source for "19D34 writes 89C"). No audio or
M5 Step 3 change.

Next discriminator: does retail type-1 at the attract
viewer start `gspTask` / write 89C, and if so who
clears it before type-2?
