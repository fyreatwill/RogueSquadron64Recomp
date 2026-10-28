# NEXT: does the outer third lose floor coverage at 21:9?
HYPOTHESIS-ID: g1d-levelselect-frustum

s6613 refuted a mask walk-off. Do not retune `ROGUESQ_HUD_ANCHOR` or
`ROGUESQ_SHIFT_REGION`. Do not add a cull or a default change. Do not
treat guest PC `80007904` as the writer.

The band is still op `0x0F`, tile 0, line 4, mask 6, perspective on,
shift 0, uls 0. Texel at screen x=0 matches across the two widths
(16/16 paired early-table triangles; 0 walk-off pairs). The 4 triangles
that cover x=0 are inside [0, 64) on both. x_major moves and dsdx
shrinks by 796/1024, so those cancel. Per-pixel outer-third dy on rows
180..250, same scorer that returns 8.32 / 25.4 on the s6612 dumps:
this run was 5.48 (16:9) and 26.9 (21:9). Logs:
`scratch/agent/s6613_st/wide16/floor.txt` and `wide21/floor.txt`.

ONE work unit: from the triangles `rs64_floor_note` already sees, build
the union of covered x intervals on each scanline y in 180..250, for
x in the outer thirds only. Both arms, one binary, the s6613 runner
(`scratch/agent/s6613_st_run.py`, `ROGUESQ_LOG_FLOOR=1`). Print, per
arm, the covered fraction and the count of scanlines that contain a
gap of more than 2 px.

- If 21:9's gap count is higher and 16:9's is near 0, the tear is
  missing coverage (edge walk or scissor). Say so. Do not patch yet.
- If both outer thirds are solid (gap count near 0, fraction near 1),
  coverage is refuted. The tear is inside covered pixels. The next
  unit then has to name a sampler or combiner difference, not another
  base-S log.

Score dy as the mean of per-pixel |row-to-row luma|, not the difference
of the row's mean luma. Negative control: 16:9 stays near 8 (the s6612
dump scores 8.32 on this scorer). Positive control: 21:9 stays above
18. Screen must be unlocked.
