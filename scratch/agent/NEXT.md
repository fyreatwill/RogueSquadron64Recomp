# NEXT: does I4 or shade jump at the torn edge columns?
HYPOTHESIS-ID: g1d-levelselect-texel

s6617 refuted H-i4, H-untex, and H-blender at x=w/6 and x=5w/6.
Do not retune `ROGUESQ_HUD_ANCHOR` or `ROGUESQ_SHIFT_REGION`. Do not
add a cull or a default change. Do not sample x=w/6 again except as
the walker control below.

The floor primitive is still op `0x0F`, tile 0, line 4, fmt 4 siz 0,
bilerp, no TLUT. Combiner `(T0-0)*SHADE+0`. Floor blender
`cyc0f0(CC*CCA+MEM*MEMA)|(CC*CCA+MEM*MEMA)` on every closed frame of
both widths. Pooled |ΔI| at the old sample was 51.18 vs 45.16.
Untex fraction was 1.0 on both because a fill rect and a 2-cycle rect
cover the band; do not treat that fraction as a discriminator again.
Logs: `scratch/agent/s6617_i4/verdict.json`.

On the same fb 1400 dumps the row step is not uniform. x=16 is
3.89 (16:9) vs 46.17 (21:9). x=w-17 is 4.49 vs 46.35. x=w/6 is only
5.86 vs 12.67. The tear that the outer-third mean (5.55 vs 23.11)
is averaging lives in the outer 1/12 of the width.

ONE work unit, one binary, both arms, the s6617 runner
(`scratch/agent/s6617_i4_run.py`, `ROGUESQ_LOG_FLOOR=1`), stopping
at 50 good frames. Move the sample from x=w/6 and x=5w/6 to x=16
and x=w-17 (y still 180..250, same edge walk, last floor triangle
wins). Keep logging |ΔT|, |ΔS|, |Δ shade luma|, |ΔI|, and the blender
string at the NEW columns.

Positive controls, same run:
- Outer-third dy stays the scene control: 16:9 under 12, 21:9 above 18.
- Pixel |Δ| at x=16 and at x=w-17, from that run's fb nearest 1400:
  16:9 under 12, 21:9 above 30. If 21:9 is under 30, the sample missed
  the edge band and the result is instrument-fail.
- |ΔT| within 25% of 4.70 vs 4.15, and the combiner still
  `(T0-0)*SHADE+0`. floor_frac near 1, badw 0, nI near npair.
  Screen unlocked. I4 self-test still prints `[floor-i4] selftest ok`.

- If 21:9 |ΔI| at the edge columns is more than twice 16:9, this
  selects H-i4-edge. Say so. Do not patch yet.
- If 21:9 |Δ shade luma| is more than twice 16:9 and |ΔI| agrees
  within 25%, this selects H-shade-edge. Say so. Do not patch yet.
- If both |ΔI| and |Δ shade luma| agree within 25% and the blender
  strings match, H-i4-edge and H-shade-edge are refuted. The edge
  tear is after the combiner. Say so. Do not patch yet.
