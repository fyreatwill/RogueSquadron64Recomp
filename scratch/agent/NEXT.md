# NEXT work unit (s2315) — remaining VI-origin retail writer census

HYPOTHESIS-ID: m5-retail-writer-vi-origin

## Work unit

Ask the retail oracle for ground truth first, retain the completed title,
four post-title 512, and four 640 buckets, then add the six remaining VI
origins observed in the same trace:

    --pc-hist-phase 0x00000280:320
    --pc-hist-phase 0x006BA280:320
    --pc-hist-phase 0x005D4500:640
    --pc-hist-phase 0x0062C200:640
    --pc-hist-phase 0x0062BD00:640
    --pc-hist-phase 0x00790800:1024

Retain the whole-ring watch, all sixteen `0x300` slot watches, lifetime
writer histograms, final snapshots, and the actual nonzero port stage pair in
the same invocation. No runtime behavior, output contract, or mitigation
change.

## Competing hypotheses and discriminating measurement

- H-Retail-Remaining-Origin: at least one remaining origin has a positive
  phase writer-PC row for `0x800078EC`; that origin is a measured publication
  phase.
- H-Retail-Shared-Remaining-Origins: two or more remaining origins have
  positive phase writer-PC rows; retail shares or alternates publication.
- H-Retail-Earlier-Or-Unattributed: every new bucket has positive VI callbacks
  but no phase writer-PC rows; the writer is outside all observed buckets or
  phase attribution remains incomplete.
- H-CoverageInvalid: whole-RDRAM, title/hangar, any new callback bucket,
  lifetime writer controls, final snapshots, port title/hangar, or retention
  fails.

The discriminator is one complete bucket × slot table: callback count,
phase writer PC/count, lifetime writer PC/count, final snapshot FNV/nonzero,
and the actual port stage/source/consumer/later-zero tuple. The lifetime
writer control must be positive before any phase null is interpreted. Any
positive remaining bucket selects the corresponding origin hypothesis;
multiple positives select shared/alternating publication; all empty with
positive callbacks selects the unattributed hypothesis. No outcome authorizes
writeback, consumer, writer, slot, gate, guard, address-remap, or default
changes.

## Ground-truth preflight

Confirm the current same-run controls before editing the launcher. Require
whole-RDRAM `10000`, title/hangar coverage, all sixteen lifetime slot writer
controls at `768`, all nine existing phase callback counts, and sixteen
nonzero final snapshots. The prior run's new buckets were
`0x0066AA00:640=139` and `0x00696600:640=219`; do not infer stability from
those counts. Re-scan the VI trace for the six candidate origins before
arming them.

## Exact commands

1. Add the six `--pc-hist-phase` arguments above to
   `scratch/agent/run_s2310_m5_per_slot_retail_polarity.sh`, retaining every
   existing phase argument.
2. Syntax-check and run one capture:

       zsh -n scratch/agent/run_s2310_m5_per_slot_retail_polarity.sh
       zsh scratch/agent/run_s2310_m5_per_slot_retail_polarity.sh

3. Parse the resulting oracle and port logs into the complete bucket × slot
   table. Report all controls, all fifteen distinct configured buckets, the
   selected hypothesis, the actual port pair, and its stage/source/consumer/
   later-zero tuple. Treat the repeated
   `--pc-phase-log-width 0x006AB400:512` as a logging-width control, not as an
   additional origin bucket.
