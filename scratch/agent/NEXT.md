# NEXT work unit (s2607) — C88 gate-polarity A/B on the restored hangar route

HYPOTHESIS-ID: m5-c88-gate-polarity

## Single work unit

s2606 showed the restored AUTOPILOT route reaches title and hangar, that
`reapplyDisplayMode` at `0x8008EC88` requests `0x01` but the C88 force-zero
hatch stores `0x00`, and that `musyxNoopStub` therefore takes the
`gate==0` early-out and never executes retail's `0x8008ED48` store.
`startSongSequence` / `0x80094648` never entered; PCM stayed zero.

M5 plan Step 4 is now evaluable. Run both C88 arms in this one iteration on
the same s2605/s2606 image. Do not change the default store, and do not
promote a gate value from a single arm.

The generated-symbol census at `0x800E8A34` stays parked.

## Competing hypotheses and discriminator

- `H-C88ForceZeroBlocksGate`: `ROGUESQ_M5_C88_VALUE=1` stores the guest
  requested `0x01` at `0x8008EC88`; title/hangar gate rows become nonzero;
  `musyxNoopStub` no longer early-outs on `gate==0`; synth/song and/or
  `0x80094648` and/or nonzero PCM appear in the same phases.
- `H-C88NotSufficient`: C88=1 stores `0x01` and the gate is nonzero, but
  `0x80094648` still does not run and PCM stays `nz=0`. The missing writer
  is then downstream of the gate, not the force-zero hatch.
- `H-C88RouteAbort`: the C88=1 arm dies before title/hangar, so the table
  is unevaluable (force-zero may still be a route hatch).

The discriminator is two concurrent AUTOPILOT hangar runs of the same image,
one with `ROGUESQ_M5_C88_VALUE` unset (control; must reproduce s2606:
requested 1, stored 0, gate 0) and one with `ROGUESQ_M5_C88_VALUE=1`.
Require title `1024 @ 0x00790400` and hangar `512 @ 0x006AB400` as the
positive control in each arm that is claimed evaluable.

## Exact checks

1. Confirm `python3 tools/check_jr_t9_host_return.py` still passes.
2. Reuse `build/RogueSquadron64Recomp` (s2605 image). Do not regenerate.
3. From `build/`, ROM present, both arms at once (one game ~50% of one core).
   Shared flags:
   `ROGUESQ_LLE_FORCE=1 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 ROGUESQ_LOG_M5_WRITER_ENTRY=1 ROGUESQ_LOG_M5_GATE_CONTRACT=1 ROGUESQ_LOG_PCM_BOUNDARY=1 ROGUESQ_LOG_AUDIO_RETURN=1 ROGUESQ_LOG_M5_B40_WRITER=1 ROGUESQ_AUTOPILOT='3:start,6:start,9:start,12:start,16:a,20:a,24:start,28:a' ROGUESQ_AUTOPILOT_STOP_WIDTH=512`
   - control: no `ROGUESQ_M5_C88_VALUE` → `scratch/agent/s2607_m5_c88_control.log`
   - arm: `ROGUESQ_M5_C88_VALUE=1` → `scratch/agent/s2607_m5_c88_value.log`
   SIGKILL each at ~90s. Final log component must not start with `.`.
4. Per arm and per title/hangar: C88 requested/stored, gate byte,
   `musyxNoopStub` entry vs `0x8008ED48` store, `startSongSequence` /
   `0x80094648`, PCM `nz`, audio-return arm. The control arm must reproduce
   s2606 or the comparison is invalid.
5. Do not change the default C88 hatch this iteration regardless of outcome.
