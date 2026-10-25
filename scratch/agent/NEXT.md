# NEXT: name the allocator that moved the command node by 0x3E200
HYPOTHESIS-ID: g1d-widescreen

Session 6200 selected H-rt64wb and refuted H-wrap. Do not add another
write hook. Do not skip, clamp, or restore the color-image writeback.
The pixels are legitimate. The wide command node overlaps them.

Both 12 MB arms write the same images, all ending at `0xB00000`:

- phase 2: `0xADD000` len `0x23000` (`320*224*2`)
- phase 3: `0xA6A000` len `0x96000` (`640*480*2`)
- phase 3, last writer before the node dump: `0xA95C00` len `0x6A400`
  (`640*340*2`, 61 rows). `[fballoc]` in both arms says `in=640x340`
  `top=0x80A95C00`.

Wide node `0xAEF620` is inside all three. Control node `0xB2D820` is
`0x2D820` past `0xB00000`. The delta `0x3E200` equals `(796-512)*448*2`,
one widened 448-line buffer. The `swl` at `0x8000D5A8` still writes
`0xB2D898` and does not repair the wide body. Tail pointers in the wide
node are the control pointers minus `0x3E200`.

The witness is `scratch/agent/soak_results/s6200/`. Do not rerun it.

Find the guest allocator that returns the gfx-task data pointer
(`0x80B2D820` control, `0x80AEF620` wide; both runs log it as
`[lle task] data=` and `[g1d-task] data_ptr=`). One paired build, no
second hook family:

- H-size: the returned block is larger in the wide arm by `0x3E200`
  (or by an integer multiple), so its start moves down into the color
  image. The size argument is the discriminator.
- H-base: the size is the same and the heap/arena base the allocator
  subtracts from is `0x3E200` lower in the wide arm. The base and the
  object that consumed that `0x3E200` are the discriminator. The likely
  consumer is one 448-line buffer grown from 512 to 796 wide, not the
  640x340 image, which did not move.
- H-not-this: the logged data pointer is not that allocator's return
  (it is a field copied from somewhere else). Name the copy. Do not
  guess a second delta.

Log the size, the returned pointer, and the guest PC in both arms.
Positive control: control must still report a pointer whose physical
address is `0xB2D820` (or the run's own control node, if the absolute
address moves; then use that run's `[g1d-node] n=0`). Wide must report
the wide node. A null log is a blind hook: fix it and rerun in the
same iteration. Do not hardcode `0x3E200` into the game. No rendering
change.
