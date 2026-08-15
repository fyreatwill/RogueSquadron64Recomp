# NEXT work unit (s1248)

HYPOTHESIS-ID: generated-symbol-renaming-sweep

The external retail-entry dependency remains open. Do not build or run.
Proceed with one bounded generated-symbol naming sweep over
`0x80075218..0x80075BB0`, using companion names and generated declarations.

Competing hypotheses and discriminator:

- H1: the selected region has exact companion mappings sufficient to rename a
  coherent helper family.
- H2: mappings are partial or ambiguous, so only exact names can be safely
  synchronized and the remainder stays `func_*`.
- H3: the region has no usable independent naming source and should be parked.

Discriminator: one table covering every generated function in the selected
range, with address, generated name, companion name/source, callers, and
confidence. Complete exact agreement selects H1; only a safe subset selects
H2; no independent names selects H3. No runtime mitigation is justified.

Exact commands:

```
rg -n '^RECOMP_FUNC' ../N64Recomp/RecompiledFuncs/funcs_18.c | awk -F: '$1>=10400 && $1<=11800'
rg -n '80075218|8007559C|80075720|80075BB0' ../rogue_squadron64/symbol_files syms/rogue_squadron.syms.toml
rg -n -C 3 'buildRandomCameraFacingOrientation|spawnScaledOrientedEffectTriple|heavyRandomBurstNpcHandler|buildNpcAnchoredCameraEffectTransform' ../rogue_squadron64/symbol_files/main_overlay.txt
```
