# Next work unit: is the objectives-complete trigger legitimate?
Hypotheses: H1 autopilot genuinely met level-0 objectives; H2 a counter/flag read by lv0_checkComplexObjectives is zeroed/stale so it fires early; H3 timer-based.
Disassembly exists: scratch/agent/objc_disasm.txt (regen: python3 tools/disasm_mips_elf.py <elf> 0x8010119C 0x801018EC). Direct reads: words 0x8010B690,B694,B698,B69C,B6A0,B6A4,B6A8 and floats 0x800A9554,9558,9574,9578; the rest is ~100 calls to helpers 800C759C/7540/76FC/7D1C (disassemble those first with the same tool; they likely read an objective-status table).
Discriminator: in a TRAPSWAP=2500 run dump those words (+ helper table) just before the setHudEnableBit4 hit (positive control: 0x3470 hit). Also record what renders after phase 6.
HYPOTHESIS-ID: m6-mission-end-trigger
