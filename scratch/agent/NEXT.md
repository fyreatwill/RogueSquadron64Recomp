# NEXT: reclassify the same two addresses after the pool clear
HYPOTHESIS-ID: g1d-widescreen

Session 6203 selects H-early and refutes H-free and H-live. Do not
write `0x801163E8`. Do not try a second address. Do not change `t0`,
`d8`, `dc`, `f0`, `f4`, `f8`, or `ec`. Do not raise `osMemSize`. Do not
skip the color-image writeback. Do not retarget `0x8096D600` yet.

Witness: `scratch/agent/soak_results/s6203/witness.txt`.

At the `0x80001010` store, with `ROGUESQ_LOG_G1D_TASK=1`, both arms
walked the main heap from `0x8010FF18` (head `0x80154690`, 109 blocks
to the hit). `0x80B25000` and `0x8096D600` are the same block:

```
addr=0x808B77F0 flags=0x0006 tag=0x0000 size=0x2DB000
```

Span is `[0x808B77F0, 0x80B92800)`. The free bit is clear. Bit 1 (the
used mark `coalesceFreeHeapBlocks` tests at `0x80002398`) is set, and
bit 2 is also set. `coalesceFreeHeapBlocks` at `0x8000235C` does not
skip a block whose flags `& 6` are nonzero. Control
`data_ptr=0x80B2D820` still reads `w78=05200002`. Wide `e8` stayed
`0x80AE6E00` and `w28=w78=00010001`. Carve n=3 and pool n=3 match
s6202. The new log does not store.

`[g1d-pool]` at `0x80018030` is not `rs_malloc`. It is the size
computation inside `buildAndRegisterDefaultMaterial` (`funcs_4.c`),
`v1 = base + bytes`, immediately before the pool clear. The carve-time
walk may simply be early, which is what H-early claimed. One new log
line, same site, no store. When `ROGUESQ_LOG_G1D_TASK=1` and this is
pool call n=3, walk from `0x8010FF18` again and print the block
covering `0x80B25000` and the block covering `0x8096D600`: `addr`,
`flags`, `tag`, `size`, `same`, `nblk`, `head`. Tag the line
`[g1d-hblk-pool]` so it cannot be confused with `[g1d-hblk]`. Print it
for both arms. A missing line is a blind hook.

Build once:
`env DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build build --target RogueSquadron64Recomp`

Then the s6203 recipe, sequential, from `build/`, SIGKILL, screen
unlocked, one game at a time:
`ROGUESQ_OSMEM_MB=12 ROGUESQ_LOG_G1D_TASK=1 ROGUESQ_LOG_PHASE=1`
`ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1`
`ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_AUDIO_UCODE=1 ROGUESQ_SPIN_YIELD=1`
with `ROGUESQ_ASPECT=4:3` then `16:9`. Do not pass `ROGUESQ_FB_WIDTH`.

- H-same: both arms still report `0x808B77F0` / flags `0x0006` /
  size `0x2DB000` / same=1. The pool clear does not subdivide it.
  The candidate is inside the live block that already held the retail
  pool at the carve store. Do not retarget `0x8096D600`. The next
  witness is the writer of that header, not another address.
- H-split: the two addresses are different blocks after the clear.
  If the candidate is then free (flag bit 0) and the control address
  is not, the carve-time walk was early and a later iteration may
  retry `ec-t2` with a flag test in place of the end test. If the
  candidate is non-free and distinct, the reject stands.
- H-grow: the wide covering size is no longer `0x2DB000` while control
  stays `0x2DB000`. That is the width-dependent block s6128 saw. Record
  its flag. Do not retarget until that flag is known.

Control must still show `w78=05200002` at `data_ptr=0x80B2D820`. Wide
`e8` must stay `0x80AE6E00`. The carve-time `[g1d-hblk]` line must
still fire, or the new hook has no positive control.
