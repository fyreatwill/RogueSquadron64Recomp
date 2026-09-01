# NEXT work unit — resolve the caller/input producer before texture indexing

HYPOTHESIS-ID: m5-preclear-caller-input-producer

Session 3546 selected `H-ProducerDivergence`: retail and port both executed
`loadTextureToMemory`, with a shared family input tuple but divergent formed
indices and record pointers. Do not repeat the destination or producer capture.

Do exactly one bounded work unit: instrument the caller/input edge immediately
before `loadTextureToMemory` at retail predecessor `0x80022ACC`, including its
arguments/returns and the input fields used to form the `0x8001FAA0` index.
Run one independent retail execution watch and one same-build real-audio port
capture. Keep all audio, PCM, image-task, output, and texture-record writes
unchanged.

Competing hypotheses and discriminator:

- `H-CallerParity`: caller inputs/returns match and the remaining gap is
  earlier than the caller.
- `H-CallerDivergence`: the caller input or returned producer state differs
  before index formation.
- `H-RetailOnlyFamily`: retail executes the caller/family in the target phase
  but the port does not; the observed port rows belong to another route/use.
- `H-CaptureInvalid`: whole-RDRAM and both phase controls or the paired family
  witnesses are absent.

The single discriminating table must include caller PC, predecessor, phase/VI,
caller inputs/returns, the fields feeding the index, and the first family
store. A matching caller tuple selects `H-CallerParity`; a first differing
input or returned field selects `H-CallerDivergence`; retail-only execution
selects `H-RetailOnlyFamily`; missing controls select `H-CaptureInvalid`.

Before building, retain `scratch/agent/retail_preclear_groundtruth.log` and
read the existing producer injection in
`/Users/williambuckley/Documents/Tools/N64Recomp/fixup_game_funcs.py`.
Batch the instrumentation, then build and run both oracle and port arms in one
iteration. Use VI phase gates, SIGKILL cleanup, and capture under:

    scratch/agent/s3546_m5_caller_input_producer

The intended oracle arm is `tools/oracle/build/rs64_oracle` with
`--watch-write 0x0:0x800000`, the retained source-span watch, and execution
watches for `0x80022ACC`, `0x8001F954`, `0x8001FAA0`, `0x8001FAB4`, and
`0x8001FAC4`, phase-gated to origins `0x00790400:1024` and
`0x006AB400:512`. The port arm must enable the new caller witness on the
validated real-audio route. Positive controls and both target VIs are required
before interpreting a missing caller row.
