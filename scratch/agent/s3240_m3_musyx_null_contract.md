# Session 3240 — MusyX null-consumer recovery contract

The bounded audit selected `H-NotPatchable`. The null allocation result is a
real invalid value, but the recovered consumer has no semantics-preserving
local skip contract.

`musyxBuildVoiceCommandList` receives the channel-array base in `a0` and the
voice count in `a1`. It loads the selected command-list pointer at
`0x80091060`, publishes it as the current head at `0x80091074`, and
immediately clears its first halfword at `0x80091078`. This dereference is
before the per-voice loop at `0x8009108C`.

The loop advances `s0` on both branches: inactive voices call
`musyxKeyOnVoice`; active voices append a command record and update list state.
Its exit is only `s0 < a1`; there is no error return or alternate head
publication. The caller at `0x80091330` continues after the call without
inspecting a result or providing array reinitialization.

`H-SkipVoice` is therefore rejected: the bad value is the selected command-list
pointer, not a voice node inside the loop. `H-ReinitArray` is not established:
the caller has no such branch, and no complete replacement preserving
allocator ownership and synth state was found. `H-NotPatchable` is selected.

This is static evidence only. No validated-route occurrence was claimed, and no
patch or global allocator change is authorized.

ORIGIN: `rs_malloc` at `0x80001C74` returns zero on no-fit;
`allocateSongChannelArray` publishes it at `0x8008F228`. Zero is not a
legitimate channel-array pointer. Teardown frees at `0x80091E28` and
`0x80091F78` remain a separate unresolved stale-after-free/concurrency risk.
