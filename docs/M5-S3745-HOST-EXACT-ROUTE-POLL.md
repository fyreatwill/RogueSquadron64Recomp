# M5 session 3745 — host-side exact-route poll

The Debug target built successfully after adding a portable, phase-gated poll
of physical RDRAM fields `0x128C92` and `0x128CD0..0x128CD3`. The poller's
live-RDRAM control observed five `0x80130B50` changes in each arm.

The concurrent qualified real/silent pair both reached title
`1024 @ 0x00790400` and hangar `512 @ 0x006AB400`. Each arm reported one
initial exact-field snapshot (`0x92=0x00`, `0xD0=0x00000400`) and no later
poll transition. The existing generated scalar/non-literal witness and RSP
DMA witness also passed their controls and emitted zero exact rows in both
arms.

This selects `H-ExactFieldUnwritten` for persistent host-side changes visible
to the 1 ms poll, while leaving a transient host write formally unevaluable:
the poll has no writer PC and can miss a write-and-clear between samples.
`H-RouteStateNotSource` remains open. No value was suppressed or rewritten.

ORIGIN: the only observed exact-field value was the pre-existing route state
(`0xD0=0x400`); no host writer changed either field in the measured window.
The `0x800078EC` zero-fill writer was not altered.

Evidence: `scratch/agent/s3744_port_exact_route/real.log` and `silent.log`.
