# NEXT work unit (s924)

HYPOTHESIS-ID: m3-decode-voice-block-class

Audit the complete MusyX `decodeAndFillVoiceBlock` idiom at `0x8009C904`:
all input/output pointer arithmetic, block-index derivation, loops and
termination, every generated caller, and companion symbol/decomp evidence.
Source-only; do not add a guard, change game behavior, build, or run a soak.

Competing hypotheses:

- H-decode-voice-unclassified: a decode site has an unchecked or incompatible
  pointer/record shape, unsafe index arithmetic, or an unbounded termination
  path.
- H-decode-voice-classified: the helper has a coherent slot/table contract,
  bounded control, and all callers pass the same shape; only dynamic value
  legitimacy remains open.
- H-decode-voice-shape-mismatch: a caller or sibling path uses a distinct
  buffer/index/slot contract; record the exact split and stop.

Discriminating measurement: a complete helper table of every memory access,
derived index and pointer, loop/termination condition, all direct callers and
argument setup, plus companion basis. Any omitted access, unsafe derivation,
unbounded loop, or incompatible caller shape rejects full classification.

Exact commands: use `sed` around the definition/caller in
`../N64Recomp/RecompiledFuncs/funcs_27.c`, `rg` for every generated reference,
then inspect the matching `main_overlay.txt` entry and any companion body.
No game build or soak is planned.
