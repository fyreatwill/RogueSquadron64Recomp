# NEXT work unit — trace the producer of the divergent init count

HYPOTHESIS-ID: m5-port-init-count-producer

Session 3430 closed the direct `setDisplayMode` audio-call count boundary.
Retail and port both expose `0x8008EBC0` with `a1=0x12` on the qualified route;
port witness saw the same value immediately before `reapplyAudioConfig`.
Neither qualified target-phase run exposed `0x8008EA78`, so it is not a live
producer on this route. The divergent port `a1=0x5622` is already present at
the `initN64RspMixer -> allocateSongChannelArray` edge and remains unexplained.

Competing hypotheses and the single discriminating measurement:

- `H-PortEarlierInitCountCaller`: the next caller before `initN64RspMixer`
  supplies `a1=0x5622` on port while retail supplies `0x561F`.
- `H-PortInitCountStateMutation`: both callers supply the same count, but a
  preceding state write or reload diverges before the init call.
- `H-PortInitCountIndirectRoute`: the differing value arrives through an
  indirect dispatch or route not covered by the current direct-call census.

Exact work: inspect the generated direct JAL/call chain immediately preceding
`0x80091D14`, identify the nearest bounded producer edge, then ask the retail
oracle first for that edge with whole-RDRAM, title, and hangar controls plus a
positive execution watch. Add one regeneration-safe phase-gated witness table
covering every candidate predecessor in the same build; run silent and Factor
5 image arms concurrently with `ROGUESQ_LOG_INIT_VOICE_SAMPLE=1`. A first
caller/state divergence selects the corresponding hypothesis; matching
predecessor state with live controls selects the indirect-route hypothesis.
Do not change waits, slots, dispatch, clear behavior, or PCM writeback.
