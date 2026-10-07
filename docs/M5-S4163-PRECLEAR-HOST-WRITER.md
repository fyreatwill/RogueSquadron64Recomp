# M5 s4163 — pre-clear host writer boundary

The canonical real-audio/LLE/autopilot capture passed host-write, non-scalar,
title-VI-1024, and hangar-VI-512 controls.

`pi_rom_to_rdram` overlapped `0x1797B0..0x179A48` during title at
`0x179720` and `0x179820` (length `0x100`); the post-write field prefix was
`0x00010540`. The later hangar pre-clear snapshot contained 607 nonzero bytes
before the guest clear. Generated guest scalar and non-scalar target rows were
zero-valued. H-host-ROM-writer is selected: the earlier producer is a
legitimate host ROM asset load, not an unobserved inline guest store. No
mitigation or behavior changed.

Evidence: `scratch/agent/s4159_m5_preclear_span_census/port.log`.
