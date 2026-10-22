# NEXT (s5912): shadowing vs no-crossing for the 12 never-struck class-1 ids

HYPOTHESIS-ID: g1-mission-progression

s5911 (static): msg-5 post = nearest-t sphere hit in audioCueDispatcherNpcHandler loop 0x8005D1C8; no id filter.
Hypotheses: H-shadow (a nearer class-0/2 sphere wins on bolts that also cross an unhit class-1 sphere); H-nocross (no bolt segment ever intersects those spheres: aim/elevation); H-thresh (t > float@0x8003B03C so crossings are lock-on only, flag 0x200).
Discriminator: one hook at the stage-3 site (rs5833_ev stage 3) logging for every sphere hit: cand id, class, t, and at loop end winner id + t + threshold; tally per unhit class-1 id: crossings, wins, lost-to-nearer, t>thresh. Control: killed ids (18,19,1B..) must show wins. Also print the two threshold floats read from rdram.
