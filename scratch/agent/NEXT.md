Single next work unit (s5614): explain why WIN_REAL gives gate 5,4,6 / B14=2 in s5613 but gate 3 / B14=1 in s5612.
Hypotheses: H1 get(2)/get(3) also cross thresholds after the poke (lose arm wins the race); H2 gate 5 (vflags 0x101) preempts, a state-dependent path before the poke settles; H3 s5612 was a one-off timing outcome.
Discriminator: in ONE run log get(1..10) (0x80138060+) every 30 polls after the poke plus gate/B14 changes; second arm with the poke at polls=100 vs 300 in the same recipe; compare which counter hits threshold first. Fix the misleading count3 format string. Locate and log a level-id word.
HYPOTHESIS-ID: m6-mission-endurance
