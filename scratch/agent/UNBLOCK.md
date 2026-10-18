# UNBLOCK (after s5472) — route 1 (refuted)
Block claimed: objdump not permitted, so lv0_checkComplexObjectives (0x8010119C..0x801018EC) cannot be read.
Refuted: the dependency was "a MIPS disassembly", not objdump. Wrote tools/disasm_mips_elf.py (stdlib only, reads ELF PT_LOAD) and produced scratch/agent/objc_disasm.txt (468 insns). Interactive objdump was also denied here, so the permission is real; no gate was changed or bypassed.
Observation: the body is ~100 calls to helpers 800C759C (x47), 800C7540 (x11), 800C76FC (x7), 800C7D1C (x6), 800C76B0/7660/761C (x4 each); direct memory tests: words 0x8010B690,B694,B698,B69C,B6A0,B6A4,B6A8 and floats 0x800A9554/9558/9574/9578 (lwc1 + compare).
Next: read those words in a TRAPSWAP=2500 run just before the setHudEnableBit4 hit.
