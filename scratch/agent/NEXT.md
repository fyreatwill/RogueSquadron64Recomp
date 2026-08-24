# NEXT work unit (s2311) — retail writer VI-origin census

HYPOTHESIS-ID: m5-retail-writer-vi-origin

## Work unit

Ask the retail oracle for ground truth first, then extend the corrected
per-slot recipe with one additional phase bucket:
0x00790400:1024. Retain both active 512 buckets
(0x006AB400:512 and 0x006AB800:512), all sixteen 0x300 slot watches, the
whole-ring watch, lifetime writer histograms, and final snapshots in the same
oracle invocation. Keep the qualified port environment and discover the
current nonzero port pair from that run. No runtime behavior or mitigation
change.

The s2310 corrected run passed the lifetime controls and both 512 VI buckets,
but all sixteen retail ring writers were absent from both 512 buckets. Its
final snapshots were nonzero, so the unresolved question is where the
lifetime writer sequence actually occurs.

## Competing hypotheses and discriminating measurement

- H-RetailTitlePhase: the title bucket contains all or most of the sixteen
  768-byte writers while both 512 buckets remain zero. Retail populates the
  ring before the port's target phase; this supports the target-phase
  role/time skew and does not authorize a port writeback.
- H-RetailOtherPhase: title and both 512 buckets remain zero despite positive
  lifetime writers. The writers occur in another VI origin/width; use the
  same-run VI trace to identify that origin before adding another arm.
- H-RetailTargetPhaseReappears: at least one 512 bucket contains the current
  slot writer. The s2310 absence was recipe-sensitive; join the exact origin
  and destination before revising the polarity result.
- H-CoverageInvalid: whole-RDRAM, title/hangar, ring-wide, all sixteen
  lifetime slot writers, a phase bucket, final snapshot, port title/hangar,
  or 45-second retention fails.

The discriminator is one table keyed by physical slot and VI bucket:
lifetime writer PC/count, title-phase count, each 512-phase count, final
snapshot FNV/nonzero, and the port stage/source/consumer/later-zero tuple for
the actual pair. The lifetime writer control must be positive before any
phase null is interpreted. Possible outcomes select one hypothesis at this
capture scope; none authorizes writeback, consumer, writer, slot, gate,
guard, address-remap, or default changes.

## Ground-truth preflight

Confirm the s2310 dual-bucket controls and the physical watch geometry before
editing the launcher:

rg -n 'pc-hist-phase origin=0x006ab400|pc-hist-phase origin=0x006ab800|watch write \[0x00166450|post-value snapshot watch=17|writer-pc watch=17' scratch/agent/s2310_m5_per_slot_retail_polarity/oracle.log | tail -30

Require the prior run's whole-RDRAM 10000 threshold, title/hangar origins,
sixteen 768-write lifetime slot controls, both 512 phase VI counts, and
sixteen nonzero final slot snapshots.

## Exact commands

1. Add --pc-hist-phase 0x00790400:1024 to
   scratch/agent/run_s2310_m5_per_slot_retail_polarity.sh, retaining both
   existing 512 phase arguments. Rename the launcher only if desired; keep
   the HYPOTHESIS-ID unchanged.
2. Syntax-check and run one capture:

   zsh -n scratch/agent/run_s2310_m5_per_slot_retail_polarity.sh
   zsh scratch/agent/run_s2310_m5_per_slot_retail_polarity.sh

3. Parse the resulting oracle.log and port.log into one complete
   dynamic-slot table. Report all controls, all three phase buckets, and the
   selected hypothesis. If the pair rotates, use its actual destinations.
