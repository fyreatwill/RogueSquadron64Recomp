# NEXT (s7945)
HYPOTHESIS-ID: owner-panel-pad-nav
s7944: pad Clear/Reset text witness 8/8 at 640x480 windowed (`zsh tools/s7944_pad_text_witness.zsh`).
0. `python3 tools/crash_reports.py --since 2026-11-25`; fold new SOAK-RESULTS lines.
1. Unit: both pad witnesses (tools/s7942_pad_cursor_witness.zsh, tools/s7944_pad_text_witness.zsh) at the OWNER recipe: 16:9
   fullscreen on the Retina display (drawable 2x, FontGlobalScale > 1). See tools/s7937_panel_e2e.zsh PANEL_ASPECT/PANEL_FS for
   the env (ROGUESQ_ASPECT=16:9 ROGUESQ_FULLSCREEN=1); add the same optional env to both witnesses. screencapture -l in
   fullscreen: the window has no title bar (title = wh - disp_h must come out 0) and scale = png_w / win_w should be 2.
   Hypotheses: H-ok (both pass unchanged), H-scale (crop maths off at 2x / no title bar -> fix the checkers, not the panel),
   H-layout (the larger font wraps the source cell or message to 2 lines, so srcA/msg first-line crops miss text -> fix the
   panel layout). Discriminator: the logged rects vs the band/text positions found in the PNG.
   Negative control as before (closed panel). If it passes, the pad thread is DONE for the agent; then take the next G6/G5 item
   that the agent can test (CURRENT-TRUTH Next steps), not one only waiting on the owner.
Limits: no physical PS pad on this host; the owner's feel is the close.
