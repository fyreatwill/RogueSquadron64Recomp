# NEXT work unit (s2310) — per-slot retail polarity

HYPOTHESIS-ID: m5-per-slot-retail-polarity

## Work unit

Ask the retail oracle for ground truth first, then run one phase-gated
same-run port/retail capture with the existing writer hooks. Keep the
whole-RDRAM control first, retain the whole-ring watch, and add all 16
`0x300` PCM-slot watches as one batched oracle arm. Collect a phase writer
histogram and final post-value snapshot for every slot. Discover the current
nonzero port stage pair from the port log; do not assume the previous
`0x168850`/`0x168B50` pair. Join the exact port stage/source/consumer/later
zero row to the corresponding retail slot summary. No runtime behavior or
mitigation change.

## Competing hypotheses and discriminating measurement

- H-RetailNonzeroSameSlot: retail writes the dynamically selected physical
  slot with nonzero final data in the target phase. The port's later
  image-DMA zero is a port-side output-contract divergence, not a harmless
  ring-role rotation.
- H-RetailZeroSameSlot: retail's corresponding slot is zero after its writer
  sequence. The port zero-fill polarity is shared and remains a candidate
  legitimate contract edge, despite the aggregate ring result.
- H-SlotRoleTimeSkew: retail writes the physical slot, but its per-slot writer
  sequence/VI and final value do not join the port's stage→PCM→zero sequence;
  the whole-ring comparison was insufficient because the animated ring role
  changed between observations.
- H-CoverageInvalid: the whole-RDRAM control, title/hangar gates, ring-wide
  watch, any per-slot writer control, or the port 45-second retention gate
  fails.

The discriminator is one table keyed by dynamic physical destination:
port stage event/FNV/nz, exact source and consumer event/FNV/nz, first later
zero event and writer provenance, retail per-slot phase writer PC/count,
post-value zero/nonzero counts, final snapshot FNV/nonzero, and the VI phase
bucket. The same-run positive controls must pass before any null is read.
Possible outcomes select one hypothesis at this capture scope; none
authorizes writeback, consumer, slot, gate, guard, address-remap, or default
changes.

## Ground-truth preflight

Confirm the prior whole-ring control and the physical slot geometry before
arming the expanded watch set:

`rg -n 'positive-control threshold reached|watch write \[0x00166450|post-value snapshot watch=1|writer-pc-phase origin=0x006ab400 width=512 watch=1|writer-pc pc=0x800078ec' scratch/agent/s2309_m5_dynamic_zero_fill/oracle.log | tail -20`

The new oracle argument list must put these watches in this order:

`--watch-write 0x0:0x800000`

`--watch-write 0x166450:0x169450`

`--watch-write 0x166450:0x166750 --watch-write 0x166750:0x166A50 --watch-write 0x166A50:0x166D50 --watch-write 0x166D50:0x167050 --watch-write 0x167050:0x167350 --watch-write 0x167350:0x167650 --watch-write 0x167650:0x167950 --watch-write 0x167950:0x167C50 --watch-write 0x167C50:0x167F50 --watch-write 0x167F50:0x168250 --watch-write 0x168250:0x168550 --watch-write 0x168550:0x168850 --watch-write 0x168850:0x168B50 --watch-write 0x168B50:0x168E50 --watch-write 0x168E50:0x169150 --watch-write 0x169150:0x169450`

Use `--pc-hist-phase 0x006AB400:512`, `--pc-hist-watch 1` through
`--pc-hist-watch 17`, and `--post-value-watch 1` through
`--post-value-watch 17`, plus the existing `--watch-pc 0x800078EC`,
`--pc-phase-log-width 0x006AB400:512`, `--vi-trace`, and eleven-Start press
schedule. Require whole-RDRAM `10,000`, title/hangar origins, ring writes,
at least one per-slot writer histogram, and a nonzero final snapshot before
interpreting a slot null.

## Exact commands

1. Create `scratch/agent/run_s2310_m5_per_slot_retail_polarity.sh` with the
   batched oracle arguments and the qualified port environment from s2309.
2. Syntax-check and run one capture:

   `zsh -n scratch/agent/run_s2310_m5_per_slot_retail_polarity.sh`

   `zsh scratch/agent/run_s2310_m5_per_slot_retail_polarity.sh`

3. Report the complete dynamic-slot table, all positive controls, and the
   selected hypothesis. If the port's nonzero pair rotates again, use its
   actual physical destinations from that run; do not read a fixed-slot null.
