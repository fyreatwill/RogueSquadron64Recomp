# Next: consume s5061 PI DMA guard soaks, then pick next M3 idiom class or M5 item
HYPOTHESIS-ID: m3-pi-dma-guard
Read SOAK-RESULTS.md tail for s5061_pi_dma_guard_{default,force}. Expected: default pg=0 (no wild DMA on route), force pg=16 (control fired). Outcomes: default pg>0 => a real wild DMA exists: name the writer (ra in the log line, s4622 note) before touching anything (iron rule 11). force pg=0 => control not wired, null is worthless. Route nohangar flake (s5042-s5051) can fail the arm: rerun, do not conclude.
If class closes, next idiom class: osEPiReadIo/do_rom_pio unguarded bounds, or osAi/SP DMA host wrappers.
