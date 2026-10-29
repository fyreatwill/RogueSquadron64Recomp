# NEXT: cap heap 8010FEFC at the live depth image
HYPOTHESIS-ID: g1d-levelselect-heap

s6630 closed the ownership question. Do not re-litigate H-stale-target, and
do not suppress rs_memset or paint the depth image back. Evidence:
scratch/agent/s6630_ownership/ownership_verdict.json (reanalyzed; wide21
selects H-live-overlap, freed=1, named_ptrs 801163E4). Both widths, one
Debug binary, screen unlocked, phase-driven, SIGKILL from build/.

What is true:
- 21:9 last carve: outw=1024 top=0x80C00000 e4=0x80B56000 dc=0x80961000.
  Drop aspect=21:9 fbw=1024 t0=0xE0000 drop=0x4B000. Image reservation
  [0x80B56000, 0x80C00000). RT64 uploads [0x00B56000, 0x00BFF800), 1024x339.
- At malloc n=13559, 801163E4 is still 0x80B56000. Heap 8010FF18 ends at
  that pointer (head 0x80154690, end 0x80B56000, n=123). Heap 8010FEFC does
  not: head 0x80961000, end 0x80C00000, n=902. The returned block is
  0x80BADB40 size 0x8000 flags 0x0002; user pointer 0x80BADB50 len 0x8000
  covers 0xBB0020 and not the three outside words. Caller: rs_malloc ->
  rs_zcalloc -> zcalloc -> inflate_blocks_new -> inflateInit2_ ->
  inflateInit_ -> processAssetLoadStep -> mainEventQueueWorker.
  rs_memset 0x800078EC then zeros 0xBB0020 (n=13560..13567).
- inflateEnd frees that block at n=13633 (rs_free -> rs_zcfree -> zcfree ->
  inflate_blocks_free). 801163E4 stays 0x80B56000 and the heap end stays
  0x80C00000. SETZIMG n=13640 and depth-read n=13643 still upload the image,
  covering all four watched words. A free of the zlib block is not a
  framebuffer release.
- 16:9 is the same heap class, not a clean reservation. Level-select carve
  e4=0x80B7BD80, and malloc n=13099 phys 0xBAA1B0 len 0x8000 covers 0xBB0020
  while 801163E4 is 0x80B7BD80 and 8010FEFC ends at 0x80BFFFE0. 8010FF18
  again ends on e4. This arm records 0 depth-reads, floor enter_ones, fail [].
  The overlap is not 21:9-only. The upload is.
- Outside the 32 KB window, still inside the 21:9 image: malloc 0xBB5B60
  len 0x4C4 covers 0xBB5FDE and 0xBB6020; malloc 0xBB6460 len 0x1008 covers
  0xBB67DE. Last pre-upload changes: 0xBB5FDE stays 0 at rs_memset;
  0xBB6020 becomes 6 at pc 0x80027E8C (n=13588); 0xBB67DE becomes 8650761
  at pc 0x8002958C (n=13600). Do not claim the stripe is only the 32 KB zero.
- After the free, guest pc 0x80001884 stores 0 through the 8010FEFC head
  word (n=13637) while 801163E4 is unchanged. That is later than the clear.
  Do not treat it as the reservation release.

ONE change: make heap 8010FEFC stop at the live depth pointer the way
8010FF18 already does. The wide carve in partitionFramebufferMemory
(tools/apply_s6031_far.py, generated funcs_0.c) moves e4 down and leaves
the 8010FEFC free block covering [e4, top). Find that free-block boundary
and split or cap it there. A host-side upload skip, a memset skip, or a
depth restore is not this change. Retail 4:3 must keep today's addresses.
No default change.

DISCRIMINATOR, same instrument, both widths, no second game in parallel:
- H-heap-cap: at the 21:9 depth-read, no malloc/clear interval intersects
  [fb start, fb end) while 801163E4 still names that fb. The zlib window's
  returned pointer is below e4. 0xBB0020 in that upload is not the memset
  zero. 21:9 summary fail loses edge-px and dy. 16:9 stays fail [], floor
  enters at 1.0, and its heap end is also at or below e4.
- If the cap is in force and the tear metric remains, stop. Record the new
  upload word at 0xBB0020 and do not add another patch in that run.
- Positive control: the real zlib allocation still returns and rs_memset
  0x800078EC still clears that returned block (guest-exact on its own
  range). Existing guest-bzero and host-memset controls must pass.
  Missing the heap-end field at the depth-read is incomplete, not a pass.

Commands:

    python3 tools/g1d_floor_depth.py --selftest
    python3 tools/g1d_floor_attachment.py --selftest
    env DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build build --target RogueSquadron64Recomp
    env ROGUESQ_LOG_FB_ALLOC=1 ROGUESQ_LOG_G1D_TASK=1 python3 tools/g1d_floor_depth.py --output-root scratch/agent/s6631_heapcap
    python3 tools/g1d_floor_depth.py --analyze --output-root scratch/agent/s6631_heapcap
    ./submodule-patches/export.sh

Screen must be unlocked (tools/g1d_floor_inputs.py screen lock check) before
the run. One game at a time from build/ with the ROM beside it. SIGKILL.
If the carve change is generated C, persist it in the fixup script. Never
tools/agent/regen_n64recomp.sh. PatchesLib C is allowed; qualify it with
this same two-arm table. Read docs/F5-UCODE-REFERENCE.md before interpreting
any new command stream. Oracle still cannot witness this above-8MB layout.
