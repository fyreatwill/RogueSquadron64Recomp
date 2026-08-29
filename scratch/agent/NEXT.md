# NEXT work unit — trace the `musyxStopVoice` index producer edge

HYPOTHESIS-ID: m3-musyx-stop-voice-index

Session 3154 selected `H-M3-UnclassifiedProducer` for the complete
`musyxStopVoice` `+0x1` computed-record store: the base check dominates, but
the sole caller's `s6` index has no dominating `<0x20` proof at the call.

## Competing hypotheses and discriminator

- `H-M3-ValidProducer`: the caller's `s6` is proven in range before the call.
- `H-M3-UnclassifiedProducer`: the producer/control-flow edge remains
  unbounded; identify it without adding a guard.
- `H-M3-DeadSite`: the call is not reachable or the site is only lowering.

## Single work unit

Trace `s6` at `tickAllAudioChannels:0x8008CED0` backward through every
pre-call predecessor and enumerate every writer/control-flow edge reaching
that call. Reconcile the result with the companion symbol/ELF if available.
The discriminator is a complete predecessor table: a dominating `0..31`
proof selects valid, any reachable unbounded producer selects unclassified,
and no predecessor selects dead. Do not edit generated functions or add guards.

Exact starting commands:

```sh
rg -n 'tickAllAudioChannels|0x8008CED0|ctx->r22|\\$s6' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_23.c
rg -n '0x8008CED0|tickAllAudioChannels' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs /Users/williambuckley/Documents/Tools/rogue_squadron64
```
