# Session 3321 — generated free-list walk audit

## Scope and controls

The audited artifact is the generated host file
`/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_3.c`,
which is the linked generated tree described by the repository configuration.
The scope is the two allocator consumers patched by the s3285 alignment/cycle
class: `allocateDisplayListBuffer` and `allocDLBlockToFillRectList`. The source
positive control is the six existing residual free-list guard blocks: each
candidate list-node `lw` has its guard immediately before `MEM_W`.

## Complete candidate table

| function | guest PC | load | role | guard immediately before load |
|---|---:|---|---|---|
| allocateDisplayListBuffer | `0x80007D9C` | `MEM_W(ctx->r3, 0)` | initial returned free-list node | yes, KSEG0 + 4-byte alignment |
| allocateDisplayListBuffer | `0x80007DA8` | `MEM_W(ctx->r4, 0)` | loop-back next-node pointer | yes, KSEG0 + alignment + `s3285_walk` cap |
| allocateDisplayListBuffer | `0x80007DAC` | `MEM_W(ctx->r4, 0)` | freshly-read next-node pointer | yes, KSEG0 + alignment + upper-word check |
| allocDLBlockToFillRectList | `0x80007E84` | `MEM_W(ctx->r5, 0)` | initial returned free-list node | yes, KSEG0 + 4-byte alignment |
| allocDLBlockToFillRectList | `0x80007E90` | `MEM_W(ctx->r3, 0)` | loop-back next-node pointer | yes, KSEG0 + alignment + `s3285_walk` cap |
| allocDLBlockToFillRectList | `0x80007E94` | `MEM_W(ctx->r3, 0)` | freshly-read next-node pointer | yes, KSEG0 + alignment + upper-word check |

The same source census found three cache-head loads (`0x80007D50`,
`0x80007DE8`, and `0x80007ED0`). They are not free-list traversal loads: they
read the active/cache head after the traversal or at the allocator handoff.
Each already has a `GENERIC_CACHE_GUARD` block.

## Result

The six candidate free-list dereferences are all guarded, and both generated
allocator functions contain the cycle counter reset at their initial-node
guard and the cap at their loop-back guard. No unguarded generated free-list
walk was found in this bounded class. This selects `H-AllWalksCovered` and
leaves the s3285 machinery as safety-only; it does not explain the VI-640
route or authorize an audio change.

This is static, single-source evidence. It does not prove that the guards are
semantically correct on retail hardware, nor that regeneration will preserve
them; the regeneration source/fixup path remains a separate concern.
