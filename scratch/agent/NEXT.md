# NEXT work unit (s2312) — retail writer other-VI-origin census

HYPOTHESIS-ID: m5-retail-writer-vi-origin

## Work unit

Ask the retail oracle for ground truth first, then extend the completed
title-plus-dual-512 recipe with both recurring post-title 512 origins:
`0x00656400:512` and `0x00656800:512`. Retain the title bucket
`0x00790400:1024`, both target buckets (`0x006AB400:512` and
`0x006AB800:512`), all sixteen 0x300 slot watches, the whole-ring watch,
lifetime writer histograms, and final snapshots in the same oracle
invocation. Keep the qualified port environment and discover the current
nonzero port pair from that run. No runtime behavior or mitigation change.

## Competing hypotheses and discriminating measurement

- H-Retail-00656400: the `0x00656400:512` bucket contains the sixteen
  `0x800078EC` slot writers while `0x00656800:512` stays zero. That origin
  is the missing retail publication phase.
- H-Retail-00656800: the `0x00656800:512` bucket contains the writers while
  `0x00656400:512` stays zero. That origin is the missing phase.
- H-Retail-Both-Alternating: both buckets contain writers. Retail alternates
  or shares publication across the two post-title origins.
- H-Retail-Earlier-Or-Unattributed: all five phase buckets remain empty. The
  writers occur in one of the earlier VI origins in the same trace or the
  phase attribution is still incomplete; do not add a guessed arm.
- H-CoverageInvalid: whole-RDRAM, title/hangar, all sixteen lifetime writer
  controls, one or more phase callback controls, nonzero final snapshots,
  port title/hangar, or 45-second retention fails.

The discriminator is one complete table keyed by physical slot and VI bucket:
lifetime writer PC/count, title count, each of the two existing 512-phase
counts, the two new 512-phase counts, final snapshot FNV/nonzero, and the
port stage/source/consumer/later-zero tuple for the actual pair. The lifetime
writer control must be positive before any phase null is interpreted. Possible
outcomes select one hypothesis at this capture scope; none authorizes
writeback, consumer, writer, slot, gate, guard, address-remap, or default
changes.

## Ground-truth preflight

Confirm the same-run positive controls and phase headings before editing the
launcher:

    rg -n 'positive-control threshold reached|pc-hist-phase origin=0x00790400|pc-hist-phase origin=0x006ab400|pc-hist-phase origin=0x006ab800|writer-pc pc=0x800078ec n=768|post-value snapshot watch=17' scratch/agent/s2310_m5_per_slot_retail_polarity/oracle.log | tail -40

Require whole-RDRAM `10000`, title/hangar coverage, all sixteen lifetime slot
controls at `768`, active callback counts for the title and both existing 512
origins, and sixteen nonzero final snapshots. The s2311 port pair was
`0x169150`/`0x166450` with exact source/consumer matches followed by later
zero rows; use the actual pair from the next run rather than assuming these
addresses are stable.

## Exact commands

1. Add both arguments below to
   `scratch/agent/run_s2310_m5_per_slot_retail_polarity.sh`, retaining every
   existing phase argument:

       --pc-hist-phase 0x00656400:512 --pc-hist-phase 0x00656800:512

2. Syntax-check and run one capture:

       zsh -n scratch/agent/run_s2310_m5_per_slot_retail_polarity.sh
       zsh scratch/agent/run_s2310_m5_per_slot_retail_polarity.sh

3. Parse the resulting oracle and port logs into the complete slot × phase
   table. Report all controls, all six phase buckets, the selected hypothesis,
   the actual port pair, and its stage/source/consumer/later-zero tuple.
