# NEXT work unit (static overlay-0x20 successor audit)

HYPOTHESIS-ID: m3-postsec2-lle-control-flow

s757 routed dest `0x1EA8` / `153==0x1C` → `OVL1C_1EA8`: LIVE
(`[ovl-route] res=0x1C tgt=0x1EA8` last n=32896; UJ `0x1EA8`
1403→0). ovl1c `$30` pair (`0x1E6C`+`0x1EA8`) is complete.
E9 match still boot-shaped 3/64. Do **not** route the n=1
`$6==0` landing `0x1E7C`. Do **not** widen `0x1E6C` to
`153==0x20`. Do **not** splice overlay `0x20` as a
`0x1DB0` sibling.

ovl1c exits `j L_1268; ori $5, 0x20` at IMEM `0x1ECC`.
Table (ROM `0x39900`): desc at `0x3999A` = `0x2157`
(`r3=2` → dest `0x12A0`, len `0x157`), dram off
`0x1AF8` → image ROM `0x27108`. Same dest class as ovl24.

Static only. No rebuild, no splice, no game run. Write
`docs/M3-OVL20-SUCCESSOR-AUDIT.md`. Sources: ROM
`build/rogue_squadron.z64`, table at `0x39900`, generated
`OVL1C_1ECC` / main `L_12A0` / ovl24 `@0x12A0`,
`docs/M3-OVL24-CONTINUATION-AUDIT.md`.

## Competing hypotheses

- **H-ovl20-skipped-12a0-emit:** overlay 0x20 is an emit /
  vertex helper at dest `0x12A0` (ovl24-class), not a
  DL-push. Skipping it leaves main `L_12A0` to treat the
  payload as a child DL. Image differs from main `L_12A0`
  and from ovl24.
- **H-ovl20-is-restore:** overlay 0x20 is a restore-DMA of
  main `L_12A0` (ovl28-class), not emit. Then the 0x20 DMA
  skip is a no-op once ovl24 is not resident.
- **H-ovl20-is-1db0-sibling:** dest decode is wrong and
  0x20 actually lands at `0x1DB0`. Then the "do not splice
  as 1DB0 sibling" warning is false.
- **H-ovl20-not-the-e9-hole:** even if skipped-emit is
  true, the image has no FULL_SYNC producer (same as
  ovl24). E9 stay boot-shaped is then expected; the next
  live consume is a dest-`0x12A0` route swap, not an E9
  restore.

## Discriminating measurement

Offline, one pass:

- Disassemble ROM `0x27108` for `len=0x157` bytes at
  IMEM `0x12A0`. First words vs main `L_12A0`
  (`0x8E43005C`) and ovl24 (`ori $10,4; j L_15D0;
  ori $30,0x12AC`).
- Confirm dest: `0x2157 >> 12 == 2` → `lhu 0x78` =
  `0x12A0`.
- Name the exit (`j L_1268` + next `r5`, or restore-DMA).
- Say whether any instruction in the image can emit E9.

Outcomes:

- first words emit-shaped + dest 0x12A0 →
  H-ovl20-skipped-12a0-emit; live consume is a 6c-style
  route swap (do not overwrite `L_12A0`).
- first words == main L_12A0 or a restore-DMA →
  H-ovl20-is-restore; do not splice.
- dest decode lands 0x1DB0 → H-ovl20-is-1db0-sibling;
  re-open the 1DB0 splice warning.
- image has no E9 / no RDP-submit → H-ovl20-not-the-e9-hole
  (report alongside the dest/class outcome).

## Commands

    # no cmake, no probe, no RSPRecomp
    # python3 one-shot: dump table row r5=0x20 and
    #   first 16 words of ROM 0x27108 vs L_12A0 / ovl24
    # write docs/M3-OVL20-SUCCESSOR-AUDIT.md

ORIGIN: ovl1c `OVL1C_1ECC` is `j L_1268; ori $5, 0x20`.
Table desc `0x2157` at ROM `0x3999A` selects dest
`0x12A0`. The three s757 `[clip-stray] 0x1E6C/20` hits
are leftover `$30` after that request, not a reason to
widen the 0x1E6C case.
