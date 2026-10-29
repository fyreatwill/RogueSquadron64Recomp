# NEXT: does outer-third S or shade jump between rows?
HYPOTHESIS-ID: g1d-levelselect-texel

s6615 refuted H-t-row and H-overdraw. Do not retune
`ROGUESQ_HUD_ANCHOR` or `ROGUESQ_SHIFT_REGION`. Do not add a cull or
a default change. Do not log another texel T, another base-S at x=0,
or another coverage union. Do not treat the higher 21:9 multi_frac
(median 0.38 vs 0.007) as a different primitive: other_frac was 0,
and the last-writer T still matched.

The floor primitive is still op `0x0F`, tile 0, line 4, perspective
on. Every closed frame covers both sample columns (floor_frac 1,
badw 0, npair 140). dy was 5.42 (16:9) and 24.82 (21:9). Raw texels
at y=200 and y=230 agree to about 0.05, and dtdx scales by about
796/1024. Logs: `scratch/agent/s6615_tex/wide16/tex.txt` and
`wide21/tex.txt`. Verdict: `scratch/agent/s6615_tex/verdict.json`.

The tear is inside those covered pixels, and it is not T. Three ways
the colour can still change between scanlines:

- H-s-row. Perspective-correct S at x=w/6 and x=5w/6 changes by many
  texels from one scanline to the next on 21:9, and not on 16:9.
  s6613 cancelled S only at x=0.
- H-shade. S agrees, and the shade luma of the same floor triangle
  changes by more than twice as much between those scanlines on 21:9.
- H-neither. S and shade both agree within 25%. The split is not the
  floor plane's S, T, or shade. The following unit then has to name
  a combiner, blender, or prim/env difference. If the combiner
  equation string already differs between the two widths, that is
  H-combiner on its own.

ONE work unit, one binary, both arms, the s6615 runner
(`scratch/agent/s6615_tex_run.py`, `ROGUESQ_LOG_FLOOR=1`). Extend the
same sample (y in 180..250, x=w/6 and x=5w/6, same edge walk, last
floor triangle wins). S is (S/W)*1024 with
S = baseS + dsde*(y-yFloor) + dsdx*(x-XH) and the same W used for T.
Shade luma is 0.2126 R + 0.7152 G + 0.0722 B from
base + colorDe*(y-yFloor) + colorDx*(x-XH). baseColor is local to
the shaded block in `rt64_gbi_rdp.cpp`; pass those three floats out.
Also print the decoded colour-combiner equation and othermode L for
that floor triangle, once per arm. Keep the s6615 |ΔT| on the same
line as a walker control: it must still agree within 25%.

Print, per arm, mean |ΔS| and mean |Δ shade luma|.

- If 21:9 |ΔS| is more than twice 16:9 and |Δluma| agrees within
  25%, this selects H-s-row. Say so. Do not patch yet.
- If 21:9 |Δluma| is more than twice 16:9 and |ΔS| agrees within
  25%, this selects H-shade. Say so. Do not patch yet.
- If the combiner strings differ, this selects H-combiner. Quote
  both equations. Do not patch yet.
- If |ΔS| and |Δluma| both agree within 25% and the combiner
  strings match, H-s-row and H-shade are refuted.

Sample points must still be covered (floor_frac near 1, badw 0).
That is the instrument control. |ΔT| staying within 25% of the
s6615 pair (4.32 vs 3.63) is the walker control. dy stays the scene
control: 16:9 under 12, 21:9 above 18. Screen must be unlocked.
