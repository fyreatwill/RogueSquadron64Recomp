# NEXT: 21:9 abort post-wipe black hold (frame turns bright ~0.4 s where 4:3/retail hold black)
HYPOTHESIS-ID: g3-wide-abort-hold

State (s6844): the right-to-left wipe now draws at 21:9 (rs64_g1d_rect_wrap clamps the wrapped lr.x 0 -> 1023.75; same-build
A/B 4 vs 0 wipe frames). After the sweep, 4:3 draws cc 11FE23:FFFFF7FB texrect ti 0x4D3F90 ul 0 lr 512 s 0 (full black,
VI 6743/6745) and holds black ~0.4 s before the hangar. At 21:9 (scratch/s6841/p21x/port.bin, tool scratch/s6844/blackrects.py
<bin> <vi_lo>) the last sweep step is ul 0 lr 982.75 s=375 and the hold rects are ul 0 lr 914.5/915.5 s=511/509, and the window
shows bright flight (scratch/s6844/p21on burst 113.50-113.85 s).

Hypotheses:
- H-clip: the game's texrect helper clips a negative/overflowed ul.x by moving s and lr (it computes in 10-bit or signed
  12-bit space), so at width 1024 the hold rect's s lands outside the soft-edge texture (alpha 0) -> transparent.
- H-wrap2: lr = 1024 + k is written and the helper subtracts as signed 12-bit, producing lr 914/982.
- H-other: the bright frames are a different missing draw (fb not swapped) and the texrects are a side issue.

Discriminator (offline first, then ONE build): find the game function that emits prim 000000FF + cc 119623/11FE23 texrects
(grep RecompiledFuncs for the 0xE4/0xE5 texrect word builder fed by the abort state; or watch the DL buffer word with
ROGUESQ_STORE_WATCH on the swap where ul.x jumps to 0). Read its clip math against w=512 vs w=1024. If H-clip/H-wrap2: fix
it in the game-side G1d patch set (fixup script) or extend rs64_g1d_rect_wrap to rebuild the hold rect (ul 0, lr 1023.75,
s 0) on >1023-wide images, A/B in one build like s6844 (ROGUESQ_G1D_RECT_WRAP=0 arm). Positive control: band score of the
burst frames after the wipe (4:3 = all bands 0).
Budget: 2 iterations. If unresolved, park (cosmetic ~0.4 s) and take the next ladder rung.
