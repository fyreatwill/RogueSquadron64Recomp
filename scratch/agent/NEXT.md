# Next work unit: M5 Step 4l positive host transport on the post-call route

HYPOTHESIS-ID: m5-audio-step4l-callee-path

Session 4088 was Hcoverage: retail controls passed, but both port attempts
crashed before title/hangar. The synthetic control was attached too late in
the path to be positive. Move it to the already-observed `0x8008D604`
post-call hook, then retain genuine detail rows only for `0x8008488C`,
`0x800848A8`, and `0x800848C4`.

Competing hypotheses:

- Htransport: the generated detail calls are not on the executed linked path,
  while the post-call host path is live.
- Hcallee-entry/load: generated detail rows become positive and show divergence
  at the count/record loads.
- Hcallee-return: generated detail rows match, but the callee return diverges.
- Hcoverage: either arm misses the whole-RDRAM, title, or hangar controls.

Discriminating measurement: one build and one control-first capture must show
retail whole-RDRAM/title/hangar controls, a port title/hangar pair, the
synthetic detail row emitted from the `0x8008D604` host path, and the existing
post-call row. With those controls, zero genuine detail rows selects
Htransport; genuine rows select entry/load/return by their values; missing
port phases selects Hcoverage.

Preparation:

1. Change only the host control placement in `src/main/upstream_compat.cpp`;
   do not change the guest detail hooks.
2. Build once:
   `cmake --build build --config Debug --target RogueSquadron64Recomp`
3. Run the qualified route:
   `zsh scratch/agent/run_s4087_m5_callee_detail_qualified.sh`
   with the retail watches extended by `0x8008488C,0x800848A8,0x800848C4`.
   Capture under a new `scratch/agent/s4089_*` directory and SIGKILL both
   processes.
