# M5 s4162 — pre-clear non-scalar writer census

The rebuilt port ran `scratch/agent/run_s4159_m5_preclear_span_census.sh` with
the independent route controls and the new regeneration-safe operation-entry
witness. Host-write, title VI 1024, hangar VI 512, and the non-scalar positive
control all fired.

The target span `0x1797B0..0x179A48` produced one operation-level row:
`rs_memset` at guest entry `0x800078E0`, destination `0x801797B0`, length
`0x298`, and zero fill. No target-overlapping `zmemcpy` row and no nonzero
non-scalar payload were observed. The two generated operation entries were
instrumented through `tools/apply_s4162_m5_nonscalar_writer.py`, so the change
survives regeneration.

This closes the measured `rs_memset`/`zmemcpy` entry class as the source of a
distinct nonzero pre-clear writer. It does not establish that the earlier
nonzero snapshot is an artifact: arbitrary uninstrumented host or inline guest
writes remain outside this census. ORIGIN: the legitimate operation writers
are the guest `rs_memset`/`zmemcpy` entries; the observed fill payload was zero,
not suppressed or changed.
