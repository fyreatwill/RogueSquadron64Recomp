# M3 s3605 — skipped-NULL destructor-free class

## Work unit

Static census of every generated original `lw; beq $zero; jal rs_free`
in `shutdownAudioEngine`, `waitForMusyXAudioTaskDone`,
`shutdownMusyXEngine`, and `musyxNoopStub`. Remaining skipped-NULL
destructor pointers after the closed unchecked class: `-0x6898` (also
stores zero before free), `-0x6890`, and wrapper `-0x50EC`. Classified
every original `sw` of each pointer and whether a free can run on a
non-allocator or already-freed value. No build or runtime run was
performed.

The discriminator was the single complete original census of those
`lw; beq $zero; jal rs_free` sites plus every original `sw` of each
pointer:

- H-NextClassGap: a remaining skipped free can pass a pointer that is
  not the matching allocator store, or can free it after a sibling
  destructor already released it without a NULL.
- H-NextClassComplete: every remaining skipped free is a destructor of
  a matching init store, and only runtime allocator legitimacy remains.
- H-NextClassUnevaluable: mixed object identities or unshared writers
  prevent a complete classification of a pointer source.

Closed classes were not repeated: destructor unchecked-free, `-0x6904`
alias, remaining-indexer, `-0x6908` non-a0, release/fade,
`+0x5C`/`+0x64`, `+0x66..+0x74`, `+0x18..+0x24`, `+0x28..+0x2C`,
`+0x30..+0x40`, `+0x60`, MORT publication, mix-table, pan-input,
hangar-Y.

## Census size

Original `lui 0x8015` `lw`/`sw` of `-0x6898`/`-0x6890` and original
`lui 0x8014` `lw`/`sw` of `-0x50EC` across all
`RecompiledFuncs/funcs_*.c`.

| Pointer | BSS | Original writers | Matching malloc | Destructors |
|---|---|---|---|---|
| `-0x6898` | `0x80149768` | `buildSongTempoSchedule` `sw $s2` `0x8008F074`; zero: `initN64RspMixer` `0x8009198C`, shutdown `0x80091DA0`, wait `0x80091F10`, `freeAudioScratchBuffer` `0x80092548` | `rs_malloc(0x48)` at `0x8008EF38`; `$s2 = $v0` | shutdown `0x80091DA4`, wait `0x80091F14`, scratch `0x8009254C` — all `beq $v0, $zero` then `sw $zero` then `jal rs_free` with delay-slot `addu $a0, $zero, $zero` |
| `-0x6890` | `0x80149770` | `initN64RspMixer` `sw $v0` `0x800919BC`; zero: `initN64RspMixer` `0x800919CC` when `a2 == 0` | `rs_malloc(2 * (computed + 0xC0))` at `0x800919B0` | shutdown `0x80091DBC`, wait `0x80091F2C` — `lw $a0; beq $a0, $zero; jal rs_free` (passes the loaded word; no post-free NULL) |
| `-0x50EC` | `0x8013AF14` | none | none | wrapper `shutdownMusyXEngine` `0x8008ECD8`, wrapper `musyxNoopStub` `0x8008ED34` — `lw $v0; beq $v0, $zero; lw $a0; jal rs_free` |

No other original `0x8015` store of `-0x6898`/`-0x6890` exists. No
original `sw`, `addiu`, or `lui 0x8014` store of `-0x50EC` exists. No
`addiu -0x5100` forms a base that is then stored at `+0x14`.

## Remaining functions

### `buildSongTempoSchedule` (`0x8008EEC0`) — nonzero `-0x6898`

Early-out when `-0x6890` is NULL. `rs_malloc(0x48)` is copied to
`$s2`; word 0 of that object is the live `-0x6890` pointer, then the
`-0x6890` buffer is zero-filled for `s1 << 1` bytes using the same
tempo-rate formula as mixer init. After `factor5MutexAcquire`, `$s2`
is stored at `-0x6898`. The only generated caller is
`tickAudioBufferUpdate` (`0x80092518`), itself the only JAL from
`syncMusyXIfActive`. Live consumer `musyxBuildVoiceCommandList` loads
`-0x6898` as `$a1`; it does not store a replacement.

### `initN64RspMixer` (`0x8009189C`) — `-0x6890` and zero `-0x6898`

On the `a2 != 0` path it stores zero at `-0x6898`, computes a sample
count into `-0x688C`, mallocs twice that count, and stores `$v0` at
`-0x6890`. On `a2 == 0` it stores zero at `-0x6890` and does not
touch `-0x6898` on that arm. There is no malloc-failure check before
the store; that is the same unproven allocator-legitimacy edge
s3602–s3604 left open, not a second pointer source. Generated callers
are `initAudioSubsystem` and `reapplyAudioConfig`.

### `freeAudioScratchBuffer` (`0x80092530`) — sibling of `-0x6898`

Same original idiom as the two inner destructors: load `-0x6898`,
skip if NULL, store zero, `jal rs_free` with delay-slot `$a0 = 0`.
The only generated caller is `runMusyXTaskLocked`, which is B40-gated
and wraps the call in `factor5MutexAcquire`/`Release`.

### `shutdownAudioEngine` (`0x80091D40`) / `waitForMusyXAudioTaskDone` (`0x80091EB0`)

Both early-out when B40 at `0x800A0F50` is zero. Shared skipped
frees: `-0x6898` (NULL store, then free of delay-slot zero) and
`-0x6890` (free of the loaded word, no NULL). The remaining
unchecked frees were closed in s3604.

### Wrappers `shutdownMusyXEngine` (`0x8008ECA4`) / `musyxNoopStub` (`0x8008ED00`) — `-0x50EC`

Each checks B40, calls the matching inner destructor, then
`lw; beq $zero; jal rs_free` of `-0x50EC` (`0x8013AF14`), then
`noopHandler_80099C44`, then stores zero to B40. Neither NULLs
`-0x50EC`. `shutdownMusyXEngine` has no generated JAL.
`musyxNoopStub` is the only generated JAL from `runVideoFrameTick`.

The word at `0x8013AF14` sits next to the voice-handle / sorted-table
heads at `-0x5100`/`-0x50FC`/`-0x50F8`/`-0x50F4`
(`0x8013AF00..0x8013AF0C`). Those four words have identified writers.
`-0x50F0` and `-0x50EC` have no original store. The skipped wrapper
free therefore runs only if BSS is already nonzero; the generated
tree never writes it.

## Sibling-free edge

`-0x6898` is NULLed before every free site, and every free site
passes delay-slot `$a0 = 0` rather than the loaded malloc pointer.
That is original MIPS, not a recompiler artifact. The `0x48` header
is leaked; `rs_free` is not given a non-allocator pointer. A later
sibling sees the NULL and skips.

`-0x6890` is freed by both inner destructors and neither NULLs it.
Sequential double-free on the generated call graph is blocked:
shutdown's wrapper is unreferenced, and wait's wrapper zeros B40 so a
later wait/shutdown pair skips. That is not a concrete stale-free of
a non-allocator pointer. Concurrent re-entry and the runtime value of
B40 on the validated route remain unproven, matching s3603/s3604.

`reapplyAudioConfig` re-calls `initN64RspMixer` without a preceding
free, so a second constructor can overwrite `-0x6890` with a new
malloc result (or zero). A later destructor would free the latest
stored pointer, not a non-allocator value. That overwrite is a leak
on reconfig, not a Gap in this class.

Live consumers (`musyxBuildVoiceCommandList` of `-0x6898`,
`buildSongTempoSchedule` of `-0x6890`) continue to load those words;
their lifetime versus either free remains the unproven
allocator/lifetime boundary s3602 already parked.

## Result

`H-NextClassComplete` is selected. `-0x6898` is the matching
`rs_malloc(0x48)` store; its skipped frees NULL the slot and pass
delay-slot zero. `-0x6890` is the matching `initN64RspMixer` malloc
store, and both inner destructors free that same word after a NULL
skip. `-0x50EC` has no original writer, so the wrapper skip is of
BSS zero. `H-NextClassGap` is not selected: no untrusted load and no
concrete sibling-free of a non-allocator pointer. The delay-slot
`$a0 = 0` is an original leak of the `0x48` header, not a Gap.
`H-NextClassUnevaluable` is not selected: `-0x50EC` is a never-stored
BSS word, not a mixed object, and the other two words are plain BSS
pointer slots with a single nonzero malloc writer each.

This is static evidence. Runtime allocator state, B40 on the
validated route, `reapplyAudioConfig` overwrite, and live contents
after either free remain unproven, matching s3586–s3604. No guard or
runtime change is authorized.

ORIGIN: writers are `buildSongTempoSchedule` (`-0x6898` nonzero
`rs_malloc(0x48)`), `initN64RspMixer` (`-0x6890` malloc or zero, and
zero of `-0x6898`), plus destructor/scratch NULL stores of
`-0x6898`. `-0x50EC` has no original writer. No mitigation was
added.
