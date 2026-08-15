# NEXT work unit (s1254)

HYPOTHESIS-ID: generated-symbol-renaming-sweep

The external retail-entry dependency remains open. Do not build or run.
Perform one bounded generated-symbol naming sweep over the next adjacent
controller-helper region, `0x8007A068..0x8007A260`. Record address, size,
generated definition, companion name/source, callers, and confidence before
editing. Synchronize only exact names in `syms/rogue_squadron.syms.toml`.

Competing hypotheses and discriminator:

- H1: every real function in the region has an exact independent companion
  mapping, so the coherent helper family can be synchronized.
- H2: mappings are partial or ambiguous, so only an exact subset is safe and
  the remainder stays address-encoded.
- H3: no independent naming source exists and this region should be parked.

The discriminator is the complete comparison table: full exact coverage
selects H1, a safe exact subset selects H2, and no independent names selects
H3. No runtime mitigation or experiment is justified.

Exact commands:

```
rg -n '8007A068|8007A0A8|8007A0E8|8007A0F0|8007A260' ../rogue_squadron64/symbol_files/main_overlay.txt syms/rogue_squadron.syms.toml ../N64Recomp/RecompiledFuncs/funcs_19.c
rg -n -C 3 'getControllerStickXPercentage|getControllerStickYPercentage|sampleRgbBoxFilter2x2AtSubpixel|downscaleImageHalfResBoxFilter' ../rogue_squadron64/symbol_files/main_overlay.txt
rg -n '8007A068|8007A0A8|8007A0E8|8007A0F0|8007A260' ../N64Recomp/RecompiledFuncs/funcs_*.c
```
