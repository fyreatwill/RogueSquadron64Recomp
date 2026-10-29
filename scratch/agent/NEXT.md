# NEXT: does the outer-third texel T jump between rows?
HYPOTHESIS-ID: g1d-levelselect-texel

s6614 refuted missing coverage. Do not retune `ROGUESQ_HUD_ANCHOR` or
`ROGUESQ_SHIFT_REGION`. Do not add a cull or a default change. Do not
treat guest PC `80007904` as the writer. Do not log another base-S at
x=0, and do not build another coverage union.

The floor primitive is still op `0x0F`, tile 0, line 4, mask 6,
perspective on, shift 0, uls 0. Every closed frame covers scanlines
180..250 across both outer thirds (hole_rows 0, hull_frac 1, mean hull
265 at 796 and 341 at 1024). Scissor is the framebuffer. dy on this
run was 7.61 (16:9) and 26.08 (21:9). Logs:
`scratch/agent/s6614_cov/wide16/cov.txt` and `wide21/cov.txt`.

The tear is inside those covered pixels. Three ways that happens:

- H-t-row. Perspective-correct T at the outer third changes by many
  texels from one scanline to the next on 21:9, and not on 16:9.
  dtde of the paired center triangles already matches (s6612); this
  is T at the outer-third sample, where dtdx * x can diverge.
- H-overdraw. A triangle that is not op `0x0F` tile 0 line 4 covers
  the same sample on 21:9 and not on 16:9, and it writes the slices.
- H-same-texel. T matches across the two widths and no other triangle
  covers the sample. The floor sampler input is not the split. The
  following unit then has to name a combiner or shade difference.

ONE work unit, one binary, both arms, the s6614 runner
(`scratch/agent/s6614_cov_run.py`, `ROGUESQ_LOG_FLOOR=1`). At each
scanline y in 180..250, at x=w/6 and x=5w/6, evaluate the floor
triangle that covers that point. T at screen x is t0 + dtdx*x and
W at screen x is w0 + dwdx*x (dwdx is texcoordDx[2], which the s6613
note does not receive). The texel is (T/W)*1024 when perspective is
on, the same quantity s6613 used at x=0. Also count how many
non-floor textured triangles cover that point, using the same edge
walk. Print, per arm, mean |Δ texel T| between consecutive scanlines
and the fraction of sample points with a non-floor hit.

- If 21:9 |ΔT| is more than twice 16:9 and the non-floor fraction is
  near 0 on both, this selects H-t-row. Say so. Do not patch yet.
- If the non-floor fraction is high only on 21:9, this selects
  H-overdraw. Say which op/tile/line. Do not patch yet.
- If |ΔT| agrees within 25% and the non-floor fraction is near 0,
  H-t-row and H-overdraw are refuted.

Sample points must actually be covered (floor hit fraction near 1).
That is the instrument control. x0spans staying above 0 is not it.
dy stays the scene control: mean of per-pixel |row-to-row luma| on
the outer thirds, rows 180..250. 16:9 stays under 12 (this run was
7.61; the s6613 dumps score 5.48 on this scorer). 21:9 stays above
18. Screen must be unlocked.
