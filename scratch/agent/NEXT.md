# NEXT (s7211): 16:9 vertical crop: does the presented 16:9 window drop the bottom native rows of every screen?
HYPOTHESIS-ID: wide-vertical-crop
Context: s7210 tools/s7210_regfit.py on the 16:9 Elite Rogues (window 1360x796, title bar 32, content 1360x764) fitted native rows
0-443 of the 448-row fb into window rows 32-796 (d 2.98; a full-448 fit was d 6.6). Rows 444-447 there are near-black, so nothing visible
was lost on ER, but the flight HUD sits near the bottom. 1360/764 = 1.780 vs fb 796/448 = 1.777, so window rounding alone explains <1 row.
Hypotheses: H-vi-range (the game's VI V_VIDEO range shows 444 lines; retail does the same, nothing to fix); H-rt64-crop (RT64 / the
wide present path scales or offsets the VI image so the bottom ~4 native rows fall off the window: fix); H-fit (the fit traded the
row count against a sub-pixel scale error; with finer steps the true count is 448).
Discriminator, ONE run (owner recipe 16:9 windowed, s7141 arm, EVERY=20 FROM in flight L4 and the title still): log VI regs
(V_VIDEO start/end, Y_SCALE, V_SYNC) per present, plus RT64's presented source rect (rows) if exposed, and regfit (tools/s7210_regfit.py,
1-step search, g1 to 448) on a flight span and a still. H-vi-range: VI lines x Y_SCALE = 444 rows and both screens fit 444; H-rt64-crop:
VI says 448 but the window shows fewer; H-fit: fine search fits 448. Also one 4:3 control arm (same fit must give 448 if 4:3 is complete).
Disk: delete raws after scoring.
