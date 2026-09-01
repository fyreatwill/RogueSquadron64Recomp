# NEXT work unit — join the cached-head branch to the heap failure

HYPOTHESIS-ID: m5-pretitle-heap-failure

Add one regeneration-safe, phase-scoped table around the cached-head path:
record the `0x8000D6F4` loaded head, `0x8000D700` taken/not-taken outcome,
`0x8000D704` node when taken, and both caller edges. Run one canonical
real-audio/LLE/spin-yield/autopilot capture.

Competing hypotheses and the discriminator:

- `H-HeapStateLegitimate`: the branch/store executes with valid state; the crash is later.
- `H-HeapStateCorrupt`: the branch/store executes with invalid state; trace its writer.
- `H-HeapPathAbsent`: entry occurs but the store path is never taken; move to its predecessor/caller route.

The single discriminating table is the joined load/branch/store witness plus
the existing positive control and VI/crash markers. A valid taken row selects
the later path; an invalid taken row selects its writer; zero taken rows with
entry activity select the branch predecessor/caller route.

Before building, update the regeneration hook in
`/Users/williambuckley/Documents/Tools/N64Recomp/fixup_game_funcs.py`, then run
make_elf -> N64Recomp -> fixup -> cmake. Capture under
`scratch/agent/s3552_m5_heap_branch/` with SIGKILL cleanup. Do not change
heap, audio, PCM, image-task, output, or texture-record writes.
