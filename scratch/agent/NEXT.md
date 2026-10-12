# NEXT: audit M5 Step 5 key-on early returns as one complete idiom class
HYPOTHESIS-ID: m5-audio-destub

Step 4 is qualified in s4677; do not repeat the `0x80094648` run. Before
building, read the Step 5 row in `docs/M5-AUDIO-PLAN.md`, enumerate all eight
key-on early-return sites in the fixup/generated pipeline, and identify the
descriptor/divisor writers and invalid-input fallback.

Competing hypotheses:

- H-keyon-valid: valid descriptors/divisors reach the normal key-on tail and
  the early returns are stale port-only safety exits.
- H-keyon-invalid: at least one descriptor/divisor is legitimately invalid and
  the early return is required; removing it would expose a real trap.
- H-keyon-upstream: descriptors/divisors are valid, but an upstream writer or
  source differs and the returns are only a downstream symptom.

Discriminating measurement: one static census plus one batched hangar run with
all eight sites instrumented in one build. Record descriptor validity, divisor,
site, normal-tail entry, slot `02`/`00` transition, and invalid-input control;
the whole-RDRAM/route controls must fire. Valid descriptors with normal tails
select H-keyon-valid; a site-specific invalid descriptor with matching writer
evidence selects H-keyon-invalid; valid inputs with a first upstream mismatch
select H-keyon-upstream. No early return may be removed from this unit.

Exact starting commands:

    rg -n -C 4 '0x80090CEC|0x80090D04|0x80090D30|0x80090D48|0x80090D74|0x80090D8C|0x80090DB8|0x80090DD0' tools/fixup_game_funcs_vendored.py docs/M5-AUDIO-PLAN.md
    cmake --build build -j8
    zsh scratch/agent/s4264_gate.sh

Adapt the recipe only by adding the Step 4 writer/value controls and use
SIGKILL for cleanup. Report the comparison in the session entry; do not spend
a separate build on each counter.
