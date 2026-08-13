# NEXT work unit (ovl1c 0x1EBC $30-return)

HYPOTHESIS-ID: m3-postsec2-lle-control-flow

s761 0x13C0 jal-L_112C widen is LIVE (H-13c0-jal-112c).
All [clip-stray] 0; ovl20 04-return class CLOSED. Residual is
UJ `0x1EBC` n=557 + `0x1E7C` n=69 from OVL1C_1F04 jr $30
(line 4987). First UJ is before the first sec2 row. Label
`OVL1C_1EBC:` exists (6k sequential). There is no case
0x1EBC. Do **not** route 0x1E7C this step. Do **not** widen
0x1E6C to 153==0x20. Do **not** touch ovl20 dest 0x12A0 or
the 0x13C0/0x13B8 04-arms.

## Competing hypotheses

- **H-1ebc-ovl1c-30ret:** inserting `case 0x1EBC` /
  `153==0x1C` → `OVL1C_1EBC` drops UJ `0x1EBC` to 0;
  dest `res=0x20 tgt=0x12A0` stays LIVE; ovl1c
  `res=0x1C tgt=0x1EA8` stays LIVE; 4/4 boot `dl06=2/2/0`;
  sibling UJ `0x1E7C` remains (predicted leftover).
- **H-1ebc-breaks-06:** 0x1EBC fires before sec2; the new
  case steals a boot/title 0x1EBC site and unpairs dl06
  or kills an ovl1c dest.
- **H-1ebc-restores-e9:** section-2 E9 match leaves the
  src0=0x000178 family (s761 was 6/64). Needs a new src0
  / rdpFs climb, not another 3–6 boot-DL copies.
- **H-1ebc-not-only:** 0x1EBC→0 and a new UJ sibling
  appears besides the known 0x1E7C (0x1E8C / 0x1ECC).

## Discriminating measurement

One build, one soak (s761 recipe; [CRASH] is a note). Same-run
controls: clip `res=0x04`, ovl24 `res=0x24 tgt=0x12A0`, ovl20
`res=0x20 tgt=0x12A0`, ovl1c `res=0x1C tgt=0x1EA8`, `dl06=`.

- UJ 0x1EBC → 0 + dest LIVE + dl06 2/2/0 + 0x1E7C leftover →
  H-1ebc-ovl1c-30ret. Next is 0x1E7C.
- dl06 breaks or ovl1c dest dies → H-1ebc-breaks-06.
- E9 match gains a non-0x000178 src and rdpFs climbs →
  H-1ebc-restores-e9.
- UJ 0x1EBC stays nonzero → rewrite the case; 153 was not
  0x1C at the jr.

## Commands

    # fixup 6t: INSERT (no existing case) before
    #   case 0x1DB0:  /* fixup: clipsplice */
    # the same 6o/6p shape:
    #   case 0x1EBC: if (153==0x1C) route(0x1C,0x1EBC);
    #                goto OVL1C_1EBC; else clip-stray
    # Precondition: OVL1C_1EBC: already in the file (6k).
    # Do not add 0x1E7C / 0x1E8C / 0x1ECC this step.
    python3 tools/fixup_factor5_ucode.py \
      build/factor5_ucode/factor5_ucode_recompiled.c
    DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer \
      cmake --build build -j8 --target RogueSquadron64Recomp
    # soak: copy s761 recipe; require
    #   [ovl-route] res=0x20 tgt=0x12A0
    #   [ovl-route] res=0x24 tgt=0x12A0
    #   [ovl-route] res=0x1C tgt=0x1EA8
    #   [ovl-route] res=0x04
    #   dl06=
    # Discriminator is UJ 0x1EBC count, not clip-stray.
    # probe.sh rc=3 on crash — do not use set -e around it if
    # the control greps must still run.

ORIGIN: OVL1C_1EAC jal 0x1ED4 at IMEM 0x1EAC, r31=0x1EBC.
OVL1C_1ED4 saves $ra → $30, jals 0x1F0C (return 0x1F04).
OVL1C_1F04 jr $30. Legitimate ovl1c $30-return; route it.
