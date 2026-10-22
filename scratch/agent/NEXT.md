# NEXT: G1 - s5863: vertical-offset arm (H22 confirm)
s5862: H23 refuted; troops hit by 9/2049 bolts. Test: within ONE run, autopilot/bolt altitude arm vs control (phase-gated on VI), e.g. ROGUESQ_TELE_BOLT-style force of bolt y to nearest class-1 troop y for a phase; measure troophit_bolts and c1 objective counter delta vs the unforced phase. Control: forced phase must raise troophit_bolts sharply.
Outcomes: kills rise -> H22 confirmed, G1 fix = aim/altitude; no rise -> receiver-side (damage not applied) re-opened.
Also: backtrace the Bus error (far=0x3c2d5b616 / 0x37fffd040).
HYPOTHESIS-ID: g1-mission-progression
