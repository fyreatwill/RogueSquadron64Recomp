# NEXT: G3c(a) jagged far-terrain edge - arm table
HYPOTHESIS-ID: g3c-visual-defects
dd3 is qualified (s6447); owner directive says switch to G3c now. Start with (a):
H-optin (auto-far/dd>1 exposes grid-aligned cell boundary, haze not scaled) vs H-aspect (s6144 frustum x-widening exposes side edge) vs H-retail (retail already shows it).
Discriminator: pinned-pose framebuffer (recipe soak_queue/s6412_attpin.sh) in arms retail / dd2 / dd3 / ASPECT alone / FPS60 alone; compare far-edge stair-step metric (row-wise horizon x-run lengths of terrain-vs-sky boundary) + a retail positive control. Queue as ONE soak script with all arms; send contact sheet to owner. Then fix: scale fog/haze start/end by dd factor or fade outer ring.
