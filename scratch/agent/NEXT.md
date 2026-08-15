# NEXT work unit (s1247)

HYPOTHESIS-ID: generated-symbol-renaming-sweep

The external retail-entry dependency remains open. Do not build or run.
Proceed with one bounded generated-symbol naming sweep over
`0x8007413C..0x80074DA4`, using companion names and generated declarations.

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
rg -n '^RECOMP_FUNC' ../N64Recomp/RecompiledFuncs/funcs_18.c | awk -F: '$1>=7480 && $1<=8200'
rg -n '8007413C|80074600|8007483C|80074B74|80074DA4' ../rogue_squadron64/symbol_files syms/rogue_squadron.syms.toml
rg -n -C 3 'triggerDistanceScaledExplosion|triggerObjectDestructionEffects|buildRandomCameraFacingOrientation|spawnScaledOrientedEffectTriple|buildNpcAnchoredCameraEffectTransform' ../rogue_squadron64/symbol_files/main_overlay.txt
```
