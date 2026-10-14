# Resume next work unit

HYPOTHESIS-ID: m5-step11-producer-witness

Single bounded work unit: qualify M5 Step 11's second MusyX wait using a new
producer-witness discriminator on the now-qualified real-image route. Run
default `ROGUESQ_AUDIO_SPIN2_YIELD=1` and rollback `=0` concurrently from one
build, with the documented autopilot and a phase gate through title/hangar.
Arm `ROGUESQ_LOG_M5_GATE_CONTRACT=1`, `ROGUESQ_LOG_AUDIO_RETURN=1`,
`ROGUESQ_LOG_PCM_BOUNDARY=1`, and the existing task/SP controls. Do not rerun
the s4829 pair unchanged.

Competing hypotheses:

* H-producer-clear: the real-image route reaches the named producer arm/clear
  and wait return; yield-on returns safely while rollback retains the old spin
  boundary.
* H-route-invalid: both arms again reach title/hangar but no producer arm/clear
  or wait-return witness occurs, so Step 11 remains unevaluable.
* H-yield-causal: the producer witness exists, but only yield-on reaches the
  wait return or downstream route while rollback stalls/crashes.

Discriminating measurement: phase-5 `[m5-gate]` rows must show producer arm,
clear, and wait return in the same arm/route join, with task/SP and nonzero PCM
source/consumer controls in both arms. Complete producer/clear/return in both
arms selects H-producer-clear; absent producer/clear/return in both selects
H-route-invalid; arm-separated return/route progress selects H-yield-causal.

Exact preparation and run: inspect the existing Step 11 controls in
`tools/run_m5_yield_ab.sh`, create or adapt one bounded same-build driver for
the two `ROGUESQ_AUDIO_SPIN2_YIELD` arms, build
`cmake --build build --config Debug --target RogueSquadron64Recomp`, then run
the driver from the repo root. Require title/hangar phase controls and SIGKILL
cleanup; enqueue any repeat soak instead of babysitting it.
