# M3 s3604 — destructor unchecked-free class

## Work unit

Static census of every generated original `lw a0; jal rs_free` in
`shutdownAudioEngine` and `waitForMusyXAudioTaskDone` that has neither a
`beq a0, zero` skip nor a post-free NULL store, after the closed
`-0x6904` alias. The ten remaining pointers are `-0x68D8`, `-0x6644`,
`-0x6640`, `-0x68A8`, `-0x68A4`, `-0x689C`, and shutdown-only
`-0x6638`, `-0x663C`, `-0x6950`, `-0x69A0`. Classified every original
`sw` of each pointer (including `allocateSongChannelArray` and sibling
init stores) and whether a free can run on a non-allocator or
already-freed value. No build or runtime run was performed.

The discriminator was the single complete original census of those ten
`lw a0; jal rs_free` sites plus every original `sw` of each pointer:

- H-NextClassGap: a remaining unchecked free can pass a pointer that is
  not the matching allocator store, or can free it after a sibling
  destructor already released it without a NULL.
- H-NextClassComplete: every remaining unchecked free is a destructor of
  a matching `allocateSongChannelArray` (or sibling init) store, and
  only runtime allocator legitimacy remains.
- H-NextClassUnevaluable: mixed object identities or unshared writers
  prevent a complete classification of a pointer source.

Closed classes were not repeated: `-0x6904` alias, remaining-indexer,
`-0x6908` non-a0, release/fade, `+0x5C`/`+0x64`, `+0x66..+0x74`,
`+0x18..+0x24`, `+0x28..+0x2C`, `+0x30..+0x40`, `+0x60`, MORT
publication, mix-table, pan-input, hangar-Y.

## Census size

Original `lui 0x8015` `lw`/`sw`/`addiu` of the ten offsets across all
`RecompiledFuncs/funcs_*.c`. Hits in `funcs_30.c` / `funcs_32.c` use
`lui 0x8011` and are different objects.

| Pointer | BSS | Only original writer | Matching malloc | Destructors |
|---|---|---|---|---|
| `-0x68A8` | `0x80149758` | `allocateSongChannelArray` `sw $v0` `0x8008F228` | `0xA10 * lhu -0x68B2` | shutdown `0x80091E28`, wait `0x80091F78` |
| `-0x68A4` | `0x8014975C` | `allocateSongChannelArray` `sw $v0` `0x8008F264` | second `0xA10 * lhu -0x68B2` | shutdown `0x80091E38`, wait `0x80091F88` |
| `-0x689C` | `0x80149764` | `allocateSongChannelArray` `sw $a0` `0x8008F2C8` (`a0` = malloc `v0`) | `0x298`, then `rs_memset`/`osWritebackDCache` | shutdown `0x80091E58`, wait `0x80091FA8` |
| `-0x68D8` | `0x80149728` | `setupSongRenderBuffers` `sw $v0` `0x8008F478` | `0x18 * lhu -0x68E4` | shutdown `0x80091DD8`, wait `0x80091F48` |
| `-0x6640` | `0x801499C0` | `buildSongDecodeBufferRing` `sw $v0` `0x8008F690` | `0x14 * count` node array | shutdown `0x80091DF8`, wait `0x80091F68` |
| `-0x6644` | `0x801499BC` | `buildSongDecodeBufferRing` `sw $a0` `0x8008F6A4` (`a0` = malloc `v0`) | `count << 8` payload | shutdown `0x80091DE8`, wait `0x80091F58` |
| `-0x663C` | `0x801499C4` | `initSampleStreamBlockCache` `sw $a0` `0x8008F890` (`a0` = malloc `v0`) | `count * 0x600` payload | shutdown-only `0x80091E18` |
| `-0x6638` | `0x801499C8` | `initSampleStreamBlockCache` `sw $v1` `0x8008F8C0` (`v1` = malloc `v0`) | `count * 0x18` node array | shutdown-only `0x80091E08` |
| `-0x6950` | `0x801496B0` | `runAiAudioStreamPlaybackLoop` `sw $v0, 0($v1)` after `lui/addiu -0x6950` at `0x8008EDA4` | `0x3000`; word 0 of a 16-entry `0x300`-stride slice table | shutdown-only `0x80091E84` |
| `-0x69A0` | `0x80149660` | `initAudioSubsystem` `sw $v0` `0x80091BE8` | `0x400` thread stack | shutdown-only `0x80091E94` |

No other original `0x8015` store of any of the ten words exists.

## Remaining functions

### `allocateSongChannelArray` (`0x8008F0A0`) — three of the ten stores

Incoming `a0` is the slot count. After the closed `-0x6904`/`-0x6908`
voice-table malloc, two equal-size `rs_malloc` results (`0xA10` times
the live `lhu -0x68B2`) are stored at `-0x68A8` then `-0x68A4`. A
later `rs_malloc(0x298)` is copied to `a0` and stored at `-0x689C`,
then zero-filled and written back. There is no malloc-failure check
before any of those stores; that is the same unproven
allocator-legitimacy edge s3602/s3603 left open, not a second pointer
source. The sibling stores at `-0x68F8`/`-0x68F4` are outside this
class (neither destructor frees them).

The only generated caller is `initN64RspMixer` (`0x80091934`), which
clamps `a1` to `<= 0x20` before passing it as `a0`. Its callers are
`initAudioSubsystem` and `reapplyAudioConfig`.

### `setupSongRenderBuffers` (`0x8008F2FC`) — `-0x68D8`

Computes a count into `-0x68E4`, mallocs `0x18 * that count`, and
stores `v0` at `-0x68D8`. Then creates a mesg queue and calls
`buildSongDecodeBufferRing` plus `initSampleStreamBlockCache`. The
only generated caller is `initN64RspMixer` (`0x80091944`). Live
consumers of the stored pointer (`acquireSampleStreamBlock`,
`fillSampleStreamRange`, `musyxSynthFrame`) load it as a table base;
none store a replacement.

### `buildSongDecodeBufferRing` (`0x8008F65C`) — `-0x6640` / `-0x6644`

Incoming `a0` is the count from `lhu -0x68E4`. First malloc
(`count * 0x14`) is stored at `-0x6640`; second (`count << 8`) is
stored at `-0x6644`. The init walk is `slt` count-bounded, links
`0x14`-byte nodes, and writes payload pointers at `+0x8` from the
second allocation. The only generated caller is
`setupSongRenderBuffers`.

### `initSampleStreamBlockCache` (`0x8008F858`) — shutdown-only `-0x663C` / `-0x6638`

Incoming `a0` is a derived count. First malloc (`count * 0x600`) is
stored at `-0x663C`; second (`count * 0x18`) is stored at `-0x6638`
and also copied to the cursor word `-0x6634`. The init walk is `slt`
count-bounded. Recycle/fill mutate `-0x6634` by walking `node+0x0`;
they do not store to `-0x6638`. Shutdown frees the original malloc
base at `-0x6638`, not the cursor. The only generated caller is
`setupSongRenderBuffers`.

### `initAudioSubsystem` (`0x80091B3C`) — shutdown-only `-0x69A0`

`rs_malloc(0x400)` is stored at `-0x69A0` and passed as the stack of
`osCreateThread` whose entry is `0x8008ED70`
(`runAiAudioStreamPlaybackLoop`). The only generated caller is
`setDisplayMode`.

### `runAiAudioStreamPlaybackLoop` (`0x8008ED70`) — shutdown-only `-0x6950`

No generated C JAL; the function is only the audio thread entry.
`rs_malloc(0x3000)` is stored at word 0 of the static 16-word table
at `0x801496B0` (`lui 0x8015; addiu -0x6950; sw $v0, 0($v1)`). The
next 15 words are `base + n*0x300` slices. Shutdown loads word 0 and
frees that malloc. `musyxSynthFrame` forms the same table address in
`$s5` and only does `sll 2; addu $s5; lw 0($v0)` before
`musyxMixActiveVoices`; it does not store a new pointer into word 0.

### `shutdownAudioEngine` (`0x80091D40`) / `waitForMusyXAudioTaskDone` (`0x80091EB0`)

Both early-out when B40 at `0x800A0F50` is zero. Shared unchecked
frees: `-0x68D8`, `-0x6644`, `-0x6640`, `-0x68A8`, `-0x68A4`,
`-0x6904` (closed s3603), `-0x689C`. Shutdown additionally frees
`-0x6638`, `-0x663C`, `-0x6950`, `-0x69A0`. Neither destructor
NULLs any of the ten words. The skipped frees of `-0x6898` (with
NULL store) and `-0x6890` are outside this class.

Shutdown's only generated JAL is `shutdownMusyXEngine`
(`0x8008ECA4`), which itself has no generated JAL. Wait's only
generated JAL is `musyxNoopStub` from `runVideoFrameTick`. Both the
wrapper and the inner check B40; the wrapper stores zero to B40
after the inner returns, so a later sequential entry of either
destructor skips.

## Sibling-free edge

The six shared pointers are freed by both destructors and neither
NULLs them. Sequential double-free on the generated call graph is
blocked: shutdown's wrapper is unreferenced, and wait's wrapper
zeros B40 so a later wait/shutdown pair skips. That is not a
concrete stale-free of a non-allocator pointer. Concurrent re-entry
and the runtime value of B40 on the validated route remain unproven,
matching s3603.

The four shutdown-only pointers are not on the live wait path.
`reapplyAudioConfig` re-calls `initN64RspMixer` without a preceding
free, so a second constructor can overwrite the six shared words
with new malloc results; a later destructor would free the latest
stored pointer, not a non-allocator value. That overwrite is a leak
on reconfig, not a Gap in this class.

Live consumers (`musyxBuildVoiceCommandList` of `-0x68A8`/`-0x689C`,
`fillSampleStreamRange`/`acquireSampleStreamBlock`/`musyxSynthFrame`
of `-0x68D8`, mix of the `-0x6950` slices) continue to load those
words; their lifetime versus either free remains the unproven
allocator/lifetime boundary s3602 already parked.

## Result

`H-NextClassComplete` is selected. Every original store of the ten
pointers is the matching `rs_malloc` result (or the same `v0` copied
to `a0`/`v1` in the delay-slot store), and every remaining unchecked
`lw a0; jal rs_free` in the two destructors passes that same word.
`H-NextClassGap` is not selected: no untrusted load and no concrete
sibling-free of a non-allocator pointer. `H-NextClassUnevaluable` is
not selected: `-0x6950` is a static slice table whose word 0 is the
malloc pointer, not a mixed object, and the other nine words are
plain BSS pointer slots.

This is static evidence. Runtime allocator state, B40 on the
validated route, `reapplyAudioConfig` overwrite, and live contents
after either free remain unproven, matching s3586–s3603. No guard or
runtime change is authorized.

ORIGIN: writers are `allocateSongChannelArray` (`-0x68A8`, `-0x68A4`,
`-0x689C`), `setupSongRenderBuffers` (`-0x68D8`),
`buildSongDecodeBufferRing` (`-0x6640`, `-0x6644`),
`initSampleStreamBlockCache` (`-0x663C`, `-0x6638`),
`runAiAudioStreamPlaybackLoop` (`-0x6950` word 0), and
`initAudioSubsystem` (`-0x69A0`); each stores the matching
`rs_malloc` result. No mitigation was added.
