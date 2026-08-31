# NEXT work unit — obtain retail writer-loop entry arguments

HYPOTHESIS-ID: m5-retail-entry-argument-ground-truth

Session 3419 selected H-PortEntryArgsZero: both port arms enter the
phase-qualified target call with a0=0x801797B0, a1=0, a2=0x298, and
v0=0x801797B0. The next unit is one independent retail-oracle capture of
the same entry boundary, not another port run.

Competing hypotheses and the single discriminating measurement:

- H-RetailEntryNonzero: retail enters the target call with a nonzero value
  or a different producer length, identifying a port-side zero-input gap.
- H-RetailEntryZero: retail also enters with the zero-fill tuple, so the
  missing nonzero stores occur after or outside this entry boundary.
- H-RetailEntryRouteDifferent: retail's target writes are produced through a
  different entry/caller route, so the observed 0x800078E0 tuple is not
  comparable.

The discriminator is a complete phase-qualified retail table for target
0x1797B0:0x179A48: first entry a0/a1/a2, computed v0, target predicate,
caller/return edge, and post-store value, with whole-RDRAM, title 1024, and
hangar 512 positive controls. Missing controls or missing hangar target rows
are unevaluable.

Use the existing validated Rice/Start oracle recipe and capture under
scratch/agent/s3422_retail_entry_arguments/. Before adding any new port
instrumentation, verify the oracle exposes the needed execution/register
fields. Do not change waits, slots, dispatch, clear behavior, or PCM
writeback.
