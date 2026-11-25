# NEXT (s7943)
HYPOTHESIS-ID: owner-panel-pad-nav
s7942: pad cursor pixel witness PASS 3/3 (`zsh tools/s7942_pad_cursor_witness.zsh`), label/hint clipping fixed.
0. `python3 tools/crash_reports.py --since 2026-11-25`; fold new SOAK-RESULTS lines.
1. Unit: pad Clear row + Reset to defaults (the pad still cannot do either). Proposal: L1 = Clear the cursor row (hint text
   updated), R3 held 1 s = Reset to defaults (Start is half of the open chord; R3 is unbound by default -- verify in
   rs64_bind_defaults before choosing, else pick another unbound button). Must not act while a capture is armed (then the
   press is a bind source). Extend the s7941 script (ROGUESQ_PAD_NAV_TEST) with: L1 clears row N (sources empty), R3 tap
   does nothing, R3 1 s hold resets (table == defaults), L1/R3 while armed are captured, not acted on; PANEL_PAD=0 control.
   Hypotheses to rule out: H-chord (L1/R3 already consumed elsewhere: grep rs64_panel_pad_step and get_n64_input), H-hold
   (hold timer counts polls, not ms: poll rate varies with game frame rate -> use SDL_GetTicks).
Limits: no physical PS pad on this host; the owner's feel is the close.
