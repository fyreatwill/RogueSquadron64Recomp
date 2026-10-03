# Next work unit: census the remaining retail writers for the M5 image span

HYPOTHESIS-ID: m5-retail-nonzero-producer-census

Session 3858 directly re-confirmed that the M3 patch pipeline is unavailable:
the MIPS compiler/linker, generated N64Recomp executable, and `PatchesLib`
target are all absent. Do not repeat the blocked build until those prerequisites
change. M5 remains the highest-priority applicable unit; session 3857 ruled out
the dominant `0x800078EC` writer as a nonzero image producer.

Competing hypotheses and discriminator:

- H1: another legitimate retail writer produces nonzero bytes in the qualified
  `0x1798B0..0x179A48` hangar span.
- H2: all remaining retail writers to that span are zero-fill or unrelated
  activity, so no nonzero producer exists at the qualified target phase.
- H3: the apparent remaining writer is an attribution/watch artifact; the
  independent whole-RDRAM control or PC/value join fails and the census is
  unevaluable.

The discriminator is one same-run oracle capture that enumerates every PC
writing the span during title/hangar phase, samples the written scalar value,
and joins each writer to a positive whole-RDRAM watch plus both target-VI
controls. H1 requires a phase-gated nonzero writer with an independent PC/value
join; H2 requires complete writer coverage with only zero/unrelated values; H3
is selected if either positive control or the PC/value attribution is missing.
Do not add a writeback guard from H2.

Exact preparation and run shape:

    sed -n '1,220p' docs/F5-UCODE-REFERENCE.md
    rg -n '1798B0|800078EC|retail.*writer|scalar.*store' scratch/agent tools docs
    git status --short
    # Reuse the existing paired retail/port oracle driver after locating its
    # writer-census entrypoint; arm whole-RDRAM, title 1024, and hangar 512
    # controls in the same run, with SIGKILL watchdog termination.

Before building instrumentation, verify the oracle driver is the independent
retail witness and that the positive controls are armed. Batch the complete
remaining-PC/value table in one build/run; do not run a single-PC follow-up.
