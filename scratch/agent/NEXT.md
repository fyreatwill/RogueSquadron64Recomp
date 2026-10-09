# Next work unit (s4460): name the writer of a link equal to 0x80193C18 (node-8) in the musyx countdown list

HYPOTHESIS-ID: m5-ai-event-cadence

State (s4459): 0x80061520 = loadCharTextureSet font LUT fill, runs before the audio pool exists; pool nodes (0x14 stride from 0x80193C20) are built later over that freed memory. C18 holds stale 0xFF table data. B (fill clobbers live/linked nodes) refuted 6/6. Remaining hypotheses:
 (A) a stray store or node-8 arithmetic writes a link value 0x80193C18 into the head/a node's +0;
 (C) a node is reused/unlinked so the walk sees stale data.
Discriminator (passive, every run, no crash needed): in rs64_m5_lowfield_store (src/main/main.cpp, s4459 block) log any 'W' store with value in 0x80193C10..0x80193C1F: pc, addr, vi, cap 20. Positive control: temporarily also log value==0x80193C20 (legit head value, must fire >=6x per run). Also at 0x8009133C head-read, verify head chain stays on the 0x14 grid and print the first offender's pc-table (reuse s4457 list_check). A: a C18-valued store pc appears (pc names the writer). C: no such store but walk still reaches C18/bad next -> look for unlink/free paths (0x8008F7xx).
Run: build (DEVELOPER_DIR=... cmake --build build -j8), zsh scratch/agent/s4459_run.sh (6 arms x 120 s; +5436 is ~1/32 so also queue 3 more batches via scratch/agent/soak_queue).
