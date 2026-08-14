# NEXT work unit (s931)

HYPOTHESIS-ID: m3-audio-rsp-mixer-class

Audit the complete `initN64RspMixer` idiom at `0x8009189C` in
`../N64Recomp/RecompiledFuncs/funcs_24.c`, including every generated caller,
all helper calls, loop bounds, global/table writes, and input clamps.
Source-only; do not add a guard, change game behavior, build, or run a soak.

Competing hypotheses:

- H-rsp-mixer-unclassified: a caller or initialization path supplies an
  invalid count/pointer/derived size or reaches an unsafe helper edge.
- H-rsp-mixer-classified: callers agree, count clamping is bounded, and all
  allocation/table-write/helper paths have fixed safe contracts.
- H-rsp-mixer-shape-mismatch: callers or helper paths use distinct contracts;
  record the exact split and stop.

Discriminating measurement: enumerate every `initN64RspMixer` reference,
caller register setup, complete callee control flow, helper signatures, loop
termination, derived allocation sizes, and every global/table write; cross-
check `main_overlay.txt` and the complete generated helper. Any caller-shape
split, unbounded walk, data-derived unsafe edge, or unbounded derived size
rejects classification.

Exact commands: `rg -n -C 8 "initN64RspMixer|8009189C|9189C" ../N64Recomp/RecompiledFuncs/funcs_24.c ../rogue_squadron64/symbol_files/main_overlay.txt`, then inspect the complete helper and every reference. No game build or soak is planned.
