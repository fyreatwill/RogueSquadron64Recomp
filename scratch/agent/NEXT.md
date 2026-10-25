# Does the 0x200 texture ladder enter the wide pool?
HYPOTHESIS-ID: g1d-widescreen

Session 6211 selects H-read-tex and refutes H-unread.
Keep the image drop. Do not revert it. Do not skip
`Framebuffer::copyNativeToRAM`. Do not retarget `0x8096D600`. Do not
write `0x801163E8`. Do not change n=3's `t0`. Do not raise `osMemSize`.
Do not patch the RDP stream. Do not move `f0`. Do not retarget the `swl`
at `0x8000D5A8`. Do not patch either texture slot. Do not dump another
chunk window. Do not restore the per-DMA hash stream.

Wide pool `0x80AE6E00`. Phase 4 fully DMA-reads chunk 151
(`dram=0x80AF09B8`, `len=0x10F`, `ov=0x108`, guest PC `0x80007904`).
The word at +0x14 is `0x80AE5F20`, the address half of `FD100000`
(RDP SetTextureImage). The s6208 exact/stride list does not keep it.
The same run's `[g1d-img-hit]` logs `kind=ti addr=0xAE5F20` and
`0xAE5D20`. The 48-line cap logged 23 distinct wide TI addresses. The
`0x200` ladder in that cap is `0xAE4920`..`0xAE6B20`. Pool physical
base is `0xAE6E00`, so the next steps would be `0xAE6D20` (still below)
and `0xAE6F20` (inside the pool). `ti_hit` on that arm is 5120. The cap
cannot say the ladder stops.

One paired run, same recipe as `scratch/agent/s6211_run.sh` (12 MB,
sequential, ctl 4:3 then wide 16:9, from `build/`, SIGKILL, screen
unlocked, do not pass `ROGUESQ_FB_WIDTH`). Keep `[g1d-img]`,
`[g1d-drop]`, and `[g1d-ch]`. In the phase-4 image scanner
(`src/main/rt64_render_context.cpp`, the `s_hits < 48` hit log), do not
raise that print cap. Beside it, record every distinct TI address whose
low 24 bits lie in `[0xA6A000, 0xB00000)`. Read the pool base from
`0x801163E8` (the n=3 `[g1d-pool]` word). Print one `[g1d-ti]` line per
arm: distinct count, min, max, how many distinct addresses are
`>=` the pool's physical base, the lowest such address, and an overflow
bit. Cap the stored set at 256. If it fills, keep counting the
above-pool total and tracking max. If the above-pool count is 1..8,
list those addresses on the same line. A periodic summary is enough;
do not print one line per hit.

- H-stop: wide above-pool count is 0 and max `< 0xAE6E00`. The sampled
  textures stay below the pool. Do not patch.
- H-cross: wide above-pool count is `> 0`. Name the lowest address and
  the count. Do not patch.

Control must still show `w78=05200002` at `data_ptr=0x80B2D820`,
`[g1d-drop] aspect=4:3 drop=0`, `[g1d-ch]` idx 72 `ov=0x108`, and a
`[g1d-ti]` set that contains `0xA6AA10`. Wide `e8` must stay
`0x80AE6E00`, `[g1d-drop]` must stay `drop=0x19200`, and the `[g1d-ti]`
set must contain `0xAE5F20`. A wide summary that does not contain
`0xAE5F20` is not a result. If the live pool word is not `0x80AE6E00`
on the wide arm, the run is invalid.
