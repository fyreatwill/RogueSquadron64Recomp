# Session 3311 — port jal cinematicInitializer skipped by 0x800A6274 ($a0=0)

HYPOTHESIS-ID: m5-osvimode-postviewer-continuation

## Competing hypotheses

- `H-JalUnreached`: `0x800A6260` region never executes (loop body
  takes an earlier skip of this block).
- `H-TimePredSkip`: `0x800A626C` is always taken (`sltu` false;
  count >= limit-10); 6274/62B4 stay silent.
- `H-FlagByteSkip`: `0x800A6274` is always taken (`$a0` byte 0);
  62B4 stays silent.
- `H-JalFires`: `0x800A62B4` does fire (store/overlay dispatch,
  not the skip, is the mismatch).

`isCinematicActive` `0x800A6288` is a same-run control, not a
lead: s3308's null word says it should not skip.

## What ran

One regeneration-safe table covering time-pred `0x800A626C`,
flag-byte `0x800A6274`, already-active `0x800A6288`, and
init-jal `0x800A62B4`. Live apply:
`tools/apply_s3311_cine_init_jal.py` into `funcs_27.c`. The same
transform is imported by `N64Recomp/fixup_game_funcs.py`.
Diagnostic only: no guest store/branch change, no M5 Step 3.
s3306/s3308 tables kept.

One 122 s watchdog launch from `build/` (no VI-320 crash, no
retry). Driver: `scratch/agent/s3311_cine_init_jal/run.sh`.
No `--press`.

## Same-run positive controls (122 s)

- `[s3311-cine-init-jal-control] mark` IDs 0–3 (4/4).
- `[s3308-stage-adv-control] mark` IDs 0–5 (6/6).
- `[s3306-cine-loop-control] mark` IDs 0–6 (7/7).
- `[s3305-postviewer-control] mark` IDs 0–23 (24/24).
- `arm=completion-wins-default` 87; `requested_pre=1 requested_post=0` 87.
- `[event-wiring] complete kind=SP` 64.
- `[phase] vi_width=640 (was 320) origin=0x0066A500` at 4.8 s `#209`.
- Viewer `[m5-postwait]` entry and return.
- s3305 cinematic-entry (`$a0=0x13`); s3306 loop-head and exit-gate.
- Zero `[CRASH]` / `[ABORT]`. No title 1024.

## Port cinematicLoopBody initializer-jal (live)

| n | site | `$v0`/`$v1`/`$a0` | taken | notes |
|---|---|---|---|---|
| 1–100 printed | time-pred `0x800A626C` | `$v1=1` `$a0=0` | **0** | count 0→`0x69`, limit=`0x4A6` (1190) |
| 1–139 | flag-byte `0x800A6274` | `$v0=0` `$a0=0` | **1** | all 139 skip to `L_800A62EC` |
| 0 | already-active `0x800A6288` | — | — | silent |
| 0 | init-jal `0x800A62B4` | — | — | silent |

s3308 ptr-check still `$v1=0` taken=1 n=139. s3306 exit-gate
printed n=100 all `$v0=0` `v0_nz=0`. Silent: 64BC, 6618,
title 1024. Last VI `#768` still `640 @ 0x00696100`.

`lw 0x44($s4->+0x1904)` minus 10 is `0x4A6`. Same-run
`[phase] cuts44=1200` is 10 more (two-source duration). Count
at `0xB28($s3)` advanced 0→`0x94` (148) across 139 flag
visits and never approached 1190. `$a0` stayed 0 on every
printed time-pred and flag-byte row (the skip-allow byte from
controller / `0x800B0B1C`; prologue stores 0 at `0x800A5EE8`).

## Conclusion

`H-FlagByteSkip` is selected. `H-JalUnreached`,
`H-TimePredSkip` as defined (626C `taken=1`), `H-JalFires`,
and `H-CoverageInvalid` are refuted. Combined with retail
Session 3310, the port-only stop of `jal cinematicInitializer`
is `0x800A6274` taking because `$a0==0` while count (148)
is still below limit-10 (1190). On MIPS, 626C taken (count
>= 1190) is the path that *bypasses* this flag check and
falls into 627C/62B4; that path never ran here.

Retail 62B4 at 48.1 s after ~972 advancer calls is consistent
with a ~30 Hz loop reaching count>=1190 and bypassing 6274.
The port loop is ~1.2 Hz on this 122 s window (single-source
rate vs retail's 48 s fire). A 600 s soak at this rate would
still be short of 1190. That rate claim is not two-source;
the skip table is.

No M5 Step 3. Next discriminator is independent retail: the
same four PCs with `$v0`/`$v1`/`$a0`, to split
time-pred bypass vs flag-byte set as the hardware path into
`0x800A62B4`.

Evidence dir: `scratch/agent/s3311_cine_init_jal/`.
