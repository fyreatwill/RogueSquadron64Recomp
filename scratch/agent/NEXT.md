# Next work unit: M5 Step 4l witness transport for the `0x8008D5FC` call

HYPOTHESIS-ID: m5-audio-step4l-callee-path

Session 4087 qualified the retail controls and port title/hangar route, but the
new `funcs_20.c` callee-detail hooks produced zero rows while the existing
`0x8008D604` post-call hook produced 86 rows. The generated object references
the detail symbol; the existing callee witness reports saved `ra=0`, so the
original return-address filter was invalid. Removing only that host-side filter
still produced zero detail rows. This is a hook transport/linkage problem, not
callee evidence.

Competing hypotheses:

- Htransport: the detail calls are not on the executed linked callee path, or
  the host hook is not reachable from that path.
- Hcallee-entry/load: once transport is proven, entry or the
  `0x8008488C`/`0x800848A8`/`0x800848C4` rows diverge.
- Hcallee-return: once inputs match, the callee's return arithmetic diverges.
- Hcoverage: either arm misses the whole-RDRAM, title, or hangar controls.

Discriminating measurement: one build and control-first capture must prove a
host-hook control, prove the linked `funcs_20` detail call executes, and retain
the existing `0x8008D604` row. A linked-call positive proves Htransport false;
zero detail calls with a positive host control selects Htransport; missing
phase controls selects Hcoverage. Only then compare retail
`--watch-pc 0x8008D5FC,0x80084860,0x80084AB8` rows with callee inputs.

Preparation and exact commands:

1. Inspect `nm build/libRecompiledFuncs.a`, the linked `funcs_20.c.o`, and the
   exact executed `evaluateVoiceModulatorRecord` path; add a positive host-hook
   control if needed. Keep detail rows phase-scoped and regeneration-safe.
2. Build once:
   `cmake --build build --config Debug --target RogueSquadron64Recomp`
3. Run one new `scratch/agent/run_s4088_*` recipe with the retail oracle
   positive control, `--watch-pc 0x8008D5FC,0x80084860,0x80084AB8`, and the
   qualified timing route. Capture under `scratch/agent/s4088_*`; SIGKILL
   every arm and reject missing controls.
