# M5 session 4156 — pre-clear overwrite qualified

The repaired regeneration-safe `rs_memset` hook was present at both entry and
exit, and the paired run enabled its positive-control logging. Retail passed
the whole-RDRAM control and both title/hangar phase gates. The port also
reached both target phases: title entry/exit snapshots were zero, while the
hangar entry snapshot for `0x1797B0..0x179A48` had `pre_nz=400` and
`FNV=0xCB1E1263`; the exit snapshot had `pre_nz=0` and
`FNV=0xC0EFD6A5`.

The same run emitted the port's known `0x800078EC` clear stores in the target
span, all zero-valued, including the hangar rows. These two observations
qualify `H-port-preclear-overwritten`: nonzero port state exists immediately
before the known clear and is gone at its exit. The identity and legitimacy of
the earlier nonzero writer remain open; this result authorizes no mitigation.

ORIGIN: the `rs_memset` entry/exit snapshots and the guest clear stores at
`0x800078EC`; no guest, audio, wait, cap, predicate, slot, or writeback
behavior changed.

Evidence: `scratch/agent/s4154_m5_preclear_provenance/`.
