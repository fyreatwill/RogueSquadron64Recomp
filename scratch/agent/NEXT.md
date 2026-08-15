# NEXT work unit (s1245)

HYPOTHESIS-ID: generated-save-account-naming-sweep

The external retail-entry dependency remains open. Do not build or run.
Proceed with one bounded generated-symbol naming sweep over the next helper
region `0x8007218C..0x80072CE8`, using companion names and generated call sites.

Competing hypotheses and discriminator:

- H1: the remaining helper region has exact companion mappings sufficient to
  rename a coherent function family without invented semantics.
- H2: mappings are partial or ambiguous, so only exact names can be safely
  applied and the remainder stays `func_*`.
- H3: the region has no usable independent naming source and should be parked.

Discriminator: one table covering every `func_*` symbol in the selected region,
with generated address, companion name/source, callers, and confidence. A
complete exact mapping selects H1; only a subset safe to rename selects H2;
absence of independent names selects H3. No code or runtime mitigation is
justified by this sweep.

Exact commands:

```
rg -n 'RECOMP_FUNC void (func_|fake_func_)|0x800721|0x80072C' ../N64Recomp/RecompiledFuncs/funcs_17.c ../N64Recomp/RecompiledFuncs/funcs_18.c
rg -n -C 3 '800721|800722|800723|800724|800725|800726|800727|800728|800729|80072A|80072B|80072C' ../rogue_squadron64/symbol_files ../rogue_squadron64/docs docs/game-architecture.md syms
sed -n '1680,3980p' ../N64Recomp/RecompiledFuncs/funcs_18.c
```
