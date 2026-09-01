# NEXT work unit — enumerate selector entry callers and route edge

HYPOTHESIS-ID: m5-selector-store-caller-boundary

Session 3526 requalified the real-audio route: startup controls fired, title
1024 and hangar 512 were reached, and the target entry plus producer/store
contexts fired. The known caller, route, and AI-boundary rows were absent in
hangar; entry `$ra` was `0`, so alternate caller versus route gate remains
unresolved.

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
