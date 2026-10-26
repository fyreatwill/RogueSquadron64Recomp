# Next: name the terrain-edge writer before proposing a fix
HYPOTHESIS-ID: g3c-owner-visual

Completed s6293: the five-arm edge table passed controls and produced an
aspect-only lead, but retail's transient p90 and the shared framebuffer source
make H-aspect provisional. Do not rerun the same arm table.

One bounded work unit: static-enumerate the terrain visibility/fog writers that
can differ under `ROGUESQ_DRAW_DISTANCE` or `ROGUESQ_ASPECT`, then instrument
only the highest-ranked candidate in one phase-gated build/run. Competing
hypotheses are H-aspect (frustum/viewport widening exposes a side boundary),
H-radius (terrain patch visibility radius is extended or mis-scaled), H-fade
(fog/haze end remains retail while terrain is extended), and H-retail (the
boundary is legitimate). The discriminator is the candidate's guest value and
writer PC in retail versus one changed arm: an aspect-only change with unchanged
radius/fog values selects H-aspect; changed radius with unchanged fog selects
H-radius; changed fog end/start selects H-fade; identical values and a retail
matching edge select H-retail. Positive controls: the candidate log must fire in
retail and opt-in flight phases, and the framebuffer edge scorer must remain
nonzero in both arms.

Static commands:

    rg -n "0x80132DB0|0x80132DB4|0x80132DB8|0x80132DBC|fog|Fog|far|radius|DRAW_DISTANCE|ASPECT_SCALE|guPerspective" tools src RecompiledPatches
    rg -n "setObjectDetailLevel|selectMeshLodAndSubmitForRender|terrain|visibility" RecompiledFuncs/funcs_*.c tools/fixup_game_funcs*.py

Then add one env-gated log at the highest-confidence generated writer/fixup
site, rebuild the normal target, and run retail plus `ROGUESQ_ASPECT=21:9
ROGUESQ_OSMEM_MB=12` in one phase-gated recipe. Record the writer PC, value,
and arm table; do not add a fog/radius mitigation in this unit.
