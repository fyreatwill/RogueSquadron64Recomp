# NEXT work unit (route ovl1c jal-return 0x1E2C)

HYPOTHESIS-ID: m3-postsec2-lle-control-flow

s753 routed dest `0x1E18` / `153==0x1C` → `OVL1C_1E18`: LIVE
(`[ovl-route] res=0x1C tgt=0x1E18` last n=6464; UJ `0x1E18`
5879→0). New residual is `Unhandled jump target 0x1E2C`
n=3213 from `OVL1C_1F9C` `jr $ra` (line 5113). After the
0x1E18 return, `OVL1C_1E18` jals callee `0x1F0C` with
`r31=0x1E2C`. Label `OVL1C_1E2C` already exists; there is
no `case 0x1E2C`. Do **not** splice overlay `0x20` (dest is
`0x12A0`). Do **not** add the later jal-return cases
(`0x1E6C`/`0x1E7C`/`0x1E8C`/`0x1EA8`/`0x1EBC`/`0x1ECC`/
`0x1F04`) until `0x1E2C` is LIVE. Do **not** name anything
ovl28.

Add fixup 6m (own marker) that routes dest `0x1E2C` when
`153==0x1C` to `OVL1C_1E2C`. No rebuild of the composite
or RSPRecomp unless the label is missing.

## Competing hypotheses

- **H-1e2c-ovl1c-jalret:** case `0x1E2C` / `153==0x1C` →
  `OVL1C_1E2C` is the missing jal return. UJ `0x1E2C` → 0.
  New residual is another ovl1c jal-return leftover
  (`0x1E6C` next: `OVL1C_1E2C` sets `r31=0x1E6C`).
- **H-1e2c-not-the-uj-path:** route LIVE but UJ `0x1E2C`
  stays. Then another `jr $ra` writer exists.
- **H-1e2c-breaks-06:** dest `0x1E2C` is also used by a
  boot/control path; routing it breaks `dl06=2/2/0`.
- **H-1e2c-restores-e9:** completing this jal return was
  the missing FULL_SYNC producer. E9 match rises above the
  boot-shaped triplet. Unlikely but cheap.

## Discriminating measurement

One rebuild, one soak (same recipe as s743–s753). Batch:

- `[ovl-route] res=0x1C tgt=0x1E2C` must be LIVE.
- UJ `0x1E2C` should drop vs s753 n=3213 (s752 was 0).
- boot 4/4 `dl06=2/2/0`.
- E9 match / rdpFs vs s753 boot-shaped 3/64 and 0→4483.
- new stray / last_ovl / UJ class (expect `0x1E6C`).
- CRASH=0.

Outcomes:

- route LIVE + UJ 0x1E2C → 0 + dl06 intact →
  H-1e2c-ovl1c-jalret SELECTED; next is the new residual.
- route LIVE + UJ stays → H-1e2c-not-the-uj-path;
  re-open `OVL1C_1F9C` `jr $ra` writers.
- dl06 breaks → H-1e2c-breaks-06; revert the 0x1E2C case
  only (keep dest-0x1E18 / 153==0x1C).
- E9 match rises above the boot-shaped triplet →
  H-1e2c-restores-e9 (report, still record the UJ outcome).

## Commands

    # no composite/RSPRecomp unless OVL1C_1E2C is missing
    # fixup 6m: case 0x1E2C if 153==0x1C goto OVL1C_1E2C
    cmake --build build -j8
    # soak: copy s753 recipe, grep res=0x1C tgt=0x1E2C, SIGKILL, 348s class

ORIGIN: ovl1c jal at `OVL1C_1E18` → callee `0x1F0C`,
return `0x1E2C`. `OVL1C_1F9C` `jr $ra` is the legitimate
return into `OVL1C_1E2C`. Route, not a default-allow of
`0x1E2C` for every resident.
