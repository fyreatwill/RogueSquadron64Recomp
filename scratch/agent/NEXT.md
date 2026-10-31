# NEXT: 21:9 level-select floor tear (reopened s6691) — name what the floor samples
HYPOTHESIS-ID: g1d-levelselect-floor-source

s6691: the 21:9 level-select floor is torn in every run (s6631's "pass" frame included); 16:9 clean;
heapslot on/off (ROGUESQ_G1D_HEAPSLOT) both torn. Scorer: tools/g1d_row_noise.py <ppm> (vhf>10 = torn;
--selftest <clean ppm> must print ok). Harness: scratch/agent/s6691_recheck/ab.py (calls
tools/g1d_floor_inputs.run_arm; pass an ABSOLUTE output root or FB dumps land nowhere).
Single-source lead: 21:9 [floor-tex] floor_frac=0.5, two combiner modes (omL 00552230 / om2 00552220),
dTr=0, tex range 3.6..126 vs 16:9 floor_frac 1.0 one mode.

Read first: CURRENT-TRUTH G1d notes ("do not return to the combiner or pixel pipe" — the s6611-s6631
thread already measured those), docs/F5-UCODE-REFERENCE.md for SetTImg/LoadBlock/LoadTile/SetTile.

Hypotheses:
- H-src-overlap: the floor's texture image (SetTImg addr) at 21:9 lies inside a buffer the wide
  layout gives to something else (colour fb 0x961000/0xA0B000 at 1024x336 = 0xA8000 each, depth at
  e4, heap slot), so the texels are another buffer's rows.
- H-load-geometry: the texture source is the same as 16:9 but the load (LoadTile/LoadBlock line,
  dxt, tile size) is computed from the screen width (1024) and walks past the image row by row.
- H-split-draw: the floor is two draws at 21:9 (floor_frac 0.5, two modes); the right/outer one
  samples a texture never loaded (stale TMEM).
Discriminator, ONE build, ONE log flag (extend the existing ROGUESQ_LOG_FLOOR census in
src/rsp/dpc_bridge.cpp): for every floor-band triangle in phase 4, the last SetTImg (addr, fmt,
siz, width), the LoadBlock/LoadTile that filled its tile (tile, uls/ult/lrs/lrt or dxt, tmem),
SetTile line/size/mask, and the owner class of [addr, addr+bytes) against the frame's CI, ZI and
heap range (rdram 0x801163E4, heap head from [g1d-heapcap]). Run 16:9 and 21:9 in one invocation
(ab.py pattern). Outcomes: 21:9 addr range overlaps CI/ZI/heap and 16:9 does not -> H-src-overlap
(name the allocator that put the texture there); same addr, larger load extent -> H-load-geometry;
a draw whose tile was never loaded this frame -> H-split-draw. Positive control: the census must
print the 16:9 floor's tile load (non-zero bytes) in the same run.
Then fix the named root cause, re-score both widths with g1d_row_noise.py, and send the owner the
before/after 21:9 level-select frames. After that: G3d turning-shake (ITERATION 3c).
