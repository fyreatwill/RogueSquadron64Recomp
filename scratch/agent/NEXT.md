# Next work unit

HYPOTHESIS-ID: oracle-poke-mission-entry

s4726: retail stores at 0x1F0D70..80 are zeros (0x800078EC) and byte-packed data (0x800C7F08..801C loop); never 0x489/1161. Samples unphased (post-target-* seen=0), single-source.
Unit: in the PORT, arm a write watch on 0x1F0D74 with PC attribution (find existing port write-watch env vars under tools/ or the runtime) and record writer and stored value when width 1161 appears. Compare writer with retail PCs (0x800078EC clear, 0x800C7F08 loop, 0x800CAC44..74).
Outcomes: writer is a retail-equivalent function storing 1161 => upstream port-state divergence (trace its input); writer is non-game code (host/DMA/ucode) => wild write, name it.
Positive control: a watch on a known-written address in the same run fires.
