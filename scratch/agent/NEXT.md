# NEXT work unit (s2313) — earlier 640-origin retail writer census

HYPOTHESIS-ID: m5-retail-writer-vi-origin

## Work unit

Ask the retail oracle for ground truth first, then extend the completed
title-plus-four-512 recipe with the two earlier 640-width origins visible in
the qualified trace: `0x0066A500:640` and `0x00696100:640`. Retain the title
bucket, both active 512 target buckets, both tested post-title 512 buckets,
all sixteen 0x300 slot watches, the whole-ring watch, lifetime writer
histograms, and final snapshots in the same oracle invocation. Keep the
qualified port environment and discover the current nonzero port pair from
that run. No runtime behavior or mitigation change.

## Competing hypotheses and discriminating measurement

- H-Retail-0066A500-640: the `0x0066A500:640` bucket contains the
  `0x800078EC` slot writers while `0x00696100:640` stays empty. That origin is
  the missing retail publication phase.
- H-Retail-00696100-640: the `0x00696100:640` bucket contains the slot
  writers while `0x0066A500:640` stays empty. That origin is the missing
  publication phase.
- H-Retail-Both-640: both 640 buckets contain writers. Retail shares or
  alternates publication across the earlier origins.
- H-Retail-Earlier-Or-Unattributed: both new 640 buckets have positive VI
  callbacks but no writer-PC rows. The writer occurs in another earlier
  origin or phase attribution remains incomplete; do not add a guessed arm.
- H-CoverageInvalid: whole-RDRAM, title/hangar, either new 640 callback,
  any lifetime writer control, final snapshots, port title/hangar, or
  retention fails.

The discriminator is one complete table keyed by physical slot and VI bucket:
lifetime writer PC/count, callback count, phase writer PC/count for the title,
four 512 buckets, and both new 640 buckets, final snapshot FNV/nonzero, and
the port stage/source/consumer/later-zero tuple for the actual pair. The
lifetime writer control must be positive before any phase null is interpreted.
Possible outcomes select one hypothesis at this capture scope; none authorizes
writeback, consumer, writer, slot, gate, guard, address-remap, or default
changes.

## Ground-truth preflight

Confirm the prior same-run controls before editing the launcher:

    rg -n 'positive-control threshold reached|pc-hist-phase origin=0x00790400|pc-hist-phase origin=0x006ab400|pc-hist-phase origin=0x006ab800|pc-hist-phase origin=0x00656400|pc-hist-phase origin=0x00656800|writer-pc pc=0x800078ec n=768|post-value snapshot watch=17' scratch/agent/s2310_m5_per_slot_retail_polarity/oracle.log | tail -60

Require whole-RDRAM `10000`, title/hangar coverage, all sixteen lifetime slot
controls at `768`, active callback counts for the title and all four existing
512 origins, and sixteen nonzero final snapshots. The s2312 port pair was
`0x166D50`/`0x167050` with one stage-only row and one exact source/consumer
join followed by zero payloads; use the actual pair from the next run rather
than assuming these addresses are stable.

## Exact commands

1. Add both arguments below to
   `scratch/agent/run_s2310_m5_per_slot_retail_polarity.sh`, retaining every
   existing phase argument:

       --pc-hist-phase 0x0066A500:640 --pc-hist-phase 0x00696100:640

2. Syntax-check and run one capture:

       zsh -n scratch/agent/run_s2310_m5_per_slot_retail_polarity.sh
       zsh scratch/agent/run_s2310_m5_per_slot_retail_polarity.sh

3. Parse the resulting oracle and port logs into the complete slot × phase
   table. Report all controls, all seven distinct phase buckets, the selected
   hypothesis, the actual port pair, and its stage/source/consumer/later-zero
   tuple. Treat the repeated `--pc-phase-log-width 0x006AB400:512` as a
   logging-width control, not as another origin bucket.
