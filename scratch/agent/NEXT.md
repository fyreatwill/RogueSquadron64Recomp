# NEXT: G3 opening crawl (STAR WARS logo + text crawl) at 21:9 (CURRENT-TRUTH item 33)
HYPOTHESIS-ID: g3-fidelity-crawl-219
State (s7144): level select, available craft and hangar all == angrylion at 21:9 once tools/s7143_affine.py registration is fitted.
On the s6995 route (tools/s7144_arm.zsh AP) the crawl runs ~71-81 s (64:a selects craft, 70:start, 76:start). Capture it:
  env FROM=<swap at ~69 s> DL=69 DU=14 SECS=86 zsh tools/s7144_arm.zsh C1 ""   then C2 with "ROGUESQ_RECT_ASPECT=0".
  Swap estimate: M1 swap 1300 ~ t 23 s and ~55-60 swaps/s in menus -> start ~FROM=3900 (check M1.idx/H2.idx mach times; too early is harmless,
  pframe 0 rows are dropped). Post: tools/s7141_post.zsh scratch/s7144 C1 0,11,469,216 117,352; then s7143_affine.py with a fit on the logo.
Hypotheses: H-equal (crawl == angrylion under one fit); H-crawl-rect (the crawl text/logo is a rect/copy path RT64 scales or filters
differently: fit on logo vs crawl text disagree by >1/4 px or text stays above floor); H-crawl-4:3 (crawl drawn into a 4:3 sub-viewport and
stretched by our wide path: x-scale sweep picks != 1, compare logo width vs angrylion).
Positive control: painted-square PASS per replay; negative control the C2 RECT_ASPECT=0 arm.
Side lead: 4:3 hangar VI fbSize (retail 512x336?) for the s7142 21:9 squash claim: run the same arm with ROGUESQ_ASPECT unset, grep VI fbSize.
CURRENT-TRUTH ~59.7 KB: keep edits net-zero (Step 0 triggers at 60000).
