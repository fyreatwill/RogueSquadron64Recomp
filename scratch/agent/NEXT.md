# NEXT work unit (ovl1c 0x1ECC $30-return)

HYPOTHESIS-ID: m3-postsec2-lle-control-flow

s762 0x1EBC $30-return is LIVE (H-1ebc-ovl1c-30ret).
UJ 0x1EBC 557→0. Residual is UJ `0x1ECC` n=2016 +
`0x1E7C` n=68 from OVL1C_1F04 jr $30 (line 4987).
First UJ is before the first sec2 row. Label
`OVL1C_1ECC:` exists (6k sequential; `j L_1268; ori $5,
0x20` — the ovl20-dispatch exit). There is no case
0x1ECC. Do **not** route 0x1E7C this step. Do **not**
widen 0x1E6C to 153==0x20. Do **not** touch ovl20 dest
0x12A0 or the 0x13C0/0x13B8 04-arms.

## Competing hypotheses

- **H-1ecc-ovl1c-30ret:** inserting `case 0x1ECC` /
  `153==0x1C` → `OVL1C_1ECC` drops UJ `0x1ECC` to 0;
  dest `res=0x20 tgt=0x12A0` stays LIVE; ovl1c
  `res=0x1C tgt=0x1EBC` stays LIVE; 4/4 boot `dl06=2/2/0`;
  sibling UJ `0x1E7C` remains (predicted leftover).
- **H-1ecc-breaks-06:** 0x1ECC fires before sec2; the new
  case steals a boot/title 0x1ECC site and unpairs dl06
  or kills an ovl1c/ovl20 dest. Extra risk: OVL1C_1ECC
  is `ori $5,0x20; goto L_1268`, so a wrong 153 arm
  would dispatch ovl20 from a non-ovl1c resident.
- **H-1ecc-restores-e9:** section-2 E9 match leaves the
  src0=0x000178 family (s762 was 6/64). Needs a new src0
  / rdpFs climb, not another 3–6 boot-DL copies. This
  landing is the ovl20-dispatch exit of the $6==0 chain,
  so a climb is more plausible than at 0x1EBC but still
  requires a non-0x000178 src.
- **H-1ecc-not-only:** 0x1ECC→0 and a new UJ sibling
  appears besides the known 0x1E7C (0x1E8C).

## Discriminating measurement

One build, one soak (s762 recipe; [CRASH] is a note).
First att of s762 died at 24 s cinematic before the UJ
window — if that recurs, re-run the same recipe; do not
chase. Same-run controls: clip `res=0x04`, ovl24
`res=0x24 tgt=0x12A0`, ovl20 `res=0x20 tgt=0x12A0`,
ovl1c `res=0x1C tgt=0x1EBC`, `dl06=`.

- UJ 0x1ECC → 0 + dest LIVE + dl06 2/2/0 + 0x1E7C leftover →
  H-1ecc-ovl1c-30ret. Next is 0x1E7C.
- dl06 breaks or dest dies → H-1ecc-breaks-06.
- E9 match gains a non-0x000178 src and rdpFs climbs →
  H-1ecc-restores-e9.
- UJ 0x1ECC stays nonzero → rewrite the case; 153 was not
  0x1C at the jr.

## Commands

    # fixup 6u: INSERT (no existing case) before
    #   case 0x1DB0:  /* fixup: clipsplice */
    # the same 6o/6t shape:
    #   case 0x1ECC: if (153==0x1C) route(0x1C,0x1ECC);
    #                goto OVL1C_1ECC; else clip-stray
    # Precondition: OVL1C_1ECC: already in the file (6k).
    # Do not add 0x1E7C / 0x1E8C this step.
    python3 tools/fixup_factor5_ucode.py \
      build/factor5_ucode/factor5_ucode_recompiled.c
    DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer \
      cmake --build build -j8 --target RogueSquadron64Recomp
    # soak: copy s762 recipe; require
    #   [ovl-route] res=0x20 tgt=0x12A0
    #   [ovl-route] res=0x24 tgt=0x12A0
    #   [ovl-route] res=0x1C tgt=0x1EBC
    #   [ovl-route] res=0x04
    #   dl06=
    # Discriminator is UJ 0x1ECC count, not clip-stray.
    # probe.sh rc=3 on crash — do not use set -e around it if
    # the control greps must still run. If the process dies
    # before VI 1024, re-run; do not chase the cinematic
    # SIGBUS (s762 att1, last-guest-pc=0x8000834c).

ORIGIN: OVL1C_1EBC jal 0x1ED4 at IMEM 0x1EBC, r31=0x1ECC.
OVL1C_1ED4 saves $ra → $30, jals 0x1F0C (return 0x1F04).
OVL1C_1F04 jr $30. Legitimate ovl1c $30-return into the
ovl20-dispatch exit (j L_1268; ori $5, 0x20). Route it.
