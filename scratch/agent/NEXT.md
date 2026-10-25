# NEXT: classify the heap block under the phase-4 pool
HYPOTHESIS-ID: g1d-widescreen

Session 6202 refutes H-ec-hole as "the span under ec is free." Do not
write `0x801163E8`. Do not try a second address. Do not change `t0`,
`d8`, `dc`, `f0`, `f4`, `f8`, or `ec`. Do not raise `osMemSize`. Do not
skip the color-image writeback. Do not rerun the s6202 placement.

Witness: `scratch/agent/soak_results/s6202/witness.txt`.

The opt-in store at `0x80001010` computed `ec - t2` and stopped.
Control `outw=512` skipped: `e8=0x80B25000`, phase-4 `data_ptr=0x80B2D820`,
task-time word `+0x78 = 05200002` (`+0x28 = 00000000`). Wide
`base=0x8096D600`, `span_end=0x809B8600` (`0x809B8600 - 0x4B000`;
the older `0x8096D800` note is 0x200 high), rejected because the main
heap walk reached `heap_end=0x80B95BF0` from `heap_head=0x80154690`.
`e8` stayed `0x80AE6E00`. Task-time `+0x28` and `+0x78` on
`0x80AEF620` are still `00010001`. `r3` was not modified, and the wide
carve globals match s6201.

The same heap end is above the working control pool
(`0x80B25000 < 0x80B95BF0`). "End above the address" is therefore true
of the retail placement too. It does not say whether `0x8096D600` is a
live block.

One new log line, same site, no store. When `ROGUESQ_LOG_G1D_TASK=1`
and this carve would have considered the retarget, walk the main heap
from `0x8010FF18` and print the one block whose span covers
`0x80B25000` and the one whose span covers `0x8096D600`:
`addr`, `flags`, `tag`, `size`, and whether the two addresses are the
same block. Print it for both arms. A missing line is a blind hook.

Build once:
`env DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build build --target RogueSquadron64Recomp`

Then the s6202 recipe, sequential, from `build/`, SIGKILL, screen
unlocked, one game at a time:
`ROGUESQ_OSMEM_MB=12 ROGUESQ_LOG_G1D_TASK=1 ROGUESQ_LOG_PHASE=1`
`ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1`
`ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_AUDIO_UCODE=1 ROGUESQ_SPIN_YIELD=1`
with `ROGUESQ_ASPECT=4:3` then `16:9`. Do not pass `ROGUESQ_FB_WIDTH`.

- H-live: the candidate address is in a used block (flag 2) and the
  control pool address is not that block. The reject stands. Do not
  retarget there.
- H-free: both addresses fall in one free block (flag 1). The end test
  was coarser than occupancy. The same `ec-t2` candidate is still the
  only address in play; a later iteration may retry it only with a
  flag test in place of the end test.
- H-early: the control pool address is already inside a used block at
  this moment, same as the candidate. The walk is too early to name
  the retail reservation. Next witness is the same two addresses after
  `[g1d-pool] n=3`, not a new base.

Control must still show `w78=05200002` at `data_ptr=0x80B2D820`. Wide
`e8` must stay `0x80AE6E00`.
