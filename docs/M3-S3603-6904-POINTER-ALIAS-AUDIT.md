# M3 s3603 — `-0x6904` voice-table pointer alias

## Work unit

Static census of every generated original access to
`lui 0x8015; lw/sw -0x6904` (the malloc alias of the `0x88` voice-table
pointer stored beside `-0x6908` at `D_801496F8`). Classified
`allocateSongChannelArray` (store + init walk), `shutdownAudioEngine`
(free at `0x80091E48`), and `waitForMusyXAudioTaskDone` (free at
`0x80091F98`), plus every generated JAL of `waitForMusyXAudioTaskDone`.
No build or runtime run was performed.

The discriminator was the single complete original `-0x6904` census:

- H-NextClassGap: a remaining `-0x6904` user can free or walk a pointer
  that is not the live `allocateSongChannelArray` result, or can use it
  after the sibling free.
- H-NextClassComplete: every remaining alias user is the allocator store,
  the count-bounded init walk, or a destructor of that same pointer, and
  only runtime allocator legitimacy remains.
- H-NextClassUnevaluable: aliases or mixed lifetimes prevent a complete
  object-level classification of the pointer source.

Closed classes were not repeated: remaining indexers, `-0x6908` non-a0,
release/fade, `+0x5C`/`+0x64`, `+0x66..+0x74`, `+0x18..+0x24`,
`+0x28..+0x2C`, `+0x30..+0x40`, `+0x60`, MORT publication, mix-table,
pan-input, hangar-Y.

## Census size

Original `lw`/`sw` of `-0x6904` across all `RecompiledFuncs/funcs_*.c`
(six sites, three functions; no hits outside `funcs_23.c` / `funcs_24.c`):

| Function | PC | Op | Role |
|---|---|---|---|
| `allocateSongChannelArray` | `0x8008F0E4` | `sw $v0` | Store malloc pointer (same `v0` as `-0x6908` at `0x8008F0EC`). |
| `allocateSongChannelArray` | `0x8008F11C`, `0x8008F138`, `0x8008F148` | `lw` | Count-bounded init walk. |
| `shutdownAudioEngine` | `0x80091E48` | `lw $a0` | `rs_free` of that pointer. |
| `waitForMusyXAudioTaskDone` | `0x80091F98` | `lw $a0` | `rs_free` of that pointer. |

No other original writer exists. Neither destructor stores zero to
`-0x6904` or `-0x6908` after the free. Patch sites that reverse-map
against `-0x6908` do not touch this alias.

## Remaining functions

### `allocateSongChannelArray` (`0x8008F0A0`) — store + count-bounded init

Incoming `a0` is the slot count, not a slot index. Size is
`(a0 & 0xFFFF) * 0x88` passed to `rs_malloc`. The same `v0` is stored at
`-0x6904` then `-0x6908`. The count is stored at `-0x6900` before the
malloc. The init loop walks `a1` from 0 while
`(a1 & 0xFFFF) < lhu -0x6900` and uses the `-0x6904` load as base,
writing `+0x0 = 0`, `+0x85 = 0`, `+0x84 = 0xFF`. Zero count skips the
walk. There is no malloc-failure check before the store or the walk;
that is the same unproven allocator-legitimacy edge s3602 left open, not
a second pointer source.

The only generated caller is `initN64RspMixer` (`0x80091934`), which
clamps `a1` to `<= 0x20` before passing it as `a0`. Its callers are
`initAudioSubsystem` and `reapplyAudioConfig`.

### `shutdownAudioEngine` (`0x80091D40`) — destructor of the same pointer

Original `-0x6904` load at `0x80091E48` is `a0` to `rs_free`. No
`beq a0, zero` skip and no post-free NULL of either alias. The function
early-outs when the B40 byte at `0x800A0F50` is zero. The only generated
JAL is `shutdownMusyXEngine` (`0x8008ECA4`), which itself has no
generated JAL and no stored address in `funcs_*.c`. After the inner
returns, that wrapper stores zero to B40. Shutdown also frees several
sibling buffers (`-0x68D8`, `-0x6644`, `-0x6640`, `-0x6638`, `-0x663C`,
`-0x68A8`, `-0x68A4`, `-0x689C`, `-0x6950`, `-0x69A0`); those pointers
are outside this class.

### `waitForMusyXAudioTaskDone` (`0x80091EB0`) — live destructor of the same pointer

Original `-0x6904` load at `0x80091F98` is the same `rs_free` of the
allocator pointer, again with no zero-skip and no post-free NULL. It
also early-outs on B40 == 0. Its free-list is the shutdown list minus
`-0x6638`, `-0x663C`, the `osSendMesg`, `-0x6950`, and `-0x69A0`.

The only generated JAL is `musyxNoopStub` (`0x8008ED00`) at
`0x8008ED14`. That wrapper is itself JAL'd unconditionally from
`runVideoFrameTick` (`0x80001388`). Both the wrapper and the inner
check B40; the wrapper stores zero to B40 after the inner returns, so a
later sequential entry of either destructor skips. Concurrent re-entry
and the runtime value of B40 on the validated route remain unproven.

## Sibling-free edge

The two destructors free the same stored pointer and neither NULLs the
alias. Sequential double-free on the generated call graph is blocked:
shutdown's wrapper is unreferenced, and wait's wrapper zeros B40 so a
later wait/shutdown pair skips. That is not a concrete stale-free of a
non-allocator pointer. Mix/synth continue to load the sibling
`-0x6908` word; their lifetime versus this free remains the unproven
allocator/lifetime boundary s3602 already parked. No `-0x6904` user
walks the pointer after the other free.

## Result

`H-NextClassComplete` is selected. Every original `-0x6904` user is the
allocator store, the count-bounded init walk of that just-stored
pointer, or a destructor of that same pointer. `H-NextClassGap` is not
selected: no untrusted load and no concrete sibling-free of a
non-allocator pointer. `H-NextClassUnevaluable` is not selected: the
word is the same malloc pointer stored at `-0x6908`, not a mixed object.

This is static evidence. Runtime allocator state, B40 on the validated
route, and live contents of `-0x6908` after either free remain unproven,
matching s3586–s3602. No guard or runtime change is authorized.

ORIGIN: the only writer is `allocateSongChannelArray` storing the
`rs_malloc` result; the init walk indexes that pointer by the live-count
halfword written in the same function; both frees pass that same word to
`rs_free`. No mitigation was added.
