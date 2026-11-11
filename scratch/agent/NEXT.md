# NEXT: G3 text crawl (yellow chapter text) at 21:9 (CURRENT-TRUTH item 34)
HYPOTHESIS-ID: g3-fidelity-text-crawl-219
State (s7145): STAR WARS logo recede (69-75 s on the s6995 route) == angrylion under one fit; the AP 70:start press skips the text crawl.
Step 1: copy tools/s7144_arm.zsh to tools/s7146_arm.zsh with AP overridable (AP=${AP:-...}); run the route with AP ending at 64:a
(drop 70:start,76:start), SECS=110, DL=69 DU=35, FROM=4150, EVERY=3: env RDIR=s7146 AP=... zsh tools/s7146_arm.zsh T1 "" ; then T2 "ROGUESQ_RECT_ASPECT=0".
Check the stream is large: at 6.9 GB per 14 s, 35 s ~ 17 GB -> raise EVERY to 6 or set ROGUESQ_G5B_FRAME_MAX_MB=12000 (already) and accept truncation.
Post: tools/s7141_post.zsh scratch/s7146 T1 0,11,469,216 117,352; drop rows with pframe<5; s7143_affine.py with the s7145 grids
(AFF_SX=0,1,2 AFF_SY=-8,-6,-4,-2,0 AFF_E=0.992,0.984,0.976,0.968,0.96); x-scale sweep scratch/s7145/xscale.py (copy into tools/ if reused).
Hypotheses: H-equal (crawl text == angrylion under the logo fit); H-crawl-rect (crawl text is a texrect/copy path: T1 vs T2 differ, text box above the floor
under the fit); H-crawl-persp (the crawl's perspective tilt is our wide path: x-scale or row-dependent x error grows toward the top).
Controls: painted square per replay; T2 as negative control if the text is texrects; shift-2 arm otherwise.
Side lead: 4:3 hangar VI fbSize (unset ROGUESQ_ASPECT, grep VI fbSize).
CURRENT-TRUTH 59961 B: any net growth triggers maintenance; trim closed items 28-33 to one line each while editing.
