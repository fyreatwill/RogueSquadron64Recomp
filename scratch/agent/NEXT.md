# NEXT work unit — qualify the producer/context edge after mixer entry

HYPOTHESIS-ID: m5-selector-store-caller-boundary

Session 3527 completed the caller/route census: startup controls fired, title
1024 and hangar 512 were reached, and the target entry plus producer/store
contexts fired. The known caller, route, and AI-boundary rows were absent in
hangar; entry `$ra` was `0`, so alternate caller versus route gate remains
unresolved. The new table showed `reapplyAudioConfig` → `initN64RspMixer` →
the sole `allocateSongChannelArray` call in hangar, with matching arguments;
`initAudioSubsystem` was absent in hangar. The generated caller/route gate is
therefore no longer the active discriminator. See
`docs/M5-S3527-SELECTOR-MIXER-CALLERS.md`.

Next unit: add one regeneration-safe witness at the next producer/context
edge after `initN64RspMixer` entry and before the two selector stores. First
enumerate that function's generated callsites and the immediate context
predecessors in the source; write all competing hypotheses and the split
outcomes here before building. Retain the three s3527 caller rows, the
entry/store/producer/mixer controls, and the retail-range/phase controls in
one build and run the canonical real-audio/LLE/spin-yield/autopilot arm.

Expected discriminator: a hangar row with a changed producer argument/context
selects that producer edge; a matching row through the next witness selects a
later mutation; absent startup or phase controls makes the comparison invalid.
Do not repeat the s3527 caller census unchanged and do not rewrite audio or
selector state.

Competing hypotheses and discriminator:

- `H-StoreCallerAlternate`: a hangar callsite row exists without the known
  route row, selecting an alternate caller or indirect path.
- `H-StoreCallerGate`: a route-edge row exists while the known callsite row is
  absent, selecting the enclosing gate.
- `H-StoreCallerParity`: callsite and route rows match, selecting a later
  internal mismatch.
- `H-CaptureInvalid`: startup controls or title/hangar phase rows are absent;
  no comparison is valid.

The discriminating table is phase-gated title 1024/hangar 512 rows for every
generated direct callsite of `allocateSongChannelArray`, its enclosing route
edge, the existing entry (`pc=0x8008F000`, `$ra`, `a0..a3`), both store
contexts, producer context, mixer entry, known route, and AI boundary. Build
all callsite and route arms in one build and run the canonical real-audio arm
once. A same-run positive control must fire before interpreting null rows.
Use `ROGUESQ_LLE_FORCE=1`, `ROGUESQ_SPIN_YIELD=1`,
`ROGUESQ_LLE_UNGATED=1`, `ROGUESQ_LLE_SOLO=1`,
`ROGUESQ_STUB_MISSING_FUNCS=1`, the documented autopilot, and
`ROGUESQ_AUDIO_UCODE=1`. Do not rewrite audio or selector state.

Before building, enumerate the callsites from the generated source and record
the hypotheses and outcome table above in the regeneration-safe probe script.
Build once, run once, and capture under
`scratch/agent/s3527_selector_callers_port.log`; SIGKILL the game.
