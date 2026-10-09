# Rogue Squadron 64 Recomp — current truth

Compact operational state for [PORTING-STATE.md](../PORTING-STATE.md). Historical
detail from s4269 onward is preserved in
[M5-CURRENT-TRUTH-ARCHIVE-s4269.md](M5-CURRENT-TRUTH-ARCHIVE-s4269.md) and the
append-only ledger. This file is intentionally limited to live state,
qualified evidence, open hypotheses, and the next bounded work unit.

Updated for session 4417 (2026-10-09). Session 4415 was a maintenance pass:
the prior 891-line version exceeded the 60 KB threshold and its repeated
session narrative was compacted here; no experiment was run.

## Current state

The qualified native route boots through attribution, N64 logo, intro
cinematic, Factor 5 logo, title VI 1024 (`0x00790400`) and hangar VI 512
(`0x006AB400`) on the real-audio/LLE/ungated/solo/spin-yield route. Hangar
geometry and colour artifacts remain. `ROGUESQ_AUDIO_UCODE=0` is the silent
control. VI 640 is the intro, not a stuck state.

Audio is no longer a zero-output stub on the qualified route. Fresh 7F saves
produce nonzero PCM; reset `build/saves` before audio A/B and use
`RS64_EEP_TRACE=1`. AI byte order is fixed (`p[i ^ 3]`, `queue_samples ^ 3`);
title AI buffers matched ucode output in the qualified capture. MusyX/MORT is
still only partially de-stubbed and must not reach stock `aspMain`.

The full regeneration flow remains unsafe since s4204: `N64Recomp ->
fixup_game_funcs.py` aborts at the E088 anchor and can clobber live generated
functions. Use the existing `tools/apply_s*.py` workflow unless regeneration
is explicitly repaired.

## M5 selector/decode boundary

M5 Step 9 is at a qualified retail selector/decode boundary. The port's
descriptor/filter route is reachable at generated callsite `0x8009D740`; the
seeded silent/real matrix reaches hangar and has independent MORT, whole-RDRAM,
and VI controls. Its later descriptor pointers, words, type/class sequence,
source/output hashes, and branch fields diverge between arms. This rejects a
post-filter-only explanation and leaves the pre-filter stream/selector
boundary open.

Session 4414's qualified retail range capture passed the whole-RDRAM positive
control (198,459 reported hits), completed 4,476 VI, and retained 629/628/538
type-2 task rows in title `0x00790400`, title `0x00790800`, and hangar
`0x006AB400`. The selector-family range executed in all three phases. Title
execution entered at `0x80029E80` from `0x8008EE84`, while exact
`0x80029E78` and its `0x80091CB8` predecessor occurred only in hangar. This
selects H-title-selector-alternate-entry over title bypass/absence for the
qualified retail route. Session 4416's port witness instead entered exact
`0x80029E78` in title and hangar, with no `0x80029E80` hits. This selects a
port/retail selector-path divergence, not port corroboration. ORIGIN: the
oracle observed guest
PCs, predecessor PCs, task fields, VI origins, and physical whole-RDRAM
callbacks; no value was skipped, rewritten, or guarded.

Session 4413's selector/payload capture passed the whole-RDRAM control (19,054
callbacks), completed 4,482 VI, and retained 629/628/691 type-2 task rows in
the same three buckets. The task publication witness was live in every
bucket, but exact selector `0x80029E78` executed only in hangar (two
executions, one retained field row: selector `0x561F`, object/argument
`0x5622`). This rules out a global source/task route null, but did not split
multiplex from phase-specific selection until s4414 widened the range.

The qualified port route independently reaches the title-side direct edge
`0x80091CB8` before the first hangar VI transition, with input `0x561F` and
argument `0x5622`; later hangar boundary/input/source/store/task witnesses are
live. Title and hangar use distinct task payload families. Retail evidence
also identifies phase-specific earlier writers and later transforms, but the
intermediate selector/decode transform remains open. These conclusions are
qualified only when the positive control, phase markers, and task/image joins
are live in the same run.

Session 4416's qualified port witness passed the input control, title and
hangar VI controls, and task/image joins; it retained 1,502 audio-task rows,
1,502 task joins, and 256 filter joins, with no crash or abort marker. Exact
selector `0x80029E78` fired 3 times in title phase 4 and 2 times in hangar
phase 5; alternate entry `0x80029E80` fired zero times. This is the second
evidence line selecting port/retail selector-path divergence. The title-side
pre-filter boundary remains open. ORIGIN: the port runtime recorded generated
guest PCs and phase-keyed controls; no value was skipped, rewritten, or
guarded.

Session 4417's paired capture passed the retail whole-RDRAM control (10,000-hit
threshold), retail VI/task controls, and the port input, VI, selector, and task
controls. Retail again showed `0x8008EE84 -> 0x80029E80` and the
`0x80091CB8 -> 0x80029D20` predecessor edge. The port selector fired twice in
title and once in hangar, with matching `0x561F` input rows, but its existing
caller and precall witnesses fired zero times. This rules out a global port
route absence, but the caller/precall comparison is unevaluable: the missing
port witness could be an instrumentation-path mismatch rather than a guest
path divergence. ORIGIN: retail debugger execution/GPR/VI/task observations
and port phase-keyed runtime observations; no selector, input, task, or output
value was rewritten, skipped, or guarded.

The s4418 static witness census resolved that unevaluable result: the current
generated `RecompiledFuncs/funcs_24.c` contains the live `0x8009131C`,
`0x8009132C`, and `0x80091330` edge, but contains zero
`rs64_m5_selector_caller` or `rs64_m5_selector_precall` invocations and zero
s3500/s3501 markers. The host callbacks exist only in
`src/main/upstream_compat.cpp`, while the standalone apply scripts still
describe insertions absent from the generated artifact. This selects
H-witness-mismatch and invalidates the prior caller/precall zero as evidence
of guest divergence. ORIGIN: static generated-file and script census; no
runtime value or control flow was changed.

## Other live lines

The graphics-side framebuffer-set growth root is a bump-time DPC ring-lap
placeholder drop; `ROGUESQ_WRAP_RESTORE` reduced ODD colour-image events from
60 to 0 in three runs, but hangar impact remains unqualified. Do not broaden
this line ahead of M5 selector work.

The VI-640 crash family and M3 guard classes are parked. No mitigation is
authorized without an ORIGIN naming the writer and assessing whether the
value is legitimate. M3 pre-publication guard runtime qualification is blocked
until a host with `mips64-elf-gcc`, `mips64-elf-ld`, and `PatchesLib` is
available.

## Superseded and closed conclusions

- The title selector is not globally absent: s4414's widened retail range
  executed the selector family in all three phases.
- The s4413 title zero was not proof of a title route null; s4414 found the
  alternate entry `0x80029E80` from `0x8008EE84`.
- Earlier C904/task zeroes were instrument-boundary failures, repaired by
  widening/repairing the capture. They do not identify a missing consumer.
- The port's missing middle-title VI origin is a qualified direct transition,
  not an instrument failure; title `0x00790400` transitions directly to
  hangar `0x006AB400` on this route.
- Audio-disabled paths, framebuffer presentation, LLE/HLE mixing, queue
  contention, and the prior hangar-yield interpretation are not the current
  selector/decode explanation. See the archive and ledger for the evidence.
- The s4417 caller/precall zero is not a guest-path result: the generated
  artifact does not contain those probe calls. It remains a probe coverage
  defect until the regeneration-safe insertion is restored and qualified.

## Next steps

1. **M5 pre-filter selector/decode boundary** — HYPOTHESIS-ID
   `m5-selector-decode-boundary`. Repair the regeneration-safe insertion path
   for the `0x8009131C/0x8009132C/0x80091330` caller/precall witnesses, then
   build and qualify the actual edge with the existing selector/input, VI, task,
   and image controls. Do not interpret a caller/precall zero as guest
   divergence until the generated artifact contains the markers and a positive
   control proves them live.
2. **M3 pre-publication guard runtime qualification**, blocked until a host
   with the MIPS toolchain and `PatchesLib` is available.
3. **Generated-symbol renaming sweep**, slug
   `generated-symbol-renaming-sweep`, only when items 1–2 are inapplicable;
   mapping-only edits do not reset the engineering-change gate.

## Evidence boundary and operating rules

Retail oracle watches are physical-address ground truth. Whole-RDRAM, VI, and
target-PC controls qualify coverage; a route failure invalidates a null. Every
instrument needs an independent witness, same-run positive control,
phase-scoped budget, and (before promotion to truth) a second evidence line.
Phase-gate animated comparisons on VI transitions and batch A/B arms in one
build/run.

Use [F5-UCODE-REFERENCE.md](F5-UCODE-REFERENCE.md), not standard F3DEX
assumptions. The graphics path is LLE-only. Keep safety guards separate from
explanations. Regeneration order is `make_elf.py -> N64Recomp ->
fixup_game_funcs.py -> CMake`; never hand-edit generated functions for
behavior. If `lib/` changes, export submodule patches. Never run submodule
update, checkout, clean, or hard reset. Kill runs with SIGKILL and run from
`build/`. Any mitigation-shaped change needs an `ORIGIN:` line naming its
writer and whether the value is legitimate.

## Evidence index

[M5-AUDIO-PLAN.md](M5-AUDIO-PLAN.md),
[M5-CURRENT-TRUTH-ARCHIVE-s4269.md](M5-CURRENT-TRUTH-ARCHIVE-s4269.md),
[PROJECT-OVERVIEW.md](PROJECT-OVERVIEW.md), and the append-only detailed
ledger in [PORTING-STATE.md](../PORTING-STATE.md). Use bounded grep/sed
windows for the ledger; do not read it whole.
