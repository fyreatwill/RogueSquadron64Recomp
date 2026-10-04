# Rogue Squadron 64 Recomp — current truth

Compact operational state for [PORTING-STATE.md](../PORTING-STATE.md). Durable
background is in [PROJECT-OVERVIEW.md](PROJECT-OVERVIEW.md); audio inventory
and the incremental de-stubbing contract are in [M5-AUDIO-PLAN.md](M5-AUDIO-PLAN.md).
Updated for session 3864 (2026-10-03).

## Current state

The validated native route boots through attribution, N64 logo, intro cinematic,
star flare, Factor 5 logo, title VI 1024 (`0x00790400`), and hangar VI 512
(`0x006AB400`) using real-audio/LLE/spin-yield/autopilot controls. Hangar
geometry and color artifacts remain. `ROGUESQ_AUDIO_UCODE=0` selects the silent
`Broke` control; real audio is not production-complete.

The active M5 boundary is source payload, not rendering. Qualified retail and
port hangar-phase source spans are both zero (`FNV=0x762B22A5`). Retail's
shutdown snapshot can retain 12 nonzero bytes, but its phase-gated hangar
snapshot is 408 bytes, nonzero=0. The port descriptor `0x1798B0 -> DMEM 0xCB0`
is finally written by legitimate zero-valued `0x800078EC` fill activity.
Session 3818 joined the active generated scalar-store census: sequence 664 at
physical `0x179A44` is the final observed writer, and every matching input DMA
had zero payload. No nonzero hangar producer is established.

The generated scalar-store census, central host/RSP writer census, native
page-fault census, and nine bounded exact-offset load candidates are closed at
their measured scopes. Do not infer a zero producer from a null attribution;
target fault attribution was absent or an arm crashed before target.

The qualified S/L family writes alternate objects and I has no hangar edge. A
paired retail/port target capture found zero retail reads or writes in physical
`0x165000..0x16C000` while retail still executed S/L family PCs. The repaired
clear witness identifies `0x8008F2CC`, object `0x801797B0`, length `0x298`.

## Next steps

Work only the first applicable item. This is one monotonic backlog.

1. **M5 image task/output edge — retail candidate-span writer class remains.** Sessions
   3839–3840 qualified the port input and separate writeback-DMA edge despite
   empty ABI output fields. Session 3857 qualified the dominant retail
   `0x800078EC` writer: it had 408 hangar-phase hits into
   `0x1798B0..0x179A48`, but all 816 sampled scalar stores were zero with no
   mismatches. Treat it as zero-fill activity, not the image producer. Do not
   add a writeback guard or infer a destination from the port address. The
   remaining M5 work is to identify a legitimate nonzero retail producer or
   prove the task/output edge is absent at this scope. Session 3860 tested
   unresolved retail PCs against physical `0x141AD0..0x141AF0`; controls
   passed, but the only target-phase rows were 24 sentinel writes from
   `0x80094648`. This is not the candidate image span, so it rules out no
   image producer and does not select the construction-vs-output hypotheses.
   Session 3861 repeated the paired arm after an initial port startup crash.
   The valid retry passed whole-RDRAM/title/hangar controls and produced 287
   candidate-span writer-PC rows, but neither known stage PC
   `0x80015BC8` nor `0x8000F3A0` wrote that span, and neither had a scalar
   payload row. Port independently reached 3,031 image-DMA joins with no
   crash/abort. This selects the bounded H2 result for those known writers;
   remaining candidate-span writer PCs still need classification.
   Session 3862 ran the fresh candidate-PC arm with positive controls and a
   completed retail oracle shutdown. `0x80022BB0`, `0x80022BC8`, and
   `0x80022A04` each had zero hangar-phase writer rows and zero scalar samples,
   selecting H2 for those three PCs only. The port arm crashed before its
   `[audtask-abi]` and image-DMA controls, so it supplies no paired evidence.
   The next bounded candidates are `0x80092020`, `0x8009206C`, and
   `0x80007670`; do not promote the three zero-hit PCs into a global absence
   claim. Session 3863 fixed the prior runner's high-volume watch stream and
   completed the paired arm. Retail whole-RDRAM, title 1024, hangar 512, and
   oracle shutdown controls passed. Those three PCs had target-phase writer
   rows but no post-value scalar rows, selecting H2 for these PCs only. The
   port independently reached hangar and 3,049 image-DMA joins with no
   crash/abort markers. Session 3864 completed the next paired arm: the
   `0x800076A0`, `0x80085890`, and `0x800852D8` classes had hangar
   candidate-span rows but zero post-target samples; retail controls and
   shutdown passed, and port reached 2,892 image-DMA joins with no
   crash/abort. Continue with `0x80085564`, `0x8009785C`, and `0x8008556C`.
2. **M3 heap guard validation — blocked dependency.** Sessions 3852–3859
   and attempted to validate the existing patch's metadata-slot class. The
   `heap_other_listhead` and `heap_tail_loc` pointers must equal their fixed
   linker-published addresses before queue-link stores. ORIGIN: those globals are
   fixed metadata slots; an arbitrary aligned KSEG0 value is not legitimate.
   Session 3841 changed full-block checks in `patches/heap_guards.c` from
   base-only `kseg0_ok` to `block_ok`, requiring a complete `0x100`-byte object
   below `0x80800000`. ORIGIN: `func_8002221C` and free-list link stores publish
   block bases; the guard rejects only an impossible boundary-crossing object.
   The configured generator has no `PatchesLib` target, the MIPS compiler/LD
   are absent, and `build/Debug/N64Recomp.exe` is absent. Restore/reconfigure
   those tools, build the patch ELF and library, then run the allocator-route
   smoke. Session 3858 repeated the direct prerequisite checks: neither MIPS
   tool was on PATH, `build/Debug/N64Recomp.exe` was absent, and CMake still
   had no `PatchesLib` target (`No rule to make target PatchesLib`). This
   selects the environment block again. Session 3859 added an active-queue-head
   integrity guard: a non-null head is now required to be a complete aligned
   KSEG0 block before queue-link stores. ORIGIN: the allocator's active-queue
   head slot at `0x801163FC` is written by the queue insertion path; a malformed
   head is not legitimate. This is a code change, not runtime validation; do
   not claim allocator behavior until the patch pipeline is restored.
3. **M5 target-phase parity — closed at current scope.** s3820/s3823/s3844
   supplied independent retail and validated port target coverage and exact
   hangar zero-payload parity. Do not repeat standalone qualification or the
   retail zero-writer census unless the route/build changes.
4. **Generated-symbol renaming sweep — parked.** Resume only after M5 has no
   applicable discriminator and M3 has a toolchain or a new discriminator.
   Keep HYPOTHESIS-ID `generated-symbol-renaming-sweep`; do not use mapping
   edits to evade the engineering-change stall gate.

## Live hypothesis table

| Hypothesis | Status |
|---|---|
| `H-M5-ProducerAbsent` | Selected for measured pre-input producer classes; only legitimate zero-fill writer observed. |
| `H-M5-ClearIsExpected` | Selected: `0x8008F2CC` clears the source object before the image edge. |
| `H-M5-RetailWriterPortEdgeAbsent` | Selected at measured target phases; retail writer families have no qualified target-buffer edge. |
| `H-M5-RetailWriterFamilyOtherObject` | Selected for S/L; stores target alternate objects. |
| `H-M5-RetailWriterFamilyAbsentTargetEdge` | Selected for I; no hangar-phase family edge. |
| `H-M5-FamilyDisconnectedOutput` | Selected at s3835 scope: retail has no access to the watched alternate-object span while port emits family stores. |
| `H-M5-TargetPhaseAudioDmaAbsent` | Selected at s3829: no `rs64_m5_audio_source_dma` invocation during target phases, despite lifetime controls. |
| `H-M5-FamilyAfterImageStage` | Selected at s3832–s3834: joined family work follows image stage/route context and has no PCM source/consumer match. |
| `H-M5-TaskOutputFieldsEmptySeparateWriteback` | Selected at s3840 port scope. |
| `H-M5-RetailTaskOutputFieldParity` | Selected at s3844 for empty fields; s3846 selects shared destination role at bounded scope, exact task join remains open. |
| `H-M5-RetailTaskStageRole` | Selected at s3846: retail task and candidate image-stage region are both active in hangar with independent phase/whole-RDRAM controls. |
| `H-M5-RetailTaskPointerGeneric` | Selected at s3854: `0x80171E70` and `0x80173CB0` join both known stage PCs and multiple `s1` structures without a unique destination/length tuple. |
| `H-M5-RetailDestinationAbsentTargetPhase` | Selected at s3855: retail writes the candidate stage span in hangar, but has zero phase-gated writes to `0x1798B0..0x179A48`; lifetime output writers are outside title/hangar buckets. |
| `H-M5-800078ECZeroFill` | Selected at s3857: the dominant lifetime writer executes in hangar but all sampled writes to `0x1798B0..0x179A48` are zero; it is not a nonzero image producer. |
| `H-M5-WriterProbe141AD0NotOutputSpan` | Selected at s3860 only for the probe scope: `0x80094648` writes sentinel values to `0x141AD0..0x141AF0` in hangar; this range is not the image span, so no image-producer conclusion follows. |
| `H-M5-KnownStagePCsNotCandidateWriter` | Selected at s3861: valid retail controls passed, but `0x80015BC8` and `0x8000F3A0` had no phase-gated writes or scalar payload rows in `0x165000..0x16C000`; other candidate-span writer PCs remain open. |
| `H-M5-RemainingCandidates-22xxAbsent` | Single-source retail result at s3862: `0x80022BB0`, `0x80022BC8`, and `0x80022A04` had no qualified candidate-span rows or scalar samples; other writer PCs remain open. |
| `H-M5-RemainingCandidates-9200Absent` | Single-source retail result at s3863: `0x80092020`, `0x8009206C`, and `0x80007670` had qualified hangar candidate-span writer rows but no post-value scalar rows; they are not established as nonzero image producers. |
| `H-M5-RemainingCandidates-076AAbsent` | Single-source retail result at s3864: `0x800076A0`, `0x80085890`, and `0x800852D8` had qualified hangar candidate-span writer rows but zero post-target samples; they are not established as nonzero image producers. |
| `H-M5-TaskSubmitCallerSplit` | Single-source oracle result at s3850: `0x80019DEC` directly passes the reused task descriptor `0x80149470` to `0x80033FCC`; `0x80019D68` passes stable `0x800377C8` and is not the same route. Unique stage ownership remains open. |
| `H-M3-HeapSpanGuard` | Code landed; validation blocked by absent MIPS toolchain/configured targets. |

## Evidence ledger — recent durable boundary

- **3835:** Rice retail reached title/hangar and S/L PCs, but had zero
  reads/writes in physical `0x165000..0x16C000`; port emitted 1,280 family
  stores. Alternate output is disconnected at this scope.
- **3839:** Port task `0x80171E70`, size 1, joined the exact input DMA at matching
  generations; all payloads were zero. Matching image-DMA joins refute a missing
  downstream edge.
- **3840:** Qualified retry found empty port ABI output fields and 452/458
  separate writeback joins. First attempt crashed before target and was rejected.
- **3841–3842:** Heap block-span guard was implemented with an explicit ORIGIN;
  build validation is blocked by missing MIPS compiler, N64Recomp executable,
  and `PatchesLib` target. The single refuting experiment is a reconfigured
  patch build followed by allocator-route smoke.
- **3844:** Fixed paired retail/port capture reached both target VIs on both
  arms with positive controls and no crash/abort. Retail had 516 hangar task
  rows; port had 3,342 named rows, 11,582 stage rows, and 2,870 image-DMA
  joins. All qualified ABI output fields were zero; retail source was
  `0x80173CB0`, so destination-role equivalence remains open.
- **3846:** Paired capture passed whole-RDRAM and both target-VI controls with
  no crash/abort. Retail had 1,144 hangar type-2 task rows and writes in both
  `0x173CB0..0x173DB0` (120,550) and candidate image-stage
  `0x167000..0x16C000` (930,770). Port had 2,964 image-DMA joins. This
  selects shared destination role, but the broad retail watch does not yet
  join an individual task generation to an exact stage destination.
- **3847:** Paired capture passed whole-RDRAM, title/hangar VI controls, and
  no-crash validation. The exact target range had title writer PCs
  `0x80015BC8`/`0x8000F3A0` at 86,146/117 stores and hangar counts
  12,706/38,214; retail produced 627 title and 528 hangar type-2 task rows.
  This confirms phase-correlated writer activity but leaves the per-task
  destination/length join unresolved.
- **3848:** Paired capture passed whole-RDRAM and both target-VI controls with
  no crash/abort. `0x80015BC8` iterated object addresses around
  `0x80169xxx`; `0x8000F3A0` iterated unrelated `0x80114xxx`/`0x801e5xxx`
  structures. Neither exposed the port stage-2 destination/length tuple, so
  H2 is selected for this argument route and the callsite/task join remains
  open.
- **3849:** Paired capture passed whole-RDRAM and both target-VI controls with
  no crash/abort. Retail reached 631 title and 516 hangar VIs and produced
  1,138 type-2 task rows. The watched callsites executed 241,789 times at
  `0x80015BC4` and 87,086 times at `0x8000F39C`; their live arguments were
  object/array values, not a task pointer or the port stage tuple. This is a
  single-source oracle selection of H2 for the callsite-argument route; the
  task-submission caller join remains open.
- **3850:** Paired capture passed whole-RDRAM and both target-VI controls with
  no crash/abort. Retail reached 631 title and 691 hangar VI observations; the
  caller PCs executed 3,449 (`0x80019DEC`) and 1,706 (`0x80019D68`) times.
  The first caller preceded 1,313 task rows with `a0=0x80149470`, matching the
  dumped task descriptor; the second carried stable `a0=0x800377C8`. The
  descriptor's output fields stayed zero. This is a single-source oracle
  result: it selects the direct submission route but does not establish a
  unique stage destination.
- **3851:** Paired capture passed whole-RDRAM and both target-VI controls with no
  crash/abort. The descriptor range recorded 44,270 writes, all from the same
  ten-PC store sequence. Post-store sampling found 13 values; task input
  pointers varied between title/hangar routes, while the output/yield fields
  stayed zero. This single-source oracle result selects H3 for the descriptor
  boundary and rules out descriptor output fields as the unique stage owner.
- **3852:** Landed an M3 guard-class change in `patches/heap_guards.c`: the two
  free-list metadata slot pointers are now checked against their fixed linker
  addresses before queue-link stores. The prescribed `PatchesLib` build could
  not run because the configured build has no such target; the configured MIPS
  compiler and `build/Debug/N64Recomp.exe` are also absent. No allocator result
  is claimed.
- **3854:** Paired retail/port capture passed whole-RDRAM, title/hangar VI, and
  no-crash controls. Retail reached 631 title and 691 hangar VIs, produced
  1,313 type-2 task rows, and yielded 21 exact `pc-task-join` rows. The two
  changing task pointers (`0x80171E70`, `0x80173CB0`) appeared at both
  `0x80015BC8` and `0x8000F3A0`, with multiple `s1` structures and no unique
  destination/length tuple. Port produced 3,006 image-DMA joins with zero
  crashes/aborts. This selects `H-M5-RetailTaskPointerGeneric` and leaves the
  retail destination/writeback role open.
- **3855:** Paired capture passed whole-RDRAM, title/hangar VI, and no-crash
  controls. Retail had 408,980 writes in the candidate stage span and
  hangar-phase writers at `0x8000F3A0`/`0x80015BC8`, but zero phase-gated
  writers in `0x1798B0..0x179A48`; its 1,125 lifetime writes there came from
  non-target-phase PCs, dominated by `0x800078EC`. The retail task join still
  produced 21 rows. Port independently produced 2,866 image-DMA joins to
  `0x1798B0`, length `0x198`, with zero crashes/aborts. This selects
  `H-M5-RetailDestinationAbsentTargetPhase` and closes the destination-role
  discriminator at the qualified target scope.
- **3856:** The prescribed M3 validation prerequisites were checked directly.
  `mips64-elf-gcc` and `mips64-elf-ld` were absent, `build/Debug/N64Recomp.exe`
  was absent, CMake exposed no `PatchesLib` target, and the requested build
  failed with `No rule to make target PatchesLib`. This selects the environment
  block only; it provides no allocator behavior evidence and leaves the guard
  unvalidated.
- **3857:** A paired retail/port capture added scalar post-store provenance for
  the dominant retail writer. The oracle whole-RDRAM control reached 10,000
  callbacks, title 1024, and hangar 512; the run completed with 8,046,202
  watch hits. `0x800078EC` wrote the candidate output span 816 times, including
  408 hangar-phase hits, but scalar sampling reported zero=816, nonzero=0,
  mismatch=0. The port independently emitted target-phase image-DMA joins and
  no crash/abort markers. This selects `H-M5-800078ECZeroFill` and rules out
  that writer as the nonzero image producer at the qualified scope.
- **3858:** The prescribed M3 validation was attempted once more. `command -v`
  found neither `mips64-elf-gcc` nor `mips64-elf-ld`; the executable check for
  `build/Debug/N64Recomp.exe` failed; and
  `cmake --build build --config Debug --target PatchesLib` returned
  `No rule to make target PatchesLib`. This is direct environment evidence,
  not allocator behavior, so the metadata-slot guard remains unvalidated.

- **3859:** Audited the active-queue link idiom in `patches/heap_guards.c` and
  added a complete-block check for the non-null queue-head value before any
  queue-link store. ORIGIN: the queue head is the allocator's fixed metadata
  slot at `0x801163FC`; a malformed KSEG0 value is not legitimate. The patch
  compiler, linker, generated recompiler, and `PatchesLib` target were not
  available, so this change has no runtime validation result.

- **3860:** Ran `scratch/agent/run_s2297_m5_target_only_writer_sequence.sh`.
  The independent whole-RDRAM control reached 10,000 callbacks; title VI
  1024 and hangar VI 512 were both observed; the oracle completed 4,104,942
  watch hits. In the phase-gated watch of physical `0x141AD0..0x141AF0`,
  `0x80094648` produced 24 target-phase writes, all sentinel `0x7F7F7F7F`;
  `0x8008EB8C` and `0x8008EBBC` produced no target rows. The range is not the
  candidate image span, so this is a valid coverage/instrument result but not
  a retail image-writer attribution. It rules out only `0x80094648` as a
  non-sentinel writer of that probe range during hangar.

- **3861:** Ran the paired candidate-span scalar harness twice because the
  first attempt crashed the port before either target VI. The retry passed
  the oracle positive control, title 1024, hangar 512, and no-crash controls;
  retail produced 287 phase-gated writer-PC rows in physical
  `0x165000..0x16C000`, but neither `0x80015BC8` nor `0x8000F3A0` appeared,
  and neither had a post-store scalar row. The port independently reached
  3,031 target image-DMA joins with zero crash/abort markers. This selects
  `H-M5-KnownStagePCsNotCandidate` only for those two PCs and leaves the
  remaining candidate-span writer classes open.

- **3862:** The fixed retry passed the retail whole-RDRAM positive control,
  title 1024, hangar 512, and oracle shutdown (`38,218,741` hits; 4,220 VI).
  The three selected remaining PCs `0x80022BB0`, `0x80022BC8`, and
  `0x80022A04` produced zero phase-gated candidate-span writer rows and zero
  scalar samples. The port arm crashed before audio/image controls, so this
  is single-source retail evidence selecting H2 only for those PCs.

- **3863:** The first runner was invalidated after its high-volume watch stream
  left the wrapper incomplete. The fixed runner removed that stream while
  retaining the phase histograms and scalar probes. Retail completed with the
  whole-RDRAM positive control, title 1024, hangar 512, and oracle shutdown;
  the three selected PCs had hangar writer rows (`0x80092020` 6097,
  `0x8009206C` 6098, `0x80007670` 1437) and no post-value scalar rows. The
  paired port reached hangar and produced 3,049 image-DMA joins with no
  crash/abort markers. This selects H2 only for the three PCs and leaves the
  remaining writer classes open.

- **3864:** The paired runner passed the retail whole-RDRAM positive control,
  title 1024, hangar 512, and oracle shutdown. The tested PCs had qualified
  hangar candidate-span writer rows (`0x800076A0` 1,665, `0x80085890` 252,
  `0x800852D8` 154), but each had zero post-target samples. The port reached
  2,892 image-DMA joins with zero crash/abort markers. This selects H2 only
  for those three PCs and leaves the remaining writer classes open.

Earlier s3730–s3838 evidence is preserved in the append-only ledger and linked
session notes. Do not repeat a boundary whose discriminator is closed.

## Superseded conclusions

The original overlay/menu-only explanation, intrinsic VI-640 flakiness,
missing-input and wait-return explanations, global-zero image-DMA theory,
route-wide PCM-gap theory, and force-zero default policy are superseded at
their measured scopes. They were believable before qualified routes,
same-build controls, or independent retail attribution existed.

The s3579–s3584 retail-versus-port stored-value inference at `0x800078EC` is
unsupported because retail executed a byte store while the oracle read an
aligned word containing neighboring bytes. Request-only SP-yield conclusions
are limited to the old diagnostic arm. The old cinematic-pool/audio-slot
interpretation was superseded by the MusyX voice-table measurement.

## Durable operating rules

Use [F5-UCODE-REFERENCE.md](F5-UCODE-REFERENCE.md), not standard F3DEX
assumptions. The qualified graphics path is LLE-only. Interpreter limits,
null-GBI guards, and similar defenses are safety mechanisms, not explanations.
Overlay dispatch is sufficient for the validated route.

MusyX/MORT audio remains partially stubbed. MusyX task data cannot be sent to
stock `aspMain`; the silent arm returns `Broke`. Never infer audio behavior
from a route that fails to reach the target phase.

Every instrument needs independent ground truth, a same-run positive control,
a phase-scoped budget, and two evidence lines before its result becomes truth.
Phase-gate animated comparisons on VI transitions. Batch A/B arms in one
build/run. A counter proving a branch ran is not a positive control.

Regeneration order is `make_elf.py -> N64Recomp -> fixup_game_funcs.py -> CMake`.
Never hand-edit generated functions for behavior changes. If `lib/` changes,
run `./submodule-patches/export.sh` and commit refreshed patches. Never run
submodule update, checkout, clean, or hard reset commands. Kill runs with
SIGKILL and run from `build/`. A mitigation-shaped change needs an `ORIGIN:`
line naming the writer and stating whether its value is legitimate.

## Evidence index

See the session-specific notes and:

- [M5-AUDIO-PLAN.md](M5-AUDIO-PLAN.md)
- [M5-S3801-IMAGE-STAGE-BOUNDARY.md](M5-S3801-IMAGE-STAGE-BOUNDARY.md)
- [M5-S3802-SOURCE-WRITER-CENSUS.md](M5-S3802-SOURCE-WRITER-CENSUS.md)
- [M5-S3824-FAMILY-ROUTE-OBJECT-JOIN.md](M5-S3824-FAMILY-ROUTE-OBJECT-JOIN.md)

Sessions 1–3844 remain in the append-only ledger. Use bounded `grep`/`sed`
windows for `PORTING-STATE.md`, never read it whole.
