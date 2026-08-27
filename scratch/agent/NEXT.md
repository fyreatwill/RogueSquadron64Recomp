# NEXT work unit (s2689) — audit producers of the named AI buffer ring

HYPOTHESIS-ID: m5-cpu-mort-publication

## Work unit

Perform a bounded static audit of the named AI worker's buffer-ring producers:
trace `setupSongRenderBuffers`, `buildSongDecodeBufferRing`, and their direct
named callers, recording every destination and source used to populate the
sixteen `0x300`-byte buffers later submitted by `runAiAudioStreamPlaybackLoop`.
Do not repeat the renderer, mixer-table, filter, persistent-object, task-field,
shared-stack, DMA callback, update/renderer, mixer callback, or AI-submit-body
audits. Stop at unresolved indirect calls or pointers rather than inferring a
MORT join.

## Competing hypotheses and discriminator

- `H-ring-producer`: a named producer fills the AI ring from a legitimate
  rendered-voice or MORT-derived source, with ordering visible.
- `H-service-boundary`: a named setup/service boundary fills the ring, but its
  source or relation to rendered voice remains outside the audited caller.
- `H-unresolved-address`: ring producers remain unrelated to rendered voice or
  terminate at unresolved indirect state.

The discriminator is a complete producer/source/destination/order table for
both ring setup helpers and every direct named caller: each outcome must name
the writer, ring range, payload polarity, and ordering relation, or explicitly
show which field is absent.

## Ground-truth prerequisite

No runtime watch, build, or soak is authorized until the static table names a
ground-truth target.

## Exact commands

1. `rg -n -H 'setupSongRenderBuffers|buildSongDecodeBufferRing|runAiAudioStreamPlaybackLoop|serviceAudioOutputBuffers|0x801569B0|0x80156A' ../N64Recomp/RecompiledFuncs/funcs_*.c ../rogue_squadron64/symbol_files/main_overlay.txt`
2. Read bounded windows for each unique helper and direct named caller; follow only named calls or direct stores/copies.
3. Record the complete producer/source/destination/order table and selected hypothesis in the ledger.
