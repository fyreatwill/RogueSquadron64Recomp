# Next: does the mission world REACT to input (ship response), beyond pad-layer delivery
HYPOTHESIS-ID: m6-mission-input
s5068 showed pad bytes reach osContGetReadData in mission with correct values, crash=0.
Hypotheses: H1 ship/camera state changes under held stick/fire (playable); H2 pad is read but mission ignores it (e.g. input gated by a stubbed state flag); H3 reaction exists but only after longer hold / needs a different state (e.g. intro cinematic not yet over).
Discriminator: same s5068 route; in ctl A vs key window, capture frames (existing ROGUESQ_LOG_VI_FB_CONTENT or a screenshot hash per window) and/or hash player-ship RDRAM region; compare key-window frame-hash variance vs ctl windows within the SAME run, with a W-hold vs D-hold vs fire distinction. Positive control: any frame change at all between ctl windows (animating scene -> use phase gating, not stopwatch).
Script base: scratch/agent/s5068_mission_input.sh (route is ~260 s on this host; keep under 600 s).
