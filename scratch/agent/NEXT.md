# NEXT: G1 — who sets slot +0x14 bit 3 (destroy request) for class-1 NPCs in lv0?
s5816: +0x1A is a reentrancy depth, no timeout exists; destroy = depth 0 && (+0x14 & 8). Flag set post-update 3083x/405 s.
Hypotheses: (a) the NPC's own update fn sets bit 3 (self-despawn by design, e.g. distance/off-screen/age in its own state); (b) an external setter (damage/kill handler or level script) sets it; (c) a port divergence makes a setter fire early (e.g. bad range/visibility compare).
Discriminator (one build, one run): trace every store that sets bit 3 of a slot's +0x14 (grep generated code for `MEM_H(0X14` stores / sh to 0x14 off slot regs; add RS64_S5798_ST-like hook logging pc, slot, class(+0x70 via NPC) and a backtrace for the first 8 distinct pcs). Positive control: total sets ~3000/405 s match [slotpost] flag8 count.
Outcomes: one dominant pc inside NPC update (a) -> read its condition vs retail; setter from kill/handler path (b) -> follow to what drives it; condition inputs look wrong (c) -> fix input.
Command: scratch/agent/g1_inv1.sh <tag> 400 with instrument in a tools/apply_s58xx_*.py fixup script.
HYPOTHESIS-ID: g1-mission-progression
