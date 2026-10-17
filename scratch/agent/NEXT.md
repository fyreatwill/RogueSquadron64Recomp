# Next: guard-class audit of SP/AI DMA host wrappers (osSpTaskLoad etc. in librecomp sp.cpp/ai)
HYPOTHESIS-ID: m3-pi-dma-guard
s5062: PIO guard landed; FORCE control fired 0 => do_rom_pio unreachable on keyed route (unexercised). Pick a wrapper reachable every frame (osSpTaskLoad) so the FORCE control must fire; build default+force pair, clone scratch/agent/s5062_pio_guard_*.sh. Nonzero default => name writer (ra) before any mitigation.
