# NEXT (s7940)
HYPOTHESIS-ID: owner-panel-overlay-coexist
s7939: F6 panel real-HID clicks pass 9/9 at 4:3, 16:9 high-DPI window, 16:9 and 21:9 fullscreen (ImGui = window points).
Queued soak s7939_panel_fs169 re-checks the fullscreen arm (idle-gated); fold its verdict.
0. `python3 tools/crash_reports.py --since 2026-11-25`; fold new SOAK-RESULTS lines.
1. Unit: F1 (RT64 developer overlay) and F6 (our panel) both draw with ImGui. Drive with REAL keys (build/winctl, as in
   tools/s7937_panel_e2e.zsh): F1 open, F6 open, click Bind A, press P, Esc, F1 close, in the owner recipe
   (PANEL_ASPECT=16:9 PANEL_FS=1). Hypotheses: H-ok (both coexist, the click arms capture, Esc closes only F6),
   H-steal (the RT64 overlay window takes the mouse/keys: C1 or C2 FAIL with F1 open), H-leak (with F1 open the game gets
   input while F6 is open). Control: the same sequence without F1 in the same session (must be 9/9).
   If H-steal/H-leak: fix the input routing in rs64_controls_panel.cpp / the event filter in main.cpp.
Limits not testable here: an external 1x display or a move between displays of different scale (no second display).
