# NEXT (s7247): WIDEWIN heavy window: stack the crack-free merge (E=16) with the far radius cut R=48
HYPOTHESIS-ID: widewin-heavy-window-cost
State (s7246): flatness gate ROGUESQ_DD_WIDEWIN_MERGE_E (default 0 exact; _C centre, default E) is built. With MERGE=0.4 E=16 the image shows no
seam excess (side seams 23.1 -> 20.1 vs ungated 26.4 -> 38.2, same session), and the window saves -1.28 ms (ungated -2.30) with flight kpx -1.1%.
That is below the -1.5 ms bar. R=48 alone: window -4.12 ms, kpx -3.2% (single run, no hole check yet).
Work unit (ONE soak with two image arms + one timing soak, owner idle >= 180 s, screen unlocked):
1. Image: scratch/s7246/arm.zsh route (copy to scratch/s7247, CW=1260 CH=540, ASP=21:9, 60 s delay, 240 s capture) arms:
   a) R48 alone (ROGUESQ_DD_WIDEWIN_R=48 + _R_TOG=1), b) MERGE=0.4 E=16 + R=48 (both TOG; they share the global tog phase).
   Score with tools/s7245_merge_cracks.py (seams) AND the fraction of rows where far terrain gives way to haze/sky earlier in the on phase
   (holes: R removes cells). Check content_w == 1191 on every arm; discard and rerun an arm whose crop is narrower (s7246 e0/e64 got 631/895).
2. Timing: copy scratch/s7246/s7246_merge_flat_timing.sh; arms r48, e16r48, e16 (repeat for a second run). Scorer tools/s7233_widewin_r.py --merge
   (it prints the s7246 flat summary). For R arms use the non --merge split (wr=) or run both.
Outcomes: H-stack (e16+r48 window <= -3 ms, flight |dkpx| <= 1%, no seam excess, no visible holes) -> owner sheet + OWNER-OPT-INS line (opt-in, 21:9);
H-r48-holes (r48 removes visible far terrain) -> use R=56 (+-0 kpx, -1.94 ms) with E=16 instead; H-overlap (the merge saving disappears once R
removes the far cells, since both act on far cells) -> keep the better single lever; then skirts (vertical strips on merged edges facing
unmerged cells) would be the only way to recover the 45% of merge saving the gate gives up.
Raws are ~35 GB per 240 s capture: delete them after scoring.
