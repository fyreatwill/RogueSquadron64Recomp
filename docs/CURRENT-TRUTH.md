# Rogue Squadron 64 Recomp — current truth

Compact operational state for [PORTING-STATE.md](../PORTING-STATE.md). Historical
detail from s4269 onward is in [PROJECT-OVERVIEW.md](PROJECT-OVERVIEW.md) and
[M5-CURRENT-TRUTH-ARCHIVE-s4269.md](M5-CURRENT-TRUTH-ARCHIVE-s4269.md).

Updated for session 4378 (2026-10-09). The preceding maintenance pass reduced
this file to durable state; session 4357 qualified phase coverage but exposed a
retail task-join instrument boundary.

## Current state

The qualified native route boots through attribution, N64 logo, intro cinematic,
Factor 5 logo, title VI 1024 (`0x00790400`) and hangar VI 512 (`0x006AB400`)
on the real-audio/LLE/ungated/solo/spin-yield route. `ROGUESQ_AUDIO_UCODE=0`
is the silent control. VI 640 is the intro, not a stuck state. Hangar
geometry/colour artifacts remain.

Audio is no longer a zero-output stub on the qualified route. Fresh 7F saves
produce nonzero PCM; reset `build/saves` before audio A/B and use
`RS64_EEP_TRACE=1`. AI byte order is fixed (`p[i ^ 3]`, `queue_samples ^ 3`);
876/894 title AI buffers matched ucode output in the qualified capture.
MusyX/MORT remains only partially de-stubbed and must not reach stock
`aspMain`.

M5 Step 9 is at a qualified retail selector/decode boundary. The port's
descriptor/filter route is reachable at generated callsite `0x8009D740`; the
seeded silent/real matrix reaches hangar and has independent MORT, whole-RDRAM,
and VI controls. Its later descriptor pointers, words, type/class sequence,
source/output hashes, and branch fields diverge between arms. This rejects a
post-filter-only explanation and leaves the pre-filter stream/selector
boundary open.

Session 4360's qualified range-argument capture passed the whole-RDRAM control,
reached title and hangar, and retained 512 rows in each phase bucket
`0x00790400:1024`, `0x00790800:1024`, and `0x006AB400:512`. In every bucket,
`0x80033FCC` received `$a0=0x80149470` with `MEM_W($a0)=2`; its task dump
recorded 1,776 type-2 rows and 1,133 non-type-2 rows, while the C904/C950
join recorded 356,986 matches. This single-source retail-oracle result selects
H-consumer-nearby and rules out an absent nearby type-2 consumer or the prior
instrument boundary for this route. It does not yet distinguish a pre-filter
origin from a consumer payload/layout transform; the next probe must compare
the joined task payload fields against the C904/C950 input and selected fields.

Session 4361's payload capture passed the whole-RDRAM control (10,000 retained
hits), reached title origins `0x00790400` and `0x00790800` and hangar origin
`0x006AB400`, and recorded 1,786 type-2 rows at `0x80033FCC` (628/628/530
live task rows by those phase buckets). In the retained C904/C950 joins, the
task pointer was shared (`0x80149470`) and the selector input was constant
(`0x04001000`, words `0x09000419/0x20010FC0`), while the first eight words at
the joined `data_ptr` varied by phase/data block. This selects
H-selector-multiplex for the qualified title comparison: the shared task
identity and input do not imply a shared payload family. It is single-source
retail evidence only because this capture retained no C904-task summary rows
for hangar despite live hangar task rows; the next probe must repair that join
boundary before promoting the cross-phase conclusion.

Session 4358's repaired C904/C950 join capture passed the retail whole-RDRAM
control and reached the hangar phase. C904/C950 witnesses were live (512
bounded rows), but the existing `0x80033FCC` task watch produced zero task
rows, so the new phase-keyed C904/C950-to-task join produced zero matches and
zero rows. This is a stronger instrument-boundary result: the retail source
boundary is live while the presumed task consumer PC is absent in the same
qualified route. The port arm independently remained live through hangar with
task/ABI and image-DMA joins. It does not select pre-filter origin or
selector-consumer divergence yet; the next probe must locate the actual retail
task consumer PC around the presumed `0x80033FCC` handoff.

Session 4357's established consumer matrix passed the retail whole-RDRAM
control (33,331,419 writes), reached title and hangar, and completed 4,478 VI;
the port reached title 1024 at 13.7 s and hangar 512 at 34.0 s without a
crash/abort. The retail task/field join at `0x80033FCC` produced zero rows,
while the port produced 2,817 ABI rows and 2,812 DMA joins. This is an
instrument-boundary result, not evidence for either stream-origin hypothesis;
the next probe must repair the retail join at the already-qualified C904/C950
witnesses.

Session 4362 repaired that boundary by raising the bounded C904/task retention
table from 512 to 1,536 rows; the first run without Rice was invalid and stayed
at VI 320, while the fixed run passed the whole-RDRAM control (10,000 retained
writes), reached title and hangar, and recorded 1,948 type-2 tasks with 4,490
C904/task matches. Retained rows covered all three buckets: 594 at
`0x00790400`, 595 at `0x00790800`, and 347 at `0x006AB400`. Hangar used
`data_ptr` `0x80171E70`/`0x80173CB0` and payload families rooted at
`0x801797B0`, unlike the title families rooted at `0x80178C80` and
`0x801E2FC0`; the selector input remained `0x04001000` with words
`0x09000419/0x20010FC0`. This repairs the prior instrument boundary and
supports H-selector-multiplex, but the retail capture is single-source and the
pre-filter-versus-consumer-transform distinction remains open.

Session 4363's source-labelled capture passed the whole-RDRAM control and
reached all three required phase buckets. The `0x80033FCC` task watch recorded
628/628/429 type-2 rows for `0x00790400`, `0x00790800`, and `0x006AB400`.
The selector/task join retained the same input pointer and eight input words
(`0x04001000`, beginning `0x09000419/0x20010FC0`) across title and hangar,
while task data pointers and payload families remained phase-specific. The new
C904 source witness was phase-labelled and fired at both `0x8009C904` and
`0x8009C950` in hangar; no C904 decode row occurred in either title bucket.
This supports H-selector-multiplex at the task-family handoff and rules out a
shared selector input implying a shared payload. It remains single-source
retail evidence and does not locate the earlier writer or distinguish a
pre-filter source from a later transform after the task handoff.

Session 4364's union writer capture passed the whole-RDRAM control (10,000
callbacks before removal), reached all three phase buckets (632/632/535 VI
rows), and retained 1,786 type-2 task rows with 3,689 C904/task joins. The
published family addresses were written, but the broad `0x00171000:0x00174000`
watch mixed initialization and maintenance stores with family traffic, so it
did not attribute any one published address. This is a qualified
watch-boundary result, not evidence for H-earlier-producer or
H-post-task-transform. The next probe must watch the four published family
addresses separately in the same phase-gated run.

Session 4365's exact-address capture exposed two setup boundaries before any
writer conclusion was possible. Runs without the Rice video plugin reached
only dummy 320 VI; the corrected Rice run passed the whole-RDRAM control,
reached both title 1024 buckets, and recorded exact writes at all four family
addresses (`0x171CE0`/`0x173B20`: 11,018 each; `0x171E70`/`0x173CB0`: 668
each). It did not reach hangar within the qualified run. The command's
`--pc-hist-watch 1..4` selectors addressed execution watches (the exact memory
watches were indices 5..8), so no exact-address writer histogram was collected.
This is an instrument-boundary result; it selects none of the three hypotheses.
ORIGIN: diagnostic-only exact-address watch; no guest or host value was
skipped, rewritten, or guarded.

Session 4366's final Rice capture corrected the oracle histogram namespace and
passed all controls: 59,327 whole-RDRAM writes, 4,481 VI, both title origins,
hangar origin `0x006AB400`, and 1,933 type-2 task rows. Exact writes were
confirmed at all four published family addresses. Title writer histograms used
`0x80091078`, `0x80091198`, `0x80090DE4`, and `0x80090B68` in phase-specific
combinations; hangar used `0x80090948`, `0x80090958`, `0x80092164`,
`0x8009216C`, `0x80091078`, `0x80090DE4`, and `0x80090B68`. This selects a
phase-specific producer/selector writer family over an absent-watch explanation,
but aggregate histograms do not establish whether each store precedes its
corresponding task publication. The next probe must add a task-ordinal join.
Independent retail evidence only. ORIGIN: named guest PCs are observed
writers; no value was skipped, rewritten, or guarded.

Session 4367's ordinal-join capture passed the whole-RDRAM control (10,000
callbacks), reached 4,486 VI, both title buckets, hangar, and 1,770 type-2
task rows. It retained 23,714 exact family writes with no ordinal overflow.
Joining each write to the nearest same-phase type-2 task publication gave
before/after counts of 8047/1, 482/0, 8033/0, 481/0, 798/0, and 5869/3
across the populated title/hangar family buckets; no join was missing. This
selects H-earlier-producer over H-post-task-transform for the qualified retail
route, but remains single-source evidence because both ordinals come from the
same retail debugger stream. The four after rows are nearest-task boundary
outliers, not enough to reverse ordering. A second independent evidence line
is still required before closing producer provenance. ORIGIN: guest writer PCs
and task-publication PCs are observed; no value was skipped, rewritten, or
guarded.

Session 4368's fixed Rice capture added the oracle post-store scalar witness
to the exact family watches and retained the ordinal join. The first launch
omitted the task execution watch and was rejected with zero task rows. The
fixed run passed the whole-RDRAM control with 63,773 writes, reached all three
phase buckets, and recorded 629/629/687 type-2 rows for `0x00790400`,
`0x00790800`, and `0x006AB400`. It retained 28,713 exact writes with no
overflow. All 16 post-store scalar groups reported `mismatch=0` and
`unsupported=0`; the ordinal join again placed each family class before its
nearest same-phase task except four nearest-task boundary outliers, with no
missing joins. This independently corroborates H-earlier-producer and closes
the absent-writer/watch-boundary explanation for this ordering question. The
payload's pre-filter origin versus a later consumer transform remains open.
ORIGIN: retail guest writer PCs and task PCs are observed; post-store scalar
values are validated with mismatch=0; no value was skipped, rewritten, or
guarded.

Session 4369's selector/payload capture passed the whole-RDRAM control (10,000
callbacks), reached all three phase buckets, and retained 628/629/690 typed
task rows for title `0x00790400`, title `0x00790800`, and hangar
`0x006AB400`. The C904/C950 witness had 4,488 executions and 4,485 matched
task joins (3 unmatched); the task rows had no invalid pointers or overflow.
Canonical selector input remained `0x04001000` with words
`0x09000419/0x20010FC0`, while joined payload families were title-rooted at
`0x80178C80` (often paired with `0x801E2FC0`) and hangar-rooted at
`0x801797B0`. This selects H-selector-multiplex / post-filter consumer
divergence over H-watch-boundary for this capture, but does not establish the
earlier writer or a direct selected-word-to-payload equality; a second
independent evidence line is still required. ORIGIN: retail guest selector
and task PCs are observed with positive-control and phase coverage; no value
was skipped, rewritten, or guarded.

Session 4370's independent physical-payload capture passed the whole-RDRAM
control (10,000 callbacks), reached 4,481 VI and all three required buckets,
and retained 1,775 valid type-2 task rows with 3,673 C904/task matches and
three unmatched witnesses. The oracle's phase snapshots of the first eight
words at `0x80171CE0`, `0x80173B20`, and `0x80171E70` were live in both title
and hangar: title values contained the distinct `mat_10`/`mat_11`,
`ltex_cache_328/329`, and `explh_tex0/1` families, while hangar values changed
to its pointer/data family. Joined task rows independently carried the same
phase-specific roots (`0x80178C80`/`0x801E2FC0` in title and `0x801797B0` in
hangar). This supplies the second evidence line for H-selector-multiplex and
rules out an absent or misaligned physical payload watch. It does not establish
direct selected-word equality or close pre-filter origin versus later consumer
transform. The initial oversized snapshot watches were invalid because the
oracle rejects ranges over 4 KiB; the corrected 32-byte watches are the only
qualified measurement. ORIGIN: retail guest memory snapshots and task joins
are observed; no value was skipped, rewritten, or guarded.

Session 4371's direct selected-word comparison passed the whole-RDRAM control
(102,877 writes), reached 4,477 VI and all three required phase buckets, and
retained 4,483 valid C904/task joins (three unmatched) plus 1,947 typed
`0x80033FCC` rows. Every joined row with a nonzero selected word had no exact
match in the first eight published payload words: 591/591 at `0x00790400`,
601/601 at `0x00790800`, and 344/344 at `0x006AB400`. The four independent
32-byte payload watches also produced live, distinct title/hangar snapshots.
This supplies the second retail evidence line for H-later-consumer-transform
and rules out the remaining watch-boundary explanation for this comparison;
pre-filter origin is not the first eight published payload words. The next
probe must locate the transform/publication boundary rather than repeat this
comparison. ORIGIN: retail selector, task, and physical payload observations;
no value was skipped, rewritten, or guarded.

Session 4372's fixed boundary-PC capture passed the whole-RDRAM control,
reached 7,190 VI, and recorded 1,709 typed `0x80033FCC` task rows with 29,672
C904/task matches and three unmatched witnesses. The existing execution
instrument path was live at C950, C954, D78C/D790, DB2C, and DC38; its retained
field table, however, contained only hangar-phase rows while the task joins
covered title and hangar. The first launch was invalid because `0x80033FCC`
was not included in the execution watch list; the fixed launch corrected that
and still did not produce phase-labelled title rows for the intermediate PCs.
This is an instrument-boundary result: it selects neither transform-before-
publication nor payload-overwrite. The next probe must add an explicit
phase-keyed join for the C950 selected word and the D790/publication fields.
ORIGIN: retail execution, task, and C904 observations; no value was skipped,
rewritten, or guarded.

Session 4373's boundary-join instrument was first invalid because the task
execution watch was omitted, then fixed in the same iteration. The qualified
75-second Rice run passed the whole-RDRAM control (10,000 writes), reached
4,480 VI and all three phase buckets, and recorded 1,959 valid type-2 task
rows with no invalid pointers. C904/task joins were live in title and hangar
(594 rows at `0x00790400`, 601 at `0x00790800`, and 341 retained at
`0x006AB400`). The five intended boundary PCs produced 2,920 phase-keyed rows
with zero missing-task joins, but every retained boundary row was hangar
phase; no C950/C954/D78C/D790/DC38 execution row occurred in either title
bucket. This selects H-phase-instrument-gap for the proposed boundary table:
the title source/task path is live, while these presumed intermediate PCs are
not the title path. It does not select transform-before-publication versus
payload-overwrite and is single-source retail evidence. ORIGIN: retail
execution, task, and C904 observations; no value was skipped, rewritten, or
guarded.

Session 4374's title-range census passed the whole-RDRAM control (10,000
writes), reached 3,490 VI and all three phase buckets, and recorded 1,571
valid type-2 task rows. The range `0x8009C904:0x8009DC3C` was active with
16,264,908 execution hits and 3,361,701 C904/task joins, but its retained
joined rows were hangar-only; title C904/task witnesses remained live in both
1024 buckets. This selects H-title-predecessor over a title overlay alias for
the presumed decode range and rules out a missing title task/C904 route. It is
single-source retail evidence; the next probe must census the title caller
chain around `0x80019C00:0x80019E20`. ORIGIN: retail execution, task, and C904
observations; no value was skipped, rewritten, or guarded.

Session 4375's title-caller census passed the whole-RDRAM control (10,000
writes), reached 4,482 VI and all three phase buckets, and recorded 1,958
valid type-2 task rows with no invalid pointers or overflow. The range
`0x80019C00:0x80019E20` produced 183,862 execution hits; its retained
C904/task rows included title-phase callers in both `0x00790400` and
`0x00790800`, while hangar coverage also remained live. The range's observed
task-call chain includes `0x80019DEC -> 0x80033FCC`, and the typed task join
was live (`matched=121,149`, `unmatched=51`) with title payload families
present. This selects H-title-caller over H-title-predecessor-deeper and
rules out the prior title execution-watch gap. It remains single-source retail
evidence; the next probe must isolate the title caller's publication/transform
boundary around `0x80019DEC` and `0x80033FCC`. ORIGIN: retail execution, task,
and C904 observations; no value was skipped, rewritten, or guarded.

Session 4376's explicit caller/publication capture passed the whole-RDRAM
control (10,000 callbacks), reached 4,482 VI and all three phase buckets, and
retained 1,958 valid type-2 task rows. The caller `0x80019DEC` executed 3,452
times with predecessor `0x80019DE8`; `0x80033FCC` executed 3,452 times with
predecessor `0x80019DEC`, and paired caller/task rows carried the same task
pointer and publication fields. The C904/task join matched 6,419 rows with
six unmatched witnesses. This second retail evidence line selects
H-publish-direct for the observed title chain and rejects H-title-watch-gap;
it narrows the remaining question to the caller's upstream selector/decode
inputs rather than a missing publication boundary. ORIGIN: retail execution,
task, C904, and whole-RDRAM observations; no value was skipped, rewritten, or
guarded.

Session 4377's batched upstream audit passed the whole-RDRAM control (10,000
callbacks), reached title VI buckets 1024 at origins `0x00790400`/`0x00790800`
and hangar 512 at `0x006AB400`, and retained 1,958 valid type-2 task rows
(`invalid=0`, `overflow=0`). The live caller chain was `0x80019D28/38/68`
followed by `0x80019DD8/E8/EC` and `0x80033FCC`; the pending-task sites
`0x80019E2C/E40/E44`, `0x80019EA4/EB8/EBC`, and `0x80019FA8/FB4/FB8` had zero
hits on this qualified route. The title source/object rows changed with the
phase (`0x80128C80` with source words `0x02000612`/`0x02000800` versus
`0x80128CE0` with `0x02000400`), while the joined task data pointers changed
between `0x80173B20` and `0x80171CE0`; all were observed before the direct
publication call. This selects H-upstream-selector over H-input-watch-gap for
the observed route and supplies the next boundary: attribute the phase-specific
payload writer after publication. It does not yet rule out a later overwrite.
ORIGIN: retail upstream execution, task joins, payload-range writes, and
whole-RDRAM observations; no value was skipped, rewritten, or guarded.

Session 4378's first launch was invalid because it omitted the explicit
`0x80033FCC` execution watch; its whole-RDRAM and VI controls were live but
its task join had zero task rows. The fixed 75-second Rice capture passed the
whole-RDRAM control, reached 632/632/542 VI rows in the title/hangar buckets,
and retained 1,793 valid type-2 task rows with 3,703/3,706 C904/task joins.
Both phase-specific payload ranges were live. Their writer histograms showed
no hits from the eight previously proposed post-publication PCs
(`0x80090DE4`, `0x80090B68`, `0x80091078`, `0x80091198`, `0x80090948`,
`0x80090958`, `0x80092164`, `0x8009216C`); observed writers were elsewhere
(`0x8008F7D4`, `0x80091374`, and phase-specific nearby sites). This selects
H-post-publish-watch-gap for this single-source retail capture and rejects the
audited candidate set as the writer attribution. It does not yet prove the
observed writers are temporally after publication or establish a direct
source/object-to-payload transform; the next probe must join the actual writer
PCs to the task ordinal. ORIGIN: retail physical payload writes, writer-PC
histograms, task execution, C904 joins, and whole-RDRAM observations; no value
was skipped, rewritten, or guarded.

Session 4379 first reproduced that boundary with a missing `--watch-pc` arm;
the fixed capture passed the whole-RDRAM control, reached all three phase
buckets, and retained 1,781 valid type-2 task rows. The oracle diagnostic was
then extended to retain ordinal writes for non-control payload ranges (the
previous implementation only retained <=4-byte watches); the final run
retained 62,372 writes with zero overflow. For `0x178C80:0x179A48`, nearest
task joins were before/after publication 21,308/585, 21,246/548, and 450/2
for the two title buckets and hangar 512. For `0x1E2FC0:0x1E3300`, the joins
were 0/17 and 181/225 in the two title buckets, with no hangar writes. This
confirms that observed payload-range writers do execute after some task
publications and rejects a complete writer-watch gap, while the dominant
range-1 traffic is earlier and the capture does not establish which values
are overwritten. It is single-source retail evidence; the next probe must
join post-write values from `0x8008F7D4`/`0x80091374` to the published payload.
ORIGIN: retail payload-range writes, writer PCs, task-publication PCs, and
whole-RDRAM observations; no value was skipped, rewritten, or guarded.

The independent retail witness at `0x8009C904`/`0x8009C950` reached title and
hangar, with 10,000 whole-RDRAM control writes and 3,107 C904 executions.
Session 4352 retained `branch_state=0x3108` in 584 rows and `0x0010` in 405
rows. Selected words and decoded `+0x18A/+0x18C` fields varied. The configured
post-value watch was mistakenly limited to caller return PCs
`0x8009C0E8..0x8009C0EC` and fired zero times; that is an instrument-boundary
result, not evidence against a writer. The s4354 bounded physical writer watch
passed the whole-RDRAM positive control and retained C904/C950 coverage, but
recorded only 150 stores at `0x1535AC..0x1535BC` and zero stores in the
selected-address subrange `0x1535C4..0x1545C0`. The s4355 run independently
watched both reads and writes: it qualified 10,820 whole-RDRAM writes, 3,107
C904 executions, 7,182 VI frames, and 40,179 reads in the broad range, while
sampled writer PCs emitted only the lower metadata-prefix stores. The bounded
source audit likewise found no direct store to `0x1535C4..0x1545C0` in the
C904 caller/callee path. This closes the post-C904 selected-range writer
hypothesis for the qualified route; the broad watch must not be interpreted as
820 distinct upper-range writes.

Earlier qualified retail work rejected the source span, base/index, route alias,
and stable base-buffer as the retained family producer. `+0x198` settled on
base `0x801B2C60`; `+0x11C8` advanced under `0x8009D790`; selected base-buffer
contents reached `0x801B4CE0` without carrying the family. The lattice store at
`0x8009DB2C` is legitimate quantized output, not the semantic family writer.
The next boundary is therefore the bounded selector/decode writer range.

The RT64 framebuffer-set growth root is a bump-time DPC ring-lap placeholder
drop; `ROGUESQ_WRAP_RESTORE` reproduced ODD-cimg reduction from 60 to 0 in
three runs, but hangar impact remains unqualified. Do not broaden this line
ahead of the M5 selector work. The VI-640 crash family and M3 guard classes are
parked; no mitigation is authorized without an ORIGIN writer and legitimacy
assessment.

The full regeneration flow is unsafe since s4204: `N64Recomp ->
fixup_game_funcs.py` aborts at the E088 anchor and can clobber live generated
functions. Use the existing `tools/apply_s*.py` workflow unless the regen issue
is explicitly repaired.

## Next steps

1. **M5 selector/decode publication writer** — HYPOTHESIS-ID
   `m5-selector-decode-boundary`. Session 4379 established qualified
   post-publication writes in both payload ranges, but not their values. The
   next run must add phase-gated post-write value/scalar capture for writer PCs
   `0x8008F7D4` and `0x80091374`, joined to the same typed `0x80033FCC` task
   rows and payload snapshots. Keep the whole-RDRAM, three-bucket, and
   nonzero-writer controls. Do not repeat the caller census, direct
   publication join, closed first-eight payload comparison, or the
   `0x8009C904:0x8009DC3C` range.
2. M3 pre-publication guard runtime qualification, blocked until a host with
   `mips64-elf-gcc`, `mips64-elf-ld`, and `PatchesLib` is available.
3. Generated-symbol renaming sweep, slug `generated-symbol-renaming-sweep`,
   only when items 1–2 are inapplicable; mapping-only edits do not reset the
   engineering-change gate.

## Live hypotheses

| Hypothesis | Status |
|---|---|
| M5 selector/decode family origin | H-earlier-stream remains confirmed for the prior selected-range audit: no direct post-C904 store reaches `0x1535C4..0x1545C0`; the s4364 family-address union watch was too broad to attribute the task families. |
| M5 title caller path | s4375/s4376 qualify `0x80019DEC -> 0x80033FCC` as the direct publication chain; s4377 selects a phase-specific selector/object input; s4378 finds payload writers outside the prior candidate set; s4379 confirms some writer traffic after publication but leaves value provenance open. |
| M5 consumer join | s4363 plus s4370/s4371 independent retail captures confirm distinct phase-specific task families and zero exact recurrence of nonzero selected words in the first eight published payload words (591/591, 601/601, 344/344). H-later-consumer-transform is confirmed for that boundary; the intermediate transform/publication stage remains open. |
| M5 audio-task-rate divergence | Single-source qualified port A/B shows no useful split: title/hangar phase transitions were both 15.0/24.2 s, and the first hangar sequence was 1064 image versus 1056 silent. Lifetime-row caps prevent an exact 18–28 s count, so this is qualified rate-equivalence evidence, not final cross-source closure. |
| M5 producer provenance | Port hangar source span is cleared by legitimate ROM-DMA/`rs_memset`; no mitigation. |
| Retail/port post-free stream layout | Retail and port share the first qualified read/free boundary, then diverge in later layout/value/order; exact consumer cause open. |
| RT64 fb-set growth | Source is the DPC bump-time placeholder-drop class; hangar effect open. |
| VI-640 crash writer | Open, independent of audio ucode/private DMEM; writer unnamed. |
| M3 sentinel ownership | Source-scope H1 only; runtime unqualified without MIPS toolchain. |

## Evidence boundary and operating rules

Retail oracle watches are physical-address ground truth. Whole-RDRAM, VI, and
target-PC controls qualify coverage; a route failure invalidates a null. Every
instrument needs an independent witness, same-run positive control, phase-scoped
budget, and (before promotion to truth) a second evidence line. Phase-gate
animated comparisons on VI transitions and batch A/B arms in one build/run.

Use [F5-UCODE-REFERENCE.md](F5-UCODE-REFERENCE.md), not standard F3DEX
assumptions. The graphics path is LLE-only. Keep safety guards separate from
explanations. Regeneration order is `make_elf.py -> N64Recomp ->
fixup_game_funcs.py -> CMake`; never hand-edit generated functions for behavior.
If `lib/` changes, export submodule patches. Never run submodule update,
checkout, clean, or hard reset. Kill runs with SIGKILL and run from `build/`.
Any mitigation-shaped change needs an `ORIGIN:` line naming its writer and
whether the value is legitimate.

## Evidence index

[M5-AUDIO-PLAN.md](M5-AUDIO-PLAN.md),
[M5-CURRENT-TRUTH-ARCHIVE-s4269.md](M5-CURRENT-TRUTH-ARCHIVE-s4269.md),
[PROJECT-OVERVIEW.md](PROJECT-OVERVIEW.md), and the append-only detailed ledger
in [PORTING-STATE.md](../PORTING-STATE.md). Use bounded grep/sed windows for
the ledger; do not read it whole.
