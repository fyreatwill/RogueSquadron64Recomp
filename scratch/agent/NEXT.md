# Capture one producer-vs-guest witness for the VI-640 stall

HYPOTHESIS-ID: vi640-producer-vs-guest

The s4796 hangar-gated mission driver never reached hangar: the run stayed in
VI 640 and emitted `vi-fs stalled=1`, so no input or overlay-0x2C conclusion is
valid. M5's current de-stubbing rows are qualified or route-blocked. The next
unit is one state-gated sample of the live stall, with no runtime mitigation.

Competing hypotheses and discriminator:
- H1: the guest is blocked in an audio wait while the host VI loop continues.
- H2: the guest advances, but the VI/RDP producer is stalled independently.
- H3: `vi-fs stalled=1` is only a presentation-side symptom and the guest is
  parked elsewhere.

The discriminating measurement is one run that waits until VI 640 has emitted
`vi-fs stalled=1` for at least 10 seconds, confirms whether `update_screen`
advances, then samples the process at that state. H1 predicts the game-thread
stack in the audio wait and a live VI producer; H2 predicts a live game thread
with the producer/RDP path blocked; H3 predicts neither and is resolved by the
sampled game-thread PC. A startup crash or failure to reach VI 640 is
route-invalid and cannot select a hypothesis.

Commands: use the existing state-gated sampler pattern, but arm the sample
only after the `vi-fs stalled=1` and static-update-screen conditions in the
same log; validate the sampler with its healthy 20-second control, run from
`build/`, SIGKILL cleanup, and capture under `scratch/agent/soak_results/`.
Do not use a stopwatch-only sample.
