# NEXT work unit (s1253)

HYPOTHESIS-ID: generated-symbol-renaming-sweep

The external retail-entry dependency remains open. Do not build or run.
Proceed with one bounded generated-symbol naming sweep over the next adjacent
controller-helper region, `0x80079CD8..0x8007A034`, using companion names and
generated declarations. Cover every generated function through the next
coherent helper boundary and synchronize only exact names.

Before editing, record the complete comparison table with address, size,
generated definition, companion name/source, callers, and confidence.

Competing hypotheses and discriminator:

- H1: every real function in the region has an exact independent companion
  mapping, so the whole coherent helper family can be synchronized.
- H2: mappings are partial or ambiguous, so only exact names can be safely
  synchronized and the remainder stays `func_*`.
- H3: the region has no usable independent naming source and should be parked.

The discriminator is the table itself: complete exact coverage selects H1, a
safe exact subset selects H2, and no independent names selects H3. No runtime
mitigation or experiment is justified.

Exact commands:

```
rg -n '80079CD8|80079CE0|80079D54|80079EB0|80079EF4|80079F20|80079F50|80079F70|80079FD8|8007A000|8007A034' ../rogue_squadron64/symbol_files/main_overlay.txt syms/rogue_squadron.syms.toml ../N64Recomp/RecompiledFuncs/funcs_19.c
rg -n -C 3 'setNewAndPreviousButtonsPressed|getControllerButtonAndStick|initNewAndPreviousButtonsPressed|getControllerNewButtonsPressed|isControllerStickReady|pollControllerUntilButtonsLatched|getControllerStickXPercentageGated|getControllerStickYPercentageGated' ../rogue_squadron64/symbol_files/main_overlay.txt
rg -n '80079CD8|80079CE0|80079D54|80079EB0|80079EF4|80079F20|80079F50|80079F70|80079FD8|8007A000|8007A034' ../N64Recomp/RecompiledFuncs/funcs_*.c
```
