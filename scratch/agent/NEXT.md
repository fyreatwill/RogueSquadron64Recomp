# NEXT work unit (s1993) — disable s1976 in-loop drain tick

HYPOTHESIS-ID: hangar-frame-freeze

## What s1992 settled

Every drain-armed `tickMusyXIfActive` is the s1976 host
injection: drain-inloop n=10064 narmed=10064 matching
`[stop-all-sum]` narmed. Drain-entry ROM jal n=1
narmed=0 (before armed). All other ROM jals narmed=0.
H-drain-inloop-only SELECTED; H-drain-entry-plus-inloop
/ H-other-tick-sites REFUTED.

The ROM drain is one entry tick then
`anyAudioSlotActive` spin. The injection re-calls
`tickMusyXIfActive` → `stopAllSynthVoices` `$a0=0` →
empty-slot `beginVoiceFadeRelease` on all 18 live
voices, restarting duration 0x14 every tick.

## Competing hypotheses

- **H-injection-prevents-idle:** with the in-loop tick
  off, fade from the ROM entry tick (or pre-drain
  handle-stop) is allowed to finish; slots go idle;
  drain returns before 10M; `fs` moves.
- **H-need-envelope-without-stopall:** in-loop off →
  `[drain-timeout]` 10M still, `[w60-sum]` envelope
  narmed=0 and fade narmed=0, `w60` stuck 0 / `h30`
  stuck 0x14. Removing the re-fade also removes the
  only envelope advance, so idle still never happens.
- **H-other-keep-alive:** in-loop off → 10M still, but
  `w60` advances / `h30` counts down and slot+0 stays
  `0x02` anyway (loopers are not released by fade).

## Discriminating measurement (one instrument, one build, one 60s probe)

Env-gate the s1976 in-loop `tickMusyXIfActive` behind
`ROGUESQ_DRAIN_INLOOP_TICK` (unset/1 = current ON;
0 = skip the call, still count iters / timeout dump).
Default stays ON. Do not skip stopAll or the fade jal.

Keep `[tick-site-sum]` / `[stop-all-sum]` /
`[stop-all-path-sum]` / `[w60-sum]` / `[drain-path]`.
Dump at `[drain-timeout]` OR at drain exit if it
returns. `S32`. No store changed.

Positive control: `[tick-site-sum]` drain-inloop n=0
narmed=0 (the gate fired); `[drain-path] call=1
unmap=0` 18 idx rows at iters=1; last alloc tickn=4
`0x801714D0 count=18`; `[drain-stop-sum] entry=1`;
first-8 `[tick-site]` rows still print for ROM sites.

Outcomes:
- drain returns before 10M (no `[drain-timeout]`, or
  timeout absent and `fs` rises past the freeze) →
  H-injection-prevents-idle
- `[drain-timeout]` 10M, envelope narmed=0, fade
  narmed=0, last `w60=0` `h30=0x14` `b=0x02` on
  loopers → H-need-envelope-without-stopall
- `[drain-timeout]` 10M, `w60`/`h30` move toward
  idle but `b=0x02` stays → H-other-keep-alive

SENTINEL is applied — incremental edit, do not rerun
full fixup.

## Exact patch sites

- Incremental wrap of the s1976 in-loop
  `tickMusyXIfActive(rdram, ctx);` in
  `/Users/williambuckley/Documents/Tools/N64Recomp/fixup_game_funcs.py`
  (`apply_s1993_drain_inloop_gate`) and `funcs_30.c`.

## Exact test

```sh
mkdir -p scratch/agent/s1993_inloop_off
env ROGUESQ_DRAIN_INLOOP_TICK=0 ROGUESQ_SPIN_YIELD=1 \
ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 \
ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_LOG_VI_CALLERS=1 \
PROBE_PHASE_WIDTH=512 PROBE_PHASE_TIMEOUT=60 PROBE_LEAVE_OK=1 \
PROBE_KEYS='6:start 11:start 16:start 21:start 26:start 31:start 36:start 41:start 46:start 51:start 56:start' \
zsh tools/probe.sh scratch/agent/s1993_inloop_off 60 2
```
