# NEXT: 339-row menu scissor column (CURRENT-TRUTH item 1)
HYPOTHESIS-ID: g3-menu-scissor-col
Why: s7188 found that on SELECT LEVEL / AVAILABLE CRAFT / hangar (339-row fbs) the RDP stream sets SETSCISSOR (0,0,711,339) and FILLRECT lr 711
at fb width 712 (and 713), so the rightmost column is never drawn (RT64 black, angrylion pre-fill magenta). Every even width shows 1 such column.
Hypotheses: H-retail (retail 640 also scissors at 639: game behaviour, VI overscan hides it -> close, no change),
H-widen (our G1d width patch computes the 339-row viewport/scissor as w-1 or evens it down; retail sets 640 -> fix the patch),
H-fill (scissor is full width but a half-width/centre rounding in the viewport code drops a column only when w != 640).
Discriminator, ONE capture per arm, no new build: the same s7146 menu route at retail 4:3 (ASP=off), 16:9 (796) and 21:9 (1024), then
tools/s7188_capscissor.py <cap> 1700 1720 (check the swap range lands on AVAILABLE CRAFT via the g5g/frames csv first). Short runs are enough:
  env RDIR=s7189 ASP=off FROM=1600 EVERY=20 SECS=45 DL=8 DU=32 zsh tools/s7146_arm.zsh R1 ""
  env RDIR=s7189 ASP=16:9 FROM=1600 EVERY=20 SECS=45 DL=8 DU=32 zsh tools/s7146_arm.zsh W1 ""
Outcomes: scissor xh 639 at 640 -> H-retail (positive control for the parser: the 448-row title phase must show xh = fbw).
xh 640 at retail but fbw-1 wide -> H-widen: find the G1d site that writes the 339-row viewport (tools/apply_s6031_far.py s6694 sites
0x80017370 / 0x80017814, upstream_compat.cpp s6113 video-state widening) and fix it; validate with tools/s7188_colprof.py (0 undrawn columns).
Delete .cap/.raw after parsing.
