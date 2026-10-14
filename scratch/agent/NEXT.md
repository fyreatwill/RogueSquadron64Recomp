# Resume next work unit

HYPOTHESIS-ID: m5-step1-new-route-discriminator

Single bounded work unit: design and run one new route discriminator for the
M5 Step 1 default-image versus silent-control qualification. The s4823/s4829
routes are invalid when they stop before the required downstream phase, so do
not repeat either recipe unchanged.

Competing hypotheses:

* H-route-progress: the new route control reaches the target title/hangar
  phase in both arms and permits the Step 1 task/service/PCM comparison.
* H-route-common-gate: both arms still stop at the same pre-target gate while
  retaining task/SP controls, proving only that the route discriminator did not
  move the boundary.
* H-route-arm-specific: the new control separates the arms before the target
  phase, selecting an arm-specific route/lifecycle difference.

Discriminating measurement: in one same-build concurrent run, the first
phase-gated target-origin row for each arm, plus task dispatch, SP completion,
service/slot, and nonzero PCM source/consumer controls. Target-origin in both
arms selects H-route-progress; same pre-target gate selects H-route-common-gate;
an arm-only target/crash/stop selects H-route-arm-specific. A missing whole-
RDRAM/route control makes the run invalid.

Before implementation, inspect the existing Step 1 harness and add one route
control only after identifying a concrete state transition it can distinguish.
Then build both arms together and run the harness phase-gated; enqueue any
repeat soak rather than babysitting it. Do not rerun the A10 replay, s4828
startup capture, or unchanged Step 11 A/B.
