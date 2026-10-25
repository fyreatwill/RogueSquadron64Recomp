# NEXT: does phase 4 read the early images that cover the wide pool?
HYPOTHESIS-ID: g1d-widescreen

Session 6205 closed the heap-block question. Do not look for another
free. Do not retarget `0x8096D600`. Do not write `0x801163E8`. Do not
change `t0`, `d8`, `dc`, `f0`, `f4`, `f8`, or `ec`. Do not raise
`osMemSize`. Do not skip `Framebuffer::copyNativeToRAM`.

The writer is `coalesceFreeHeapBlocks`, called from `runVideoFrameTick`
at `0x80001430` because `partitionFramebufferMemory` returned 0.
`a0=a1=0` is that mode. `a2` is the heap head. `a3` is `ec`. The stores
at `0x8000249C` and `0x800024A4` produce the pool-time size and the
flag-8 terminator at `ec-0x10`. That value is the game's own heap bound.

The overlap that remains is layout. Carve n=0, n=1, and n=2 are
identical in both arms. Their `d8` images all end at `0x80B00000`:

- n=0 `0x80ADD000` plus `0x23000` (320x224)
- n=1 `0x80A6A000` plus `0x96000` (640x480)
- n=2 `0x80A95C00` plus `0x6A400` (640x340)

The 4:3 n=3 pool starts at `0x80B25000`, above that end. The 16:9 n=3
pool is `[0x80AE6E00, 0x80B31D58)` and crosses it. n=3's own stack is
packed from `ec` to the top, so there is no hole to slide the pool into
without saying which other buffer is dead.

One paired run, same recipe as s6205, no new store. Add one env-gated
counter, not a new heap walk. Log every phase-4 RDP color-image and
texture-image address that intersects `[0x80A6A000, 0x80B00000)`, with
the guest PC already available on the task row. Also count
`copyNativeToRAM` spans that intersect that same range, as the positive
control: that count must be >0 in both arms (s6200 already saw those
writebacks).

`ROGUESQ_OSMEM_MB=12 ROGUESQ_LOG_G1D_TASK=1 ROGUESQ_LOG_PHASE=1`
`ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1`
`ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_AUDIO_UCODE=1 ROGUESQ_SPIN_YIELD=1`
with `ROGUESQ_ASPECT=4:3` then `16:9`. From `build/`, one game at a
time, SIGKILL, screen unlocked. Do not pass `ROGUESQ_FB_WIDTH`.

- H-read: phase-4 CI or TI count in that range is >0. The images are
  live. The next change relocates them or the pool; it does not drop
  the writeback.
- H-clobber: CI and TI counts are 0 in both arms, while the writeback
  control is >0 in both. The bytes are a stale render-target copy into
  memory n=3 reused. Only then is an opt-in refusal of writeback spans
  that intersect the live pool (`e8`, `e8+0x4AF58`) a candidate, and
  only on the wide arm. The 4:3 pool does not intersect the range, so
  its writeback count must stay >0.
- H-blind: the new counter does not fire and the writeback control is
  also 0. The instrument missed the phase. Do not relocate anything.

Control must still show `w78=05200002` at `data_ptr=0x80B2D820`. Wide
`e8` must stay `0x80AE6E00` and `w28=w78=00010001`.
