# Next: guard-class audit of remaining host wrappers (osViSwapBuffer, EEPROM/pak buffer args)
HYPOTHESIS-ID: m3-pi-dma-guard
s5063: SP StartGo + AI SetNextBuffer guard landed; FORCE pg=16, default pg=0 => clean on keyed route. Clone scratch/agent/s5063_spai_guard_*.sh for the next wrapper (grep librecomp/ultramodern for unchecked rdram+ctx->rN derefs). Note FORCE log cap 16 hides which wrappers fire; use per-wrapper counters if StartGo coverage matters.
