# M5 Session 3519 — selector callsite context join

The independent retail oracle ran first with a whole-RDRAM positive control,
the physical selector span, and the newly chosen execution range
`0x80091C58..0x80091D18`. The positive control reached 10,000 callbacks and
the selector watch remained armed. The range fired in the 512 hangar phase at
origin `0x006AB400`, including the live caller path through `0x80091D14`.

Retail's phase-matched rows carried `a0=0x80165ED0` and `a1=0x12` into the
callsite. At `0x80091CC0`, the path passed `a0=0x5622` to the call at
`0x80029E78` and observed `v0=0x561F`; the eventual selector stores therefore
have a live internal transformation between the callsite context and the
store field.

The existing Debug build was rebuilt before the port run. The real-audio,
LLE/spin-yield/autopilot port arm reached title VI 1024 and hangar VI 512.
The new producer-context witness fired in both phases. In hangar it recorded
`a0=0x80165ED0`, `a1=0x12`, and `s1=0x80165ED0`. The qualified selector-store
witnesses also fired: the port stored `0x80171E70` and `0x80173CB0` while its
store `s1` was `0x5622`.

Thus the producer/call boundary is phase-qualified and agrees on the
meaningful selector inputs; it does not select an upstream producer
divergence. The first observed difference is later in the mixer path, with
the retail callsite evidence identifying `0x80029E78` as the next internal
boundary to capture. This does not yet establish whether that function's
input, return value, or a subsequent instruction writes the differing field.

ORIGIN: diagnostic-only oracle execution watches and port context/store
witnesses; no audio, selector, task, or output state was rewritten or
skipped.

Evidence: `scratch/agent/s3519_selector_callsite_oracle/run.log` and
`scratch/agent/s3519_selector_callsite_port/run.log`.
