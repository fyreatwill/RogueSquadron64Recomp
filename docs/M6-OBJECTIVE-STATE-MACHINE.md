# lv0_checkComplexObjectives hint-latch chain (0x801016B8..0x80101830)
Source: scratch/agent/objc_disasm.txt (tools/disasm_mips_elf.py), session 5476. Single-source (static read, no run).

Words 0x8010B690/94/98/9C are ONE-SHOT LATCHES in a sequential chain, each guarded by busy word 0x8010B6A8 (==0 required):
- w0 (B690): set when 0; calls 800C76FC(7, 5.0f).
- w1 (B694): set when w0==1 and w1==0; plays message id 0x224.
- w2 (B698): set when w1==1 and w2==0; calls 800C7660 twice.
- w3 (B69C): reached only when w1!=1 or w2!=0; fires when flags 31, 5 and 26 (helper 800C759C) are ALL zero and w3==0; plays message 0x225.
- 0x8010B6A0: separate latch gated on flag 22 == 1; message 0x1F0.
B6A8 is cleared by a float timer compare (0x800A9580), i.e. these are spoken-hint/HUD-message latches.

Consequence: word[3] staying 0 is NOT evidence the mission-end step is missing. It is a hint latch that depends on flags 31/5/26 being clear
(if any is set it never fires). The mission-end condition remains counter[2]>=3 or counter[3]>=9 on 0x80138060 (s5474).
