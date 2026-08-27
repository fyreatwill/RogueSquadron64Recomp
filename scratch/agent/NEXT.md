# NEXT work unit (s2741) — census SP yield call sites

HYPOTHESIS-ID: m5-audio-yield-contract

## Work unit

Perform one bounded static census of every generated reference to
`osSpTaskYield_recomp` and `osSpTaskYielded_recomp`. For each reference record
the generated function, guest address, containing file, caller/callee context,
and whether the surrounding path is an audio-task path or a non-audio control
path. Use the census to decide whether a target-phase runtime validation is
still meaningful; do not modify generated behavior.

## Competing hypotheses and discriminator

- H-yield-audio-callsite: at least one yield API reference is on an audio-task
  path, so the failed runtime reachability remains the only missing evidence.
- H-yield-non-audio: all references are on graphics, scheduler, or unrelated
  control paths, making an audio-task validation unsupported by current code.
- H-yield-no-reference: the generated snapshot has no references because the
  API is only a runtime symbol; the next action must then be a symbol/linkage
  audit rather than another phase-gated run.

The discriminator is the complete reference table, with every possible result
classifying all call sites into audio-task, non-audio, or no-reference. This
is static evidence only; no conclusion about actual yielding is allowed.

## Exact commands

```sh
rg -n "osSpTaskYield(_recomp|ed_recomp)" RecompiledFuncs build/factor5_ucode \
  > scratch/agent/s2741_yield_callsite_census.txt
rg -n "osSpTaskYield(_recomp|ed_recomp)" RecompiledFuncs build/factor5_ucode \
  | cut -d: -f1 | sort -u
```
