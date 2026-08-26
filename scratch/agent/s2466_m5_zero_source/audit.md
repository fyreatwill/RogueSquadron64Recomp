# s2466 M5 zero-source audit

## Scope

Static-only audit of the complete generated `traverseSceneGraphRecursive`
caller and `convertMat3x4ToN64Mtx` body in
`../N64Recomp/RecompiledFuncs/funcs_4.c`. No build, runtime instrument, or
behavior change was made.

## Census

| Region | Evidence | Result |
|---|---|---|
| `traverseSceneGraphRecursive` entry | No assignment to `ctx->r31` before the converter call; it is only saved at `0x80015580` and restored at the epilogue | The converter inherits the caller's context `$ra`; this body does not create a new link value |
| Direct converter call | `0x800155E4: jal 0x80018D80`; generated C calls `convertMat3x4ToN64Mtx(rdram, ctx)` then jumps to `after_4` | The continuation is represented by host control flow; no `ctx->r31` write occurs at the call or delay slot |
| Converter entry | `0x80018D84: addu $t9, $ra, $zero`; `ctx->r25 = ADD32(ctx->r31, 0)` | Resolver input is exactly the incoming `ctx->r31`, with no matrix-field or `$a0/$a1` contribution |
| Converter internal calls | Three direct `jal 0x80018E60` calls, each lowered to `packMtxRowFloatToFixed` plus `after_0/1/2`; no `LOOKUP_FUNC` | No hidden indirect edge in the row-packing path |
| Converter terminal edge | `0x80018E58: jr $t9`; generated output executes `LOOKUP_FUNC(ctx->r25)(rdram, ctx)` before `return` | A zero incoming `$ra` becomes `get_function(0)` at the shared resolver |
| Other generated references | Exactly one direct generated call to `convertMat3x4ToN64Mtx`, at `funcs_4.c:21451` | No alternate generated caller can explain this event in the current tree |

## Hypotheses and discriminator

- `H-ConverterRegisterZero`: not selected. The converter does not zero or load
  the resolver register from a matrix field; it copies `r31` into `r25`.
- `H-CallerContextZero`: selected at static ABI/context scope. The direct
  caller supplies no new `r31`, so a resolver request of zero must have been
  inherited in the shared `recomp_context` from an earlier caller boundary.
- `H-UnseenLoweringEdge`: not supported by this census. All converter calls,
  continuations, register writes, and the sole terminal lookup are accounted
  for in the generated body.

## Limits

This audit cannot identify which earlier caller first supplied `r31 == 0`;
that requires the already-planned live boundary tuple (`r31` at converter
entry and at resolver entry) with the retained indirect positive control.
It also does not authorize replacing the lookup, adding a null guard, or
changing audio dispatch.

Commands used:

```sh
awk ... ../N64Recomp/RecompiledFuncs/funcs_4.c
rg -n "jal|LOOKUP_FUNC|ctx->r31|ctx->r25|after_|convertMat3x4ToN64Mtx" /tmp/rs64_traverse.txt
rg -n "jal|jalr|LOOKUP_FUNC|ctx->r31|ctx->r25|after_|MEM_W|cache" /tmp/rs64_converter.txt
rg -n "convertMat3x4ToN64Mtx\(rdram, ctx\)" ../N64Recomp/RecompiledFuncs
```
