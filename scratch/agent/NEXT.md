# NEXT work unit — bounded M3 audit of the next unresolved producer edge

HYPOTHESIS-ID: m3-idiom-audit

Session 3164 completed the `stopVoicesByHandle` handle producer table and
selected `H-HandleUnclassified`: all four callers use the same node `+0x8`,
but the sole identified writer copies unconstrained `$a3`; no allocator
dispatch edge was recovered. Evidence:
`scratch/agent/s3164_m3_stop_voices_handle_producer_audit.md`.

Session 3163 completed the `musyxTriggerVoiceAttack` site/producer table.
The tick producer is bounded to `0..31`; the streamed producer is the proven
`stopVoiceByKey` `0..31`/`-1` edge, but the local callee has no `<64` check.
Evidence: `scratch/agent/s3163_m3_musyx_trigger_voice_attack_audit.md`.

Session 3161 classified `musyxTriggerVoiceAttack` as
`H-M3-Unclassified`: the tick caller is proven within the 0x20 channel range,
but `startStreamedSampleVoice` receives `stopVoiceByKey`'s non-`-1` result
without a dominating `<64` proof. Do not add a guard from this classification.

## Single work unit

Audit the next unresolved NULL-plus-offset idiom-class inventory entry after
the completed voice/handle producer edges. Enumerate every site and all
reachable pointer producers in one static table. Do not add a guard or audio
change from an unclassified result.

Competing hypotheses and discriminator for the selected next class:

- `H-M3-Proven`: every reachable pointer producer proves the indexed access is
  valid.
- `H-M3-Unclassified`: at least one reachable producer lacks that proof; this
  is a contract classification, not proof of a retail-invalid value.
- `H-M3-Dead`: apparent sites are unreachable lowering artifacts.

The discriminating measurement is one complete site/producer table containing
guest PC, caller, pointer writer/construction, range checks, dispatch edges,
and independent companion symbol/ELF metadata. Every outcome selects one of
the three hypotheses.

Exact starting commands: select the next unresolved entry from the existing
M3 inventory, then run the complete generated call/access and companion-symbol
census in one batch. Do not build or run.

```sh
rg -n 'MEM_[A-Z]+\([^;]*0X[0-9A-F]+|MEM_[A-Z]+\([^;]*0x[0-9a-f]+' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_*.c
rg -n '<selected symbol>|<selected address>|<companion semantic name>' /Users/williambuckley/Documents/Tools/rogue_squadron64/symbol_files
```

Expected outcome: a complete table selects `H-M3-Proven`,
`H-M3-Unclassified`, or `H-M3-Dead`. No runtime probe or build is authorized
for this static audit.
