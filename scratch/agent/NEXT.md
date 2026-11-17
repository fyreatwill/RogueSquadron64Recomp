# NEXT (s7504)
HYPOTHESIS-ID: m3-partition-over-live-block

Fold first: SOAK-RESULTS line for s7503_fa_levels (rows `s7503_fa_levels fa arm=` in scratch/s7503_fa_levels/out.txt). Score 5 is
EXPECTED (live>0 by design since s7503); judge by ctlC/ctlV=ok and by the `[s7503] verdict=live` rows: each must be one of the three
s7503 shapes (present-path upload with small RT64 diffpx; up,set,draw after a zmem/cpu compose; tex load inside a stale extent). Any
other live shape (draw/zread on a stale record with NO upload before it, or upP long after a cpu write) is new: read it.

Work unit, class FB: is the allocator header that RT64 uploads on the present path (shape 1: L4 751E00 hdr 75C004, L15 B20000 hdr
B20004, t~28.2 sw 1640 mission load; L15 961000 t~58.7) visible in the PRESENTED image, and is it retail?
Hypotheses: H-fb-visible (the presented frame at that swap shows the 2 header words as 4 odd pixels at the header's x,y) /
H-fb-covered (VI scanout window / HUD / later draw covers it, or the frame is black: osViBlack is ignored by the port s982, check the
VI control/type) / H-fb-retail (retail RAM holds the same header there at that frame).
Discriminator, ONE build: at the present-path upload of an s7503-armed fb, compute the header word's (x,y) from (addr - base)/(w*2),
read RT64's presented texture at that pixel (or dump the presented frame, tools/ framebuffer capture used by the G3 sheets) and the
VI h/v start window; log pixel value vs RAM word. Control: plant a host write of a bright word at the same row in a live presented fb
(t>=30 s) and see it in the readback. Retail: the oracle does not reach mission load; if H-fb-visible, ask whether an oracle savestate
at the mission load exists (tools/oracle/README.md) before claiming port-only.
Run: `env NAME=s7504_fb zsh tools/s7503_fa_recipe.zsh` with the new flag in XC.
