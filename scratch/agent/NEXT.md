# Next work unit: ^3 byte-order audit of remaining audio rdram readers (s4242)

HYPOTHESIS-ID: m5-audio-destub-sequence

s4241: retail also has the constant rms-33 prefill; port entry transient benign. Closed.
Hypotheses: (a) other TO_PTR readers in audio host code (lib/ ai.cpp siblings, audio logger/probes) read s16 in host word-swapped order -> more bogus stats; (b) only ai.cpp was affected.
Discriminator: grep -n TO_PTR over audio host code; classify each s16/u8 access for ^3/^1 correctness; positive control: a known-sample buffer read through each reader.
Then: phase-align port vs retail title RMS (4.7k vs 1.4k) at the same ucode-DMA ordinal.
