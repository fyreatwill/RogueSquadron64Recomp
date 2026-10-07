# Next work unit: attribute the earlier nonzero pre-clear writer

HYPOTHESIS-ID: m5-pre-clear-producer-provenance

Use the repaired `rs_memset` entry/exit control to attribute the earlier
nonzero writer that populates `0x1797B0..0x179A48` before `0x800078EC` clears
it. The s4156 port reached both target phases, with hangar `pre_nz=400` at
entry and `pre_nz=0` at exit; its known clear stores were zero.

Competing hypotheses and discriminator:

- H-earlier-writer-legitimate: a source-level port writer with a legitimate
  nonzero value precedes the clear and accounts for the retail-shaped bytes.
- H-earlier-writer-mismatch: the earlier writer fires but produces a value or
  span that does not match the retail source; the clear is downstream of the
  mismatch.
- H-instrument-gap/route-invalid: the CPU-writer positive control still does
  not fire, or either arm lacks whole-RDRAM/title/hangar gates. No provenance
  conclusion is valid.

Exact work: add one regeneration-safe, phase-gated writer census at the
source-level stores that can populate `0x1797B0..0x179A48`, batch its positive
control with the existing entry/exit snapshots, build once, and run the paired
capture. Require whole-RDRAM, title, and hangar controls plus a writer-control
row before interpreting source rows. Do not change guest, audio, wait, cap,
predicate, slot, or writeback behavior.

Expected outcomes: a matching nonzero port writer selects
H-earlier-writer-legitimate; a mismatching writer selects
H-earlier-writer-mismatch; missing writer control or route gates selects
H-instrument-gap/route-invalid.
