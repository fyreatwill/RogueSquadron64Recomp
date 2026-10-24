# NEXT: G1d step 13 - single ROGUESQ_ASPECT knob, then menus/hangar at 683
HYPOTHESIS-ID: g1d-widescreen
Known (s6119-s6120): FB_WIDTH=683 + VPW_SCALE/ASPECT_SCALE=1.3333 renders an undistorted 16:9-ish frame in the window on L1 (activated screenshots, scratch/agent/m6/s6120/).
Do: (1) implement ROGUESQ_ASPECT=4:3|16:9|21:9 that sets FB_WIDTH=round(448*r) (16:9=797? NOTE 683 was ~1.525; derive from 448*r, check width allowlist/stride constraints) and the two scales = FB_WIDTH/512; default 4:3 = retail. (2) one run, 3 arms (4:3, 16:9, 21:9) on L1 with activated screenshots + a hangar/title arm; positive control = 4:3 arm equals ctl.
Discriminating outcomes: render ok at 797/1045 -> allowlists generalise; black/garbage -> another width constraint (grep 683/512 hardcodes in RT64 + game).
