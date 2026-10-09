# Next work unit (s4463): who bounds the 0x18-stride record run that walks into the audio pool?

HYPOTHESIS-ID: m5-ai-event-cadence

State (s4462): insert calls form a descending 0x18-stride a1 run crossing the pool (0x80193B00..0x80194C00) at VI 1024; overlap F supported in the port (6/6 arms, single-source).
Hypotheses: (P) run count/base comes from a wrongly-read SND header word (port-induced); (Q) retail run also overlaps and the pool is allocated afterwards on consumed records (benign); (R) run legitimately larger and the pool allocator mis-places its block.
Discriminator: log ra + a0/a2 at insert entry for first/last call of each run and the caller loop bound; then oracle (tools/oracle/README.md, physical read watch with whole-RDRAM control) on retail: max a1 of the run vs pool base. P: bound word differs from retail; Q: retail max a1 also above pool base; R: retail run ends below pool and port pool base differs.
