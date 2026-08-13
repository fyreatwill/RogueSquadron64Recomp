# NEXT work unit (route ovl1c $30-return 0x1E6C)

HYPOTHESIS-ID: m3-postsec2-lle-control-flow

s755 routed dest `0x1F04` / `153==0x1C` → `OVL1C_1F04`: LIVE
(`[ovl-route] res=0x1C tgt=0x1F04` last n=55232; UJ `0x1F04`
3185→0). New residual is `OVL1C_1F04` `jr $30` (line 4987):
`Unhandled jump target 0x1EA8` n=1609 and `0x1E6C` n=1570.
Label `OVL1C_1E6C` already exists; there is no `case 0x1E6C`.
The other predicted `$30` landings (`0x1E7C`/`0x1E8C`/
`0x1EBC`/`0x1ECC`) are 0 — those jals sit on `$6==0` arms
that this soak did not take. Do **not** splice overlay
`0x20` (dest is `0x12A0`). Do **not** name anything ovl28.
Route `0x1E6C` first; `0x1EA8` is the sibling leftover
and should remain until its own case.

Add fixup 6o (own marker) that routes dest `0x1E6C` when
`153==0x1C` to `OVL1C_1E6C`. No rebuild of the composite
or RSPRecomp unless the label is missing.

## Competing hypotheses

- **H-1e6c-ovl1c-30ret:** case `0x1E6C` / `153==0x1C` →
  `OVL1C_1E6C` is the missing `$30` restore from the
  `jal 0x1ED4` that sets `r31=0x1E6C`. UJ `0x1E6C` → 0.
  Sibling UJ `0x1EA8` stays (different jal, same `jr $30`).
- **H-1e6c-not-the-uj-path:** route LIVE but UJ `0x1E6C`
  stays. Then another writer of jump_target `0x1E6C` exists.
- **H-1e6c-breaks-06:** dest `0x1E6C` is also used by a
  boot/control path; routing it breaks `dl06=2/2/0`.
- **H-1e6c-restores-e9:** completing this `$30` restore
  was the missing FULL_SYNC producer. E9 match rises above
  the boot-shaped triplet. Unlikely but cheap.

## Discriminating measurement

One rebuild, one soak (same recipe as s743–s755). Batch:

- `[ovl-route] res=0x1C tgt=0x1E6C` must be LIVE.
- UJ `0x1E6C` should drop vs s755 n=1570.
- UJ `0x1EA8` should stay near s755 n=1609 (sibling).
- boot 4/4 `dl06=2/2/0`.
- E9 match / rdpFs vs s755 boot-shaped 9/192 and 0→5167.
- new stray / last_ovl / UJ class.
- CRASH=0.

Outcomes:

- route LIVE + UJ 0x1E6C → 0 + 0x1EA8 stays + dl06 intact →
  H-1e6c-ovl1c-30ret SELECTED; next is case `0x1EA8`.
- route LIVE + UJ 0x1E6C stays → H-1e6c-not-the-uj-path;
  re-open `OVL1C_1F04` `jr $30` writers.
- dl06 breaks → H-1e6c-breaks-06; revert the 0x1E6C case
  only (keep dest-0x1F04 / 153==0x1C).
- E9 match rises above the boot-shaped triplet →
  H-1e6c-restores-e9 (report, still record the UJ outcome).

## Commands

    # no composite/RSPRecomp unless OVL1C_1E6C is missing
    # fixup 6o: case 0x1E6C if 153==0x1C goto OVL1C_1E6C
    cmake --build build -j8
    # soak: copy s755 recipe, grep res=0x1C tgt=0x1E6C, SIGKILL, 348s class

ORIGIN: ovl1c jal at IMEM `0x1E60` sets `r31=0x1E6C` and
`goto OVL1C_1ED4`. The trampoline saves that into `$30`,
returns through `OVL1C_1F04`, then `jr $30`. `OVL1C_1F04`
`jr $30` is the legitimate return into `OVL1C_1E6C`.
Route, not a default-allow of `0x1E6C` for every resident.
