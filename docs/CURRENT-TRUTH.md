# Rogue Squadron 64 Recomp — current truth

Compact operational state for [PORTING-STATE.md](../PORTING-STATE.md). Historical
detail from s4269 onward is preserved in
[M5-CURRENT-TRUTH-ARCHIVE-s4269.md](M5-CURRENT-TRUTH-ARCHIVE-s4269.md) and the
append-only ledger. This file is intentionally limited to live state,
qualified evidence, open hypotheses, and the next bounded work unit.

Updated for session 4427 (2026-10-09). Session 4415 was a maintenance pass:
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

This iteration repaired that coverage defect in the durable regeneration path:
the fixup now inserts the s3500 caller and s3501 pre-call witnesses, and the
regen helper reapplies them after generation. The rebuilt artifact contains
one caller marker and two pre-call markers. A qualified real-audio/LLE run
passed the phase/task/filter controls and emitted 1,001 caller rows and 2,002
pre-call rows in title phase 4, with no crash or abort marker. Port pre-call
values included `0x801919B0`, `0x801772F0`, and `0x80175960`; the independent
retail s3501 boundary had `0x801772F0` in all sampled title rows. This selects
H-divergence-before-selector and closes H-witness-mismatch; the next boundary
is the writer/initializer of the `0x80150000` selector table or its index.
ORIGIN: generated marker census plus phase-keyed runtime witness; the probes
only observed registers and table loads, and no selector state was rewritten.

Session 4420 attempted the selector-table writer boundary with the repaired
caller/pre-call witness, selector input, phase, task, image, and filter
controls. Title phase 4 and hangar phase 5 controls were live; caller/pre-call
emitted 1,008/2,016 rows and selector input emitted 2 rows. The table-store
and store-context hooks emitted zero rows. A static census confirms their
standalone apply scripts are not wired into the durable regeneration path, so
this selects H-join-failure/instrumentation coverage rather than H-init-route
or H-writer-value. The run reached hangar, then hit the native VI-retrace bus
error family; that crash is not selector evidence. ORIGIN: phase-keyed host
controls and a static script/artifact census; no table value was rewritten,
skipped, or guarded.

Session 4421 wired the existing table-store and store-context transforms into
the durable regeneration helper, reapplied them to the live generated artifact,
and rebuilt successfully. The static artifact contained four expected markers.
A 90-second real-audio/LLE capture passed phase, task, image, filter, and
no-crash controls: table-store and store-context emitted 4/4 rows, caller and
pre-call emitted 1,007/2,014 rows, selector input emitted 2 rows, and the
capture reached title phase 4 and hangar phase 5. Port stores were
`0x80149758=0x80171CE0` and `0x8014975C=0x80173B20` in title, then
`0x80149758=0x80171E70` and `0x8014975C=0x80173CB0` in hangar. This closes
H-join-failure and proves the writer boundary is live; it does not yet select
H-writer-value versus H-index-value because the paired retail store values and
an explicit store-to-load join were not captured in this unit. ORIGIN: durable
generated-marker census plus phase-keyed runtime witnesses; the probes only
observed stores, contexts, inputs, and later loads, and no value was rewritten,
skipped, or guarded.

Session 4422 paired the live port witnesses with the retail oracle's physical
table-write watches and selector-load execution watch. Whole-RDRAM, title and
hangar VI, and selector-load controls were live in both arms. Retail performed
no `0x80149758/0x8014975C` stores in title phases, then performed the two
hangar stores with values `0x80171E70/0x80173CB0`; the port performed title
stores `0x80171CE0/0x80173B20` and the same hangar values. This selects
H-init-route over H-writer-value and closes H-join-failure for this boundary.
ORIGIN: retail physical write callbacks/post-store summaries and port
phase-keyed generated hooks; no table value was rewritten, skipped, or guarded.

Session 4423 reran the title-initializer capture with the required oracle
emulator mode and widened execution-range witness after the first recipe lacked
the hangar positive control. The corrected run passed whole-RDRAM, title and
hangar VI, and selector-load controls: retail selector-load PC
`0x80091060` executed 1,421 times and the widened range executed 20,063,244
times. Retail performed zero stores to physical `0x00149758/0x0014975C` in
both title buckets, but performed six stores to each in hangar at
`0x8008F228/0x8008F264`, with values `0x80171E70/0x80173CB0`. The port arm
independently emitted title and hangar stores and remained crash-free. This
left retail title preinitialization versus a title bypass unresolved. The
initial uncorrected capture is invalid for this distinction because its
retail hangar writer control was zero. Session 4425 resolved it.
ORIGIN: retail physical write callbacks, retail execution watches, and port
phase-keyed generated hooks; no table value was rewritten, skipped, or guarded.

Session 4424 passed those controls but did not sample the pre-title stores.
Title `0x80091064` loads returned `0x80171CE0` and `0x80173B20`, the title
writer buckets were empty, and the only lifetime writer PCs were
`0x8008F228`/`0x8008F264` (six stores each). `v0` at `0x80091060` is the slot
index shifted left by 2. Post-value arms only at the first title or hangar
VI, so the earlier stores had no values. That capture cannot choose between
a pre-title store and DMA or the initial image.

Session 4425 recorded every store with `--store-field-dump-any-phase`.
Whole-RDRAM, both title origins, hangar VI, and 3,734 selector-load
executions were live. Each word was stored eight times, all by those two
PCs, and all eight rows were kept. Both words started at 0. On the last
640-wide frame, origin `0x00790500`, before the 1024 title switch,
`0x8008F228` stored `0x80171CE0` over `0x8018DD30` and `0x8008F264` stored
`0x80173B20` over `0x8018FB70`. The following title loads returned those
pointers (629 and 628). The same PCs later stored the known hangar pointers.
This selects H-pretitle-same-writer and refutes DMA, the initial image, and
a title-phase bypass for these two words. Which title origin consumes which
word swapped relative to the s4424 capture; the stored words did not.
Straight-line code does not write `v0` between `jal 0x80001ACC` and either
store. That callee returns `s2`, and `0x80001C10` is `addiu s2, a1, 16`.
ORIGIN: retail physical store callbacks and ROM disassembly; no table or
heap value was rewritten, skipped, or guarded.

Session 4426 selected H-freelist-header. A deferred watch on `0x80001C10`
armed on the single `0x00790500` VI and missed the stores. The corrected
capture armed execution watches at the first VI and printed only while that
origin was live. Whole-RDRAM, both establishing stores, the title VI switch,
and 33/33 executions of `0x80001C10`/`0x80001C14` were in that run. The calls
returning to `0x8008F218` and `0x8008F244` had headers `0x80171CD0` and
`0x80173B10`; `s2` after `addiu s2, a1, 16` was the stored pointers. All 33
post-addiu rows had `s2 == a1+16`. Both requests were `0x1E30` with flags 0.
Free sizes `0x232C0` and `0x21480` satisfy `0x232C0 - 0x1E30 - 16 = 0x21480`,
and the second header is the first user pointer plus `0x1E30`. The two title
pointers are the user halves of one split free block. The publisher does not
fill those bytes. ORIGIN: retail execution and store callbacks; no heap or
table value was rewritten, skipped, or guarded.

Session 4427 selected H-residual for the post-publish window. Whole-RDRAM,
both title-pointer stores, and the title `0x80091064` loads were live
(232 returns of each pointer). This run's publish was width 640 origin
`0x00790A00`, not `0x00790500` (that origin had zero VI). No CPU store
hit either user word between those publishes and the first title load, and
the words were already `0x6D61745F` / `0x6C746578` at the publish and at
that load. The same sample was zero at the previous table publish and
changed again when `sh zero, 0(v0)` at `0x80091078` cleared the first
halfword after the load, so the sample is not stuck. The only earlier
stores are four `sb` each at `0x80007670` while origin was `0x00696600`:
the bounded copy at `0x80007640`, called from `0x80022B44` with length 16,
destinations already `0x80171CE0` (t=7.3s) and `0x80173B20` (t=9.4s).
Lifetime counts reconcile to those four stores plus post-load writers
only. A DMA fill inside the window is ruled out by the unchanged sample.
Whether that copy wrote a live block later freed, or memory that was
already free, is the open boundary. ORIGIN: retail store callbacks and
paired memory samples; no heap or table value was rewritten, skipped, or
guarded.

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
  artifact did not contain those probe calls. Session 4419 restored them.
- The two title table words are not supplied by DMA or the initial image,
  and the title phase does not bypass their store. s4425 saw both words
  start at 0 and receive `0x80171CE0`/`0x80173B20` from `sw v0` at
  `0x8008F228`/`0x8008F264` on the last 640-wide frame. Empty title writer
  buckets were real; the writer runs one VI mode earlier.
- Those stored words are not produced by a path other than `addiu s2, a1, 16`.
  s4426 saw `s2` become `a1+16` on the next instruction for both establishing
  calls and for every other allocation on that frame. A different `s2` was
  believable only because a breakpoint on the addiu itself samples `s2`
  before the instruction runs.
- The title user words are not filled between pointer publish and the first
  title selector load. s4427 saw zero CPU stores there, and the bytes were
  already the earlier copy. A post-publish filler was believable because the
  publisher returns without writing the user bytes.

## Next steps

1. **Decide whether the earlier copy wrote a live block** —
   HYPOTHESIS-ID `m5-selector-copy-lifetime`. The bytes at the first title
   load were written by `sb` at `0x80007670` (copy `0x80007640`, caller
   `0x80022B44`, length 16) into `0x80171CE0` / `0x80173B20` at origin
   `0x00696600`, seconds before those pointers were published. Malloc's
   header is a halfword at +0 (bits `0x1` and `0x8` are tested) and a size
   word at +4; the user pointer is header+16. On retail, sample those two
   header fields at the copy and at the establishing `sw`, and record every
   store to them in between. A free-size header at the copy selects a write
   into the block malloc later returns. An allocated header at the copy,
   then a free, then the establishing malloc, selects a previous owner. An
   unchanged allocated header at both samples contradicts the fresh split.
   Keep whole-RDRAM, both pointer stores, and one title `0x80091064` load
   whose `v0` is one of those pointers. Do not rewrite or guard heap state.
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
