# NEXT (s7220): RETINA=1 + ASPECT=auto FULLSCREEN long-route front end (menus, hangar, cutscenes, interlaced stills)
HYPOTHESIS-ID: retina-frontend
Context: RETINA=1 flight endurance is CLOSED (s7218 + s7219: 600 s on screen, 59.7/s, 0 gaps >250, 0 hidden). Every RETINA datum so far is
LEVEL=4 flight; the front end at contentsScale 2 (2D texrects, RECT_ASPECT, interlaced 0x80128D50 stills via VI_ILACE_ADDR, mode switches
and their pillarbox correction) has never been checked with RETINA=1.
Hypotheses: H-ok (same presents/shape census as the s7215 21:9 run, 0 new boxes, front-end frames == RETINA=0 after a 2x downscale);
H-scale (some path uses point size, not drawable size: rect/scissor/pillarbox at half size or offset, visible as a box/shift in the shape
census or a misregistered frame); H-cost (interlaced stills or mode switches cost a re-create / >250 ms gap at 2x).
Run: copy scratch/s7215/r.zsh (L17 long route: boot -> menus -> L17 -> MISSION FAILED -> Elite Rogues x2) into scratch/s7220/, set
ROGUESQ_ASPECT=auto ROGUESQ_FULLSCREEN=1 ROGUESQ_RETINA=1 ROGUESQ_VI_SHAPE_LOG=1 + ROGUESQ_PRESENT_RING, screencapture -x at the
menu / hangar / ER / title timestamps instead of the 15.9 GB window capture. Quiet host, screen unlocked, one run per arm, arms RETINA=1 and 0.
Score: tools/s7215_shape_census.py (exit 1 = correction off a mode switch); tools/s7204_ring_cost.py (hidden 0, gaps >250 only at loads);
grep -c '[retina] swapchain create' (positive control: >=1 per arm, a1 at 3024x1898); per-shot downscale-2 diff a1 vs a0 on static menus.
Outcomes: H-ok -> front end closed at RETINA=1, sheet for owner; H-scale -> name the point-size path (plume/RT64) and fix it; H-cost -> name
the event from the Q row (acq/gpu) and the [retina] rows.
