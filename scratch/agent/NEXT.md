# NEXT: G5f at 21:9 (owner's ultrawide) — W clamp off vs on, same run, dd4 L4
HYPOTHESIS-ID: g5f-219
Context: s7005 owner sheet at dd4 L4 16:9: 100+ px lines 145 -> 26 (T40) / 252 -> 34 (T20), 0 of 24 viewed clamp-on candidates are knife lines.
G5f has never been measured at 21:9, where the viewport is wider (s6142 w<=1024) and the W_SHEET_PX=200 limit and guard band may behave differently.
Hypotheses: H-holds (same 5x drop, 0 clamp-on knife lines at 21:9), H-wide (wider viewport lets knife tris pass the clamp: clamp-on knife lines),
H-holes (the clamp drops tris that are real at 21:9 and leaves holes: check every in-flight ROGUESQ_W_SHEET_DROPLOG drop's frame).
Unit: copy scratch/s7005/arm.zsh to scratch/s7006 (sed s7005->s7006); run
`env CULL=1 ASP=21:9 zsh scratch/s7006/arm.zsh 4 4 s1 "ROGUESQ_W_CLAMP=tog ROGUESQ_W_SHEET_DROPLOG=$PWD/scratch/s7006/drops_s1.txt" 120 90`.
Check `[ddscene] level=4 on=1`, multiplier 4, and the capture size in cap_s1.txt (g5b_capture takes w h args: use a 21:9 size, e.g. 1260 540, if 960x540
squashes; check the window line). Detect with scratch/s6906/g5f_lines at T=40 and T=20 (control >= 70%), find the last flight frame from a thumbnail strip.
Sheet: `python3 tools/g5f_owner_sheet.py s1.raw lines_s1.txt docs/owner_sheet_s7006_g5f_219.png <maxf> 6 100`. View every clamp-on single-frame 100+ candidate
at phase 0.05-0.95 (toggle-edge frames belong to the previous second, s7005). Delete the raw.
Outcomes: H-holds -> G5f closes on the owner's look at all aspects; H-wide -> log the escaping tris (W signs, screen coords) via a G5F_ESCAPE dump in rt64
in the same build; H-holes -> tighten the drop rule.
