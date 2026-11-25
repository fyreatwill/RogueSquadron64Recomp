# NEXT (s7939)
HYPOTHESIS-ID: owner-panel-fullscreen-scale
s7937 verified F6 panel clicks with real HID events only at a 640x480 window (fb == win, 1x). The owner plays FULLSCREEN
(ROGUESQ_FULLSCREEN=1, ASPECT=16:9) on Retina / TV displays, where drawable != window points. s7938 confirmed Cmd+Ctrl+F
toggles fullscreen with real keys (tools/s7938_hotkeys_e2e.zsh).
0. `python3 tools/crash_reports.py --since 2026-11-25`; fold new SOAK-RESULTS lines.
1. Unit: run tools/s7937_panel_e2e.zsh logic with ROGUESQ_FULLSCREEN=1 (and a second arm ROGUESQ_RETINA=1), CLICK_MODE=hid.
   Hypotheses: H-ok (clicks land: ImGui uses window points, [panel-rect] disp == window points), H-scale (ImGui display size is
   drawable pixels -> click lands at 2x offset, C1 FAIL), H-offset (fullscreen has no title bar but the script's
   bounds.h - disp.h offset assumes one -> vertical miss).
   Discriminator: per arm, [panel-rect] disp vs `winctl find` bounds and C1/S1 pass/fail; the windowed arm in the same session is
   the positive control (must stay 8/8). If H-scale/H-offset is a harness bug, fix pt(); if the panel itself mis-maps mouse at
   Retina, fix rs64_controls_panel.cpp.
