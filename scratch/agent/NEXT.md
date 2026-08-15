# NEXT work unit (s1240)

HYPOTHESIS-ID: generated-save-account-naming-sweep

The external retail-entry dependency remains open: the adjacent Mupen64Plus
frontend source, installed `--savestate` binary invocation, and existing state
files were audited in s1239 and add no unmatched handoff. Do not build or run.
Proceed with one bounded generated-symbol naming sweep in the save/account
region, using the companion decomp names and generated call sites.

Competing hypotheses and discriminator:

- H1: a bounded save/account region has exact companion mappings sufficient to
  rename a coherent function family without invented semantics.
- H2: mappings are partial or ambiguous, so only exact names can be safely
  applied and the remainder stays `func_*`.
- H3: the region has no usable independent naming source and should be parked.

Discriminator: one table covering every `func_*` symbol in the selected region,
with generated address, companion name/source, callers, and confidence. A
complete exact mapping selects H1; only a subset safe to rename selects H2;
absence of independent names selects H3. No code or runtime mitigation is
justified by this sweep.

Exact commands after the artifact is supplied:

```
rg -n 'func_[0-9A-Fa-f]{8}' RecompiledFuncs/funcs_*.c | rg '8005|8006|8007'
rg -n -C 3 'save|account|EEPROM|func_[0-9A-Fa-f]{8}' ../rogue_squadron64 docs/game-architecture.md syms
sed -n 'START,ENDp' RecompiledFuncs/funcs_N.c
```
