# M3 s3653 — initSaveData rs_free of $s2 and freeSaveDataBuffer *0x80112724

## Work unit

Static census of `initSaveData` `jal rs_free`
at `0x8000671C` (`$a0` = `$s2` from
`addu $a0, $s2` at `0x80006708`).
Enumerated every original load/store of
that `$s2` (including the matching
allocator, every later store, whether the
caller holds the buffer, and the sibling
`jal rs_free` at `0x8000672C` of the same
`$s2`) and every `jal rs_free` that can
receive that pointer. `freeSaveDataBuffer`
`0x80006774` (`$a0` = `*0x80112724`,
`lui 0x8011; lw 0x2724`) was included
because it is the destructor of the other
`rs_malloc` in `initSaveData`; that word
is not the published `$s2`. Other loads
were classified as consumers or as a
second free. No build or runtime run was
performed.

Absolute `0x80112724` never appears in
generated code. The word is
`lui 0x8011; 0x2724`. Zero gp-relative
`-0xD8DC` aliases.

The discriminator was the single complete
original census of those three `jal rs_free`
sites plus every original `lw`/`sw`/`addu`
of `initSaveData` `$s2` that can become
this `$a0`, every original `lw`/`sw` of
`*0x80112724`, and every `jal rs_free`
that can receive either pointer. No
overlay duplicate of `initSaveData` /
`0x80006338` or `freeSaveDataBuffer` /
`0x80006764` exists as a second generated
body.

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
that same writer as this `$s2` or this
word.

## Census size

Original `jal 0x80001C98` in `funcs_2.c`:
4 sites. This census covers 3
(`0x8000671C`, `0x8000672C`,
`0x80006774`). The remaining site is
`unregisterServiceWorker` `0x80007128`.
`funcs_3.c`, `funcs_5.c`, and `funcs_0.c`
have zero sites. `funcs_1.c` has 7 sites,
not in this unit.

`initSaveData` is `0x80006338`..`0x80006760`,
frame `-0x48`. One generated `jal 0x80006338`
(`runIdleFramesAndLoadSaveData`
`0x8006DA0C`). Zero `LOOKUP_FUNC(0x80006338)`.
Zero `lui`/`addiu` function-pointer
constructions of `0x80006338`. One
overlay-table entry (rom offset `0x5EF8`,
size `0x42C`); not a second generated body.
Single `jr $ra` at `0x8000675C`.
`freeSaveDataBuffer` starts at `0x80006764`
immediately after.

`$s2` is first `lui 0x8011` (callback-base
for `0x26F0`) and is rebound at
`0x800065E8` to the second malloc. The
two `$s2` frees are reachable only after
that rebind.

## `$s2` — EEPROM default-image scratch

`$s2` is never stored to a global. It is
not `*0x80112724`.

| Site | PC | Op | Object | Value |
|---|---|---|---|---|
| malloc | `0x800065E0`/`0x800065E8` | `jal rs_malloc(*0x801126C4, 8)`; `addu $s2, $v0` | `$s2` | live heap-pointer writer; register only |
| memset | `0x800065EC`/`0x800065F4` | `addu $a0, $s2`; `jal rs_memset` | `$s2` | consumer of the just-allocated buffer |
| interior | `0x80006630` | `addu $s0, $s2, $s0` then checksum `sw` at `0x0`/`0x4($s0)` | `$s2+$off` | interior consumer; not a second heap object |
| EEPROM write | `0x8000669C` | `addu $a2, $s2`; `jal osEepromLongWrite` | `$s2` | consumer; write source |
| fail-free | `0x80006708`/`0x8000671C` | `addu $a0, $s2`; `jal rs_free` | `$s2` | destructor; no NULL skip; then return |
| success-free | `0x8000672C`/`0x80006730` | `addu $a0, $s2`; `jal rs_free` | `$s2` | destructor; no NULL skip; then re-enter the EEPROM read loop at `L_800064DC` |

The size check at `0x800065BC` takes the
malloc only when `*0x801126C4 >=
(*0x80112728 * *0x801126CE) + 0x20`.
The too-small path returns through the
callback without allocating `$s2` and
without reaching either free.

The two frees are mutually exclusive per
allocation. Write-success frees `$s2` and
jumps to the header-read loop, which does
not use `$s2` until a later trip through
the same malloc. Write-failure after
retries frees `$s2` and returns.
`L_80006704` retry (`callback == 1`)
rewrites the same `$s2` without freeing.
Neither free can fire on the pre-malloc
`lui $s2, 0x8011` value.

There is no `sw $s2` of this pointer
after the malloc. The caller
`runIdleFramesAndLoadSaveData` does not
hold `$s2`. Failed malloc leaves `$s2 ==
0`; `rs_free(0)` skips. That is the same
unproven allocator-failure edge
s3604–s3652 left open.

No other function contains a
`jal 0x80001C98` of this register. The
s3636 overlay `0x1C`/`0x20` writer is
not this `$s2`.

## `*0x80112724` — persistent save-data buffer

14 original `lui 0x8011` `0x2724` sites,
all in `funcs_2.c`. One store.

| Site | PC | Op | Object | Value |
|---|---|---|---|---|
| malloc | `0x800063C4`/`0x800063D0` | `jal rs_malloc(*0x801126C8+0x118, 0x81)`; `sw $v0, 0x2724` | `*0x80112724` | live heap-pointer writer |
| destructor | `0x80006768`/`0x80006774` | `lw 0x2724`; `jal rs_free` | `*0x80112724` | destructor; no NULL skip; no post-free NULL |
| 12 other loads | see consumers | `lw 0x2724` | `*0x80112724` | buffer-base consumers; none `jal rs_free` of this pointer |

There is no `sw $zero` of `0x2724`.
Failed malloc still stores `$v0 == 0`.
The first malloc always runs before the
EEPROM-present branch; `initSaveData`
does not free this word.

`freeSaveDataBuffer` is
`0x80006764`..`0x80006788`, frame `-0x18`.
Zero generated `jal 0x80006764`. Zero
`LOOKUP_FUNC(0x80006764)`. Zero
`lui`/`addiu` constructions of
`0x80006764`. One overlay-table entry
(rom offset `0x6324`, size `0x28`); not a
second generated body. Single `jr $ra`
at `0x80006784`. Sequential double-free
of the dangling post-free global would
require a second call of this destructor;
it has no generated caller.

### Consumers — buffer-base reloads, not a second free

| Function | PC | Use after `lw 0x2724` |
|---|---|---|
| `writeSaveBodyToEeprom` | `0x80005DEC` | `jal rs_memset` dest |
| `writeSaveBodyToEeprom` | `0x80005E98` | `osPfsReadWriteFile` file-data arg |
| `writeSaveDataBodyToEeprom` | `0x800060A8` | `osPfsReadWriteFile` file-data arg |
| `writeSaveDataBodyToEeprom` | `0x800060FC` | `adler32` of the buffer (`$s0` still `lui 0x8011` on this path) |
| `copySaveUnk08` | `0x80006284` | `osPfsReadWriteFile` file-data arg (`$s6` = `lui 0x8011` at `0x80006208`) |
| `copySaveUnk08` | `0x800062A4` | `adler32` of the buffer |
| `saveLoadDispatcher` | `0x80006818` | `jal rs_memset` dest |
| `saveLoadDispatcher` | `0x800068A8` | `osEepromLongWrite` source |
| `loadOrSaveEepromRecord` | `0x800069B0` | `osEepromLongRead` dest |
| `loadOrSaveEepromRecord` | `0x800069D0` | `adler32` of the buffer |
| `loadOrSaveAllEepromRecords` | `0x80006B34` | `osEepromLongRead` dest (`$s4` = `lui 0x8011` at `0x80006B1C`) |
| `loadOrSaveAllEepromRecords` | `0x80006B54` | `adler32` of the buffer |

`0x80031BDC` is `osPfsReadWriteFile_recomp`.
It does not `jal rs_free`. Interior
checksum stores write into the buffer,
not a second heap object.

A second `initSaveData` overwrites
`*0x80112724` without freeing the
previous set. That is a leak of the first
malloc, not a second free. The destructor
still receives the latest matching
allocator store. One generated caller.

These words are not the s3636 overlay
`0x1C` / `0x20` writer. Host
`rs64_m5_writer_parity` /
`rs64_probe_submit_gate_store` probes on
the stores are diagnostics, not original
skips.

## Pairing

`$s2` has one allocator and two mutually
exclusive destructors of that register.
`*0x80112724` has one allocator store and
one destructor. There is no second
`jal rs_free` of either pointer outside
those three sites. Same
unchecked-NULL destructor shape already
closed as Complete for
`freeRenderSubsystemResources` (s3652)
and earlier classes. Runtime allocator
legitimacy and whether every call's malloc
succeeds remain unproven.

## Classification

The only `jal rs_free` sites that can
receive `$s2` are `0x8000671C` and
`0x8000672C`. The only `jal rs_free` site
that can receive `*0x80112724` is
`0x80006774`. The only live original
heap-pointer writer of `$s2` is the
flags-8 malloc at `0x800065E0`. The only
live original heap-pointer writer of
`*0x80112724` is the flags-0x81 malloc
store at `0x800063D0`. All other loads of
`0x2724` are buffer-base consumers. This
selects `H-NextClassComplete`.
`H-NextClassGap` is refuted at static
scope. `H-NextClassUnevaluable` is not
selected: two objects, one live allocator
function, register-local scratch plus one
published word, three destructor sites.

No guard was added. Runtime allocator
state remains unproven. The s3636 overlay
skip-path NULL store was not landed: these
pointers are not that writer.

## Next remaining `jal rs_free`

The next remaining original site in
`funcs_2.c` is `unregisterServiceWorker`
`0x80007128` (`$a0` = `$s0` from
`addu $a0, $s0` at `0x8000712C`; `$s0`
walks `*0x801128D0`).
