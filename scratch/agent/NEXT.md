# NEXT work unit (s1992) — tickMusyXIfActive caller census

HYPOTHESIS-ID: hangar-frame-freeze

## What s1991 settled

stopAll drain path is empty-slot fade: n_free_armed=0
n_empty_armed=181152 lastv0armed=0. The 13 FREEs are
pre-drain. L_8008DCC4 merge still fades live 0x88 voices
by idx. Sole static caller of stopAllSynthVoices is
tickMusyXIfActive 0x8008DA2C ($a0=0). H-empty-then-fade
SELECTED; H-free-every-tick / H-free-once REFUTED.

## Competing hypotheses

- **H-drain-inloop-only:** all ~10064 armed stopAll come
  from the s1976 injected tick inside the drain spin
  (`funcs_30.c` after `L_800B24D4`, no jal comment).
  Other 10 ROM `jal 0x8008DA00` sites narmed=0.
- **H-drain-entry-plus-inloop:** mix of original drain
  jal `0x800B24CC` and the in-loop injection; no other
  sites.
- **H-other-tick-sites:** menuControllerInput /
  menuOverlayInit / waitForAnyAudioSlot / screen handlers
  also fire during drain-armed.

## Discriminating measurement (one instrument, one build, one 60s probe)

Keep `[stop-all-sum]` / `[stop-all-path-sum]` / `[w60-sum]`.
At every `tickMusyXIfActive(rdram, ctx)` call site, count
n/narmed by named site. Dump all sites at `[drain-timeout]`.
First 8 + every 10000th per site. `S32`. No store changed.
Do not skip stopAll or the fade jal.

Sites (11):
- drainAudioAndFinalizeSpeechBuffer jal 0x800B24CC (ROM)
- drainAudioAndFinalizeSpeechBuffer in-loop s1976 (injected)
- waitForAnyAudioSlot 0x800668B8
- gracefulMenuShutdown 0x800AE754
- menuControllerInput 0x800B8048
- runMenuRandomBackdropScreen 0x800BFF58
- runMenuShipSelectScreen 0x800C1748
- runMenuModelViewerScreen 0x800C2DA8
- menuSubtype02Handler 0x800C3F5C
- menuOverlayInit 0x800C5928
- runModelViewerLoop 0x800CA578

Outcomes:
- in-loop narmed ≈ 10064, all others narmed=0 → H-drain-inloop-only
- in-loop + drain-entry narmed>0, others 0 → H-drain-entry-plus-inloop
- any other site narmed>0 → H-other-tick-sites

Positive control: `[drain-path] call=1 unmap=0` 18 idx rows
`h58=0x0014` at iters=1; `[drain-stop-sum] entry=1` fade
n>=150; last alloc tickn=4 `0x801714D0 count=18`; `[w60-sum]`
fade narmed>0; `[drain-timeout]` 10M; `[stop-all-sum]`
n_work>0 lastgate=18; `[stop-all-path-sum]` n_free_armed=0
n_empty_armed>0; first-8 `[tick-site]` rows printed.
Keep `ROGUESQ_SPIN_YIELD=1` and `ROGUESQ_LOG_VI_CALLERS=1`.

SENTINEL is applied — incremental edit, do not rerun full fixup.

## Exact patch sites

- Incremental `apply_s1992_tick_site` in
  `/Users/williambuckley/Documents/Tools/N64Recomp/fixup_game_funcs.py`.
- Each `tickMusyXIfActive(rdram, ctx);` listed above.
- Sum dump at existing `[drain-timeout]` in `funcs_30.c`.

## Exact test

```sh
mkdir -p scratch/agent/s1992_tick_site
env ROGUESQ_SPIN_YIELD=1 ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 \
ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_LOG_VI_CALLERS=1 \
PROBE_PHASE_WIDTH=512 PROBE_PHASE_TIMEOUT=60 PROBE_LEAVE_OK=1 \
PROBE_KEYS='6:start 11:start 16:start 21:start 26:start 31:start 36:start 41:start 46:start 51:start 56:start' \
zsh tools/probe.sh scratch/agent/s1992_tick_site 60 2
```
