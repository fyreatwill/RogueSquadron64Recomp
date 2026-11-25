# NEXT (s7946)
HYPOTHESIS-ID: owner-panel-21x9
s7945: both pad witnesses PASS at 16:9 fullscreen Retina (cursor 3/3, text 8/8) -> pad thread done for the agent.
0. `python3 tools/crash_reports.py --since 2026-11-25`; fold new SOAK-RESULTS lines.
1. Unit: the owner's other screen is a 21:9 ultrawide. Run, one at a time, windowed 21:9 (this host has no 21:9 display, so
   fullscreen 21:9 cannot be tested; windowed high-DPI is the closest):
     env PANEL_ASPECT=21:9 PANEL_FS=0 zsh tools/s7942_pad_cursor_witness.zsh
     env PANEL_ASPECT=21:9 PANEL_FS=0 zsh tools/s7944_pad_text_witness.zsh
     env PANEL_ASPECT=21:9 PANEL_FS=0 zsh tools/s7937_panel_e2e.zsh   (mouse/key path)
   Hypotheses: H-ok (all pass), H-title (windowed high-DPI: title = wh - disp_h must be ~28 pt; checker crop off by it),
   H-layout (a short/wide window: row 17 scroll or message line clipped by the window height -> fix panel layout).
   Discriminator: logged rects vs bands/text found in the PNGs, plus window size vs display.
   If all pass, the F6 panel is qualified on every owner screen shape; then take the next agent-testable G6/G5 item
   (CURRENT-TRUTH Next steps), not one waiting only on the owner.
Limits: no physical PS pad; the owner's feel closes G6b.
