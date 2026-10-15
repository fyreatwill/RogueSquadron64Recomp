# M3 s4998 — register-target indirect-call source audit

## Work unit and discriminator

This iteration pivoted away from `voice-count-before-base-race` after three
stalled iterations. The new hypothesis was that the remaining non-`$ra`
indirect-call sites could hide a recompiler lowering defect or a silent
misdispatch. The discriminator was a complete census of every generated
`LOOKUP_FUNC(ctx->rN)` site, classified by the most recent local register
definition, paired with the existing direct `jr/jalr` census and a runtime
search for missing-function markers.

Competing outcomes were: (1) a reachable malformed lowering or silent target,
which would require a focused recompiler fix; (2) valid memory/function-table
dispatches, which closes the class; or (3) unresolved data-as-code/callback
sites, which remain a bounded evidence gap rather than a mitigation target.

## Evidence

Commands run against `/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs`:

```text
python3 tools/census_indirect_calls.py ...
  register-target sites: 113
  constant-target sites: 28185
  classified: mem-load=42, other=11, unresolved=57, arith=3
  functions: 47

python3 tools/census_indirect_jump.py ...
  jump-table switches: 177
  switch_error defaults: 177
  $zero sites: 114
```

The independent instruction census reports 177/177 jump-table defaults with
`switch_error`, and all 114 `$zero` targets remain in the already identified
data-as-code regions (`audioCompandS16`, `data_gap_800CC3D4`, static tables,
and `__OSGlobalIntMask`). The register-target source census found no emitted
silent fallback: each site uses `LOOKUP_FUNC`, which resolves through the
runtime's loud missing-target path. The 57 locally unresolved sites are
callback/function-pointer calls or malformed/data-as-code regions; examples
include `binarySearchWithComparator`, `musyxSynthFrame_s4562_impl`, the
`inflate_*` callback family, `_Printf`, and the known audio/data gaps.

As a second, independent runtime check, the available soak-log search found
no `Failed to find function` or `missing function` marker. It found only
Factor 5 microcode `Unhandled jump target` messages, which are a separate RSP
interpreter path and not evidence against this CPU indirect-call census.

## Result

No reachable CPU indirect-call lowering defect or silent dispatch path was
selected. The class is closed for M3 purposes. No guard, skip, or value rewrite
is authorized. The unresolved local-source rows remain useful only if a future
run produces a CPU missing-function marker or a new caller-specific witness.
