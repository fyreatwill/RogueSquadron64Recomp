# NEXT (s7286): G1c phase 2 step: dd8 on today's owner path (auto stack R=88 + merge + E16), find the binding limit
HYPOTHESIS-ID: g1c-dd8-owner-path
State: G5c fully closed (s7284 load edges, s7285 transition gaps guest-side/retail). Every G5 item awaits the owner. Ladder G1c
phase 2 ("push draw distance as far as it will go") was last measured at dd8 in s6466-s6470, before FWDWIN/WIDEWIN/auto stack/
spill arena. dd6 at R=88 holds 60/s at 12.3 ms (s7267). Fold first: s7285_bootloop_qos verdict (SOAK-RESULTS tail).
Unit: one queued or in-session run, L4 + L12, owner env (FPS60, 16:9 FULLSCREEN, WIDEWIN=1 auto stack), arms dd6 (reference) / dd8,
300 s hold each, G1b per-frame timing (tools/g1e_owner_quiet_arms.zsh style win77-97 ms, beyond-route s), heap/alloc-failure lines,
[s7258] stack print, crash lines. Plus a terrain-fraction still (same camera) per arm.
Hypotheses (binding limit at dd8):
  - L-heap: alloc failures / spill arena exhaustion lines at dd8 only.
  - L-cost: frame time > 16.7 ms at win77-97 (VI drops below 60/s) with no alloc failures.
  - L-cap: ucode iteration cap / DL buffer: missing far cells or [cap] lines while cost and heap are fine.
  - L-none: dd8 clean -> next step is the 4.0..8 clamp / dd>8.
Positive control: dd6 arm must reproduce s7267's ~12 ms / 60/s; a SIGSTOP 1 s mid-hold must show in the frame-time ring.
Note the single-source rare dd4/dd8 gfx SIGBUS (s6466 att1): any SIGBUS here is a side-effect crash to root-cause (G4 rule).
