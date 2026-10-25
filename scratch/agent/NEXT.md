# NEXT: name the host writer of the wide command-node fill
HYPOTHESIS-ID: g1d-widescreen

Session 6199 closed the guest block paths. Do not add another scalar or
`swl` hook, and do not re-hunt `05200002`.

Control node 0 (`dram=0x80B2D820`, phys `0xB2D820`) has `05200002` at +0x78.
That word is `swl` at guest PC `0x8000D5A8`, phase 3, `00000000`->`05200002`,
dest phys `0xB2D898`. The instruction is the 8-byte `lwl`/`lwr`/`swl`/`swr`
copy at `L_8000D584` inside the generated symbol `heapFreeListDequeue`.
The wide process's same PC still writes absolute `0xB2D898`, which is
`0x3E200` above wide node 0 (`dram=0x80AEF620`, phys `0xAEF620`). Wide
node+0x28 is 81 words of `00010001` (`fill_off=40`). Joins of
`scratch/agent/soak_results/s6199/` and `s6199b/` found zero PI DMA, RSP
`dma_dmem_to_rdram`, `zmemcpy`, or signature `swl`/`swr`/`sdl`/`sdr` rows
on that window. s6199b's 521 short signature rows and 114 `zmemcpy` rows
are the positive control that the short scan is not blind.

Do not change rendering. Keep `ROGUESQ_LOG_G1D_BLK` and call the existing
`rs64_g1d_blk_dma` from the host copies that write the rdram the node dump
reads (`g_rdram_for_submit`, set in `rsp_dpc_submit`). New kinds, distinct
from `pi` / `rsp` / `zmemcpy` / `swl`:

- `rt64wb`: `Framebuffer::copyNativeToRAM`
  (`lib/rt64/src/hle/rt64_framebuffer.cpp`), after the pixel bytes are
  stored. dest = `dst - g_recomp_rdram_for_wp_raw` when `dst` is inside
  that buffer; len = the row span actually copied. Skip a dst outside it.
- `wrap`: the shadow install `memcpy` in `src/rsp/dpc_bridge.cpp` (the
  `ROGUESQ_WRAP_RESTORE` path, default on, about line 3020). dest =
  `r.first`, len = `r.second - r.first`.
- `unwrap`: the `liveSave` copy-back immediately after
  `submit_rdp_range` (about line 3025), same range.

Do not hook `rs64_s4223_memcpy`. It only prints `dst==0x8013A5C0` and
does not store. A `lib/` edit must be followed by
`./submodule-patches/export.sh` in the same commit.

The paired runner now writes `scratch/agent/soak_results/s6200/` and
retries the node extract after SIGKILL. Do not point it back at s6199
or s6199b.

    zsh scratch/agent/s6179_g1d_rdp_words.sh

It stops when both arms have 160 phase-4 joins, one `root_seq=1
root_norm=0x003BD0`, and a fill summary. Wide copies plateau below 400.
SIGKILL the process group. Join block rows to that run's
`[g1d-node] n=0` base. Do not hardcode the physical address. If
`ctl.node` or `wide.node` is empty, the node line is in that arm's
`run.log`; extract it before concluding a miss.

Positive control: the control arm must still show the `swl` row covering
that run's node+0x78, and the wide node dump must still show the
`00010001` fill. One new host row must cover wide node+0x28. A row that
only overlaps the header or the RDP list at +0x108 does not count. The
new kinds must also fire at least once somewhere. If `rt64wb`, `wrap`,
and `unwrap` are all absent while `swl` still fires, the host hook is
blind: fix it and rerun in the same iteration.

- H-rt64wb: the covering row is `rt64wb`. Next iteration reads that
  framebuffer's address and size against the node. No new hook.
- H-wrap: the covering row is `wrap` or `unwrap`. Next iteration reads
  which shadow range it was and who filled the shadow. No new hook.
- H-still-host: the three new kinds fire elsewhere, none cover
  node+0x28, and the dump still has the fill. Do not invent a guest
  hook. The following witness is a watch on the node address installed
  before phase 4, and that plan has to learn the address from the run
  rather than hardcoding it.
