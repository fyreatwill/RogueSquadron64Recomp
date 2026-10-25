# Compare the sibling texture-command windows
HYPOTHESIS-ID: g1d-widescreen

Session 6209 selects H-two and refutes H-shift and H-moved.
Keep the image drop. Do not revert it. Do not skip
`Framebuffer::copyNativeToRAM`. Do not retarget `0x8096D600`. Do not
write `0x801163E8`. Do not change n=3's `t0`. Do not raise `osMemSize`.
Do not patch the RDP stream. Do not move `f0`. Do not retarget the `swl`
at `0x8000D5A8`. Do not patch either texture slot. Do not add a store
watch.

The first phase-4 prefix is the address half of a `G_SETTIMG`
(`FD100000` immediately before the pointer) in both arms. Control:
index 71, chunk+0x1C, `0x80B29954` = `0x80A6AA10`. Wide: index 150,
chunk+0x14, `0x80AF08C4` = `0x80AE6120`. Chunk bytes `[0x00,0x10)` match
(`00000000,00000000,E6000000,00000000`). Control then has
`F5100000/07080200` (opcode 0xF5, G_SETTILE) and wide does not, so the
shared opcode sits 8 bytes later. The other neighbors disagree. The
`[g1d-win]` `chunk_off` field is decimal.

The open fact is whether that neighbor pattern is the aspect template
or one odd pair of chunks. One paired run, same recipe as
`scratch/agent/s6209_run.sh` (12 MB, sequential, ctl 4:3 then wide
16:9, from `build/`, SIGKILL, screen unlocked, do not pass
`ROGUESQ_FB_WIDTH`). Keep `[g1d-img]`, `[g1d-drop]`, and `[g1d-ptr]`.
Log two `[g1d-win]` lines per arm: the first prefix, and the next
prefix whose `word_at` differs. Do not log the same address twice
(a later DMA starts 8 bytes earlier and repeats the wide word).

- H-template: the second control word is `0x80A6BA10` at index 72
  +0x1C, and its before/after words equal the first control window.
  The second wide word is `0x80AE5520` at index 151 +0x14, and its
  before/after words equal the first wide window. The address word
  itself may differ. The command list differs by aspect. Do not patch.
- H-unique: a second window's before/after differs from the first
  window in that arm, ignoring the address word. Name the disagreeing
  words and both chunk offsets. Do not treat index 71/150 as the
  template.
- H-other: the second distinct `word_at` is not the sibling above.
  Report the address, index, and offset. Do not compare neighbors.

Control must still show `w78=05200002` at `data_ptr=0x80B2D820` and
`[g1d-drop] aspect=4:3 drop=0`. Wide `e8` must stay `0x80AE6E00` and
`[g1d-drop]` must stay `drop=0x19200`. The first control hit on
`0x80A6AA10` remains the positive control for the scan.
