# NEXT work unit (s2503) — identify the legitimate writer of the active AI buffers

HYPOTHESIS-ID: m5-ai-buffer-writer-provenance

## Single work unit

Run one exhaustive static census over the active generated tree and companion
symbol/decomp inputs for the heap-backed AI buffers rooted at `0x801496B0`.
Enumerate every store to the root, every store to its derived table entries,
and every producer of the `0x300`-byte buffers passed to
`osAiSetNextBuffer_recomp`. Do not use the superseded `0x801096B0` address.
No build, runtime fields, address remap, or behavior change.

## Competing hypotheses and discriminator

- `H-writer-generated`: an active generated game-side store produces the
  buffers or table entries consumed by the AI calls.
- `H-writer-host`: only host/runtime code produces the buffers observed by
  the consumers; no active generated producer exists.
- `H-writer-unresolved`: generated stores exist, but the static boundary does
  not prove which one produces the consumed buffers.

The discriminator is a complete producer-to-consumer table keyed by guest PC,
destination expression, and buffer pointer derivation. A joined generated
store selects `H-writer-generated`; an exhaustive zero-store result with only
host producers selects `H-writer-host`; otherwise select `H-writer-unresolved`.

## Exact commands

```sh
rg -n -- "801496B0|801496B[0-9A-F]+|0x6950|0x300|osAiSetNextBuffer_recomp" ../N64Recomp/RecompiledFuncs --glob 'funcs_*.c'
rg -n -i "801496B0|801496F8|AI buffer|audio buffer|queue_samples|osAiSetNextBuffer|runAiAudioStreamPlaybackLoop" ../N64Recomp/fixup_game_funcs.py ../N64Recomp ../rogue_squadron64 --glob '*.py' --glob '*.c' --glob '*.h' --glob '*.toml' --glob '*.txt' --glob '!RecompiledFuncs.s*/**' --glob '!scratch_batch*/**'
```

Record the producer-to-consumer table and conclusion in
`scratch/agent/s2503_m5_ai_buffer_writer_audit/audit.md`.
