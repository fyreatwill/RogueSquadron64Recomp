# NEXT (s7212): 16:9 mode-switch pillarbox: is the one-shot 4:3 viewport at the flight -> 448-row switch a visible flash?
HYPOTHESIS-ID: mode-switch-pillarbox
Context: s7211 run (scratch/agent/m6/g1_lvl17s7141V169/run.log; window raw scratch/s7141/V169.raw 1360x796 + .cap kept) logged twice
`[g1d-vishape-vp] fb 796x444 vp 166.1,0.0 1027.8x764.0 tex 4246x1360 ... sc 166..1192` right after VI #21 (flight 105..439 -> 43..501
yScale 0x7B9, mission end). Every other 796-wide viewport fills 0..1360. The tex is the previous flight target (stale).
Hypotheses: H-flash (one presented frame is pillarboxed 4:3 inside the 16:9 window: owner-visible black side bars for 1 frame: fix the
aspect term that uses the stale target / first-frame state); H-unseen (the pass draws but the next present overwrites it before the
swapchain shows it, or it is the fade-to-black frame so the bars are invisible); H-design (G1d pillar/edge crop deliberately boxes a
4:3-drawn screen: check rs64_g1d_pillar_crop / edge crop gates in lib/rt64/src/render/rt64_vi_renderer.cpp ~line 120).
Discriminator (offline first, capture once): from V169.raw (tools/s7122_fidelity.Raw) find frames around the switch time (cap_V169.txt /
present ring timing) and measure mean luma of cols 0-160 and 1200-1360 vs centre per frame: H-flash = a frame with dark side bands and a
lit centre whose neighbours are full-width; H-unseen = no such frame (positive control: a real full-width lit frame next to it, and the
same metric fires on a synthetic boxed frame). If H-flash, read the vp/scissor code path that produced 166..1192 and fix; one rerun to
verify the line disappears. Delete V169.raw/.cap afterwards.
