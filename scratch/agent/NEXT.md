# NEXT (s7869)
HYPOTHESIS-ID: g3-det-prefix-render
First: `python3 tools/crash_reports.py --since 2026-11-13 | grep -v '^FOLDED'`, owner answers in docs/OWNER-REVIEW-QUEUE.md, new
SOAK-RESULTS lines. A crash or owner report outranks this.
State (s7868): det-exact ticks are a per-frame render oracle. Bonus 17: 1120/1120 frames of the matched prefix exact vs retail
(tris + texrects/HUD), plant caught, unpinned p2 fails. Single mission so far.
Unit: widen it to the longest exact mission, 0x31=12 (s7856: 5765 ticks, death t5304 + respawn t5490, 11 song switches,
record 0 diffs), which also covers death/respawn and explosion draws:
  env RBIN=1 zsh tools/s7849_det_pair.sh 12 scratch/s7869/v12      (defaults: BASE_EEP scratch/s7832/lvl.eep, SECS 305, hangar PP/AP)
  python3 tools/s7868_det_frame_cmp.py scratch/s7869/v12/r1/retail.bin scratch/s7869/v12/p1.bin --plant --neg scratch/s7869/v12/p2.bin
Check first that the s7856 recipe used the default PP/AP (grep '^## Session 7856' PORTING-STATE.md); retail.bin may hit the
6000 MB cap: check the cap line and the frame count against ~5765 ticks.
Outcomes: H-clean = one exact run spanning the whole flight (G3 in-flight render CLOSED for exact missions, two lines);
H-render = interior non-exact frames on det-exact ticks -> name the draw (print the differing tris/texrects, find the DL op);
H-align = several exact runs split by non-exact islands with no state diff -> add a tick stamp join (port RDP header w[3] is the
phase ordinal; retail header has vi_width only) before claiming anything.
Then delete the .bin files (keep the txt scores); s7868/v17 bins can go too once v12 is scored.
