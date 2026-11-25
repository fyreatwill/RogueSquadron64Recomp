# NEXT (s7938)
HYPOTHESIS-ID: owner-hotkeys-real-events
s7937 closed the F6 panel's interactive gap with REAL OS events (tools/s7937_panel_e2e.zsh, 8/8 x2, negative controls N1/N2,
pid-click arm = failing control). Same method, next untested owner-facing input: the window hotkeys.
0. `python3 tools/crash_reports.py --since 2026-11-25` first; fold new SOAK-RESULTS lines.
1. Unit: README documents **F11** / **Cmd+Ctrl+F** / Alt+Enter fullscreen toggle (main.cpp ~14263) and **F9** (audio device),
   F1-F4, F12. Every fullscreen proof so far (s6688, s6888, s7670) used ROGUESQ_FS_TEST_TOGGLE_S = SDL_PushEvent of a synthetic
   F11, which bypasses macOS. Hypotheses:
   H-ok: real F11 / Cmd+Ctrl+F / Alt+Enter each reach the handler and toggle once ([g1f] log + window bounds change).
   H-os-eats: macOS consumes the key first (F11 = Show Desktop / Mission Control by default; Cmd+Ctrl+F = Cocoa
     toggleFullScreen: menu item, which may toggle native fullscreen itself -> double toggle or a different (Space) fullscreen).
   H-double: SDL sees both the Cocoa menu action and the keydown -> toggles twice (net no change).
   Discriminator, one script (copy the s7937 raise/VOID logic: System Events frontmost, CLICK not needed): post each chord with
   real CGEvents (extend winctl `key` with a modifier-flags arg: cmd/ctrl/alt), record per chord the [g1f] toggle log count,
   winctl find bounds before/after (fullscreen = display size), and whether the frontmost app stayed the game.
   Positive control: ROGUESQ_FS_TEST_TOGGLE_S in the same run (synthetic toggle must show the same bounds change);
   negative control: a non-hotkey (F7) changes nothing.
   If H-os-eats/H-double: fix in main.cpp (e.g. handle the Cocoa fullscreen notification, or drop the chord the OS owns) and
   correct README/OWNER-OPT-INS so the owner is told a key that works.
