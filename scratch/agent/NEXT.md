# Next work unit: per-origin bad-row budget in the s4988 s4540 boundary instrument

HYPOTHESIS-ID: m5-s4540-per-origin-budget

Context: s5007 BLOCKED asked the owner to pick (a)/(b)/(c). Option (b) was already run as s4987 (narrow lock; title reached; bad=8; refuted) and the s4990/s4991 next step was never run.
Do: in tools/apply_s4988_s4540_boundary.py replace the global 4-row cap on bad s4540 rows with a per-origin budget so mission-origin rows are captured. Keep route controls (title, hangar, both mission origins, ctl_arm=1, s4579A>=9, PCM>0, crash=0, abort=0). Discriminator: do bad rows at a mission origin carry current 20/0x8018C720 (H-propagation) or stale 32/0x801714D0 with a stale caller (H-uninstrumented-reader / H-classifier-phase)? No guard, rewrite, or mitigation.
