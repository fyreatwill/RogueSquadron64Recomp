# NEXT: move the early images below the wide pool
HYPOTHESIS-ID: g1d-widescreen

Session 6206 selected H-read and refuted H-clobber and H-blind. Do not
drop `Framebuffer::copyNativeToRAM`. Do not retarget `0x8096D600`. Do
not write `0x801163E8`. Do not change n=3's `t0`. Do not raise
`osMemSize`.

Phase 4's color image is the real framebuffer (`0xB90000` on 4:3,
`0xB51E00` on 16:9). The span `[0xA6A000, 0xB00000)` is the 640x480
image, and phase 4 samples it with `SetTextureImage`: 83 commands per
submission on 4:3, 32 on 16:9. The logged prefix of those addresses
stays below the wide pool (`0xAE6E00`). The bytes that actually cover
the pool are the phase-2/3 writeback of the images that end at
`0xB00000`, including `0xADD000` len `0x23000`. The 4:3 pool starts at
`0xB25000`, so the same writeback misses it and `w78` stays
`05200002`.

One paired run, same recipe as s6206 (`scratch/agent/s6206_run.sh`).
Opt-in only, when `ROGUESQ_ASPECT` is wider than 4:3. In
`partitionFramebufferMemory`, lower the carves whose images currently
end at `top-0x100000` by the overlap (`0xB00000 - e8` for the wide
arm, `0x19200` at width 796) so those images end at or below `e8`.
Leave the 4:3 arm on the retail cursor. The texture pointers have to
follow the moved globals; do not patch the RDP stream.

Keep `[g1d-img]` and `[g1d-wb]`. From `build/`, one game at a time,
SIGKILL, screen unlocked. Do not pass `ROGUESQ_FB_WIDTH`.

- H-clear: wide `w78` at `data_ptr` becomes `05200002`, `e8` is still
  the pool base, and `[g1d-img-hit]` addresses move down by the same
  delta as the image. `ci_hit` stays 0. `last_ci` stays the real
  framebuffer. 4:3 `w78` stays `05200002` at `0x80B2D820` and its TI
  addresses do not move. That is the fix. Then dump one phase-4 frame
  per arm and confirm the wide central rectangle is gone.
- H-still: wide `w78` is still `00010001`, or the TI addresses did not
  move. The carve change missed the pointer the RSP reads. Do not add
  a writeback skip. Name the global the texture address comes from.
- H-broke: 4:3 `w78` changes, or either arm crashes, or `ci_hit`
  becomes nonzero. Revert the carve change.

Control must still show `w78=05200002` at `data_ptr=0x80B2D820`.
Wide `e8` must stay the n=3 pool base from `[g1d-carve]`.
