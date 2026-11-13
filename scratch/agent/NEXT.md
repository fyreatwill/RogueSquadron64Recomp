# NEXT (s7275): G5c close criterion: one LONG run at the owner's PLAIN recipe (no WIDEWIN/MELT env), fullscreen 16:9 dd4 FPS60
HYPOTHESIS-ID: g5c-long-plain
State: s7272-s7274 show 0 in-flight holds >= 250 ms in 300 s captures (L1/L4/L5/L12, 16:9 + 21:9, windowed + fullscreen, SIGSTOP control
caught every time), but every one of those runs set DD_MELT + WIDEWIN env, and none was longer than 300 s. G5c says "Fixed when a long run
has no gap over 250 ms outside loads, including the catch-up burst". The owner's recipe is FPS60 dd4 ASPECT=16:9 FULLSCREEN=1 only.
Hypotheses: H-none-long (0 flight holds over 900 s on L4 and L12 -> G5c engineering CLOSED, owner flight only); H-late (holds appear only
late in a long run: heap/pool growth, shader cache growth, log or file writes; note the time and look at the sheet frames); H-plain (holds
appear without WIDEWIN/MELT: the plain dd4 terrain path stalls, e.g. the far-loss fill; compare against s7274's runs on the same level).
Discriminator: tools/s7272_g5c_hold_arm.zsh PLAIN=1 DUR=900 KEEP=1 FS=1 (SIGSTOP 1 s controls x3 at +57/+158/+259 s; holds sheet).
Commands (in-session: ~1045 s per run, over the loop's 600 s soak cap): check HID idle >= 120 s and the screen is unlocked, then
  `env PLAIN=1 DUR=900 KEEP=1 FS=1 LEVEL=4 TAG=s7275p4 ASP=16:9 CW=480 zsh tools/s7272_g5c_hold_arm.zsh` then the same with LEVEL=12 TAG=s7275p12.
  Watch whether the autopilot leaves flight inside 900 s (L4/L1 restarted their mission at ~+50-60 s / +205 s in s7274). Holds inside those
  transitions are loads. View scratch/s7272/<tag>/holds_sheet.jpg. Phase labels mean nothing under PLAIN.
Expected: H-none-long -> mark G5c engineering closed in CURRENT-TRUTH item 5 and take the next ladder rung; any flight hold -> its time,
frames and phase name the next unit (sample the live process with `sample` at the next recurrence).
