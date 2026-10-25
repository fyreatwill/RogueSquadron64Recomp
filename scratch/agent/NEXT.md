# Wide title art x-origin: find the writer of the width-dependent offset
HYPOTHESIS-ID: g1d-widescreen
s6224: origin of the 64x32 title texrect grid = 0 @4:3, 241 @FB_WIDTH 796 (scale 1.5547), 384 @1024 (scale 2.0); constant over all submits (slide refuted). guest_pc 0x8000834C in the log is stale, not the emitter.

Hypotheses:
- H-scale-math: offset = f(width, scale) computed by guest layout code from 0x8011A838 / hooked dims (e.g. (W - 640*k)/2 form). Predicts a third width (e.g. ROGUESQ_ASPECT=16:10 or FB_WIDTH=900) lands on the same formula; fit the 3 points.
- H-hook: the s6113 menu-dimension hook (512x448 / 512x340 rewrites) feeds the layout. Predicts offset changes with the hooked dims while FB_WIDTH is fixed.
- H-dl-data: the offset is baked into the DL by a builder that reads the FB width. Predicts a guest write of the value *4 (964=0x3C4 @796, 1536=0x600 @1024) into a DL word before the submit.

Discriminator (one build/run): add a third width arm (ROGUESQ_FB_WIDTH=900 with the c43/ctl recipe of scratch/agent/s6224_run.sh) to fit the formula, and in the same run dump the first texrect's DL words (w0/w1 already logged) and scan guest RAM at the submit for the 4x-unit value; then lldb/guest write-watch that DL word address (positive control: the 4:3 arm's 0 word is untouched, use a known-written neighbour) to name the writer.
Run: copy scratch/agent/s6224_run.sh (one game at a time; SIGKILL; analyse with scratch/agent/s6224_minx.py on run.log, NOT fail_att*.log for the c43 arm).
