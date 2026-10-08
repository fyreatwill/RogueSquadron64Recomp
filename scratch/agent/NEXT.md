# Next work unit: M5 Step 9o — retail content of the data_ptr block

HYPOTHESIS-ID: m5-audio-destub-sequence

s4216: data_ptr writer = PC 0x8009177C (known since s3482); retail stores the same 7728 B heap blocks. H-builder-wrong-target / H-builder-skipped refuted. See docs/M5-S4216-DATAPTR-RECONCILE.md.

Hypotheses:
- H-content-matches: retail block 0x80171CE0 (title/1024 phase, physical 0x171CE0) also holds ASCII names + 0x28-stride pointer structs => input legit, divergence is in ucode consumption/output.
- H-content-differs: retail block holds real audio records (zeros/commands, no 0x801xxxxx pointers) => content producer diverges in the port.
Discriminator: tools/oracle (README) — whole-RDRAM watch control first (~1.6M fires/8 s), then read 0x1E30 bytes at physical 0x171CE0 at several title-phase VIs; compare record0 words/ASCII fraction with s4214 scan (scratch/agent/s4214_record_scan.sh output).
Any lib/ edit needs submodule-patches/export.sh + commit.
