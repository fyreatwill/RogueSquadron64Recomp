# NEXT: 21:9 level-select tear
HYPOTHESIS-ID: g1d-levelselect-tear

s6610 closed the flight-radar clip. Do not retune `ROGUESQ_HUD_ANCHOR` or
`ROGUESQ_SHIFT_REGION`. The open opt-in defect is the 21:9 level-select
tear: VI-bounded source and the paired window, frames n=1400/1500/1600,
absent from 16:9 and retail level-select and from later 21:9 bay/flight
(s6609). The s6610 run wrote the same frames again:

- torn candidates: `scratch/agent/s6610_hud_anchor/wide21/fbd/fb_0001400_w1024.ppm`
  and n=1500, n=1600
- clean 1024 control, same run: `fb_0002500_w1024.ppm` (flight, ring inset 31)
- 16:9 level-select control, not torn in s6609:
  `scratch/agent/s6608_capture_bounds/wide16/fbd/fb_0001400_w796.ppm`

ONE work unit, offline, no rebuild. For each frame, per row, record the
column of the strongest horizontal step and whether that column is stable
down the frame.

Hypotheses:
- H-stride: the step's x changes linearly with y (a shear). Slope times
  bytes-per-pixel equals a stride error (1024-wide row vs 640 or 512).
  The clean flight frame must not shear.
- H-composite: one y-band (around rows 150-260) has a stable vertical step,
  and the segment on one side of it matches a narrower buffer (512 or 640)
  while rows outside the band are one coherent 1024-wide image. Flight
  control has no such band.
- H-game: the step follows a silhouette, not a straight or sheared line,
  in the torn frames only. Then the writer is the level-select draw, and
  the next unit names that draw. No copy fix.

Positive control, same script: copy the clean flight frame, paste a
200-row-tall 640-wide block into its middle, and the metric must flag
that band and must not flag the untouched flight frame. If both the
synthetic band and the real level-select frame score the same class,
that class is the writer family. If the real frame scores nothing, the
metric is blind — do not add another field; look at the rows.

No cull, skip, or default change. Do not run the game unless the three
existing 1024 frames are missing or not actually level-select (check
the shot json phase/width first).
