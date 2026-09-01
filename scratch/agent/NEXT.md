# NEXT work unit — qualify mixer input load before allocate call

HYPOTHESIS-ID: m5-selector-caller-input-boundary

Session 3528 parity-qualified all three `rs_malloc` edges inside
`allocateSongChannelArray` against the retail oracle. The first divergence is
already at the callee's `a1`/`s1` argument: retail `0x561F`, port `0x5622`.
Static inspection identifies the immediate producer in `initN64RspMixer`:
the `lw a1, 0(s1)` at `0x8009192C`, immediately before the direct call at
`0x80091934`.

Next unit: add a regeneration-safe witness after the `0x8009192C` load and
retain the s3528 allocation table, s3527 caller/entry rows, store contexts,
producer/mixer controls, phase controls, and positive controls in one build.
Run the canonical real-audio/LLE/spin-yield/autopilot port arm and the retail
oracle with whole-RDRAM control plus phase-gated watches at `0x8009192C` and
`0x80091934`.

Competing hypotheses and discriminator:

- `H-InputLoadDivergence`: retail and port differ immediately after the
  `0x8009192C` load, selecting the load's source field or its writer.
- `H-InputLoadParity`: the loaded value matches but differs before the call,
  selecting an intervening generated instruction or wrapper contract.
- `H-CaptureInvalid`: a same-run positive control or title/hangar phase bucket
  is absent; no comparison is valid.

The discriminating table is phase-keyed title 1024/hangar 512 rows for the
load result, the direct-call arguments, allocate entry `a1`, both selector
stores, and the existing controls. A differing load result selects the
caller-input producer; a matching load and call but differing entry selects
the call/ABI boundary; matching entry moves the search to the load's source
writer. Do not rewrite audio, selector, task, or output state.

Before building, enumerate the load and call PCs from the generated source
and add the witness to `fixup_game_funcs.py` plus a bounded host hook. Build
once with `cmake --build build --config Debug --target RogueSquadron64Recomp`.
Run from `build/` with `ROGUESQ_AUDIO_UCODE=1`,
`ROGUESQ_LLE_FORCE=1`, `ROGUESQ_SPIN_YIELD=1`, `ROGUESQ_LLE_UNGATED=1`,
`ROGUESQ_LLE_SOLO=1`, `ROGUESQ_STUB_MISSING_FUNCS=1`,
`ROGUESQ_AUTOPILOT='3:start,6:start,9:start,12:start,16:a,20:a,24:start,28:a'`,
`PROBE_PHASE_WIDTH=1024`, `PROBE_PHASE_TIMEOUT=180`,
`PROBE_KEYS_FROM_PHASE=1`, `PROBE_LEAVE_OK=1`, and space-delimited
`PROBE_KEYS='6:start 11:start 16:start 21:start 26:start 31:start 36:start 41:start 46:start 51:start 56:start'`.
Capture under `scratch/agent/s3529_selector_input_port/run.log` and SIGKILL
the game.
