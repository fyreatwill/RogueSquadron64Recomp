# NEXT (s7942)
HYPOTHESIS-ID: owner-panel-pad-nav
s7941 landed pad-only navigation for the F6 panel (main.cpp rs64_panel_pad_step, panel row cursor g_pad_row):
touchpad click / Share(Back)+Start opens; D-pad rows, Cross=Bind, Square=Add, Triangle=Save, Circle closes, held buttons masked
from the game until released. `zsh tools/s7941_pad_nav_test.zsh` = on 16/16 + ROGUESQ_PANEL_PAD=0 control fail=14.
0. `python3 tools/crash_reports.py --since 2026-11-25`; fold new SOAK-RESULTS lines.
1. Unit: (a) VISUAL witness that the pad cursor is drawn where the log says: one run, panel opened by the synthetic pad,
   cursor moved to row 1 then row 17 (scrolls the table), window screenshot per step (tools/winctl or screencapture -l <wid>),
   measure the highlight band's y against [panel-rect]-style row rects (add a ROGUESQ_PANEL_RECTS rect for the cursor row).
   Hypotheses: H-ok (band on the logged row, scrolls into view at row 17), H-clip (row 17 off-screen: SetScrollHereY placed
   before the row's content height is known), H-none (RowBg1 overridden by ImGuiTableFlags_RowBg alternation).
   (b) the pad still cannot Clear a row or Reset to defaults: decide if L1 = Clear row (with the Clear text shown) and a 1 s
   Options/Start hold = Reset are worth adding; Start is the open chord's second half, so prefer a dedicated hold on R3
   (unbound by default) and test the hold is not a bind source while a capture is armed.
Limits: no physical PS pad on this host (virtual SDL pad only); the owner's feel is the close.
