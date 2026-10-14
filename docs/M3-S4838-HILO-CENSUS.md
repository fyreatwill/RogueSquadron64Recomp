# M3 HI16/LO16 construction census

## Scope and discriminator

This is a static census of the current `../N64Recomp/RecompiledFuncs/funcs_*.c`
tree. A candidate HI16/LO16 construction is a `lui` followed by an immediate
`addiu` or `ori` that reads and writes the same register. The discriminating
properties are destination-register preservation, immediate adjacency, and the
expected signed-versus-unsigned low-half operation. Runtime reachability is not
inferred from this census.

## Results

| class | count |
| --- | ---: |
| generated `lui` source occurrences | 24,276 |
| canonical `lui` + `addiu` pairs | 2,479 |
| canonical `lui` + `ori` pairs | 536 |
| canonical same-register pairs | 3,015 |
| `lui` sites without a canonical pair | 21,261 |
| adjacent low-half-looking operations with a different destination/source register | 1,174 |

The 3,015 canonical pairs preserve the `lui` destination as both operands of
the low-half operation. No pair combined a high-half register with a different
low-half source register, and no pair required an intervening instruction.
`addiu` sites use the generated signed low-half form; `ori` sites use the
unsigned low-half form. This is the expected MIPS relocation/lowering split.

The 21,261 non-pair `lui` occurrences include ordinary base-register loads,
floating-point bit-pattern constants, stores and loads using the high half
directly, branch-delay/control-flow duplication, and other independent
instructions. The 1,174 adjacent operations in the last row were excluded
because their low operation does not consume the `lui` destination; they are
not HI16/LO16 pairs. They are not evidence of a bad relocation.

## Independent checks

Two source passes were used:

1. An instruction-comment pass matched the guest PC of every `lui` to the next
   guest instruction and required exact `lui` PC + 4 adjacency plus identical
   destination/source registers.
2. A raw source-adjacency pass independently classified every adjacent
   `addiu`/`ori`; it found 3,015 same-register pairs and 1,174 different-register
   operations. The different-register examples are excluded by the pair
   definition rather than silently treated as valid pairs.

Representative valid forms are:

```c
// 0x80003428: lui         $a1, 0x801A
ctx->r5 = S32(0X801A << 16);
// 0x8000342C: addiu       $a1, $a1, -0xB18
ctx->r5 = ADD32(ctx->r5, -0XB18);

// 0x8003E260: lui         $v0, 0xFDFF
ctx->r2 = S32(0XFDFF << 16);
// 0x8003E264: ori         $v0, $v0, 0xFFFF
ctx->r2 = ctx->r2 | 0XFFFF;
```

The exact command shape was:

```text
rg -n -i -C 4 'lui|addiu|ori|lui.*0x801|0x[0-9A-Fa-f]+.*(lui|addiu|ori)' ../N64Recomp/RecompiledFuncs/funcs_*.c
```

## Conclusion

`H-hi-lo-faithful` is selected for the generated canonical HI16/LO16 idiom.
`H-hi-lo-mismatch` and `H-hi-lo-intervening-write` are not selected: the
complete canonical class has no register mismatch or intervening instruction.
The qualified title/hangar positive control does not establish site-level
reachability, so no claim is made for `H-hi-lo-route-gap`; reachability remains
orthogonal to this closed lowering audit. No runtime guard or mitigation is
authorized by this census.
