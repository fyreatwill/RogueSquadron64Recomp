# NEXT: G1d step 11 - VI registers under ROGUESQ_FB_WIDTH=683 (RT64 present path)
HYPOTHESIS-ID: g1d-widescreen
Known (s6118): RDP stream is width-consistent; flips drawn directly; no copy stage. Black window is downstream.
Competing: H-vi-width (VI_WIDTH_REG still 512 or xScale/hStart unscaled, RT64 reads flip with wrong stride) vs H-rt64-fb-size (RT64 fb width keyed off scissor/colorimage, mismatch with VI) vs H-readback (only our fbdump reader is wrong; window truly black).
Discriminator: one run, log per swap the VI regs RT64 sees (VI_WIDTH_REG, X_SCALE, H_START, V_START, ORIGIN, CTRL) in ctl vs ROGUESQ_FB_WIDTH=683 (src/main/upstream_compat.cpp ~358, ~626). Scale the mode table comRegs width (+0x04) and xScale per fbw/512 if they read 512. Positive control: ctl must print width 512 + origin; fix arm must flip the window from black.
