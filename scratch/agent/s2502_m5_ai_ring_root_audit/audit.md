# s2502 M5 AI-ring root identity audit

## Question and discriminator

The competing hypotheses were `H-root-typo` (the documented `0x801096B0`
root is mistaken for `0x801496B0`), `H-root-dual` (both are live objects),
and `H-root-unresolved` (the independent sources cannot identify either).
The discriminator was independent symbol/decomp ownership and address
evidence, not the runtime's own probes.

## Evidence table

| Source | Address/name | Establishes |
|---|---|---|
| `../rogue_squadron64/undefined_syms_auto.txt:1002` | `D_801496B0 = 0x801496B0` | The companion symbol inventory recognizes `0x801496B0` as data, with adjacent `0x801496xx` globals in the same audio-state region. |
| `../rogue_squadron64/symbol_files/main_overlay.txt:2648,2873` | `serviceAudioOutputBuffers = 0x8008ED6C`; `runAiAudioStreamPlaybackLoop = 0x8008ED70` | The companion names the exact routines that initialize and consume the active AI-buffer table. |
| `../N64Recomp/RecompiledFuncs/funcs_23.c:11260-11370` | `0x80150000 - 0x6950 = 0x801496B0` | The active generated loop allocates `0x3000` bytes, stores the allocation at this root, and initializes sixteen entries at four-byte strides, each advanced by `0x300`. |
| `../N64Recomp/RecompiledFuncs/funcs_23.c:11360,11455` | AI calls at `0x8008EE08` and `0x8008EE84` | Both `osAiSetNextBuffer_recomp` calls consume a pointer loaded from the root or one of its entries, with a `0x300` byte count. |
| `../rogue_squadron64/undefined_syms_auto.txt:26` | `D_801096B9 = 0x801096B9` | The companion inventory has a nearby data byte, but does not identify `0x801096B0` as a data root. |
| `../N64Recomp/RecompiledFuncs/funcs_49.c:1854-1857` | `0x801096B0` is `nop`; `0x801096B4` is `sd $ra,-1($ra)` | The active generated tree treats `0x801096B0` as instruction/code-region content in the mission overlay; the `0x801096B4` hit is unrelated malformed/generated code. |
| `../rogue_squadron64/symbol_files/mission_overlay.txt:331-338,552-558` | mission symbols/data around `0x80109620..0x80109730` | The companion map places `0x801096B0` among mission-overlay code and separately named data, not in the main-overlay AI table. |

## Conclusion

`H-root-typo` is selected at the address-identity boundary. Independent
symbol/decomp evidence identifies `D_801496B0` in the main-overlay audio
region, and the active generated loop independently constructs that address
and uses it as the sixteen-entry AI pointer table. The proposed `0x801096B0`
root is instruction content; only a nearby `D_801096B9` byte is listed.

This resolves the root identity only. It does not identify the writer of the
heap-backed `0x300` buffers or establish an image-stage-to-AI-buffer handoff.
No build, runtime change, address remap, mitigation, or writer attribution is
authorized by this audit.
