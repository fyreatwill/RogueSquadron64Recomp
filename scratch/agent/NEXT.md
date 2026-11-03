# NEXT: FPS60 tick timers - exercise the last kept sites (button-held +0x15C, lvl16/17)
HYPOTHESIS-ID: g3-fps60-tick-timers

State (s6823): tools/fixup_fps60_ticks.py steps 10 sites; UNFIX = 800DAB64, 800E32CC, 800E1E28 (s6822 runtime) +
800C96B8, 800806AC (s6823 static: behind dt interval timers). Kept but never exercised: 8007CD50, 800B5350, 800BC778,
800FB4F8; 800F8708 ran only in an FPS60 arm (8x at lvl11 t=110 s). scratch/s6823/census.sh (presses 6..121 s, 300 s)
reaches flight on lvl6/11.
Hypotheses per site: H-tick (keep step) / H-event (drop) / H-dead.
Step 1: find which button the player-config +0x1E mask is (table 0x8010BE18 stride 0x24, field +0x1E vs fire +0x1A,
secondary +0x1D) from the controller-config init; add it to the AP hold (g3_port_capture.sh AP syntax) so 800B5350
runs on an X-wing level (lvl2). Step 2: census.sh with EEPS=lvl16/lvl17 eeps (scratch/s6769, s6770). Step 3: for each
site that runs, a30 vs b60fix ex/gs on the same level (tools/g3_tick_countdown_span.py); equal ex/gs => event-gated
=> UNFIX. Positive control: 8006C024 (frame-locked, ex/gs ~2x at FPS60 off-step).
If after this the remaining sites still never run, close the class: 10 sites kept, document the unexercised ones as
static-only, and move to the next G-ladder rung (G3e/G2b/G3f per CURRENT-TRUTH).
