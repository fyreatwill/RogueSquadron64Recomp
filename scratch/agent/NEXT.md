# NEXT work unit (static provenance of clip-stray 0x1DF4/00)

HYPOTHESIS-ID: m3-postsec2-lle-control-flow

s746 selected H-ovl24-class-needed-but-not-e9: widening every
remaining ovl24-only clip-stray case to `0x24||0x04` killed that
class (0x1320/1330/1344 → 0), kept boot `dl06=2/2/0`, and moved
sec2 `last_ovl` from `0x24/0x1364` to `0x0C/0x1DF4`, but E9 stayed
3/64. Residual is `[clip-stray] tgt=0x1DF4 153=0x00` n=3157, all
line=451 (`L_11B0` TriGen DMA-helper `jr`). Case `0x1DF4` is
ovl12-only (`153==0xC` → `OVL12_1DF4`); `OVL12_1DD8` jals `L_122C`
with `$ra=0x1DF4`. Resident 0 means IMEM `0x1DF4` is the main
image — do **not** widen to `==0`. Overlay 14 is the rare-path
`0x1DB0` sibling (s742); keep it as a competing lead, not a
default route.

No rebuild. No IMEM DMA. Static audit only, written to
`docs/M3-1DF4-PROVENANCE-AUDIT.md`.

## Competing hypotheses

- **H-1df4-stale-ra:** overlay 12 set `$ra=0x1DF4`, then `0x153`
  was cleared / the window restored to main before `L_11B0` `jr`s
  it. IMEM `0x1DF4` is main bytes; the stray is correct; the bug is
  a leftover `$ra` after overlay teardown.
- **H-1df4-main-jal:** the main image itself jals a helper that
  returns to `0x1DF4`. Stray is correct; there is no ovl12 image to
  restore. Do not route.
- **H-1df4-window-still-ovl12:** `0x153` is 0 but IMEM `0x1DF4` is
  still the ovl12 image (resident byte desynced from the window).
  Then a later splice/route may be justified — only after this
  audit names the writer of both `$ra` and `0x153`.
- **H-1df4-ovl14:** the jump belongs to overlay 14's `0x1DB0`
  sibling, not ovl12. Route (if any) is `OVL14_*`, not `OVL12_1DF4`.

## Discriminating measurement

Offline, no soak. Enumerate every `r31 = 0x1DF4` / `jal` return-to-
`0x1DF4` writer in main, ovl12, clip, ovl24, and the ovl14 ROM
image. For each, say whether `L_11B0` is on the return path and
what `0x153` must be at the `jr`. Cite ROM offsets.

Outcomes:

- only ovl12 writes `$ra=0x1DF4` and main `L_11B0` is the return
  of `L_122C` after `0x153` is already 0 → H-1df4-stale-ra; next
  is a live predecessor of the stray (who cleared 0x153 / who
  restored the window), not a widen.
- main also writes `$ra=0x1DF4` → H-1df4-main-jal; close the
  stray as expected; pick the next leak or ovl14.
- ovl12 writes it and the window cannot have been restored yet
  (dest still `0x1DB0` or no restore-DMA since entry) →
  H-1df4-window-still-ovl12; then a predecessor soak before any
  route.
- ovl14 image owns `0x1DF4` → H-1df4-ovl14; treat as a new
  splice, not an ovl12 widen.

## Commands

    # no cmake, no game. Read:
    #   build/factor5_ucode/factor5_ucode_recompiled.c  (OVL12_1DD8,
    #     OVL12_1DF4, L_11B0, L_122C, main labels near 0x1DF4)
    #   build/factor5_ucode/factor5_ucode_ovl12_recompiled.c
    #   docs/M3-OVERLAY12-AUDIT.md
    #   docs/M3-OVL24-CONTINUATION-AUDIT.md (ovl14 sibling)
    #   tools/make_clip_composite.py overlay 14 if the ROM image
    #     is not already extracted
    # Write docs/M3-1DF4-PROVENANCE-AUDIT.md with the writer table.
    # Do not enable IMEM DMA. Do not widen case 0x1DF4.

ORIGIN: L_11B0 jr (line 451) of $ra=0x1DF4 with 153=0. Writer of
that $ra is unnamed until this audit. Do not mitigate first.
