# NEXT work unit — locate the producer of port init mixer count

HYPOTHESIS-ID: m5-port-setup-state-producer

Session 3428 directly witnessed both generated callsites. Retail and both
port arms use `0x80091D14`; neither port arm uses `0x80091C58`. The port init
entry still has `a1=0x0F`, and its pre-allocate edge has `a1=0x5622`; the
earlier producer remains open.

Competing hypotheses and the single discriminating measurement:

- `H-PortCountAtReapplyEntry`: port `a1=0x5622` is already present at
  `reapplyAudioConfig` entry, so its caller supplies the divergent value.
- `H-PortCountFromInitEntry`: port `a1=0x5622` is first observed at
  `initAudioSubsystem`/its route, not at `reapplyAudioConfig` entry.
- `H-PortCountUnresolved`: both entries are live but neither exposes the
  divergent value, requiring an earlier or indirect producer edge.

Exact work: ask the retail oracle first to watch `0x80091B84` and
`0x80091848` with whole-RDRAM, title, and hangar controls. Then add one
regeneration-safe phase-gated host witness at each corresponding generated
port entry, recording `a0..a3`; build once; run the existing silent/image pair
concurrently with `ROGUESQ_LOG_INIT_VOICE_SAMPLE=1`. A port `a1=0x5622` at
`0x80091848` selects `H-PortCountAtReapplyEntry`; only at the `0x80091B84`
route selects `H-PortCountFromInitEntry`; neither with live controls selects
`H-PortCountUnresolved`. Do not change waits, slots, dispatch, clear behavior,
or PCM writeback.
