Single next work unit (s5606): rebuild, run ROGUESQ_MISSION_WIN=<n> once (positive control: the mission-win log line shows count3 -> 9), and compare the post-mission screen against the known MISSION FAILED fall-back, phase-gated on VI transitions. Offline in parallel: read 800C7738 vs 800C776C (disasm_mips_elf.py) to see which is the win path.
HYPOTHESIS-ID: m6-mission-endurance
