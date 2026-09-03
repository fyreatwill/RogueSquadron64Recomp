# M3 s3602 — remaining `-0x6908` table-base users (non-a0)

## Work unit

Static census of every generated function that loads `lui 0x8015; lw -0x6908`
(the `0x88` voice-table base `D_801496F8`) but does **not** form
`D_801496F8 + a0*0x88` from incoming `a0`. The six remaining names from
s3601, plus every original `-0x6908` site in `funcs_23.c` / `funcs_24.c`,
were classified. No build or runtime run was performed.

The discriminator was the single complete remaining `-0x6908` non-a0 census:

- H-NextClassGap: a remaining base user can index the `0x88` table with an
  untrusted or sentinel value (not the live-count walk and not the malloc
  size).
- H-NextClassComplete: every remaining base user is a count-bounded walk, a
  table allocator, or a non-index load, and only runtime allocator
  legitimacy remains.
- H-NextClassUnevaluable: aliases or mixed layouts prevent a complete
  object-level classification of the offset source.

Closed classes were not repeated: remaining indexers, release/fade,
`+0x5C`/`+0x64`, `+0x66..+0x74`, `+0x18..+0x24`, `+0x28..+0x2C`,
`+0x30..+0x40`, `+0x60`, MORT publication, mix-table, pan-input, hangar-Y.

## Census size

Original `lw`/`sw` of `-0x6908` across all `RecompiledFuncs/funcs_*.c`:

| Function | PC | Op | Role |
|---|---|---|---|
| `allocateSongChannelArray` | `0x8008F0EC` | `sw` | Store malloc pointer. |
| `musyxMixActiveVoices` | `0x80090E78`, `0x80090EA0`, `0x80090EBC` | `lw` | Count-bounded `0x88` walk. |
| `musyxSynthFrame` | `0x800913BC` | `lw` | Count-bounded pointer walk. |
| `isAudioSlotActive` … `getVoiceUserField` | (s3600/s3601) | `lw` | Incoming-`a0` indexers; closed. |

All other `-0x6908` hits in `musyxRenderVoiceSamples`, `musyxKeyOnVoice`,
`shutdownAudioEngine`, and `tickAllAudioChannels` are diagnostic patches
that reverse-map a pointer against the table; they are not original loads.

The live-count halfword at `-0x6900` (`0x80149700`) has a single original
writer: `allocateSongChannelArray` `sh $s0` at `0x8008F0CC`. Mix and synth
only read it.

## Remaining functions

### `allocateSongChannelArray` (`0x8008F0A0`) — malloc size, not an indexer

Incoming `a0` is the slot count, not a slot index. Size is
`(a0 & 0xFFFF) * 0x88` (`sll 4 / addu / sll 3`) passed to `rs_malloc`.
The same pointer is stored at `-0x6908` and `-0x6904`. The count is stored
at `-0x6900`. The init loop walks `a1` from 0 while `a1 < lhu -0x6900` and
uses the `-0x6904` alias as base, writing `+0x0 = 0`, `+0x85 = 0`,
`+0x84 = 0xFF`.

The only generated caller is `initN64RspMixer` (`0x80091934`). That
function takes the count in `a1`, keeps it if `< 0x21`, otherwise clamps
to `0x20`, then passes it as `a0`. Its callers are `initAudioSubsystem`
and `reapplyAudioConfig`, which forward their own `a1`. Runtime value of
that incoming count is unproven; the generated clamp is a 32-slot cap,
not a proof that the caller is legitimate.

### `musyxMixActiveVoices` (`0x80090E04`) — live-count walk

Incoming `a0` is a mix destination (`s7`), not a slot index. `s0` starts
at 0. Each iteration:

1. `lw` base from `-0x6908`.
2. Forms `base + (s0 & 0xFFFF)*0x88`.
3. Reads `+0x85` (clear-if-set), `+0x84` (shift into a bitmask), `+0x0`
   (skip render when zero).
4. When `+0x0 != 0`, JALs `musyxRenderVoiceSamples` with `a0` equal to
   that slot pointer.
5. `addiu s0, 1`; continue while `(s0 & 0xFFFF) < lhu -0x6900`.

Zero count skips the walk (`beq a0, zero` on the first `-0x6900` load).
The later `+0x22` stores use the mix-table ping-pong at `-0x68F8`, not
this base (s3592/s3597). No sentinel or incoming-`a0` index.

Callers are three sites inside `musyxSynthFrame`
(`0x800914C8`, `0x80091588`, `0x8009163C`).

### `musyxSynthFrame` (`0x8009123C`) — live-count pointer walk

One original `-0x6908` load at `0x800913BC`. Bound is `lhu -0x6900`;
`blez` skips the walk. `a1` starts at 0, `a3` is that count, `a0` starts
as the base and advances `addiu $a0, $a0, 0x88` while `a1 < a3`. Per live
slot (`+0x0 != 0`) it reads `+0x8` (double) and `+0x10`, and writes
`+0x14` and `+0x10`. The walk index is the loop counter, not incoming
`a0`. No sentinel-as-index.

### `musyxRenderVoiceSamples` (`0x8008FFAC`) — non-index consumer

No original `-0x6908` load. `s1 = a0` is the voice-slot pointer already
formed by mix's count-bounded walk. The only generated JAL is mix
`0x80090F00`. Field accesses on that pointer (`+0x0..+0x8`, volume
halfwords `+0x18..+0x26`, cursor words `+0x34..+0x4C`, envelope `+0x5C`,
decode-mode `+0x6D`, `+0x84`) do not re-form an index from the table
base. Patch sites reverse-map `s1` against `-0x6908` for logging only.

### `musyxKeyOnVoice` (`0x80090A3C`) — not a voice-table indexer

No original `-0x6908` load. The only generated JAL is
`musyxBuildVoiceCommandList` `0x800910A8`, whose `a0` is
`D_80149708[pingpong^1] + i*0x88` with `i <` the matching `-0x68F0`
count (s3597 mix-table / command-list ping-pong). Key-on copies from
that mix-table slot into a command dest formed as
`(-0x68B0) + count*0xA10 + halfword[0]*0x50 + 0x10`, not
`D_801496F8 + idx*0x88`. Patch reverse-maps of that dest against
`-0x6908` are a different layout.

### `shutdownAudioEngine` (`0x80091D40`) — alias free, not an indexer

No original `-0x6908` load. Original destructor is `lw a0, -0x6904` then
`rs_free` at `0x80091E48`. `-0x6904` is the same malloc pointer stored
beside `-0x6908` in `allocateSongChannelArray`. The `-0x6908` read is a
lifecycle diagnostic comparing the two aliases. Caller is
`shutdownMusyXEngine` `0x80091D40`.

## Result

`H-NextClassComplete` is selected. Every remaining original `-0x6908`
user is a count-bounded walk versus `-0x6900`, the table allocator's
malloc size / pointer store, or a non-index load (render consumes mix's
already-formed pointer; key-on indexes the mix-table ping-pong; shutdown
frees the `-0x6904` alias). `H-NextClassGap` is not selected: no
untrusted or sentinel-as-index edge on this base. `H-NextClassUnevaluable`
is not selected: the `-0x6904` alias is the same malloc pointer, not a
mixed object identity.

This is static evidence. Runtime allocator state, the incoming init
count before the `<= 0x20` clamp, and live contents of `-0x6900` remain
unproven, matching s3586–s3601. No guard or runtime change is authorized.

The `-0x6904` alias is also loaded/freed by `waitForMusyXAudioTaskDone`
(`0x80091F98`). That function never touches `-0x6908` and is outside this
class.

ORIGIN: walk indices are the live-count halfword written only by
`allocateSongChannelArray` from the clamped init count; malloc size is
that same count times `0x88`; render's pointer is mix's
already-formed slot; key-on does not index this table; shutdown frees
the allocator alias. No mitigation was added.
