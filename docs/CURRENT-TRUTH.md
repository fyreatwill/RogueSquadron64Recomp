# Rogue Squadron 64 Recomp — current truth

Compact operational state for [PORTING-STATE.md](../PORTING-STATE.md). Historical
detail from s4269 onward is in [PROJECT-OVERVIEW.md](PROJECT-OVERVIEW.md) and
[M5-CURRENT-TRUTH-ARCHIVE-s4269.md](M5-CURRENT-TRUTH-ARCHIVE-s4269.md).

Updated for session 4413 (2026-10-09). The preceding maintenance pass reduced
this file to durable state; session 4357 qualified phase coverage but exposed a
retail task-join instrument boundary.

Session 4413's single-source retail selector/payload capture passed the
whole-RDRAM control (19,054 callbacks), completed 4,482 VI, and retained 629,
628, and 691 type-2 task rows in title `0x00790400`, title `0x00790800`, and
hangar `0x006AB400`. The task publication witness was live in all buckets, but
selector `0x80029E78` executed only in the hangar bucket (two executions,
one retained field row: branch selector `0x561F`, object/argument `0x5622`).
The selector field did not fire in either title bucket, so the planned shared
input-versus-phase-specific comparison is not yet evaluable. This rules out a
global source/task route null, but selects neither multiplex nor phase-split;
it identifies a title selector-path boundary requiring a wider execution
range capture. ORIGIN: the retail oracle observed guest execution, task fields,
VI origins, and physical whole-RDRAM callbacks; no value was skipped,
rewritten, or guarded. This is single-source evidence only.

Session 4412's retail-oracle selector-source capture passed the whole-RDRAM
control (10,000 callbacks), reached title `0x00790400` and hangar
`0x006AB400`, and retained 1,776 task-witness executions (1,119 type-2).
Hangar source PCs `0x8009C904` and `0x8009C950` each had 768 lifetime hits;
the selector `0x80029E78` and direct edge `0x80091CB8` both fired in hangar,
while `0x80091BAC` remained absent. This overturns session 4411's
retail-watch-boundary interpretation and selects H-retail-hangar-selector-live:
the source/task arm and selector path are both live. It does not yet prove
which selector input or payload transform supplies the hangar task family.
ORIGIN: the oracle observed guest PCs, VI origins, and task pointers; no value
was skipped, rewritten, or guarded.

Session 4408's retail-oracle ground-truth attempt passed the whole-RDRAM
positive control and reached title 1024, but its driven 85-second route did not
reach hangar, so that arm is invalid for hangar interpretation. The fixed port
run qualified the positive control, title `0x00790400` (2,667 rows), hangar
`0x006AB400` (672 rows), 2,293 task/image joins, and no crash or abort. The
first post-store join design was invalid because the source-store row preceded
the later input/direct call. The corrected direct-call join emitted four
phase-keyed rows, including title `0x80091CB8` with input `0x561F` and call
argument `0x5622`; no hangar callsite row appeared even though hangar input and
AI-boundary/return witnesses were live. This is a qualified phase-order /
callsite instrument boundary, not proof of an indirect caller or value
divergence. ORIGIN: host probes observed guest arguments; no value was skipped,
rewritten, or guarded.

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

Session 4403 widened the existing AI-boundary and AI-callsite filters to admit
title `0x00790400` while retaining hangar as the same-run control. The run
passed the input control, reached title and hangar, retained 2,303 task/image
joins and 256 filter joins, and recorded AI-boundary rows in both phases; the
separate AI-callsite witness recorded zero rows in either phase. This selects
H-title-boundary-without-callsite over the prior filter-hidden explanation and
rules out a title route-coverage null. It does not identify the actual consumer
callsite or prove whether the boundary's direct path is a selector return,
store, or dead-end; the next unit must locate that call chain. ORIGIN: host
boundary and callsite probes observe guest call arguments; no value was
skipped, rewritten, or guarded.

Session 4404 repaired a stale generated probe anchor, rebuilt, and reran the
qualified route. The positive control fired, title `0x00790400` and hangar
`0x006AB400` were live, and the AI-boundary/setup controls remained live. The
repaired direct-call witness fired at `0x80091CB8` in title but not hangar;
the prior zero-row callsite result was an instrumentation omission, not
evidence that the title boundary had no direct consumer. Static inspection
found exactly two generated calls to `0x80029D20`: `0x80091BAC` and
`0x80091CB8`, each followed by setup stores. The title/hangar split remains
open; next compare the two direct edges with phase gates. ORIGIN: guest
callsite and phase arguments were observed; no value was skipped, rewritten,
or guarded.

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

Session 4405 compared both generated direct AI edges in one qualified
phase-gated run. The positive control fired; title `0x00790400` and hangar
`0x006AB400` were live, with 2,320 task/image joins and 256 filter joins and
no crash or abort. The raw direct-callsite witness fired once at
`0x80091CB8` in title and never at `0x80091BAC`; hangar had no direct-edge row,
but its setup, AI-boundary, source, mixer, input, and store-entry witnesses
remained live. This supports a title-only/phase-specific direct edge and
rejects a simple hangar callsite-filter or row-budget null. It does not locate
the hangar caller that reaches the live AI boundary; the next probe must map
that alternate call chain. ORIGIN: guest direct-edge, setup, and boundary PCs
were observed; no value was skipped, rewritten, or guarded.

Session 4406 exhaustively enumerated the generated tree and found exactly two
materialized calls to `0x80029D20`, at `0x80091BAC` and `0x80091CB8`; there is
no uninstrumented generated direct candidate for a new witness. The rebuilt
qualified capture passed the positive control, reached title `0x00790400`
(2,692 rows) and hangar `0x006AB400` (512 rows), and retained 2,313 task/image
joins plus 256 filter joins without a crash or abort. The existing direct-edge
witness fired once at `0x80091CB8` in title and zero times in hangar. Hangar
still produced setup/AI-boundary return activity, so the boundary is live but
neither generated direct edge is its hangar caller. This rules out a missing
third generated direct caller and a simple direct-edge filter/row-budget
explanation; it selects an indirect/aliased or otherwise uninstrumented
call-chain boundary over H-title-only-boundary-path. ORIGIN: generated static
call edges and host phase-gated guest call/boundary witnesses were observed; no
value was skipped, rewritten, or guarded.

Session 4407 reran the qualified capture with the existing phase-keyed direct
callsite and boundary witnesses. The positive control fired; title
`0x00790400` produced 2,692 rows, hangar `0x006AB400` 512, with 2,313
task/image joins, 256 filter joins, and no crash or abort. The hangar bucket
did contain a direct `0x80091CB8` callsite row, followed by the live boundary
and return rows. This overturns session 4406's hangar-zero interpretation: the
missing row was a readout/filter interpretation error, not an indirect caller.
The result selects a phase-scoped direct-call witness discrepancy and rules out
an indirect or aliased entry for this route. ORIGIN: generated direct callsite
and host boundary witnesses observed guest execution; no value was skipped,
rewritten, or guarded.

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

Session 4380's batched post-value capture passed the whole-RDRAM control
(103,725 writes), reached title VI 632/633 and hangar VI 694, and retained
1,948 valid type-2 task rows (`invalid=0`, `overflow=0`). The ordinal table
retained 64,244 payload writes with zero overflow. Both named writers were
live in the payload range: `0x80091374` produced 7,931 scalar samples and
`0x8008F7D4` produced 25,960; every scalar sample had `mismatch=0`. The
range-1 ordinal join still contained both pre- and post-publication traffic
(title `21297/575`, `21271/539`; hangar `385/284` before/after), while range 2
had title `0/17` and `176/220` before/after. This qualifies the writer/value
instrument and rules out a missing named-writer or scalar-validation boundary,
but it does not select overwrite versus maintenance: post-value detail
overflowed and the scalar rows were not keyed to the task ordinal. The next
probe must add that writer-PC-plus-ordinal join before interpreting payload
semantics. ORIGIN: retail writer PCs, scalar source-register comparison, task
publication, payload writes, and whole-RDRAM observations; no value was
skipped, rewritten, or guarded.

Session 4381 extended ordinal payload-write rows with exact destination,
instruction, effective address, source register/value, scalar mask, and
pre-store word, then ran the qualified retail capture through title and hangar
using the PTY-backed oracle runner. The whole-RDRAM control produced 57,822
writes; the run reached title origins `0x00790400`/`0x00790800` and hangar
origin `0x006AB400`, with 1,462 valid type-2 task rows (`invalid=0`,
`overflow=0`). The ordinal table retained 44,225 writes with zero overflow.
Named writers `0x8008F7D4` and `0x80091374` were live in payload range 1 with
26,020 and 7,971 scalar samples respectively; every scalar sample had
`mismatch=0`. Aggregate nearest-task joins remained before/after 21,247/503
and 21,422/640 for range 1 in the two title buckets, while range 2 was
198/202 and 0/13. This qualifies the new exact-write instrument and rejects a
missing-writer, task, scalar-validation, or phase-coverage explanation, but it
does not select overwrite versus maintenance: task rows do not yet print their
event ordinal, so named-writer rows cannot be joined to publication ordinal in
the same table. The next probe must add task event ordinals and a per-writer
before/after aggregation. ORIGIN: retail writer PCs, exact guest store fields,
task execution, scalar validation, and whole-RDRAM/VI controls; no value was
skipped, rewritten, or guarded.

Session 4382 added task publication ordinals to the oracle shutdown rows and a
bounded writer-PC/effective-destination ordinal join. The qualified 50-second
Rice run passed the whole-RDRAM control (60,782 hits), reached 2,979 VI, and
retained 1,466 valid type-2 rows with zero invalid or ordinal overflow. Task
rows covered title origins `0x00790400`/`0x00790800` (628 each) and hangar
origin `0x006AB400` (210). For both named writers in both title buckets,
every retained writer row had a nearest task: `0x8008F7D4` split
21202/548 and 21338/608 before/after, while `0x80091374` split 3492/478 and
3485/495. Scalar validation remained `mismatch=0`. No watched payload-range
write occurred during the retained hangar rows, so this run does not
distinguish hangar overwrite from maintenance and does not close writer
provenance. This is single-source retail evidence for title ordering and a
qualified hangar coverage boundary. ORIGIN: retail writer PCs, exact effective
destinations, task publication ordinals, scalar validation, and whole-RDRAM/VI
controls; no value was skipped, rewritten, or guarded.

Session 4383 extended that same capture to 75 seconds. It passed the
whole-RDRAM positive control with 125,025 writes, reached 4,472 VI, and
retained 629/628/481 valid type-2 task rows for the two title buckets and
hangar (`invalid=0`, `overflow=0`). The ordinal table retained 44,363 writes
with zero overflow; named scalar samples remained live and had `mismatch=0`.
Hangar range 1 had 165 nearest-task writes, so the task/ordinal join was live,
but neither named writer (`0x8008F7D4` or `0x80091374`) wrote that range in the
hangar bucket. This selects H-hangar-maintenance-or-other-range over
H-writer-task-join-boundary and rejects the simple short-window explanation.
It is single-source retail evidence: the actual hangar writer set and whether
its traffic is maintenance remain open. ORIGIN: retail writer PCs, exact
effective destinations, task publication ordinals, scalar validation, and
whole-RDRAM/VI controls; no value was skipped, rewritten, or guarded.

Session 4384's actual-hangar-writer capture passed the whole-RDRAM positive
control (10,000 callbacks before removal), reached title 1024 and hangar 512,
and retained 1,721 valid type-2 rows with `invalid=0` and `overflow=0`. The
hangar writer set was live at high volume: every retained requested writer had
scalar validation `mismatch=0`; the ordinal writer table retained 920 keys with
zero overflow. The observed writers produced both before- and after-publication
rows, so the value-watch-gap explanation is closed. The capture did not compare
those stores to task payload values, however, and the join's `equal` field is
event-ordinal equality rather than payload equality. This is a qualified
single-source boundary result, not proof of selector/decode provenance. The
next probe must add a phase/task-keyed comparison of requested writer
post-values against the published task payload. ORIGIN: retail writer PCs,
exact effective destinations, task publication ordinals, scalar validation,
and whole-RDRAM/VI controls; no value was skipped, rewritten, or guarded.

Session 4385's post-value-detail capture passed the whole-RDRAM control
(123,382 writes), reached all three phase buckets with 628/628/482 valid type-2
rows, and retained 1,738 valid type-2 task rows with `invalid=0` and
`overflow=0`. The ordinal table retained 44,911 writes with zero overflow. The
actual high-volume hangar writers `0x8008F7D4` and `0x80091374` were scalar
validated (`121` and `36` samples; `mismatch=0`), but they were not included in
the requested detail-PC list. The requested detail table overflowed by 43,546
rows, so it cannot compare actual writer values to task payload values. This is
an instrument-boundary result, not evidence for selector-writer versus
maintenance traffic; the next capture must request detail for the actual
writers only and retain the same task/payload watches. ORIGIN: retail writer
PCs, exact effective destinations, task publication ordinals, scalar
validation, and whole-RDRAM/VI controls; no value was skipped, rewritten, or
guarded.

Session 4386 fixed the detail boundary with a phase filter and requested only
`0x8008F7D4`/`0x80091374`. The qualified 75-second Rice run passed the
whole-RDRAM control (125,701 writes), reached 4,487 VI, and retained 1,753
valid type-2 tasks with `invalid=0`, `overflow=0`; the ordinal payload table
retained 44,845 writes with `overflow=0`. Both requested writers were
scalar-valid (`25,994` and `7,961` samples, `mismatch=0`), and the hangar
payload range was live through task and ordinal rows. Neither requested writer
produced a phase-512 hangar detail row, selecting
H-hangar-other-writer-or-range over the two named writers for this capture.
This is single-source retail evidence; it does not prove those PCs are absent
from all hangar destinations. ORIGIN: retail writer PCs, exact scalar
post-store values, task publication, payload-range writes, and whole-RDRAM/VI
observations; no value was skipped, rewritten, or guarded.

Session 4387's phase-512 writer/destination census passed the whole-RDRAM
control (125,701 writes), reached title buckets with 633/633 VI rows and the
hangar bucket with 504 rows, and retained 1,753 valid type-2 tasks with
`invalid=0`, `overflow=0`; the ordinal table retained 44,845 writes with
`overflow=0`. In the hangar payload range `0x178C80:0x179A48`, the only
high-volume writer was `0x800078EC` (`664` stores); the named title writers
`0x8008F7D4` and `0x80091374` had no phase-512 rows. The retained scalar sample
for `0x800078EC` had `mismatch=0` and wrote zero, and its exact ordinal rows
were a contiguous zero-fill tail at `0x179A28..0x179A47`. This selects
H-hangar-other-range/maintenance over H-actual-hangar-writer for the watched
range: the range is being cleared in hangar, not populated by the semantic
task writer. It remains single-source retail evidence and does not identify
the actual task data/output destination. ORIGIN: retail phase-keyed writer
histograms, exact effective stores, scalar validation, task publication, and
whole-RDRAM/VI controls; no value was skipped, rewritten, or guarded.

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

Session 4388's corrected retail task-destination census passed the positive
control (10,000 whole-RDRAM callbacks), reached the title and phase-512 task
route, and completed with 1,449 valid type-2 task rows (`invalid=0`,
`overflow=0`) and 1,173,281 retained destination writes (`overflow=0`). The
phase-512 task rows used `data=0x80171E70` in this run (the prior run used
`0x80173CB0`), `data_size=2`, and always had `output=0`/`output_size=0`.
The watched data-block union and its `+0x100` union both had substantial
phase-512 writer traffic, while the null output span had no phase-512 writer
rows. This selects H-task-data over H-task-output and H-watch-gap for the
qualified retail route, but the union watch is broader than one dynamic task
block and the result is single-source retail evidence. The next probe must
split exact per-task data spans (including both observed hangar bases) and
add an independent evidence line before promoting destination provenance.
ORIGIN: retail task fields, physical writer PCs, phase-gated destination
watches, ordinal joins, and whole-RDRAM/VI controls; no value was skipped,
rewritten, or guarded.

Session 4389's exact-span retail capture passed the whole-RDRAM control (10,000
callbacks), reached title VI rows 631/632 and hangar VI 504, and retained 1,751
valid type-2 tasks (`invalid=0`, `overflow=0`) with ordinal-write overflow 0.
Hangar task rows split between `data=0x80171E70` (237 rows) and
`data=0x80173CB0` (259 rows), with `data_size` 1 or 2. Separate watches for
`0x171E70:0x173290` and `0x173CB0:0x1750D0` both had substantial phase-512
writer traffic; their exact `+0x100` fields (`0x171F70` and `0x173DB0`) also
had writers, while the null output span `0:0x20` had none. Exact-span writer
rows joined to same-phase task ordinals with no missing task (`117,930` and
`104,779` hangar rows; ordinal overflow 0). This selects H-task-data over
H-task-output and H-watch-gap for the exact dynamic spans, using task-field
rows and independent physical writer watches as two evidence lines. It remains
single-source retail evidence and does not yet prove which stores are semantic
payload versus maintenance. ORIGIN: retail task-field observations, exact
physical writer PCs, phase/ordinal joins, and whole-RDRAM/VI controls; no value
was skipped, rewritten, or guarded.

Session 4390's batched exact-span scalar capture passed the whole-RDRAM control
(1,559,513 callbacks), reached 4,486 VI, and retained 1,748 valid type-2 task
rows with ordinal-write overflow 0. Post-store scalar validation found live
nonzero stores in both exact task-data spans and their `+0x100` fields: watches
1/2/3/4 had 176/257/130/251 nonzero samples, with `mismatch=0` throughout the
supported scalar samples. The null output watch had zero writes. Watch 1 had 14
unsupported samples from non-scalar store forms, so this is not a
zero-unsupported instrument qualification; it does not invalidate the
supported scalar evidence. Together with s4389's task-field and physical-writer
witnesses, this selects H-semantic-data over pure maintenance/zero-fill for the
exact spans. It remains single-source retail evidence and does not identify the
semantic writer's full phase/ordinal mapping. ORIGIN: retail task fields, exact
physical writes, post-store source-register validation, and whole-RDRAM/VI
controls; no value was skipped, rewritten, or guarded.

Session 4391's exact-span ordinal capture passed the whole-RDRAM control
(1,551,202 writes), reached all three phase buckets, retained 1,719 valid
type-2 task rows, and had zero ordinal overflow. The four exact target fields
had no missing nearest task: hangar watch 3 was 87,360 before versus 125 after,
and hangar watch 4 was 160 before versus 0 after; title buckets were likewise
predominantly before-task. Exact nonzero target stores were attributed to
phase-specific PCs `0x80090DE4`/`0x80090B68`, while `0x80090CA4` and
`0x80091078` also wrote the target fields. This supports H-ordinal-semantic
for nonzero exact-span stores over an absent-task explanation, but the nearest
task join does not yet separate semantic stores from maintenance stores and is
single-source retail evidence. ORIGIN: retail task-publication PCs, exact
writer PCs/source values, phase-keyed ordinal joins, and whole-RDRAM controls;
no value was skipped, rewritten, or guarded.

Session 4392's batched exact-span writer-class capture passed the whole-RDRAM
control (1,555,836 writes), reached 4,489 VI, retained 1,762 valid type-2 task
rows, and recorded 725,451 exact-span writes with ordinal overflow 0. The
new table split each phase/watch by named writer class and scalar value class:
both semantic PCs (`0x80090DE4`/`0x80090B68`) and maintenance PCs
(`0x80090CA4`/`0x80091078`) produced scalar-zero and scalar-nonzero stores.
Every class had a task join (`no_task=0`); ordering was predominantly before
the nearest task, with phase-specific after rows in both named classes. This
rejects both exclusive semantic-PC and exclusive maintenance-PC explanations
and rejects H-source-gap for this table. It does not establish which class
writes the published task payload; the next discriminator must test each
writer's effective address against the joined task's `data_ptr/data_size`.
This is qualified single-source retail evidence. ORIGIN: retail task-publication
PCs, exact writer PCs/effective addresses/source values, phase-keyed ordinal
joins, and whole-RDRAM controls; no value was skipped, rewritten, or guarded.

Session 4393's corrected exact-span containment capture passed the whole-RDRAM
control (1,559,546 callbacks), reached 4,484 VI and all three phase buckets,
and retained 1,731 valid type-2 task rows with zero ordinal overflow. The
bounded span table had 32 keys and zero key overflow; every retained writer
row joined a task (`no_task=0`). Across title and hangar phases, semantic
writers `0x80090DE4`/`0x80090B68` were contained in the joined task data span
for 52,435/52,435 rows, while maintenance writers `0x80090CA4`/`0x80091078`
were in-span for 31,194/31,997 rows, with 802 in the separate `data_ptr+0x100`
field and one outside. This selects H-semantic-payload-span for the bounded
containment discriminator, while showing maintenance traffic is mixed rather
than absent. It does not prove source-value equality with the published task
payload and remains single-source retail evidence; the next probe must add an
independent payload-value comparison. ORIGIN: retail task-publication PCs,
exact writer PCs/effective addresses, task data spans, scalar value classes,
and whole-RDRAM/VI controls; no value was skipped, rewritten, or guarded.

Session 4394's first published-word comparison was invalidated because it read
task words at shutdown after later task cycles had overwritten the same buffers.
The corrected same-run capture snapshots the four published words at each task
publication before joining exact writer rows. It passed the whole-RDRAM control
(10,000 callbacks), reached 4,486 VI and all three phase buckets, retained
1,724 valid type-2 tasks (`invalid=0`, `overflow=0`), 22,901 writer rows, and
zero ordinal overflow; supported post-store scalar validation still reported
`mismatch=0`. Title source-value match rates were semantic 482/7,291 and
maintenance 130/629; post-store matches were semantic 482/7,291 and
maintenance 20/629. Hangar was semantic 0/4,660 and maintenance 56/467 for
both source/post comparisons. This single-source retail result favors
H-maintenance over H-semantic for the published-word value discriminator, but
it does not yet provide the required independent evidence line; retain the
selector/decode boundary as open. ORIGIN: named retail writer PCs and task
publication PCs are observed; task words are snapshotted before later reuse;
no value was skipped, rewritten, or guarded.

Session 4395's direction-split published-word capture passed the whole-RDRAM
control (10,000 callbacks), reached 4,484 VI and all three phase buckets, and
retained 1,731 valid type-2 tasks with 22,989 writer rows and zero ordinal
overflow. Supported post-store scalar validation again reported mismatch=0.
The nearest-task direction was overwhelmingly before-publication: title
semantic writers matched 481/7,274 and maintenance writers 130/628 in the
`0x00790400` bucket; hangar semantic matched 0/4,781 and maintenance 57/470.
Only seven after rows occurred, all maintenance-class and all nonmatching
(one title row and six hangar rows); no equal-direction rows were retained.
This independent direction split strengthens H-maintenance over H-semantic for
the bounded published-word value question and rules out a match advantage
caused by after-publication mixing. The transform/publication boundary remains
open because the dominant before rows still do not identify the upstream
selector/decode transform. ORIGIN: retail task-publication PCs, exact writer
PCs/effective addresses, snapshotted task words, ordinal direction, and
whole-RDRAM/VI controls are observed; no value was skipped, rewritten, or
guarded.

Session 4396's selector/decode boundary census had two invalid capacity runs,
then a corrected 75-second Rice capture. The corrected run passed the
whole-RDRAM control, reached both title origins and hangar, retained 1,719
valid type-2 tasks (`invalid=0`, `overflow=0`), 2,938/2,938 phase-gated
caller-range rows (`overflow=0`), and 24,165 exact payload writes with zero
ordinal overflow. The range executed through the qualified
`0x80019DEC -> 0x80033FCC` chain, but no candidate-range PC appeared as a
semantic payload writer; exact writers remained in the `0x80090...` family.
Published-word matches were before-task: semantic 481/7,276 and 482/7,291 in
title and 0/4,629 in hangar; maintenance 130/1,091, 130/1,091, and 51/854.
This qualifies H-later-transform over a missing range-watch explanation, but
is single-source retail evidence and does not close the boundary. The two
earlier capacity runs are invalid and select no hypothesis. ORIGIN: retail
execution range, task publication, exact writer PCs, source/post scalar
validation, and phase/VI controls were observed; no value was skipped,
rewritten, or guarded.

Session 4397's bounded port capture passed its positive control, reached title
VI `0x00790400` and hangar VI `0x006AB400`, and retained 2,290 valid audio-task
rows plus 2,290 task/image joins with no crash or abort. It also produced 1,058
phase-gated input-DMA rows and 256 selector/decode join rows. However, the port
route produced no `0x00790800` title bucket, and the selector join was capped in
the hangar bucket; therefore the required all-three-bucket comparison was not
qualified. This is H-instrument-gap, not evidence for port corroboration or
divergence. The next probe must repair the port phase capture (or explain the
missing `0x00790800` route with a same-run control) before comparing payload
relationships. ORIGIN: existing port phase/task/DMA witnesses and the
same-run positive control were observed; no value was skipped, rewritten, or
guarded.

Session 4398's repaired port capture removed the stop-width gate and passed the
same positive control. It recorded 2,662 `0x00790400` observations, 224
`0x006AB400` observations, 2,320 audio-task rows and 2,320 task/image joins,
plus 1,051 input-DMA and 256 selector/decode joins; it recorded zero
`0x00790800` observations and no crash or abort. The missing middle-title
bucket therefore persists with the gate removed and selects H-port-route-boundary
over H-port-three-buckets or H-port-instrument-failure for this route. This is
not yet a payload corroboration: the next probe must classify the port's actual
VI-origin/action sequence in the same qualified run. ORIGIN: port phase/task/DMA
witnesses and same-run positive control were observed; no value was skipped,
rewritten, or guarded.

Session 4399's phase/action capture passed the positive input-writer control and
recorded 2,692 `0x00790400` title observations, 135 `0x006AB400` hangar
observations, 2,313 audio-task rows, 2,313 task/image joins, 1,064 input-DMA
rows, and 256 selector/decode joins. The ordered phase transitions were
`0/320`, `640` cinematic, `1024 @ 0x00790400`, then `512 @ 0x006AB400`;
`0x00790800` never occurred. Autopilot actions fired at 3, 6, and 9 seconds
in the 640 phase. No crash or abort occurred. This selects
H-port-direct-transition over H-port-middle-origin and rules out
H-port-instrument-failure for the qualified port route. It does not establish
payload equivalence or explain the retail transform/publication boundary.
ORIGIN: port phase transitions, action events, task/DMA witnesses, and the
same-run control were observed; no value was skipped, rewritten, or guarded.

Session 4401's bounded port payload capture passed the positive input-writer
control, retained the qualified direct route (`0x00790400 -> 0x006AB400`),
and recorded 2,323 audio-task rows with 2,323 joins, 1,064 input-DMA rows,
and 256 selector/decode joins; there was no crash or abort. The title task
families used `0x80171CE0`/`0x80173B20` with source hashes including
`0x050C5D40`, `0x050C5D67`, and `0x59770940`, while hangar used
`0x80171E70` with distinct hashes including `0x050C5D3F` and `0x3176CAB5`.
The selector/filter witness fired only in hangar, and `0x00790800` remained
absent, so direct selected-word equality was not qualified. This selects
H-port-payload-divergence from phase-specific task payload families, while
leaving the title selector witness and retail transform/publication boundary
open. ORIGIN: port phase, task, DMA, selector, and payload logs are observed;
no value was skipped, rewritten, or guarded.

Session 4402's all-selector-gates port capture passed the input-writer control,
reached title `0x00790400` (2,692 observations) and hangar `0x006AB400` (163),
and retained 2,325 audio-task rows with 2,325 joins and 256 filter joins; the
middle title origin remained absent and there was no crash or abort. Title
selector setup/source/mixer/input/store-entry/tick witnesses all fired, so the
selector path is reached in title and the missing title row is not an env-gate
or route-coverage null. The narrower AI-boundary callsite witness still fired
only in hangar because its host filter is hard-coded to width 512/origin
`0x006AB400`; this selects H-title-selector-uninstrumented and makes the next
probe a title-enabled callsite capture. ORIGIN: port phase, task/image joins,
positive control, and selector witnesses are observed; no value was skipped,
rewritten, or guarded.

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

Session 4410's phase-latched port capture passed the positive control, reached
title `0x00790400` and hangar `0x006AB400`, and retained 2,229 audio-task joins
without a crash or abort. The direct `0x80091CB8` call was latched in title
phase 4 (`input=0x561F`, argument `0x5622`), then consumed at the first phase-5
hangar VI transition. Later hangar boundary/input/source/store/task witnesses
were live in the same run. This selects H-pre-phase-call and rules out
H-no-hangar-call and H-phase-state-mismatch for the qualified port route. The
prior filtered zero was an ordering boundary, not call absence. ORIGIN: host
probes observed guest call arguments and the RT64 phase transition; no value
was skipped, rewritten, or guarded.

## Next steps

1. **M5 pre-filter selector/decode boundary** — HYPOTHESIS-ID
   `m5-selector-decode-boundary`. Session 4413 found the exact selector
   `0x80029E78` only in hangar while title task publication remained live.
   Next use one phase-gated retail execution-range capture over the selector
   family around `0x80029D20..0x80029F20`, with whole-RDRAM, all three VI
   buckets, source PCs, direct edges, and `0x80033FCC` controls. A title-range
   hit at another PC identifies the alternate selector path; no title-range
   hit with live title task rows selects a pre-range/title-side boundary; loss
   of task/source controls invalidates the comparison.
2. M3 pre-publication guard runtime qualification, blocked until a host with
   `mips64-elf-gcc`, `mips64-elf-ld`, and `PatchesLib` is available.
3. Generated-symbol renaming sweep, slug `generated-symbol-renaming-sweep`,
   only when items 1–2 are inapplicable; mapping-only edits do not reset the
   engineering-change gate.

## Live hypotheses

| Hypothesis | Status |
|---|---|
| M5 selector/decode family origin | H-earlier-stream remains confirmed for the prior selected-range audit: no direct post-C904 store reaches `0x1535C4..0x1545C0`; the s4364 family-address union watch was too broad to attribute the task families. |
| M5 title AI boundary | s4410 phase latch selected a title-phase `0x80091CB8` call consumed at the first hangar VI transition; later hangar boundary/input/source/store/task witnesses were live. This closes the phase-order ambiguity for the qualified port route and rules out an indirect/aliased caller there. |
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
