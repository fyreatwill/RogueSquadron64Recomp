# M5 Session 3525 — selector-store entry boundary

The retail oracle used a whole-RDRAM positive control and a phase-gated
execution range `0x8008F000..0x8008F2A0`. The positive control reached 10,000
callbacks and was removed; retail reached title 1024 and hangar 512. The
range executed 981 times, including the two selector stores, and the
independent `0x80029E78` watch fired twice in hangar from `0x80029E64`.

The port build added a regeneration-safe entry witness at
`allocateSongChannelArray` (`0x8008F000`) with `$ra` and argument capture. The
first port arm omitted the validated LLE/spin-yield/autopilot route and stalled
at width 640. The corrected arm used the validated route but crashed before
title in `spTaskSchedulerThread`, with `last-guest-pc=0x8000834c`. Its entry
positive control fired at startup, but it produced no title or hangar rows.

This selects `H-CaptureInvalid` for the port comparison. It does not select an
alternate caller, a route gate, or parity at the entry boundary. The retail
range result remains useful: the immediate predecessors of the store
instructions are `0x8008F224` and `0x8008F260` within the same function.

ORIGIN: the entry witness records phase, guest return address, and arguments;
it does not alter audio, selector, task, or output state. The crash is a route
failure observed in the runtime, not a mitigation target.

Evidence: `scratch/agent/s3525_selector_oracle.log`,
`scratch/agent/s3525_selector_port.log`, and
`scratch/agent/s3525_selector_port_fixed.log`.
