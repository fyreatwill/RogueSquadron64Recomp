# NEXT: name which musyxRenderVoiceSamples jal passed a3

HYPOTHESIS-ID: odd-dma-voice-a3

s4533 closed FE98 vs FB64. Do not rebuild that probe and do not re-read the node. The devAddr is `fillSampleStreamRange` at `0x8008FDC0`: node+8 = a3 + 0x600*k, k=0x55, remainder 0, so node+8 == t4 == `0x6C637265`. `0x8008FDCC` stored node+0xC = a3 = `0x6C617465`. a3 is not written inside that function. It is not a legitimate cart offset. Do not add a skip. Do not grep the tree for writers of voice+0x34.

The four jals are in `musyxRenderVoiceSamples` (`funcs_24.c`). Each does `lw a3, 0x34($s1)` and s1 is the voice (a0 of that function). Callee ra is 0, so the log has to sit on the jal, before the call.

- `0x8009024C` and `0x800902CC`: delay slot `addiu a3, a3, 0x100`. If this site is the bad call, the voice word is `0x6C617365`.
- `0x8009039C` and `0x800903F0`: delay slot changes a1 only. If this site is the bad call, the voice word is `0x6C617465`.

One instrument, one build, one run. Gate it on a new env (do not reuse `ROGUESQ_LOG_S4533`; that probe already did its job). At each jal print one bad row when a3 is odd or its top byte is ASCII, and one in-range control per site (`a3 < 0x01000000` and even). Include the guest PC, s1, the raw word at s1+0x34, a3, and a1. Phase-scope nothing: the death is the 512-to-640 edge, and the title/hangar gate on `[m5-fill-range-source]` fired 0 times on that edge.

A same-run control is mandatory. The s4533 ctl row had wC=`0x00C80000`, so a sane a3 does occur. If the bad row fires and no control row does, the log is not qualified.

Outcomes:

- Bad row at `0x8009024C` or `0x800902CC`, and `(s1+0x34) + 0x100 == a3 == 0x6C617465`: selects H-plus100. The voice word is `0x6C617365`. Stop. Do not add a skip.
- Bad row at `0x8009039C` or `0x800903F0`, and `(s1+0x34) == a3 == 0x6C617465`: selects H-raw. The voice word is `0x6C617465`. Stop. Do not add a skip.
- Bad row whose a3 is `0x6C617465` but the field identity above fails: the delay-slot reading is wrong. Quote the four registers and stop.
- Run dies in `do_rom_read` on `0x6C637265` with no bad row, and a control row did fire: the four jals are not the producer. Quote the last control site and stop. Do not add a fifth speculative callsite without a new static grep.
- Run dies in `fillSampleStreamRange` with no bad row: the parked bus error. Not this join. Do not re-run.
- Run never reaches VI 640: the edge was missed. Do not re-run the same recipe.

Arm the existing passive breadcrumb envs in the run. Kill with SIGKILL. Run from `build/` with the ROM beside the binary.
