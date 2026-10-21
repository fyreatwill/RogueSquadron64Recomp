# NEXT: name the writer of the w=442 SetColorImage in forced lvl7 (ORIGIN for the copyToRAM guard).
Hypotheses: (H1) misparsed DL data word (ucode interprets non-command data as SetColorImage); (H2) game genuinely sets a 442-wide image (odd viewport/letterbox) in lvl7 flight; (H3) stale/corrupt DL from a freed task buffer.
Discriminator: at the first SKIP_WILD_W in lib/rt64/src/hle/rt64_state.cpp (~line 134), log the raw 64-bit RDP word, the DL pointer/task it came from, and 8 words before/after. Build once, run s5710_lvl7a recipe x3 concurrently-free (one at a time), expect the wild event in ~2/3. Positive control: SKIP_WILD_W counter >=1 in the same run.
H1 => words around look like data; H2 => neighbours are sane RDP cmds; H3 => task ptr in freed region.
Any lib/ edit => ./submodule-patches/export.sh + commit.
HYPOTHESIS-ID: g1-level-select
