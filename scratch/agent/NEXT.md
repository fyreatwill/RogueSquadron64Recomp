# NEXT: do fill color or shade alpha step with the tear?
HYPOTHESIS-ID: g1d-levelselect-texel

s6619 refuted H-last. At x=16 and x=w-17, y 180..250, the last
primitive is the floor triangle on every sample of both widths
(lastF 1.0 vs 1.0, both columns). A fill rect touches every sample
first (touchR 1.0, touchU 0, over 1.0). Median multi_frac is 0 on
16:9 and 0.18 on 21:9, so most torn pixels are one floor triangle
over that fill. The floor blend is
`cyc0f0(CC*CCA+MEM*MEMA)|(CC*CCA+MEM*MEMA)`.
Filtered I4 and shade luma do not carry the row step.
Do not retune `ROGUESQ_HUD_ANCHOR` or `ROGUESQ_SHIFT_REGION`.
Do not add a cull or a default change. Do not sample x=w/6.
Logs: `scratch/agent/s6619_last/verdict.json`.

The blend is CC*CCA + MEM*MEMA. CC's inputs agree. What is left:

- H-mem. The fill word under the triangle (color and its alpha bits)
  changes from row to row on 21:9 only.
- H-alpha. Shade alpha, or the alpha combiner, changes from row to
  row on 21:9 only. Memory does not.
- H-pipe. Fill word, shade alpha, and the alpha combiner agree.
  The tear is RT64's raster or blender. Coverage is part of this
  until a later pass can log it.

ONE work unit, one binary, both arms, the s6619 runner
(`scratch/agent/s6619_last_run.py`, `ROGUESQ_LOG_FLOOR=1`), stopping
at 50 good frames. Keep the sample at x=16 and x=w-17, y 180..250.

Pass three new values into the existing hooks. `drawRect` already
sees `fillColorStack`. Stamp that word on each sample a FILL rect
covers. The triangle decoder already has `baseColor.w`, `colorDe.w`,
and `colorDx.w` and does not pass them. Stamp shade alpha the same
way as shade luma: base + De*(y-yFloor) + Dx*(x-XH), last floor
triangle wins. Log the alpha combiner beside the color combiner
(`decodeAlphaInput`, same shape as `rs64_cc_equation`). A lib/ edit
needs `./submodule-patches/export.sh` in this same iteration.

On each closed frame emit, over the 142 samples: the number of
distinct fill words, the fill word if there is only one, mean
|Δ shade alpha|, and the alpha combiner string.

Positive controls, same run:
- lastF 1.0 on both, touchR 1.0, over 1.0, touchU 0.
- Outer-third dy: 16:9 under 12, 21:9 above 18.
- Pixel |Δ| at x=16 and x=w-17, fb nearest 1400: 16:9 under 12,
  21:9 above 30.
- |ΔI| within 25% of 45.21 vs 42.15. |Δ shade| within 25% of
  2.95 vs 2.96. Combiner still `(T0-0)*SHADE+0`. Floor blender
  string unchanged. Screen unlocked. `[floor-i4] selftest ok`.

- If 21:9 has more than one fill word, or its fill-word row step
  is more than twice the 16:9 step, this selects H-mem. Do not patch.
- If the fill word is one constant on both and |Δ shade alpha| is
  more than twice on 21:9, or the alpha combiner string differs,
  this selects H-alpha. Do not patch.
- If the fill word is one constant on both, |Δ shade alpha| agrees
  within 25%, and the alpha combiner string matches, H-mem and
  H-alpha are refuted. The tear is the pixel pipe. Do not patch.
