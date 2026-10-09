# Rogue Squadron 64 Recomp — current truth

Compact operational state for [PORTING-STATE.md](../PORTING-STATE.md). Durable
background: [PROJECT-OVERVIEW.md](PROJECT-OVERVIEW.md); audio inventory and
de-stubbing contract: [M5-AUDIO-PLAN.md](M5-AUDIO-PLAN.md).

Updated for session 4339: the fixed, qualified C904/C88C field witness reached
both target phases and rejected source/branch field parity; port C88C had
branch_state=0 on all 256 rows while retail C904 used 0x3108/0x0010 by s1,
selecting a pre-filter stream/state divergence. This is single-source
cross-runtime field evidence; host, VI, filter, and retained oracle controls
qualify the routes. Previously 4338: the qualified in-process C904/C88C field join reached
both target phases and rejected ordinal/offset payload parity; retail C904 and
port C88C diverge before the filter, selecting pre-filter route/stream
selection. This is single-source comparative field evidence; the independent
oracle controls qualify the routes. Previously 4337: the fixed same-build route A/B selected the in-process
autopilot schedule: it reached VI 512 with 253 C88C and 256 direct rows, while
the external field-key arm stopped before VI 512 and crashed at
`rs64_m5_descriptor_start+460`. This refutes stale-save and universal synth
lifetime explanations; the C904/C88C comparison can resume on the qualified
route. This is single-source port route evidence; the existing retail controls
remain independent route qualification. Previously 4336: three port field-join route attempts all crashed at
`musyxSynthFrame+4284` after VI 1024 and before VI 512, so the planned retail /
port field comparison was unevaluable. The C904 retail table remains valid.
Previously 4335: the controlled retail C904 field dump passed
whole-RDRAM, title, and hangar controls and produced stable phase-gated
object/source/branch rows. C904 is now the retail counterpart boundary for the
port C88C descriptor helper; exact payload correspondence remains open.
Previously 4333: the retail oracle reached the qualified hangar phase,
but the port C88C address had zero retail execution hits even though the
surrounding 0x8009C000-0x8009D000 range executed heavily; the exact retail
descriptor counterpart is not yet identified. Previously 4332: the C88C descriptor witness joined every valid D740
row in a qualified two-arm matrix; early descriptors match but later pointer,
word, and type/class sequences diverge, selecting pre-filter route/stream
selection. The initial matrix was invalid because concurrent frontmost key
injection drove only one arm; the fixed recipe uses the in-process autopilot
and the known M4 width qualifier. Previously 4331: the co-located D740
sequence witness placed the active caller boundary in decodeAndFillVoiceBlock
and rejected the prior
missing-entry interpretation. Previously 4330: static D740 census found no alternate generated
transfer; the runtime caller-row absence is an instrumentation/state
contradiction, not a named static bypass.
Updated for session 4327 (M5 descriptor witness rejected; CPU caller object is next boundary). Previously 4326 (clean M5 filter/output join selected input-stream divergence). Previously 4325 (M5 filter-join instrument built; matrix retries not jointly interpretable). Previously 4324 (M5 filter matrix route-qualified; both arms hit the same active callsite). Previously 4323 (caller/entry witness built; matrix route-invalid on descriptor crash). Previously 4322 (MORT reference qualified; hangar route requalified; real-image filter path absent). Previously 4321 (MORT reference qualified; runtime route did not reach hangar). Previously 4320 (MORT/filter callsites witnessed). Previously 4319 (descriptor entry reached; MORT payload/filter witnesses absent). Previously 4318 (M5 matrix route-qualified but MORT boundary absent). Previously 4317 (retail/port consumer stream diverges). Previously 4316 (retail/port consumer comparison shortfall). Previously 4315 (retail consumer boundary requalified). Previously 4314 (extended port capture valid; retail detail stream not requalified). Previously 4313 (retail/port consumer sequence matches through 4,096 rows). Previously 4312 (extended port free/read route qualified). Previously 4311 (extended port join route-invalid). Previously 4310 (port free/read join qualified).

Updated for session 4330: the generated-source census found no alternate D740
transfer; the direct/caller probe contradiction remains unresolved.

## Current state (as of s4268)

Per-session chains (s4164-s4268: object-path parity, zero-volume save artifact,
gap/stall instrument ladder, private-DMEM A/B) are archived verbatim in
[M5-CURRENT-TRUTH-ARCHIVE-s4269.md](M5-CURRENT-TRUTH-ARCHIVE-s4269.md). Only
durable conclusions are kept here.

**Route.** The validated native route boots through attribution, N64 logo, intro
cinematic, Factor 5 logo, title VI 1024 (`0x00790400`) and hangar VI 512
(`0x006AB400`) on the real-audio/LLE/ungated/solo/spin-yield route.
`ROGUESQ_AUDIO_UCODE=0` is the silent control. VI 640 is the ~52-56 s intro, not
a stuck state. Hangar geometry/colour artifacts remain.

**Audio output is real.** With a fresh 7F save the real ucode produces nonzero PCM
at title (s4225). The long "zero payload / zero volume" boundary (s4164-s4224)
was a stale persisted port save (`build/saves` 0x48 = 00 00 00; retail 7F7F7F),
closed s4224. Reset `build/saves` before any audio A/B; `RS64_EEP_TRACE=1`.
The "unrecompiled gap" 0x8002A120..0x8002B18F is libultra EEPROM/controller code
replaced natively by librecomp. The AI byte-order artifact (s4239) is fixed
(`p[i ^ 3]`, `queue_samples ^3`); 876/894 title AI buffers FNV-match ucode output.
Residual: ~3x RMS vs retail at title (unaligned phases, single-run); the
19-buffer constant -33 hangar entry transient is benign prefill (retail does it).

**M5 Step 9 callsite result (s4320).** The independent retail oracle passed its
whole-RDRAM, title/hangar, and watched-PC controls; both port arms reached
title 1024 and hangar 512. With the descriptor probe enable flag and all
candidate witnesses enabled, `init-desc` fired 928 times in the silent arm and
370 times in the real-image arm. The real arm produced 128 filter call/entry
rows, all at generated callsite `0x8009D740`; the other two enumerated
callsites (`0x8009C540`, `0x8009C88C`) produced zero rows. The silent arm
produced zero filter rows in this run. This refutes the prior null as a
coverage/config conclusion: the generated callsite is active and the MORT
descriptor path is reachable. The prior s4319 null was caused by omitting
`ROGUESQ_LOG_VI_CALLERS`, which gates `init-desc`; it is superseded below. No
decoder, AI bridge, or game-path guard changed. Callsite ownership is
static-enumeration plus port runtime evidence; the oracle supplies the
independent route control.

**M5 Step 9 route-qualified result (s4322).** With the known
`M4_Y8000_WIDTH=512` qualifier, the same-build oracle and both port arms reached
VI 512 at `0x006AB400`; neither arm crashed or aborted. The independent MORT
reference again passed four nonzero rows spanning 8000 and 16000 Hz. The silent
arm (`ROGUESQ_AUDIO_UCODE=0`) emitted 256 active filter rows at `0x8009D740`;
the real-image arm (`=1`) emitted none despite 1,095 descriptor entries and
valid PCM source/consumer activity. The route blocker is closed, but the runtime
MORT comparison is not: this selects an audio-arm path divergence, not
H-MORT, H-layout, or H-AI. Positive controls were the oracle whole-RDRAM watch,
title/hangar VI controls, and per-arm filter controls.

**M5 Step 9 matrix requalification (s4324).** The seeded-save matrix passed
the independent MORT reference, oracle whole-RDRAM/title/hangar controls, and
both port VI-512 controls. Silent and real-image arms each emitted 256 filter
rows: all active calls reached `0x8009D740` (`updateVoiceChannelParamsLarge`),
with `0x8009C540` quiet and `0x8009C88C` contributing the paired entry rows.
Both arms had 271-272 descriptor entries and 517-518 PCM-consumer rows. The
first filter payload rows matched, while later `a0/a1` and table-used/value
sequences diverged; source/output buffer geometry remained the same. Both
arms then hit the known shared `do_rom_read` crash after the target phase.

**M5 Step 9 clean filter/output join (s4326).** The seeded matrix passed
`oracle_gate=1`, the oracle whole-RDRAM positive control, oracle title VI 1024
and hangar VI 512, the MORT reference verdict, and one port VI control in each
arm. Silent and real-image arms each emitted 128 filter calls at
`0x8009D740` before the shared known crash. Both arms stayed at rate 22047 Hz
on the 17 common route-row keys, but every common row differed in source hash
and output hash; route ordinals also differed, and 15/17 rows differed in
`a0` and 12/17 in `a1`. This rejects H-output-join (equivalent filter inputs
with only post-filter output divergence). It does not distinguish descriptor
class from an earlier route/stream selection because the current join table
records rate but not descriptor type. Exact row comparison is single-source
port evidence; the independent oracle/MORT controls qualify the route and
reference decoder, not the payload values.

This refutes s4323's route/state blocker and rejects H-real-eligibility and
H-real-dispatch as explanations for the previous real-arm null. It also
supersedes s4322's real-arm-zero result, which was a route/run-state artifact,
not a stable audio-arm divergence. The remaining M5 discriminator is the
descriptor/filter payload and decoded-output join, not RSP dispatch or a game
path guard. The route-qualified payload comparison is port-side evidence; the
MORT reference and oracle are independent controls.

**M5 Step 9 descriptor witness (s4327).** Two prescribed seeded matrix runs
passed the oracle whole-RDRAM/title/hangar controls, MORT reference, and both
port arm/filter controls; each arm produced 256 filter rows at `0x8009D740`.
The RSP task `data_ptr+0x100` candidate was invalid (silent `data_ptr=0`,
image non-RDRAM). A corrected `sp+0x114` candidate was `0xB2C71180` on call
rows and zero on entry rows, also invalid. These are rejected witnesses, not
descriptor nulls. The source/output divergence remains open and no runtime
behavior changed.

**M5 Step 9 caller-object join (s4328).** The same seeded matrix passed oracle
whole-RDRAM/title/hangar controls, MORT reference, both port VI controls, and
both filter controls; silent and real-image arms each emitted 256 filter rows.
The corrected process-wide retained caller tuple nevertheless reported
`caller_join=0` in all 512 rows. The caller probe emitted only its 128
`0x8009C88C` rows and no joinable `0x8009D740` witness. This is an
instrument-boundary result, not descriptor equality or a null descriptor. The
next discriminator must capture the original arguments directly at the
`0x8009D740` filter callsite, or prove why the entry probe is bypassed.

**M5 Step 9 direct D740 witness (s4329).** The corrected build and one
prescribed seeded matrix passed the oracle whole-RDRAM/title/hangar controls,
MORT reference, both port VI controls, and both filter controls. The direct
probe immediately before the generated `filterVoiceSampleBlock` call at
`0x8009D740` emitted 256 VI-512 rows in each silent and real-image arm, with
the scoped `d740_store_n` reaching 256. The retained caller tuple was absent
(`caller_join=0`) on all direct rows, and the caller probe emitted only its
`0x8009C88C` bucket. This independently proves the D740 callsite executes and
selects an entry-bypass or transfer/probe-placement boundary; it does not
prove descriptor equality and leaves descriptor-class versus pre-filter route
divergence open. Exact direct-row comparison is port-side evidence; the
oracle/MORT controls independently qualify route and decoder behavior.

**M5 Step 9 co-located sequence witness (s4331).** The same-build seeded
matrix passed the oracle whole-RDRAM/title/hangar controls and both port VI
controls. The image arm emitted entry, post-helper, and D740 direct events
from one sequence stream; sequences 1-3 show entry+caller before their direct
rows. The silent arm reached the route controls but emitted no target-phase
sequence/direct rows. The generated source places D740 inside
`decodeAndFillVoiceBlock` (entry `0x8009C904`); `updateVoiceChannelParamsLarge`
at `0x8009C5BC` is not the containing function. Thus the s4329 missing D740
caller row was an instrumentation-boundary contradiction: the active helper
is the C88C entry helper, not a D740-site caller helper. This rejects
H-helper-not-invoked and the previous entry-bypass reading. Descriptor class
and silent/image payload ownership remain open.

**M5 Step 9 C88C descriptor join (s4332).** The corrected seeded matrix passed
the oracle whole-RDRAM positive control, title VI 1024, hangar VI 512, both
port VI controls, and both filter controls; neither arm crashed or aborted.
Silent and real-image arms emitted 255-256 C88C descriptor rows and 256 D740
direct rows. Every direct row joined the retained C88C tuple (`caller_join=1`),
closing the probe-boundary hypothesis. The first descriptor sequence was
identical in both arms (including the initial `a1=0x801B2DA0`, type 4/class
42 and the next type 2/class 37 descriptor), but later descriptor pointers and
words diverged; the joined type/class histograms also differed. This rejects
stable post-descriptor selection and selects pre-filter route/stream selection.
The paired descriptor comparison is port-side evidence; the independent
oracle and VI controls qualify that both arms traversed the same target phase.

**M5 Step 9 route recovery (s4337).** A fixed concurrent A/B copied the same
seeded save into isolated build directories and passed the host positive control
in both arms. The known in-process autopilot reached title VI 1024 and hangar
VI 512, producing 253 phase-gated C88C descriptor rows and 256 direct-filter
rows. The external field-key recipe was corrected to send its keys from boot;
it reached VI 1024 but then crashed at `rs64_m5_descriptor_start+460`, before
VI 512, with zero C88C/direct rows. The first attempt's phase-relative field
arm was invalid because it waited for VI 1024 before sending the keys needed to
reach VI 1024. The corrected result rejects stale-save/config and universal
synth-lifetime blockers and selects input/route scheduling as the current
blocker for the field recipe. Exact route selection is single-source port
evidence; the existing oracle controls remain independent controls.

**M5 Step 9 C904/C88C field join (s4338).** The qualified in-process autopilot
run passed the host positive control, title VI 1024, hangar VI 512, and both
port filter controls; it emitted 256 C88C descriptor rows and 256 direct rows,
all joined to the retained caller tuple. Against the retained retail C904
phase-512 table, the port descriptor pointers and words had no ordinal match or
stable address offset: the retail rows alternated `s1`/source/branch-state
records while the port stream began at a different descriptor sequence and
later pointer order diverged. This rejects H-payload-parity and selects
H-pre-filter-stream; it does not identify the writer or exact semantic mapping.
The comparison is single-source cross-run field evidence; the host, VI, and
retained oracle controls independently qualify the route.

**M5 Step 9 retail boundary probe (s4333).** The required 180-second retail
oracle run passed the whole-RDRAM positive control (10,000 writes), reached
title VI 1024 and hangar VI 512 at origin `0x006AB400`, but recorded zero
execution hits at exact guest PC `0x8009C88C`. A corrective range probe in the
same route recorded 999,770 hits in `0x8009C000..0x8009D000`, including the
512-wide phase, while a narrowed `0x8009C800..0x8009C900` probe recorded zero.
This is single-source retail evidence that the port's C88C symbol is not a
retail execution boundary. It makes direct retail descriptor comparison at
C88C unevaluable and selects a retail-boundary mapping probe; it does not
select silent versus real-image payload ownership.

**M5 de-stubs landed.** A11 waitForAnyAudioSlot yield (default 2000), A12 countdown
yielding spin (`ROGUESQ_AUDIO_WAIT_NOPUMP` unset=2; s4192), A15 spin-yield default
on, A13 drain-tick gate (dormant on title+hangar), A14 status-03 wait (s4296 host yield, `ROGUESQ_A14_YIELD=0` rolls back; s4297: loop IS entered in the hangar, b0 stuck 0x03, exits after ~160-180k iterations only with the yield; yield-on reaches VI 640 and then the known do_rom_read crash at 0x80001b08, yield-off stays in hangar, no crash - 2 on / 1 off runs), A9/A10 voice-base/song-tick guards (0 fires). Declared-size staging
(0x800) qualified equal to legacy 0xF80; task-contract guard rejects
ucode_data_size 0 or >0xFC0. `ROGUESQ_AUDIO_PRIVATE_DMEM` defaults ON (s4256;
=0 restores `g_lle_task_mutex` serialisation): audio 25-36 tasks/s at t=18-30
vs 7-8/s with the lock (gfx LLE holds the mutex for whole DLs, s4248/s4249).
Object-path parity (0x8008F900..0x8008F93C, s4175-s4191) is closed
parity-clean; add no more witnesses there.

**Audio gap at t~19-28 s = host renderer, not audio (s4258-s4268).** Gap seconds
are RT64 `send_dl` taking 0.2-0.9 s per gfx task (healthy 12-20 ms), persisting
in a single-arm run (no 2-instance contention). >=95% is `processDisplayLists`
CPU, waits ~0 (s4267). Hotspot (s4268): `State::checkRDRAM` XXH3-hashing a
tracked framebuffer set that grows 3 -> 56 (1.8 -> 13 MB per fullSync). The extra
framebuffers are GARBAGE colour-image sets (s4270: from t=14.09 s hangar entry,
widths 1-1217, unaligned addresses like 0x001CFFFF; sane before). Writer UNNAMED. Guest-side chain behind it: tid
3 waits on 0x8011A818 sent only by tid 0 (s4261); completions fan out from
`spTaskSchedulerThread`/`dpInterruptHandlerThread` (s4263).

**Wrap-flush restore (s4284-s4287).** ODD (garbage) colour-image sets at VI 640 come from RDP ring lap-2 stores overwriting lap-1 content before the wrap flush submits it (s4284/s4285). Feeding RT64 the bump-time shadow bytes (`ROGUESQ_WRAP_RESTORE`, now default ON, cap 0x2000; needs `ROGUESQ_DPC_WRAP_FLUSH=1` + S4271/S4272 shadow) takes ODD cimgs 60 -> 0, reproduced 3/3 runs (s4286, s4287 x2) and with pure defaults. Unmeasured: effect on the hangar fb-set growth / 0x130393 wipe (80 s route stops at title).

**Crash families (M3, parked).** The VI-640-intro crash (fillSampleStreamRange
+8136/+8292/+932 NULL or wild ptr; RT64 copyToRAM) is independent of private DMEM
and of the audio ucode (s4252/s4255/s4256: pooled ~2/13 vs ~4/21); writer
unnamed. Allocator head==0/tail!=0 (s4230) RECURRED 8/8 in s4277 and precedes the early musyx crash; s4278 named the writer: legitimate unlink at 0x8008FD94 once the node pool hits 0 (~9.5k calls, key-timing independent; `tools/apply_s4278_headwriter.py`); root = pool never replenished. Crash PCs 0x80001b08 and
the early `spTaskSchedulerThread+9632`/0x8000834c were OUR zero-extended
`MEM_x(...,0x8...u)` diagnostics (s4229, class closed); last-guest-pc is not the
fault site (use the host pc-symbol).
**REGEN WARNING (s4204):** the full `N64Recomp -> fixup_game_funcs.py` flow aborts
at the s3290 E088 anchor and a regen clobbers the live patched RecompiledFuncs.
Patch the live tree with `tools/apply_s*.py`; do not regen.

## Next steps

00. (s4339) Name the branch-state writer behind the C904/C88C divergence. The
fixed C88C-entry witness passed host/title/hangar/filter controls and emitted
256 rows, but port `branch_state` was 0 for both `s1=1/2`, while retail C904
phase-512 rows used `0x0010`/`0x3108`; source words/bytes and row order also
diverged. Run one batched writer census for the physical low field at
`s1+0x22`, with a positive-control write and phase-gated port/retail
attribution. A matching writer/value family selects stale/late-read; a
retail-only writer selects a missing publication boundary; no writer in either
arm selects wrong field mapping/probe semantics. Do not add a guard or alter
decoder/RSP/AI behavior.

00a. (s4338) Name the pre-filter stream divergence behind the C904/C88C field
mismatch. Keep the qualified in-process autopilot route, retained seeded save,
`M4_Y8000_WIDTH=512`, LLE/solo/spin-yield, real audio, and existing probes.
Add one phase-gated port witness for the C88C helper's source/branch selector
fields corresponding to retail C904 `s1`, `source_word`, `source_byte`, and
`branch_state`; compare it to the retained retail C904 rows in one run. Require
the host positive control, title VI 1024, hangar VI 512, and nonzero joined
C88C/direct rows. A matching source/branch sequence with different descriptor
words selects descriptor mapping; a diverging source/branch sequence names the
pre-filter stream. Do not use the external field-key arm or add a mitigation.

00a. (s4335) The retail C904 field dump passed the whole-RDRAM positive
control (10,000 writes), title VI 1024, and hangar VI 512 controls. C904
executed 3,107 times; the phase-gated dump produced 461 rows at origin
`0x006AB400` and 836 at `0x006AB800`. Rows consistently had caller
`0x8009C0E4`, object pointer `0x80153420`, and nonzero source/branch fields.
This selects C904 as the retail counterpart boundary for the port C88C
descriptor helper; the rows are retail-side evidence and the controls are
independent route evidence. Next: compare a bounded, same-phase port C88C
field table against the retail C904 table, including object-relative source
words and branch state. Keep decoder, RSP, AI, and game-path behavior
unchanged; do not add a mitigation.

00a. (s4311, superseded by s4312) The 4,096-row port free/read join was not interpretable: the first launch omitted the known `M4_Y8000_WIDTH=512` route qualifier, and both corrected seeded-save launches (including the `ROGUESQ_A14_YIELD=0` rollback) crashed at `fillSampleStreamRange+13572` / guest `0x8000834C` while still at VI 640. It was believable because those launches reproduced the prior crash, but s4312 replayed the qualified route and captured the full table.

00a. (s4310) The corrected seeded-save/key route reached VI 512 at 42.0 s and passed both same-run controls: the adjacent-range store control and the phase-gated synth-read control. The target block `0x8017D910` was freed by `waitForAnyAudioSlot` at guest PC `0x80095D54` before the hangar phase; the port then captured 256 target reads and 256 selected writer rows, all 0 requested-vs-post mismatches. The first port read was `0x8008FCE8: 0x17D9E0 -> 0x8017D9F8`, matching the independent retail boundary. This rules out port-only reuse before the first consumer read and selects the shared-free/equivalent-first-read boundary; later traversal/layout divergence remains open. Next: extend the bounded join past the first 256 rows or compare a keyed post-free snapshot at the first divergent read to name the later consumer divergence. No guard/skip is authorised.

00a. (s4309, superseded by s4310) The first port free/read join route was invalid: three variants reached only VI 640 or crashed before VI 512, and the wrap-shadow variant stalled at VI 640. It was believable because the s4306 control fired, but the corrected boot-relative key schedule now reaches VI 512 with both controls and target rows.

00a. (s4308) do_rom_read odd-address crash: the independent retail arm passed the whole-RDRAM read control (214,786,365 reads), reached hangar VI 512 at 38.4 s, and the target read watch captured 1,434,154 reads. The fixed oracle logger now records loaded words; the first hangar consumer row is `pc=0x8008FCE8 addr=0x17D9E0 value=0x8017D9F8`, before the retail post-free writer sequence, and later rows retain the retail-specific address/value order. This is a second independent line confirming H-retail-layout-different at the consumer boundary, not H-shared-read-layout. H-port-only-consumer remains unsupported by the paired port writer table's zero mismatches. Exact lifetime/consumer fault remains open; no guard/skip is authorised.

00a. (s4299-s4303) do_rom_read odd-address crash ROOT: stale musyx stream nodes. The 47664-byte block 0x8017D910 (stream nodes at 0x17DBE0 plus DMA sample buffers) is freed after `waitForAnyAudioSlot` and reused by level-texture/cache work while `musyxSynthFrame` keeps walking it. Name-copy and host-write refuted. The three frees are retail guest code on the natural exit path, and retail independently reaches hangar, enters the wait three times in 48 s, and accesses the block 1,141,187 times (1,072,566 reads, 68,621 writes) while `musyxSynthFrame` runs 2,820 times. This rules out both “retail skips the free” and “retail stops synth globally.” The writer histogram includes guest audio/object and cache/allocator PCs; exact post-free value/layout ordering remains open. Do not add a skip/guard until a legitimate retail/port lifetime difference is named. Single-source for exact retail counts; combined with the port-side s4301 trace this establishes shared free plus continued synth activity.

0c. (s4295) Odd control restored only on the s4290 route (PHASE_WIDTH=1024, phase-relative keys, S4268): RESTORE=0 odd=60 vs RESTORE=1 odd=0, with seeded saves, but that route never reaches 512. The s4294-style route (PHASE_WIDTH=512) reaches 512 but shows odd=0 in both arms, with or without SPIN_YIELD/Y8000. Next: isolate S4268 vs 1024-width phase gating (NEXT.md), find a route with odd>0 AND 512, then run the hangar RESTORE A/B. Hangar effect still UNMEASURED.

0b. (s4293) Title slowdown s4289-s4292 was the EMPTY per-arm saves dir (build_arm_* skip saves): seeded save 1024@13.9s #765 (= s1949 #786) and hangar 512@47.4s; empty 1024@46.8s #2751. NOT a code regression. Every probe arm must copy build/saves in (scratch/agent/s4293_save_ab.sh). Next: hangar A/B WRAP_RESTORE 1 vs 0, seeded saves, phase-gated on VI 512.

0. (s4279) Allocator head==0 / early musyx crash ROOT FOUND: the sample-stream node heap block (0x801F9CD0..0x801FB3F4, header 0x1800) is zeroed wholesale by ONE RT64 `copyToRAM` of a garbage colour image (addressStart 0x130393 unaligned, width 1033, siz 3, rows 118..339 -> range [0x1A742B,0x28633F), VI 640), within one ENTRY of the wipe in 2/2 runs; list was invariant-clean before, no guest store did it. Pool==0 is designed (free list has no push site; LRU steal) — the s4278 "pool never replenished" framing is superseded. Next: name the guest SetColorImage/DPC source of addr 0x130393 w1033 (scratch/agent/NEXT.md). Hangar route and the WRAP_FLUSH A/B stay blocked until resolved.

0a'''''. (s4286) RESTORE-FROM-SHADOW WORKS: with WRAP_FLUSH=1 + `ROGUESQ_WRAP_RESTORE=1` + `ROGUESQ_S4272_CAP=0x2000` ODD cimgs 60 -> 0 vs 60 without restore (phase-matched to VI 1024, positive control postDiff=0, wordsRestored 5814; single run/arm). Next: replicate 2x, crash soak, then default-on candidate (`scratch/agent/s4286_restore.sh`).

0a''''. (s4285) At WRAP_FLUSH time ~21% of flushes (591/2816, 564/2816, two runs) already have shadow!=live words: lap-2 overwrote lap-1 before the END<seen bump arrives, so flush cannot recover it (F2). Fix needs bump-time content fed to RT64 (restore-from-shadow arm next; shadow only covers ranges <=0x400).
0a'''. (s4284) ODD cimg commits ALL contain ring-lap dropped bumps (210/210 over two arms, vs 26% of all commits); cross-task cause refuted. WRAP_FLUSH=1 trims ODD only 5.0%->4.0% (single run). Next: why flush leaves ODD (does RT64 read at commit after flush?)

0a''. (s4283) ODD cimg = old triangle tail left in a ring slot whose head was overwritten by a newer command burst that never entered the commit's range list (CF header present at bump; H-D and H-F refuted; 0 duplicate range starts in 10 windows). Writer = the ucode on a ring lap whose bumps the within-task high-water filter drops (inferred, s4273-consistent). Next: count lap drops per commit joined to ODD events, WRAP_FLUSH 0/1 arms (scratch/agent/NEXT.md); supersedes the write-watch plan in 0a'.

0a'. (s4282) ODD cimgs (6/6 over 3 runs, control passed) are reached by contiguous walking from triangle coefficient data that follows a non-inline command (2F/E6) with no triangle header: the desync PRECEDES the cimg, so the cimg is decoded data (B refuted, C supported; single-source). Next: write-watch the dword after the last valid command to name the writer of the missing header (scratch/agent/NEXT.md).
0a. (s4280) The 0x130393 w1033 'SetColorImage' is NOT a guest command and NOT edited by our bump/commit filters (bump==commit; it is the 2nd word of intact CF-triangle coefficients at 4E2958). RT64's walk parsed different bytes at 4E27B0..4E2910 than RDRAM shows at bump or post-commit (ring: E9 at 4E2910; RDRAM: FF2E0C68). s4281: walk-entry snapshot == live RDRAM at the event (0 DIFF, 9 runs), so A is refuted; the walker's ring sits at 4E22D0..4E2308, ~0x500 before the bridge window. Next: print 16 words around g_s4271_dl and check that the previous command's advance lands on it, plus a DIFF positive control (scratch/agent/NEXT.md). About half of ODD cimgs are late-filled placeholders (R2), half are this unexplained class.

Work only the first applicable item. One monotonic sequence.

1. **Qualify `ROGUESQ_DPC_WRAP_FLUSH`** (s4273: ring laps drop ~4.8M bumps/45 s; lap-1 head is overwritten before commit-time read; flush option default OFF, ODD 12.4%->8.6% single-run, VI 640 only). s4274 ran it to 75 s: neither arm reached VI 512, no decision, flush stays OFF. s4275 re-ran with the s1949 PROBE_KEYS: arm0 died at VI 640, arm1 reached only 1024 (50.7 s); no 512, no decision (route reach is the blocker, see NEXT.md). Re-run once 512 is reached reliably; phase-gate on VI 512 + frame dumps; decide default. The other bump-time filters (cimg suppress, gate_inject, PRIM_FF) are default OFF - R1 closed. Older text: **Finish the placeholder-drop class** (s4272: bump-time PIPESYNC drop deleted
   future triangle words; ROGUESQ_DPC_KEEP_PIPE default ON cut ODD cimg 61% -> 7%).
   Audit the remaining bump-time 8-byte filters in `rsp_dpc_submit` (0xFF cimg
   suppress, fs-inject/`gate_inject`, F3/FD/F5 drop): bump-time content is a
   placeholder, so apply any filter at commit time on final content instead.
   Then qualify: hangar reach + crash soak with the fix (scratch/agent/NEXT.md).
2. **Resume M5 plan steps** (docs/M5-AUDIO-PLAN.md Step 9/10) once the stall is
   explained; measure default-arm audio task rate t=18-28 with an `=0` control.
3. **M3 pre-publication guard runtime qualification:** blocked on a host with
   `mips64-elf-gcc`/`mips64-elf-ld` and a `PatchesLib` target; no host-only work.
4. **Generated-symbol renaming sweep** (slug `generated-symbol-renaming-sweep`),
   only when 1-3 are inapplicable; mapping-only edits do not reset the
   engineering-change gate.

## Live hypotheses

| Hypothesis | Status |
|---|---|
| RT64 fb-set growth origin | RESOLVED at source (s4272): bump-time E7 drop in dpc_bridge deleted triangle words (slots are placeholders until after the DPC_END bump); fix default ON, ODD 61%->7% (cross-run, single-source); residual 7% = other bump-time filters. |
| VI-640 intro crash writer | Open; independent of private DMEM and audio ucode (silent-ucode arm crashes equally, s4252). |
| M5 producer provenance | Port hangar source span is zero because ROM-DMA data (`pi_rom_to_rdram`) is cleared by the legitimate `rs_memset` (0x800078E0/EC); producer setup/object/loop/load-use state is retail-parity (s4150-s4189). No mitigation authorised. |
| Allocator list head==0 | Single-source s4230, not reproduced (s4231/s4234); parked. |
| M3 sentinel ownership | H1 at source scope; runtime unqualified (no MIPS toolchain). |
| waitForAnyAudioSlot B39 skip flag | Retail does not avoid the frees: the aligned physical watch shows the B39-byte read at 0x00130B38, followed by all three asset-pointer reads at the free sites (s4302). |
| Retail/port post-free stream-node layout | s4306 matched an independent retail ordered table against a valid port VI-512 run: 256 port rows, 0 requested-vs-post mismatches, but different address/value/order tuples and writer mix. This selects H-retail-layout-different; exact synth consumer read/lifetime failure remains open. |
| Port synth-read/free join | s4307 captured 256 reads with a phase-gated control; s4310 additionally joined the shared free and captured 256 post-free writer rows. The first port read/value matches retail, and the free precedes it, ruling out port-only reuse before the first consumer read. Later traversal/layout divergence remains open; no mitigation is authorised. |
| Port synth-read/free join, extended route | s4312 requalified the route and captured 4,096 writer/read rows in one run; both controls fired at VI 512, the free was again at guest `0x80095D54`, and all 4,096 requested/post pairs matched. s4313 independently matched the first 4,096 retail keyed rows; comparison beyond that remains open. |
| Retail synth-read value join | s4308/s4313: whole-RDRAM and VI-512 controls passed; the value-aware oracle captured 1.43M target reads, and the first 4,096 keyed retail rows exactly match the qualified port sequence. Later divergence remains open. |
| Retail/port 16,384-row consumer comparison | s4317: whole-RDRAM control and hangar VI 512 passed; both arms supplied 16,384 rows, with an ordinal-0 tuple divergence (retail `0x8008FADC,0x17DA1C,0xB035DC20`; port `0x8008FCE8,0x17D9E0,0x8017D9F8`). This selects a retail/port layout-or-filter divergence; exact writer/consumer cause remains open. |
| M5 Step 9 complete matrix | s4322: both port arms reached title/hangar and passed route/host controls; silent audio emitted 256 filter rows at `0x8009D740`, while real-image audio emitted none despite 1,095 descriptor entries and PCM source/consumer rows. The route blocker is closed; an audio-arm path divergence is selected. |
| M5 Step 9 MORT/filter callsite | s4322: the silent arm reached `0x8009D740`; the real-image arm did not reach any enumerated filter callsite. MORT output/type/rate versus PCM remains open; do not treat the real-arm zero as a MORT null. |
| M5 Step 9 MORT output | s4322: the independent reference decoder passed four rows covering both rates with nonzero output. Runtime comparison is now route-qualified but blocked on explaining why the real-image arm has no active filter rows. |
| M5 Step 9 payload join | s4324: both arms reached `0x8009D740` for 128 calls and produced 256 call/entry rows; early payloads match but later arguments/table values diverge. Descriptor class/rate and decoded-output ownership remain open. |
| M5 Step 9 filter join instrument | s4325: built a phase-scoped route-keyed table with rate, arguments, live sp-based table value, and source/output hashes. The reference/oracle controls passed, but corrected paired rows were not jointly valid; descriptor class/rate and decoded-output ownership remain open. |
| M5 Step 9 clean filter/output join | s4326: both valid port arms emitted 128 calls at the same active site and rate, but all 17 common route-row keys differed in source and output hashes; H-output-join is rejected. Descriptor type/class is not yet recorded, so payload ownership remains open. |
| M5 Step 9 caller-object join | s4328: all controls passed and both arms emitted 256 rows, but the retained caller tuple joined zero rows; only the C88C caller bucket emitted. Descriptor class versus pre-filter route remains open; this is a probe-boundary result, not a descriptor null. |
| M5 Step 9 direct D740 witness | s4329: the direct D740 callsite emitted 256 rows per arm and its scoped counter reached 256, while no D740 caller-entry bucket or retained tuple joined. Static census s4330 found no alternate generated transfer, so this is an unresolved instrumentation/state contradiction rather than proof of entry bypass; descriptor class versus pre-filter route remains open. |
| M5 Step 9 co-located sequence witness | s4331: image-arm entry, post-helper, and D740 direct events share sequence ids inside `decodeAndFillVoiceBlock`; silent-arm target rows are absent. This rejects the entry-bypass/helper-not-invoked reading and identifies the prior D740 caller null as a probe-boundary error. Descriptor class and payload ownership remain open. |
| M5 Step 9 C88C descriptor join | s4332: both arms reached VI 512, every D740 row joined a C88C tuple, and the initial descriptor prefix matched; later descriptor pointer/word/type-class sequences diverged. This rejects H-join-boundary and stable post-descriptor selection; pre-filter route/stream selection remains open. |
| M5 Step 9 C88C source/branch fields | s4339: the fixed port witness emitted 256 rows with retail-compatible `s0`, `s1`, and branch-selector shape, but port `branch_state` was 0 on every row versus retail `0x3108`/`0x0010`; source words/bytes and order also diverged. This selects pre-filter stream/state divergence; the writer/publication boundary remains open. Single-source cross-runtime field evidence, with independent route controls. |

## Durable evidence boundary

Retail (oracle: tools/oracle/README.md, physical-address watches, whole-RDRAM
positive control) reaches title/hangar and attributes writer PCs; the port matches
it at every witnessed producer boundary. The qualified consumer comparison used
same-build declared/real, declared/silent and legacy/real arms. A route failure
invalidates a null; it never proves absence.

## Superseded conclusions
- s4329 "active D740 callsite is reached without the probed function entry"
  (believable because direct rows and `d740_store_n` reached 256 while the
  retained D740 caller tuple never joined): s4331 placed the witness in the
  actual containing generated function, `decodeAndFillVoiceBlock`, and showed
  shared entry/helper/direct sequence ids in the image arm. The D740 caller
  bucket was never the right helper boundary; this was instrumentation state,
  not evidence of an entry bypass.

- s4329 "active D740 callsite is reached without the probed function entry" (believable because direct rows and `d740_store_n` reached 256 while the retained caller tuple never joined): s4330's complete generated-reference census found only the normal `updateVoiceChannelParamsLarge` wrapper and its in-function D740 edge, with no alternate body transfer; runtime caller-row absence remains unexplained.

- s4322 "real-image filter path absent" (believable because the prior
  route-qualified run had 1,095 descriptors and PCM activity but zero filter
  rows): s4324 requalified the seeded-save route after the s4323 pre-512 crash;
  both arms reached VI 512 and produced 256 filter rows at `0x8009D740`. The
  null was run/state-dependent, not a stable eligibility or dispatch split.

- s4323 "matrix route-invalid on descriptor crash" (believable because both
  port arms crashed before VI 512): s4324 used the known seeded save and the
  same controls, reached VI 512 in both arms, and captured the complete filter
  row set. The crash remains after the target phase and is shared by both arms.

- s4319 "MORT descriptor/filter witnesses absent" (believable because the
  route controls and descriptor-start were valid): s4320 reran the matrix with
  the generated `init-desc` gate `ROGUESQ_LOG_VI_CALLERS=1`; `init-desc` then
  fired in both arms and the real filter callsite at `0x8009D740` produced
  rows. The earlier null was instrumentation configuration, not route absence.

- s4316 "full retail/port consumer comparison remains unevaluable" (believable:
  the first fixed retry stalled before VI 512 and the earlier detail cap left
  only 14,140 filtered rows); s4317 restored the Rice/`--vi-trace` route and
  raised the bounded cap, qualifying 16,384 rows and selecting a first-row
  retail/port layout-or-filter divergence.

- (s4294 hypothesis) "SPIN_YIELD/Y8000 or seeded saves suppress the ODD condition" - superseded by s4295: a0 (neither env) still odd=0; b0 (seeded saves) odd=60. It was believable because s4294 was the first run changing those variables together with the key route.

- s4280 hypothesis A "RDRAM changes between bump time and RT64's walk read" (believable: the walk saw E9 at 4E2910 while RDRAM showed FF2E0C68): s4281 snapshotted the list at walk entry and diffed it against live RDRAM at the event, 0 differing words over 9 runs (single-source, no DIFF positive control). The list is rewritten between walks, not within one.

- s4278 "root = node pool never replenished / port consumes nodes faster than retail" (believable: pool hit 0 right before head==0): pool==0 is the designed LRU-steal state; the list is clean until RT64 copyToRAM wipes the whole block (s4279).

- s4222/s4223 "port misses code that fills the source block" and every
  zero-volume/zero-payload conclusion s4164-s4221: stale-save artifact (s4224).
- s4235-s4238 AI-output statistics (clipping, 13x hot, DC ramp, identical
  buffers): host byte-order instrument artifact (s4239); ramp magnitude was the
  byte-swapped logger (s4240).
- s4259 "host message late"; s4253 "head->next / cache-recycle" and "t~28 s
  private-DMEM crash is an audio race" (s4254: VI-640 intro, chain intact); s4245
  "stale-ring / half-rate"; s4262 "tid-0 send gate" (it is task-completion
  fan-out, s4263); s4248/s4249 lock wait as the cause of the *residual* dip
  (private DMEM fixed that part; residual is host-renderer side).
- s4179 H-earlier-producer-mismatch (KSEG-only guard artifact, s4180).
- s4075 missing-store (fixup omitted witness); s4088 detail hook (s4089); s4149
  route-invalid (s4150); s3579-s3584 byte-vs-word comparison; s4226 "A12
  refuted / no hangar" (save-dependent flow and input mismatch, s4227).
- Overlay/menu-only explanation, intrinsic VI-640 flakiness, missing-input and
  wait-return explanations, global-zero image-DMA, route-wide PCM-gap, force-zero
  default policy, s327 "only decrementer" (A12 pump was a silent skip).
- s4228/s4231/s4232 early-crash PCs: our diagnostic probes (s4229).
- "Full regen flow works": broken since s4204 (see regen warning).

## Durable operating rules

Use [F5-UCODE-REFERENCE.md](F5-UCODE-REFERENCE.md), not standard F3DEX
assumptions. The qualified graphics path is LLE-only. Interpreter limits,
null-GBI guards and similar defenses are safety mechanisms, not explanations.
MusyX/MORT audio is partially stubbed; MusyX data must not reach stock `aspMain`.

Every instrument needs independent ground truth, a same-run positive control,
a phase-scoped budget and two evidence lines before its result becomes truth.
Phase-gate animated comparisons on VI transitions; batch A/B arms in one
build/run. A counter proving a branch ran is not a positive control.

Regeneration order is `make_elf.py -> N64Recomp -> fixup_game_funcs.py ->
CMake` (but see REGEN WARNING). Never hand-edit generated functions for behaviour
changes. If `lib/` changes, run `./submodule-patches/export.sh` and commit. Never
run submodule update, checkout, clean or hard reset. Kill runs with SIGKILL and
run from `build/`. A mitigation-shaped change needs an `ORIGIN:` line naming the
writer and whether its value is legitimate.

## Evidence index

[M5-AUDIO-PLAN.md](M5-AUDIO-PLAN.md),
[M5-S3801-IMAGE-STAGE-BOUNDARY.md](M5-S3801-IMAGE-STAGE-BOUNDARY.md),
[M5-S3802-SOURCE-WRITER-CENSUS.md](M5-S3802-SOURCE-WRITER-CENSUS.md),
[M5-S3824-FAMILY-ROUTE-OBJECT-JOIN.md](M5-S3824-FAMILY-ROUTE-OBJECT-JOIN.md),
[M5-CURRENT-TRUTH-ARCHIVE-s4269.md](M5-CURRENT-TRUTH-ARCHIVE-s4269.md).
Detailed counts remain in `PORTING-STATE.md`.

## s4291 note
Hangar (VI 512) unreachable on current route: title at ~52 s vs 14 s at s1949 (640->1024 idle ~48 s), either key schedule, solo or concurrent. Restore effect (odd 60 vs 0) reproduced again. Next: bisect the slowdown (drop DPC_WRAP_FLUSH / S4271+S4272+S4268 / add M4_Y8000_WIDTH=512, concurrent arms, compare [phase] 1024 time).
