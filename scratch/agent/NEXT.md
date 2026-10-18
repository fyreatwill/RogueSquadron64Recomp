# Next work unit: M6 endurance across mission restarts (x3)
HYPOTHESIS-ID: m6-flown-render-fidelity

State (s5435): post-results flow works (a/start restarts the mission; hangar and second flight reached; 0 crash). Hypotheses: (A) repeated mission cycles stay clean; (B) a distinct crash/stall appears on a later restart (teardown/voice arrays); (C) renders degrade on the second flight.
Discriminator: enqueue 3 recipes copying m6_keyed_hold_post.sh with HOLD=1200 (`env LATE=520 FBD_EVERY=400 zsh scratch/agent/m6_keyed_hold_post.sh <tag> 1200`). B = CRASH line or vi_stalls>0; C = compare second-flight frames to first. Control: results frame at ~swap 8000.
