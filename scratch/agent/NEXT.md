# NEXT: isolate the width-bearing root-DL tail words
HYPOTHESIS-ID: g1d-widescreen

Session 6195 selected the first differing candidate in the complete DMA-read
census: `mem=0x170`, `len=0x10F`, root-relative offset zero, same guest PC
`0x80007904`, control hash `0x8D4703B3` versus wide `0x12499740`. The earlier
root witness only covered the first 0x100 bytes, which matched and was zero.
The remaining question is whether the differing 0x100..0x10E tail is merely
relocation metadata or contains the width-bearing command words.

Resume next work unit: dump and normalize the 15 tail bytes (0x100..0x10E) of
the first root-relative 0x10F DMA, alongside the existing root relocation
sequence, in both arms. Attribute each nonzero word to pointer relocation,
command opcode, or ordinary data; do not change rendering. Keep all existing
controls and `ROGUESQ_LOG_G1D_READS` enabled. Build once, then run:

    zsh scratch/agent/s6179_g1d_rdp_words.sh

The witness must retain positive controls in each arm: at least 160 joins, 400
copies, and both known root sequences. The discriminator is the first tail word
that remains different after applying the already-known relocation delta.

Competing hypotheses:

- H-relocation: every differing tail word is a relocated pointer and the
  referenced command bytes match after relocation normalization.
- H-command: at least one tail word is a command/operand whose normalized value
  differs; it is the width-bearing producer input.
- H-other: the tail is only a pointer table; follow the first referenced target
  and witness that target in the same run.

Do not add a rendering mitigation.
