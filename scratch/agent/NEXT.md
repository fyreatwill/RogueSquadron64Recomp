# Next: discriminate the jagged far-terrain edge with one fixed-camera arm table
HYPOTHESIS-ID: g3c-owner-visual

Completed this unit (s6292): `tools/g3c_jerk.py` on all four phase-gated arms. Retail
sign-alternation=0.395, FPS60=0.625, wide=0.384, FPS60+wide=0.632; each arm had
thousands of `[g3c]` records and zero crash markers. This selects H-fps60 for the
turn shake; aspect alone is not causal. The next G3c defect is the blocky
far-terrain edge.

Before building, write the competing hypotheses and discriminator into the session
ledger: H-fade (haze/fog end is not scaled with draw distance), H-radius (terrain
visibility radius exposes a grid boundary), H-aspect (wide frustum exposes a side
edge), and H-retail (the edge is present at retail). Build one instrument carrying
the fixed-camera framebuffer dump/scorer and run retail, DD2, DD3, ASPECT, and
DD3+ASPECT arms in the same phase-gated recipe. The discriminating measurement is
the outer-edge pixel profile against the haze colour: retail edge absent + DD-only
edge selects H-fade/H-radius; wide-only edge selects H-aspect; edge present in
retail selects H-retail. Positive control: terrain scorer must report nonzero
terrain fraction and every arm must produce a framebuffer dump.

Exact commands: create the five-arm recipe under `scratch/agent/soak_queue/`,
run it from the repo root with the existing level-1 fixed-camera route, then use
`python3 -I tools/g1c_fixed_score.py <run-dir>` and a contact sheet. Keep the
default retail settings unchanged. If the edge measurement is positive, name the
writer/constant before proposing a fog or outer-ring fix.
