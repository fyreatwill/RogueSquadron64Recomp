# Next work unit: is the persistent MISSION GOALS screen caused by the autopilot's `start` key (pause)?
HYPOTHESIS-ID: m6-flown-render-fidelity

State (s5431): 568 s hold: flight swaps ~2800-4400, then MISSION GOALS screen to the end (swap 16400), emblem animating (fbhash 15333 distinct/16508). Preceded by flight => not a restart.
Hypotheses: (A) overlay = pause menu from autopilot `start` (toggles every 4 s alternating with z); (B) mission-end/briefing flow independent of keys; (C) ship death.
Discriminator: copy m6_keyed_hold.sh to a variant whose AP uses only `z` (no `start` after the title->hangar->mission keys are done; keep early start presses needed for the route), run `env FBD_EVERY=20 zsh <variant> s5432a 300`, contact sheet with `python3 scratch/agent/m6_sheet.py <fbd> 20 <png>`. If flight persists far longer than 4400 swaps => A; if overlay still appears at ~4400 => B/C. Positive control: s5431a sheet (overlay at ~4800). Delete fbd dumps afterwards.
