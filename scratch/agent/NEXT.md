# NEXT: G3 in-flight pause menu at 21:9, owner recipe (CURRENT-TRUTH item 38)
HYPOTHESIS-ID: g3-pause-menu-219
State (s7149): the whole mission intro (space, sea cinematic, flight) is RT64 == angrylion at 21:9 after one fit (<= 0.005);
ROGUESQ_VI_EXACT_ROWS=1 is worse in every phase and stays opt-in. The pause menu was matched at 4:3 only (s6778, retail oracle);
at 21:9 it is a 2D overlay (emblem + text boxes) on the 1024 fb, i.e. the texrect path that s7142 RECT_ASPECT fixed for menus.
Route: s7149 route reaches flight at swap ~13520, flight shown until the 275 s end. Add a START press late in flight.
Step 1 (one run): env RDIR=s7150 ASP=21:9 SECS=300 FROM=13300 EVERY=5 DL=150 DU=115 \
  AP=6:start,11:start,16:start,21:start,25:left,27:start,33:start,40:right,46:left,52:right,58:left,64:a,262:start zsh tools/s7146_arm.zsh P1 ""
  Check the pause menu is in the capture (op census tools/s7146_opcensus.py: texrect count jumps; or eyeball one presented frame). If the
  start press landed in a cutscene, move it later (268) and rerun once.
Step 2: zsh tools/s7141_post.zsh scratch/s7150 P1 0,11,469,216 117,352; split frames into flight-before / pause-open by swap;
  tools/s7148_pfsearch.py per phase; scratch/s7149/fitrun.py pattern (copy, D=scratch/s7150) with JE 0.976..1.0, JY -4..4, JX 0..2.
  Boxes: all, centre, left, right, plus text-box rects read off the presented frame. Delete .cap after scoring.
Hypotheses / outcomes:
  H-equal: pause frames reach the flight floor (<= ~0.005 fitted) with the same (e, sx, sy) as flight -> close item 38, owner sheet.
  H-rect-diff: text boxes / emblem score above the floor with a width mismatch (RECT_ASPECT path wrong for this overlay) -> fix in
    rt64 rect path (export.sh + commit after any lib/ edit).
  H-hud-anchor: the flight HUD (shifted by g1d anchor) is drawn under/over the open pause window in one renderer only.
Owner save rule: no SAVE_FROM; NO_SAVE_WRITE stays. Keep CURRENT-TRUTH under 60000 B (58.8 KB now).
