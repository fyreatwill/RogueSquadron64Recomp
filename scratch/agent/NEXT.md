# Does phase 4 read wide pool chunk 151?
HYPOTHESIS-ID: g1d-widescreen

Session 6210 selects H-other and refutes H-template.
Keep the image drop. Do not revert it. Do not skip
`Framebuffer::copyNativeToRAM`. Do not retarget `0x8096D600`. Do not
write `0x801163E8`. Do not change n=3's `t0`. Do not raise `osMemSize`.
Do not patch the RDP stream. Do not move `f0`. Do not retarget the `swl`
at `0x8000D5A8`. Do not patch either texture slot. Do not add a store
watch. Do not compare the wide neighbor bytes. Do not rerun the
control -0x20 comparison: idx 72 matches idx 71 except `04C304C3` vs
`00000000` at -0x20, and that already refutes H-template on control.

Wide pool `0x80AE6E00`. Chunk 150 holds `0x80AE6120` at +0x14
(`0x80AF08C4`). The next logged prefix is chunk 157 +0x14
(`0x80AF0FFC` = `0x80AE5520`), not chunk 151 +0x14 (`0x80AF09CC`).
The s6210 pointer log has 0 hits in chunks 151..156, and it only
records words in `[0xA6A000, 0xB00000)`. The first wide window's word
at -0x20 is `0x80AF0DD8` (chunk 155's start) then `B5000000`. That is
not a proven link. Do not chase it in this run.

One paired run, same recipe as `scratch/agent/s6210_run.sh` (12 MB,
sequential, ctl 4:3 then wide 16:9, from `build/`, SIGKILL, screen
unlocked, do not pass `ROGUESQ_FB_WIDTH`). Keep `[g1d-img]`,
`[g1d-drop]`, and `[g1d-ptr]`. On a phase-4 DMA whose range overlaps
pool chunk 151 (wide; start `0x80AF09B8`, length `0x108`) or chunk 72
(control; start `0x80B29A40`, the positive control), log one
`[g1d-ch]` line: arm pool, chunk index, dram, len, guest pc, and the
first 8 big-endian words at the chunk start. Also log one line when a
phase-4 DMA overlaps any byte of wide chunks 151..156 even if it
misses the first `0x20`. Cap 4 lines per arm. Do not restore the
per-DMA hash stream.

- H-unread: control logs chunk 72 (positive control) and wide logs
  zero lines whose range overlaps chunk 151 or chunks 151..156. Phase
  4 does not read that span. Do not patch.
- H-read-other: wide overlaps chunk 151 and none of its first 8 words
  is a pointer into `[0xA6A000, 0xB00000)`. Name the words. Do not patch.
- H-read-tex: wide overlaps chunk 151 and one of those words is a
  texture pointer the exact list missed. Name the word and its chunk
  offset. Do not patch.

Control must still show `w78=05200002` at `data_ptr=0x80B2D820` and
`[g1d-drop] aspect=4:3 drop=0`. Wide `e8` must stay `0x80AE6E00` and
`[g1d-drop]` must stay `drop=0x19200`. The chunk-72 line is the
positive control. A wide log with no chunk-72-equivalent control line
is not a result.
