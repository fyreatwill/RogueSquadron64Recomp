# NEXT work unit (s1991) — stopAll FREE path vs empty-slot fade

HYPOTHESIS-ID: hangar-frame-freeze

## What s1990 settled

stopAllSynthVoices never blez-skips: n_skip=0 n_work=10073
lastgate=18 through 10M. Gate is the allocated voice count
(setDisplayMode/reapplyDisplayMode sb, clamp 0x20; matches
ch=18 / alloc count=18), not a pending-stop flag. Every
in-loop tickMusyXIfActive therefore fades all 18 idxs
(stopAll-fade narmed=181152=10064×18). Handle-fade narmed=0.
H-stop-all-gate-stuck SELECTED; skip/once REFUTED.

The loop at L_8008DC50 either FREEs an occupied 0x17C synth
slot (fallthrough L_8008DC78 freeSynthVoiceFromActiveList)
or branches empty to L_8008DCC4 and still fades. Both arms
jal beginVoiceFadeRelease.

## Competing hypotheses

- **H-empty-then-fade:** 0($s2)==0 on every armed iter;
  n_empty ≈ 181152, n_free=0. Synth table is empty; the
  rewrite is the empty-slot fade jal.
- **H-free-every-tick:** n_free huge (occupied synths torn
  down every tick); n_empty + n_free ≈ 181152.
- **H-free-once:** n_free small at drain start then 0;
  remaining fade jals are empty-slot.

## Discriminating measurement (one instrument, one build, one 60s probe)

Keep `[stop-all-sum]` / `[w60-sum]` / `[drain-path] w60=`.
At `L_8008DC50` after `lw 0x0($s2)` (`0x8008DC50`): n/narmed/
n_empty (v0==0)/n_free (v0!=0), last v0. Dump at
`[drain-timeout]`. First 8 + every 10000th. `S32`. No store
changed. Do not skip or rewrite the fade jal.

Outcomes:
- n_free=0, n_empty ≈ 181152 → H-empty-then-fade
- n_free huge, n_empty+n_free ≈ 181152 → H-free-every-tick
- n_free small then 0 → H-free-once

Positive control: `[drain-path] call=1 unmap=0` 18 idx rows
`h58=0x0014` at iters=1; `[drain-stop-sum] entry=1` fade
n>=150; last alloc tickn=4 `0x801714D0 count=18`; `[w60-sum]`
fade narmed>0; `[drain-timeout]` 10M; `[stop-all-sum]`
n_work>0 lastgate=18; first-8 `[stop-all-path]` from the
L_8008DC50 loop (v0 printed). Keep `ROGUESQ_SPIN_YIELD=1`
and `ROGUESQ_LOG_VI_CALLERS=1`.

SENTINEL is applied — incremental edit, do not rerun full fixup.

## Exact patch sites

- Incremental `apply_s1991_stop_all_path` in
  `/Users/williambuckley/Documents/Tools/N64Recomp/fixup_game_funcs.py`.
- After `lw 0x0($s2)` in `funcs_23.c` `stopAllSynthVoices`
  (`L_8008DC50` / `0x8008DC50`).
- Sum dump at existing `[drain-timeout]` in `funcs_30.c`.

## Exact test

```sh
mkdir -p scratch/agent/s1991_stop_all_path
env ROGUESQ_SPIN_YIELD=1 ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 \
ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_LOG_VI_CALLERS=1 \
PROBE_PHASE_WIDTH=512 PROBE_PHASE_TIMEOUT=60 PROBE_LEAVE_OK=1 \
PROBE_KEYS='6:start 11:start 16:start 21:start 26:start 31:start 36:start 41:start 46:start 51:start 56:start' \
zsh tools/probe.sh scratch/agent/s1991_stop_all_path 60 2
```
