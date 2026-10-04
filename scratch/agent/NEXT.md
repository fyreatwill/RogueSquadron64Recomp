# Next work unit: M5 bounded retail candidate-writer census

HYPOTHESIS-ID: m5-candidate-writer-census

Run the next adjacent retail candidate set `0x800051BC`, `0x800051C0`, and
`0x800051C4`. Use the existing same-build retail/port driver; keep the
qualified port route on the legacy audio-DMA rollback because s3977's declared
size arm crashed before title.

Competing hypotheses:

- H1: one of the three PCs executes in a qualified target phase and joins the
  image-stage scalar payload.
- H2: none executes, but controls and independent post-store rows pass.
- H3: a control or target phase fails, so this PC class is unevaluable.

Discriminator: the independent whole-RDRAM control, retail title/hangar phases,
oracle completion, and paired port controls must all pass in one run. H1 is
selected only by a candidate execution plus matching post-store/payload join;
H2 by zero candidate rows with all controls intact; H3 by any lost control or
target phase.

Commands:

    cmake --build build --config Debug --target RogueSquadron64Recomp
    zsh scratch/agent/run_s3976_m5_candidate_writers.sh

The wrapper now transforms the direct s3967 recipe (not another wrapper) for
this adjacent set. Record the independent controls and candidate rows before
deciding H1/H2/H3.
