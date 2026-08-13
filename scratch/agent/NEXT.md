# NEXT work unit (splice overlay 0x1C at dest 0x1DB0)

HYPOTHESIS-ID: m3-postsec2-lle-control-flow

s751 routed ovl10 handshake `153==0x10` at dest `0x1F40`: LIVE
(`[ovl-route] res=0x10 tgt=0x1F40` last n=7488;
`last_ovl=0x10/0x1F40` 61/64). Stray `0x1F40/10` → 0. New leftover
is `[clip-stray] tgt=0x1F40 153=0x00 line=1421` hits=3767
(`L_1778` `jr $30` of leftover `$30`). Pred first-edge all 61
`dest=0x1DB0,line:621,resident:0x1C` (ra=`0x16B8`). ovl10 exits
`j L_1268; ori $5, 0x1C` at IMEM `0x1FBC`. Overlay `0x1C` is ROM
`0x26EF8`, dest `0x1DB0`, table len `0x20B` → `0x20C` B, first
word `0x9228FFFA`, exit `j L_1268; ori $5, 0x20` at IMEM
`0x1ECC`. Has jals (`0x1ED4` / `0x1F0C`). Do **not** widen
`0x1F40` to `153==0`. Do **not** splice overlay `0x20` in this
unit. Do **not** name the toml/composite `ovl28` — that id is
already the `r17+=32` restore route.

Add overlay `0x1C` to `make_clip_composite.py` (accept `0x1C` /
28; output `scratch/s47_ovl1c_composite.z64`), add
`factor5_rsp_ovl1c.toml`, RSPRecomp, and a new fixup 6k that
extracts `L_1DB0..`, renames `OVL1C_*`, and routes
`153==0x1C` at dest `0x1DB0` only. Extra targets for the jal
returns if RSPRecomp needs them to emit labels; do not add
those cases until dest-`0x1DB0` is LIVE.

## Competing hypotheses

- **H-ovl1c-stops-1f40-00:** routing dest `0x1DB0` / `153==0x1C`
  to `OVL1C_1DB0` runs the skipped image. Pred `resident:0x1C`
  → 0. Stray `0x1F40/00` → 0. New residual is dest `0x1DB0`
  `153==0x20` and/or leftover jal-return `$ra`.
- **H-ovl1c-not-the-1f40-path:** route LIVE but stray
  `0x1F40/00` stays at the s751 hit count. Then another
  `jr $30` writer exists.
- **H-ovl1c-breaks-06:** dest-`0x1DB0` `153==0x1C` is also used
  by a boot/control path; routing it breaks `dl06=2/2/0`.
- **H-ovl1c-restores-e9:** completing ovl10's successor was the
  missing FULL_SYNC producer. E9 match rises above the
  boot-shaped triplet (s751 3/64). Unlikely but cheap.

## Discriminating measurement

One rebuild, one soak (same recipe as s743–s751). Batch:

- `[ovl-route] res=0x1C` must be LIVE (positive control; extend
  the host print filter if it still drops `0x1C`).
- stray `0x1F40/00` should drop vs s751 hits=3767.
- pred `resident:0x1C` 61 → 0.
- boot 4/4 `dl06=2/2/0`.
- E9 match / rdpFs vs s751 3/64 and 0→11238.
- new stray / last_ovl / UJ class (expect ovl-`0x20` and/or
  jal-return leftovers).
- CRASH=0 (s751 was clean).

Outcomes:

- route LIVE + stray 0x1F40/00 → 0 + pred 0x1C → 0 + dl06
  intact → H-ovl1c-stops-1f40-00 SELECTED; next is the new
  residual (likely ovl `0x20`).
- route LIVE + stray stays → H-ovl1c-not-the-1f40-path;
  re-open `L_1778` callers.
- dl06 breaks → H-ovl1c-breaks-06; revert the 0x1C arm of
  case 0x1DB0 only (keep the 0x1F40 handshake).
- E9 match rises above the boot-shaped triplet →
  H-ovl1c-restores-e9 (report, still record the stray outcome).

## Commands

    # add OVERLAYS[0x1C] = (0x26EF8, 0x20C, "ovl1c", WINDOW, END)
    python3 tools/make_clip_composite.py 0x1C
    # factor5_rsp_ovl1c.toml (do not call it ovl28)
    # RSPRecomp factor5_rsp_ovl1c.toml
    # fixup 6k: require L_1DB0; route 153==0x1C at dest 0x1DB0
    cmake --build build -j8
    # soak: copy s751 recipe, add res=0x1C grep, SIGKILL, 348s class

ORIGIN: dest `0x1DB0` / `153==0x1C` is the skipped ovl1c image
(ROM `0x26EF8`). The `0x1F40/00` stray is leftover `$30` after
that skip falls into main `L_1DB0`. Route, not a `0x1F40` widen
to `153==0`.
