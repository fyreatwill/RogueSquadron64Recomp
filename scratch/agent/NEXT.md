# NEXT: G1 — explain the 3->2 life loss at overlay reload, then drive to mission end with real input

s5784: ALT_HOLD validated (target y=-6.5, 421 s, no ret1 deaths). One life loss (livesbyte ord=7 3->2, origin 0x690400) coincided with menuOverlayInit/overlay start-match in scratch/agent/m6/s5777_althold/run.log ~line 769266.
- H-reload: the life is decremented by a mission restart/reload path (writer = the mission-fail arm at 0x64?) -> find writer PC of lives byte via existing [livesbyte] instrumentation / CURRENT-TRUTH 'objective booleans' thread.
- H-death: a real in-flight death not from terrain (enemy fire; GODV=0) -> look for damage/health logging before ord=7.
Discriminator: print the 200 log lines before run.log:769266 filtered for health/fail/objective; control = ord=3/4 livesbyte init lines (0->3) already firing.
Then: extend flight to attempt objective completion with real stick/fire input; log win/advance.
Open: idle-autopilot LOSE ~+342 s (s5627).
HYPOTHESIS-ID: g1-mission-progression
