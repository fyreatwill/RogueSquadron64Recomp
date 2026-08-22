# NEXT work unit (s2174) — classify failing =1 heap0 $v0=0

HYPOTHESIS-ID: m5-a1-cinematic-split

## Work unit

s2173 selected `H-PortHeap0MatchesRetail`: same-build `=1`/`=0`
both store KSEG0 first-slot dest `0x8025A580` value `0x800CA748`
at `0x80057100` and `0x800A87A0` reloads it (933/933 and 317/317,
mismatch=0, zero=0). Completing `=1` reached title+hangar with
lwc zero_logged=0. The s2171 `$v0=0` at `0x800A87A8` is not a
missing constructor.

Queued soak `scratch/agent/soak_queue/s2173_image_heap0_fail.sh`
re-runs `=1` with the s2173 always-log (dest phys `0x25A580` and
87A8 `$v0==0`). If the loop already appended a verdict, fold it.
If not, run the same recipe. Do not S32-address, NULL-skip,
re-flip default-on, skip/allow the lwc, add a wait/slot guard,
or log `$t0`.

## Competing hypotheses and discriminator

- `H-ClobberFirstSlot`: failing run logs `[heap0] site=load87a0`
  dest=`0x8025A580` value=0 (always-log) before SIGBUS. Then a
  later writer zeroed word0; next unit names that writer.
- `H-LwcZeroOtherDest`: `[heap0] site=lwc87a8 zero=1` with
  dest != `0x8025A580` while first-slot loads stay `0x800CA748`.
  Then s2171 `$v0=0` is a different slot/object.
- `H-NoZeroThisRun`: title+hangar, load/lwc zero=0 (intermittent
  miss; does not refute s2171).
- `H-CoverageFailure`: missing `[heap0-ctl]` /
  `[cutscene-a2-50-ctl]` at 640/`0x00696100`, or store57100 n=0.

Positive controls: ctl at width=640 origin=`0x00696100`;
store57100 dest `0x8025A580` n>=1; load87a0 n>=1.

## Exact commands

If `scratch/agent/SOAK-RESULTS.md` has a new `s2173_image_heap0_fail`
line, classify from that log (do not re-run). Else:

    env GAME_EXTRA_ENV="ROGUESQ_SPIN_YIELD=1 ROGUESQ_AUDIO_UCODE=1 ROGUESQ_LOG_ALL=1 ROGUESQ_LOG_CUTSCENE_A2_50=1" \
      zsh scratch/s73_post_a_scene/run_mission_keys.sh s2174_on 30 12

180s SIGKILL. Table to `scratch/agent/s2174_heap0_fail.txt`.
The binary already carries the s2173 probes; rebuild only if
`[heap0-ctl]` is absent from a coverage check.
