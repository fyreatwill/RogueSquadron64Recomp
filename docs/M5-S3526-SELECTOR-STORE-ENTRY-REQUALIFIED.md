# M5 Session 3526 — selector-store entry requalification

Ran the reachable real-audio/LLE/spin-yield/autopilot port arm with the
selector entry, producer-context, store-context, table, route, caller, mixer,
and AI-boundary witnesses enabled. Startup controls fired. The port reached
title VI 1024 (`0x00790400`) at 13.8 seconds and hangar VI 512
(`0x006AB400`) at 34.1 seconds.

In hangar, `allocateSongChannelArray` entry `0x8008F000` fired once with
`a0=0x12`, `a1=0x5622`, `a2=0`, and `a3=1`. Both selector-store contexts
fired, and the producer-context witness fired once with `a0=0x80165ED0`,
`a1=0x12`, `s1=0x80165ED0`. The known caller, route, and AI-boundary rows
remained absent in hangar. The run was SIGKILLed after the bounded 90-second
window without a crash marker.

This validates that the target entry and producer/store path execute on the
reachable real-audio route. It does not distinguish an alternate caller from
an enclosing route gate: the generated host wrapper reports `ra=0`, and the
known route witnesses were not present in the same hangar phase. No audio,
selector, task, or output state was changed.

ORIGIN: diagnostic-only entry and phase-keyed context observations; no
mitigation or guest-state rewrite.

Evidence: `scratch/agent/s3526_selector_port.log` and the independently
qualified retail controls recorded in `scratch/agent/s3525_selector_oracle.log`.
