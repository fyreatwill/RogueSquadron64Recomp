# NEXT work unit — qualify the pre-title heap failure

HYPOTHESIS-ID: m5-pretitle-heap-failure

Use the generated body around `heapFreeListDequeue` and its callers to identify
the exact operation at guest PC `0x8000D704`, then add one regeneration-safe,
phase-scoped caller/state witness. Run one canonical real-audio/LLE/spin-yield/
autopilot capture after the role map is complete.

Competing hypotheses and the discriminator:

- `H-HeapStateLegitimate`: the freelist operation receives valid state and the
  crash is a later route/runtime issue.
- `H-HeapStateCorrupt`: a mapped writer leaves an invalid freelist link or
  count immediately before `0x8000D704`; that writer is next.
- `H-HeapRoleUnknown`: the generated body cannot identify the operation or
  state fields; move to the exact dereference without classifying heap state.

The single discriminating table is the heap-entry/state witness plus the
existing positive control and VI/crash markers. Each row must identify the
guest PC, caller edge, freelist head/node fields, mappedness, and first
contract violation. A valid-state row selects the later runtime path; an
invalid-state row selects its mapped writer; an unclassifiable row moves to the
exact dereference.

Before building, inspect the generated body and all callers of
`heapFreeListDequeue` at `0x8000D704`; update the regeneration hook in
`/Users/williambuckley/Documents/Tools/N64Recomp/fixup_game_funcs.py`.
Then run the normal make_elf -> N64Recomp -> fixup -> cmake order and capture
under `scratch/agent/s3551_m5_heap_failure/`, with SIGKILL cleanup. Do not
change heap, audio, PCM, image-task, output, or texture-record writes.
