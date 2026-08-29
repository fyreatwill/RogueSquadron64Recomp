# Session 3139 — M5 retail boundary static census

Command:

```sh
rg -n 'pending|descriptor|osViSetMode|__osViSwapContext|VI_ORIGIN_REG' \
  /Users/williambuckley/Documents/Tools/rogue_squadron64 \
  syms docs --glob '!PORTING-STATE.md'
```

## Candidate table written before any build

| Candidate/source | Static status | Target-phase watch decision |
|---|---|---|
| `requestViFeatureChange` / pending word `0x80128E90` | Named 16-byte helper at `0x8001B7B8`; already rejected as a target publication edge by prior retail attribution | Repeated candidate; do not arm |
| `applyPendingViChanges` `0x8001B7F0` and `selectAndApplyViMode` `0x8001BB6C` | Named symbols and prior closed caller/helper ranges; no body/disassembly in the available source | Repeated candidate; do not arm |
| `osViSetMode` `0x800352D0` / `__osViSwapContext` `0x80035550` | Companion `INCLUDE_ASM` stubs; consumer/publication PCs already independently watched | Repeated candidate; do not arm |
| `VI_ORIGIN_REG` / origin publication `0x80035788` | Register-level label only; prior retail watch found it live in title/hangar and prior port parity stopped before it | Repeated candidate; do not arm |
| `advanceVideoFrame` `0x8001818C` / `runVideoFrameTick` `0x80001354` | Symbol comments describe the known caller chain; no new transition-capable instruction or restored body | No defensible new PC |
| `viMgrMain` `0x80034F38` / `__osViNext` `0x80039214` | `viMgrMain` is an `INCLUDE_ASM` stub; `__osViNext` is only a data symbol; no new writer/consumer edge | No defensible new PC |

## Result

The command produced only existing declarations, symbol records, comments,
and probes. The companion's relevant executable bodies remain
`INCLUDE_ASM`, and the matching generated-function snapshot/disassembly is
not present. This run cannot name a new retail instruction whose phase-keyed
watch would distinguish the route hypotheses. The positive-control watch
that would be required for any future oracle capture is whole-RDRAM writes,
with title `1024 @ 0x00790400` and hangar `512 @ 0x006AB400` as phase controls;
no watch was built or run in this iteration.

Selected hypothesis: `H-SourceInsufficient`.
