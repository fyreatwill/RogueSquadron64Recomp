# Next work unit (s4287): replicate restore arm and qualify as default

HYPOTHESIS-ID: m5-audio-destub-sequence

s4286: WRAP_FLUSH=1 + WRAP_RESTORE=1 + S4272_CAP=0x2000 -> ODD cimgs 0 vs 60 (same phases, control postDiff=0). Single run.
Hypotheses: Q1) reproducible and also kills fb-set growth / 0x130393 wipe; Q2) ODD returns on repeat (first run luck); Q3) restore costs CPU/memory enough to hurt (per-range vector alloc, 2.6M ranges/53s).
Discriminator: run `zsh scratch/agent/s4286_restore.sh` 2 more times (compare odd counts), also grep `[fbset]`/tracked framebuffer counts and the 0x130393 copyToRAM wipe line per arm; extend to 75s+ for VI 512 if reached.
Then: make restore default-on (env =0 to disable), avoid per-range allocation, commit with ORIGIN line.
