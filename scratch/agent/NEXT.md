# NEXT: 640x300 crawl fb presented 0.25% wider than its fb dump (CURRENT-TRUTH item 35)
HYPOTHESIS-ID: g3-crawl-640fb-xscale
State (s7146): crawl/logo are tris on a 640x300 fb (cimg w640 @9F9800); RT64 presented vs angrylion fb dump needs x-scale 1.0025
(1024-fb hangar/flight: 1.000, same run). pfm 640x300 issues no osViSetMode, so the VI mode in force is unknown.
Step 1 (one run, boring first): log the VI regs RT64 sees during the crawl (VI_WIDTH, X_SCALE, H_START, H_VIDEO/hStart-hEnd, V regs) and
RT64 VI::fbSize() + the present rect; route = env RDIR=s7147 AP=6:start,11:start,16:start,21:start,25:left,27:start,33:start,40:right,46:left,52:right,58:left,64:a
SECS=100 zsh tools/s7146_arm.zsh V1 "<vi log env>" (drop G5B_FRAME capture if not needed: FROM=999999). Find/patch a VI logger in
lib/rt64/src/hle/rt64_vi.cpp (export.sh + commit if edited) or ultramodern get_vi_regs.
Hypotheses: H-vi-hw (VI hEnd-hStart / xScale shows ~638.4 fb px across the line: hardware does the same, RT64 correct, close as retail);
H-rt64-present (VI says exactly 640, RT64 fbSize/present maps a different width, e.g. rounding: fix in RT64 behind an env);
H-capture (window capture resample: check with the 1024-fb scenes at the same window, which give 1.000, so this is already unlikely).
Discriminator: computed visible fb width = (hEnd-hStart)*xScale/1024 vs 640.
Side lead: 4:3 hangar VI fbSize (unset ROGUESQ_ASPECT, grep VI fbSize).
Keep CURRENT-TRUTH under 60000 B (58 KB now).
