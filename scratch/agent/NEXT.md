# Next work unit: classify the next bounded M5 candidate-writer class

HYPOTHESIS-ID: m5-candidate-writer-sweep

The M3 validation unit remains externally unavailable: the configured build
has no `PatchesLib` target and the MIPS toolchain is absent. Resume the
ground-truth-qualified M5 census at the next three unclassified retail PCs:
`0x8000518C`, `0x80005190`, and `0x80005194`. Build all controls and
candidates together, then run the paired retail oracle and port route in the
phase-gated recipe.

Competing hypotheses:

- H1: at least one candidate executes in a qualified retail target phase and
  is a writer for the target image-stage value.
- H2: a candidate executes, but its stores are unrelated to the qualified
  target image-stage payload.
- H3: none of these candidate PCs executes in the qualified target phase; the
  class is not the retail writer at this measured scope.

Discriminator: the same run must show the independent whole-RDRAM oracle
positive control, title VI 1024, hangar VI 512, post-store scalar controls,
and candidate execution/post-target rows. H1 requires a candidate row joined
to the target phase and payload; H2 requires candidate execution without that
join; H3 requires zero target-phase execution, post-target rows, and scalar
samples for all three candidates.

Commands:

    cmake --build build --config Debug --target RogueSquadron64Recomp
    zsh scratch/agent/run_s3970_m5_candidate_writers.sh

The harness must preserve the independent whole-RDRAM positive control and
`ROGUESQ_AUDIO_UCODE=1`, and terminate both processes with SIGKILL.
