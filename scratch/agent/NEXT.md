# NEXT work unit (ovl20 0x13C0 jal-L_112C return)

HYPOTHESIS-ID: m3-postsec2-lle-control-flow

s760 0x13B8 clip-hand widen is LIVE (H-13b8-clip-hand).
Stray 0x13B8/04 419→0. Dest 0x12A0/20 stays LIVE. Residual is
`[clip-stray] tgt=0x13C0 153=0x04` n=643 line=400 — OVL20_13B8
jal L_112C sets r31=0x13C0; L_112C copies r31→r30; L_11A0
jr $30. Same class as s745/s760. Do **not** widen 0x13D8 /
0x13F0 yet (0x13C0 is a restore-regs then j OVL20_133C, not
those labels). Do **not** route UJ 0x1EBC/0x1E7C this step
(OVL1C_1F04 jr $30; first UJ is before sec2). Do **not**
revert dest 0x12A0. Do **not** chase the 250 s SIGBUS
(calculateDatItemDistanceToPlayer / last-guest-pc 0x8000834c).

## Competing hypotheses

- **H-13c0-jal-112c:** widening case 0x13C0 to
  `153==0x20 || ==0x04` (still `goto OVL20_13C0`) drops the
  0x13C0/04 stray to 0; dest `res=0x20 tgt=0x12A0` stays LIVE;
  4/4 boot `dl06=2/2/0`; 0x13B8/04 stays 0.
- **H-13c0-breaks-06:** the 0x04 arm steals a main/ovl24
  0x13C0 site; boot dl06 unpaired or ovl24 dest dies.
- **H-13c0-restores-e9:** section-2 E9 match leaves the
  src0=0x000178 family (s760 was 6/64, still that src). Needs
  a new src0 / rdpFs climb, not another 3–6 boot-DL copies.
- **H-13c0-not-only:** 0x13C0/04 goes to 0 and a sibling
  ovl20 return leaks (0x13D8/04, 0x13F0/04, or a 0x133C-window
  label) — then that sibling, not a blanket ovl20-04ret.

## Discriminating measurement

One build, one soak (s760 recipe; [CRASH] is a note). Same-run
controls: clip `res=0x04`, ovl24 `res=0x24 tgt=0x12A0`, ovl20
`res=0x20 tgt=0x12A0`, ovl1c `res=0x1C tgt=0x1EA8`, `dl06=`.

- stray 0x13C0/04 → 0 + dest LIVE + dl06 2/2/0 →
  H-13c0-jal-112c. Predicted next leak is whatever OVL20_133C
  jals with 153 still 0x04, or 0x13D8/0x13F0.
- dl06 breaks or ovl24 dest dies → H-13c0-breaks-06.
- E9 match gains a non-0x000178 src and rdpFs climbs →
  H-13c0-restores-e9.
- 0x13C0/04 stays nonzero → rewrite the case; the 0x04 arm
  did not take.

## Commands

    # fixup 6s: only case 0x13C0, currently
    #   153==0x20 → OVL20_13C0 else stray
    # become
    #   153==0x20 || ==0x04 → OVL20_13C0 else stray
    # Do not touch 0x13D8 / 0x13F0 / 0x133C yet.
    # Do not steal ovl24 0x1364's 0x24||0x04 arm.
    python3 tools/fixup_factor5_ucode.py \
      build/factor5_ucode/factor5_ucode_recompiled.c
    DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer \
      cmake --build build -j8 --target RogueSquadron64Recomp
    # soak: copy s760 recipe; require
    #   [ovl-route] res=0x20 tgt=0x12A0
    #   [ovl-route] res=0x24 tgt=0x12A0
    #   [ovl-route] res=0x04
    #   dl06=
    # Treat [CRASH] as a note, not the dest-route discriminator.
    # probe.sh rc=3 on crash — do not use set -e around it if
    # the control greps must still run.

ORIGIN: OVL20_13B8 jal L_112C at IMEM 0x13B8, r31=0x13C0.
L_112C copies r31→r30; L_11A0 jr $30. Legitimate ROM clip
continuation; route the return.
