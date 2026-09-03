# M3 s3608 — remaining format-message rs_free class

## Work unit

Static census of every generated original `jal rs_free` in
`tickFormatMessageWorker` and `disposeFormatMsgQueueMember`. Remaining
frees after the closed speech-file class: the three
`tickFormatMessageWorker` frees and the two
`disposeFormatMsgQueueMember` frees. Classified every original `sw`
of each pointer and whether a free can run on a non-allocator or
already-freed value. No build or runtime run was performed.

The discriminator was the single complete original census of those
`jal rs_free` sites plus every original `sw` of each pointer:

- H-NextClassGap: a remaining free can pass a pointer that is not
  the matching allocator store, or can free it after a sibling
  already released it without a NULL.
- H-NextClassComplete: every remaining free is a destructor of a
  matching init store, and only runtime allocator legitimacy remains.
- H-NextClassUnevaluable: mixed object identities or unshared writers
  prevent a complete classification of a pointer source.

Closed classes were not repeated: speech-file `rs_free`, speech/cache
`rs_free`, destructor skipped-NULL, destructor unchecked-free,
`-0x6904` alias, remaining-indexer, `-0x6908` non-a0, release/fade,
`+0x5C`/`+0x64`, `+0x66..+0x74`, `+0x18..+0x24`, `+0x28..+0x2C`,
`+0x30..+0x40`, `+0x60`, MORT publication, mix-table, pan-input,
hangar-Y.

## Census size

Original `jal 0x80001C98` in `funcs_30.c`: nine sites. Five are this
class. The other four (`0x800B17C8` in `bridgeLoadShipBlueprints`,
`0x800B3244`/`0x800B32BC` in `loadNamedTextureDescriptor`,
`0x800B354C` in `allocTextRenderTarget`) are a later text-texture
class.

The glyph-buffer object is the stack struct passed as `a1` to
`buildFormatMessageGlyphBuffer`. Tick's locals at `$sp+0x28` and
dispose's `$s0` (`a1`) are that object. Field `+0x38` is tick
`0x60($sp)`; field `+0x3C` is tick `0x64($sp)`.

| Pointer | Slot | Original writers | Matching malloc | Destructors |
|---|---|---|---|---|
| glyph `+0x38` | stack `a1+0x38` | `buildFormatMessageGlyphBuffer` memset `0x800B2940` (`s2+0x38`, len `0x34`); then `sw $v0` `0x800B2A58` | `rs_malloc` `0x800B2A50` (size `(w*h*field4 + sign_adj)>>1`) | tick `0x800B37E4` (`lw 0x60($sp)`); dispose `0x800B3E94` (`lw 0x38($s0)`); no post-free NULL |
| glyph `+0x3C` | stack `a1+0x3C` | same memset (zeros `+0x3C`); `sw $v0` `0x800B2A74` only when `0x1C(element)&6` | `rs_malloc` `0x800B2A6C` (size `(w*h)/4`) | tick `0x800B37CC` and dispose `0x800B3E7C`, both behind the same `0x1C&6` skip; no post-free NULL |
| message `$s3` | heap 0x60 | `enqueueFormatMessage` `rs_malloc(0x60)` `0x800B3F4C`, then `rs_memset` 0x60 | that 0x60-byte service message | tick `0x800B3814` (`addu $a0, $s3`); delay-slot sets `a0` before the call |

Original `sw $v0, 0x38($s2)` / `sw $v0, 0x3C($s2)` in `funcs_30.c`
are only `0x800B2A58` / `0x800B2A74`. Hits in other `funcs_*.c` are
different PCs and different objects. Generated `MEM_W` stores match
those original `sw` list exactly. `rasterizeFormatMessageGlyphs`
only `lw`s `+0x38`/`+0x3C` as `buildDebrisMeshFromCells` sources.

`rs_free` itself `beq $s0, $zero` and returns, so a memset-zero
`+0x3C` that is never malloc'd cannot reach a free: both destructors
skip `+0x3C` when `0x1C&6 == 0`.

## Remaining functions

### `buildFormatMessageGlyphBuffer` (`0x800B2630`) — both glyph stores

`s1` is the format-text element (`a0`); `s2` is the output glyph
buffer (`a1`). There is no mid-function `jr $ra`; both the
`0x4(element+0x10) != 0` skip to `L_800B28D8` and the fall-through
reach the same tail.

`rs_memset(s2+0x38, 0, 0x34)` zeros `+0x38` through `+0x6B`. Then
`+0x38` is always replaced by `rs_malloc`. `+0x3C` is replaced only
when `0x1C($s1) & 6`; otherwise it stays zero and the matching
destructors skip it. Last writer before each free is therefore the
matching malloc, or (for skipped `+0x3C`) the memset zero.

`+0x6C`/`+0x70` are `loadJfifAsset` results destroyed by
`freeJfifDecodeState`, not `rs_free`. They are outside this class.

The three generated callers pass a stack glyph buffer as `a1`:

- `tickFormatMessageWorker` — `$sp+0x28`, element `0x14($s3)`
- `buildScaledFormatTextElement` — `$sp+0x10`, then dispose
- `processAndDisposeFormatMessage` — `$sp+0x10`, then dispose

### `tickFormatMessageWorker` (`0x800B3650`) — three frees

Infinite recv loop. `recvServiceMessage` of `0x0($s5)` (the worker
from `registerServiceWorker`) returns the sent payload into `$s3`.
The only generated `lw $a1, -0x37A8` send to that worker is
`enqueueFormatMessage` (`0x800B3F9C`), which always mallocs 0x60
first. `unregisterServiceWorker` destroys the worker thread and
frees the worker node, and does not send a sentinel payload.

After `buildFormatMessageGlyphBuffer`, if `0x8(element) != 0` the
glyph walk consumes `+0x38`/`+0x3C` via `buildDebrisMeshFromCells`.
Then: `0x1C(element)&6` frees `+0x3C` and the `+0x70` jfif state;
always frees `+0x38` and the `+0x6C` jfif state; sends a *stack*
reply at `$sp+0x10` (not `$s3`); `rs_free($s3)`; loops. The next
iteration rebuilds the same stack slots before the next free.

Tick never calls `disposeFormatMsgQueueMember`.

### `disposeFormatMsgQueueMember` (`0x800B3E5C`) — two frees

`a0` is the element (flags at `+0x1C`); `a1` (`$s0`) is the stack
glyph buffer. The `0x1C&6` skip still copies `$a1` into `$s0` in the
delay slot. Then: flags set frees `+0x3C` and `+0x70`; always frees
`+0x38` and `+0x6C`. Both generated callers
(`buildScaledFormatTextElement`, `processAndDisposeFormatMessage`)
build into `$sp+0x10` then dispose that same buffer. Neither enqueues
a message, so they do not share an object with tick's frees.

### `enqueueFormatMessage` (`0x800B3F24`) — message malloc

`rs_malloc(0x60)`, `rs_memset` 0x60, stores the caller-owned element
at `+0x14`, copies the format string at `+0x18`, stores the reply
dest at `+0x58` and the seq at `+0x5C`, then
`sendServiceMessage(..., dest=-0x37A8, a2=malloc)`. Tick frees that
same pointer after the reply send. `shutdownFormatMessageWorker` only
unregisters; it does not free in-flight messages (leak on shutdown,
not a double-free).

`sendServiceMessage` writes header fields at payload `+0x2/+0x4/+0x8`
and `osSendMesg`s the payload pointer itself; `recvServiceMessage`
returns that pointer from the worker node's `+0x1E8`. Those header
stores are interior to the 0x60 malloc.

## Double-free / non-allocator edges

Worker path and direct path allocate distinct stack glyph buffers.
`buildFormatMessageGlyphBuffer` stores the pixel mallocs only at
`s2+0x38/+0x3C`, not onto the element, so dispose cannot free tick's
heap pixel buffers (and tick cannot free dispose's). Sequential
double-free of one stack glyph is blocked: dispose returns; tick
rebuilds before the next free.

`$s3` is the enqueue 0x60 malloc. A NULL malloc is `rs_free`'s skip.
A non-malloc payload would require a second sender to `-0x37A8`;
none exists in the generated tree.

Re-init without shutdown, malloc-size zero, and allocator failure
are the same unproven runtime edges s3604–s3607 left open, not a
second pointer source.

This selects `H-NextClassComplete`. `H-NextClassGap` is refuted at
static scope. `H-NextClassUnevaluable` is not selected: the three
pointers are the stack glyph `+0x38`/`+0x3C` pair and the 0x60
message.
