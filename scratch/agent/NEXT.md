# G1d: wide-title residual, H-bg-wrap
HYPOTHESIS-ID: g1d-widescreen
s6249: RI_CLEAR (clear before RDRAM read-in) moved texrect-skip residual only 0.174->0.132 -> H-readin minor.
Hypotheses: H-bg-wrap (texrect S range repeats at 512 span, seams x~65/130/195/705/770), H-fillrect (fill rects paint residual ~0.13 lower band).
Discriminator: log per-texrect x0,x1,s0,dsdx in the wide title phase (ROGUESQ_LOG_TEXRECT_T or add), compare to seam columns; a texrect with width>512 or s-span wrapping selects H-bg-wrap. Also skip arm 'fill' with texrect-all in same run to attribute residual.
Recipe: SKIPPH=4 TAGX=_x env "EXTRA_E=ROGUESQ_WB_CLEAR=1 ROGUESQ_RI_CLEAR=1 " zsh scratch/agent/s6244_run.sh <arm>; analyze with scratch/agent/nb_frac.py. lib/ edit => export.sh + commit.
