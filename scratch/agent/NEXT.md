# NEXT work unit — identify the heap-dequeue caller/path split

HYPOTHESIS-ID: m5-pretitle-heap-caller-route

Add one regeneration-safe, phase-scoped caller table at generated callsites
`0x800104A8` and `0x80010CD8`, recording callsite, phase, entry ordinal, and
the caller's relevant arguments immediately before `heapFreeListDequeue`.
Join it to the existing `[heap-dequeue-entry]` and positive-control rows in
one canonical real-audio/LLE/spin-yield/autopilot capture. Update the
regeneration hook in `/Users/williambuckley/Documents/Tools/N64Recomp/fixup_game_funcs.py`,
then run make_elf -> N64Recomp -> fixup -> cmake.

Competing hypotheses and the discriminator:

- `H-CallerA`: edge `0x800104A8` supplies the entries and its route explains the absent store path.
- `H-CallerB`: edge `0x80010CD8` supplies the entries and its route explains the absent store path.
- `H-AlternatePath`: neither known edge accounts for the target entries; an indirect/non-generated route remains.
- `H-BranchReaches`: a joined caller row reaches a taken branch/store; return to classifying its node/state.

The single discriminating table is the caller-edge row joined by ordinal to
the existing entry witness, with the same positive control and VI/crash
markers. Rows at `0x800104A8` select H-CallerA; rows at `0x80010CD8` select
H-CallerB; entry rows with neither edge select H-AlternatePath; a taken store
row selects H-BranchReaches. Missing controls make the capture invalid.

Capture under `scratch/agent/s3553_m5_heap_caller/` with SIGKILL cleanup. Do not change
heap, audio, PCM, image-task, output, or texture-record writes.
