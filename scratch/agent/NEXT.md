# NEXT: read RDRAM at 0x00BB0020 after the byteswap and at the depth store
HYPOTHESIS-ID: g1d-levelselect-ram

s6627 selects H-later-zero and refutes H-writeback and H-unwritten. One
Debug binary, both widths. 16:9 34.2 s / 21:9 33.5 s, 54/52 good frames,
alive, 0 crash markers. The upload at state.cpp:2604 is n=2093. The
previous event is n=2092, and the 16-bit call count is still 2092, so no
copyToRAM of any width entered the witness in between. That write, and
all 935 wide writes before it, is phys 0x00B20000, width 1024, rows
0..447. The span covers 0x00BB0020. That address is this image's pixel
x=16, y=288, not its y=180. The native rawBe there is 0x9F4C on every
cover and 0x0000 on none. Other words in the same write are 0xFFFC.
The upload head is still 13 zeros at x=16, y=180..192, and the GPU match
stays max abs 0. Image y=180 of the 0x00B20000 write is rawBe 0 at
0x00B7A020. Do not treat that pixel as the stripe. The only later rawBe
0 at 0x00BB0020 is n=2095, the depth image's own copyToRAM at 0x00B56000
after the upload. Do not patch the shader. Do not change a default.

The native witness reads the pre-byteswap readback. copyNativeToRAM then
byteswaps those words into RDRAM. A 32-bit byteswap cannot turn a nonzero
word into 0. The freelist restore in that function runs only for a range
that contains 0x001F3CC0. This span does not. The remaining question is
what the live RDRAM bytes are, on the pointer the upload actually copies.

ONE work unit, one binary, both widths. Keep the s6627 copyToRAM witness
and the s6626 guest column capture. Add two RDRAM reads, gated by
ROGUESQ_FLOOR_DEPTH_DIR, from boot, not phase-gated. Each read logs the
4 bytes at 0x00BB0020 and the rawBe uint16 at x=16 and x=1007 for
y=180..192 and y=200 (stride 2048, origin 0x00B56000). rawBe is the
s6626 conversion of those RDRAM bytes: 32-bit byteswap, then the 16-bit
swap. Also log the host pointer and whether it equals
g_recomp_rdram_for_wp_raw.

- Site A: end of Framebuffer::copyNativeToRAM, after the byteswap and
  after the freelist restore, when the written range covers 0x00BB0020.
  Include that call's native rawBe at the same address so a swap that
  zeroed the bytes is visible.
- Site B: the fbStorage.store that feeds state.cpp:2604, on the source
  pointer about to be copied, when the stored range covers 0x00BB0020.
  This is the bytes the upload turns into nativeSwappedRAM.

Hypotheses and discriminating outcomes:
- H-swap: site A fires, its native rawBe at 0x00BB0020 is nonzero, and
  the post-byteswap RDRAM rawBe is 0. The writer is inside
  copyNativeToRAM. Name the step (byteswap versus anything after it).
- H-alias: site A's bytes are nonzero, site B's bytes are 0, and the two
  host pointers are not the same base plus the same offset. Name both
  pointers. copyToRAM wrote a different mapping than the upload reads.
- H-between: both sites see the same base, site A's rawBe is nonzero
  (0x9F4C on the s6627 control), and site B's rawBe head is 0x0000.
  The zero is written after copyNativeToRAM returns and before the
  store. Do not start a guest-store watch in this unit.
- H-witness: the 21:9 clear-then-0x0000 upload does not recur, either
  site count is 0, the native witness no longer shows 0x9F4C before the
  upload, or the 16:9 z store is absent. Repair the log in this same
  iteration before interpreting a null.

Positive controls, required: magenta pixel (16,180) still changes; 16:9
floor-enter depth stays 1.0 and a later floor op stores z in 0.990..0.998;
the 21:9 upload rawBe head is 0x0000 on x=16 for y=180..192 and the GPU
match stays max abs 0; the s6627 native witness still reports nonzero
rawBe at 0x00BB0020 on the last covering copyToRAM; both new sites fire
at least once on 21:9. A silent log is not a result. Phase-gate the
route. No cross-run animation compare. Screen must be unlocked. SIGKILL.
One game run at a time. Do not overwrite scratch/agent/s6624_attachment,
scratch/agent/s6625_depth, scratch/agent/s6626_guest, or
scratch/agent/s6627_ram.

Build and run from build/ with the ROM beside it:

    env DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build build --target RogueSquadron64Recomp
    python3 tools/g1d_floor_depth.py --output-root scratch/agent/s6628_rdram

Keep tools/g1d_floor_depth.py --selftest and tools/g1d_floor_attachment.py
--selftest green. If lib/ changes, ./submodule-patches/export.sh is part
of the commit.
