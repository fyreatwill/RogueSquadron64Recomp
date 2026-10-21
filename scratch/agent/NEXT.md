# NEXT: name the writer of the w=442 SetColorImage in forced-lvl7 (H1 misparsed DL data vs H2 real emission).
Build once: in lib/rt64/src/hle/rt64_state.cpp at the first SKIP_WILD_W log (~line 175) also print the raw RDP words of the SetColorImage and the DL pointer/ucode op that produced it. Positive control: existing SKIP_WILD_W line must fire in the same run. Run lvl7 x3 (queue as soaks, recipe like scratch/agent/soak_queue/done/s5712_lvl7a.sh).
H1: words are a misparse (stale/shifted DL pointer advance, see docs/F5-UCODE-REFERENCE.md) -> raw word is not a valid SetColorImage encoding of w=442. H2: game really emits it -> word decodes cleanly, DL ptr in game RAM.
Fold s5712_lvl7c verdict first (grep SKIP_WILD_W / 'exceeds readback' in scratch/agent/m6/s5712_lvl7c/run.log).
Any lib/ edit => ./submodule-patches/export.sh + commit.
HYPOTHESIS-ID: g1-level-select
