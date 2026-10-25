# NEXT: name the PC that fills the wide command node
HYPOTHESIS-ID: g1d-widescreen

Session 6197 refuted H-shift. Control node 0 contains `05200002` once at
offset `0x78`. Wide node 0 (`dram` base from `[g1d-node] n=0`) contains that
word at no byte offset in `0x200` bytes. `00010001` fills `0x28..0xD8`,
`0xE0..0x104` and `0x198..0x1FC`, with `0001FFFF` at `0xDC`. The header and
the RDP list at `0x108..0x194` are already written in both arms (9 pointer
words relocate by `0x3E200`; `0x178` is framebuffer width minus one). Do not
re-dump the node and do not treat those RDP immediates as the missing block.

Do not change rendering. The store hook `rs64_m5_writer_parity` passes
`value` as literal `0` and runs before the store
(`tools/fixup_game_funcs_vendored.py`). Read the word back from RDRAM on the
next hook entry, the same pending-store pattern as `rs64_s5654_vstore`.

Add one env-gated witness, `ROGUESQ_LOG_G1D_FILLPC`, phase >= 4 only. When
the word just stored is `0x00010001`, `0x0001FFFF`, or `0x05200002`, record
guest PC, address, value, and a monotonic order. Collapse per PC (count,
first address, last address, first order, last order) so a framebuffer clear
does not flood the log. Keep the existing paired runner and its controls,
including `ROGUESQ_LOG_G1D_READS`:

    zsh scratch/agent/s6179_g1d_rdp_words.sh

Copy the `[g1d-fill]` lines out before a `nomission` retry truncates
`run.log`. Game logs are `scratch/agent/m6/g1_lvl1_ctl/run.log` and
`g1_lvl1_wide/run.log`. Join store rows to that run's `[g1d-node] n=0` base.
Do not hardcode the physical address. SIGKILL the process group once both
arms have 160 phase-4 joins, 400 copies, both root sequences
(seq1 `root_norm=0x003BD0`), and the fill-PC summary.

Positive control: the control arm must show a PC whose stored word is
`05200002` at that run's node+`0x78`. If it does not, the hook is blind and
the run is void.

Competing hypotheses:

- H-skipped: that `05200002` PC never stores the value in the wide arm, and
  a `00010001` PC's address span already covers wide node+`0x28`. The body
  writer did not run; the fill is leftover.
- H-clobber: the same `05200002` PC hits wide node+`0x78`, and a later
  `00010001` store overwrites it. Order is the measurement.
- H-elsewhere: the `05200002` PC runs in the wide arm, but not inside the
  node. The address delta from node+`0x78` is the measurement.
- H-dma: no CPU store of `00010001` hits wide node+`0x28` even though the
  control positive control fired. The fill arrived by DMA; that is the next
  witness, not another store hook.
