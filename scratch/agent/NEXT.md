# Next work unit

HYPOTHESIS-ID: mission-phase-correctness

OPEN DEPENDENCY (human, NOT to be retried): RSPRecomp not in headless allowlist (UNBLOCK.md). The full 0x2C splice
(sprites) resumes only when a human adds the allow rules and removes this paragraph.

s4751 DONE: fixup 24 (ovl2c drop route, default on) removed the runaway (154 -> 0 tasks); mission reaches pause menu with text.
Work unit: with the runaway gone, run the s4751_run.sh recipe (arm `on`) with phase-gated captures and compare mission
frames (HUD/ship absence, terrain ribbons) against the retail oracle s4724 recipe; decide whether ship/HUD absence is
only the dropped 0x2C sprites (count nbd per frame = expected missing texrects) or another defect (e.g. terrain ribbons).
Do not add runaway counters; that question is closed.
