# NEXT work unit (s1989) — dest-map +0x60 elapsed add vs fade zero

HYPOTHESIS-ID: hangar-frame-freeze

## What s1988 settled

Hangar +0x58 is duration, frozen at fade copy `0x14` through 10M
(108 samples, 12 loopers). `w64=0` `w68=0x3F800000` frozen.
`w60` is 0 on 103/108 and `0x0008B000` on 5 (all loopers, same
iters). H-working-timer-is-0x58 REFUTED; H-envelope-fields-stuck
SELECTED for +0x58/64/68. Static: `advanceVolumeFadeEnvelope`
adds `$a1` into +0x60; fade zeros +0x60 every call.

## Competing hypotheses (why +0x60 stays 0 at dump-after-tick)

- **H-fade-rearms-zeros-elapsed:** envelope `sw +0x60` hangar-armed
  n>0 (lastval often `0x8B000`); fade `sw $zero, +0x60` hangar-armed
  n matches fade narmed. Dump sees 0 because fade re-inits after
  the add in the same `tickMusyXIfActive`.
- **H-envelope-never-called:** envelope hangar narmed=0; the 5×
  `0x8B000` hits are another writer.
- **H-step-is-zero:** envelope hangar narmed>0 but stored val is
  always 0 (`$a1=0`); fade-zero is incidental.

## Discriminating measurement (one instrument, one build, one 60s probe)

Keep `[drain-path] w60=` / `h58=`. Dest-map:
- `advanceVolumeFadeEnvelope` `0x8008F64C` `sw $v0, 0x60($a0)`
  (val after `addu $a1`).
- `beginVoiceFadeRelease` `0x800924DC` `sw $zero, 0x60($a0)`
  (both copies if delay/fallthrough).
- `musyxStartVoiceRelease` `0x800922B0` `sw $zero, 0x60($a0)`
  (both copies).

Hangar dest = `0x801714D0+idx*0x88`, idx<18. Same census shape
as s1987: n/nhangar/narmed, lastval, lastidx; unique (site,val)
for hangar; first 8 any dest; hangar first 16 + every 10000th.
Dump sums at `[drain-timeout]`. `S32`. No store changed.

Outcomes:
- envelope narmed>0, lastval `0x8B000`-class, fade-zero
  narmed ≈ fade narmed → H-fade-rearms-zeros-elapsed
- envelope narmed=0 → H-envelope-never-called
- envelope narmed>0 and lastval always 0 → H-step-is-zero

Positive control: `[drain-path] call=1 unmap=0` 18 idx rows
`h58=0x0014` at iters=1; `[drain-stop-sum] entry=1` fade n>=150;
last alloc tickn=4 `0x801714D0 count=18`; `[h30-sum]` fade
narmed>0; `[drain-timeout]` 10M; first-8 `[w60-store]` on
envelope and fade. Keep `ROGUESQ_SPIN_YIELD=1` and
`ROGUESQ_LOG_VI_CALLERS=1`.

SENTINEL is applied — incremental edit, do not rerun full fixup.

## Exact patch sites

- Incremental `apply_s1989_w60_store` in
  `/Users/williambuckley/Documents/Tools/N64Recomp/fixup_game_funcs.py`.
- Envelope store in `funcs_23.c`; fade/release zeros in `funcs_24.c`.
- Sum dump at existing `[drain-timeout]` in `funcs_30.c`.

## Exact test

```sh
mkdir -p scratch/agent/s1989_w60_store
env ROGUESQ_SPIN_YIELD=1 ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 \
ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_LOG_VI_CALLERS=1 \
PROBE_PHASE_WIDTH=512 PROBE_PHASE_TIMEOUT=60 PROBE_LEAVE_OK=1 \
PROBE_KEYS='6:start 11:start 16:start 21:start 26:start 31:start 36:start 41:start 46:start 51:start 56:start' \
zsh tools/probe.sh scratch/agent/s1989_w60_store 60 2
```
