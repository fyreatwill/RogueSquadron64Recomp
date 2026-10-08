# Next work unit: M5 Step 9q — retail post-task output-buffer contents vs port zeros

HYPOTHESIS-ID: m5-audio-destub-sequence

s4218: voice records equal retail (end-state). Divergence is downstream: ucode consumption.

Hypotheses:
- H-retail-nonzero: retail output buffers (output ring 0x80166450.., +0x7C/ptr in record) are nonzero after the audio task in title-1024 n>=256 while port is all-zero => port RSP/ucode execution loses audio on identical input (LLE bug); next diff one voice's DMEM.
- H-retail-zero: retail output is also zero/DC at this phase => title has no real PCM in retail either; "zero PCM" is not the defect, look at AI/sound path elsewhere.
Discriminator: extend oracle (`tools/oracle/rs64_oracle.c`, near dump_pc_task / blk-census) to census nonzero bytes of the output ring (record +0x44 ptr, 0x300 B each) at the audio task return PC for n>=256; positive control: nonzero-census of the data_ptr block (known nonzero). Compare to port s4207/s4208 zero counts.
