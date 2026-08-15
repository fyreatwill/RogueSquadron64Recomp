# NEXT work unit (s1252)

HYPOTHESIS-ID: generated-symbol-renaming-sweep

The external retail-entry dependency remains open. Do not build or run.
Proceed with one bounded generated-symbol naming sweep over the next adjacent
helper region, `0x80079278..0x80079C10`, using companion names and generated
declarations. Cover every generated function through the next coherent helper
boundary and synchronize only exact names.

Competing hypotheses and discriminator:

- H1: the selected region has exact companion mappings for the generated
  function(s), so the coherent helper family can be synchronized.
- H2: mappings are partial or ambiguous, so only exact names can be safely
  synchronized and the remainder stays `func_*`.
- H3: the region has no usable independent naming source and should be parked.

Discriminator: one table covering every generated function in the selected
range, with address, generated name, companion name/source, callers, and
confidence. Complete exact matches select H1; a safe subset selects H2; no
independent names select H3. No runtime mitigation is justified.

Exact commands:

```
rg -n '80079278|80079280|800799C0|80079A70|80079A94|80079BC8|80079C10' ../rogue_squadron64/symbol_files/main_overlay.txt syms/rogue_squadron.syms.toml ../N64Recomp/RecompiledFuncs/funcs_18.c
rg -n -C 3 'heavyMechSubEffectNpcHandler|concatChildTransformAlongChain|initWaterSprayEffectAndSfx|spawnNpcWithRandomRotation|spawnHeavyMechSubEffect' ../rogue_squadron64/symbol_files/main_overlay.txt
```
