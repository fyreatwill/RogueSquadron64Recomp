# Next work unit: M5 Step 4l callee value comparison on a qualified route

HYPOTHESIS-ID: m5-audio-step4l-callee-path

Session 4089 proved detail-hook transport at title scope: the synthetic row
fired from `0x8008D604`, and 511 genuine detail rows fired. Retail did not
reach hangar, so no value classification is allowed yet.

Competing hypotheses:

- Hcallee-entry/load: the first divergence is in the values observed at
  `0x8008488C` or `0x800848A8`.
- Hcallee-return: the first two detail stages match, but `0x800848C4`
  diverges.
- Hlater: all three detail stages match and the mismatch is downstream.
- Hcoverage: either side misses the required title or hangar phase.

Discriminating measurement: one control-first capture must show the retail
whole-RDRAM/title/hangar controls, a port title/hangar pair, and phase-scoped
detail rows on both sides. Compare the three watched PCs by record and value;
the first mismatch selects the boundary, while matching all three moves the
search later.

Preparation:

1. Remove the invalid `ra=0x8008D604` condition from the recipe summary
   counters; retain the synthetic marker and three detail PCs.
2. Build once:
   `cmake --build build --config Debug --target RogueSquadron64Recomp`
3. Run the control-first qualified timing route, capturing under a new
   `scratch/agent/s4090_*` directory and SIGKILLing both processes. Accept a
   result only if the oracle positive control and both title/hangar gates fire.
