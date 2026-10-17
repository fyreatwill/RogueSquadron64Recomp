# Next: locate the in-mission stick-state storage via the game's pad consumer (not RDRAM diffing)
HYPOTHESIS-ID: m6-mission-input
H1: game copies OSContPad stick bytes into a fixed struct each frame (readable by tracing the osContGetReadData result consumer). H2: input is consumed in a path our runtime never reaches in mission.
Discriminator: in the recompiled code, find the callers of the pad-read wrapper (grep RecompiledFuncs for the osContGetReadData stub address) and log (once per VI, phase-gated to origin 0x620400) the destination addresses written with stick x/y during a W hold vs no hold, in ONE run with a same-run no-key control.
Do NOT repeat snapshot diffing (s5074: 205k whole-page witnesses). Script run caveat: run.log >1M lines slows `has` greps; mission onset ~260 s, so budget 600 s cap for fewer snaps or use run_in_background with a lighter log level.
