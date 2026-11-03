# NEXT: where do the abort-wipe pixels come from? (21:9 lacks retail's right-to-left black wipe)
HYPOTHESIS-ID: g3-wide-abort-wipe

State (s6842): the wipe is NOT in the captured gfx RDP stream (tools/rdp_bin_cmds.py on scratch/s6841/p43/port.bin,
VI 6731-6745 constant draw classes); RT64's VI ignores hStart/hEnd; retail oracle saw no CPU-visible writes into
0x690000-0x700000 at the 512-wide flight origins (single-source). Yet retail RDRAM dumps and port 4:3 window grabs show it.

Hypotheses:
- H-rdram: the pixels are written into RDRAM by something outside the captured gfx stream (a non-gfx RSP task / DMA),
  and RT64 picks up the RDRAM change.
- H-capture: port.bin misses a gfx submit (look at [dpc-merge] in the window; s6841 p43 run.log ~line 187100).
- H-rt64: RDRAM is clean in the port and RT64 synthesises the wipe (unlikely; would not explain retail RDRAM).

Discriminator, ONE port 4:3 run (scratch/s6841/port_abort.sh p43b "<env>"), env:
  ROGUESQ_FB_DUMP_DIR=$PWD/scratch/s6843/fb ROGUESQ_FB_DUMP_MODE=80128DA0 ROGUESQ_FB_DUMP_EPOCH_N=40 ROGUESQ_FB_DUMP_VI=1
  ROGUESQ_VI_EXTENT_PROBE=1
  plus the same RS64_RDP_BIN_PORT capture. Positive control: an earlier flight-frame dump (mode 0x80128E40, or
  ROGUESQ_FB_DUMP_EVERY) must show the terrain. Outcomes: wipe present in RDRAM dumps but absent in port.bin -> H-rdram,
  then log every RSP task (type, ucode, out ptr) between VI 6731 and 6747; wipe absent in RDRAM -> H-rt64; a missed
  submit in port.bin around [dpc-merge] -> H-capture. Then the same at 21:9 (ROGUESQ_ASPECT=21:9) to see where the
  native-512 writer lands (likely the stale 0x620000/0x690000 buffers instead of 0x8F5000/0x9D5000).
Rule 8: this slug has 1 non-discriminating iteration (s6842 narrowed but did not select).
