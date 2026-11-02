# NEXT: s6736 right-edge sky column under ROGUESQ_EXACT_EDGES (G3 cinematic follow-up)
HYPOTHESIS-ID: g3-cinematic-sweep

State: s6795 closed the TRI flag on shots 48/64 (frame weighting; tools/g3_cine_tri.py). s6794 added the exact-edge
fan in RT64 (ROGUESQ_EXACT_EDGES default on; =tog alternates off/on per 1 s of epoch time, on = odd second).
s6736 found the right-edge sky column = source column cw-1 holds the game's fill-mode clear because every content tri/rect
stops at x = cw-1.00 exclusive; ROGUESQ_G1D_EDGE_CONTENT (default 1) crops it at display time.

Question: does the exact-edge fan change what RT64 draws into column cw-1 (it changed edge sampling at x=318)?
Hypotheses:
- H-same: column cw-1 still holds the clear colour under EXACT_EDGES on and off (crop still needed, still correct).
- H-fan-fills: with exact edges, triangles ending at x = cw-1.00 now light column cw-1 (crop now hides real content; consider
  turning EDGE_CONTENT off when EXACT_EDGES is on).
- H-fan-new-line: exact edges leave a NEW unsampled column elsewhere at the right edge (another seam).
Discriminator, ONE run: scratch/s6736/dense.sh recipe (lvl1 forced route, 4:3) with ROGUESQ_EXACT_EDGES=tog and
ROGUESQ_G1D_EDGE_CONTENT=0 (so the raw column is visible), scorer scratch/s6736/edge.py split by odd/even epoch second.
Per arm (on vs off seconds of the same run): briefing/flight frames with the sky edge column, and load frames with the line.
Positive control: the off seconds must reproduce s6736 ctl (~70% of briefing/flight frames show the column).
Outcomes: on == off -> H-same, close; on < off -> H-fan-fills; a new column elsewhere -> H-fan-new-line.
