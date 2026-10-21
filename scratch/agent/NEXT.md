# NEXT: why does the level-select modal (drawRadarIcon@0x800C5ED8 / tickCraftSelectScreen) return 2?
s5703: B40 forced 3/5 both revert to 2 via `sb s0,0(s2)` at 0x800C5ED8 (select-screen result). Legit writer.
Hypotheses: H1 unlock mask (initCraftSelectScreen r6=(1<<(lim+1))-1, lim from 0x12/save) clamps/limits to 2; H2 cursor default ignores r5 and Start auto-confirms; H3 injected key soak input moves/confirm cursor; H4 tickCraftSelectScreen reads stale pad state.
Discriminator: one run logging init args (r5 cursor mask, r6 unlock mask) and each tick's return + pad buttons (patch via fixup script, positive control = log fires on every tick), force3 arm. If r5 bit3 set and r6 allows 3 but return=2 -> H3/H4 (input); if r6 < 0b1000 -> H1 (fix save unlock source).
Then: make result N (force at store under env knob) and run lvN.
HYPOTHESIS-ID: g1-level-select
