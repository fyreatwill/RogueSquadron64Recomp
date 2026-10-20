# NEXT: G1 - find who spawns the lvN init (ra=0 entry) and what feeds it
Context: s5697 showed lv2 init and initMission enter with ra=0, gCurrentLevel=B40=2; no MIPS code references the 0x8010B050 table or jal's an lvN init.
Hypotheses: H1 a thread is created with entry = table[B40*16] by an osCreateThread-wrapper reading the ROM/RAM table through a computed pointer (not a constant); H2 the port/host dispatches overlays by symbol (e.g. overlay loader keyed on level); H3 ra=0 is just the instrument seeing a recomp wrapper that zeroes r31 (check with a known jal-called function as control).
Discriminator: (offline) grep funcs for osCreateThread-style callers whose a1 (entry) comes from lw with sll 4; (instrument) log ra/entry at the thread-create wrapper with a control jal-called function printing a nonzero ra in the same run. Then vary B40 via poke (ROGUESQ_MISSION_* / existing poke arm) to see lvN follow it.
HYPOTHESIS-ID: g1-level-select
