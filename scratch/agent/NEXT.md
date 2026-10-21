# NEXT: fold s5765_slotwatch_3C (watches corrected to 0x137F3C slot0 / 0x1381DC slot1; natural deaths)
Read SOAK-RESULTS.md s5765 line + scratch/agent/m6/s5765_slotwatch_3C/lldb_att1.log.
Control (same run): wp4 (0x130B10) lives byte 3->2->1->0 hits. If absent -> void (route had no deaths).
Discriminator: bt of wp2/wp3 writes (value low halfword with 0x8/0x10) preceding each lives-- hit.
- Writer = death handler/damage path => slot state is death-driven (H1); name writer fn, check legitimacy.
- Only init writes (constant 0x10000, computeCraftSelectTurnFromInput) => flags set elsewhere (H2: different address/width; H3: bit set by objective path).
HYPOTHESIS-ID: g1-nonhealth-fail
