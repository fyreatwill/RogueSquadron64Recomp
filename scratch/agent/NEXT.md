# Next work unit: install and qualify the missing family-edge witness

HYPOTHESIS-ID: m5-family-edge-hook

The s3778 image-only capture was qualified: the oracle control, six
family-store controls, repaired writer-setup control, title VI, and hangar VI
all fired. The corrected row joined `0x8008F2CC` to clear object
`0x801797B0` with `a2=0x298`. Family-edge controls and rows were absent even
though family-store controls were positive.

Competing hypotheses and the discriminator:

- H1: the family-entry hook is absent from the generated bodies; adding it will
  produce positive family-edge controls and rows.
- H2: the hook exists but is attached to the wrong generated functions or
  argument mapping; a corrected hook will produce controls and rows showing
  the route/object relationship.
- H3: the family bodies execute, but no target-relevant entry edge exists; a
  qualified hook will control-fire without target edge rows.

The discriminating measurement is one same-build image/oracle capture with the
repaired clear-object row, six family-store controls, family-edge controls,
family-edge rows, family-store destinations, and both target VIs. Source
inspection proving no hook exists selects H1; a qualified edge control with
rows selects H2 or H3 by destination; missing controls remain unevaluable.

Exact commands:

    rg -n "rs64_m5_family_entry|m5-family-edge|rs64_m5_family_store" /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs tools
    sed -n '460,550p' src/main/main.cpp
    sed -n '1,180p' tools/apply_s3740_m5_family_provenance.py
    cmake --build build --config Debug --target RogueSquadron64Recomp
    zsh scratch/agent/run_s3773_m5_image_only.sh

Make the family-entry hook regeneration-safe through a fixup tool, then rebuild
and run the capture once. Do not suppress or replace the clear, inject values,
or change an audio gate.
