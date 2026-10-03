# Next work unit: validate one-shot SP-yield control against default audio arm

HYPOTHESIS-ID: m5-sp-yield-one-shot-control

The runtime change in session 3797 is landed and built. Do one phase-gated
validation run; do not add another instrument or alter the audio contract.

Competing hypotheses and discriminator:

- H1: repeated request-only polling caused the scheduler retry loop. The
  request-only arm reports `returned=1` once, then `pending_after=0`, and the
  default arm remains completion-wins (`returned=0`).
- H2: the scheduler hang is elsewhere. The request-only arm still reaches
  `pending_after=0`, but route progress is unchanged from the default arm.
- H3: the change is not exercised. No `[sp-yielded-ab]` rows or no positive
  `[sp-yield-reset]` rows means the run is invalid, not evidence for H1/H2.

The discriminating measurement is one same-build, phase-gated A/B run with
the default arm and `ROGUESQ_SP_YIELDED_REQUEST_ONLY=1`, collecting the
request/return/pending fields plus E60/E70/E80F and title/hangar transitions.

Commands:

    cmake --build build --config Debug --target RogueSquadron64Recomp
    env ROGUESQ_LOG_SP_YIELDED_AB=1 ROGUESQ_LOG_ALL=1 zsh tools/run_m5_yield_ab.sh

If the helper is absent, create one self-contained capture script before
running; it must launch from `build/`, use SIGKILL, and capture both arms in
one run. Do not resume the rename sweep until this validation selects or
refutes H1 with both controls positive.
