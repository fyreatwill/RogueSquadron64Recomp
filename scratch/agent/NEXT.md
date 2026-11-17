# NEXT (s7519)
HYPOTHESIS-ID: libultra-host-surface-census

First: fold s7518_fo_levels from SOAK-RESULTS if it ran (score 0 -> FO CLOSED 6 levels in CURRENT-TRUTH item 20; 1 -> read
scratch/s7518_fo_levels/out.txt stale_load / unflushed rows (pc, addr); 3 -> no arm's planted invalidate hit a CPU-re-read buffer:
pick another ROGUESQ_CACHE_SHAPE_CTL k (s7518 L4 k=600 hit the 0x80766C40 inflate scratch); 4 -> no rows).

Work unit: class FP = the store side of FO (the gap s7518 left). On hardware the D-cache is write-back + write-allocate: a guest
STORE into a line that is later PI-DMA'd without an osWritebackDCache/osInvalDCache in between can be evicted AFTER the DMA and
overwrite the DMA'd bytes (port: DMA always wins). Hypotheses: H-canon (every DMA'd line the CPU stored to was written back or
invalidated before the DMA: the game's wb -> DMA -> inv slot idiom), H-dead (dirty-at-DMA lines exist but are invalidated after the DMA
before any eviction could matter, i.e. the after-DMA inv discards them), H-live (a dirty line survives a DMA with no later inv - the MusyX
stream ring 0x17C000-0x1AA000 is the only DMA family with no cache ops at all; a CPU store there would be live).
Instrument: extend the s7518 watch to stores (the s7475 store-watch macros already route marked-byte stores to rs64_s7475_store;
add a s7518 branch like rs64_s7484_load's): store on a marked line -> state D (dirty); wb -> clean; inv -> N (discard: count dirty
discards too = hardware loses that store); DMA over D -> DIRTY_OVER_DMA row unless an inv follows before the next load. Ctl: drop one
osWritebackDCache before a slot DMA the CPU had written (ROGUESQ_CACHE_SHAPE_CTL extended with a wb mode). Runs: L4 dd1 + L15 dd8 21:9
via tools/g1e_owner_quiet_arms.zsh (s7518 command in PORTING-STATE), scorer tools/s7518_cache_shape.py extended, levels soak after.
When FP closes, the libultra replaced-function surface is exhausted (census in PORTING-STATE s7518): take CURRENT-TRUTH item 21.
OWNER SAVE RULE: never clear ROGUESQ_NO_SAVE_WRITE; never touch build/saves.
