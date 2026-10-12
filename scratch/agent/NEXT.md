# NEXT: find the non-CPU, non-RT64-writeback source of hangar col-511 noise (buffer 0x656400)
HYPOTHESIS-ID: hangar-renderer-artifacts

s4638: CPU stores refuted (controlled). s4637: RT64 writeback refuted. Remaining: H-dma (RSP/PI DMA into RDRAM; use rs64_m5_host_write_census with ROGUESQ_LOG_M5_HOST_WRITE and an RSP DMEM->RDRAM hook), H-rdp-host (other RT64 RDRAM write sites in lib/rt64), H-stale (col 511 already nonzero at first 512-wide VI).
Discriminator: one build with (a) a physical-range watch for 0x656400 col-511 offsets in the host census + RSP DMA-out path, (b) RDRAM col-511 snapshot at first 512-wide VI. Positive control: a whole-buffer write-census hit in the same run.
Tools: scratch/agent/s4635_mask.sh (pass ROGUESQ_LOG_S4299=1 ROGUESQ_EDGE_DUMP=<abs dir>), s4637_an.py, tools/apply_s4638_edgewatch.py.
