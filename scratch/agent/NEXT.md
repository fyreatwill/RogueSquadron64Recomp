# NEXT (s7227): fullscreen toggle + display removal when the game targets a NON-main display
HYPOTHESIS-ID: aspect-auto-display-choice
Context: s7226 added rs64_g1f_target_display (ROGUESQ_WIN_DISPLAY=<n>|mouse). Boot on the secondary fills (FB 796 on 16:9). Untested:
F11 toggles on the secondary (does leaving fullscreen keep the window there and re-entering fill that display?), and REMOVING the
secondary while fullscreen on it (s7202 path re-enters on the remaining display; the game width stays the boot width -> bars, by
s7225 design).
Hypotheses: H-ok (toggle x2 = one swap chain step each, back to 1920x1080 fill on the secondary; removal -> built-in, bars at
lit 1.778, 30/s within 2 s); H-jump (leaving fullscreen puts the window back on display 0 / centred on main: macOS restores the
pre-fullscreen frame, which SDL created on the target, so expect not); H-dead (removal of the target display leaves a hidden Space,
the s7202 gate s7222 checks "own display" by bounds and may mis-match).
Run: scratch/s7226/flight.zsh-style arm with ROGUESQ_WIN_DISPLAY=1 ROGUESQ_FS_TEST_TOGGLE_S=100,130 and virtual_display hold
shortened so it is destroyed at ~170 s; shots -D 2 then -D 1 after removal; present ring (ROGUESQ_PRESENT_RING) for gaps.
Score: tools/s7226_display_fill_score.py per display + [g1f-win]/[retina] swapchain rows.
