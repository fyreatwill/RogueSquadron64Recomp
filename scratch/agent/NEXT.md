# NEXT work unit (route overlay 18 at dest 0x1DB0)

HYPOTHESIS-ID: m3-postsec2-lle-control-flow

s748 routed ovl14: dest `0x1DB0` / `153==0x14` is LIVE
(`last_ovl=0x14/*` 61/64). Pred `resident:0x14` → 0; all 61 first-edge
preds are now `dest=0x1DB0,line:621,resident:0x18`. Residual leftover-
`$ra` strays at `L_11B0` line=451: `0x1DF4/00=1395` (ovl14 no-jal),
`0x1E28/00=1200`, `0x1EEC/00=77`. Do **not** widen those to `==0`.
Do **not** enable IMEM DMA.

Route overlay 18 the same way 6g routed ovl14: extract the ROM image
into the `0x1DB0` window, RSPRecomp, fixup-rename `OVL18_*`, case
`0x1DB0` when `153==0x18` (plus in-overlay jal-returns `0x1EEC` /
`0x1F40` if the translator emits them as `do_indirect_jump`). ovl18
ROM `0x26CD8` len `0x21F`, dest `0x1DB0`, exit `j L_1268; ori $5, 0x10`.
`0x1EEC` is already an ovl14-only case — widen to `0x14||0x18`, do not
overwrite. Overlay `0x10` is the successor residual — do not splice it
in this unit. `[ovl-route]` now prints 0x14/0x18 (s748 host fix).

## Competing hypotheses

- **H-ovl18-stops-1db0-reset:** routing `153==0x18` at dest `0x1DB0`
  runs ovl18 instead of main `L_1DB0`. Pred `resident:0x18` → 0.
  Leftover-`$ra` strays (1DF4/1E28/1EEC /00) → 0 or become the ovl18
  jal-return / ovl-0x10 skip class. New residual is dest `0x1DB0`
  `153==0x10` or an ovl18 jal-return stray.
- **H-ovl18-not-the-l11b0-path:** ovl18 route is LIVE but line-451
  leftover-`$ra` strays stay at the s748 counts. Then another
  `L_11B0` entry exists.
- **H-ovl18-breaks-06:** dest-`0x1DB0` `153==0x18` is also used by a
  boot/control path; routing it breaks `dl06=2/2/0`.
- **H-ovl18-restores-e9:** ovl18 was the missing FULL_SYNC producer.
  E9 match rises above 3/64. Unlikely but cheap to read off the same
  soak.

## Discriminating measurement

One rebuild, one soak (same recipe as s743–s748). Batch:

- `[ovl-route] res=0x14` and `res=0x18` must be LIVE (positive
  control; 0x14/0x18 now print). Also `last_ovl=0x18/*` on sec2 reset.
- sec2 first-edge pred `resident:0x18` should drop (those jr `0x1DB0`
  now route).
- leftover-`$ra` stray n: `0x1DF4/00` + `0x1E28/00` + `0x1EEC/00`
  vs s748 1395+1200+77.
- boot 4/4 `dl06=2/2/0`.
- E9 match / rdpFs vs s748 3/64 and 0→8092.
- new stray / UJ class (expect ovl-0x10 or ovl18 jal-return).

Outcomes:

- route LIVE + pred 0x18→0 + dl06 intact → H-ovl18-stops-1db0-reset
  SELECTED; next is the new residual (likely ovl 0x10).
- route LIVE + line-451 stray counts stay → H-ovl18-not-the-l11b0-path;
  do not keep iterating ovl18, re-open `L_11B0` callers.
- dl06 breaks → H-ovl18-breaks-06; revert the 0x18 arm.
- E9 match rises → H-ovl18-restores-e9 (report, still record
  the stray/pred outcome).

## Commands

    python3 tools/make_clip_composite.py 18   # add id 18 first
    # RSPRecomp factor5_rsp_ovl18.toml → build/factor5_ucode/factor5_ucode_ovl18_recompiled.c
    # fixup 6h in tools/fixup_factor5_ucode.py (route 153==0x18 at 0x1DB0)
    cmake --build build -j8
    # soak: copy s748 recipe, same env, SIGKILL, 348s class

ORIGIN: dest 0x1DB0 / 153==0x18 is the skipped ovl18 image
(ROM 0x26CD8). The leftover-$ra L_11B0 strays are after that skip
falls into L_1DB0. Route, not a 0x1DF4/0x1E28 widen.
