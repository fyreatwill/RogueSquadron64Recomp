# Rogue Squadron 64 Recomp — current truth

Operational state for [PORTING-STATE.md](../PORTING-STATE.md). Durable background
and archived session detail are in [PROJECT-OVERVIEW.md](PROJECT-OVERVIEW.md).
This file is the compact active-state record; full run logs live under
`scratch/agent/` and the session evidence documents.

Current active marker: Session 3496 (2026-08-31). This record was
compacted during the next maintenance iteration; sessions 3201–3445 remain in
the append-only ledger and overview archive.

## Current state

The native port boots through attribution, N64 logo, intro cinematic, star
flare, Factor 5 logo, title VI 1024 (`0x00790400`), and hangar VI 512
(`0x006AB400`) on the validated spin-yield/F5-LLE route. Hangar geometry and
color artifacts remain. Audio is not production-complete: the Factor 5 image
task is the qualified real-audio arm; `musyx_stub`/Broke is the silent control.

The default route returns from the attract viewer and reaches the cinematic
loop, but the stage advancer sees null `0x800B0934`; the initializer at
`0x800A62B4` is skipped while port skip-allow is zero. Retail independently
sets that byte and reaches title. Do not force the flag or bypass state.

M5 is the active engineering thread. The status-03 worker/clear contract,
task ABI, completion/delivery, callback-table, field348 input-to-clear edge,
send/receive zero-message boundary, and first consumer boundary are closed at
their measured scopes. The remaining qualified gap is the first output/state
contract:

- Retail `0x80001CC8` sees varied `v1` values while `s1=0x80194B20`.
- Both port arms reach the same consumer/output controls, but
  `0x80001CB8` sees `0x801Bxxxx` state pointers and `0x80001CC8` returns `2`.
- Earlier hangar-qualified `rs_free` rows still had `s1=0x80194B20`, pointed
  word `0x80194B40`, and `a0=0x801BEEB0`; the repaired title route instead
  shows stable `s1`/pointed-word tuples in the `0x801Bxxxx` state family.
  Retail-equivalence of these contexts remains unqualified.
- The generated host wrapper reports `ra=0`; the exact clobber is unresolved.

The s3449 rerun repaired the state-pointer witness's hard-coded hangar-only
phase gate. Both arms emitted 512 title entry and 1,024 title checkpoint rows
at origin `0x790400`, with no crash; sampled `s1` and pointed-word values
were unchanged from entry through post-receive and pre-consumer in both arms.
The independent retail field watch also observed the matching title tuple
(`s1=0x801B1590`, state pointer `0x801B95F0`) at the consumer site. This
closes the phase-mismatch defect and establishes title pointer parity at the
observed `rs_free` boundary with two evidence lines, but does not locate the
downstream output-contract cause or explain the alternate `0x80194B20` route.

Session 3450's fixed oracle control passed 1,000 whole-RDRAM callbacks,
completed 3,273 VI, and recorded 742/742/742/741 executions at
`0x80001C98`/`0x80001CB8`/`0x80001CC8`/`0x80001F84`; its field tables had
460/511/511/458 unique rows. The port silent and image arms remained mutually
identical, but the oracle fields (`s0`, `s1`, source word, branch selector,
source byte, branch state) are not yet exposed by the port witness, so parity
versus divergence remains unevaluable.

M5 audio source work remains unresolved upstream: qualified port image-stage
rows carry zero source/output PCM, while retail independently writes nonzero
PCM spans. Do not change waits, slots, status handling, consumer dispatch,
clear behavior, or PCM writeback while locating the state-pointer edge.

Session 3451's image-arm zero-row verdict was a stale interpretation of the
retained log. Session 3452's fresh build and two-arm run showed the schema
positive control and all four target-PC buckets in both arms: 2,048 rows per
arm, with target counts 514/510/510/514, plus 512 consumer and 343 output
rows. The retained s3449 logs independently show the same image control. This
closes the image-arm control defect and permits the planned join.

The sequential silent/image rows diverge from ordinal 4, including `s1` and
source fields. That difference is not a contract selection because the arms
run separately through an animating title scene. Output/state parity remains
unevaluable until port rows are joined to retail by phase, PC, and ordinal.

Session 3453 performed that controlled join. At title origin `0x00790400`,
the first joined row diverges in `s0` at all four target PCs for both port
arms; no exact six-field tuple matches in the common prefixes. The port
four-PC control and independent retail whole-RDRAM control both fired, so this
selects a real first output/state-context divergence and rules out an absent
port hook. It does not identify the writer of `s0`; the next probe must trace
the producer feeding the target calls.

Session 3454's corrected thread-local callsite join shows that port `rs_free`
preserves caller `s0` at `0x80001C98` in all 514 captured rows (480 from
caller `0x80005268`). The first divergence is already in the producer/input
register context; wrapper/ABI clobber is ruled out at this boundary.

Session 3455's independent retail preflight passed 18,497 whole-RDRAM control
callbacks and reached title 1024, with 781 executions of the
`0x80005268 -> 0x80001C98` edge and 2,570 executions each at
`0x80001CB8` and `0x80001CC8`. The batched port run reached title 1024, fired
the four-PC schema control, and emitted 1,024 callsite rows plus 514/514/510
rows at the three target PCs. Caller-side `s0` was varied before the target
calls in the port rows, matching the independently observed retail edge. This
reinforces the upstream producer/input selection, but the callsite witness
still does not attribute the writer of `s0`. Evidence: [M5-S3455-PRODUCER-JOIN.md](M5-S3455-PRODUCER-JOIN.md).

Session 3456's independent Rice-oracle run passed the whole-RDRAM control,
reached title, and observed 3,233 executions of `0x80001C98` from
`0x800645AC`. A new port load witness at `0x800645A8` passed its existing
four-PC schema control and emitted 1,024 rows. The first ordered prefix
diverges at the producer/input value: retail has `s0=0x801B4F00` where the
port loads `0x801B5E70`, while both use source pointer `0x801E8710`; the port
target preserves that value. This selects the upstream producer/input
boundary and rules out wrapper/ABI clobber at this scope. It does not name the
writer of `*(0x801E8710)`. Evidence: [M5-S3456-PRODUCER-INPUT.md](M5-S3456-PRODUCER-INPUT.md).

Session 3457's retail source-slot watch passed the whole-RDRAM control with
11,483 callbacks, recorded 1,483 writes to physical `0x001E8710`, and showed
title-phase writers at `0x800644B0`, `0x80064524`, `0x800078EC`,
`0x80018F5C`, `0x80018F80`, `0x80028F90`, `0x800C871C`, and `0x80006FF4`.
The matching port run passed its four-PC schema control and emitted 1,024
source-writer rows, but only at `0x800644B0` and `0x80064524`. This selects a
retail-side writer/route difference at the observed title boundary and rules
out a port-only writer. The generated parity hook passed zero as its value
argument, so writer-value legitimacy remains unevaluable. Evidence:
[M5-S3457-SOURCE-WRITER.md](M5-S3457-SOURCE-WRITER.md).

Session 3458's retail post-store arm passed the whole-RDRAM control (11,198
callbacks), reached title origin `0x00790400`, and measured the actual source
word: `0x800644B0` stored zero in 807 samples, `0x80064524` stored nonzero in
269, and retail-only writers such as `0x800078EC` and `0x80018F80` also had
nonzero samples. The matching port arm was rebuilt, but the first attempt used
an invalid route and the corrected LLE/spin-yield attempt crashed at startup
(`spTaskSchedulerThread`, guest PC `0x8000834C`) before title, with zero source
rows. Retail value evidence is therefore single-source and the cross-runtime
writer/value join remains unevaluable. Evidence:
[M5-S3458-SOURCE-VALUE.md](M5-S3458-SOURCE-VALUE.md).

Session 3459 rebuilt the prescribed LLE/spin-yield port arm and reached title
origin `0x00790400`, producing 20 title captures. Its parity control fired in
the earlier width-640 phase, but the title-scoped control and source-writer
table both emitted zero rows. The run later changed to width 640 and crashed
in `musyxSynthFrame+4268` (last guest PC `0x80001B08`). Title reachability is
qualified for this arm, but the title writer witness is not; the source-value
join remains unevaluable and no audio behavior is implicated. Evidence:
[M5-S3459-SOURCE-VALUE-PORT.md](M5-S3459-SOURCE-VALUE-PORT.md).

Session 3460 added a regeneration-safe title-scoped entry control at
`rebuildActiveDisplayObjectList`. The first prescribed capture hit the known
startup crash at guest PC `0x8000834C` before title; an unchanged retry reached
title origin `0x00790400`, fired the entry control, and emitted 64 entry rows
plus 1,024 source-writer rows (768 at `0x800644B0`, 256 at `0x80064524`). The
captured port source-store values were zero. The phase, control, and store rows
refute gate suppression, missing generated route, no-title-store, and
control-failure interpretations at this scope. The later
`musyxSynthFrame+4268` crash does not invalidate the earlier title rows.
Port-versus-retail value legitimacy remains unevaluable until the rows are
joined; evidence: [M5-S3460-SOURCE-VALUE-WITNESS.md](M5-S3460-SOURCE-VALUE-WITNESS.md).

Session 3461 repeated the prescribed title source-writer capture. The port
reached origin `0x00790400`, passed the earlier width-640 writer control, and
emitted 1,024 ordered rows: 768 at `0x800644B0` and 256 at `0x80064524`, all
with value zero. It later left title and crashed in the existing
`musyxSynthFrame+4268` path. The retained retail artifact has only phase/PC
totals and value histograms, not ordered phase/PC/value rows, so the planned
cross-runtime ordinal join is unevaluable; no source-contract hypothesis is
selected. Evidence: [M5-S3461-SOURCE-VALUE-JOIN.md](M5-S3461-SOURCE-VALUE-JOIN.md).

Session 3462 obtained the missing independent retail table. With the
whole-RDRAM control and physical source watch both active, the oracle reached
633 title VI frames and emitted 1,294 ordered title rows at origin
`0x00790400`: 978 zero-valued stores from `0x800644B0`, and 316 stores from
`0x80064524` with values `0x80194EA0` (19), `0x801B4F00` (165), or
`0x801B5E70` (132). The control recorded 12,734 writes and the source watch
2,734. This selects the ordered-retail-data hypothesis and makes the next
step the port-versus-retail ordinal join; it does not select a port/shared
writer explanation by itself. Evidence: [M5-S3462-RETAIL-ORDERED-SOURCE.md](M5-S3462-RETAIL-ORDERED-SOURCE.md).

Session 3463 joined the qualified port and retail title rows by phase, writer
PC, and per-PC ordinal. All 768 comparable `0x800644B0` rows match at zero.
At the shared `0x80064524` writer, the first comparable row diverges: port
writes zero and retail writes `0x801B4F00`. The independent retail controls
and the port title control fired. This selects the first value divergence,
not a writer-route divergence; evidence is
[M5-S3463-SOURCE-VALUE-JOIN.md](M5-S3463-SOURCE-VALUE-JOIN.md).

Session 3464 captured the independent retail producer/store table in one
controlled run. Whole-RDRAM and physical-source controls fired (12,706 and
2,706 callbacks), title reached 630 VI frames, and execution watches at
`0x800644A8` and `0x80064524` fired 18,554 times. Retail's ordered
`0x80064524` rows include nonzero values such as `0x801B4F00`, while the
qualified port rows remain zero; `0x800644A8` is active with caller
`0x80001C90`. This selects the producer/value divergence and narrows the
unresolved edge to the table load between `0x800644A8` and `0x80064524`, but
does not yet name the exact table-entry writer. Evidence:
[s3464_m5_retail_producer_value.md](../scratch/agent/s3464_m5_retail_producer_value.md).

Session 3466 captured the source-table entry span in the independent retail
oracle. The whole-RDRAM and physical-source controls fired 14,948 and 1,916
times; title phase reached 535 VI frames; and the observed table span
`0x001B4AA0:0x001B4B24` recorded 3,032 writes. Title-phase writer attribution
includes `0x80064350`, `0x80064360`, `0x80064378`, and `0x800646D8`, while
`0x80018F5C`, `0x80018F60`, and `0x80018F80` are active initialization/copy
writers. The existing `0x800644A8`/`0x800644DC`/`0x80064524` watches also
fired. This rules out an absent retail table-write route and identifies the
candidate writer set, but detailed write rows do not expose stored word
values, so the exact writer/value join remains unevaluable. Evidence:
[M5-S3466-RETAIL-ENTRY-WRITER.md](M5-S3466-RETAIL-ENTRY-WRITER.md).

Session 3465 captured the intervening retail table-load site at `0x800644DC`
in the same controlled run as `0x800644A8` and `0x80064524`. Whole-RDRAM and
physical-source controls fired 12,666 and 2,666 times; title-gated execution
rows fired 16,905, 3,971, and 16,745 times respectively. Retail table-entry
addresses such as `0x801B4AA0` led to nonzero shared-writer values including
`0x801B4F00`, while the qualified port rows remain zero. This selects a
table-entry/value divergence and rules out absent load/writer routes and failed
controls at this scope. It does not name the table-entry writer or establish
whether the port table pointer differs. Evidence:
[M5-S3465-RETAIL-TABLE-LOAD.md](M5-S3465-RETAIL-TABLE-LOAD.md).

Session 3467 repeated the independent Rice capture with candidate writer
execution watches and store-field rows. Whole-RDRAM and physical source-slot
controls fired 14,936 and 1,904 times; title phase reached 533/534 VI frames;
and the table span recorded 3,032 writes. Candidate writers
`0x80064350`, `0x80064360`, `0x80064378`, and `0x800646D8` all fired in both
title origins, with rows tied to entries such as `0x801B4AA0`. The shared
`0x80064524` post-value sampler again saw 398 nonzero samples, including
`0x801B4F00` and `0x801B5E70`. The candidate rows expose pre-store words, not
post-store values, so the exact writer/value join remains unevaluable; this
confirms active legitimate retail writers but selects neither pointer nor
value divergence. Evidence: [M5-S3467-RETAIL-WRITER-VALUES.md](M5-S3467-RETAIL-WRITER-VALUES.md).

Session 3468 corrected the post-store instrument configuration and repeated
the independent Rice capture. Whole-RDRAM, table-span, and source-slot
controls fired with 14,935, 3,032, and 1,903 writes; title reached both
1024-wide origins. Candidate writers `0x80064350`, `0x80064360`,
`0x80064378`, and `0x800646D8` all fired, yielding 1,863 phase-qualified
store callbacks and 968 unique rows. Post-store values were measured for all
four writers, and the shared `0x80064524` sampler recorded 398 nonzero rows
(327 `0x801B4F00`, 71 `0x801B5E70`). This repairs the earlier instrument
failure and establishes legitimate retail post-store values, but the run did
not expose the port-side table pointer or selection. Therefore neither
`H-SourceWriterValue` nor `H-TablePointerDivergence` is selected across
runtimes. Evidence: [M5-S3468-RETAIL-POST-VALUE.md](M5-S3468-RETAIL-POST-VALUE.md).

Session 3469 added a regeneration-safe port table-selection witness at
`0x800644DC` and `0x80064524`. The corrected autopilot run reached title
`0x00790400` at width 1024 and hangar `0x006AB400` at width 512. The existing
four-PC schema control fired, and the witness emitted 1,024 rows at each edge;
the existing output/state witness emitted 2,048 rows. Port selections include
`0x801B4AA0 -> 0x801B4F00` and `0x801B4B20 -> 0x801B5E70`, matching the known
retail pointer family and values from the independent Session 3468 baseline.
This rules out a port-side table-pointer-family divergence at this boundary
and selects the downstream output/state value contract as the next boundary;
it does not yet provide an ordinal cross-runtime join. Evidence:
[M5-S3469-PORT-TABLE-SELECTION.md](M5-S3469-PORT-TABLE-SELECTION.md).

Session 3470 attempted the prescribed port-selection/output-state join. The
port controls and ordered rows were live, but the retained retail post-value
rows are keyed by VI ordinal, writer PC, store address, and value; they lack
the port selection entry/identity and shared invocation ordinal. Thus the
cross-runtime join is unevaluable, not a null, and neither output-state nor
later-selection hypothesis is selected. Evidence:
[M5-S3470-OUTPUT-STATE-JOIN.md](M5-S3470-OUTPUT-STATE-JOIN.md).

Session 3471 qualified the existing regeneration-safe four-PC output/state
tuple witness. An independent retail preflight passed the whole-RDRAM control
(29,630 writes), reached title origin `0x00790400`, and produced
659/763/763/654 unique rows at the four target PCs. The matching port run
passed the schema control and emitted 514/510/510/514 rows with no crash. At
the consumer boundary, the port tuple uses `s1=0x80110000` and
`source_word=0xFF5555FF`, while retail has the qualified
`s1=0x801B1590`/`source_word=0x00000008` tuple. This selects an upstream
producer/state-field divergence before downstream output; exact writer
attribution remains unevaluable because the two logs lack a shared invocation
ordinal. Evidence: [M5-S3471-OUTPUT-STATE-TUPLE.md](M5-S3471-OUTPUT-STATE-TUPLE.md).

Session 3472 asked the independent oracle to watch physical table span
`0x001B4AA0..0x001B4B24` with a same-run whole-RDRAM control. The control
recorded 13,527 writes, the span 3,527 writes, and the title phase reached
634 width-1024 VI frames. Title-gated writer rows were live at
`0x800078EC`, `0x80064350`, `0x80064360`, `0x80064378`, and `0x800646D8`;
post-store sampling recorded 267 samples with 115 nonzero bytes and the
candidate writers were each observed with nonzero values. This refutes
`H-ObservationInvalid` and establishes active retail producer writers, but
does not select `H-RetailStateWriter` over `H-PortPointerSelection` because
the oracle has no selected-entry identity for an ordinal join. Evidence:
[M5-S3472-RETAIL-STATE-WRITER.md](M5-S3472-RETAIL-STATE-WRITER.md).

Session 3473 joined the existing port table-selection, producer-input, and
output/state witnesses in one title-gated image-arm capture. Both positive
controls fired; the run produced 2,048 table rows, 1,024 producer rows, and
514/510/510/514 rows at the four target PCs. Port producer values included
`0x801B4F00` and `0x801B5E70`, matching the qualified retail value family,
while the downstream port state pointers were in the `0x80110xxx` family
instead of retail's qualified `0x801B1590` tuple. This selects
`H-PortPointerSelection` and rules out an absent port observation, but does
not name the pointer writer or transformation. Evidence:
[M5-S3473-PORT-STATE-JOIN.md](M5-S3473-PORT-STATE-JOIN.md).

Session 3474 ran the required independent retail span preflight and a
regeneration-safe port store census. Retail's whole-RDRAM control fired
2,255,979 times, the physical `0x00110000:0x00112000` span was active, and the
run reached 3,269 VI. The final port capture reached title and hangar, passed
both existing M5 controls, and emitted 1,024 pointer-valued stores in that
span. The first candidate construction PCs were `0x800027C4`, `0x800027D0`,
`0x800027DC`, and repeated `0x80003C28` stores forming `0x80111xxx` links.
Because the rows lack a shared producer/consumer ordinal and do not include
loads, this narrows the candidate set but selects neither pointer-writer nor
alternate-dispatch hypothesis. Evidence:
[M5-S3474-POINTER-WRITER.md](M5-S3474-POINTER-WRITER.md).

Session 3475 joined the four candidate port store PCs to the title-gated
`rs_free` consumer boundary. All three port controls fired and the run
emitted 1,024 candidate stores plus 512 consumer rows. No consumer row's
nonzero latest candidate value matched its incoming `s1`; repeated
`0x80003C28` values were different `0x80111xxx` links. The independent retail
preflight also had live consumer execution and candidate-span activity. This
selects `H-AlternateDispatch` for the four measured latest-store links and
rules out `H-InterveningPointerWriter` at that scope. An uninstrumented writer
or route difference remains possible. Evidence:
[M5-S3475-POINTER-JOIN.md](M5-S3475-POINTER-JOIN.md).

Session 3476 audited the complete generated caller path for the remaining
`0x80005268 -> rs_free` edge. There is one direct edge, inside `rs_zcfree`,
and one generated caller at `zcfree` `0x80029CFC`; `rs_zcfree` performs no
`$s1` load or assignment between them. The independent retail oracle's
whole-RDRAM control fired 10,000 callbacks, title 1024 was reached, and the
edge executed 825 times. The fixed image-arm port run reached title 1024,
emitted 827 sole-edge rows and 512 consumer rows, and 477 consumer rows
matched the latest sole-edge `$s1`; the 35 nonmatches are other `rs_free`
callers with a stale sole-edge latch. This selects the inherited caller-side
edge as the source at that scope and rules out an uninstrumented assignment
between `0x80005268` and `rs_free`, but it does not explain the downstream
state/output divergence. Evidence: [M5-S3476-ZCFREE-EDGE.md](M5-S3476-ZCFREE-EDGE.md).

Session 3477 ran the independent retail preflight before building the port
witness. Retail's whole-RDRAM control recorded 4,990,424 writes, title reached
2,654 VI, and the selected post-edge `rs_free` PCs were live. The corrected
port image arm reached title with no crash; title, downstream-store, four-PC
schema, and zcfree controls all fired, producing 2,048 downstream-store rows
and 512 consumer rows. Zero latest enumerated store addresses equalled `s1`
or fell within `0x100` bytes of it; 477 rows retained a matching zcfree latch.
This rules out the enumerated early `rs_free` stores as the first consumer
state mutation at this scope, but does not distinguish a later guest mutation
from the host callback/task/output boundary. Later store PCs were hidden by
the row cap and need a narrower capture. Evidence:
[s3477_m5_downstream.md](../scratch/agent/s3477_m5_downstream.md).

ORIGIN: the new witness observes generated store addresses and values only;
it does not rewrite, skip, or validate any pointer or state value.

Session 3478 added regeneration-safe post-call `osSendMesg` and host
audio-task enqueue/output witnesses. The independent retail preflight passed
the whole-RDRAM control, reached title origin `0x00790400`, and found the six
selected late `rs_free` PCs absent while `0x80033410` was active. Three port
route attempts stopped in the 640 phase, so the new title-gated rows were
zero. This is an instrument/build result, not a downstream hypothesis
selection; re-qualify the title route before interpreting the null. Evidence:
[M5-S3478-DOWNSTREAM-INSTRUMENT.md](M5-S3478-DOWNSTREAM-INSTRUMENT.md).

Session 3479 re-qualified the route. Retail's whole-RDRAM control and title
phase fired, and `0x80033410` was active. The initial port arm reached title
and hangar, passed the downstream-store positive control, and produced 481
host-task plus 512 post-call rows, but its shared store cap was consumed by
earlier `0x80001D10`/`0x80001D3C` sites. A built late-only filter on the same
route reached title and produced 486 host-task plus 512 post-call rows, but
zero late-store control/store rows. The current generated `rs_free` source
contains writer-parity hooks at the six late PCs, not the regeneration-safe
downstream hook, so this is an instrument-path gap, not a guest-store null.
No downstream hypothesis is selected. Evidence is in
`scratch/agent/s3479_m5_downstream_requal/`.

Session 3480 rebuilt the late-only capture after the generated-path audit.
The independent retail preflight passed 10,000 whole-RDRAM control hits,
reached title 1024, observed `0x80033410`, and recorded zero executions at
all six selected late `rs_free` PCs. The port reached title 1024, fired its
host-boundary positive control, and emitted 483 host-task plus 512
`osSendMesg` return rows, but zero late-store control/store rows. The helper
is present at all six generated sites, so the null is a qualified absence of
that guest path. Two independent lines rule out the selected late guest
writer at this boundary; the host task/send/output contract remains
unresolved. Evidence: [M5-S3480-LATE-STORE-BOUNDARY.md](M5-S3480-LATE-STORE-BOUNDARY.md).

ORIGIN: this iteration only observes guest-PC execution and host/task/send
fields; it does not rewrite or validate guest state.

Session 3481 joined the independent retail `OSTask` dump to the port host
task/send capture. Both controls and the title phase were live. At enqueue PC
`0x80033FCC`, both arms used task pointer `0x80149470`, type 2, and zero
output/yield fields, but retail's first title task had `data_ptr=0x80171CE0`,
`data_size=2`, while port's first row had `data_ptr=0x8018FB70`,
`data_size=3`. This selects the first task-field divergence and rules out an
absent task hook or send-only divergence at this scope. The guest writer and
payload legitimacy remain unresolved; evidence:
[M5-S3481-HOST-TASK-JOIN.md](M5-S3481-HOST-TASK-JOIN.md).

ORIGIN: this iteration only observes retail and port task fields and queue
returns; it does not rewrite, skip, or validate the differing payload.

Session 3482 added a regeneration-safe title-scoped witness to the existing
generated guest-store hook and joined it to a fresh independent retail task
span watch. Both controls and both title origins were live. Retail's task-span
writer histogram and the port witness contain the same ten writer PCs
`0x80091718` through `0x80091784`; the port emitted 204–205 rows per PC. This
rules out an absent or wholly different writer route at this boundary. The
resulting payloads still diverge: retail task rows use `0x80171CE0` or
`0x80173B20` with sizes 1–2, while port enqueue rows also expose
`0x8018DD30`/size 3 and `0x8018FB70`/size 1. This selects the broad
payload/operand divergence boundary and rules out invalid observation and a
writer-route-only explanation, but does not establish whether the differing
operand is supplied at `0x8009177C/0x80091784` or mutated afterward. Evidence:
[M5-S3482-TASK-WRITER-JOIN.md](../M5-S3482-TASK-WRITER-JOIN.md).

ORIGIN: the new witness observes generated task-struct stores and values only;
it does not rewrite, skip, or validate task fields.

Session 3483 joined independent retail post-store values to the port writer and
enqueue rows. The oracle whole-RDRAM control fired 15,248 times, the physical
task-field watch fired 5,248 times, and title reached 633 width-1024 VIs; its
post-store detail captured 629 rows at each target PC. Retail stored only
`0x80171CE0` or `0x80173B20` at `0x8009177C`, with size 1 or 2 at `0x80091784`.
The validated port arm fired its task-writer and downstream positive controls,
reached title, and emitted 480 enqueue rows plus 2,048 writer rows. Port title
writer values included the same two retail values but also
`0x8018DD30`/size 1 and `0x8018FB70`/size 3; the enqueue rows carried those
same extra payloads. This selects `H-WriterOperand` at the measured boundary
and rules out an intervening payload mutation there. It does not identify the
upstream producer of the extra port operands. Evidence:
[scratch/agent/s3483_m5_task_field_writer/RESULTS.md](../scratch/agent/s3483_m5_task_field_writer/RESULTS.md).

Session 3484 performed the planned producer-span capture. The retail oracle's
whole-RDRAM control fired 24,592 times, candidate spans
`0x18DD20:0x18DD50` and `0x18FB60:0x18FB90` fired 4,681 and 4,673 times, and
the task-field watch fired 5,238 times across 632 title VIs. The port reached
title, fired the source-span and task-writer controls, and emitted nine source
rows: initialization and nearby-field stores at `0x80091078`, `0x8009114C`,
`0x80091168`, and `0x80091170`; it did not store either extra operand into the
candidate spans. The same port capture emitted 205 rows for each normal task
operand but one row each for `0x8018DD30` and `0x8018FB70`. This rejects the
candidate-span-store producer hypothesis at the measured scope and moves the
unresolved edge to the upstream read/table-selection path. Evidence:
[M5-S3484-PRODUCER-SPAN.md](../M5-S3484-PRODUCER-SPAN.md).

Session 3485 joined an independent Rice-oracle execution-range capture to a
new regeneration-safe port selector witness. Oracle whole-RDRAM and candidate
span controls fired (19,300 and 4,643/4,657), title reached 3,566 VI, and the
preceding block executed 154,327 times overall. Port selector rows at
`0x800916F0` included extra sources `0x8018FB70` and `0x8018DD30`, while the
retail writer evidence remains restricted to `0x80171CE0`/`0x80173B20`. This
selects the pre-writer selector/load divergence and rules out an intervening
mutation as the first measured edge. The upstream table read/writer is
unresolved. Evidence: [M5-S3485-SELECTOR-JOIN.md](M5-S3485-SELECTOR-JOIN.md).

ORIGIN: the probe is diagnostic-only; it does not rewrite, skip, or validate
task fields.

Session 3486 joined the exact selector pointer word. Retail's whole-RDRAM
control fired, the title phase reached 632 VI, and physical `0x80149750` had
3,228 writes and 78,106 reads; all title-phase pointer writes were attributed
to `0x80091074` (629 phase rows). The qualified port retry passed its controls,
reached title, and likewise attributed its bounded pointer stores to
`0x80091074`. Port normal values matched the known retail family, with one
title `0x8018DD30` selection/store; no `0x8018FB70` appeared in this retry.
This rules out a writer-route-only explanation and narrows the gap to writer
input/value or a later selection transform. The exact cross-runtime writer
value join remains unresolved. Evidence:
[M5-S3486-SELECTOR-POINTER.md](M5-S3486-SELECTOR-POINTER.md).

ORIGIN: the witness observes the pointer word, selector registers, and writer
PC/value; it does not rewrite, skip, or validate task fields.

Session 3487 qualified the independent retail side of the planned writer
input/value join: whole-RDRAM control fired 12,029 times, physical selector
word `0x00149750` was written 2,029 times, and the `0x80091074` execution watch
fired 3,096 times including title rows. The matching port hook built
successfully, but two unchanged prescribed LLE/spin-yield retries with
`ROGUESQ_AUDIO_UCODE=1` crashed before title in `fillSampleStreamRange` at
guest PC `0x8000B650`; both emitted zero title writer rows. The join is
therefore unevaluable and no writer-input or later-transform hypothesis is
selected. Evidence: [M5-S3487-WRITER-INPUTS.md](M5-S3487-WRITER-INPUTS.md).

ORIGIN: diagnostic-only writer-register/value observation at `0x80091074`; it
does not rewrite, skip, or validate task fields.

Session 3488 ran the prescribed silent port arm with `ROGUESQ_AUDIO_UCODE=0`.
It reached title origin `0x00790400` at width 1024, fired the existing
positive controls and the `0x80091074` selector-writer control, emitted 1,024
bounded writer rows, later reached hangar width 512, and produced no crash or
abort marker. Audio dispatch identified the `musyx_stub` arm, with no real
image-stage rows as expected. This selects the route-specific audio blocker
seen in Session 3487: disabling the audio image removes the pre-title
`fillSampleStreamRange` failure and restores the writer target. The retail
capture has 533 title rows versus 1,024 port rows; because these are separate
animated runs, ordinal writer-input/value joining is invalid. The writer-input
and later-transform hypotheses therefore remain open. Evidence:
[M5-S3488-AUDIO-DISABLED-ROUTE.md](M5-S3488-AUDIO-DISABLED-ROUTE.md).

ORIGIN: diagnostic-only audio-dispatch and selector-writer observations; no
task fields or selector values were rewritten, skipped, or validated.

Session 3489 performed the prescribed non-ordinal join at `0x80091074` using
title origin, writer PC, selector value, and operand-class fields. The
independent retail control and the port selector/task controls all fired.
Retail had 533 title rows, all selector value `0x80171CE0`; the silent port had
1,024 rows: 512 `0x80171CE0`, 511 `0x80173B20`, and one `0x8018DD30`. The
common source family and route-exclusive port families remain visible under
operand-class joins. This selects `H-WriterInputDivergence` and rules out a
later-transform explanation at this boundary; the upstream selector/table
producer is unresolved. Evidence: [M5-S3489-NONORDINAL-WRITER-JOIN.md](M5-S3489-NONORDINAL-WRITER-JOIN.md).

ORIGIN: diagnostic-only parsing of existing rows; no selector or task field
was rewritten, skipped, or validated.

Session 3490 qualified the independent retail predecessor boundary before
building. The oracle whole-RDRAM control fired, both title origins appeared,
and paired execution watches at `0x80091060` and `0x80091074` each produced
2,555 rows; retail's indexed load returned selector indices 0/4 before
publishing the known `0x80171CE0`/`0x80173B20` source family. A new
regeneration-safe port witness was added immediately after the `0x80091060`
load and the full build succeeded. The fixed silent LLE/spin-yield retry,
however, remained in the 640 route for its 30-second watchdog and emitted zero
title controls, load rows, and writer rows. The port-vs-retail discriminator is
therefore unevaluable, not null; route re-qualification is required before
interpreting the witness. Evidence: [M5-S3490-UPSTREAM-SELECTOR-LOAD.md](M5-S3490-UPSTREAM-SELECTOR-LOAD.md).

ORIGIN: the new witness observes selector index, table address, loaded value,
and register context; it does not rewrite, skip, or validate selector state.

Session 3491 retried the prescribed silent LLE/spin-yield route with the new
selector-load witness. The 30-second arm crashed before title at guest PC
`0x8000834C`, with host `spTaskSchedulerThread+9556`; all title controls and
selector rows were zero. A corrective 60-second retry of the same route also
crashed before title, now at `fillSampleStreamRange+932` below
`musyxRenderVoiceSamples`/`musyxSynthFrame`, again with zero title controls
and rows. This makes the route failure reproducible and rules out watchdog
duration as its explanation, but leaves the selector discriminator
unevaluable. It selects the immediate audio/scheduler qualification blocker;
whether `ROGUESQ_AUDIO_UCODE=0` is honored for every task remains unresolved.
Evidence: [M5-S3491-ROUTE-REQUALIFICATION.md](M5-S3491-ROUTE-REQUALIFICATION.md).

ORIGIN: diagnostic-only route and crash observations; no audio state,
selector value, or task field was rewritten, skipped, or validated.

Session 3492 asked the independent retail oracle first: its whole-RDRAM
control fired 10,000 writes and the phase-qualified `0x80033FCC` handoff
observed 666 type-2 tasks with `task_ptr=0x80149470` and
`data_ptr=0x80171CE0`. The matching silent port arm, with
`ROGUESQ_LOG_AUDIO_RETURN=1`, passed its dispatch positive control: 47
`[audtask-dispatch]` samples through `n=896` all reported `real_ucode=0`.
No real MusyX function or audio-return row appeared. The run instead reached
the existing `[audio-wait-pump-stall] countdown=16 after 64 musyxSynthFrame
pumps` and never reached title. This selects `H-SilentGateHonored` at the
dispatch boundary and refutes `H-SilentGateBypassed`; it does not qualify the
silent route or select a non-audio scheduler fault. The selector witness
remains unevaluable on this arm. Evidence: [M5-S3492-AUDIO-DISPATCH-GATE.md](M5-S3492-AUDIO-DISPATCH-GATE.md).

ORIGIN: the dispatch witness is observational; it does not alter task routing,
audio state, wait behavior, or selector data.

Session 3493 ran the required independent retail preflight first. Its
whole-RDRAM control reached 10,000 writes, the `0x80033FCC` execution watch
recorded 6,358 hits, and the phase-qualified task dump recorded 1,257 type-2
rows including title origins. The prescribed real-audio port arm selected
`real_ucode=1` in 48 dispatch samples, but crashed before title in
`fillSampleStreamRange` at guest PC `0x8000B650`; selector controls/rows and
the audio-return marker were zero. This selects the real-audio route blocker
and refutes a dispatch-setting failure at this scope, but leaves the selector
discriminator unevaluable. Evidence: [M5-S3493-REAL-AUDIO-SELECTOR.md](M5-S3493-REAL-AUDIO-SELECTOR.md).

ORIGIN: diagnostic-only oracle, dispatch, phase, selector, and crash
observations; no audio state, selector value, task field, or route behavior was
rewritten, skipped, or validated.

Session 3494 repeated the prescribed real-audio/LLE/spin-yield capture with
the existing positive controls. The route reached title origin `0x00790400`,
fired both selector controls, emitted 1,024 selector-load and 1,024
selector-writer rows, and recorded 62 audio-dispatch plus 260 audio-return
rows. No crash, abort, or last-guest-PC marker occurred during the 60-second
watchdog window; the first title source included `0x8018DD30`, followed by
the known `0x80171CE0`/`0x80173B20` families. This selects
`H-RealAudioRouteTransient` and refutes a stable pre-title
`fillSampleStreamRange` failure for this recipe, but it does not compare the
selector rows against retail. Evidence: [M5-S3494-REAL-AUDIO-ROUTE.md](M5-S3494-REAL-AUDIO-ROUTE.md).

ORIGIN: diagnostic-only route, selector, audio-dispatch, and audio-return
observations; no audio state, selector value, task field, or route behavior
was rewritten, skipped, or validated.

Session 3495 ran the independent retail selector arm first. Its whole-RDRAM
control passed with 10,000 callbacks, title reached origin `0x00790400`, and
the two watched selector PCs produced 78 rows each: load index `0x4` and
source `0x80173B20`. The first real-audio port invocation emitted 48 dispatch
rows but no title or selector controls. A fixed direct-PID retry of the same
route again emitted zero selector controls/rows and crashed at guest PC
`0x8000834C` in the width-640 scheduler/audio path. The selector comparison
is unevaluable; the retail data is not a valid animated A/B against the failed
port route. This selects a transient route-qualification blocker and rules
out an absent retail selector observation, but selects neither selector parity
nor source divergence. Evidence: [M5-S3495-SELECTOR-COMPARISON.md](M5-S3495-SELECTOR-COMPARISON.md).

ORIGIN: diagnostic-only oracle and port route/selector observations; no audio
state, selector value, task field, or route behavior was rewritten, skipped,
or validated.

Session 3496 ran one fresh direct-PID real-audio/LLE/spin-yield port arm with
the existing phase, task-writer, selector, and audio-return controls. It
exited with SIGSEGV before title after 11 seconds; no title or selector
controls/rows fired. The last guest PC was `0x8000B650`
(`fillSampleStreamRange`), while the host stack was in RT64 framebuffer
writeback. This fresh failure is distinct from Session 3495's `0x8000834C`
failure, so the selector comparison remains unevaluable and no selector
parity/source hypothesis is selected. Evidence:
[M5-S3496-REAL-AUDIO-ROUTE.md](M5-S3496-REAL-AUDIO-ROUTE.md).

ORIGIN: diagnostic-only route, phase, selector, audio-return, and crash
observations; no audio state, selector value, task field, or route behavior was
rewritten, skipped, or validated.

## Next steps

1. Execute M5 plan Step 1: one build and one phase-gated run containing the
   silent control and the default real image arm, with task dispatch/exit,
   DMEM/DMA, SP completion, service/slot, PCM, and route controls. The
   discriminator is whether the image arm reaches the target phase and shows
   downstream progress beyond the silent arm; a pre-title image crash remains
   a route qualification failure, not evidence about selector data.
2. After the real-audio route and both selector controls fire, run the
   selector-load/writer capture with the existing four-PC controls and the
   independent retail task-dispatch control in the same iteration. The
   discriminator is whether both port selector controls fire at title and
   whether their source/value rows match the retail title route.
3. If the selector comparison identifies a first divergent source/value,
   trace the
   upstream selector/table producer feeding `0x80091074` with one batched
   retail/port discriminator keyed by source family and title origin.
4. Keep Sessions 3494–3496's real-audio route outcomes and Session 3492's
   dispatch result as baselines; do not repeat any unchanged route retry.
4. Keep Session 3488's silent route as the qualification baseline; do not
   repeat the same silent gate audit unchanged.
5. Retain the Session 3486 pointer-word result; do not repeat the exact
   pointer-word writer histogram unchanged.
7. Retain the Session 3484 retail writer census and port source-span rows; do
   not repeat the rejected candidate-span store capture unchanged.
8. Retain the Session 3483 retail post-store table and Session 3482 port
   writer/enqueue rows; do not repeat either unchanged capture.
9. Retain the Session 3468 retail post-store table and Session 3473–3475 port
   joins as baselines; do not repeat either unchanged capture.
10. Keep the controlled phase/PC/ordinal join as the baseline; do not compare
   sequential silent/image rows as an animated A/B.
11. Matching fields close the boundary; the first divergent field selects the
   missing contract edge. Keep the retail oracle and port positive controls
   in the same run before trusting any null.
12. Keep M5 Step 3 gated until that output comparison names one missing
   image-task/output contract edge. The M5 design inventory is complete in
   [M5-AUDIO-PLAN.md](M5-AUDIO-PLAN.md). Configured-host PatchesLib validation
   is an external dependency; this Unix checkout lacks its MIPS toolchain and
   generated patch input.
13. After M5 closes or a new discriminator is found, resume only systematic M3
   idiom-class audits. Keep external retail-entry, hangar `0x8000`
   Y/accumulator arithmetic, and SP-yield/MORT publication threads parked.
   Generated-symbol renaming is last priority and remains closed at its
   measured scope.

Closed or parked boundaries include the task-start guest-pointer guard, the
`0x800919D4 -> 0x800919EC -> 0x80007910` callback chain, the B1C source census,
the generated free-list-walk class, direct `setDisplayMode` count boundary,
direct `initN64RspMixer` boundary, and corrected MORT descriptor edge `+0x190`
to `dmaVoiceSampleAndSignal`.

## Durable boundaries and operating rules

Factor 5 uses [F5-UCODE-REFERENCE.md](F5-UCODE-REFERENCE.md), not standard
F3DEX assumptions. The qualified graphics path is LLE-only. Interpreter
limits, null-GBI guards, and similar defenses are safety mechanisms, not
explanations. Overlay dispatch is sufficient for the validated route.

Ask the independent retail oracle for ground truth before adding port
instrumentation. Every instrument needs a same-run positive control, a
phase-scoped budget, and two independent evidence lines before promotion.
Phase-gate animated comparisons on VI transitions. Batch all A/B arms in one
build and run. A null without a positive control is worthless.

Regeneration order is `make_elf.py -> N64Recomp -> fixup_game_funcs.py -> CMake`.
Never hand-edit generated functions for behavior changes. If `lib/` changes,
run `./submodule-patches/export.sh` and commit refreshed patches in the same
iteration. Never run submodule update, checkout, clean, or hard reset commands.
Kill runs with SIGKILL and run from `build/`. A mitigation-shaped change needs
an `ORIGIN:` line naming the writer and stating whether its value is legitimate.

CMake's `RECOMP_FUNCS_DIR` is `../N64Recomp/RecompiledFuncs`. The strong
SP-task override and completion-aware `osSpTaskYielded` contract are current
defaults; request-only behavior is superseded. Static boundary-only symbol
classifications are not renames without defensible semantic evidence.

## Superseded conclusions

The original overlay/menu-only explanation, intrinsic VI-640 flakiness,
missing-input and wait-return explanations, global-zero image-DMA theory,
route-wide PCM-gap theory, and force-zero default policy are superseded at
their measured scopes. They were believable before qualified routes,
same-build controls, or independent retail attribution existed.

The request-only SP-yield/viewer-stall chain from sessions 3288–3302 describes
only the old diagnostic arm; completion-aware default behavior in s3304
returns the viewer. The old interpretation of the 1,578-entry cinematic pool
as an audio-slot pool was superseded by the MusyX voice-table measurement.

The s3402 claim that `0x8002BEEC` was the retail JAL dispatch to `0x800078EC`
is not a current oracle target. Later same-route adjacent-PC captures found
zero at both addresses while `0x800078EC` was live; the earlier attribution is
route-dependent and unreconciled. Do not treat it as a writer without a new
independent discriminator.

## Evidence index

Latest state-pointer/output evidence:

- [M5-S3445-STATE-POINTER-ENTRY.md](M5-S3445-STATE-POINTER-ENTRY.md)
- [M5-S3448-STATE-POINTER-PHASE.md](M5-S3448-STATE-POINTER-PHASE.md)
- [M5-S3447-STATE-POINTER-CHECKPOINT.md](M5-S3447-STATE-POINTER-CHECKPOINT.md)
- [M5-S3444-STATE-POINTER-PRODUCER.md](M5-S3444-STATE-POINTER-PRODUCER.md)
- [M5-S3443-FREQUENCY-OUTPUT-JOIN.md](M5-S3443-FREQUENCY-OUTPUT-JOIN.md)
- [M5-S3442-FREQUENCY-OUTPUT-USE.md](M5-S3442-FREQUENCY-OUTPUT-USE.md)
- [M5-S3441-FREQUENCY-CONSUMER.md](M5-S3441-FREQUENCY-CONSUMER.md)
- [M5-S3440-SEND-RECEIVE-JOIN.md](M5-S3440-SEND-RECEIVE-JOIN.md)
- [M5-S3438-FREQUENCY-CALLERS.md](M5-S3438-FREQUENCY-CALLERS.md)
- [M5-S3437-FREQUENCY-ENTRY.md](M5-S3437-FREQUENCY-ENTRY.md)
- [M5-S3410-FIELD348-INPUT.md](M5-S3410-FIELD348-INPUT.md)
- [M5-S3400-FIELD348-PRODUCER.md](M5-S3400-FIELD348-PRODUCER.md)
- [M5-S3398-STAGE3-DESTINATION.md](M5-S3398-STAGE3-DESTINATION.md)
- [M5-S3376-ZERO-PCM-SOURCE.md](M5-S3376-ZERO-PCM-SOURCE.md)

Earlier detail is preserved in the ledger and the M5 archive sections of
[PROJECT-OVERVIEW.md](PROJECT-OVERVIEW.md). Use bounded `grep`/`sed` windows
for `PORTING-STATE.md`; never read it wholesale. The soak queue is consumed by
automation; fold only new tail lines into the next audit.
