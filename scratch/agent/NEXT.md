# NEXT work unit (route overlay 14 at dest 0x1DB0)

HYPOTHESIS-ID: m3-postsec2-lle-control-flow

s747 selected H-1df4-stale-ra: the `[clip-stray] 0x1DF4/00` n=3157
is leftover `$ra` from `OVL12_1DD8` `jal L_122C` after skipped
ovl14 DMA falls through to main `L_1DB0`, which stores `153=0` and
`j L_11B0`. Table: `docs/M3-1DF4-PROVENANCE-AUDIT.md`. Do **not**
widen case `0x1DF4` to `==0`. Do **not** enable IMEM DMA.

Route overlay 14 the same way 6b/6c routed ovl12/ovl24: extract the
ROM image into the `0x1DB0` window, RSPRecomp, fixup-rename
`OVL14_*`, case `0x1DB0` when `153==0x14` (plus the three in-overlay
jal-returns `0x1E28`/`0x1E94`/`0x1EEC` if the translator emits
them as `do_indirect_jump`). ovl14 ROM `0x26AB8` len `0x21F`, dest
`0x1DB0`, exit `j L_1268; ori $5, 0x18`. ovl18 is the successor
residual — do not splice it in this unit.

## Competing hypotheses

- **H-ovl14-stops-1df4-stray:** routing `153==0x14` at dest `0x1DB0`
  runs ovl14 instead of main `L_1DB0`, so `153` stays `0x14` and
  `L_11B0` never jrs leftover `0x1DF4`. Stray `0x1DF4/00` → 0.
  New residual is the ovl18 miss (`153==0x18` at dest `0x1DB0`)
  or an ovl14 jal-return stray.
- **H-ovl14-not-the-1df4-path:** ovl14 route is LIVE but
  `0x1DF4/00` line=451 stays. Then the leftover-`$ra` story is
  incomplete (another `L_11B0` entry).
- **H-ovl14-breaks-06:** dest-`0x1DB0` `153==0x14` is also used
  by a boot/control path; routing it breaks `dl06=2/2/0`.
- **H-ovl14-restores-e9:** ovl14 was the missing FULL_SYNC
  producer. E9 match rises above 3/64. Unlikely (ovl14 is a
  vector loop, not emit) but cheap to read off the same soak.

## Discriminating measurement

One rebuild, one soak (same recipe as s743–s746). Batch:

- `[ovl-route] res=0x14` must be LIVE (positive control).
- `[clip-stray] tgt=0x1DF4 153=0x00` n vs s746 3157.
- boot 4/4 `dl06=2/2/0`.
- sec2 first-edge reset-predecessor `resident:0x14` should drop
  (those jr `0x1DB0` now route, so they never enter `L_1DB0`).
- E9 match / rdpFs vs s746 3/64 and 0→4117.
- new stray / UJ class (expect ovl18 or ovl14 jal-return).

Outcomes:

- route LIVE + stray 1DF4→0 + dl06 intact → H-ovl14-stops-1df4-stray
  SELECTED; next is the new residual (likely ovl18).
- route LIVE + stray 1DF4 stays → H-ovl14-not-the-1df4-path; do
  not keep iterating ovl14, re-open `L_11B0` callers.
- dl06 breaks → H-ovl14-breaks-06; revert the 0x1DB0 arm.
- E9 match rises → H-ovl14-restores-e9 (report, still record
  the stray outcome).

## Commands

    python3 tools/make_clip_composite.py 14   # add id 14 first
    # RSPRecomp factor5_rsp_ovl14.toml → build/factor5_ucode/factor5_ucode_ovl14_recompiled.c
    # fixup 6g in tools/fixup_factor5_ucode.py (route 153==0x14 at 0x1DB0)
    cmake --build build -j8
    # soak: copy s746 recipe, same env, SIGKILL, 348s class

ORIGIN: dest 0x1DB0 / 153==0x14 is the skipped ovl14 image
(ROM 0x26AB8). The 0x1DF4 stray is leftover $ra after that skip
falls into L_1DB0. Route, not a 0x1DF4 widen.
