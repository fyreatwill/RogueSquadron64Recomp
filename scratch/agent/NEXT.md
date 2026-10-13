# Next work unit

HYPOTHESIS-ID: m3-idiom-class-audit

H-alloc-window-sched-switch CLOSED (s4715): 6 re-allocs same tid, block reused with valid header, 0 crashes; re-allocs are retail behaviour.
Next unit: M3 idiom-class census of the next unexamined class after tools/census_ld.py and tools/census_lwl.py (candidates: SDL/SDR, LWR-pair stores SWL/SWR, LL/SC, LDC1/SDC1). Model: s282-s288 `-0x25A4`: grep-enumerate every site in build/RecompiledFuncs, classify each (guarded / provably dead / unguarded), land a guard in the fixup scripts for unguarded ones, close the class. Commit the census tool.
Discriminator: unguarded-site count >0 with a reachable base register => land guard; 0 => class closed with proof.
