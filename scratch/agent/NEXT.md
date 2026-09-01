# NEXT work unit — implement actual AI-frequency return semantics

HYPOTHESIS-ID: m5-ai-frequency-contract-fix

Session 3534 resolved the split from the retail ELF: `osAiSetFrequency`
returns `osViClock / round(osViClock / frequency)`, so `0x5622` maps to
`0x561F` at the NTSC clock. The host implementation currently returns its
input.

Next unit: make the regeneration-safe host implementation match that actual
frequency contract, then build and run the qualified real-audio route. Do not
change selector/task/output state.

Competing hypotheses and discriminator:

- `H-ContractFix`: the standard actual-frequency calculation makes the port
  setup return `0x561F` for `0x5622` and preserves title/hangar reachability.
- `H-AudioAbstractionMismatch`: the calculation is right but the runtime's
  audio-register abstraction requires a different clock/register treatment;
  the returned value or route will diverge.
- `H-RouteRegression`: the contract fix changes audio lifecycle behavior and
  causes a new pre-title/target-route failure.
- `H-CaptureInvalid`: startup positive control or title/hangar phase witness
  is absent; no route conclusion is allowed.

Required discriminator: one same-build run with the startup control plus
phase-keyed setup rows. `H-ContractFix` requires target rows showing input
`0x5622` and return/store `0x561F`, with title 1024 and hangar 512 reached;
the other outcomes select the corresponding hypothesis above.

Build/run shape: edit `lib/N64ModernRuntime/librecomp/src/ai.cpp`, export
`./submodule-patches/export.sh`, build the normal Debug target, then use the
existing real-audio LLE/spin-yield/autopilot recipe with all passive
breadcrumbs. Do not repeat the silent arm.
