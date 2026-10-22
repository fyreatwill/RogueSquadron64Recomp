# NEXT: G1 - player bolts never land within a sphere (s5835: 0/29694 segment-clamped, centres live). Aim/bolt-travel (a) is what remains.
Step: fix tools/apply_s5835_sphere_probe.py summary format (P columns shifted); add P min sd2 and min sd2/r2, plus per-bolt travel (position at spawn vs now, frames alive) for P vs N in rs5833/5834 hooks. Then run with F1/F2 so autopilot fires while NPC is close (or ROGUESQ god/teleport of player near an NPC if available) and compare. Control: N SEGIN rows.
Run: env ROGUESQ_LOG_HITS=1 zsh scratch/agent/g1_fire.sh s5836 320
Outcomes: min P sd2 >> r2 everywhere -> bolts fly elsewhere (aim); min P sd2 ~ r2 but lands just outside -> step/length/radius scaling bug.
HYPOTHESIS-ID: g1-mission-progression
