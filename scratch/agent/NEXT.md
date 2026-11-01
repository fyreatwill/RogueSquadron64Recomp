# NEXT: G3 render fidelity -- edge audit of the other three borders (left col 0, top row, bottom row) with one reach table
HYPOTHESIS-ID: g3-edge-reach-audit

s6736 showed that the game's content draws never reach source column cw-1. Only the fill-mode clear does, and that column showed the
sky colour at the right edge until the s6736 content-reach trim. The same class may exist on the other borders: a bottom
row (y = height-1) or top/left line holding only the clear colour or stale bytes. (s6735's horizontal line was a present-
target substitution, not this class.)
Hypotheses: H-none (content covers col 0 and rows 0/h-1 on every screen); H-bottom (triangle yl stops at h-1.00, so the
last row shows the clear, as the right column did); H-left (x0 min > 0 on some screens).
Discriminator, one build: extend `[g1d-reach]` (src/rsp/dpc_bridge.cpp rs64_g1d_pillar_scan) with min content x0, min
y0 and max y1 per epoch and colour width (triangles: yh/yl; rects: y fields; same inclusive/exclusive rules as s6736's
x reach, i.e. copy/fill rects inclusive, fill-mode fill rects excluded as the clear). Take the colour-image height from the VI
height or the scissor yl. One run of scratch/s6736/dense.sh (r-tag) plus offline edge scan of the captures (border rows
and columns of the 4:3 content rect vs their inner neighbours, like scratch/s6736/edge.py). If a border is clear-only,
extend the trim to it (display-only, knob default on, =0 old) and run fix vs ctl arms in the same iteration.
Then: G3 in-flight frame diffs against the retail lvl1 oracle frame; G1d close-out still awaits the owner's judgement.
