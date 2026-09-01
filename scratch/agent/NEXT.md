# NEXT work unit — identify the malformed pre-title HMT input

HYPOTHESIS-ID: m5-preclear-caller-input-producer

Session 3547 selected `H-CaptureInvalid` for the new caller comparison: the
retail oracle was phase-valid, but the real-audio port SIGBUSed in
`parseHmtMaterials+3588` before target entry. Do not repeat the caller table
until the port route is phase-valid.

Do exactly one bounded work unit: add a regeneration-safe, phase-independent
entry table for `loadDebugAssets` -> `registerHmtTextureInTable` ->
`parseHmtMaterials`, rebuild once, and run the canonical real-audio route once.
Capture every call's pointer/index/count tuple and the first malformed pointer
before the existing crash. Preserve all existing witnesses and keep all audio,
PCM, image-task, output, and texture-record writes unchanged.

Competing hypotheses and discriminator:

- `H-HmtInputValid`: all three entry tuples are valid and the route reaches a
  target VI; the caller/input table can be rerun.
- `H-HmtInputMalformed`: a specific pre-title tuple or pointer is outside the
  mapped RDRAM range before `parseHmtMaterials`; that producer is the next
  correction boundary.
- `H-HmtEntryAbsent`: the positive control or entry table is absent, so the
  capture is invalid and no input conclusion is allowed.

The single discriminating measurement is one joined table containing positive
control, each HMT entry tuple, pointer validity, title/hangar VI, crash PC,
and last guest PC. Valid tuples plus target VI select `H-HmtInputValid`; an
invalid tuple immediately before the crash selects `H-HmtInputMalformed`;
missing controls select `H-HmtEntryAbsent`.

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
