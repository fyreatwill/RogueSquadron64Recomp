# NEXT work unit — audit `musyxStoreVoiceAdsrParams` voice-index class

HYPOTHESIS-ID: m3-idiom-class-audit

Session 3156 closed item -292's 43/43 `0x801529C0` reader inventory.

Session 3155 selected `H-M3-ValidProducer` for the complete `musyxStopVoice`
`+0x1` computed-record store: `s6` starts at zero, the call precedes its
increment, and both sole writers of the loop-count byte clamp it to at most
`0x20`, so the call argument is `0..31`.

## Single work unit

Audit the complete `musyxStoreVoiceAdsrParams` voice-indexed record/table class
in one static pass. Enumerate every generated caller, every indexed load/store
and its base/count producer, then reconcile with companion symbols/ELF when
available. Do not edit generated functions or add guards. No build or runtime
probe is authorized for this source-only discriminator.

Competing hypotheses and discriminator:

- `H-M3-Proven`: every reachable indexed access has a dominating producer and
  range proof for the 64-entry `0x88` voice array; this closes the class
  without a guard.
- `H-M3-Unclassified`: at least one reachable caller or indexed access lacks a
  complete base/index/count proof; this keeps the class open and authorizes no
  mitigation.
- `H-M3-LoweringOnly`: all apparent multiple sites collapse to duplicate
  delay-slot/shared-tail lowering, with no independent unsafe access.
- `H-M3-Dead`: all candidate callers/sites are unreachable or unreferenced in
  the generated dispatch graph.

The discriminating measurement is a complete site/caller/producer table. A
real reachable row with an unproved index or base selects
`H-M3-Unclassified`; all rows locally proven selects `H-M3-Proven`; only
duplicate/lowering rows selects `H-M3-LoweringOnly`; no reachable rows selects
`H-M3-Dead`. This is static evidence only and does not authorize audio or
voice behavior changes.

Exact starting commands:

```sh
rg -n 'musyxStoreVoiceAdsrParams|voice index|voice-index|0x88 voice' docs /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs | head -240
rg -n 'musyxStoreVoiceAdsrParams' /Users/williambuckley/Documents/Tools/rogue_squadron64 | head -120

Expected discriminator outcomes: a complete site table with all reachable
rows locally proven selects `H-M3-Proven`; any reachable row lacking a
producer/range proof selects `H-M3-Unclassified`; only duplicate/lowering
rows select `H-M3-LoweringOnly`. No runtime probe is valid unless a positive
control and a phase-scoped discriminator are first designed.
```
