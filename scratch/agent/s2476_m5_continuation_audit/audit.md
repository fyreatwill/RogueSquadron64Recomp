# s2476 continuation audit

Date: 2026-08-26

## Scope and controls

This was a static audit only. No build or game run was performed. The generated
tree searched was `../N64Recomp/RecompiledFuncs/funcs_*.c`.

The variable-register census searched every `LOOKUP_FUNC(ctx->r25)`,
`LOOKUP_FUNC(ctx->r31)`, and `LOOKUP_FUNC(ctx->r9)` occurrence. It found one
match. The broader generated tree contains many constant-address lookups and
variable lookups through other registers, but no other member of this
continuation-tail class.

## Complete continuation-tail table

| Generated site | Caller/source link | Target expression | Target kind | Host lowering |
|---|---|---|---|---|
| `funcs_4.c:33578`, `convertMat3x4ToN64Mtx`, guest `0x80018E58` (`jr $t9`) | `traverseSceneGraphRecursive` at guest `0x800155E4`; fixup writes `ctx->r31 = 0x800155EC` | `ctx->r25`, assigned from `ctx->r31` at `0x80018D84` | `0x800155EC`, the caller's local `after_4` label immediately after the direct call | Direct named call plus `goto after_4`; no host function-map entry or continuation registration |

The direct call's delay slot is `addiu $a1,$sp,0x10`, so it cannot write the
link. The legitimate guest link is therefore PC+8, `0x800155EC`, as recorded
by s2475.

## Runtime registration cross-check

`overlays.cpp` inserts only function starts and overlay/patch offsets into
`func_map`. No path registers generated `after_N` labels, and generated direct
calls use a C call plus a local `goto`, not a callable host continuation.

## Selection

This selects **H-HostContinuationOnly**. The only qualifying tail target is an
intra-function `after_4` label, while the runtime has no mapped continuation
entry. H-ContinuationMap is refuted at the inspected generated/runtime scope;
H-WrongTailContract is refuted by the consumed PC+8 link and the immediate
`after_4` continuation in the generated caller.

The next design question is how to bridge this one guest tail edge while
preserving the shared `recomp_context` and returning to the caller's `after_4`
path. No bridge, guard, or runtime change was made in this audit.
