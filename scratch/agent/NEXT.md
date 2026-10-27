# NEXT: G1c phase 2 — why does terrain vanish at dd3/dd4?
HYPOTHESIS-ID: g1c-dd-phase2
Evidence (s6413): pinned, position-matched lvl1 frames: dd1/dd2 draw the near mountain, dd3/dd4 draw none (view/s6413/sheet2.png).
Hypotheses: H-chunk (display-list chunk supply exhausted at dd>=3, terrain DLs dropped), H-pool (terrain tile pool/grid dims s6035 overflow or wrap), H-cap (ucode iteration cap / tri budget hit; cap already 65536 at dd>1), H-cull (far/near clip scaled wrongly so near tiles culled).
Discriminator: one build, reuse tools/ s6412_attpin recipe (dd1,dd2,dd3,dd4), log per VI in flight: DL chunk alloc count/fail count, terrain tiles submitted, tri count, ucode cap fires. Positive control: dd1 vs dd2 tri count rises. Whichever counter diverges at dd3 selects the hypothesis; fix its root cause (grow arena above 0x80800000 per G1c phase 2 plan) rather than guarding.
