# NEXT work unit (ovl20 0x13B8 clip-hand return)

HYPOTHESIS-ID: m3-postsec2-lle-control-flow

s759 dest-0x12A0 / 153==0x20 route is LIVE (H-ovl20-route-runs).
UJ 0. Predicted 0x1E6C/20 leftover 0. Residual is
`[clip-stray] tgt=0x13B8 153=0x04` n=419 line=2852 — ovl20
`jal L_17F0` at IMEM 0x13B0 sets r31=0x13B8; L_17F0 hand
(r5=4; goto L_1268) stores 153=4; CLIP_1E48 jr's it. Same
class as s744/s745 0x1364. Do **not** widen every ovl20-only
case. Do **not** revert dest 0x12A0. Do **not** chase the
hangar leave SIGSEGV (sticky last-guest-pc 0x800ac8c0).

## Competing hypotheses

- **H-13b8-clip-hand:** widening case 0x13B8 to
  `153==0x20 || ==0x04` (still `goto OVL20_13B8`) drops the
  0x13B8/04 stray to 0; dest `res=0x20 tgt=0x12A0` stays LIVE;
  4/4 boot `dl06=2/2/0`; UJ stays 0.
- **H-13b8-breaks-06:** the 0x04 arm steals a main/ovl24
  0x13B8 site; boot dl06 unpaired or ovl24 dest dies.
- **H-13b8-restores-e9:** section-2 E9 match leaves the
  boot-shaped 3/64 triplet (refute of s758 static). Needs a
  crash-free soak that reaches outdoor, or remains
  unevaluable.
- **H-13b8-not-only:** 0x13B8/04 goes to 0 and a sibling
  ovl20 return leaks at 0x13C0/04 (jal L_112C) or another
  0x13xx/04 — then the next unit is that sibling, not a
  blanket ovl20-04ret.

## Discriminating measurement

One build, one soak (s759 recipe without the CRASH-fail, or
keep CRASH as a note not a wrapper-fail). Same-run controls:
clip `res=0x04`, ovl24 `res=0x24 tgt=0x12A0`, ovl20
`res=0x20 tgt=0x12A0`, ovl1c `res=0x1C tgt=0x1EA8`, `dl06=`.

- stray 0x13B8/04 → 0 + dest LIVE + dl06 2/2/0 →
  H-13b8-clip-hand. Predicted next leak is 0x13C0/04.
- dl06 breaks or ovl24 dest dies → H-13b8-breaks-06.
- E9 match rises off the boot-shaped triplet →
  H-13b8-restores-e9.
- 0x13B8/04 stays nonzero → rewrite the case; the 0x04 arm
  did not take.

## Commands

    # fixup 6r: only case 0x13B8, currently
    #   153==0x20 → OVL20_13B8 else stray
    # become
    #   153==0x20 || ==0x04 → OVL20_13B8 else stray
    # Do not touch 0x13C0 / 0x13D8 / 0x13F0 yet.
    # Do not steal ovl24 0x1364's 0x24||0x04 arm.
    python3 tools/fixup_factor5_ucode.py \
      build/factor5_ucode/factor5_ucode_recompiled.c
    DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer \
      cmake --build build -j8 --target RogueSquadron64Recomp
    # soak: copy s759 recipe; require
    #   [ovl-route] res=0x20 tgt=0x12A0
    #   [ovl-route] res=0x24 tgt=0x12A0
    #   [ovl-route] res=0x04
    #   dl06=
    # Treat [CRASH] as a note (s759 hangar leave), not the
    # dest-route discriminator.

ORIGIN: OVL20 jal L_17F0 at IMEM 0x13B0, r31=0x13B8.
L_17F0 hand is a legitimate ROM clip dispatch. Route the
return; do not skip L_17F0.
