# NEXT work unit — qualify source writer for mixer input

HYPOTHESIS-ID: m5-selector-input-source-boundary

Session 3529 qualified the immediate load: retail loaded `0x561F` and the port
loaded `0x5622`, with positive controls and downstream allocator/store rows
live. The load reads `MEM_W(0x80165ED0)` through `s1`.

Next unit: enumerate and instrument the writer/source of `0x80165ED0` in one
phase-keyed table, retaining the input-load, call, entry, allocator, store,
producer/mixer, phase, and positive controls. Run the canonical real-audio
port arm and the retail oracle with whole-RDRAM control plus phase-gated
writer/load watches.

Competing hypotheses and discriminator:

- `H-SourceWriterDivergence`: retail and port differ at the writer/source of
  `0x80165ED0`, selecting that edge.
- `H-SourceWriterParity`: source and writer context match, moving the search
  to an intervening memory read or generated instruction.
- `H-CaptureInvalid`: a same-run positive control or title/hangar phase bucket
  is absent; no comparison is valid.

The discriminating table is phase-keyed title 1024/hangar 512 rows for every
writer/source candidate, the load result, direct-call arguments, allocate entry
`a1`, both selector stores, and existing controls. A differing writer value or
PC selects the source edge; matching writer and load values move later. Missing
controls invalidate the join. Do not rewrite audio, selector, task, or output
state.

Before building, enumerate all generated writes to `0x80165ED0` and add the
regeneration-safe witness to `../N64Recomp/fixup_game_funcs.py` plus a bounded
host hook and current-output helper. Build with
`cmake --build build --config Debug --target RogueSquadron64Recomp`.
Run from `build/` with the same real-audio/LLE/spin-yield/autopilot variables
as s3529, retaining all `PROBE_*` phase controls and
`ROGUESQ_LOG_M5_SELECTOR_INPUT=1` plus the existing selector probes. Capture
under `scratch/agent/s3530_selector_input_source_port/run.log` and SIGKILL
the game.
