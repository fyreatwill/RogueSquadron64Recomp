# Next work unit: post-mission-fail flow endurance (results -> title/hangar -> retry)
HYPOTHESIS-ID: m6-flown-render-fidelity

State (s5433): the autopilot mission fails at ~swap 8100 (results screen "MISSION FAILED"), a legitimate game flow. Mission flight endurance is clean to that point.
Hypotheses: (A) after the results screen the game returns to hangar/title and a second mission start is clean; (B) post-fail transition crashes/hangs (teardown/endMissionCleanup, audio/voice arrays); (C) the game sits on the results screen forever awaiting a key (autopilot z may or may not advance it).
Discriminator: one 900 s hold, FBD_EVERY=200 (sparse dumps), contact sheet from swap ~8000 onward + VI origin transitions after failure; CRASH/stall lines. Positive control: the existing sheet script must show the results frame at ~8100.
Recipe: `env FBD_EVERY=200 zsh scratch/agent/m6_keyed_hold_zonly.sh s5434a 900`; view with `python3 scratch/agent/m6_sheet.py <dir>/fbd 4 scratch/agent/m6/view/x.png` (no `-I`, PIL is in user site; viewable PNGs must live inside the repo). Delete dumps afterwards.
