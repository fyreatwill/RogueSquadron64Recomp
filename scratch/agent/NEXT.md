# NEXT: who sets the per-slot craft state bit 0x8/0x10 (kill source) on the route that dies every ~7.5 s?
s5759: death chain read (docs/M6-S5759-DEATH-CHAIN.md): state bit 0x10 -> 0x800B1024 settle tick -> bit1 -> mtm(1) -> lives--. Slot state halfword = lhu -0xD0 off (craft+0xB8)*0x2A0 + 0x8014(-0x7FF4 base): compute exact address from funcs_30.c ~0x800B1E60 (a1 base).
Hypotheses: H1 the state bit is set by collision/damage code with hp->0 (hp writer is only updatePlayerCraftPhysics swc1); H2 set by a timer/objective script (non-health fail); H3 set by an uninitialised/stale value from a stubbed subsystem (audio/DMA).
Discriminator: lldb (or a built [slotst] probe) write-watch on that halfword on the route where deaths occur (GODMODE3=2 + AUTOPILOT_HOLD_MS=1800, see CURRENT-TRUTH s5742/s5738), with a positive control (watch must fire at mission init). PC of the setter splits H1/H2/H3.
HYPOTHESIS-ID: g1-nonhealth-fail
