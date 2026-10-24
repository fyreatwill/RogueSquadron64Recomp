# NEXT: fold G1c frame-time arms (s6077_g1b_dd{1,2,3}_l1), then G4/G5
HYPOTHESIS-ID: g1c-frame-time
G3 closed as stale (s6077: pillar stubs = FIX_ZERO_SHADE, resolved s5971). Queued s6077_g1b_dd{1,2,3}_l1 (ROGUESQ_G1B per-VI timing, no fb dumps).
Unit: fold SOAK-RESULTS lines; extract [g1b] frame-time p50/p95 per arm (see s6013 fold for the parser). Hypotheses: H-flat (dd2/3 within ~1 ms p50 of dd1; RSP +10 ms/s is ~0.17 ms/frame), H-rsp (p95 grows with tri count -> dd3 visibly slower).
Outcome split: H-flat => G1c fully done, only owner look-judgement left. H-rsp => document per-step cost in docs/DRAW-DISTANCE.md, still opt-in.
Then: G4 any distinct stall hunting, else G5 renaming sweep (check session titles first).
