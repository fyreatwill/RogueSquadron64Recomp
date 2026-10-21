# NEXT: G1 — does npcProbeDriod (0x800CABD4, funcs_36.c) legitimately target class-2 ground objects? (H1 vs H2')
Evidence (s5794): the 11/12 shooters hitting the class-2 victims are live probe droids; 1 wingman. Slot-staleness refuted.
Hypotheses: H1 retail-by-design (droids attack these objects; player should intervene/kill droids); H2' our target selection picks the wrong target (e.g. a faction/team word wrong, or class-2 objects should be non-hostile); H5 the droids are supposed to be dead/not spawned yet (spawn-time or count anomaly).
Discriminator: read npcProbeDriod's target-selection code path (offline, via generated funcs_36.c / objdump) and name the field compared (faction/team word) between droid and victim; then one run logging that field for droid vs victim at the first hit (extend apply_s5794_shooter.py). Outcome: droid faction != victim faction by a legitimate enemy/ally pair -> H1; field equal/garbage -> H2'. Also compare droid count vs the mission's spawn table (H5).
Reuse: tools/apply_s5794_shooter.py, scratch/agent/s5793_npcd.sh (bump TAG).
HYPOTHESIS-ID: g1-mission-progression
