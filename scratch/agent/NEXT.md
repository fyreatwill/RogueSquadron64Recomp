# NEXT: why does rs64_g1d_rect_wrap never see the residual wrapped game-DL HUD texrects? (s6850 residual)
HYPOTHESIS-ID: g1d-hudrect-walker-miss

State (s6850): ROGUESQ_G1D_SPRITE_WRAP clamps edge-straddling wrapped texrects (A/B on lvl17; the rewrites show up in
RT64's input bin). Residual: a 3-frame run of game-DL G_TEXRECT (w0 0xE4.., 16x30 px, ul.x ~1012 -> 999 -> 985,
ul.y ~85; lvl17 VI ~11444 and ~11923, also lvl5/lvl9) stays wrapped in the bin, merged record lo=0x6F6000 +0x1F330.
ROGUESQ_G1D_SPRITE_DIAG=1 printed nothing for it (no fix/skip/wrap-at-cw/early-return), so the walker never reads those
words in wrapped form. The bin also has 8-byte per-range records (lo 0x6F6000, 0x6F6008, ...).

Hypotheses (one instrument, one build, one run discriminates):
- H-shadow: the word is submitted through the s4273 per-range wrap flush. record_submit walks an 8-byte range holding
  only w0/w1 of the texrect, or the bump-time shadow bytes, and those differ from the live bytes RT64 later re-reads in
  the merged record. Expect: the address is in a per-range record before the merged one, with different contents.
- H-split: the texrect is split across two submit ranges (w0/w1 | w2/w3). The walker sees it in neither range in a
  wrapped state, or misses it because the range starts mid-command and the walker desyncs.
- H-late: something writes the texrect words after record_submit (e.g. a second submit of the same lo..hi without a
  fresh record_submit, such as RT64 re-reading a merged span). Expect: a walker log at the address showing different
  words than the bin.
Measurement: add one cheap ring (env ROGUESQ_G1D_SPRITE_DIAG=2) that logs every record_submit (lo, hi, path id: merged /
per-range-wrap / commit / live) whose range covers any texrect with ul.x >= 960 px on a 1024-wide image, plus the words
the walker read there. Run lvl17 once (scratch/s6850/abd.sh 17 1, keep port.bin), match by address against the bin
records holding the wrapped words. Positive control: the 3 known TexrectGen rewrites must show up in the ring.
Fix by result: H-shadow / H-split -> walk the merged span (or clamp in the shadow too); H-late -> move the clamp to the
point RT64 reads.
Budget: 1 iteration. If it doesn't discriminate, close the residual as "3-frame 16x30 px HUD element, owner-visible?" and
move on to the next ladder rung.
