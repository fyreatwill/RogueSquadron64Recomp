# M3 s3654 — unregisterServiceWorker rs_free of $s0

## Work unit

Static census of `unregisterServiceWorker` `jal rs_free`
at `0x80007128` (`$a0` = `$s0` from
`addu $a0, $s0` at `0x8000712C`).
Enumerated every original load/store of
that `$s0` (including the matching
allocator, the list-head word
`*0x801128D0` / `lui 0x8011; lw 0x28D0`,
every later store, whether the caller
holds the node, and any sibling
`jal rs_free` of the same node or of
`0x18($s0)` / `0x20($s0)`) and every
`jal rs_free` that can receive that
pointer. Other loads were classified as
consumers or as a second free. No build
or runtime run was performed.

Absolute `0x801128D0` never appears in
generated code. The word is
`lui 0x8011; 0x28D0`. Zero gp-relative
`-0xD730` aliases. `funcs_19.c`
`addiu -0x28D0` is `lui 0x8004` then
`0x8003D730`, a jump table, not this
word.

The discriminator was the single complete
original census of that `jal rs_free`
site plus every original `lw`/`sw`/`addu`
of `unregisterServiceWorker` `$s0` that
can become this `$a0`, every original
`lw`/`sw` of `*0x801128D0`, and every
`jal rs_free` that can receive that
pointer. No overlay duplicate of
`unregisterServiceWorker` / `0x800070BC`
or `registerServiceWorker` / `0x80006C28`
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
that same writer as this `$s0`.

## Census size

Original `jal 0x80001C98` in `funcs_2.c`:
4 sites. This census covers the last
remaining one (`0x80007128`).
`funcs_3.c`, `funcs_5.c`, and `funcs_0.c`
have zero sites. `funcs_1.c` has 7 sites,
not in this unit.

`unregisterServiceWorker` is
`0x800070BC`..`0x80007144`,
frame `-0x20`. Six generated
`jal 0x800070BC`
(`teardownAssetManifestService`
`0x80004FE8`, `teardownGridLayerWorker`
`0x800495D0`, `setUnlockBitAndPersist`
`0x8006E3CC`, `stopSaveServiceWorker`
`0x8006EFFC`, `shutdownFormatMessageWorker`
`0x800B3F10`, `shutdownSongAssetLoadWorker`
`0x800C5820`). Zero
`LOOKUP_FUNC(0x800070BC)`. Zero
`lui`/`addiu` function-pointer
constructions of `0x800070BC`. One
overlay-table entry in
`section_3_text` (rom offset `0x6C7C`,
size `0x8C`); not a second generated
body. Single `jr $ra` at `0x80007140`.

`registerServiceWorker` is
`0x80006C28`..`0x80006D98`,
frame `-0x38`. Seven generated
`jal 0x80006C28`. Zero
`LOOKUP_FUNC(0x80006C28)`. One
overlay-table entry (rom offset `0x67E8`,
size `0x174`); not a second generated
body. One `RECOMP_FUNC`.

## `$s0` — service-worker node

`$s0` is loaded from `*0x801128D0` and
walked via `0x18($s0)` until
`0x0($s0) == $a0` (the service ID). It is
not a caller-held buffer.

| Site | PC | Op | Object | Value |
|---|---|---|---|---|
| malloc | `0x80006C78`/`0x80006C88` | `jal rs_malloc(size, 0x81)`; `addu $s5, $v0` | node | live heap-pointer writer |
| next-init | `0x80006CD4` | `sw $zero, 0x18($s5)` | `0x18(node)` | next-link = NULL; not a nested malloc |
| interiors | `0x80006CB8`..`0x80006CC8` | `sw` of stack-end / `$s5+0x1F0` into `0x8`/`0x1C` | same allocation | interior consumers |
| ID store | `0x80006CEC` | `sw ++*0x801128D4, 0x0($s5)` | `0x0(node)` | published ID; callers pass this, not the node |
| empty-head | `0x80006D50` | `sw $s5, 0x28D0` | `*0x801128D0` | publishes malloc result as list head |
| append | `0x80006D5C`/`0x80006D70` | `sw $s5, 0x18($v1)` | `0x18(tail)` | publishes malloc result as next |
| destroy | `0x800070FC` | `jal osDestroyThread`; `$a0 = $s0+0x20` | `0x20($s0)` | interior OSThread; not `rs_free` |
| unlink-head | `0x8000711C` | `sw 0x18($s0), 0x28D0` | `*0x801128D0` | successor or NULL; not a new allocation |
| unlink-mid | `0x80007124` | `sw 0x18($s0), 0x18($s1)` | `0x18(prev)` | successor or NULL |
| destructor | `0x80007128`/`0x8000712C` | `addu $a0, $s0`; `jal rs_free` | `$s0` | destructor of the matching malloc |

Malloc size is
`((($s1+0x20)&~7)+0x1F0)+(($s2&0xFFFF)<<2)`.
There is no `beq $v0, $zero` after the
malloc. Failed malloc leaves `$s5 == 0`
and still writes through it; empty-list
insert then stores 0 onto a head that
`initServiceRegistry` already zeroed.
`rs_free(0)` skips. That is the same
unproven allocator-failure edge
s3604–s3653 left open.

The ID-miss / empty-list fallthrough
still reaches `osDestroyThread($s0+0x20)`
and `rs_free($s0)` with `$s0 == 0`. That
is the same unchecked-NULL destructor
shape already closed as Complete. It
does not pass a live non-allocator
pointer.

`0x18($s0)` is only the next-link
(initialized 0, then `$s5`, then
successor-on-unlink). `0x20($s0)` is the
in-allocation `OSThread` passed to
`osCreateThread` / `osDestroyThread`.
Neither is a sibling `jal rs_free`.

Callers pass the ID in `$a0`, not the
node. `teardownAssetManifestService`
then `rs_free(*0x80110D50)` is a
different object (remaining `funcs_1.c`
site `0x80005000`).
`teardownGridLayerWorker`
`rs_free(*0x80137614)` was closed s3641;
its unregister arg is `*0x80137A40`, the
ID word, not that buffer.
`stopSaveServiceWorker` skips the
unregister when the ID word is `-1`.

A second unregister of the same ID walks
an already-unlinked list, misses, and
`rs_free(0)`. That is not a second free
of the node.

## `*0x801128D0` — list head

19 original `lui 0x8011` `0x28D0` sites,
all in `funcs_2.c`. Three stores.

| Site | PC | Op | Object | Value |
|---|---|---|---|---|
| init | `0x80006C04` | `sw $zero, 0x28D0` | `*0x801128D0` | NULL; `initServiceRegistry` |
| malloc-head | `0x80006D50` | `sw $s5, 0x28D0` | `*0x801128D0` | live heap-pointer writer |
| unlink-head | `0x8000711C` | `sw 0x18($s0), 0x28D0` | `*0x801128D0` | successor or NULL |
| 16 other loads | see consumers | `lw 0x28D0` | `*0x801128D0` | list-head walk; none `jal rs_free` of this pointer |

`initServiceRegistry` also zeros
`*0x801128D4` (ID counter) and
`*0x801128D8` (message serial). Those
are not heap pointers. One generated
caller (`0x800011C8` in `funcs_0.c`).

### Consumers — ID walks, not a second free

| Function | PC | Use after `lw 0x28D0` |
|---|---|---|
| `registerServiceWorker` | `0x80006D40` | empty-vs-append test |
| `startServiceWorker` | `0x80006DA4` | walk by ID; `osStartThread($a0+0x20)` |
| `checkServiceWorkerStackGuard` | `0x80006DF0` | walk by ID; compare `CDCDCDCD` at `0xC` |
| `peekServiceMessage` | `0x80006E4C` | walk by ID; `osRecvMesg` of `+0x1D0` |
| `tryRecvServiceMessage` | `0x80006ED0` | walk by ID; nonblocking recv |
| `recvServiceMessage` | `0x80006F30` | walk by ID; blocking recv |
| `sendServiceMessage` | `0x80006F84`/`0x80006FB8` | two ID walks; `osSendMesg` of `+0x1D0` |
| `postMessageToServiceWorker` | `0x80007078` | walk by ID; `osSendMesg` |
| `unregisterServiceWorker` | `0x800070C8`/`0x80007108` | destructor walk and head compare |
| `sendServiceMessageAwaitReply` | `0x80007154`/`0x8000718C` | two ID walks; send then recv |
| `setServiceWorkerPriority` | `0x80007264` | walk by ID; `osSetThreadPri($a0+0x20)` |
| `stopServiceWorker` | `0x800072D4` | walk by ID; `osStopThread($a0+0x20)` |
| `restartServiceWorker` | `0x80007324` | walk by ID; `osStartThread($a0+0x20)` |

None of those loads is passed to
`rs_free`. Host `rs64_m5_writer_parity` /
`rs64_probe_submit_gate_store` probes on
the stores are diagnostics, not original
skips.

## Pairing

One allocator function, one published
list of those nodes, one destructor of
the matched node. There is no second
`jal rs_free` of this pointer outside
`0x80007128`. Same unchecked-NULL
destructor shape already closed as
Complete for `freeRenderSubsystemResources`
(s3652) and `initSaveData` (s3653).
Runtime allocator legitimacy and whether
every call's malloc succeeds remain
unproven.

## Classification

The only `jal rs_free` site that can
receive this `$s0` is `0x80007128`. The
only live original heap-pointer writer of
the node is the flags-0x81 malloc at
`0x80006C78`, published to
`*0x801128D0` or `0x18(tail)`. All other
loads of `0x28D0` are list-head
consumers. `0x18($s0)` / `0x20($s0)` are
not sibling frees. This selects
`H-NextClassComplete`. `H-NextClassGap`
is refuted at static scope.
`H-NextClassUnevaluable` is not
selected: one object, one live allocator
function, one published list head, one
destructor site.

No guard was added. Runtime allocator
state remains unproven. The s3636 overlay
skip-path NULL store was not landed: this
`$s0` is not that writer. `funcs_2.c`
`jal rs_free` is exhausted.

## Next remaining `jal rs_free`

The next remaining original site is
`funcs_1.c` `processAssetLoadStep`
`0x80003E7C` (`$a0` = `0x48($s0)`;
post-free `sw $zero, 0x48($s0)` at
`0x80003E8C`). First of seven in that
file.
