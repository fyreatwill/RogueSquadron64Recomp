# Next work unit: make SP-yield validation stable without changing the contract

HYPOTHESIS-ID: m5-sp-yield-one-shot-control

The runtime change in session 3797 is landed and built. The s3798 corrected
validation was coverage-invalid: default stopped before phase 640 and the
request-only arm crashed 36 times before its positive control. Design one
stability-preserving same-build capture using the existing harness diagnostics;
do not alter the runtime contract or add a new counter.

Competing hypotheses and discriminator:

- H1: repeated request-only polling caused the scheduler retry loop. Both arms
  reach phase 640; request-only reports `returned=1` once then
  `pending_after=0`, default remains completion-wins, and lifecycle progress
  can be compared.
- H2: the scheduler hang is elsewhere. Both controls are positive, but route
  and title/hangar progress remain unchanged between arms.
- H3: arm stability/coverage is still the blocker. Missing phase/control rows
  or a pre-control crash makes the run invalid, not evidence for H1/H2.

The discriminating measurement is one same-build, phase-gated A/B run with
both positive controls: default reset/completion-wins and request-only
one-shot/pending-after-zero, plus E60/E70/E80F and title/hangar transitions.

Commands:

    cmake --build build --config Debug --target RogueSquadron64Recomp
    zsh tools/run_m5_yield_ab.sh

The helper launches both arms from `build/`, uses SIGKILL cleanup, and writes
`scratch/agent/m5_yield_ab/driver.log`. Do not resume the rename sweep until
this validation selects or refutes H1 with both controls positive.
