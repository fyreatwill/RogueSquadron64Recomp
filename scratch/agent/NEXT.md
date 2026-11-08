# NEXT: G5b outer ring 7 near diagonals — offline, from existing traces (no new run needed first)
HYPOTHESIS-ID: g5b-ring7-diagonal
Context: s7000 showed the s6901 FWDWIN fix removes heading-driven far loss on L7 (dips 36 -> 0, ring 5/6 0/3) as on L4/L1/L5.
One leftover from s6901: ring 7 dips ROSE armed on L4 (47 -> 107) and L1 (31 -> 79), flat on L7 (72 -> 77) and L5 (62 -> 56).
s6901 guessed "a square window's per-axis reach is shorter at diagonals". Traces: scratch/s6901/{tg,g3e}_{f4,fw,f2,l1,l5}.txt,
scratch/s7000/{tg,g3e}_d4.txt. Score with tools/g5b_fwdwin_seamless.py <dir> <arm> (drops the flip seam).
Hypotheses:
- H-diag: armed ring-7 dips cluster at headings 45/135/225/315 +-15 (square window corner geometry); off dips do not.
- H-edge: ring-7 dips track the window touching the map/bounds edge (win x or z at the clamp limit), any heading.
- H-noise: ring 7 holds few quads (ref median near the 60 threshold), so dips are threshold noise; dips vanish at threshold 120.
Discriminator, one offline script over all six arms: per ring-7 dip, heading, window w/h and position vs pre-clamp bounds
(site 13), ring-7 ref median. If H-diag: fix is a centre offset along the diagonal (or a 64x64 rotated placement) in
tools/apply_s6901_fwdwin.py, then one same-run =tog arm on L4 dd4 to confirm. If H-noise: close the item in CURRENT-TRUTH.
