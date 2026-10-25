# NEXT: name the free that replaces the carve-time heap block
HYPOTHESIS-ID: g1d-widescreen

Session 6204 refutes H-same and the stated H-grow. The carve-time
block `0x808B77F0` flags `0x0006` size `0x2DB000` is gone by pool
call n=3. Do not retarget `0x8096D600`. Do not write `0x801163E8`.
Do not change `t0`, `d8`, `dc`, `f0`, `f4`, `f8`, or `ec`. Do not
raise `osMemSize`. Do not skip the color-image writeback. Do not add
another heap walk.

Witness: `scratch/agent/soak_results/s6204/witness.txt`.

At `[g1d-hblk-pool]` (`0x80018030`, n=3) both arms walk 21 blocks from
head `0x80154690` and stop at `ec-0x10`. `0x8096D600` is inside
`0x80195180` flags `0x0001` (free bit set, bits 1 and 2 clear), size
`0x861660` in 4:3 and `0x823460` in 16:9. The delta is `0x3E200`, the
same as `ec`. `0x80B25000` is not covered. Both live pool bases are
above the stop: control `0x80B25000`, wide `0x80AE6E00`. The wide pool
`[0x80AE6E00, 0x80B31D58)` still crosses the color images that end at
`0x80B00000`. `ec-t2` is the wrong hole: it sits in the free block,
and the retail pool sits above the terminator.

The hooks already in `rs_free` (`ROGUESQ_LOG_RS_FREE`) and
`coalesceFreeHeapBlocks` (`ROGUESQ_LOG_COALESCE_HEAP_ENTRY`) name a
caller. No rebuild. The free log is uncapped; keep only the rows
between `[g1d-hblk]` and `[g1d-hblk-pool]`.

Same s6204 recipe, sequential, from `build/`, SIGKILL, screen
unlocked, one game at a time. Add the two env vars. Do not pass
`ROGUESQ_FB_WIDTH`.

`ROGUESQ_OSMEM_MB=12 ROGUESQ_LOG_G1D_TASK=1 ROGUESQ_LOG_PHASE=1`
`ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1`
`ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_AUDIO_UCODE=1 ROGUESQ_SPIN_YIELD=1`
`ROGUESQ_LOG_RS_FREE=1 ROGUESQ_LOG_COALESCE_HEAP_ENTRY=1`
with `ROGUESQ_ASPECT=4:3` then `16:9`.

- H-free: in that window, an `[rs-free]` pointer is `0x808B77F0` or
  its block contains that header, or the freed span ends at `ec-0x10`.
  `caller_ra` is the writer. Record the wide-versus-control pointer
  delta. Do not retarget.
- H-coalesce: no such free, but a `[coalesce-entry]` `a0`/`a1` covers
  `0x808B77F0` or `0x80195180`. `ra` is the writer. Do not retarget.
- H-neither: neither tag touches that range. The positive control is
  then that the tag appears somewhere else in the same log. The next
  witness is a store of the header words `0x808B77F0` and
  `0x80195180`, not a pool move.

Control must still show `w78=05200002` at `data_ptr=0x80B2D820`. Wide
`e8` must stay `0x80AE6E00`. `[g1d-hblk-pool]` must still report flags
`0x0001` at `0x80195180`, or the window has no positive control.
