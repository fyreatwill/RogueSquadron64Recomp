# NEXT work unit (ovl1c 0x1E8C $30-return)

HYPOTHESIS-ID: m3-postsec2-lle-control-flow

s764 0x1E7C $30-return is LIVE (H-1e7c-ovl1c-30ret).
UJ 0x1E7C 91→0. Residual is UJ `0x1E8C` n=102 from
OVL1C_1F04 jr $30 (line 4987). First UJ is after leave
and before the first sec2 row. Label `OVL1C_1E8C:` exists
(6k sequential; lbu / beq 0x1ECC / 0x1EAC, else jal
0x1ED4 r31=0x1EA8 already a case). There is no case
0x1E8C. Do **not** add any other case this step. Do
**not** widen 0x1E6C to 153==0x20. Do **not** touch ovl20
dest 0x12A0 or the 0x13C0/0x13B8 04-arms.

## Competing hypotheses

- **H-1e8c-ovl1c-30ret:** inserting `case 0x1E8C` /
  `153==0x1C` → `OVL1C_1E8C` drops UJ `0x1E8C` to 0;
  dest `res=0x20 tgt=0x12A0` stays LIVE; ovl1c
  `res=0x1C tgt=0x1E7C` stays LIVE; 4/4 boot `dl06=2/2/0`;
  leftover UJ=0 (every ovl1c jal 0x1ED4 return now has
  a case: 0x1E18/1E2C/1E6C/1E7C/1E8C/1EA8/1EBC/1ECC/1F04).
- **H-1e8c-breaks-06:** 0x1E8C fires before sec2; the new
  case steals a boot/title 0x1E8C site and unpairs dl06
  or kills an ovl1c/ovl20 dest.
- **H-1e8c-restores-e9:** section-2 E9 match leaves the
  src0=0x000178 family (s764 was 12/64). Needs a new src0
  / rdpFs climb, not another 3–8 boot-DL copies.
- **H-1e8c-not-only:** 0x1E8C→0 and a new UJ sibling
  appears (ovl1c $30 class was not the last unhandled
  jr $30).

## Discriminating measurement

One build, one soak (s764 recipe; [CRASH] is a note).
s763 att1 stalled in cinematic, att2 hangar-stuck, att3
leave-craft SIGBUS (loadDatFile / 0x380000000) — if those
recur, re-run the same recipe; do not chase. Same-run
controls: clip `res=0x04`, ovl24 `res=0x24 tgt=0x12A0`,
ovl20 `res=0x20 tgt=0x12A0`, ovl1c `res=0x1C tgt=0x1E7C`,
`dl06=`.

- UJ 0x1E8C → 0 + dest LIVE + dl06 2/2/0 + UJ leftover 0 →
  H-1e8c-ovl1c-30ret. ovl1c $30-return class CLOSED.
  Next is a new E9/FS lead (not another 3–8 boot-DL copy).
- dl06 breaks or dest dies → H-1e8c-breaks-06.
- E9 match gains a non-0x000178 src and rdpFs climbs →
  H-1e8c-restores-e9.
- UJ 0x1E8C stays nonzero → rewrite the case; 153 was not
  0x1C at the jr.
- UJ 0x1E8C → 0 and a new UJ sibling appears →
  H-1e8c-not-only; name the writer before routing it.

## Commands

    # fixup 6w: INSERT (no existing case) before
    #   case 0x1DB0:  /* fixup: clipsplice */
    # the same 6o/6v shape:
    #   case 0x1E8C: if (153==0x1C) route(0x1C,0x1E8C);
    #                goto OVL1C_1E8C; else clip-stray
    # Precondition: OVL1C_1E8C: already in the file (6k).
    # Do not add any other case this step.
    python3 tools/fixup_factor5_ucode.py \
      build/factor5_ucode/factor5_ucode_recompiled.c
    DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer \
      cmake --build build -j8 --target RogueSquadron64Recomp
    # soak: copy s764 recipe; require
    #   [ovl-route] res=0x20 tgt=0x12A0
    #   [ovl-route] res=0x24 tgt=0x12A0
    #   [ovl-route] res=0x1C tgt=0x1E7C
    #   [ovl-route] res=0x04
    #   dl06=
    # Discriminator is UJ 0x1E8C count, not clip-stray.
    # probe.sh rc=3 on crash — do not use set -e around it if
    # the control greps must still run. If the process dies
    # before VI 1024, or never leaves hangar, re-run; do not
    # chase cinematic stall / loadDatFile SIGBUS
    # (si_addr=0x380000000).

ORIGIN: OVL1C_1E7C jal 0x1ED4 at IMEM 0x1E7C, r31=0x1E8C.
OVL1C_1ED4 saves $ra → $30, jals 0x1F0C (return 0x1F04).
OVL1C_1F04 jr $30. Legitimate ovl1c $30-return.
Route it.
