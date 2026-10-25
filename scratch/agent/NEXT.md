# NEXT: find where the wide command node lost its payload
HYPOTHESIS-ID: g1d-widescreen

Session 6196 classified the first root-relative `mem=0x170` `len=0x10F` node
(`ctl 0x80B2D820`, `wide 0x80AEF620`, delta `0x3E200`). Pointer words relocate
and the RDP list at +0x108 matches. From offset `0x28` the wide node is the
word `0x00010001` where control is `0`, and that fill covers control's
fixed-point block at `0x78..0xB4` (`05200002`, `01750000`, `03ADFFFE`, ...).
The same tail pattern repeats on the second node (`0xB313F0` / `0xAF31F0`).
`0x00010001` is not a relocated pointer. This selects H-command for the node
body. The writer is unnamed.

Do not change rendering. Keep the existing paired runner and every current
control (`ROGUESQ_LOG_G1D_READS` included):

    zsh scratch/agent/s6179_g1d_rdp_words.sh

Extend the existing `[g1d-tail]` snapshot so the first two root-relative nodes
in each arm dump `0x200` bytes, not only `0x10F`. Search that window for the
control signature `05200002`.

Competing hypotheses:

- H-shift: wide still contains `05200002` at a different offset inside the
  `0x200` window. The RSP's `0x10F` read then misses it. The offset delta is
  the next measurement.
- H-fill: the signature is absent and the `0x00010001` fill covers the window.
  Next probe is the store PC of the first `0x00010001` word (control's zero
  and the `05200002` block are the comparison).
- H-alias: rejected as the game bug. The 23-bit mask is only in
  `g_e9prov.root_dl` / `[g1d-root]`. The DMA dram address is the full
  `0x80xxxxxx` pointer. Do not "fix" the witness mask as if it were the writer.

Positive controls, each arm: at least 160 phase-4 joins, 400 copies, and both
root sequences (seq1 `root_norm=0x003BD0`). The discriminator is whether
`05200002` occurs in the wide `0x200` window.

Game logs are `scratch/agent/m6/g1_lvl1_ctl/run.log` and `g1_lvl1_wide/run.log`,
not `soak_results/s6179/*.out`. Copy the `[g1d-tail]` lines out before a
`nomission` retry truncates `run.log`. SIGKILL the process group once the
controls and the `0x200` dump are on disk.
