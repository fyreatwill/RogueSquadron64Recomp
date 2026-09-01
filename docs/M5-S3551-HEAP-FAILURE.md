# M5 session 3551 — pre-title heap failure

The generated body identifies guest `0x8000D704` as `sw $zero, 0x4($v0)`,
after the cached free-list head load at `0x8000D6F4` from `0x801163B0`. The
only generated callers are `submitSceneNodeRender` edges at `0x800104A8` and
`0x80010CD8`.

A regeneration-safe table recorded phase, all four entry arguments, cached
head, cached node offset-0, count byte, limit, and return address, with 32
rows per phase. The final real-audio/LLE-solo/spin-yield/autopilot run reached
title `0x00790400` and hangar `0x006AB400`, emitted 96 entry rows, but zero
pre-store rows, zero heap-list guard rows, and no crash before deliberate
SIGKILL. Cached heads were mapped KSEG0 values; the failing path was absent,
so state legitimacy was not classified. `ra` was not reliable direct-call
attribution (`0x800155EC` in phase 3 and zero in phase 5).

The independent retail oracle passed its whole-RDRAM positive control (10,000
callbacks before cap; 58,148 total in 30 seconds), reached title 1024, and
observed 48,148 writes to physical `0x1163B0:0x1163C0`. This establishes
retail cache activity but not a writer PC or equivalence to the port state.

This closes `H-HeapRoleUnknown` but does not distinguish legitimate from
corrupt state. The next probe must join the `0x8000D6F4` load, `0x8000D700`
branch outcome, and `0x8000D704` store in one phase-bucketed table.

ORIGIN: diagnostic-only observation; no mitigation was added.
