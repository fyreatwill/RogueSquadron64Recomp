# NEXT work unit (route ovl1c jal-return 0x1E18)

HYPOTHESIS-ID: m3-postsec2-lle-control-flow

s752 spliced overlay `0x1C` at dest `0x1DB0`: LIVE
(`[ovl-route] res=0x1C tgt=0x1DB0` last n=5888;
`last_ovl=0x1C/0x1DB0` 183/192). Stray `0x1F40/00` → 0.
Pred-tag 122→0. New residual is `Unhandled jump target
0x1E18` n=5879 from `OVL1C_1F9C` `jr $ra` (line 5114).
ovl1c jal at IMEM `0x1E10` targets callee `0x1F0C` and
returns to `0x1E18`. Label `OVL1C_1E18` already exists
(fixup 6k extra target); there is no `case 0x1E18`.
Do **not** splice overlay `0x20` in this unit (dest is
`0x12A0`, table `0x2157`). Do **not** add the other
jal-return cases (`0x1E2C`/`0x1E6C`/`0x1E7C`/`0x1E8C`/
`0x1EA8`/`0x1EBC`/`0x1ECC`/`0x1F04`) until `0x1E18` is
LIVE. Do **not** name anything ovl28.

Add fixup 6l (own marker) that routes dest `0x1E18` when
`153==0x1C` to `OVL1C_1E18`. No rebuild of the composite
or RSPRecomp unless the label is missing.

## Competing hypotheses

- **H-1e18-ovl1c-jalret:** case `0x1E18` / `153==0x1C` →
  `OVL1C_1E18` is the missing jal return. UJ `0x1E18` → 0.
  New residual is another ovl1c jal-return leftover and/or
  dest `0x12A0` / `153==0x20`.
- **H-1e18-not-the-uj-path:** route LIVE but UJ `0x1E18`
  stays. Then another `jr $ra` writer exists.
- **H-1e18-breaks-06:** dest `0x1E18` is also used by a
  boot/control path; routing it breaks `dl06=2/2/0`.
- **H-1e18-restores-e9:** completing this jal return was
  the missing FULL_SYNC producer. E9 match rises above the
  boot-shaped triplet. Unlikely but cheap.

## Discriminating measurement

One rebuild, one soak (same recipe as s743–s752). Batch:

- `[ovl-route] res=0x1C tgt=0x1E18` must be LIVE.
- UJ `0x1E18` should drop vs s752 n=5879 (s751 was 0).
- boot 4/4 `dl06=2/2/0`.
- E9 match / rdpFs vs s752 boot-shaped 9/54 and 0→5203.
- new stray / last_ovl / UJ class (expect another jal-
  return: `0x1E2C` / `0x1E6C` / …).
- CRASH=0.

Outcomes:

- route LIVE + UJ 0x1E18 → 0 + dl06 intact →
  H-1e18-ovl1c-jalret SELECTED; next is the new residual.
- route LIVE + UJ stays → H-1e18-not-the-uj-path;
  re-open `OVL1C_1F9C` `jr $ra` writers.
- dl06 breaks → H-1e18-breaks-06; revert the 0x1E18 case
  only (keep dest-0x1DB0 / 153==0x1C).
- E9 match rises above the boot-shaped triplet →
  H-1e18-restores-e9 (report, still record the UJ outcome).

## Commands

    # no composite/RSPRecomp unless OVL1C_1E18 is missing
    # fixup 6l: case 0x1E18 if 153==0x1C goto OVL1C_1E18
    cmake --build build -j8
    # soak: copy s752 recipe, grep res=0x1C tgt=0x1E18, SIGKILL, 348s class

ORIGIN: ovl1c jal at IMEM `0x1E10` → callee `0x1F0C`,
return `0x1E18`. `OVL1C_1F9C` `jr $ra` is the legitimate
return into `OVL1C_1E18`. Route, not a default-allow of
`0x1E18` for every resident.
