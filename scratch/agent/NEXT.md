# NEXT (s7941)
HYPOTHESIS-ID: owner-panel-pad-nav
s7940 closed owner-panel-overlay-coexist: RT64's F1 inspector cannot open on macOS (SDL filter never installed, sdlWindow=0x0,
dev mode on or off); panel e2e with F1 pressed 12/12 (`env PANEL_F1=1 PANEL_ASPECT=16:9 PANEL_FS=1 zsh tools/s7937_panel_e2e.zsh`).
0. `python3 tools/crash_reports.py --since 2026-11-25`; fold new SOAK-RESULTS lines.
1. Unit: the F6 panel is mouse-only (rs64_panel_feed feeds ImGui mouse events only; keys deliberately not fed). The owner plays on
   a 65" TV with a PS pad, possibly without a mouse at hand. Measure whether the panel can be OPENED, NAVIGATED and SAVED from the pad
   alone. Hypotheses: H-none (no pad path: a pad user cannot reach Bind/Save; F6 needs a keyboard), H-partial (capture accepts pad
   buttons once armed - s7765 shows pad:a sources - but arming needs the mouse), H-ok (some pad path exists). Read
   src/main/rs64_controls_panel.cpp + rs64_bind_capture_step (main.cpp ~12936) first; boring-first, this is likely H-partial.
   If H-none/H-partial: add opt-in-free pad navigation that cannot clash with binding: e.g. while the panel is open and NO capture
   is armed, D-pad up/down moves a row cursor, Cross = Bind, Square = Add, Triangle = Save, Circle = close (closing must not
   pass the press to the game); a pad combo to open (e.g. Back/Share+Start, check it is unused by get_n64_input). Feed via
   ImGuiConfigFlags_NavEnableGamepad or our own row cursor (simpler, testable by log lines).
   Proof: ROGUESQ_PAD_TEST-style synthetic pad events (rs64_pad_test_tick exists) open, move, bind A to a pad button, save;
   same-run control: the same synthetic presses with the panel closed reach the game as N64 buttons and arm nothing.
Limits not testable here: an external 1x display or a move between displays of different scale (no second display).
