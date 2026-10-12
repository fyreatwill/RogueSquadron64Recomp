# NEXT: why RT64 colour writeback at width 512 never overwrites column 511 of 0x656400
HYPOTHESIS-ID: hangar-renderer-artifacts

s4639: col-511 noise is stale (present at first 512 VI; only 640-wide writebacks + a zmemcpy asset copy wrote it earlier); 512-wide writeback (phys 0x656000 len 0x54C00) fixes col 510 but not 511.
Hypotheses: H-native-w (RT64 native fb width is 511 or copyNativeToRAM loop bound is width-1), H-scissor (RDP scissor xh/xl excludes x=511 so RT64 never renders it - then screenshot edge garbage is just unrendered stale data), H-vi-crop.
Discriminator (one build): in lib/rt64 writeback log colorFb->width, colorWriteWidth, scissor extents, and a copyNativeToRAM col-511 pixel write count; positive control: col 510 write count equals rows. Also compare the SETSCISSOR/SETCIMG stream via existing RDP log. Remember: edits under lib/ need submodule-patches/export.sh + commit.
Tools: scratch/agent/s4639_bw.sh, ROGUESQ_BUF_WATCH=1.
