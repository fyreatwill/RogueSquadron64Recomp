# NEXT work unit — witness real setup-state callers

HYPOTHESIS-ID: m5-port-setup-state-producer

Session 3429 showed that the prior labels are instructions, not the named
function entries: retail hit `0x80091848` but not `0x80091B84`, while the port
entry witness saw only `reapplyAudioConfig a1=0x12` and no target-phase init
entry. The actual `setDisplayMode` callsites are `0x8008EA78` and
`0x8008EBC0`.

Competing hypotheses and the single discriminating measurement:

- `H-PortCountAtReapplyCaller`: port `a1=0x5622` is present before
  `0x8008EBC0`, so `setDisplayMode` supplies it.
- `H-PortCountAtInitCaller`: port `a1=0x5622` is present before
  `0x8008EA78`, so the init route supplies it.
- `H-PortCountUnresolved`: neither real callsite exposes the divergent count,
  requiring an earlier or indirect producer edge.

Exact work: ask the retail oracle first to watch `0x8008EA78` and `0x8008EBC0`
with whole-RDRAM, title, and hangar controls. Then add one regeneration-safe
phase-gated host witness immediately before each generated call, recording
`a0..a3`; build once; run the existing silent/image pair concurrently with
`ROGUESQ_LOG_INIT_VOICE_SAMPLE=1`. A port `a1=0x5622` before `0x8008EBC0`
selects `H-PortCountAtReapplyCaller`; only before `0x8008EA78` selects
`H-PortCountAtInitCaller`; neither with live controls selects
`H-PortCountUnresolved`. Do not change waits, slots, dispatch, clear behavior,
or PCM writeback.
