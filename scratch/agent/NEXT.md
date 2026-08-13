# NEXT work unit (route ovl1c $30-return 0x1EA8)

HYPOTHESIS-ID: m3-postsec2-lle-control-flow

s756 routed dest `0x1E6C` / `153==0x1C` → `OVL1C_1E6C`: LIVE
(`[ovl-route] res=0x1C tgt=0x1E6C` last n=7744; UJ `0x1E6C`
1570→0). Sibling leftover is `Unhandled jump target 0x1EA8`
n=1403 from `OVL1C_1F04` `jr $30` (line 4987). Label
`OVL1C_1EA8` already exists; there is no `case 0x1EA8`.
The other predicted `$30` landings (`0x1E7C`/`0x1E8C`/
`0x1EBC`/`0x1ECC`) stayed 0. Do **not** splice overlay
`0x20` (dest is `0x12A0`). Do **not** widen `0x1E6C` to
`153==0x20` (s756 had only 2 stray hits).

Add fixup 6p (own marker) that routes dest `0x1EA8` when
`153==0x1C` to `OVL1C_1EA8`. No rebuild of the composite
or RSPRecomp unless the label is missing.

## Competing hypotheses

- **H-1ea8-ovl1c-30ret:** case `0x1EA8` / `153==0x1C` →
  `OVL1C_1EA8` is the missing `$30` restore from the
  `jal 0x1ED4` that sets `r31=0x1EA8`. UJ `0x1EA8` → 0.
- **H-1ea8-not-the-uj-path:** route LIVE but UJ `0x1EA8`
  stays. Then another writer of jump_target `0x1EA8` exists.
- **H-1ea8-breaks-06:** dest `0x1EA8` is also used by a
  boot/control path; routing it breaks `dl06=2/2/0`.
- **H-1ea8-restores-e9:** completing this `$30` restore
  was the missing FULL_SYNC producer. E9 match rises above
  the boot-shaped triplet. Unlikely but cheap.

## Discriminating measurement

One rebuild, one soak (same recipe as s743–s756). Batch:

- `[ovl-route] res=0x1C tgt=0x1EA8` must be LIVE.
- UJ `0x1EA8` should drop vs s756 n=1403.
- boot 4/4 `dl06=2/2/0`.
- E9 match / rdpFs vs s756 boot-shaped 3/64 and 0→4017.
- new stray / last_ovl / UJ class.
- CRASH=0.

Outcomes:

- route LIVE + UJ 0x1EA8 → 0 + dl06 intact →
  H-1ea8-ovl1c-30ret SELECTED; ovl1c LIVE `$30` pair is
  complete. Next is whatever new residual appears (do not
  splice overlay `0x20`; do not add the `$6==0` landings
  until they fire).
- route LIVE + UJ 0x1EA8 stays → H-1ea8-not-the-uj-path;
  re-open `OVL1C_1F04` `jr $30` writers.
- dl06 breaks → H-1ea8-breaks-06; revert the 0x1EA8 case
  only (keep dest-0x1E6C / 153==0x1C).
- E9 match rises above the boot-shaped triplet →
  H-1ea8-restores-e9 (report, still record the UJ outcome).

## Commands

    # no composite/RSPRecomp unless OVL1C_1EA8 is missing
    # fixup 6p: case 0x1EA8 if 153==0x1C goto OVL1C_1EA8
    cmake --build build -j8
    # soak: copy s756 recipe, grep res=0x1C tgt=0x1EA8, SIGKILL, 348s class

ORIGIN: ovl1c jal at IMEM `0x1E9C` sets `r31=0x1EA8` and
`goto OVL1C_1ED4`. The trampoline saves that into `$30`,
returns through `OVL1C_1F04`, then `jr $30`. `OVL1C_1F04`
`jr $30` is the legitimate return into `OVL1C_1EA8`.
Route, not a default-allow of `0x1EA8` for every resident.
