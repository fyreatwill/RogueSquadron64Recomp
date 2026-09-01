# M5 Session 3521 — selector AI callsite boundary

The independent retail oracle ran with a whole-RDRAM positive control, the
physical selector span `0x00149758..0x00149760`, and an execution watch at
`0x80029E78` phase-traced to the 512 hangar. The controls were live: 10,012
whole-RDRAM writes, 12 selector-span writes, and one hangar execution at
`0x80029E78`. Its caller was `0x80029E64`; the row carried `a0=0x5622`,
`a1=0x8A0`, `a2=0x10`, `s1=0x80165ED0`, and `v0=0x561F`.

The port was rebuilt with callsite labels at generated calls `0x80091BAC` and
`0x80091CB8`, plus the existing native AI-boundary and selector producer/store
controls. The validated real-audio LLE/spin-yield/autopilot route reached title
1024 and hangar 512. The port callsite control fired during startup, and the
producer/store controls fired in hangar, but neither labeled callsite produced
a hangar row; the host AI-boundary target row was also absent.

This selects `H-PortCallMissing` at the qualified scope: the two known
generated callers do not enter the native AI primitive during the target phase.
It rules out a target-phase argument mismatch at those callsites. It does not
yet prove that `0x80029E78` is semantically equivalent to the host primitive,
nor does it identify the route gate or missing caller that replaces the retail
path.

ORIGIN: diagnostic-only retail execution watch and port callsite/host/store
witnesses; no audio, selector, task, or output state was rewritten, skipped,
or validated.

Evidence: `scratch/agent/s3521_selector_callsite/retail.log`,
`scratch/agent/s3521_selector_callsite/port.log`, and
`scratch/agent/s3521_selector_callsite/status.txt`.
