# Name the global the SetTextureImage address comes from
HYPOTHESIS-ID: g1d-widescreen

Session 6207 selects H-still and refutes H-clear and H-broke. Keep the
drop. Do not revert it. Do not skip `Framebuffer::copyNativeToRAM`. Do
not retarget `0x8096D600`. Do not write `0x801163E8`. Do not change n=3's
`t0`. Do not raise `osMemSize`. Do not patch the RDP stream. Do not move
`f0`. Do not retarget the `swl` at `0x8000D5A8` in this iteration.

The wide pool fill is gone. Logged phase-4 `w28` and `w78` are
`00000000`, not `00010001` and not `05200002`. The white rectangle in
`fb_0001438_w796.ppm` is still there. The wide `SetTextureImage` prefix
is still `0xAE6120`, `0xAE5520`, `0xAE5320`, `0xAE5120` (`w0=0xFD100000`,
PC `0x80007904`), the same addresses as s6206. `ti_hit` is still 32 per
submission. Those addresses are not `d8` (`0x801163D8`, now `0x80A50E00`
for the 640x480 image) and not `dc` (`0x801163DC`, now `0x809BAE00`).
`+0x28` and `+0x78` are zero while the pointer stayed, so those two node
words are not it either. `0xAE6120` is `0xCE0` below the pool base
`0xAE6E00`, still inside the moved image. Control prefix is still
`0xA6AA10` stride `0x1000`. `f0` (`0x801163F0` = `0x80B00000`), `f4`, and
the early `e8` did not move. They are candidates, not a named source.

One paired run, same recipe as `scratch/agent/s6207_run.sh` (12 MB,
sequential, ctl 4:3 then wide 16:9, from `build/`, SIGKILL, screen
unlocked, do not pass `ROGUESQ_FB_WIDTH`). Keep `[g1d-img]` and
`[g1d-drop]`. Add one change to `rs64_m4_dma_probe` in
`src/rsp/dpc_bridge.cpp`: under `ROGUESQ_LOG_G1D_READS`, scan each
phase-4 RSP DMA payload (full length, stop the scan at 0x1000 bytes) for
a big-endian word whose low 24 bits lie in `[0xA6A000, 0xB00000)`. Emit
a row only on a hit. Log `dram`, byte offset, the word, `guest_pc`, and
whether `dram` falls inside the first 0x200 bytes of the phase-4
`data_ptr` (control `0x80B2D820`, wide `0x80AEF620`). Cap 64 hit rows.
Do not also emit the old per-DMA hash line; s6195 showed that log is
thousands of rows and will bury the hit.

- H-f0: the slot (`dram`) is `0x801163F0`, `0x801163F4`, or `0x801163E8`,
  or the same absolute slot in both arms within a few bytes of one of
  those. Name it. Do not move it.
- H-recompute: the control word `0x80A6AA10` and the wide word
  `0x80AE6120` are both found, and the slot is neither those globals nor
  inside the command node. Name the address and the guest PC. Do not
  patch it.
- H-node: the word sits in the first 0x200 bytes of `data_ptr` at an
  offset other than `0x28` or `0x78`. Name the offset.
- H-miss: the control log never contains `0x80A6AA10`. The scan is
  blind. Narrow it to the logged `[g1d-img-hit]` prefix and rerun the
  same pair once. Do not conclude the RSP synthesizes the pointer until
  a scan that finds the control word still misses `0x80AE6120`.

Control must still show `w78=05200002` at `data_ptr=0x80B2D820` and
`[g1d-drop] aspect=4:3 drop=0`. Wide `e8` must stay `0x80AE6E00` and
`[g1d-drop]` must stay `drop=0x19200`. A control hit on `0x80A6AA10` is
the positive control for the new scan.
