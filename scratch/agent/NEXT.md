# NEXT work unit — bounded M3 audit of the next unresolved voice-index producer

HYPOTHESIS-ID: m3-idiom-audit

Session 3161 classified `musyxTriggerVoiceAttack` as
`H-M3-Unclassified`: the tick caller is proven within the 0x20 channel range,
but `startStreamedSampleVoice` receives `stopVoiceByKey`'s non-`-1` result
without a dominating `<64` proof. Do not add a guard from this classification.

## Single work unit

Audit every reachable producer edge for `stopVoiceByKey`'s return value that
can feed the voice-indexed `0x88` record family. Enumerate all callers of
`stopVoiceByKey`, the `allocateSynthVoice` result flow, and independent
companion symbol/ELF evidence. Do not add a guard or audio change from an
unclassified result.

Competing hypotheses and discriminator:

- `H-M3-Proven`: every reachable producer proves `0..63`.
- `H-M3-Unclassified`: at least one reachable producer lacks that proof; this
  is a contract classification, not proof of a retail-invalid value.
- `H-M3-Dead`: apparent producer edges are unreachable lowering artifacts.

The discriminating measurement is one complete producer table containing
guest PC, caller, return source, rejection/range checks, and independent
metadata. Every outcome selects one of the three hypotheses.

Exact starting commands:

```sh
rg -n 'stopVoiceByKey|allocateSynthVoice' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_*.c /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs.h
rg -n 'stopVoiceByKey|allocateSynthVoice|801496F8|count:0x40' /Users/williambuckley/Documents/Tools/rogue_squadron64/symbol_files
```

Expected outcome: a complete producer table selects `H-M3-Proven`,
`H-M3-Unclassified`, or `H-M3-Dead`. No runtime probe or build is authorized
for this static audit.
