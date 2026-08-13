# NEXT work unit (s858)

HYPOTHESIS-ID: m3-guest-pc-8000834c-audit

Perform a source-only, whole-idiom audit of the function at guest PC
0x8000834c (`getNextSlotNpcTypeId`) and every generated caller, including all
reads of slot-table links and all return-value consumers. Do not build or run.
The s858 dispatcher trace covered 626 entries / 790 pre/post rows with valid
inputs; the observed death was guest PC 0x8000834c, not the dispatcher.

Competing hypotheses:

- H-link-state: 0x8000834c reads a live but invalid slot-table link or index.
- H-caller-transition: callers pass a corrupted selector/context into the
  helper or consume its result incorrectly.
- H-legitimate: all observed reads and callers are valid; the crash is outside
  this helper's source path.
- H-stale-breadcrumb: the guest-PC handoff does not identify the faulting
  instruction or function.

Discriminator: map every helper read, caller, and consumer. An invalid link
path selects H-link-state; a caller-only bad argument/result use selects
H-caller-transition; complete valid paths with the crash elsewhere select
H-legitimate; an unmappable guest-PC handoff selects H-stale-breadcrumb. No
source-only result authorizes a mitigation without identifying the writer and
legitimacy.

Exact commands:

1. `rg -n -C 8 "getNextSlotNpcTypeId|0x8000834c|jal 0x8000834c|slot-table|80130BB0|80130BC0|80130BC4" ../N64Recomp/RecompiledFuncs src docs`
2. Read bounded windows around the sole helper definition and every caller;
   enumerate each slot/link read and each consumer of the return value.
3. `rg -n "getNextSlotNpcTypeId|8000834c" ../N64Recomp/fixup_game_funcs.py`
4. Record a source verdict and the smallest phase-gated runtime boundary, if
   one exists; do not add instrumentation or mitigation in this unit.
