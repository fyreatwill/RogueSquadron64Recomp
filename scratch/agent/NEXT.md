# Next work unit: M5 Step 4m downstream post-callee comparison

HYPOTHESIS-ID: m5-audio-step4m-post-callee

Session 4090 matched the sampled port detail values at
`0x8008488C/0x800848A8/0x800848C4` against the retail register handoff. The
next boundary is downstream at the existing `0x80084AB8` witness.

Competing hypotheses:

- Hpost-callee: the first divergence appears at the `0x80084AB8` handoff.
- Hlater-transform: `0x80084AB8` matches and the mismatch is later.
- Hcoverage: either side lacks a qualified title/hangar sample.
- Hmapping: the `0x80084AB8` witness is not the same downstream value path.

Discriminating measurement: one control-first capture must fire the retail
whole-RDRAM positive control and both title/hangar gates, while the port fires
its synthetic transport row, detail rows, and `0x80084AB8` state rows. Compare
the first downstream handoff for the same visible record shapes: a mismatch
selects Hpost-callee; matching values selects Hlater; no qualified paired
rows selects Hcoverage; a consistent field/record mismatch selects Hmapping.

Preparation:

1. Keep the three callee detail PCs and synthetic control as positive controls.
2. Add only the phase-scoped `0x80084AB8` comparison field if it is not
   already emitted by `ROGUESQ_LOG_M5_VOICE_MODULATION`; do not add a second
   independent route.
3. Build once:
   `cmake --build build --config Debug --target RogueSquadron64Recomp`
4. Run the control-first route:
   `zsh scratch/agent/run_s4091_m5_post_callee.sh`
5. Accept a conclusion only if the oracle positive control and both title and
   hangar gates fire, and the port synthetic/detail controls are positive.
