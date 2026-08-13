# NEXT work unit (s916)

HYPOTHESIS-ID: m3-voice-pool-reset-inventory

Audit the adjacent generated helper `func_8009BCC4` (`0x8009BCC4`, size
`0xB8`) in `../N64Recomp/RecompiledFuncs/funcs_26.c`. Enumerate its complete
outer/inner scan, calls to `func_8009B268`, slot/global accesses, termination
conditions, return behavior, all generated callers, and companion symbol or
decomp evidence. Do not add a guard, change game behavior, build, or run a
soak.

Competing hypotheses:

- H-voice-pool-reset-unclassified: the helper's repeated scan has an
  unproven termination contract, hidden state dependence, or incompatible
  slot shape between its two phases.
- H-voice-pool-reset-classified: both phases are explicit one-pass scans over
  the same voice-slot active-byte shape, with bounded termination and a
  consistent caller contract.
- H-voice-pool-reset-shape-mismatch: a caller or `func_8009B268` path uses a
  different index/table contract; record the exact split and stop.

Discriminating measurement: a complete instruction/site table for
`func_8009BCC4`, its direct callers, the callee `func_8009B268` contract, and
the companion symbol/decomp basis. Any omitted memory access, non-terminating
counter path, or incompatible caller/callee shape rejects full
classification.

Exact commands: use `rg` to enumerate `func_8009BCC4`, `func_8009B268`, and
their callsites in `../N64Recomp/RecompiledFuncs/funcs_26.c`, then bounded
`sed` windows and companion `rogue_squadron64`/symbol files. No game build or
soak is planned.
