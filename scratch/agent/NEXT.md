# Resume next work unit

HYPOTHESIS-ID: m5-step11-route-stabilization

Single bounded work unit: rerun the M5 Step 11 default versus rollback pair
with the route-stabilizing tuple from the prior qualified wait recipe: add
`ROGUESQ_STUB_MISSING_FUNCS=1` and use the phase-gated autopilot
`40:start,44:start,48:start,52:start,56:a,60:a,64:start,68:a`, retaining
LLE force/ungated/solo and host spin yield. Run both arms concurrently from
one rebuilt binary: default `ROGUESQ_AUDIO_SPIN2_YIELD=1`, rollback `=0`.

Arm `ROGUESQ_LOG_WAITMUSYX_SPIN2=1`, `ROGUESQ_LOG_M5_WAIT_CONTRACT=1`,
`ROGUESQ_LOG_M5_GATE_CONTRACT=1`, audio return, PCM boundary, task contract,
and event-wiring controls. Keep SIGKILL cleanup and require title/hangar phase
controls before interpreting any null.

Competing hypotheses:

* H-producer-clear: both phase-gated arms reach named producer arm/clear and
  wait return, with no crash; yield-on and rollback differ only in yields.
* H-route-invalid: either arm misses title/hangar or both phase-gated arms lack
  producer/clear/return witnesses, so Step 11 remains unevaluable.
* H-yield-causal: both arms reach the producer witness, but only yield-on
  reaches wait return/downstream progress or rollback hits the old spin boundary.

Discriminating measurement: phase-5 rows must show
`[waitmusyx-spin2-arm]`, `[waitmusyx-spin2-clear]`, and
`[waitmusyx-spin2-loop] event=return` in the same arm/route join, with
task/SP and nonzero PCM source/consumer controls in both arms. Complete
producer/clear/return in both arms selects H-producer-clear; absent or
pre-phase rows select H-route-invalid; arm-separated return/route progress
selects H-yield-causal.

Exact preparation and run: update `tools/run_m5_yield_ab.sh` with the tuple
above, build `cmake --build build --config Debug --target
RogueSquadron64Recomp`, then run `zsh tools/run_m5_yield_ab.sh` from the repo
root. Record the per-arm driver summary and do not interpret a null without
the `[m5-gate]` positive control and phase transitions.
