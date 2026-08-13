# NEXT work unit (route overlay 0x10 at dest 0x1DB0)

HYPOTHESIS-ID: m3-postsec2-lle-control-flow

s749 routed ovl18: dest `0x1DB0` / `153==0x18` is LIVE
(`[ovl-route] res=0x18` last n=6848; `last_ovl=0x18/*` 183/192).
Pred `resident:0x18` → 0; all 183 first-edge preds are now
`dest=0x1DB0,line:621,resident:0x10`. Leftover-`$ra` strays at
`L_11B0` line=451: `0x1DF4/00=2619`, `0x1E28/00=2345`,
`0x1F40/00=901`, `0x1EEC/00=56`. Do **not** widen those to `==0`.
Do **not** enable IMEM DMA.

Route overlay 0x10 the same way 6h routed ovl18: extract the ROM
image into the `0x1DB0` window, RSPRecomp, fixup-rename `OVL10_*`,
case `0x1DB0` when `153==0x10`. ovl10 ROM `0x268A0` table len
`0x213` → `0x214` B, dest `0x1DB0`, first word `9626000C`
(`lhu $6, 12($17)`), **no jals**, exit `j L_1268; ori $5, 0x1C`
at IMEM `0x1FBC`. Overlay `0x1C` is the successor residual — do
not splice it in this unit. `[ovl-route]` already prints 0x14/0x18;
add 0x10 to the host filter if it is still silent.

## Competing hypotheses

- **H-ovl10-stops-1db0-reset:** routing `153==0x10` at dest `0x1DB0`
  runs ovl10 instead of main `L_1DB0`. Pred `resident:0x10` → 0.
  Leftover-`$ra` strays (1DF4/1E28/1F40/1EEC /00) → 0 or become
  the ovl-0x1C skip class. New residual is dest `0x1DB0`
  `153==0x1C`.
- **H-ovl10-not-the-l11b0-path:** ovl10 route is LIVE but line-451
  leftover-`$ra` strays stay at the s749 counts. Then another
  `L_11B0` entry exists.
- **H-ovl10-breaks-06:** dest-`0x1DB0` `153==0x10` is also used by
  a boot/control path; routing it breaks `dl06=2/2/0`.
- **H-ovl10-restores-e9:** ovl10 was the missing FULL_SYNC producer.
  E9 match rises above the boot-shaped triplet rate (s749 9/192 =
  three copies of s748's 3/64). Unlikely but cheap to read off
  the same soak.

## Discriminating measurement

One rebuild, one soak (same recipe as s743–s749). Batch:

- `[ovl-route] res=0x18` and `res=0x10` must be LIVE (positive
  control). Also `last_ovl=0x10/*` on sec2 reset.
- sec2 first-edge pred `resident:0x10` should drop (those jr
  `0x1DB0` now route).
- leftover-`$ra` stray n: `0x1DF4/00` + `0x1E28/00` + `0x1F40/00`
  + `0x1EEC/00` vs s749 2619+2345+901+56.
- boot 4/4 `dl06=2/2/0`.
- E9 match / rdpFs vs s749 9/192 (boot-shaped triplet) and
  0→5120.
- new stray / UJ class (expect ovl-0x1C).

Outcomes:

- route LIVE + pred 0x10→0 + dl06 intact → H-ovl10-stops-1db0-reset
  SELECTED; next is the new residual (likely ovl 0x1C).
- route LIVE + line-451 stray counts stay → H-ovl10-not-the-l11b0-path;
  do not keep iterating ovl10, re-open `L_11B0` callers.
- dl06 breaks → H-ovl10-breaks-06; revert the 0x10 arm.
- E9 match rises above the boot-shaped triplet → H-ovl10-restores-e9
  (report, still record the stray/pred outcome).

## Commands

    python3 tools/make_clip_composite.py 16   # id is 0x10 = 16
    # RSPRecomp factor5_rsp_ovl10.toml → build/factor5_ucode/factor5_ucode_ovl10_recompiled.c
    # fixup 6i in tools/fixup_factor5_ucode.py (route 153==0x10 at 0x1DB0)
    cmake --build build -j8
    # soak: copy s749 recipe, same env, SIGKILL, 348s class

ORIGIN: dest 0x1DB0 / 153==0x10 is the skipped ovl10 image
(ROM 0x268A0). The leftover-$ra L_11B0 strays are after that skip
falls into L_1DB0. Route, not a 0x1DF4/0x1E28/0x1F40 widen.
