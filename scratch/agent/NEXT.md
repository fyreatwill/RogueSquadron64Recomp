# NEXT: G5f at dd2 on a second level (L7) — does the default W clamp still remove knife lines without new holes?
HYPOTHESIS-ID: g5f-dd2-l7
Context: s7002 (dd4 L4) and s7003 (dd1 L4) showed the clamp removes knife lines and its kept slivers are real. Every G5f
measure so far is LEVEL=4. dd2 is an owner recipe ("dd2 fewer but not gone") and L7 is a dense terrain level (s7000).
Hypotheses:
- H-holds: clamp on has fewer 60+ px lines than off in >= 4/5 windows, and on-block lines viewed are real geometry.
- H-level: L7 terrain gives mixed-sign tris > 200 px the drop rule removes visibly (clamp-on block shows sliver holes /
  more 20-39 px lines than off, and [wsheet] dropped >> s7003's 3).
- H-escape: clamp-on 100+ lines viewed are still knife lines (wedges the clamp misses: non-perspective or all-W<=0 path).
Discriminator, ONE run: `env CULL=1 zsh scratch/s7003/arm.zsh 7 2 d1 "ROGUESQ_W_CLAMP=tog ROGUESQ_W_SHEET_STATS=1" 120 90`
(edit the copy into scratch/s7004 first; check run.log `[ddscene] level=7` and `multiplier 2`; disk ~21 GB, 90 s = 9.5 GB).
Score: scratch/s6906/g5f_lines d1.raw lines_d1.txt 40 20 50 (control >= 85%), python3 tools/g5f_short_buckets.py lines_d1.txt;
view 6 per block per bucket (scratch/s6906/crop.py, phase 0.2-0.9, pick script in PORTING-STATE s7003). Delete the raw.
Outcomes: H-holds -> G5f closed at all measured recipes, owner sheet; H-level -> measure dropped-tri spans on L7, consider
raising W_SHEET_PX per dd; H-escape -> log those tris (W signs, texturePerspective) with a G5F_ESCAPE dump in the same build.
