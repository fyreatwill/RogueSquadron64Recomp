# Next work unit: M5 Step 9r — find the first zero-producing ucode command for one voice in the port

HYPOTHESIS-ID: m5-audio-destub-sequence

s4219: retail output buffers ~98% nonzero at title-1024 n>=256; port all-zero; records equal (s4218). Divergence = port RSP/ucode execution.

Hypotheses:
- H-cmd-decode: one command (ADPCM decode / resample / mix) in the port's ucode emulation yields zeros from nonzero input (LLE bug in a vector op).
- H-param-zero: a command parameter read from the command struct (volume/pitch/loop addr) is zero in port DMEM due to a DMA/byte-order issue.
- H-late-dma: output DMA out happens before mix completes (ordering).
Discriminator: in one port run (gate ROGUESQ_LOG_S4213), after each ucode command in one phase-5 task dump DMEM nonzero-byte counts of the input, working and output regions (positive control: input region nonzero); the first command where nonzero->zero selects among hypotheses. Read docs/F5-UCODE-REFERENCE.md first.
