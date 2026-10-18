# Next work unit: B vs C — is the MISSION GOALS screen a mission-end flow or ship death?
HYPOTHESIS-ID: m6-flown-render-fidelity

State (s5432): z-only autopilot still reaches the goals screen (~swap 8000 vs ~4800 with start) => not the `start` pause (A refuted as sole cause).
Hypotheses: (B) objective/mission-end flow independent of keys; (C) ship death (z-only, no steering, flying into enemies/ground).
Discriminator: in one run, log the player-ship health/alive word and the game mode/screen-state word at each 20 swaps through goals onset (find via CURRENT-TRUTH mission-state notes or grep PORTING-STATE for "health"/"gamemode"), plus FB dumps. Health hitting 0 before onset => C; health nonzero and mission-complete/objective flag set => B. Positive control: the same logging must show the health word change during the title->flight transition.
Recipe: `env FBD_EVERY=20 zsh scratch/agent/m6_keyed_hold_zonly.sh <tag> 300` plus the new logging. Delete fbd dumps afterwards.
