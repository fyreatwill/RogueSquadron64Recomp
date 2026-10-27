# NEXT: G3c(a) fold s6353 soak (radfade2 pairs 0x44/0x48 and 0x44/0x4C vs none)
HYPOTHESIS-ID: g3c-owner-visual

s6352 fold: ctl arm (R2=0,1) turned far terrain flat sky-blue vs dark terrain in log arm (fb_0004500) => AA74 site is live under dd3 (positive control PASSED). Default xoff/zoff (0x40/0x48) read ~0, so d was |cam*0.5|=27.6 for every vertex (f=1 everywhere): not a valid position pair. Only stack word w3 (callee sp+0x44) varies per call (19..29, ~cam.x*0.5=24 => x-like); w4 (0x48) is 0, w5 (0x4C) 12.89 or denormal.
s6353 soak (s6353_g3c_r2_pairs.sh): arms p4448 (68,72), p444c (68,76) fade 18..26 sky haze, plus none. Read [radfade2] d values per arm: valid pair = d varies per vertex, bounded (<~40). Then compare far-edge frames (tools/g3c_edge_score.py) and send owner contact sheet. If neither pair varies in z, extend the stack dump past 0x64 (rebuild; edit EF9_CODE in tools/apply_s6311_edgefade.py, 12->24 words) and find z.
