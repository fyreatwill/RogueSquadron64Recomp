# NEXT work unit (s1994) — post-drain jal enter/exit breadcrumbs

HYPOTHESIS-ID: hangar-frame-freeze

## What s1993 settled

`ROGUESQ_DRAIN_INLOOP_TICK=0` skips the s1976 host
injection. Drain returns at 300k with v0=1; all 18
hangar slots `b=0x00`. Envelope narmed=48; stopAll
narmed=0. H-injection-prevents-idle SELECTED for
drain. H-need-envelope-without-stopall /
H-other-keep-alive REFUTED.

fs still 1245 from `#2112` after drain-exit (same
freeze as s1976 force-idle). 0 slot-ret after exit.
Host VI SKIP `lastCimg=0 pairs=0 stalled=1`. Drain
is the craft-select exit path; the next ROM jal
after `[drain-exit]` is `bufferArbiterProducerScanWait`.

Default stays ON. Recipe for this unit keeps
`ROGUESQ_DRAIN_INLOOP_TICK=0`.

## Competing hypotheses

- **H-arbiter-wait:** drain-exit then
  `bufferArbiterProducerScanWait` enter=1 exit=0.
  Guest never reaches destroy/shutdown/finalize or
  the overlay caller.
- **H-later-drain-jal:** arbiter exits; hang is in
  `destroyPlayerShipRecord` /
  `shutdownFormatMessageWorker` /
  `finalizeCurrentSpeechBuffer` (enter=1 exit=0 on
  one of those).
- **H-caller-returned:** all four post-idle jals
  enter=1 exit=1; overlay caller
  (`tickCraftSelectScreen` loop at `0x800C5EA4`)
  stores s0 and returns; hang is in that parent.
- **H-drain-exit-never-reached-again:** this run's
  drain-exit was a fluke; 10M timeout returns.

## Discriminating measurement (one instrument, one build, one 60s probe)

Named enter/exit counters on the four post-idle jals
inside `drainAudioAndFinalizeSpeechBuffer` after
`L_800B24E4_drain_done`. Log `[drain-post] site=
arbiter|destroy|shutdown|finalize nenter= nexit=`
on each edge (first 8). Dump `[drain-post-sum]` at
process end is unnecessary — a 60s hangar window
after drain-exit is enough. Also log overlay caller
s0 (`ctx->r16`) once at the `jal 0x800B24C4` return
in funcs_34.c (`[craft-select-s0] s0=0x...`).

Keep `[drain-exit]` / `[tick-site-sum]` /
`[drain-inloop-gate]`. `S32`. No store changed.
Do not default the in-loop tick off.

Positive control: `[drain-inloop-gate] en=0`;
`[drain-exit] v0=1` iters<10M; `[drain-post]
site=arbiter nenter=1` (the first jal after
drain-exit must fire if we returned).

Outcomes:
- arbiter nenter=1 nexit=0 → H-arbiter-wait
- arbiter exits; one later site nenter=1 nexit=0
  → H-later-drain-jal (name the site)
- all four nenter=1 nexit=1 and `[craft-select-s0]`
  prints → H-caller-returned (s0 is the extra key)
- no `[drain-exit]` / `[drain-timeout]` 10M →
  H-drain-exit-never-reached-again

SENTINEL is applied — incremental edit, do not rerun
full fixup.

## Exact patch sites

- Incremental wrap of the four post-idle jals in
  `drainAudioAndFinalizeSpeechBuffer` after
  `L_800B24E4_drain_done` in
  `/Users/williambuckley/Documents/Tools/N64Recomp/fixup_game_funcs.py`
  (`apply_s1994_drain_post`) and `funcs_30.c`.
- One log at the `jal 0x800B24C4` return in
  `funcs_34.c` (overlay craft-select loop).

## Exact test

```sh
mkdir -p scratch/agent/s1994_drain_post
env ROGUESQ_DRAIN_INLOOP_TICK=0 ROGUESQ_SPIN_YIELD=1 \
ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 \
ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_LOG_VI_CALLERS=1 \
PROBE_PHASE_WIDTH=512 PROBE_PHASE_TIMEOUT=60 PROBE_LEAVE_OK=1 \
PROBE_KEYS='6:start 11:start 16:start 21:start 26:start 31:start 36:start 41:start 46:start 51:start 56:start' \
zsh tools/probe.sh scratch/agent/s1994_drain_post 60 2
```
