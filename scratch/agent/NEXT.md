# NEXT: which primitive writes the torn edge pixels last?
HYPOTHESIS-ID: g1d-levelselect-texel

s6618 refuted H-i4-edge and H-shade-edge at x=16 and x=w-17.
Filtered I4 |Δ| is 46.03 vs 41.18. Shade |Δ| is 2.94 vs 2.97.
The floor blender string matches. Pixel |Δ| on the same fb 1400
is 5.71/5.04 vs 54.37/51.82. The tear is after the combiner.
Do not retune `ROGUESQ_HUD_ANCHOR` or `ROGUESQ_SHIFT_REGION`.
Do not add a cull or a default change. Do not sample x=w/6.
Logs: `scratch/agent/s6618_edge/verdict.json`.

Untex fraction is 1.0 on both widths. That only says a rect or an
untextured primitive touches the point at some time. It does not
say who writes last. Do not use that fraction as a discriminator.

ONE work unit, one binary, both arms, the s6618 runner
(`scratch/agent/s6618_edge_run.py`, `ROGUESQ_LOG_FLOOR=1`), stopping
at 50 good frames. Keep the sample at x=16 and x=w-17, y 180..250,
last primitive wins. On each sample record the class of that last
primitive: floor triangle (op 0x0F tile 0 line 4), any other
triangle, or a rect/fill. Emit the fraction of the 142 samples in
each class.

Positive controls, same run:
- Outer-third dy: 16:9 under 12, 21:9 above 18.
- Pixel |Δ| at x=16 and at x=w-17, fb nearest 1400: 16:9 under 12,
  21:9 above 30. If 21:9 is under 30, the sample missed the edge.
- |ΔI| within 25% of 46.03 vs 41.18, |Δ shade| within 25% of
  2.94 vs 2.97, combiner still `(T0-0)*SHADE+0`, floor blender
  string unchanged, floor_frac near 1, badw 0, x0=16, x1=w-17.
  Screen unlocked. `[floor-i4] selftest ok` still prints.

- If the floor-last fraction differs by more than 0.25 and the
  rect-last fraction makes up that gap, this selects H-last.
  Say which width ends on the floor triangle. Do not patch yet.
- If both widths are floor-last on at least 0.90 of the samples,
  H-last is refuted. The tear is the blend memory term or the
  pixel pipe after this triangle. Say so. Do not patch yet.
- If both widths are rect-last on at least 0.90 of the samples,
  the rect is the surface that shows the tear. Say so. Do not
  patch yet.
