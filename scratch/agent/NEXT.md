# NEXT work unit (s2314) — companion 640-origin retail writer census

HYPOTHESIS-ID: m5-retail-writer-vi-origin

## Work unit

Ask the retail oracle for ground truth first, then extend the completed
title-plus-six-640/512 recipe with the two companion 640-width origins visible
in the retained VI trace: `0x0066AA00:640` and `0x00696600:640`. Retain the
title bucket, all four existing post-title 512 buckets, both earlier 640
buckets, all sixteen `0x300` slot watches, the whole-ring watch, lifetime
writer histograms, and final snapshots in the same oracle invocation. Keep the
qualified port environment and discover the current nonzero port pair from
that run. No runtime behavior or mitigation change.

## Competing hypotheses and discriminating measurement

- H-Retail-0066AA00-640: the `0x0066AA00:640` bucket contains the
  `0x800078EC` slot writers while `0x00696600:640` stays empty. This is the
  missing retail publication phase.
- H-Retail-00696600-640: the `0x00696600:640` bucket contains the slot
  writers while `0x0066AA00:640` stays empty. This is the missing phase.
- H-Retail-Both-Companion-640: both companion buckets contain writers. Retail
  shares or alternates publication across the paired 640 origins.
- H-Retail-Earlier-Or-Unattributed: both new buckets have positive VI
  callbacks but no writer-PC rows. The writer occurs in another origin or
  phase attribution remains incomplete; do not guess an arm.
- H-CoverageInvalid: whole-RDRAM, title/hangar, either new 640 callback, any
  lifetime writer control, final snapshots, port title/hangar, or retention
  fails.

The discriminator is one complete table keyed by physical slot and VI bucket:
lifetime writer PC/count, callback count, phase writer PC/count for the title,
four 512 buckets, four 640 buckets, final snapshot FNV/nonzero, and the port
stage/source/consumer/later-zero tuple for the actual pair. The lifetime writer
control must be positive before any phase null is interpreted. Possible
outcomes select one hypothesis at this capture scope; none authorizes
writeback, consumer, writer, slot, gate, guard, address-remap, or default
changes.

## Ground-truth preflight

Confirm the s2313 same-run controls before editing the launcher:

    rg -n 'positive-control threshold reached|pc-hist-phase origin=0x00790400|pc-hist-phase origin=0x006ab400|pc-hist-phase origin=0x006ab800|pc-hist-phase origin=0x00656400|pc-hist-phase origin=0x00656800|pc-hist-phase origin=0x0066a500|pc-hist-phase origin=0x00696100|writer-pc pc=0x800078ec n=768|post-value snapshot watch=17' scratch/agent/s2310_m5_per_slot_retail_polarity/oracle.log | tail -80

Require whole-RDRAM `10000`, title/hangar coverage, all sixteen lifetime slot
controls at `768`, active callback counts for all seven existing buckets, and
sixteen nonzero final snapshots. The s2313 port pair was `0x168850`/`0x168B50`
with exact nonzero joins followed by zero payloads; use the actual pair from
the next run rather than assuming those addresses are stable.

## Exact commands

1. Add both arguments below to
   `scratch/agent/run_s2310_m5_per_slot_retail_polarity.sh`, retaining every
   existing phase argument:

       --pc-hist-phase 0x0066AA00:640 --pc-hist-phase 0x00696600:640

2. Syntax-check and run one capture:

       zsh -n scratch/agent/run_s2310_m5_per_slot_retail_polarity.sh
       zsh scratch/agent/run_s2310_m5_per_slot_retail_polarity.sh

3. Parse the resulting oracle and port logs into the complete slot × phase
   table. Report all controls, all nine distinct phase buckets, the selected
   hypothesis, the actual port pair, and its stage/source/consumer/later-zero
   tuple. Treat the repeated `--pc-phase-log-width 0x006AB400:512` as a
   logging-width control, not as another origin bucket.
