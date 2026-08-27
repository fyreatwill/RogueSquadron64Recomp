# NEXT work unit (s2686) — audit the next M5 CPU publication boundary

HYPOTHESIS-ID: m5-cpu-mort-publication

## Work unit

Perform a bounded static audit of the remaining `updateVoiceChannelParams`
indirect-call setup and the `voice object+0x140` consumer path. Use companion
address/name evidence and existing generated callers to identify whether a
caller-owned destination or ordered service boundary publishes renderer output
to PCM/AI. Do not add runtime watches, writeback, remaps, or mitigation from
unresolved pointer shapes.

## Competing hypotheses and discriminator

- `H-publish-caller`: the audited caller setup names a legitimate destination
  and ordering edge from rendered voice output toward PCM/AI.
- `H-service-boundary`: the path reaches a service/slot boundary but the
  publication destination remains outside the audited caller.
- `H-unresolved-address`: the remaining callers only pass filter/delay data or
  temporary voice-object storage, so no legitimate publication edge is named.

The discriminator is a complete caller/destination table for both audited
paths: each outcome must identify the writer, destination, payload polarity,
and ordering relation, or explicitly show which field is absent.

## Ground-truth prerequisite

No runtime watch, build, or soak is authorized until the static table names a
ground-truth target.

## Exact commands

1. `grep -n 'updateVoiceChannelParams\|renderVoiceAudioBlock\|0x8009D' ../N64Recomp/RecompiledFuncs/funcs_*.c | head -200`
2. Read bounded caller windows and companion symbol/source matches for every hit.
3. Record the complete destination/order table and selected hypothesis in the ledger.
