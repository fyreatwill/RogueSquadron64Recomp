# NEXT work unit (s2501) — census the generated AI-ring writer

HYPOTHESIS-ID: m5-generated-ai-ring-writer

## Single work unit

Perform a bounded static census of every generated store whose effective
destination is the AI-ring/table root `0x801096B0` or its known derived slots.
Include direct constants, base-plus-offset stores, and callees reached from
the two AI consumers at `0x8008EE00` and `0x8008EE84`. Record guest PC, store
width, raw address expression, physical address/range class, enclosing
function, and whether the value is an image/task field or a PCM sample. Also
check the fixup source for any writer rewrite that changes this boundary. Do
not add runtime fields, enable stale instrumentation, or change behavior.

## Competing hypotheses and discriminator

- H-ring-direct: a generated store reaches the ring with a recoverable slot
  relation and a named enclosing writer.
- H-ring-callee: the ring is written by a named callee reached from the audio
  path, but not at the two AI callsites themselves.
- H-ring-unresolved: candidate stores exist but their effective destination or
  writer relation cannot be established from available sources.
- H-ring-absent: no generated store reaches the root or derived ring slots.

The discriminator is one complete generated-store/callee table. A recoverable
direct row selects H-ring-direct; a reachable named callee selects
H-ring-callee; complete absence selects H-ring-absent; any unresolved address
or call edge selects H-ring-unresolved.

## Exact commands

```sh
test -d ../N64Recomp/RecompiledFuncs; printf 'generated status=%s\n' "$?"
rg -n "0x801096B0|0x801096B4|0x6950|0x694C|osAiSetNextBuffer_recomp" ../N64Recomp/RecompiledFuncs --glob 'funcs_*.c'
rg -n "0x8008EE00|0x8008EE84|80029E80|AI ring|pcm.*ring|audio.*ring" ../N64Recomp/fixup_game_funcs.py ../N64Recomp --glob '*.py' --glob '*.c' --glob '*.h' --glob '*.toml' --glob '!RecompiledFuncs.s*/**'
```

Write the table and conclusion to
`scratch/agent/s2501_m5_ai_ring_writer_audit/audit.md`. No build is needed
unless the static census exposes a concrete missing caller or wrong kind.
