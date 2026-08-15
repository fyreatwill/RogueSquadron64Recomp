# NEXT work unit (s1244)

HYPOTHESIS-ID: generated-save-account-naming-sweep

The external retail-entry dependency remains open. Do not build or run.
Proceed with one bounded generated-symbol naming sweep over the next helper
region `0x80071064..0x8007202C`, using companion names and generated call sites.

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
rg -n 'RECOMP_FUNC void (func_|fake_func_)|0x800710|0x800720' ../N64Recomp/RecompiledFuncs/funcs_17.c
rg -n -C 3 '800710|800711|800712|800713|800714|800715|800716|800717|800718|800719|80071A|80071B|80071C|80071D|80071E|80071F|800720' ../rogue_squadron64/symbol_files ../rogue_squadron64/docs docs/game-architecture.md syms
sed -n '8500,9800p' ../N64Recomp/RecompiledFuncs/funcs_17.c
```
