# Next work unit

HYPOTHESIS-ID: oracle-poke-mission-entry

s4727: port per-frame poll of 0x1F0D70..80 never shows width 1161 (control 0xCC3E4 passed); it shows uniform 16-byte fills at frames 268/457/458 (title phase), writer unknown.
Unit: widen the osViSwapBuffer_recomp poll (src/main/upstream_compat.cpp, ROGUESQ_LOG_S4727_IMG_WATCH) to log the extent (first/last differing word) of change around 0x1F0000..0x1F1000 at each event; run scratch/agent/s4727_run.sh once.
Outcomes: large aligned extent (>=0x1000, 0x40-aligned) => host/RT64 clear or copyToRAM; small extent matching a game memset => game code (compare retail 0x800078EC clear).
Positive control: 0xCC3E4 moves (already works).
