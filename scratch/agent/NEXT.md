# NEXT work unit — qualify setup-writer source/return contract

HYPOTHESIS-ID: m5-selector-setup-writer-contract

Session 3530 selected the qualified setup writer `0x80091CC8`: the port writes
`0x5622` to `MEM_W(0x80165ED0)` in title/hangar before the load, while retail's
independent writer census includes that PC and its qualified load is `0x561F`.
The retail writer value was not dumped, so writer-value parity remains open.

Next unit: instrument the complete source/return contract feeding
`reapplyAudioConfig`/`0x80091CC8` in one phase-keyed table. Retain the source
writer, `0x80091CC8` store, input load `0x8009192C`, direct call, entry,
allocator, producer-context, selector stores, phase, and positive controls.
Use the retail oracle's whole-RDRAM control, target write watch, and watched
execution/source fields if available; do not repeat the same store-only census.

Competing hypotheses and discriminator:

- `H-SetupWriterSourceDivergence`: source arguments or return differ before
  `0x80091CC8`, selecting that producer/contract.
- `H-SetupWriterSourceParity`: source and return match but the port store value
  still differs, selecting an intervening generated instruction or ABI edge.
- `H-CaptureInvalid`: a positive control or title/hangar bucket is absent; the
  join is unevaluable.

Before building, enumerate the generated callers and source computations for
`reapplyAudioConfig` and the `osAiSetFrequency_recomp` return. Add only a
regeneration-safe witness to `../N64Recomp/fixup_game_funcs.py` plus its host
hook. Build with:
`cmake --build build --config Debug --target RogueSquadron64Recomp`.

Run from `build/` with the validated real-audio/LLE/spin-yield/autopilot
variables, `PROBE_PHASE_WIDTH=1024`, `PROBE_KEYS_FROM_PHASE=1`, and all
existing selector controls plus the new contract control. Capture under
`scratch/agent/s3531_selector_setup_contract/run.log`; SIGKILL the game.
Do not rewrite audio, selector, task, or output state.
