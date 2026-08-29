# NEXT work unit — select and audit the next complete M3 idiom class

HYPOTHESIS-ID: m3-idiom-class-audit

Session 3155 selected `H-M3-ValidProducer` for the complete `musyxStopVoice`
`+0x1` computed-record store: `s6` starts at zero, the call precedes its
increment, and both sole writers of the loop-count byte clamp it to at most
`0x20`, so the call argument is `0..31`.

## Competing hypotheses and discriminator for the next unit

- `H-M3-Proven`: every site in the selected idiom has a local proof.
- `H-M3-Unclassified`: at least one reachable site lacks a proof.
- `H-M3-Dead`: every apparent site is unreachable or lowering-only.

The discriminator is a complete site table for one idiom class, including all
writers/control-flow edges needed by each site. A proof for every site closes
the class; any reachable unclassified edge selects `H-M3-Unclassified`; no
reachable site selects `H-M3-Dead`.

## Single work unit

Read the existing M3 audit inventory, choose its highest-priority still-open
complete NULL-plus-offset idiom, and audit every guest site and producer edge
in one pass. Reconcile with companion symbols/ELF when available. Do not edit
generated functions or add guards.

Exact starting commands:

```sh
rg -n -i 'NULL|plus.?offset|computed|idiom|M3' docs scratch/agent
rg -n 'MEM_[BHW]\([^)]*ctx->|MEM_[BHW]\([^)]*\+' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs | head -200
```
