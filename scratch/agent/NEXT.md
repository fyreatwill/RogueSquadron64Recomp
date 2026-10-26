# G1d: wide-title residual after texrect skip
HYPOTHESIS-ID: g1d-widescreen
s6247: texrect-all skip (ph4, WB_CLEAR) leaves lower-band 0.174 non-black; tri-all/fill skips do not remove it.
Hypotheses: H-bg-wrap (texrect S range repeats at 512-wide span; widen/clamp), H-native-white (RT64 native fb not cleared to black at wide alloc -> white corners).
Discriminator: add ROGUESQ_WB_NATIVE_BLACK (clear RT64 native colour target to black at wide alloc) and run texrect-all + none arms; residual->0 selects H-native-white. Then inspect texrect S ranges for the tiling seams (x~65/130/195/705/770) via ROGUESQ_LOG_TEXRECT_T.
Recipe: SKIPPH=4 TAGX=_x env "EXTRA_E=ROGUESQ_WB_CLEAR=1 ..." zsh scratch/agent/s6244_run.sh <arm>; analyze with scratch/agent/nb_frac.py.
