# Dump the two texture-pointer chunk fields
HYPOTHESIS-ID: g1d-widescreen

Session 6208 selects H-recompute and refutes H-f0, H-node, and H-miss.
Keep the image drop. Do not revert it. Do not skip
`Framebuffer::copyNativeToRAM`. Do not retarget `0x8096D600`. Do not
write `0x801163E8`. Do not change n=3's `t0`. Do not raise `osMemSize`.
Do not patch the RDP stream. Do not move `f0`. Do not retarget the `swl`
at `0x8000D5A8`. Do not patch the chunk field.

The phase-4 texture address is a word in an n=3 pool chunk. It is not
`0x801163E8`, `0x801163F0`, or `0x801163F4` (no DMA from that page). It
is not the root `data_ptr` (index 132 in both arms). Control:
`0x80A6AA10` at `0x80B29954` = pool `0x80B25000` + index 71 * 0x108 +
0x1C. Wide: `0x80AE6120` at `0x80AF08C4` = pool `0x80AE6E00` + index 150
* 0x108 + 0x14. The other wide prefixes are also at chunk+0x14. Guest
PC on the RSP read is `0x80007904`. The logged `in_node` flag is blind
because `root_dl` is stored with a 23-bit mask. Do not treat it as
evidence.

The open fact is the 8-byte field difference, on different chunk
indexes. One paired run, same recipe as `scratch/agent/s6208_run.sh`
(12 MB, sequential, ctl 4:3 then wide 16:9, from `build/`, SIGKILL,
screen unlocked, do not pass `ROGUESQ_FB_WIDTH`). Keep `[g1d-img]`,
`[g1d-drop]`, and `[g1d-ptr]`. On the first prefix hit in each arm,
also log 0x20 bytes before the word and 0x20 bytes after it, as
big-endian words, plus the pool-relative chunk index and the offset
within that chunk. One dump per arm. Do not add a store watch.

- H-shift: the 0x40-byte windows match after an 8-byte slide (control
  +0x1C lines up with wide +0x14), and the bytes on either side of the
  pointer are the same values. One field, shifted. Name the aligned
  offset. Do not patch it.
- H-two: the windows do not match under that slide. Two different
  slots. Name both offsets and the neighboring words that disagree.
  Do not pick one.
- H-moved: the first prefix word is not at `0x80B29954` / `0x80AF08C4`.
  The chunk moved. Report the new address, index, and offset. Do not
  compare the windows until both arms hit the known prefix values.

Control must still show `w78=05200002` at `data_ptr=0x80B2D820` and
`[g1d-drop] aspect=4:3 drop=0`. Wide `e8` must stay `0x80AE6E00` and
`[g1d-drop]` must stay `drop=0x19200`. A control hit on `0x80A6AA10`
remains the positive control for the scan.
