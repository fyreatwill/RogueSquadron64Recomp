# NEXT: G1c extended draw distance - find WHICH limit applies (discriminator first)
HYPOTHESIS-ID: g1c-draw-distance
G1b closed (s6017): baseline lvl1 post-fix = 0 slow seconds, mean sd_wall 10.3 ms, tasks/s 30.2.
Hypotheses (see iteration prompt G1c): L-fade (haze baked in shade/combiner; re-test ROGUESQ_FORCE_FOG in flight), L-radius (terrain tile visibility radius / far clip constant), L-lod (detail index 0x80137CE4, selectMeshLodAndSubmitForRender / setObjectDetailLevel), L-budget (DL/vertex/tile buffer caps).
Discriminator: fixed-camera lvl1 framebuffer, measure distant-terrain pixel fraction while perturbing ONE lever per arm in the same build (env-gated): fog off, radius const x2, lod index forced 0, then check budget overflow counters. Positive control: an arm that visibly changes the distant fraction (e.g. force-hide terrain) must fire. Build all arms in one iteration (iron rule 13), run as queued soaks with G1B=1 on.
First step: grep for terrain visibility radius / far-clip consts and 0x80137CE4 readers in recompiled code; write the arm list here, then implement env hooks in a fixup script.
