# NEXT work unit — audit M5 named consumer reachability

HYPOTHESIS-ID: m5-consumer-reachability-audit

Session 3348 reached the validated hangar phase with positive controls and
observed port slot/status activity, but none of the four retail-named
consumer PCs. Do one bounded static audit before adding instrumentation or
changing behavior.

Competing hypotheses:

- `H-ConsumerIndirect`: each named consumer is reached only through an
  indirect callback/function-pointer edge absent from the direct caller map.
- `H-ConsumerGate`: direct or indirect callers exist, but a visible status,
  slot, or phase predicate prevents the port from entering them.
- `H-ConsumerWrongNames`: the retail PCs are not the corresponding port
  consumers for this route, so the existing runtime probe is aimed at the
  wrong bodies.

Discriminator: enumerate every generated caller/reference and every callback
or function-pointer registration edge for `0x80094648`, `0x8009B600`,
`0x8009B85C`, and `0x8009BDE8`, then reconcile each with the M5 plan's slot,
status, and voice-table accesses. A complete indirect-only chain selects
`H-ConsumerIndirect`; an enumerated chain with a reachable predicate selects
`H-ConsumerGate`; no corresponding port body/edge selects
`H-ConsumerWrongNames`. An incomplete static map selects none and defines the
next ground-truth probe.

Exact commands:

    rg -n -S '80094648|8009B600|8009B85C|8009BDE8' ../N64Recomp/RecompiledFuncs docs src
    rg -n -S 'registerSiCallback|8011A8A4|80141AD8|80154620|startSongSequence|serviceVoicePoolFrame|accumulateVoiceSampleOffset' ../N64Recomp/RecompiledFuncs docs src
    sed -n '<bounded caller windows>p' ../N64Recomp/RecompiledFuncs/funcs_*.c

Do not build, add a probe, change behavior, or add a mitigation until the
static census identifies the discriminating edge.
