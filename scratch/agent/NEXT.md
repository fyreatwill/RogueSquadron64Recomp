# Who writes the wide texels at 0xAE5F20 between phase-3 wb and phase-4 TI hit 1?
HYPOTHESIS-ID: g1d-widescreen

s6214: wide 0xAE5F20/0xAE6B20 are `00010001` fill after every wb, real texels (`00010845 008300C5 ...`) by TI hit 1.
Writer unknown. Hypotheses: H-guest-copy (guest memcpy/DMA from a decoded asset, PC attributable), H-rsp-dma (RSP/ucode DMA into RDRAM),
H-rt64-other (a second RT64 writeback path not tagged rt64wb).
Discriminator: one run, wide arm, ROGUESQ_WATCH-style write watch (or lldb hw watchpoint, see upstream_compat.cpp:619) on physical 0xAE5F20..+32,
log first non-fill write with guest PC + kind. Positive control: same watch on 0xA6AA10 must fire in the ctl arm (63556355 appears there).
Do not patch until writer named.
