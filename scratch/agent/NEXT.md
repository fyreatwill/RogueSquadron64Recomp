# NEXT work unit (s2502) — resolve the AI-ring root address discrepancy

HYPOTHESIS-ID: m5-ai-ring-root-identity

## Single work unit

Resolve whether the documented AI-ring root `0x801096B0` is a typo for the
active generated loop's `0x801496B0`, or whether both are legitimate objects.
Use the companion symbol/decomp sources and the generated input/context files;
do not infer from runtime values. Record each source's symbol/address,
allocation/table initialization, and the two AI consumer arguments. No build,
runtime fields, stale instrumentation, address remap, or behavior change.

## Competing hypotheses and discriminator

- H-root-typo: independent source material names `0x801496B0` as the AI table.
- H-root-dual: independent source material proves `0x801096B0` is a separate
  live object as well as the generated `0x801496B0` table.
- H-root-unresolved: sources do not identify either address sufficiently.

The discriminator is an independent symbol/decomp address table: a source
naming `0x801496B0` as the AI table selects H-root-typo; proof of a second live
`0x801096B0` object selects H-root-dual; otherwise select H-root-unresolved.

## Exact commands

```sh
test -d ../N64Recomp/RecompiledFuncs; printf 'generated status=%s\n' "$?"
rg -n "0x801096B0|0x801096B4|0x6950|0x694C|osAiSetNextBuffer_recomp" ../N64Recomp/RecompiledFuncs --glob 'funcs_*.c'
rg -n "0x8008EE00|0x8008EE84|80029E80|AI ring|pcm.*ring|audio.*ring" ../N64Recomp/fixup_game_funcs.py ../N64Recomp --glob '*.py' --glob '*.c' --glob '*.h' --glob '*.toml' --glob '!RecompiledFuncs.s*/**'
```

Write the table and conclusion to
`scratch/agent/s2502_m5_ai_ring_root_audit/audit.md`. No build is needed.
