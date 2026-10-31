# NEXT: 21:9 level-select tear — which RT64 depth step rejects the floor at w=1024
HYPOTHESIS-ID: g1d-levelselect-rt64-depth

s6692: RDP input is equivalent at 16:9/21:9 (same floor loads, ~1000 lower tris z-compare on, Z in
range, one full-screen depth clear FFFCFFFC 0..W-1 x 0..339 per frame); CULL_SPIKE=0 still torn; only
RT64 native-swap writes the depth rows. Frames: scratch/agent/s6692_floorsrc/t21.png (floor + front
console ring missing) vs t16.png. Harness: scratch/agent/s6692_floorsrc/ab.py (census in run.log).

Hypotheses (all in lib/rt64; edits need submodule-patches/export.sh + commit):
- H-reload: after the depth clear, RT64 reloads depth from RDRAM (copyFromChanges / RAM->native
  upload) and the RDRAM image holds last frame's (or partial) depth, so near geometry fails the test.
  s6625 saw copyFromChanges replace cleared pixels (single-source).
- H-size: RT64 sizes the depth target from cimg width but the fill/clear covers 340 rows and the
  write-back covers 339 (depth-read h=339) — row/stride mismatch at 1024 shifts the depth by rows.
- H-writeback: native-swap depth write-back granularity (35840 B chunks = 17.5 rows at w1024)
  leaves half-rows that the next frame's reload treats as changed.
Discriminator (one build, two env arms, same run pair): an RT64 env kill-switch that skips the
RAM->depth reload for the depth image (or forces a GPU-side clear after any reload), run 21:9 with
and without it, score with g1d_row_noise.py. Torn->clean selects H-reload; still torn -> log the
depth target dims vs fill rect (H-size). Positive control: the 16:9 arm stays clean with the switch on.
Then send owner the before/after 21:9 level-select frames. After that: G3d turning-shake.
