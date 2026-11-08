# NEXT: G5f leftover — knife lines shorter than 60 px, and s6895's dd1 small transients (306 vs 157)
HYPOTHESIS-ID: g5f-short-lines
Context: s6906 made W_CLAMP + W_SHEET_PX=200 default on at every dd; detector tools/g5f_lines.cpp stops at runs >= 60 px, and
clamped triangles spanning <= 200 px stay drawn. s6895's dd1 small transients (306 vs 157) were never explained.
Owner bar (G5f): spike count at the owner recipe with no new missing geometry. Short wedges may be what the owner still sees.
Hypotheses:
- H-sheet: short lines are W<=0 wedges under the 200 px W_SHEET_PX cut (clamped but kept). Lowering W_SHEET_PX removes them.
- H-real: they are real thin geometry (cloud/terrain edges, bolts), unchanged by any W lever.
- H-other: an RDP-side path (thin triangles inside the cull bound) that W levers do not touch.
Discriminator, ONE build, ONE run: LEVEL=4 dd4 16:9 FPS60 (owner recipe), same-run toggle of W_SHEET_PX 200 vs 40
(add =tog in lib/rt64 rt64_gbi_rdp.cpp like W_CLAMP=tog if absent; export patches), capture with g5f_lines at min run 20 px
plus in-memory injection control (must fire >= 85%). Bucket line events 20-39 / 40-59 / 60-99 by block. H-sheet: on-block
(40) drops 20-59 px lines vs 200; H-real: equal; then view 6 frames each. Flip-diff MAD both directions for missing geometry.
Commands: scratch/s6906 arm scripts (copy to scratch/s7002), tools/g5f_lines.cpp, tools/g5f_flip_diff.cpp.
