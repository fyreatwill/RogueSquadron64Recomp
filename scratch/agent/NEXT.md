# NEXT work unit — bounded M3 audit of the unresolved handle producer edge

HYPOTHESIS-ID: m3-idiom-audit

Session 3163 completed the `musyxTriggerVoiceAttack` site/producer table.
The tick producer is bounded to `0..31`; the streamed producer is the proven
`stopVoiceByKey` `0..31`/`-1` edge, but the local callee has no `<64` check.
Evidence: `scratch/agent/s3163_m3_musyx_trigger_voice_attack_audit.md`.

Session 3161 classified `musyxTriggerVoiceAttack` as
`H-M3-Unclassified`: the tick caller is proven within the 0x20 channel range,
but `startStreamedSampleVoice` receives `stopVoiceByKey`'s non-`-1` result
without a dominating `<64` proof. Do not add a guard from this classification.

## Single work unit

Audit the unresolved `stopVoicesByHandle` handle producer edge. Enumerate every
reachable caller, every writer/allocator of the node `+0x8` handle field, and
the direct/indirect dispatch evidence in one static table. Do not add a guard
or audio change from an unclassified result.

Competing hypotheses and discriminator:

- `H-HandleProven`: every reachable producer proves a valid handle contract.
- `H-HandleUnclassified`: at least one reachable producer lacks that proof; this
  is a contract classification, not proof of a retail-invalid value.
- `H-HandleDead`: apparent producer edges are unreachable lowering artifacts.

The discriminating measurement is one complete site/producer table containing
guest PC, caller, field writer, handle construction/range checks, dispatch
edges, and independent companion symbol/ELF metadata. Every outcome selects
one of the three hypotheses.

Exact starting commands:

```sh
rg -n 'stopVoicesByHandle|allocVoiceHandleNode|resolveVoiceSlotByHandle|0x8\(' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_*.c /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs.h
rg -n 'stopVoicesByHandle|allocVoiceHandleNode|resolveVoiceSlotByHandle|handle list' /Users/williambuckley/Documents/Tools/rogue_squadron64/symbol_files
```

Expected outcome: a complete table selects `H-HandleProven`,
`H-HandleUnclassified`, or `H-HandleDead`. No runtime probe or build is authorized
for this static audit.
