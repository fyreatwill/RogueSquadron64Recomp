# NEXT work unit (s2504) — identify the nonzero PCM payload writer

HYPOTHESIS-ID: m5-pcm-payload-writer-provenance

## Single work unit

Run one exhaustive static dataflow census over the active generated tree and
companion decomp inputs for writes into the heap-backed AI buffers rooted at
`0x801496B0`, after the known allocation/clear/layout boundary. Enumerate
callers and direct stores that can receive `D_801496B0[i]` or
`D_801496B0 + n*0x300`, and classify each as payload-producing, initialization,
or unrelated. Do not use the superseded `0x801096B0` address. No build, runtime
fields, address remap, or behavior change.

## Competing hypotheses and discriminator

- `H-payload-generated`: an active generated game-side path writes nonzero PCM
  payload into the allocated blocks.
- `H-payload-host`: only host/runtime code writes the nonzero payload observed
  by the AI consumers.
- `H-payload-unresolved`: candidate generated paths exist, but the static
  boundary cannot join one to the consumed buffers.

The discriminator is a complete producer-to-consumer table keyed by guest PC,
operation/callee, destination expression, and buffer-pointer derivation. A
joined non-initialization generated writer selects `H-payload-generated`; an
exhaustive generated zero-result with only host producers selects
`H-payload-host`; otherwise select `H-payload-unresolved`.

## Exact commands

```sh
rg -n --glob 'funcs_*.c' -- '801496B0|801496B[0-9A-F]+|0x300|osAiSetNextBuffer_recomp|rs_memset|memcpy|memmove' ../N64Recomp/RecompiledFuncs
rg -n -i --glob '*.py' --glob '*.c' --glob '*.h' --glob '*.toml' --glob '*.txt' --glob '!RecompiledFuncs.s*/**' --glob '!scratch_batch*/**' -- '801496B0|801496F8|PCM|sample|audio buffer|queue_samples|osAiSetNextBuffer|runAiAudioStreamPlaybackLoop|rs_memset|memcpy|memmove' ../N64Recomp/fixup_game_funcs.py ../N64Recomp ../rogue_squadron64
```

Record the payload producer-to-consumer table and conclusion in
`scratch/agent/s2504_m5_pcm_payload_writer_audit/audit.md`.
