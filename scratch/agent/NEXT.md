# NEXT work unit (s1259)

HYPOTHESIS-ID: generated-symbol-renaming-sweep

Do not build or run. Perform one bounded generated-symbol naming sweep over the
next adjacent NPC effect region, `0x8007DD94..0x8007E810`. Record address, size,
generated definition, companion name/source, callers, and confidence before
editing. Synchronize only exact names in `syms/rogue_squadron.syms.toml`; leave
any address-encoded or ambiguous entries unchanged.

Competing hypotheses and discriminator:

- H1: all six region functions have exact independent companion mappings, so
  the coherent effect/helper family can be synchronized.
- H2: mappings are partial or ambiguous, so only an exact subset is safe and
  the remainder stays address-encoded.
- H3: no independent naming source exists and this region should be parked.

The discriminator is the complete comparison table: full exact coverage
selects H1, a safe exact subset selects H2, and no independent names selects
H3. No runtime mitigation or experiment is justified.

Exact commands:

```
rg -n '8007DD94|8007DF60|8007E154|8007E360|8007E504|8007E810' ../rogue_squadron64/symbol_files/main_overlay.txt syms/rogue_squadron.syms.toml ../N64Recomp/RecompiledFuncs/funcs_19.c
rg -n -C 3 'emitPresetSparkBurst|updateWalkerLegStrideAndDust|npcWalkerUpdate|submitOrientedEffectMesh|findAndZeroTableSlotMatching|clearFourWordTable' ../rogue_squadron64/symbol_files/main_overlay.txt
rg -n '8007DD94|8007DF60|8007E154|8007E360|8007E504|8007E810' ../N64Recomp/RecompiledFuncs/funcs_19.c
```
