# NEXT work unit (s2450) — inspect direct-`jal` lowering semantics

HYPOTHESIS-ID: m5-port-static-rsmemset-callsite

## Work unit

Perform a bounded source audit of N64Recomp's direct-`jal` lowering and C
generator call emission, then compare it with one generated static
`rs_memset` call and one generated indirect positive-control call. Do not
change runtime or generated output.

## Competing hypotheses and discriminator

- H-GeneratorIntentionalNoRA: direct C calls intentionally omit guest link
  writes, while indirect calls use a different contract.
- H-GeneratorLoweringDefect: direct `jal` lowering should write the guest link
  but the emitted path does not.
- H-CallsiteSpecificRewrite: a later generation/fixup rewrite removes the link
  only for this generated call family.

The discriminator is the source-to-output contract comparison: if the generator
explicitly omits links for all direct calls and the positive-control indirect
path writes/resolves one, select intentional semantics; if source requires a
link but output omits it, select a lowering defect; if only fixup output differs,
select a callsite-specific rewrite.

## Exact commands

`sed -n '120,370p' ../N64Recomp/src/recompilation.cpp`

`sed -n '400,450p' ../N64Recomp/src/cgenerator.cpp`

`rg -n -C 4 "rs_memset\\(rdram, ctx\\)|get_function\\(.*8009123C|ctx->r31 =" ../N64Recomp/RecompiledFuncs/funcs_2.c ../N64Recomp/RecompiledFuncs/funcs_*.c | head -240`
