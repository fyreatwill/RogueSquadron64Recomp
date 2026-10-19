# Next work unit: what increments counters 0x80138060[0..3] (end fires on [2]>=3 or [3]>=9)
s5476: 0x10B69C is a hint latch (docs/M6-OBJECTIVE-STATE-MACHINE.md), not the end gate. Disassemble the writers of 0x80138060..6C (grep objc_disasm for B060 / helper 800C7540/7660), then run a 900 s hold (TRAPSWAP=2500) sampling the 4 counters; decide autopilot change.
HYPOTHESIS-ID: m6-mission-end-trigger
