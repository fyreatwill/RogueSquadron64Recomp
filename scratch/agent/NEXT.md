# NEXT work unit (widen remaining ovl24-only clip-resident returns)

HYPOTHESIS-ID: m3-postsec2-lle-control-flow

s745 selected H-1364-needed-but-not-e9: routing `0x1364` for
resident `0x24||0x04` killed that stray (4454→0) and kept boot
`dl06=2/2/0`, but E9 stayed 3/64. The new residual is the same
class: ovl24-only cases `0x1320`/`0x1330`/`0x1344` arriving with
`153=0x04` after `OVL24_1364` → `L_112C` restores `$ra` from
`0xB30` (saved by `OVL24_1358` before the `jal L_17F0`). Clip dest
is still `0x1DB0`, so IMEM `0x12A0..0x1384` is still ovl24.
`0x1DF4/00` is a different class — defer it.

Widen every remaining ovl24-only `goto rs64_clip_stray` case to
`0x153==0x24 || ==0x04` (not shared cases that fall through to
main `L_*`; not a bare always-OVL24). Keep the s744/s745
predecessor counters. Do not enable IMEM DMA.

## Competing hypotheses

- **H-ovl24-class-restores-e9:** routing the live 0x04 returns
  (`0x1320`/`0x1330`/`0x1344`, and any sibling that then fires)
  into `OVL24_*` → emit continues through `L_112C` and post-sec2
  FULL_SYNC recovers (E9 match >> 3/64; rdpFs climbs with GFX).
- **H-ovl24-class-needed-but-not-e9:** those strays go to 0 and
  ovl24 emit continues, but E9 match stays 3/64. Remaining leak is
  elsewhere (`0x1DF4/00`, ovl14, or a later class).
- **H-ovl24-class-breaks-06:** the extra 0x04 arms steal a
  main-image return and break the four boot `dl06=2/2/0` controls
  or bring UJ back.

## Discriminating measurement

One build: fixup 6e-family rewrite of the ovl24-only clip-stray
cases. One soak, same recipe as s743–s745. SIGKILL.

Outcomes:

- stray `0x1320/04` + `0x1330/04` + `0x1344/04` → 0 AND sec2 E9
  match >> 3/64 → H-ovl24-class-restores-e9; productize.
- those strays → 0, `dl06` still 2/2/0, E9 still 3/64 →
  H-ovl24-class-needed-but-not-e9; next is `0x1DF4`/ovl14.
- `dl06` breaks or UJ returns → H-ovl24-class-breaks-06; revert.

## Commands

    # edit tools/fixup_factor5_ucode.py: after 6e, rewrite every
    #   case 0x1xxx: if (RSP_MEM_BU(0X153, 0) == 0x24) { ... goto OVL24_* }
    #   goto rs64_clip_stray;
    # to also accept == 0x04. Then
    #   python3 tools/fixup_factor5_ucode.py build/factor5_ucode/factor5_ucode_recompiled.c
    #   DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build build -j8
    # one s745-shaped soak. SIGKILL. do not enable IMEM DMA.

ORIGIN: s744/s745 named the writer (CLIP_1E48 jr of OVL24_135C jal;
OVL24_1364 then jr's 0xB30). The 0x04 arms are routes of legitimate
returns, not guards.
