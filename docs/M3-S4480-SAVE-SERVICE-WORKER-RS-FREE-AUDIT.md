# M3 s4480 — saveServiceWorker rs_free of the 0x14 save-message token

## Work unit

Static census of the one original `jal rs_free` in
`saveServiceWorker` (`0x8006F2CC`, size `0xBC`), at `0x8006F378`.
The delay slot is `addu $a0, $s0, $zero`. `0x8006F380` is
`j 0x8006F318`, so the free is inside the recv loop. No build or
runtime run was performed. `runIdleFramesAndLoadSaveData` (s4479)
was not re-audited.

The discriminator was the complete original assignment list for
`$s0` from the prologue through each reach of `0x8006F378`, every
callee `jal rs_free`, and every caller argument:

- H-NextClassGap: `$s0` can be a non-allocator value, or a pointer
  a sibling already freed, with that writer named.
- H-NextClassComplete: every assignment that reaches the free is
  the matching allocator return, and each such pointer is freed
  once.
- H-NextClassUnevaluable: more than one pointer identity can reach
  `$a0`.

Same-scan positive control: `jal 0x80001C98` still locates closed
`0x8006DA28` and this site in `funcs_17.c`, and still locates
`0x8006C8C4` (also `0x8006B814`, `0x8006C4A8`, `0x8006C650`) in
`funcs_16.c`. The ROM word `0x0C000726` matches `0x8006B814`,
`0x8006C8C4`, `0x80005268`, `0x8006DA28`, and `0x8006F378`. A scan
that missed `0x8006DA28` would have been invalid.

## Census

| Site | `$a0` | Setup | Classification |
|---|---|---|---|
| `funcs_17.c`, `0x8006F378` | `$s0` | `addu $s0, $v0` at `0x8006F334` after `jal recvServiceMessage` | sole free; the `rs_malloc(0x14)` token queued by `triggerSaveMessage` |

ROM register-write scan of `0x8006F2CC`..`0x8006F388` finds one
write of `$s0`: `addu $s0, $v0, $zero` at `0x8006F334`. The
generated function has the same single assignment
(`ctx->r16 = v0` at that PC). `sw $s0, 0x28($sp)` at `0x8006F2FC`
saves the incoming `$s0` and does not assign it. There is no
epilogue reload. The function has no `jr`.

| PC | Instruction | Reaches the free? |
|---|---|---|
| `0x8006F2FC` | `sw $s0, 0x28($sp)` | no; save of the incoming register, not a write |
| `0x8006F334` | `addu $s0, $v0, $zero` | yes; this is the freed value on every trip |

`$s5` is the incoming `$a0` (`addu $s5, $a0` at `0x8006F2D4`).
Nothing copies `$s5` into `$s0`. The rebind at `0x8006F334`
dominates every path to the free, including the back-edge.

Straight line from the recv return to the rebind:

```
0x8006F324  addiu $a0, $zero, 1
0x8006F328  addu  $a1, $zero, $zero
0x8006F32C  addu  $a2, $a1, $zero
0x8006F330  addiu $a3, $sp, 0x18
0x8006F334  addu  $s0, $v0, $zero
```

None of those four instructions writes `$v0`, so `$s0` is the
`recvServiceMessage` return. The two `beql` instructions at
`0x8006F348` and `0x8006F370` have delay slot `sb $s1, 0x2C($s2)`.
That store writes a byte at `0x80130B6C`. It does not write `$s0`.
Both outcomes fall through to the free. Nothing between the rebind
and `0x8006F378` assigns `$s0`.

The back-edge `j 0x8006F318` / `nop` returns to `lw $a0, 0($s5)`
and the recv, which is before the rebind. The next trip frees the
next recv return, not the pointer already freed on the previous
trip.

## What `$v0` is

`recvServiceMessage` (`0x80006F24`, size `0x54`) walks
`*0x801128D0` until `0($node) == $a0`, then calls `osRecvMesg`
with `$a0 = node+0x1D0`, `$a1 = node+0x1E8`, `$a2 = 1`. It
returns `lw $v0, 0x1E8($node)`. It contains no `jal rs_free`.
Its own `$s0` is restored at `0x80006F6C` before `jr`, and the
worker copies `$v0` only after that return.

`osRecvMesg` saves the caller's `$a1` at `0x2C($sp)` and, when
that pointer is not zero, executes `sw $t9, 0($t3)` at
`0x8003326C`. `$t9` is the word loaded from the queue array.
`osSendMesg` saves the caller's `$a1` at `0x3C($sp)` and executes
`sw $t0, 0($t3)` at `0x800334D8`, where `$t0` was reloaded from
that slot (`lw $t0, 0x3C($sp)` at `0x800334B0`). The word the
worker frees is the pointer that was passed to `osSendMesg` on
this worker's queue.

`sendServiceMessage` (`0x80006F78`) sends `$a2` to the worker
whose id is `$a1`, after writing the reply queue, sequence, and a
zero flag into the payload (`+0x8`, `+0x2`, `+0x4`). Those stores
are interior. The queued pointer is still `$a2`. The function
contains no `jal rs_free`.

## The only sender

The save worker id is the word at `0x800A0A60`.
`registerSaveService` stores the `registerServiceWorker` return
there and passes entry `0x8006F2CC` (`lui $a3, 0x8007` /
`addiu $a3, $a3, -0xD34`). A whole-ROM scan of `lw`/`sw`/`addiu`
with immediate `0xA60` and a nearby `lui 0x800A` finds only:

| PC | Function | Use |
|---|---|---|
| `0x8006EFC4` | `registerSaveService` | store the new id |
| `0x8006EFE8`, `0x8006F008` | `stopSaveServiceWorker` | load id for `unregisterServiceWorker`, then store `-1` |
| `0x8006E3BC`, `0x8006E3E8` | `setUnlockBitAndPersist` | load id; unregister when it is not `-1`; store `-1`; then call `saveLoadDispatcher` inline |
| `0x8006E2C4` | `serializeSettingsToSaveAndPersist` | compare to `-1` |
| `0x8006F1E4` | `persistSaveDataBody` | compare to `-1` |
| `0x8006F2B0` | `triggerSaveMessage` | `$a1` of `sendServiceMessage` |

`triggerSaveMessage` (`0x8006F274`, size `0x58`) is straight-line.
It calls `rs_malloc` with size `0x14` and flags `0`, copies `$v0`
to `$s0`, `rs_memset`s `0x14` bytes, then
`sendServiceMessage($a0 = *0x80138920, $a1 = *0x800A0A60, $a2 = $s0, $a3 = 0)`.
It does not free. It restores the caller's `$s0` before `jr`, so
the token does not escape in `$s0`. `$a3 = 0` means a full queue
does not retry; the token leaks rather than being sent twice.

The whole ROM contains two `jal triggerSaveMessage` words, both
with delay slot `nop`:

| Caller | Site | When |
|---|---|---|
| `serializeSettingsToSaveAndPersist` | `0x8006E334` | `*0x800A0A60 != -1` |
| `persistSaveDataBody` | `0x8006F254` | `*0x800A0A60 != -1` |

When the id is `-1`, both callers run `saveLoadDispatcher`
themselves and do not reach the jal. Neither path both enqueues
and saves inline. Neither caller is given the token; the malloc
is inside `triggerSaveMessage`.

`setUnlockBitAndPersist` and `stopSaveServiceWorker` store `-1`
and do not send. `postMessageToServiceWorker` has three ROM jal
sites and none of them is in the `0x800A0A60` reference list.
`signalServiceWorkerStop` has zero jal words in the ROM.
`saveServiceWorker` itself has zero jal words; it is only the
thread entry.

`unregisterServiceWorker`'s `jal rs_free` at `0x80007128` frees
the registry node. That object was closed in s3654. It is not the
`0x14` token. Destroying the thread while a token is still queued
leaks that token; it does not free it twice.

## Callees do not free this pointer

Direct callees of the worker are `rs_memset` (prologue, before the
rebind), `recvServiceMessage`, `saveLoadDispatcher` (twice), and
`rs_free`. The first three contain zero `jal rs_free`.

`saveLoadDispatcher` (`0x80006798`, size `0x19C`) saves the
incoming `$s0` at `0x18($sp)` at `0x800067AC`, before
`addu $s0, $a0` at `0x800067B0`. The only `jr` is `0x8000692C`.
Every path reaches it through the epilogue, which reloads
`0x18($sp)` at `0x80006928`. No other instruction stores that
slot. The worker's two calls pass `$a0 = 1`, so the `$a0 == 0`
reload and the `$a0 == 2` call of `writeSaveBodyToEeprom` are not
taken. On the `$a0 == 1` path the dispatcher's own `$s0` becomes
the save-body pointer at `0x80112724`, which is not the token.
The token is not an argument. `writeSaveBodyToEeprom` has four
`jalr` and zero `jal rs_free`, and is not reached from these
calls. `waitForSerialIdle`, `releaseSerialLock`, `rs_memset`,
`memcpy`, `adler32`, and `osEepromLongWrite` contain zero
`jal rs_free`.

A NULL `rs_malloc` return would make the token zero. `rs_free`
branches to `0x80001F78` when `$a0 == 0` (`beq` at `0x80001CA4`).
`triggerSaveMessage` does not test `$v0` first, so a failed
malloc would also be written through before the send. That is the
same unproven allocator-failure edge left open by s3604–s4479,
not a second pointer identity.

## Callers of the worker

Zero direct calls. `registerSaveService` installs `0x8006F2CC` as
the thread entry. The thread argument is the worker node: the
function keeps it in `$s5` and passes `0($s5)` to
`recvServiceMessage` as the id. That node is not the freed
register.

## Classification

H-NextClassComplete. H-NextClassGap is refuted at static scope:
the only `$s0` that reaches the free is that iteration's
`recvServiceMessage` return, that return is the pointer
`osSendMesg` queued, and the only enqueue to `0x800A0A60` is the
`rs_malloc(0x14)` inside `triggerSaveMessage`. No callee frees
that pointer, and this function frees it once per receive.
H-NextClassUnevaluable is not selected. Runtime allocator and
freelist legitimacy remain unproven. No guard was added.

The next unaudited `jal rs_free` in address order is
`walkDatTreeAndCollectSubtypes` at `0x80072B8C` (entry
`0x80072AF8`, size `0xE8`, `funcs_18.c`). The instruction before
the jal is `lw $a0, 8($s0)` at `0x80072B88`. The delay slot is
`nop`, so it does not replace `$a0`. `$s0` itself is the incoming
`$a0` and is not the freed pointer. The free is skipped when
byte 0 is `255` or when bit `0x80` of byte 0 is clear.
