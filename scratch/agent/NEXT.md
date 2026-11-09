# NEXT: G5f owner sheet — knife lines with the clamp off vs on, same run, dd4 and dd2
HYPOTHESIS-ID: g5f-owner-sheet
Context: G5f measurements are done (s7002 dd4 L4, s7003 dd1 L4, s7004 dd2 L7: clamp-on has fewer long lines in every run, drops leave
no holes per ROGUESQ_W_SHEET_DROPLOG). The item closes on "spike count + owner sheet". No owner sheet exists yet.
Unit: one capture at LEVEL=4 dd4 16:9 FPS60 (`env CULL=1 zsh scratch/s7004/arm.zsh 4 4 s1 "ROGUESQ_W_CLAMP=tog" 120 90`, copy arm.zsh to
scratch/s7005 first; check `[ddscene] level=4`, multiplier 4). Score with scratch/s6906/g5f_lines s1.raw lines_s1.txt 40 20 50 (control >= 85%),
keep frames < the first non-flight frame (make a thumbnail strip first: L7 autopilot crashed ~75 s in, s7004).
Sheet: 6 clamp-off 100+ px knife lines (each f-1/f/f+1 crop) beside 6 clamp-on frames from adjacent odd seconds at a similar view
(scratch/s6906/crop.py; scratch/s7004/strip.py for full frames), plus the per-bucket table, saved to docs/owner_sheet_s7005_g5f.png.
Outcomes: sheet shows knife lines only in off frames -> G5f awaits the owner's look; if an on frame shows a knife line -> H-escape, log that
tri (W signs, texturePerspective) with a G5F_ESCAPE dump in the same build. Delete the raw.
