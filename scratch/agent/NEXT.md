# G1d: wide-title residual, remaining 0.05 after fill+texrect skip
HYPOTHESIS-ID: g1d-widescreen
s6251: fill,texrect-all skip -> lower residual 0.050 (texrect-all alone 0.132). Fill paints ~0.08. "all" arm is not a zero control (reads 1.0).
Hypotheses: H-fill-extent (fill rects wider than the 512 scissor/FB width, repaint with last fill colour), H-tri-rest (tris paint the last 0.05), H-white-corner.
Discriminator: arm "fill,texrect-all,tri-all" (csv) -> if ~0 then tris; else log fill rect extents/colours in ph4 (WBLOG) and compare to 512 width.
Recipe: env SKIPPH=4 TAGX=_ri "EXTRA_E=ROGUESQ_WB_CLEAR=1 ROGUESQ_RI_CLEAR=1 " zsh scratch/agent/s6244_run.sh <csv arm>; scan with scratch/agent/nb_frac.py on g1_lvl1s6244_<arm>_ri_ph4/fbd/fb_0001000_w900.ppm
