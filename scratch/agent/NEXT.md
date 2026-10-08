# Next work unit (s4298): name the writer of the odd ROM address in do_rom_read at guest 0x80001b08 (now reached deterministically after hangar->640 with A14 yield on)

HYPOTHESIS-ID: m5-audio-destub-sequence

Recipe: scratch/agent/s4297_a14on.sh (crashes ~21s after 512, 2/2 runs). Hypotheses: H-dma-args (caller passes odd PI address because a struct/offset field is stale/zero from a skipped init), H-audio-dma (MusyX sample DMA with odd offset - audio-related, fits M5), H-real (retail also does odd DMA, port's PI layer must support it). Discriminator: log a0..a3/ra and the caller chain at the assertion (or ROGUESQ-gated print before do_rom_read) plus retail oracle check of the same DMA. Also still open: what exits the A14 loop (b0 stays 0x03).
