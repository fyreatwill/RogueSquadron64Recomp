# NEXT (s7963)
HYPOTHESIS-ID: post-preset-class-ladder
s7962 closed class PS (apostrophe in exe folder broke crash symbol table; rs64_shell_quote.h; gate S7962_PS, e2e tools/s7962_ps_e2e.zsh).
Do not redo PS (s7962), SD (s7961), DR (s7960), RD (s7959), FW (s7958), CK (s7954 wall clock), LC (s7953 locale), TF (s7955), EV.
An src/ edit needs the FULL sweep (`python3 -u tools/s7651_gate_sweep.py --jobs 2`, ~28 min: run it in the background).
0. `python3 tools/crash_reports.py --since 2026-11-25`; fold new SOAK-RESULTS lines.
1. Ladder 3c, new host class AN (App Nap / background throttling / process suspension). No site in src/ or lib/ calls
   NSProcessInfo beginActivity / IOPMAssertion (grep s7962: 0 hits), so when the owner backgrounds or occludes the window
   macOS may nap the process (timer coalescing), and a laptop sleep or SIGSTOP freezes it. Hypotheses: H-nap (an occluded/
   background window throttles VI/audio, then the game catches up in a burst = G5c "buffering" signature) vs H-moot (SDL
   audio + Metal present keep the app un-napped; steady_clock pacing resumes cleanly after a stop). Discriminators, one build,
   one run each, owner save never written: (a) `lsappinfo info -only ApplicationType,AppNap... <pid>` / `pmset -g assertions`
   while the game window is in front vs hidden (Cmd+H via osascript) for 60 s each, with the present ring (G1e dump) scoring
   VI cadence per phase; (b) `kill -STOP` 5 s then `kill -CONT` mid-flight: count VIs/presents in the 1 s after resume
   (catch-up burst > 2x nominal = H-nap-like pacing defect). Positive control: the same ring during a foreground phase must
   show 60 VI/s. Needs an unlocked screen (check CGSSessionScreenIsLocked) — if locked, queue as SOAK_NEEDS_IDLE soak.
   If H-nap: add an NSProcessInfo activity (latency-critical, user-initiated) while a game is running, gate it.
