# Next work unit: qualify the port route, then attribute the earlier writer

HYPOTHESIS-ID: m5-pre-clear-producer-provenance

Use the repaired `rs_memset` entry/exit control and the new target-span writer
census to attribute the earlier nonzero writer that populates
`0x1797B0..0x179A48` before `0x800078EC` clears it. Session 4157's retail arm
was valid and saw 664 hangar `0x800078EC` writes plus the named earlier writer
families, but both port retries crashed before title at `0x8000834C`.

Competing hypotheses and discriminator:

- H-earlier-writer-legitimate: a source-level port writer with a legitimate
  nonzero value precedes the clear and accounts for the retail-shaped bytes.
- H-earlier-writer-mismatch: the earlier writer fires but produces a value or
  span that does not match the retail source; the clear is downstream of the
  mismatch.
- H-instrument-gap/route-invalid: the CPU-writer positive control still does
  not fire, or either arm lacks whole-RDRAM/title/hangar gates. No provenance
  conclusion is valid.

Exact work: rerun `zsh scratch/agent/run_s4157_m5_preclear_writer_census.sh`
with the same rebuilt binary, after first requiring a port title/hangar route.
Require whole-RDRAM, title, and hangar controls plus
`[m5-preclear-writer-control]` before interpreting target rows. Do not change
guest, audio, wait, cap, predicate, slot, or writeback behavior.

Expected outcomes: a matching nonzero port writer selects
H-earlier-writer-legitimate; a mismatching writer selects
H-earlier-writer-mismatch; missing writer control or route gates selects
H-instrument-gap/route-invalid.
