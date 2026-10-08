# Next work unit: M5 - classify fillSampleStreamRange+8136 crash (null guest ptr)

HYPOTHESIS-ID: m5-audio-destub-sequence

s4229: probe-induced crashes (sched+9632, stage_adv) fixed; remaining early crash fillSampleStreamRange+8136 (fault 0x380000000 = rdram+0x80000000, i.e. guest pointer 0 dereferenced), last-guest-pc 0x8000b650 / 0x8000834c, ~1/4 stale runs.
Hypotheses: (a) guest passes uninitialised/zero sample-stream descriptor because audio bring-up state differs (race with audio thread start); (b) our stub of a MusyX DMA/alloc returns 0; (c) another unsigned-literal probe (grep class is closed, so unlikely).
Discriminator: python3 -I tools/agent/disasm_at.py fillSampleStreamRange 8136 (prints lldb window); name the register holding 0 and its source in the generated .c; then run scratch/agent/s4229b_tally.sh style runs logging that field.
