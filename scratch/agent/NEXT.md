# NEXT: name the non-scalar writer of the command node
HYPOTHESIS-ID: g1d-widescreen

Session 6198 closed the scalar path. SB/SH/SW/SD that change a word into
`05200002`, `00010001`, or `0001FFFF` do not touch either phase-4 command
node. The hook is not blind: the same run logged 259 `05200002` creates,
including `inflate_fast` at `0xA3DE48` (about 0xEFA50 below control
node+0x78). Control node 0 is still `dram=0x80B2D820` with `05200002` at
+0x78. Wide node 0 is still `dram=0x80AEF620` with the `00010001` fill from
+0x28. Do not add another scalar store hook. `rs_memset` (`0x800078EC`) was
a false credit when a byte store was scored on a word it left unchanged.

Do not change rendering. One env-gated witness, `ROGUESQ_LOG_G1D_FILLPC`
still set, plus a new `ROGUESQ_LOG_G1D_BLK` (name it that). Log only writes
that can produce a 0x80-byte or larger block without a scalar store:

- PI DMA completion whose RDRAM dest overlaps phys `>= 0x800000` (source,
  dest, length, guest PC).
- RSP `dma_dmem_to_rdram` with the same overlap (DMEM address, dest, length).
- `do_swl` / `do_swr` when the aligned word changes into one of the three
  command-node words. That hook lives in `recomp.h`; a `lib/` edit must be
  followed by `./submodule-patches/export.sh` in the same commit.

Keep the paired runner:

    zsh scratch/agent/s6179_g1d_rdp_words.sh

It stops when both arms have 160 phase-4 joins, one `root_seq=1
root_norm=0x003BD0`, and a fill summary. Wide copies plateau below 400; do
not wait for 400. SIGKILL the process group. Game logs are
`scratch/agent/m6/g1_lvl1_ctl/run.log` and `g1_lvl1_wide/run.log`. Join
block rows to that run's `[g1d-node] n=0` base. Do not hardcode the physical
address.

Positive control: control must show one logged block write whose dest range
covers that run's node+0x78, and the wide arm must show one whose dest range
covers node+0x28. A row that only overlaps the header or the RDP list at
+0x108 does not count; those words already match after relocation.

- H-dma: the covering write is a PI or RSP DMA. The source address (ROM or
  the other RDRAM region) is the measurement. Next iteration reads that
  source, it does not add another hook.
- H-swl: no DMA covers the body, and a `do_swl`/`do_swr` row does. That PC
  is the writer.
- H-host: neither DMA nor SWL covers the body even though the node dump
  still has the words. The writer is a host memcpy; the next witness is the
  C++ write into `g_recomp_rdram_for_wp_raw`, not another guest hook.

If the new log is empty everywhere while the old `05200002` exact rows still
fire, the block hook is blind. Fix it and rerun in the same iteration.
