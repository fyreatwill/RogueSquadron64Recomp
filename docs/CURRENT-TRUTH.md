# Rogue Squadron 64 Recomp — current truth

Compact operational state for [PORTING-STATE.md](../PORTING-STATE.md). Historical
detail from s4269 onward is preserved in
[M5-CURRENT-TRUTH-ARCHIVE-s4269.md](M5-CURRENT-TRUTH-ARCHIVE-s4269.md) and the
append-only ledger. This file is intentionally limited to live state,
qualified evidence, open hypotheses, and the next bounded work unit.

Updated for session 4432 (2026-10-09). Session 4415 was a maintenance pass:
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

Session 4430 (port arm of s4428): the port runs the same 16-byte name copy at
`0x80007670` onto zeroed `0x80171CD0`/`0x80173B10` and publishes
`0x80171CE0`/`0x80173B20` with headers `2/0x1E30` and user words
`6D61745F`/`6C746578...` identical to retail. This selects H-port-same and
refutes H-port-no-copy and H-port-heap-first; the table words are not the
selector divergence. ORIGIN: read-only port RDRAM witness; nothing rewritten.

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

- s4414/s4416/s4417 "port/retail selector-path divergence at `0x80029E80`" was
  believable because the port witness sat on guest PCs, but the port routes
  osAiSetNextBuffer through a host shim. s4432 saw the generated submit call at
  `0x8008EE84` fire every title loop iteration.

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
- "The port's audio thread paces ~1 buffer/VI, half of what is needed" (s4435)
  was believable because 59 vs 115 buffers/s looked like a 2x submit gap; s4437
  showed retail also submits ~1 per VI, so the gap is in the 115/s figure or
  the SDL side, not in the game-side submit rate.

## Next steps

- **s4467 (newest):** the queued s4467_hdr_nested soak was INVALID (recipe `cd` resolved to scratch/, no game launched, false rc=0); no evidence either way. Recipe fixed (git rev-parse root) and requeued as s4468_hdr_nested; read its result first and confirm non-zero rs-malloc lines before trusting it. Soak recipes must not use dirname math for the root.
- **s4466 (prior):** header-dump hook built (tools/apply_s4466_hdrdump.py; `[rs-hdr]`, `[rs-hdr-nested]`); 0/4 runs reached VI 1024, so s4465's A-vs-B is unresolved. Candidate unlogged free: coalesceFreeHeapBlocks, called inside rs_malloc.
- **s4465 (single-source 1/3 runs):** VI-1024 crossing reproduced; rs_malloc(3964)=0x801931F0 overlaps live 0x30/0x300 blocks never rs_free'd in log -> allocator overlap (A) selected unless an unlogged free path exists. See PORTING-STATE s4465.
- **s4464 (partly superseded by s4465):** s4463's allocator-overlap reading is REFUTED at VI 640: the insert clusters are per-phase rs_malloc'd 0xF7C tables (0x801920A0, 0x8021D5D0); the pool alloc 0x80193C20 follows the free of the first and lies outside it. Block 0x801767E0 (0x1E000) is freed by the game's own coalesceFreeHeapBlocks, not leaked. in_pool_range never fired (0/4 runs, none reached VI 1024), so s4462's crossing is unreproduced. Next: reach VI 1024 and log inserts there.
- **s4463 (superseded by s4464):** insert pointers (relocateSndPointer base + 0x18-stride record offsets, 0xFFFF-sentinel bounded) span 0x801928E8..0x8021E538 (~0x8C000 B); buildSongDecodeBufferRing's rs_malloc returned node block 0x80193C20 / buffer 0x80196CC0 inside that span at VI 640 (3/3 arms, hooks live, port-only). Bad-bound (P) refuted; allocator-overlap (R') selected. Next: log rs_malloc/free vs the SND span, then oracle.
- **s4462 (prior):** factor5SortedTableInsertWidePair is called once per 0x18-byte record in a descending run that, at VI 1024, crosses 0x80193B00..0x80194C00 - the audio node pool (head 0x801499B0, 0x14-stride, init pcs 0x8008F6F4-0x8008F818). 6/6 arms, hook control live; port-only (single-source). SND record array and pool overlap in the port (F). Next: find the caller supplying run base/count (ra of the insert) and compare with the oracle: does retail's run end below the pool?
- **s4461 (newest):** pc 0x800853A8 = shift loop of factor5SortedTableInsertWidePair; C18 (a1, first stored at 0x80085424) is a caller-supplied relocated SND pointer, not a pool-link writer (code reading, single-source). Open: does that SND pointer overlap the later-built audio node pool (F) or not (E)? Next: log insert args+ra and pool/SND allocator ranges in one run.
- **s4460:** only writer of a 0x80193C18 value is pc 0x800853A8 filling a 0xC-stride table at 0x8013B060 (VI 1024, 6/6 arms, ctl fired); no C18 store into the pool list => refutes stray-store (A); lead (D) = who consumes that table. Next: name 0x800853A8 and watch reads of 0x8013B0xx entries.

0k000. **s4454 (oracle, control OK): retail musyxMixActiveVoices loops run a fixed 45,700x/20 s (2,285/s), cmdlist build 23,900x; next: port-side per-call rate (NEXT.md).** 0k00. **s4453 (oracle, positive control OK, bisected): retail executes 0x80090768-0x80091B3C 1.65M times in 20 s pre-title (control range 62.8k). This OVERTURNS s4448/s4449 "retail never renders voices" (exact-PC watch at 0x80090768 was a bad witness; hot code starts ~0x80090e04, past the KeyOnVoice trap sites). Next: oracle per-PC range histogram vs port counts; reconcile voice array base (s4448 voice0 read-watch 0 hits stands unreconciled).** 0k0. **s4449: oracle exec-watch 0x80090768+0x8008FFAC = 0 hits in 20 s pre-title (AI active; control osViSwapBuffer fired 1x, low-rate) -> single-source, overlay-alias caveat; next: range watch + AI producer attribution.** 0k. **s4448: oracle read-watch of voice0 = 0 hits in 20 s (control 2.83M) -> retail does not touch voice array in title; exec-watch 0x8008FFAC next.** 0k2. **s4447 (offline, single-source: s4441 log + generated code): all 4 guest callers of fillSampleStreamRange are inside musyxRenderVoiceSamples; the port renders 31 voices (0x801951B8+i*0x88) round-robin from one frame; the `ra=` column is dead (recomp omits r31 on jal). Next: per-voice state dump + oracle read-watch of voice 0 (see NEXT.md).**
0j. **s4446 (oracle, two lines: head/tail/pool each written once, at init pc=0x8008F8C8 t=0.1s, over 60 s retail; whole-RDRAM control 10000 hits): retail never touches the sample-stream allocator list after init in boot/attract/title.** The port's ~1 insert per fillSampleStreamRange call is port-induced; "missing retire path" (s4445) is the wrong frame. Exec-watch of 0x8008FAAC was unusable (its control osViSwapBuffer fired once in 3600 VI). Next: identify the port's callers of fillSampleStreamRange (ra histogram of [s4234-ENTRY]); hangar untested.
0i. **s4444 (offline, single-source): B1 is a null pop of an exhausted chain** (head 0x801FAB68 len=1 -> head=0 -> fillSampleStreamRange derefs guest 0). Chain len=256 is the walker cap, not real length. Next: push vs pop counts per window from [s4234-ENTRY] rows, then oracle-compare retail.
0h. **s4443 (1 run per arm): s4442's "B1 pool overrun / unnamed writer" premise is superseded.** Store watch with passing control (0x801F9CE0) shows 0x801FB3F0->0x801FB408 and 0x801FB408->0x801FB420 are written by guest init 0x8008F90C as normal chain links; the pool is larger than the 247 nodes s4442 assumed. 115 Hz arm B ran clean 150 s; unset arm A hit a host bus error. Next: re-derive B1 without the 247-node assumption; repeat arms for crash rate.
0g. (superseded by 0h) **s4442 (offline, single-source): the two s4441 fillSampleStreamRange+15116 crashes are different shapes.** A1 = the s4279 whole-block zero wipe; B1 (115 Hz) = no wipe, the node pool is popped past its last node (0x801FB3F0 next = 0x801FB408, out of the 247-node block) so tail/pool land outside the heap. Init writes 0 in that word, so its writer is unnamed. Next: store watch on 0x801FB3F0/0x801FB408 with positive control, both arms in one iteration (NEXT.md).
0f. **s4440: 192 frames/submit is a guest constant (0x300 B immediate, runAiAudioStreamPlaybackLoop 0x8008EE08/EE84); the loop is paced by OS_EVENT_AI, which the port posts once per VI (events.cpp vi_thread_func).** Real hardware posts per buffer drain (~114.8/s). `ROGUESQ_AI_EVENT_HZ=115` (default off) lifts port submits 59.3 -> 110.6/s (arm A control crashed in fillSampleStreamRange before phase 4; baseline from s4435). Not yet checked: audible quality, soak stability, whether retail really runs ~115/s (mupen shows ~60/s; its AI timing is suspect). **s4441: 2x2 soak (115 vs unset) all crashed; fillSampleStreamRange+15116 in both arms (A1,B1), musyxSynthFrame+5436 once (B2, reached title), RT64 assert once (A2). 115 Hz not default-ready, not the crash cause.** Next (`m5-ai-event-cadence`): run the 115 Hz arm in a soak with the passive instruments, check queue depth stays bounded and the title phase completes; if stable, decide default-on and record the oracle disagreement as an emulator artifact only if a second witness (e.g. mupen CPU Count per submit) confirms.

0e. **s4439: oracle AI_LEN read is valid (control: nonzero on 98.7% of title VIs, avg 379 B) and the DAC is ~99% busy, yet retail submits 768 B at 0.96/VI exactly at drain.**
   So mupen plays 768 B in ~16.5 ms, ~1.9x slower than dacrate 2207 implies
   (suspect `get_dma_duration` cpu_counts estimate, ai_controller.c:62-69; not
   confirmed). The oracle's "retail ~1 submit/VI" may be an emulator artifact,
   so 0c/0d's "port starvation is retail-faithful" is downgraded. Next
   (`m5-sdl-consume-rate`): (1) oracle emulated-time per submit via CPU Count to
   confirm/refute the 2x; (2) find what sets 192 frames/tick in the guest mixer
   (constant vs derived from osAiGetLength/status); if derived, feed the port
   the real-hardware answer.

0d. **s4438: retail dacrate 2207 (22047.9 Hz) == port; retail title ~0.96
   submits/VI, 768 B each, AI idle (AI_LEN=0, status 0) at every submit.** The
   port's starved SDL queue (s4435) matches retail's own stream, so it is not
   a port defect on current evidence (AI_LEN=0 single-source, no nonzero
   control). Remaining oddity: 192 frames/buffer vs 367 expected at 60 VI/s.
   Next (`m5-sdl-consume-rate`, nearly closed): compare ucode frames-per-tick
   retail vs port, else move to the next M5-AUDIO-PLAN step.

0c. **s4437: retail title also submits ~1 AI buffer per VI swap** (oracle: 1210
   calls / 1052 vi_swaps; positive control pre-title 5882 / 464). The port's
   ~59 buffers/s is retail cadence, so the shortfall is host-side. Next
   (`m5-sdl-consume-rate`): reconcile the "115/s needed" figure (SDL freq vs
   the game's programmed AI dacrate vs bytes per submit) and log SDL callback
   consumption vs queue depth over the same title window. Build tools with
   `clang`, not `cc`.

0b. **s4435: SDL end of title audio is starved** (queue depth <= one 768 B
   buffer, device 22047 Hz). Its "port is slow to feed" reading is overturned
   by s4437; the starvation observation itself stands.

0a. **s4434: Step 10 qualification result - nonzero PCM reaches
   `queue_samples` in the port title phase** (phase 4 width 1024: 251 nonzero
   buffer reports in run, fixed_rms 2275-6484, setnext==queue ~60/s,
   task_enter==task_ok). H-source-zero / H-silent-by-design refuted. Next:
   verify the SDL device end (queued size, underrun, format) and compare
   content against retail via oracle AI DMA source. Single-source on content.

0. **s4433: both `m5-selector-entry-path` and `m5-title-reapply-config` are
   CLOSED.** Retail ALSO calls reapplyAudioConfig at the title->hangar mode
   change (chain `0x8008EB5C`->`0x8008EBC0`->`0x80091C88`->`0x80091CB8` at
   t=38.4s width 1024 and t=52.9s width 512; the port logs the first one VI
   earlier by origin label). "Retail only does in hangar" had bucketed by
   origin 0x6ab400/width 512 only. No port-vs-retail selector or reapply
   divergence remains. Next: M5 plan Step 10 qualification (NEXT.md).
   Historical item below kept for the s4432 evidence:
1. **s4432: the port's title audio loop DOES reach the `0x8008EE84` submit**
   (stages 0-3 fire in phases 2-5 incl. title, >=1536 loop iterations; the port
   calls the `osAiSetNextBuffer_recomp` shim directly, so a guest-PC witness at
   `0x80029E80` can never fire). The s4414-s4430 "retail enters `0x80029E80`,
   port enters `0x80029E78`" divergence is therefore an instrument gap, and the
   `m5-selector-entry-path` thread is closed. Remaining real difference: the
   port hits `0x80029E78` (osAiSetFrequency epilogue via reapplyAudioConfig
   `0x80091CB8`) in title while retail only does in hangar. Next work unit
   (HYPOTHESIS-ID `m5-title-reapply-config`): identify the port's title caller
   of reapplyAudioConfig (ra/state), and confirm with retail whether title
   really lacks it. Port runs die pre-title ~2/3 of the time in the phase-3
   voice/free-list corruption family; plan for retries.
2. **M3 pre-publication guard runtime qualification**, blocked until a host
   with the MIPS toolchain and `PatchesLib` is available.
3. **Generated-symbol renaming sweep**, slug
   `generated-symbol-renaming-sweep`, only when items 1–2 are inapplicable;
   mapping-only edits do not reset the engineering-change gate.

0g. **s4455: port mix-call rate is 60/s (unset) and 86/s (`ROGUESQ_AI_EVENT_DRAIN=768`) vs retail 114.3/s (2,285 epilogue hits/20 s); build calls 120/s in both arms.** Mix rate tracks AI-event rate, so the port under-drives the mixer by 25-48%. Both arms crashed at ~32 s in musyxSynthFrame+5436. **Confirmed same session: HZ=115 gives mix 114-116/s (ctl 60/s in same run) — event pacing is the whole rate gap.** Crashes occur in both arms. Next: 4+4 soak for crash parity, then active-voice count vs retail.
0h. **s4456: hz115 (mix 114/s) vs unset 4+4 soak: all 8 crash (7/8 musyxSynthFrame+5436); hz115 3/4 die at ~15 s vs ctl 0/4 early (ctl reach VI 1024 and live ~77-80 s). Single-source, n=4/arm.** Retail-rate mixing exposes the +5436 defect sooner; next: characterise +5436 (deref, voice/field, writer) with hz115 armed so it reproduces in ~15 s.
0i. **s4457: musyxSynthFrame+5436 = guest `lhu 0x10($v1)` (0x80091368) in the node countdown loop after a corrupt `next` (0x94fc in s4456 ctl; 0x80193C18, off the 0x14-stride pool grid, once in s4457). s4456's 'hz115 crashes earlier' did NOT replicate (+5436 1/20; families vary: fillSampleStreamRange+15116, bad-pc jumps).** `ROGUESQ_LOG_S4457=1` adds a last-two-writers table + list-walk check (control passes). Writer of the bad link still unnamed; treat +5436 as pool-list corruption, not a hz115 effect.
0j. **s4458: rerun of the s4457 harness (6 arms, hz115) gave 0/6 `+5436` hits** (crashes: initVec4TripletFromArgs+308, advanceSongRegion+7536); cumulative `+5436` rate 1/26. No `[s4457-ptr]` line, so writer hypotheses A/B/C stay unsplit. Don't spend more iterations re-running this harness; next unit is a single-run instrument for frees of still-linked nodes / the 0xFF fill caller 0x80061520, or pivot to M5 plan steps.
0k. **s4459 (6/6 arms, deterministic): pc 0x80061520 is the loadCharTextureSet 256-byte font LUT fill (0xFF = not-in-set), not a pool memset.** Its first table (0x80193B90..C8F, VI 640) is written BEFORE the audio node pool exists (pool words last-written by allocator clear 0x800078EC; head=0); the pool nodes (C20,C34,...) are then built on that freed memory by 0x8008F708/0x8008F7C8. So 0x80193C18 = stale 0xFF table byte just below node 1. REFUTES hypotheses B (freed-while-linked fill) and 'fill clobbers live nodes'. Legit links are never C18, so the writer of a C18-valued link (A: stray store / node-8 arithmetic, or C: unlinked reuse) is still unnamed. Next: passive log of every word store with value 0x80193C10..1F + list integrity check at musyxSynthFrame entry (NEXT.md).

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

- s4445 (single-source, port logs): the s4441 audio chain only fills — head advances 91x in first 1000 ENTRYs then ~0/1000 while tail inserts ~1/ENTRY; retire writer unnamed; next: oracle retail head-advance rate + PC of early advances (NEXT.md).

- s4450: `ROGUESQ_AI_EVENT_DRAIN=768` (default off) posts AI event from host-queue drain; soak queued (s4450_ai_drain_event.sh). **s4451 result: both arms clean for 240 s (0 crashes, reached hangar); baseline did not crash, so no positive control — uninformative (N=1).** **s4452 replicate (2 drain + 2 vi, concurrent): 4/4 arms crashed.** The drain arm crashed with the s4441 signature (fillSampleStreamRange+15116, si_addr 0x380000000, last guest pc 0x8000834c); the other 3 arms (drain2, vi, vi2) crashed with a NEW shared signature, wild host jump to 0x1859645e8, last guest pc 0x80001b08. Baseline now reproduces (positive control OK) and drain-event pacing does not prevent either crash => **AI-event cadence is closed as a crash cause** (ROGUESQ_AI_EVENT_DRAIN stays default-off). Next: oracle PC-range probe (--watch-pc-range 0x8008F000:0x80092000 with a hot-PC control).
