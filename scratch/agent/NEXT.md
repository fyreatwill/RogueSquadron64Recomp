# NEXT work unit (s1246)

HYPOTHESIS-ID: generated-symbol-renaming-sweep

The external retail-entry dependency remains open. Do not build or run.
Proceed with one bounded generated-symbol naming sweep over
`0x80072CF0..0x80073E4C`, using companion names and generated declarations.

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
sed -n '3920,4750p' ../N64Recomp/RecompiledFuncs/funcs_18.c | rg '^RECOMP_FUNC'
rg -n '80072CF0|80072EC4|80073750|800739A4|80073BD8|80073E4C' ../rogue_squadron64/symbol_files syms/rogue_squadron.syms.toml
rg -n -C 3 'initWaterSprayParticles|npcWaterSprayUpdate|spawnDestructionEffectBurst|spawnDistanceScaledDebrisBurst|spawnDirectionalDebrisBurst|distanceAndDopplerNpcHelper' ../rogue_squadron64/symbol_files/main_overlay.txt
```
