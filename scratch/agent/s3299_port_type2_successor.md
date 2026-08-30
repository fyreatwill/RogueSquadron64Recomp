# Session 3299 — port type-2 yields after last 19ED0; 19DC0 stores 0x80149470

HYPOTHESIS-ID: m5-osvimode-viewer-frame-exit

## Competing hypotheses

- `H-PortType2Idle`: during the viewer and around last
  19ED0, 19D90 is live and 19DCC is live; 19DAC / 19DC0
  stay 0. Same successor as retail; extra yieldw has a
  different publisher.
- `H-PortType2Yields`: 19DC0 executes (especially in the
  gap after last 19ED0 n=123) and stores `0x80149470`.
- `H-PortType2BusySkip`: 19D90 is live but 19D94 skips
  (`0x8011A8A0` already set); neither 19DCC nor 19DC0.
- `H-PortCoverageInvalid`: viewer `[m5-postwait]` entry,
  `[phase]` `640 @ 0x0066A500`, SENT n=3, last 19ED0, or
  19CDC type-`0x02` miss, or the new probes are silent at
  width 640.

## What ran

Fixup probe at `L_80019D90`, `0x80019D94` skip, `0x80019DAC`,
`0x80019DC0`, and `L_80019DCC`
(`tools/apply_s3299_type2_successor.py`, also hooked from
`fixup_game_funcs.py`). Kept s3288 fade / s3289 SENT /
s3290 inner / s3293 gate / s3294 loop / s3295 dispatch.
Debug rebuild. One 30 s run from `build/` with
`ROGUESQ_LOG_M5_POSTWAIT=1`, SIGKILL.

Log: `scratch/agent/s3299_port_type2_successor.log`.

No skip, allow, restore, wait bypass, or M5 Step 3.

## Same-run positive controls

- `[phase] vi_width=640 (was 320) origin=0x0066A500 at 4.6s`
- `[m5-postwait]` viewer `entry` `pc=0x800C28F0` `width=640 origin=0x66A500` `thr=3`
- `[s3288-fade] site=2D50 n=3 taken=0`
- `[s3289-stall] site=SENT n=3` with `SRET` max n=2
- `[s3290-stall]` `E0B4` n=41 without `R0B4` n=41 (max 40)
- `[s3293-sched] site=19F1C n=41` at width 640, `a0=0x8011A818`
- last 19ED0 n=123 (`s2b0=0x02`) at width 640
- new `[s3299-t2]` 19D90/19DCC live at width 640 before last
  19ED0 (19D90 n=80..82, 19DCC n=80..82, `sp89c=0`)

Failed instrument would have been a silent viewer entry,
no 640 phase, missing `2D50` n=3, `SRET` n=3, silent last
19ED0, silent type-`0x02`, or silent new probes at width
640. Zero crash/abort/Bus-error/last-guest-pc.

## Lifetime (last printed `n`)

| site | last n | notes |
|---|---:|---|
| 19D90 | 1246 | every visit `a0=0x80128C80` `v0=0` (`0x8011A8A0` clear) |
| 19D94S | 0 | busy-skip never taken |
| 19DCC | 82 | all `sp89c=0`; last is before last 19ED0 |
| 19DAC | 1164 | all `sp89c=0x01`; first is after last 19ED0 |
| 19DC0 | 1164 | every store `v0=yieldw=0x80149470` |

1246 = 82 + 1164. 1:1 with no leftover 19D90.

## Join around last 19ED0 n=123 / SENT n=3

| line | site | n | notes |
|---:|---|---:|---|
| 809-810 | 19D90/19DCC | 82 | `sp89c=0` `yieldw=0`; last idle type-2 |
| 816-818 | 19DFC/19E7C/19E80T | 123 | `type=0x81` `yieldw=0` `s2b0=0x02` |
| 819 | 19ED0 | 123 | last gate |
| 838 | 19CDC | 247 | **type `0x01`** `a0=0x80128CE0` `yieldw=0` |
| 844-847 | 19CDC/19D90/19DAC/19DC0 | 248/83/1/1 | type `0x02`; `sp89c=1`; store `0x80149470` |
| 859 | SENT | 3 | submitGfxFrame blocked after this |
| 865 | 19DFC | 124 | first `yieldw=0x80149470` (matches s3295) |

After last 19ED0: 19DCC = 0, 19D90 = 19DAC = 19DC0 = 1164,
all `a0=0x80128C80`. Width-640 19CDC type-`0x02` after last
19ED0 is 1164 (1:1 with 19DC0).

## Classification

- `H-PortCoverageInvalid` is refuted: viewer, 640 /
  `0x0066A500`, `2D50` n=3, SENT n=3 without SRET n=3,
  E0B4 n=41 without R0B4, last 19ED0 n=123, live type-`0x02`,
  and live new probes at width 640 all fired. 19D90 n=82
  → 19DCC n=82 is a same-run positive control that the idle
  arm prints.
- `H-PortType2BusySkip` is refuted: 19D94S = 0; every 19D90
  has `v0=0`.
- `H-PortType2Idle` is refuted for the post-last-19ED0
  window: 19DC0 n=1 starts on the first type-2 after last
  19ED0 (`sp89c=1`) and every later type-2 also yields.
  Pre-last-19ED0 type-2 is idle (82/82), matching retail's
  successor in that earlier window only.
- Selected `H-PortType2Yields`: the extra `yieldw=0x80149470`
  publisher is `0x80019DC0` on type-2 while
  `0x8011A89C==1`. Combined with s3298, retail type-2 never
  takes this arm because SP is idle.

Single-source port census, compared with s3298 retail
(two-source for "port type-2 yield-publishes; retail type-2
idle-starts"). No audio or M5 Step 3 change.

Next discriminator: in the gap after last 19ED0, type-1
`19CDC n=247` (`$a0=0x80128CE0`) arrives, then type-2 sees
`0x8011A89C==1`. Who writes that busy byte (idle-start
`0x80019DD4` vs clearer `0x80019FE4` vs the type-1 handler)?
