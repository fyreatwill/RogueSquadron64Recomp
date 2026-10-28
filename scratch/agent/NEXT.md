# NEXT: why the same floor triangles tear only at 21:9
HYPOTHESIS-ID: g1d-levelselect-frustum

s6612 named the primitive and ruled out a stride or T derivative that
jumps with width. Do not retune `ROGUESQ_HUD_ANCHOR` or
`ROGUESQ_SHIFT_REGION`. Do not add a cull or a default change. Do not
bring back the DPC byte walker: it scored 0 sane triangles of 3577
(16:9) and 3389 (21:9).

The band x < width/3, y in 170..260, is RDP op `0x0F` (shaded, textured,
z), tile 0, TMEM line 4, fmt 4, siz 0, mask 6. Logged from RT64 after
decode (`rs64_floor_note`). The largest pair is y=249..300 on both
arms. dtde matches (19.5312 vs 19.5314, and the same match on 20.425,
29.790, 31.275, 50.116, -41.655, 15.762, 49.863). Y spans match. X span
and dsdx scale by 1024/796. line stays 4. Guest PC `80007904` is on
every row and is not the writer.

Same-run outer-third dy on rows 180..250: 16:9 = 8.47, 21:9 = 24.55.
Dumps: `scratch/agent/s6612_floor/wide16/fbd/fb_0001400_w796.ppm` and
`wide21/fbd/fb_0001400_w1024.ppm`.

ONE work unit: log the base S and T that `decodeTriangles` already
computes for this same key (op 0x0F, tile 0, line 4), both arms, one
binary, the s6612 runner. Record S at the visible left edge (x=0), not
only the derivative.

- If 21:9's S there is outside the 64-wide mask and 16:9's is inside,
  the wider frustum walks off the texture. Say so. Do not patch yet.
- If both sit inside the mask, walk-off is refuted. The next unit then
  has to name a different difference (coverage, scissor, or which part
  of the triangle is inside x < width/3). Do not invent a writer from
  PC `80007904`.

Negative control: 16:9 floor-band dy stays near 8. Positive control:
21:9 floor-band dy stays above 18. Screen must be unlocked.
