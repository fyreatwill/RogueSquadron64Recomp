# Next work unit: expand the live port span census to resolve the mismatch

HYPOTHESIS-ID: m5-pre-clear-producer-provenance

Session 4158 qualified the route and positive control, but observed only zero
port target-span rows while retail had nonzero hangar bytes. The next unit must
enumerate the entire span on the live port arm, not infer from the sampled
first-byte parity rows.

Competing hypotheses and discriminator:

- H-port-writer-omitted: the port never writes nonzero bytes anywhere in the
  target span before the clear.
- H-port-writer-zero-state: the port writes the span, but its writer fires with
  a zero or wrong producer object/state relative to retail.
- H-port-span-under-sampled: the earlier port writer is nonzero but the current
  parity target selection misses its byte/width/site.

Exact work: make one regeneration-safe, phase-scoped port probe that records
every byte/halfword/word write intersecting `0x1797B0..0x179A48`, retaining PC,
width, value, and phase. Batch it with the existing positive control, then run
`zsh scratch/agent/run_s4158_m5_preclear_span_census.sh` against the same
retail oracle controls. Require whole-RDRAM, title, hangar, and writer-control
gates before interpreting rows. Do not change guest, audio, wait, cap,
predicate, slot, or writeback behavior.

Expected outcomes: no nonzero intersecting port row selects H-port-writer-omitted;
nonzero rows with zero/wrong tuples select H-port-writer-zero-state; a
nonzero row missed by the old parity target selects H-port-span-under-sampled.
