# M3 variable-shift lowering census

## Scope and discriminator

This is a static census of the current `../N64Recomp/RecompiledFuncs/funcs_*.c`
tree. The class is the three MIPS variable-shift instructions `sllv`, `srlv`,
and `srav`. The expected generated forms are 32-bit results with the MIPS
five-bit shift-count mask: `S32(src << (count & 31))`,
`S32(U32(src) >> (count & 31))`, and `S32(SIGNED(src) >> (count & 31))`,
respectively.

## Results

| class | `sllv` | `srlv` | `srav` | total |
| --- | ---: | ---: | ---: | ---: |
| all textual mentions | 420 | 142 | 159 | 721 |
| direct instruction comments | 309 | 73 | 87 | 469 |
| `.word` data-as-code annotations | 111 | 69 | 72 | 252 |
| expected lowering, live destination | 272 | 61 | 70 | 403 |
| discarded `$zero` destination | 37 | 12 | 17 | 66 |

The 252 `.word` annotations are decoded instruction names embedded in data
comments; they are not generated shift operations. All 469 direct instruction
comments have either the expected lowering or a `$zero` destination whose
result is discarded. No direct site had a missing or mismatched lowering.

## Independent checks

Two source passes were used:

1. A raw comment census counted every operation name and independently split
   direct instruction comments from `.word` annotations.
2. A register-aware semantic pass mapped every direct site's operands to
   `ctx->rN`, skipped diagnostic lines between the guest comment and generated
   assignment, normalized register zero to the constant zero, and checked the
   destination, count mask, result width, and right-shift signedness.

The second pass produced 272/37 for `sllv`, 61/12 for `srlv`, and 70/17 for
`srav` (expected/discarded), with zero mismatches or missing assignments.

## Conclusion

`H-variable-shift-faithful` is selected for the generated direct variable-shift
class. `H-variable-shift-mismatch` and
`H-variable-shift-intervening-write` are not selected. The qualified
title/hangar route does not establish site-level reachability, so no runtime
reachability claim is made and no guard or mitigation is authorized.
