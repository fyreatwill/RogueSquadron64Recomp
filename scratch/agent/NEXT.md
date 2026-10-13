# Next work unit

HYPOTHESIS-ID: m3-idiom-class-audit

Closed M3 classes: MEM_B/BU/H/HU/W/WU, LD, lwl/lwr, unaligned stores/64-bit (s4716), jalr/jr indirect calls (s4717; all funnel through get_function, which aborts/stubs loudly).
Remaining candidates: (a) LL/SC grep (likely 0 live sites); (b) LWC1/SWC1/LDC1/SDC1 FPR load/store base-register class — check overlap with the MEM_W census (same base-register guards?) and whether FPR data loads hit unguarded bases.
Do (a)+(b) in ONE tool (tools/census_fpr_llsc.py modelled on tools/census_indirect_calls.py), reconcile with grep.
Discriminator: any live site whose base register is not covered by the existing MEM_* guard => land guard in fixup script; else close class. If no candidate classes remain afterwards, go BLOCKED asking the owner for a mission-entry discriminator.
