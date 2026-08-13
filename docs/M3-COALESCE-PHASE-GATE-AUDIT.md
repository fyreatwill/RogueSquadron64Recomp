# M3 coalescer and frame-tick phase-gate audit

Source-only audit performed in s873 (2026-08-13) against
`../N64Recomp/RecompiledFuncs`.

## State inventory

`0x801163f8` is the `0x63f8` word in the `0x80110000` global region. It is
written only by `partitionFramebufferMemory` (`0x80000dd4`): `0x80001024`
writes the fourth-boundary fit value and `0x80001038` writes the complementary
residual value. It is read at `0x8000126c` by the boot worker and at
`0x80001470` by `runVideoFrameTick`. There are no other generated-tree reads,
writes, aliases, or delay-slot duplicates.

The same partition routine writes `0x801163e4` at `0x80000ed8` and
`0x801163e8` at `0x80000ffc` or `0x80001010`. It is called from the boot worker
at `0x80001180` and from `runVideoFrameTick` at `0x800013f0`, so normal frame
ticks refresh the values; this is not an init-only writer.

## Call and gate inventory

`runVideoFrameTick` has four direct callers: two `mainGameLoop` paths
(`funcs_8.c`, `0x8003e29c` and `0x8003e360`), `initSceneForMission`
(`funcs_27.c`, `0x800a9c70`), and `menuOverlayInit` (`funcs_34.c`,
`0x800c5a18`). Every caller supplies scene/display-state pointers.

The tick normalizes width (`0x18` becomes `0x20`), computes partition inputs,
calls `partitionFramebufferMemory`, and unconditionally calls
`coalesceFreeHeapBlocks` at `0x80001430`. The partition return only selects
the coalescer's `a0/a1` arguments; it does not suppress the call. At the
coalescer boundary, `a0/a1` reload `0x801163e4/0x801163e8`, `a2` is
`0x80113200 + 0x47490`, and `a3` reloads `0x801163f8`.

The tick's first call is `musyxNoopStub`. `menuOverlayInit` separately loops
on `tickMusyXIfActive` and `anyAudioSlotActive` before constructing its display
state and calling the tick. `anyAudioSlotActive` reaches the audio-disabled
`audioStubReturnZero`, but this is a menu-init predecessor, not a gate inside
the tick/coalescer path. No direct controller or `osCont*` call surrounds any
of the four tick callsites.

## Classification and result

The two `0x801163f8` stores are per-partition updates; the boot call is
initialization, the normal tick call is a per-frame update, and the coalescer
call has no state gate. No site was dead or unreachable by static callsite
coverage. This rules out a missing/stale port writer or an in-function phase
gate as the complete explanation for the observed boot state. It selects the
source-level form of H-retail-driver-only over H-port-state-gate and
H-audio/input-gate, while remaining single-source evidence: source alone does
not prove runtime pointer/heap-value legitimacy or explain the retail
width-320 stall. No mitigation is justified.

ORIGIN: generated-tree source inventory only; no guest value, control flow, or
mitigation behavior changed.
