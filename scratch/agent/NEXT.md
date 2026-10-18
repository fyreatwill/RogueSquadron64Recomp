# Next work unit: advance past the results screen (post-results flow)
HYPOTHESIS-ID: m6-flown-render-fidelity

State (s5434): flight to ~swap 8000 then results screen (GAME OVER / 0:00), terminal under z-only autopilot for 19000 swaps; no crash, no stall.
Hypotheses: (A) start (or z+start alternation) on the results screen returns to hangar/title and a retry mission runs clean; (B) the transition crashes/hangs (teardown, audio/voice arrays); (C) still stuck whatever key is sent (needs a different button, e.g. a/b/enter).
Discriminator: copy scratch/agent/m6_keyed_hold_zonly.sh to a variant with `START_UNTIL=9999` (start alternates for the whole run; env var already supported) and run 900 s, FBD_EVERY=200; sheet from swap 8000 on. Outcome A: frames change after results + new VI origin pattern; B: CRASH line; C: results frame persists. Control: the results frame must appear at ~8000.
Recipe: `env START_UNTIL=9999 FBD_EVERY=200 zsh scratch/agent/m6_keyed_hold_zonly.sh s5435a 900`; sheet via `python3 scratch/agent/m6_sheet.py <dir>/fbd 3 scratch/agent/m6/view/x.png`; delete dumps afterward. If C, try other autopilot key names.
