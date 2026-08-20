# NEXT work unit (s1990) — stopAllSynthVoices gate 0x80141AD0 vs n_work

HYPOTHESIS-ID: hangar-frame-freeze

## What s1989 settled

Fade zeros hangar +0x60 on every armed call (narmed=131404,
all val=0) matching the +0x30 `0x14` rewrite. Envelope adds
step `0x8B000` (narmed=2690, n0=0, n8b=2678). Dump sees 0
because fade re-inits in the same `tickMusyXIfActive`.
H-fade-rearms-zeros-elapsed SELECTED; H-envelope-never-called
/ H-step-is-zero REFUTED.

Static: fade has two direct callers. `stopVoicesByHandle`
runtime n=30. Remainder must be `stopAllSynthVoices`
`0x8008DBF4`, jal'd from every `tickMusyXIfActive` with
`$a0=0`. That function `blez`-skips the sweep on
`lbu 0x80141AD0`.

## Competing hypotheses

- **H-stop-all-gate-stuck:** `0x80141AD0` stays >0 through
  10M; stopAll n_work ≈ drain ticks; its fade jal narmed ≈
  fade-zero narmed (131404). Gate never drops so every in-loop
  tick re-fades every live voice.
- **H-stop-all-skips:** gate<=0, n_work=0, fade jal narmed=0;
  the 131k fade zeros are not this function (missing caller).
- **H-stop-all-once:** n_work small at drain start then gate
  drops; remaining fade zeros come from `stopVoicesByHandle`
  (already n=30 total — would need that count to be wrong).

## Discriminating measurement (one instrument, one build, one 60s probe)

Keep `[drain-path] w60=` / `[w60-sum]`. Dest-map:
- `stopAllSynthVoices` entry after `lbu 0x80141AD0`
  (`0x8008DBF8`): n/narmed/n_skip (blez)/n_work, last gate.
- fade jal inside `stopAllSynthVoices` `0x8008DCC4`.
- fade jal inside `stopVoicesByHandle` `0x8008DB98`.

Dump sums at `[drain-timeout]`. First 8 + every 10000th;
log every gate change. `S32`. No store changed.

Outcomes:
- gate>0 through 10M, n_work huge, stopAll-fade narmed ≈
  131404 → H-stop-all-gate-stuck
- n_work=0 / n_skip ≈ drain ticks → H-stop-all-skips
- n_work small then gate=0 → H-stop-all-once

Positive control: `[drain-path] call=1 unmap=0` 18 idx rows
`h58=0x0014` at iters=1; `[drain-stop-sum] entry=1` fade
n>=150; last alloc tickn=4 `0x801714D0 count=18`; `[w60-sum]`
fade narmed>0; `[drain-timeout]` 10M; first-8 `[stop-all]`
from `tickMusyXIfActive` (gate printed). Keep
`ROGUESQ_SPIN_YIELD=1` and `ROGUESQ_LOG_VI_CALLERS=1`.

SENTINEL is applied — incremental edit, do not rerun full fixup.

## Exact patch sites

- Incremental `apply_s1990_stop_all` in
  `/Users/williambuckley/Documents/Tools/N64Recomp/fixup_game_funcs.py`.
- Entry + fade jal in `funcs_23.c` (`stopAllSynthVoices`,
  `stopVoicesByHandle`).
- Sum dump at existing `[drain-timeout]` in `funcs_30.c`.

## Exact test

```sh
mkdir -p scratch/agent/s1990_stop_all
env ROGUESQ_SPIN_YIELD=1 ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 \
ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_LOG_VI_CALLERS=1 \
PROBE_PHASE_WIDTH=512 PROBE_PHASE_TIMEOUT=60 PROBE_LEAVE_OK=1 \
PROBE_KEYS='6:start 11:start 16:start 21:start 26:start 31:start 36:start 41:start 46:start 51:start 56:start' \
zsh tools/probe.sh scratch/agent/s1990_stop_all 60 2
```
