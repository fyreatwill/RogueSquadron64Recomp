# Are the wide texture pointers a fill, or real texels?
HYPOTHESIS-ID: g1d-widescreen

Session 6212 selects H-stop and refutes H-cross. The wide phase-4
TI set in `[0xA6A000, 0xB00000)` is 23 addresses, `ov=0`, max
`0xAE6B20`, above-pool count 0 against live pool `0xAE6E00`.
Do not patch. Keep the image drop. Do not raise the 48-line
`[g1d-img-hit]` cap. Do not skip `Framebuffer::copyNativeToRAM`.
Do not retarget `0x8096D600`. Do not write `0x801163E8`. Do not
change n=3's `t0`. Do not raise `osMemSize`. Do not move `f0`.
Do not retarget the `swl` at `0x8000D5A8`. Do not patch either
texture slot.

The 23 starts all lie inside the logged phase-3 writeback
`0xA50E00`..`0xAE6E00` (that log is sampled, not a complete
census). `0xAE6B20` is only `0x2E0` below the pool. That does
not say what bytes are there when phase 4 samples them.

One paired run, same recipe as `scratch/agent/s6212_run.sh`
(12 MB, sequential, ctl 4:3 then wide 16:9, from `build/`,
SIGKILL, screen unlocked, do not pass `ROGUESQ_FB_WIDTH`).
Keep `[g1d-img]`, `[g1d-drop]`, `[g1d-ch]`, and `[g1d-ti]`.
On a phase-4 TI hit, once per address, print one `[g1d-tb]`
line for `0xA6AA10`, `0xAE5F20`, and `0xAE6B20`: the address
and 8 big-endian words at that physical address (RDRAM `^ 3`).
No other addresses. No per-hit line.

- H-fill: both wide dumps are one repeated word (`00000000` or
  `00010001` or another single word), and the control dump at
  `0xA6AA10` is not that word. Do not patch.
- H-texture: the control dump and both wide dumps are non-fill.
  Do not patch.
- H-split: `0xAE5F20` is non-fill and `0xAE6B20` is a repeated
  word, or the reverse. Name which. Do not patch.

A control line that does not contain `0xA6AA10` is not a result.
A wide run that does not print both `0xAE5F20` and `0xAE6B20`
is not a result. Control must still show `w78=05200002` at
`data_ptr=0x80B2D820`, `[g1d-drop] aspect=4:3 drop=0`, and
`[g1d-ch]` idx 72 `ov=0x108`. Wide `e8` must stay `0x80AE6E00`,
`[g1d-drop]` must stay `drop=0x19200`, and `[g1d-ti]` must stay
`above=0` with `max=0xAE6B20` and `saw=0xAE5F20`. If the live
pool word is not `0x80AE6E00` on the wide arm, the run is invalid.
