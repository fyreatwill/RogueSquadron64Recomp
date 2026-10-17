# Next: guard-class audit of do_rom_pio + SP DMA host wrappers
HYPOTHESIS-ID: m3-pi-dma-guard
s5061 CLOSED: default pg=0, force pg=16 (H2 selected, two-source). Build a default-vs-FORCE pair for the next class; expected default 0 fires, force >0. A nonzero default means name the writer (ra) before any mitigation.
