# Next: footprint-derived fade centre for G3c(a) jagged far-terrain edge
HYPOTHESIS-ID: g3c-owner-visual
State (s6318): AA94 cell stash (rs64_ef_col/row) works; cells are 64x64 ring-buffer indices (wrap), no world-position float found at 0x80138D20/0x80137DBC (constant garbage).
Hypotheses: H-footprint (visited cells per frame form a contiguous disc mod 64 around the player; its circular mean is the centre and fade by circular distance works without any position source) vs H-needs-world (footprint is irregular/auto-far square so the mean is biased) vs H-none.
Discriminating measurement: add a per-frame marker (VI/frame counter) to the [edgefade5] log, drop cam/pl floats, rerun one lvl1 hold, offline per frame compute circular mean + max circular radius; centre must move smoothly frame to frame while flying (positive control: radius ~constant, centre drift >0).
Then: hook A6C0 epilogue fade with that centre (apply10c f formula), rerun dd3_log vs dd3_fade, score with tools/g3c_edge_score.py, send PNGs to owner.
