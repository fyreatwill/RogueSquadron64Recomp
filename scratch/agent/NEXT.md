# NEXT: 21:9 hole fixes on L4 and L15 (G3 ladder, item 29 follow-up; L6 s7136 and L1 s7139 clean)
HYPOTHESIS-ID: g3-wide-holes-levels
State (s7139): L1 (fadeH 8) at 21:9 dd4 FPS60: fixes on 0/111 flight swaps with unpainted px; SKYFILL=0 control 95/107 (max 1020, 1 px
bottom/right strips in banked dives). Fill colour equals the skirt top within 4/255. L4 (water level) and L15 have other sky HOBs.
Hypotheses:
- H-clean: L4/L15 fixes-on arms show 0 unpainted px per flight swap while the SKYFILL=0 arm shows >0.
- H-newclass: a fixes-on arm shows holes (then streamseq that swap: which object/rect is missing).
- H-seam: the clear colour (table +0x24) differs visibly from that level's skirt top colour (TRIC alpha-FF in streamseq).
Run (one game at a time; each arm ~5.5 min, stream ~9.4 GB, delete .cap/.raw after post; disk ~63 GB free):
  env CW=504 CH=216 zsh tools/s7138_arm.zsh 4 Y1L4 "ROGUESQ_ASPECT=21:9 ROGUESQ_G5B_FRAME_MAX_MB=9000" 120 180
  env CW=504 CH=216 zsh tools/s7138_arm.zsh 4 Z1L4 "ROGUESQ_ASPECT=21:9 ROGUESQ_HORIZON_SKYFILL=0 ROGUESQ_G5B_FRAME_MAX_MB=9000" 120 180
  (then the same for 15). Flight start: first non-"no sky" swap in tools/s7138_bindegen.py output.
  zsh tools/s7139_post.zsh scratch/s7138 Y1L4 <flightstart>; same for Z1L4; per-swap holes from <name>r.log ($12-$10).
  Pose-match with tools/s7135_campitch.py, sheet with tools/s7136_sheet.py; colour check with tools/s7138_streamseq.py on a corner swap.
Control: the SKYFILL=0 arm must show >0 or the fixes-on 0 is not a result. Owner save rule applies. CURRENT-TRUTH ~59.5 KB: keep edits net-zero.
