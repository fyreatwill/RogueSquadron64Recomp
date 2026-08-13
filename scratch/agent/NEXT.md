# NEXT work unit (route ovl1c jal-return 0x1F04)

HYPOTHESIS-ID: m3-postsec2-lle-control-flow

s754 routed dest `0x1E2C` / `153==0x1C` → `OVL1C_1E2C`: LIVE
(`[ovl-route] res=0x1C tgt=0x1E2C` last n=53440; UJ `0x1E2C`
3213→0). New residual is `Unhandled jump target 0x1F04`
n=3185 from `OVL1C_1F9C` `jr $ra` (line 5114). `OVL1C_1ED4`
saves `$ra` into `$30` then jals callee `0x1F0C` with
`r31=0x1F04`. Label `OVL1C_1F04` already exists; there is
no `case 0x1F04`. The predicted leftover `0x1E6C` is a
`$30` restore *after* `OVL1C_1F04` `jr $30` — UJ
`0x1E6C`/`0x1E7C`/`0x1E8C`/`0x1EA8`/`0x1EBC`/`0x1ECC`
are all 0 until `0x1F04` is routed. Do **not** splice
overlay `0x20` (dest is `0x12A0`). Do **not** add those
`$30`-return cases until `0x1F04` is LIVE. Do **not**
name anything ovl28.

Add fixup 6n (own marker) that routes dest `0x1F04` when
`153==0x1C` to `OVL1C_1F04`. No rebuild of the composite
or RSPRecomp unless the label is missing.

## Competing hypotheses

- **H-1f04-ovl1c-jalret:** case `0x1F04` / `153==0x1C` →
  `OVL1C_1F04` is the missing 1ED4 trampoline return. UJ
  `0x1F04` → 0. New residual is a `$30` restore leftover
  (`0x1E6C` first: `OVL1C_1ED4` callers set `r31` to
  `0x1E6C`/`0x1E7C`/… before the trampoline).
- **H-1f04-not-the-uj-path:** route LIVE but UJ `0x1F04`
  stays. Then another `jr $ra` writer exists.
- **H-1f04-breaks-06:** dest `0x1F04` is also used by a
  boot/control path; routing it breaks `dl06=2/2/0`.
- **H-1f04-restores-e9:** completing this trampoline return
  was the missing FULL_SYNC producer. E9 match rises above
  the boot-shaped triplet. Unlikely but cheap.

## Discriminating measurement

One rebuild, one soak (same recipe as s743–s754). Batch:

- `[ovl-route] res=0x1C tgt=0x1F04` must be LIVE.
- UJ `0x1F04` should drop vs s754 n=3185.
- boot 4/4 `dl06=2/2/0`.
- E9 match / rdpFs vs s754 boot-shaped 9/192 and 0→5150.
- new stray / last_ovl / UJ class (expect a `$30` return
  such as `0x1E6C`, from `OVL1C_1F04` `jr $30`).
- CRASH=0.

Outcomes:

- route LIVE + UJ 0x1F04 → 0 + dl06 intact →
  H-1f04-ovl1c-jalret SELECTED; next is the new residual.
- route LIVE + UJ stays → H-1f04-not-the-uj-path;
  re-open `OVL1C_1F9C` `jr $ra` writers.
- dl06 breaks → H-1f04-breaks-06; revert the 0x1F04 case
  only (keep dest-0x1E2C / 153==0x1C).
- E9 match rises above the boot-shaped triplet →
  H-1f04-restores-e9 (report, still record the UJ outcome).

## Commands

    # no composite/RSPRecomp unless OVL1C_1F04 is missing
    # fixup 6n: case 0x1F04 if 153==0x1C goto OVL1C_1F04
    cmake --build build -j8
    # soak: copy s754 recipe, grep res=0x1C tgt=0x1F04, SIGKILL, 348s class

ORIGIN: ovl1c `OVL1C_1ED4` saves `$ra` to `$30`, jals
`0x1F0C` with return `0x1F04`. `OVL1C_1F9C` `jr $ra` is
the legitimate return into `OVL1C_1F04`, which then
`jr $30` to the original caller. Route, not a default-allow
of `0x1F04` for every resident.
