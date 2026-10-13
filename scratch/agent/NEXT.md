# Next work unit

HYPOTHESIS-ID: H-alloc-window-sched-switch

Voice +0x34 "late" is closed (s4708). Question: in RETAIL, does the mixer run between the allocator's count store (0x8008F0CC, phys 0x149700) and base store (0x8008F0EC, phys 0x1496F8)?

Hypotheses: (A) retail never switches threads inside the window; our scheduler preempts where retail doesn't -> fix is scheduling fidelity. (B) retail switches, but count<=capacity because retail never reaches a 6th alloc with a larger count -> upstream cause is the song-channel alloc sequence. (C) retail has the same race latently.

Commands (from repo root, one game run at a time; positive control FIRST):
1. Control: `tools/oracle/build/rs64_oracle --core ~/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib --rom ~/Documents/Tools/rogue_squadron64/rogue_squadron.z64 --secs 60 --watch-write 0x000000:0x7FFFFF` -> must report hits (instrument live).
2. Real: same command with `--secs 180 --watch-write 0x1496F8:0x149704`, plus `--watch-pc` on mixer entry 0x800913xx (find exact entry via recomp symbol map) to see interleaving. Title -> hangar.
3. Log order of count-store vs base-store hits and any mixer exec between them.

Discriminating outcomes: a 6th count store of 32 in retail -> (A) or (C) (then check mixer interleave: none -> A, some -> C); only counts 20,17,16,15,18 -> (B). Zero hits on the real watch with control passing = wrong address; re-derive phys from KSEG0 (addr & 0x1FFFFFFF).
