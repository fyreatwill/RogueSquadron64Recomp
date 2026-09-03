# M3 s3655 — processAssetLoadStep rs_free of 0x48($s0)

## Work unit

Static census of `processAssetLoadStep` `jal rs_free`
at `0x80003E7C` (`$a0` = `0x48($s0)` from
`lw $a0, 0x48($s0)` at `0x80003E78`).
Enumerated every original load/store of
that `0x48($s0)` (including the matching
allocator, every later store, whether the
caller holds the buffer, the post-free
`sw $zero, 0x48($s0)` at `0x80003E8C`,
and any sibling `jal rs_free` of the same
word or of adjacent slots on `$s0`) and
every `jal rs_free` that can receive that
pointer. Other loads were classified as
consumers or as a second free. No build
or runtime run was performed.

`$s0` is not a caller-held buffer. It is
the current event-queue slot
`D_80110D60 + (*0x80111240)*0x74`
(`lui 0x8011; addiu 0xD60`, stride
`*7<<2+1<<2` = `0x74`, eight slots).
`mainEventQueueWorker` computes the same
base in `$s5` and the same `$s0`. Type-2
enqueue in `pushEventToRingBuffer` uses
the write cursor `*0x80111244` into the
same table as `$a2`.

Absolute `0x80110DA8` (slot0+0x48) never
appears. The word is `0x48($s0)` /
`0x48($a2)`. Zero gp-relative aliases of
`D_80110D60`. Overlay integer
`lw`/`sw 0x48($s0)` sites live in other
functions whose `$s0` is not this table
(no `addiu 0xD60` outside `funcs_1.c`
except unrelated `funcs_7.c` immediates
and a `funcs_33.c` halfword store).

The discriminator was the single complete
original census of that `jal rs_free`
site plus every original `lw`/`sw`/`addu`
of `processAssetLoadStep` `0x48($s0)` that
can become this `$a0`, every original
`lw`/`sw` of the same slot field, and
every `jal rs_free` that can receive that
pointer. `mainEventQueueWorker`
`0x8000450C` is a second generated
`jal rs_free` of the same word and is in
this census. No overlay duplicate of
`processAssetLoadStep` / `0x80003D64`,
`mainEventQueueWorker` / `0x80004360`, or
`pushEventToRingBuffer` / `0x80003BCC`
exists as a second generated body.

- H-NextClassGap: a remaining free can pass a
  pointer that is not the matching allocator
  store, or can free it after a sibling already
  released it without a NULL.
- H-NextClassComplete: every remaining free is
  a destructor of a matching init store, and
  only runtime allocator legitimacy remains.
- H-NextClassUnevaluable: mixed object
  identities or unshared writers prevent a
  complete classification of a pointer source.

Closed classes were not repeated. Do not
land a skip-path NULL store for the s3636
overlay Gap unless this census identifies
that same writer as this `0x48($s0)`.

## Census size

Original `jal 0x80001C98` in `funcs_1.c`:
7 sites. This census covers the first two
(`0x80003E7C` and `0x8000450C`), which
share `0x48($s0)`. `funcs_3.c`,
`funcs_5.c`, and `funcs_0.c` have zero
sites. `funcs_2.c` / `funcs_4.c` /
`funcs_6.c` / `funcs_7.c` are exhausted.

`processAssetLoadStep` is
`0x80003D64`..`0x80004360`,
frame `-0x28`. One generated
`jal 0x80003D64`
(`mainEventQueueWorker` `0x800044F0`,
type-2 slot only). Zero
`LOOKUP_FUNC(0x80003D64)`. Zero
`lui`/`addiu` function-pointer
constructions of `0x80003D64`
(`funcs_15.c` `lwc1 -0x3D64($at)` is
unrelated). One overlay-table entry in
`section_3_text` (rom offset `0x4964`,
size `0x5FC`); not a second generated
body. Single `jr $ra` at `0x80004358`.

`mainEventQueueWorker` is
`0x80004360`..`0x800045E8`,
frame `-0x40`. Zero generated `jal`.
One `lui 0x8000; addiu 0x4360` at
`initDmaSlots` `0x800047BC` as
`registerServiceWorker(..., 0x80004360)`
then `startServiceWorker`; ID stored at
`*0x80110D54`. Zero
`LOOKUP_FUNC(0x80004360)`. One
overlay-table entry (rom offset `0x4F60`,
size `0x288`); not a second generated
body. One `RECOMP_FUNC`.

`pushEventToRingBuffer` is
`0x80003BCC`..`0x80003C98`. Two generated
`jal 0x80003BCC` (both inside
`mainEventQueueWorker`). Zero
`LOOKUP_FUNC`. One overlay-table entry
(rom offset `0x47CC`, size `0xCC`).

## `$s0` — event-queue slot

`$s0` is `D_80110D60 + idx*0x74`.
`processAssetLoadStep` loads idx from
`*0x80111240` (`lui 0x8011; 0x1240`) at
`0x80003D70` and sets `$s0` at
`0x80003DD4`. `mainEventQueueWorker`
uses the same formula at `0x8000445C`
with `$s5 = 0x80110D60`. The table is
eight BSS slots. Worker init zeros only
`0x1($slot)` (busy). Type-2 enqueue
zeros flags `0x8($slot)` and
`0x48($slot)`.

`$s1` is `*slot+0x4 + 0x18` (event
sub-struct). `$s2` is
`D_80110BC0 + event[0x18]*0x18` (16-entry
subscribe table). Neither is this
`0x48` word.

## `0x48($s0)` — staging / inflate input

| Site | PC | Op | Object | Value |
|---|---|---|---|---|
| type-2 init | `0x80003C88` | `sw $zero, 0x48($a2)` | slot+0x48 | NULL; `pushEventToRingBuffer` event type 2 |
| malloc 0x10 A | `0x80003EA0`/`0x80003EAC` | `jal rs_malloc(0x10, 9)`; `sw $v0` | slot+0x48 | live heap-pointer writer; `ori 0x8400` on flags |
| malloc 0x10 B | `0x80003F0C`/`0x80003F1C` | `jal rs_malloc(0x10, 9)`; `sw $v0` | slot+0x48 | live heap-pointer writer; same `ori 0x8400` |
| malloc 0x1000 | `0x80003FC4`/`0x80003FCC` | `jal rs_malloc(0x1000, 9)`; `sw $v0` | slot+0x48 | live heap-pointer writer; `ori 0x4000` |
| destructor A | `0x80003E78`/`0x80003E7C` | `lw $a0, 0x48`; `jal rs_free` | slot+0x48 | destructor of the 0x10 malloc (flag `0x400`) |
| post-free NULL | `0x80003E8C` | `sw $zero, 0x48($s0)` | slot+0x48 | NULL after destructor A; return 1 |
| destructor B | `0x80004508`/`0x8000450C` | `lw $a0, 0x48`; `jal rs_free` | slot+0x48 | destructor of leftover `0x48` when step returns 1 |

There is no `beq $v0, $zero` after any of
the three mallocs. Failed malloc stores 0
into `0x48`. `rs_free(0)` skips. That is
the same unproven allocator-failure edge
s3604–s3654 left open.

The 0x10 and 0x1000 mallocs are mutually
exclusive on one job: L_80003DFC vs
L_80003F88 is keyed off the event
(`0x8(event) == -1` or `0xC(event)` bit
2), not leftover slot flags. Flag `0x400`
is set only with the 0x10 malloc
(`ori 0x8400`). Flag `0x4000` is set only
with the 0x1000 malloc. Destructor A runs
only on L_80003DFC after DMA complete,
`0x70($s0) != 0`, and `0x400` set. The
inflate path (L_80003F88) never takes
destructor A; at `0x800040FC` it clears
`0x400` if it were set.

Destructor A always NULLs before return
1. Destructor B then `rs_free(0)`.
Destructor B with no prior A is the
inflate-complete return 1 at
`0x80004278` (`inflateEnd` then `$v0=1`)
or the `0x70==0` return 1, which never
malloc'd `0x48` this job (still NULL from
type-2 enqueue). B does not NULL; the
next type-2 enqueue writes 0 at
`0x80003C88` before the slot is busy
again. After B the worker stores
`sb $zero, 0x1($slot)` so the slot is not
re-stepped until enqueue. That is not a
second free of a live pointer.

Type 2 is the only dispatch to
`processAssetLoadStep` and to destructor
B (`beq $v1, 2, L_800044F0`). Types 0
and 1 do not load `0x48($s0)`.

`0x10($s0)` at `0x80004308` is a copy of
`0x48` into the in-slot `z_stream`
`next_in`. `inflateInit_` /
`inflate` / `inflateEnd` take
`$s0+0x10`. That interior is not
`jal rs_free`. Adjacent `0x4C`/`0x50`/
`0x54`/`0x58`/`0x5C` are DMA
src/remaining/step words, not heap.

### Consumers — DMA dest / memcpy src, not a second free

| Function | PC | Use after `lw 0x48` |
|---|---|---|
| `processAssetLoadStep` | `0x80003E6C` | `memcpy(0xC($s1), 0x48($s0), 1)` then destructor A |
| `processAssetLoadStep` | `0x80003EE4` | `submitDmaSlot` dest (`$a1`) after 0x10 malloc A |
| `processAssetLoadStep` | `0x800042AC` | `submitDmaSlot` dest (`$a1`) for 0x1000 feed |
| `processAssetLoadStep` | `0x800042F8` | copy into `0x10($s0)`; not `rs_free` |

None of those loads is a second
`jal rs_free`. Host
`rs64_m5_writer_parity` /
`rs64_probe_submit_gate_store` probes on
the stores are diagnostics, not original
skips.

`findManifestEntryByName` `sw size>>5,
0x48($s3)` at `0x80004948` is a different
object (manifest DMA slot). Remaining
`funcs_1.c` `jal rs_free` sites
(`0x8000490C`, `0x80004A0C`,
`0x80004A80`, `0x80005000`,
`0x80005268`) do not load this
`0x48($s0)`.

## Pairing

One slot table, three malloc sites of
`0x48` (two 0x10, one 0x1000, flags 9),
one type-2 init NULL, two destructors of
that word (in-step 0x10 free+NULL, caller
leftover free). There is no third
`jal rs_free` of this pointer. Same
unchecked-NULL destructor shape already
closed as Complete for
`unregisterServiceWorker` (s3654) and
`initSaveData` (s3653). Runtime allocator
legitimacy and whether every call's
malloc succeeds remain unproven.

The missing NULL after destructor B is
not the s3636 skip-path Gap: type-2
enqueue stores NULL before any malloc or
free, and B only runs after a return-1
from this step. s3636 freed words that
setup never stored.

## Classification

The only `jal rs_free` sites that can
receive this `0x48($s0)` are
`0x80003E7C` and `0x8000450C`. The only
live original heap-pointer writers of the
word are the flags-9 mallocs at
`0x80003EA0`, `0x80003F0C`, and
`0x80003FC4`. All other loads are
memcpy/DMA/`next_in` consumers or the
type-2 init NULL. Adjacent slot words
are not sibling frees. This selects
`H-NextClassComplete`. `H-NextClassGap`
is refuted at static scope.
`H-NextClassUnevaluable` is not
selected: one slot field, one table,
three malloc sites in one function, two
destructor sites of that field.

No guard was added. Runtime allocator
state remains unproven. The s3636 overlay
skip-path NULL store was not landed: this
`0x48($s0)` is not that writer.

## Next remaining `jal rs_free`

The next remaining original site is
`funcs_1.c` `findManifestEntryByName`
`0x8000490C` (`$a0` = `$s2` from
`addu $a0, $s2` at `0x80004900`). Five
sites remain in that file.
