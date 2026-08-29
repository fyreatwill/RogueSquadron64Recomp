# Session 3237 M3 census — MusyX pointer globals

## Competing hypotheses

- `H-NewClass`: an unresolved repeated unsafe-access idiom remains in active audio paths.
- `H-ClosedClasses`: all repeated pointer idioms are covered by the existing voice-array census.
- `H-GuardOnly`: remaining matches are proven scalar/configuration accesses or isolated readers.

The census used `rg` over `src`, `patches`, `tools`, and the generated
`../N64Recomp/RecompiledFuncs/funcs_*.c` tree. No build or runtime run was
appropriate for this static unit.

## Result: H-NewClass

The repeated unguarded pointer class is the MusyX globals `0x80149758`
(`-0x68A8`) and `0x80149750` (`-0x68B0`). They are distinct from the already
audited voice-array base `0x801496F8` (`-0x6908`).

Writers:

- `allocateSongChannelArray` at `0x8008F228` writes `-0x68A8` after `rs_malloc`.
- `musyxBuildVoiceCommandList` at `0x80091074` writes `-0x68B0` from the
  `-0x68A8` allocation result.

Generated reader sites, grouped by function:

- `musyxKeyOnVoice`: `funcs_24.c:3909` reads `-0x68B0`.
- `musyxBuildVoiceCommandList`: `funcs_24.c:5174` reads `-0x68A8`;
  `5246`, `5308`, and `5439` read `-0x68B0`.
- `musyxSynthFrame`: `funcs_24.c:6532` reads `-0x68B0`.
- `shutdownAudioEngine`: `funcs_24.c:7935` reads `-0x68A8`.
- `waitForMusyXAudioTaskDone`: `funcs_24.c:8232` reads `-0x68A8`.
- Additional generated `-0x68B0` address arithmetic occurs at
  `funcs_13.c:21801,22738,22793,22874` and `funcs_45.c:1781`; these require
  caller-context classification before being merged into the class.

The prior `AUDIO_VOICE_BASEPTR_ENTRY_GUARD` and loop guards cover only
`-0x6908`; no corresponding `-0x68A8`/`-0x68B0` guard was found. The writers
look legitimate by static shape (allocator result and derived publication),
but this census does not prove KSEG0 range, lifetime, or publication ordering.
No mitigation or guard is authorized yet.

The repeated `-0x6900`, `-0x68FE`, and `-0x68F0` matches are scalar count/index
state with initialization/publication in `allocateSongChannelArray` and
`musyxBuildVoiceCommandList`, not pointer dereferences. The `break 6/7` grep
produced no active generated-code matches.

## Next discriminator

Audit the complete `-0x68A8`/`-0x68B0` class: recover exact function/address
context for every site, identify writers, frees, aliases, and consumers, and
prove legitimate KSEG0 range plus publication ordering. One unresolved
consumer selects a patch-based guard work unit; complete proof closes the
class without behavior change.
