# G1d: wide-title residual after texrect skip
HYPOTHESIS-ID: g1d-widescreen
s6248: native-target-black arm is a no-op (clear is already opaque black) -> H-native-white refuted.
Hypotheses: H-readin (RDRAM read-in at rt64_state.cpp ~2412 pulls non-black wide rows; WB_CLEAR only zeroes at writeback), H-bg-wrap (texrect S range repeats at 512 span).
Discriminator: extend WB_CLEAR to also memset the wide fb span immediately before the read-in (ww>512, siz 2), run texrect-all ph4 + none; residual->0 selects H-readin. Then ROGUESQ_LOG_TEXRECT_T for seams x~65/130/195/705/770.
Recipe: SKIPPH=4 TAGX=_x env "EXTRA_E=ROGUESQ_WB_CLEAR=1 ..." zsh scratch/agent/s6244_run.sh <arm>; analyze with scratch/agent/nb_frac.py. lib/ edit => export.sh + commit.
