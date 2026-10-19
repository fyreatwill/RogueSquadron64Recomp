# Next work unit: find what advances 0x8010B690 word[3] (and 0x138060 beyond 1)
s5475a (562 s hold): 0x10B690[0..2] became 1 gradually; word[3] stayed 0; setHudEnableBit4 never hit. Either the autopilot never triggers the 4th objective (needs player action) or it needs more time. Use the stdlib MIPS disassembler on the writer of 0x8010B69C, identify the condition, then decide an autopilot change or a longer hold (TRAPSWAP=2500, hold 900).
HYPOTHESIS-ID: m6-mission-end-trigger
