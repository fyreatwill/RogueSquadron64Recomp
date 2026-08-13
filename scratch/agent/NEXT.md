# NEXT work unit (route ovl10 L_15D0 handshake return at 0x1F40)

HYPOTHESIS-ID: m3-postsec2-lle-control-flow

s750 routed ovl10 dest `0x1DB0` / `153==0x10`: LIVE
(`[ovl-route] res=0x10` last n=5440; `last_ovl=0x10/0x1DB0`
122/128). Leftover-`$ra` `/00` `L_11B0` strays → 0. New stray
is `[clip-stray] tgt=0x1F40 153=0x10 line=1421` n=5501.
Line 1421 is `L_1778` `jr $30`, not `L_11B0`. ovl10 at IMEM
`0x1F38` is `j L_15D0; ori $30, $zero, 0x1F40`; `0x1F40` is
`lhu $10, 0x56($18)`. Do **not** widen `0x1F40` to `OVL18_*`.
Do **not** splice overlay `0x1C` in this unit. Do **not**
enable IMEM DMA.

Add `0x1F40` to `factor5_rsp_ovl10.toml` extra targets,
re-RSPRecomp, teach fixup 6i to require `L_1F40`, and widen
case `0x1F40` to `153==0x18 → OVL18_1F40` **or**
`153==0x10 → OVL10_1F40`.

## Competing hypotheses

- **H-1f40-ovl10-handshake:** routing `153==0x10` at dest
  `0x1F40` to `OVL10_1F40` runs the post-`L_15D0` body.
  Stray `0x1F40/10` → 0. New residual is dest `0x1DB0`
  `153==0x1C` (ovl10's `ori $5, 0x1C` exit) and/or a new
  leftover class.
- **H-1f40-not-the-handshake:** route LIVE but stray
  `0x1F40/10` stays at the s750 count. Then another `jr $30`
  writer exists.
- **H-1f40-breaks-06:** dest-`0x1F40` `153==0x10` is also
  used by a boot/control path; routing it breaks `dl06=2/2/0`.
- **H-1f40-restores-e9:** completing the ovl10 handshake was
  the missing FULL_SYNC producer. E9 match rises above the
  boot-shaped triplet rate (s750 6/128). Unlikely but cheap.

## Discriminating measurement

One rebuild, one soak (same recipe as s743–s750). Batch:

- `[ovl-route] res=0x10` must be LIVE and include `tgt=0x1F40`
  (positive control).
- stray `0x1F40/10` should drop vs s750 n=5501.
- boot 4/4 `dl06=2/2/0`.
- E9 match / rdpFs vs s750 6/128 and 0→5169.
- new stray / last_ovl / UJ class (expect ovl-0x1C).
- CRASH=0 vs s750's late SIGSEGV (report; do not treat a
  still-crashing run as H-1f40-breaks-06 unless dl06 breaks).

Outcomes:

- route LIVE + stray 0x1F40/10 → 0 + dl06 intact →
  H-1f40-ovl10-handshake SELECTED; next is the new residual
  (likely ovl 0x1C).
- route LIVE + stray stays → H-1f40-not-the-handshake;
  re-open `L_1778` callers.
- dl06 breaks → H-1f40-breaks-06; revert the 0x10 arm of
  case 0x1F40 only (keep dest 0x1DB0).
- E9 match rises above the boot-shaped triplet →
  H-1f40-restores-e9 (report, still record the stray outcome).

## Commands

    python3 tools/make_clip_composite.py 16
    # add 0x1F40 to factor5_rsp_ovl10.toml extra_indirect_branch_targets
    # RSPRecomp factor5_rsp_ovl10.toml
    # fixup 6i: require L_1F40; widen case 0x1F40 to 0x18||0x10
    cmake --build build -j8
    # soak: copy s750 recipe, same env, SIGKILL, 348s class

ORIGIN: ovl10 `ori $30, 0x1F40; j L_15D0` at IMEM `0x1F38`.
`L_1778` `jr $30` returns into ovl10 at `0x1F40`
(`lhu $10, 0x56($18)`). Legitimate ROM handshake, same family
as ovl24's `ori $30, 0x12AC`. Route to `OVL10_1F40`, not
`OVL18_1F40`.
