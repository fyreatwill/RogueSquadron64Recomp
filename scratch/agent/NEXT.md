# NEXT work unit — bounded M3 audit of `musyxTriggerVoiceAttack`

HYPOTHESIS-ID: m3-idiom-audit

Session 3160 exhausted the `0x800A0000..0x800B0000` generated-symbol lead:
all 14 remaining placeholders were ambiguous/static fragments or an explicit
companion fake. Do not rename them. Resume the M3 idiom queue.

## Single work unit

Audit every reachable `musyxTriggerVoiceAttack` voice-indexed record access in
the generated tree. Enumerate all callers, the computed base/index expression,
dominating range checks, and independent companion symbol or ELF evidence. Do
not add a guard or audio change from an unclassified result.

Competing hypotheses and discriminator:

- `H-M3-Proven`: every reachable index has a dominating producer/range proof.
- `H-M3-Unclassified`: at least one reachable index lacks a local proof; this
  is a contract classification, not proof of a retail-invalid value.
- `H-M3-Dead`: apparent sites are unreachable lowering artifacts or false
  splits, with the complete reachable class documented.

The discriminating measurement is one complete site table containing guest PC,
caller, base, index source, dominating range proof, and independent metadata.
Every possible outcome selects one of the three hypotheses above.

Exact starting commands:

```sh
rg -n 'musyxTriggerVoiceAttack' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_*.c /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs.h
rg -n 'musyxTriggerVoiceAttack' /Users/williambuckley/Documents/Tools/rogue_squadron64/symbol_files
```

Expected outcome: a complete static site table selects `H-M3-Proven`,
`H-M3-Unclassified`, or `H-M3-Dead`. No runtime probe or build is authorized
for this static audit.
