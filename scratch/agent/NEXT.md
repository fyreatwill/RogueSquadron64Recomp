# NEXT (s7944)
HYPOTHESIS-ID: owner-panel-pad-nav
s7943: pad Clear (L1) + Reset (R3 hold 1 s) landed, `zsh tools/s7941_pad_nav_test.zsh` 23/23 + control 21 fail.
0. `python3 tools/crash_reports.py --since 2026-11-25`; fold new SOAK-RESULTS lines.
1. Unit: pixel witness for the new pad hint + status message ("Row cleared" / "Defaults restored") in the drawn panel.
   Extend tools/s7942_pad_cursor_witness.zsh with a hold after clear_idle / r3_hold_idle (ROGUESQ_PAD_NAV_HOLD covers only
   open_idle/down_idle/wrap_idle: add clear_idle and r3_hold_idle to `held`). Screenshot, then check the A row's source
   cell is empty after clear and shows defaults after reset (cell diff against the open_idle shot). Negative control: the
   same crop with the panel closed.
   Hypotheses: H-draw (the live table updates but the panel draws a cached copy until the next frame or never), H-msg
   (rs64_panel_set_msg from the input thread is overwritten by the draw thread).
   If this passes, the pad-nav thread has nothing left that the agent can test. Then take the next G6/G5 item that is not only
   waiting on the owner (CURRENT-TRUTH Next steps).
Limits: no physical PS pad on this host; the owner's feel is the close.
