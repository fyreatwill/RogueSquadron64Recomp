# NEXT: does the I4 texel, or an untextured cover, jump between rows?
HYPOTHESIS-ID: g1d-levelselect-texel

s6616 did not select H-s-row or H-shade. Do not retune
`ROGUESQ_HUD_ANCHOR` or `ROGUESQ_SHIFT_REGION`. Do not add a cull or
a default change. Do not log another T, S, or shade luma except as
the walker controls below.

The floor primitive is still op `0x0F`, tile 0, line 4, fmt 4 siz 0
(I4), mask 6, perspective on. Combiner on every closed frame of both
widths: `(T0-0)*SHADE+0`. othermode L alternates `00552230` and
`00552078` on both arms; that is the animation, not the width.
Pooled |ΔS| was 3.93 (16:9) vs 2.69 (21:9). Pooled |Δ shade luma|
was 2.66 vs 3.52. Pixel dy was 5.97 vs 20.0. Logs:
`scratch/agent/s6616_ss/wide16/tex.txt` and `wide21/tex.txt`.
Verdict: `scratch/agent/s6616_ss/verdict.json`.

The pixel is texel times shade. Shade does not track the 3.3x dy.
Three ways the colour can still change between scanlines:

- H-i4. The I4 intensity fetched at the same perspective-correct
  S,T changes by more than twice as much between those scanlines
  on 21:9 as on 16:9.
- H-untex. An untextured triangle or a rectangle covers the sample
  on 21:9 (fraction above 0.15) and not on 16:9 (fraction under
  0.05). The s6616 logger only sees textured triangles.
- H-blender. I4 |Δ| agrees within 25% and untextured coverage
  agrees within 0.05, and the blender equation string differs.
  If the blender strings already differ, that is H-blender on its
  own.

ONE work unit, one binary, both arms, the s6616 runner
(`scratch/agent/s6616_ss_run.py`, `ROGUESQ_LOG_FLOOR=1`), stopping
at 50 good frames so the window matches this run. Same sample
(y in 180..250, x=w/6 and x=5w/6, same edge walk, last floor
triangle wins). Decode the I4 texel the way the RDP fetch does for
fmt 4 / siz 0 at that S,T (TMEM in `rt64_rdp.h`). Intensity is
0..255. Also count untextured triangles and rectangles that cover
the point, and print the blender equation once per arm.

Keep |ΔT| and |Δ shade luma| on the same line. |ΔT| must stay
within 25% of 4.79 vs 4.09. |Δ shade luma| must stay within 25%
of 2.66 vs 3.52. Raw S at y=200 and y=230 must still agree across
widths to about 0.05 (s6616: 23.199 vs 23.215 and 34.814 vs
34.813). dy stays the scene control: 16:9 under 12, 21:9 above 18.
floor_frac near 1, badw 0. Screen must be unlocked.

- If 21:9 untex fraction is above 0.15 and 16:9 is under 0.05,
  this selects H-untex. Say so. Do not patch yet.
- If 21:9 |ΔI| is more than twice 16:9 and untex agrees, this
  selects H-i4. Say so. Do not patch yet.
- If the blender strings differ, this selects H-blender. Quote
  both. Do not patch yet.
- If |ΔI| agrees within 25%, untex fractions agree within 0.05,
  and the blender strings match, H-i4, H-untex and H-blender are
  refuted.
