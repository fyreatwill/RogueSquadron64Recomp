# NEXT work unit — select and audit the next complete M3 idiom class

HYPOTHESIS-ID: m3-idiom-class-audit

Session 3156 closed item -292's 43/43 `0x801529C0` reader inventory.

Session 3155 selected `H-M3-ValidProducer` for the complete `musyxStopVoice`
`+0x1` computed-record store: `s6` starts at zero, the call precedes its
increment, and both sole writers of the loop-count byte clamp it to at most
`0x20`, so the call argument is `0..31`.

## Single work unit

Select the highest-priority still-open complete NULL-plus-offset idiom from
the existing M3 inventory, then enumerate every site and producer/control-flow
edge in one pass. Before any build, write the class-specific competing
hypotheses and discriminator here. Reconcile with companion symbols/ELF when
available. Do not edit generated functions or add guards.

Exact starting commands:

```sh
rg -n -i 'NULL|plus.?offset|computed|idiom|M3|NEEDS_GUARD' docs scratch/agent | head -240
rg -n 'MEM_[BHW]\([^)]*ctx->|MEM_[BHW]\([^)]*\+' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs | head -200

Expected discriminator outcomes: a complete site table with all reachable
rows locally proven selects `H-M3-Proven`; any reachable row lacking a
producer/range proof selects `H-M3-Unclassified`; only duplicate/lowering
rows select `H-M3-LoweringOnly`. No runtime probe is valid unless a positive
control and a phase-scoped discriminator are first designed.
```
