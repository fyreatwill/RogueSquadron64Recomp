# Next work unit: M5 Step 4l callee path for the `0x8008D5FC` call

HYPOTHESIS-ID: m5-audio-step4l-callee-path

Session 4086 qualified the separate callsite. Retail's `0x8008D5FC` return
varied by voice record, while the port's sampled `0x8008D604` result repeated
`0x3F80`; the port's `0x8008D610` lhs stayed zero. The next boundary is inside
`evaluateVoiceModulatorRecord` for the `a1=s0+0xC0` call path.

Competing hypotheses:

- Hcallee-entry: the call arguments or callee entry state already diverge.
- Hcallee-load: entry matches, but a callee input load or branch diverges.
- Hcallee-return: entry and inputs match, but the callee's return arithmetic
  diverges.
- Hcoverage: either arm misses the whole-RDRAM, title, or hangar controls.

Discriminating measurement: one build and one control-first capture must pair
retail `--watch-pc 0x8008D5FC,0x80084860,0x80084AB8` rows with a port witness
that tags the `0x80084860` entry/return to the `0x8008D5FC` caller (using its
return address), records the callee's input loads/branch result, and retains
the `0x8008D604` return row. Hcallee-entry selects the first argument/state
mismatch; Hcallee-load selects the first load/branch mismatch after matching
entry; Hcallee-return selects a first mismatch only at the callee return;
matching all rows moves the search earlier than this callee. Hcoverage rejects
the run.

Preparation and exact commands:

1. Extend `/Users/williambuckley/Documents/Tools/N64Recomp/fixup_game_funcs.py`
   and `src/main/upstream_compat.cpp` with the tagged callee witness; apply
   the regenerated-equivalent patch to
   `/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_20.c`.
2. Build once:
   `cmake --build build --config Debug --target RogueSquadron64Recomp`
3. Run one new `scratch/agent/run_s4087_*` recipe with the retail oracle
   positive control first, `--watch-pc 0x8008D5FC,0x80084860,0x80084AB8`, and
   the isolated direct-AUTOPILOT port arm. Capture under
   `scratch/agent/s4087_*`; SIGKILL every arm and reject missing controls.
