# Next work unit: repair the clear-object/I-edge witness

HYPOTHESIS-ID: m5-clear-object-edge-join

The s3777 image-only capture was qualified: the oracle control, six
family-store controls, writer-setup control, title VI, and hangar VI all fired.
However, the two writer-setup rows at `0x8008F2CC` had `a2=0`, `alloc_len=0`,
and `clear_obj=0`, while family-edge rows remained absent. This is an
unevaluable witness, not evidence of an alternate legitimate object.

Competing hypotheses and the discriminator:

- H1: `0x8008F2CC` is the actual clear/allocator boundary, but the witness
  observes the wrong generated register mapping; a corrected witness will
  record a nonzero destination and length and join the family stores.
- H2: the clear/allocator is a different generated callsite or predecessor;
  the current edge is only a later setup call; an allocator/clear-boundary
  witness will record the real object, while the current edge remains zero.
- H3: family entry instrumentation is not installed on the executed generated
  bodies; a positive family-edge control will remain absent even after the
  clear witness is corrected.

The discriminating measurement is one same-build image/oracle capture with a
nonzero clear-object record, family-edge controls, family-edge rows, family
store destinations, and both target VIs. A nonzero object joining stores
selects H1/H2 according to callsite identity; a qualified run with no edge
control selects H3. Missing rows remain unevaluable.

Exact commands:

    rg -n "8008F2CC|rs_memset|m5_writer_setup_state|m5_family_entry" src tools build RecompiledFuncs 2>/dev/null
    sed -n '400,710p' src/main/main.cpp
    cmake --build build --config Debug --target RogueSquadron64Recomp
    zsh scratch/agent/run_s3773_m5_image_only.sh

Make the witness change regeneration-safe through the existing fixup tool,
then rebuild and run the capture once. Do not suppress or replace the clear,
inject values, or change an audio gate.
