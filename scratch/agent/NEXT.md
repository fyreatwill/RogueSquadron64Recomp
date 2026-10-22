# NEXT (s5907): who consumes the fine-hit, and is RET attribution right?

HYPOTHESIS-ID: g1-mission-progression

s5906: fine test hits 91-100% for all classes (80323f58: 671 hits, RET=1). Not the gate.

Hypotheses:
- H-attr: RET attribution via rs5856_sinobj (last in-sphere obj) is wrong; RETs actually come from the object whose fine test hit.
- H-caller: findSegmentObjectSphereHit returns 1 but the caller (intersectSegmentWithObject loop, funcs_16.c around 0x8006AB58 return) discards it for non-80330c5c objs (team/owner/id compare).
- H-late: hit is accepted, but later damage/progress handler ignores non-NPC classes.

Discriminator (one build, one run of scratch/agent/s5902_life.sh): at fine-hit (tally kind 3) record obj ptr into rs5906_hitobj; at RET (rs5834_pre hit) tally class of rs5906_hitobj alongside sinobj; also log caller ra of findSegmentObjectSphereHit returns that are 1 vs RET count. Positive control: sum of hitobj-class RETs == total RETs.
Build pattern: apply_s5906_fine.py (apply via python3; build in build/ with DEVELOPER_DIR; run: zsh scratch/agent/s5902_life.sh, no `timeout` binary on macOS).
