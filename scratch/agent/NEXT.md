# NEXT work unit (s2880) — m5-audio-plan

HYPOTHESIS-ID: m5-audio-destub-plan

## Work unit

Create the first M5 design document, `docs/M5-AUDIO-PLAN.md`. Survey every
audio stub, trap, early return, disabled ucode path, and host-side gate that is
currently active. Separate the Factor 5 image/audio-RSP arm from the CPU MORT
speech boundary, then define a strictly incremental de-stubbing sequence with
one validation soak and positive control per step. This is documentation and
design only; do not change runtime behavior or build the game.

## Competing hypotheses and discriminator

- H-degenerate-audio: the active stubs and traps create degenerate paths that
  plausibly account for the recurring audio crash families.
- H-independent-audio: the current guards are not on the relevant contracts;
  de-stubbing audio would not address the observed failures.
- H-mixed-contracts: image-stage and CPU MORT paths have separate blockers and
  require separate validation gates.

The discriminating deliverable is an exhaustive table mapping each active
stub/trap/gate to its caller or task path, contract status, expected legitimate
writer/producer, safe first change, positive control, phase gate, and failure
signal. A row without a named contract edge remains blocked and is not a
candidate for implementation. The document must also state the exact soak
recipe and expected outcomes for each proposed step.

## Exact next commands

1. `rg -n "aspMain|musyx|MORT|AUDIO_UCODE|audio|PCM|voice|Broke|stub|trap|waitForAnyAudioSlot|filterVoiceSampleBlock" src lib tools /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_*.c`
2. Inspect bounded source windows for every hit and read the existing M5
   artifacts referenced by `docs/CURRENT-TRUTH.md`.
3. Write `docs/M5-AUDIO-PLAN.md`, run `git diff --check`, and do not build or
   launch the game in this iteration.
