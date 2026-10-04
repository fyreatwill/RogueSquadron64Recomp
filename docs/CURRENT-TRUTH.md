# Rogue Squadron 64 Recomp — current truth

Compact operational state for [PORTING-STATE.md](../PORTING-STATE.md). Durable
background is in [PROJECT-OVERVIEW.md](PROJECT-OVERVIEW.md); audio inventory
and the incremental de-stubbing contract are in [M5-AUDIO-PLAN.md](M5-AUDIO-PLAN.md).
Updated for session 3890 (2026-10-03).

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

1. **M3 heap guard validation — active-queue reciprocal-link guard.** Session
   3890 landed the guard in `patches/heap_guards.c`, but the configured
   `PatchesLib` target and MIPS/N64Recomp tools are unavailable. Restore the
   patch pipeline and run the allocator smoke; do not add another guard until
   this validation is possible. A guard fire must identify the malformed
   reciprocal link and is not, by itself, proof of a retail corruption source.
2. **M5 image task/output edge — retail candidate-span writer class remains.** Sessions
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
   Session 3865 completed the retry after an initial port startup crash.
   Retail controls and shutdown passed; `0x80085564`, `0x8009785C`, and
   `0x8008556C` each had qualified hangar candidate-span writer rows but zero
   post-target scalar samples. The port reached 2,858 image-DMA joins with
   no crash/abort. Continue with `0x800331D4`, `0x80033414`, and
   `0x8003326C` as the next representative writer classes. Session 3867
   confirmed the M3 validation prerequisites are still unavailable, so this
   M5 discriminator is the next runnable unit. Session 3868 passed the
   whole-RDRAM, title, hangar, and oracle-shutdown controls. All three PCs had
   qualified title/hangar candidate-span writer rows but zero post-target
   scalar rows: `0x8003326C` 1210/1027, `0x800331D4` 8244/3537, and
   `0x80033414` 5291/2384. The port independently reached 3,009 image-DMA
   joins with zero crash/abort markers. This selects H2 for these three PCs
   only; continue with `0x80029E8C`, `0x80035124`, and `0x80004520`.
   Session 3869 passed the whole-RDRAM, title, hangar, and oracle-shutdown
   controls. None of those three PCs produced a qualified candidate-span
   writer row or post-value scalar sample. The port independently reached
   2,720 image-DMA joins with zero crash/abort markers. This selects H3 for
   these PCs only. Session 3870 selected H2 for `0x80084E48`, `0x8008509C`,
   and `0x800852E0` after qualified writer rows but zero post-target scalar
   samples; port reached 3,057 image-DMA joins. Session 3871 found no
   candidate-span writer rows or post-target samples for `0x80084C0C`,
   `0x80084D58`, and `0x80084FAC`; the port reached 2,611 image-DMA joins.
   The next representative writer classes are `0x80085898`, `0x8008589C`,
   and `0x80066450`. Session 3872 passed the whole-RDRAM, title, hangar, and
   oracle-shutdown controls. `0x80085898` and `0x8008589C` had qualified
   title/hangar candidate-span writer rows (105/233 each) but zero post-target
   scalar samples; `0x80066450` had one hangar writer row and zero post-target
   samples. The port reached 3,024 image-DMA joins with zero crash/abort
   markers. This selects H2 for these three PCs only. Continue with the next
   measured candidate-span writer class, `0x80001AD0`, `0x80001AD8`, and
   `0x80001AE0`. Session 3874 passed the retail whole-RDRAM, title-1024,
   hangar-512, and shutdown controls. All three PCs had qualified title and
   hangar candidate-span writer rows (1680/358 each) but zero post-target
   scalar samples, selecting H2 for these PCs only. The paired port arm
   stalled before its target-VI/image-DMA controls in this run, so this is
   single-source retail evidence; do not promote it to a global producer
   absence. Session 3875 completed the paired arm: retail controls passed,
   and the port reached target phases and 2,071 image-DMA joins with no
   crash/abort. All three PCs had qualified title/hangar candidate-span
   writer rows (`0x80001AE8` 1680/358, `0x80001AF4` 1680/358,
   `0x80001B78` 1677/338) but zero post-target samples, selecting H2 for
   these PCs only. Session 3877 repeated the paired arm after the first port
   attempt crashed before controls. Retail controls passed on both attempts;
   all three PCs had qualified title/hangar candidate-span writer rows
   (23/74, then 31/72) but zero post-target scalar samples. This is
   repeatable single-source H2 evidence for these PCs only. The port crashed
   before ABI/image-DMA controls on both attempts at
   `spTaskSchedulerThread+9556`, guest PC `0x8000834C`, so no paired port
   conclusion is claimed. Session 3878 completed the paired arm for
   `0x80003A48`, `0x80003A50`, and `0x80003AFC`: retail controls passed, each
   PC had qualified title/hangar candidate-span rows, and all three had zero
   post-target scalar samples; port reached 2,857 image-DMA joins with no
   crash/abort. This selects H2 for these PCs only. Continue with
   `0x80003B98`, `0x800044C8`, and `0x80004AB0`.
   Session 3879 passed the paired controls and selected H2 for those three PCs;
   continue with `0x80004BE8`, `0x80004E74`, and `0x80004E8C`.
   Session 3882 passed the retail whole-RDRAM positive control, title VI 1024,
   hangar VI 512, and oracle shutdown. Each of `0x80004BE8`, `0x80004E74`,
   and `0x80004E8C` produced qualified title/hangar candidate-span writer rows
   but zero post-target scalar samples, selecting H2 for these PCs only. The
   paired port reached 3,073 image-DMA joins with zero crash/abort markers.
   Session 3883 completed the corrected paired capture: retail controls passed
   and all three PCs had qualified title/hangar candidate-span writer rows
   (14/38 each) but zero post-target scalar samples, selecting H2 for these PCs
   only. The port crashed before ABI/image-DMA controls at
   `spTaskSchedulerThread+9556`, so no paired port conclusion is claimed. The
   next measured representatives are `0x80066474`, `0x80097524`, and
   `0x8009752C`.
   Session 3884 passed whole-RDRAM, title 1024, hangar 512, and shutdown
   controls. Each of `0x80066474`, `0x80097524`, and `0x8009752C` produced one
   qualified hangar candidate-span writer row and zero post-target scalar
   samples, selecting H2 for these PCs only. The port reached 2,085
   image-DMA joins with zero crash/abort markers. Continue with
   `0x80097534`, `0x8009753C`, and `0x80097540`.
   Session 3885 passed whole-RDRAM, title 1024, hangar 512, and shutdown
   controls. None of `0x80097534`, `0x8009753C`, or `0x80097540` produced a
   qualified candidate-span writer row or post-target scalar sample, selecting
   H3 for these PCs only. The port reached 2,854 image-DMA joins with no
   crash/abort markers. Continue with `0x80097544`, `0x80097548`, and
   `0x8009754C`.
   Session 3886 passed the same retail controls. Each of
   `0x80097544`, `0x80097548`, and `0x8009754C` produced one qualified
   hangar candidate-span writer row but zero post-target scalar samples or
   rows, selecting H2 for these PCs only. The port reached 2,996 image-DMA
   joins and 3,000 ABI events with no crash or abort markers. Continue with
   the next unclassified candidate representatives `0x80097554`,
   `0x80055780`, and `0x8005578C`.
   Session 3887 passed the whole-RDRAM, title 1024, hangar 512, and oracle
   shutdown controls. `0x80097554` had one qualified hangar candidate-span
   writer row but zero post-target scalar samples or rows, selecting H2 for
   that PC only. `0x80055780` and `0x8005578C` had no qualified candidate-span
   writer rows or post-target samples, selecting H3 for those PCs only. The
   port reached 3,034 image-DMA joins and 3,038 ABI events with zero crash or
   abort markers. Continue with `0x8006EFAC`, `0x80006C2C`, and `0x80006C34`.

   Session 3889 passed the whole-RDRAM, title 1024, hangar 512, and oracle
   shutdown controls. `0x80003A48`, `0x80003A50`, and `0x80003AFC` each had
   qualified title/hangar candidate-span writer rows, but zero post-target
   scalar samples or rows, selecting H2 for these PCs only. The port crashed
   at `spTaskSchedulerThread+9556` with guest PC `0x8000834C` before its ABI
   and image-DMA controls, so no paired port conclusion is claimed. Continue
   with `0x80003B98`, `0x800044C8`, and `0x80004AB0`.

   ORIGIN: independent retail phase-gated writer-PC and post-target attribution,
   paired with port image-DMA joins; no guest or host state was rewritten,
   skipped, or guarded.
3. **M3 heap guard validation — active guard class, validation blocked.** Session
   3866 audited the free-list reciprocal-link idiom in `patches/heap_guards.c`;
   session 3873 extended the guard to validate the head's `next->prev` back-link
   before the dequeue dereference. ORIGIN: `func_8002221C` and allocator link
   stores publish both directions; a mismatched reciprocal link is not
   legitimate allocator state. Validation remains blocked because
   `mips64-elf-gcc`, `mips64-elf-ld`, `build/Debug/N64Recomp.exe`, and the
   configured `PatchesLib` target are absent. The prescribed build returned
   `No rule to make target PatchesLib`. No runtime allocator result is claimed;
   restore the patch pipeline before validation. Session 3880 added an alias
   guard before active-queue link stores: the popped free-list block must not
   equal the queue sentinel, active head, or current queue node. Session 3881
   repeated the prescribed build and directly checked all required tools; the
   target still returns `No rule to make target PatchesLib`, while the MIPS
   compiler, linker, and generated recompiler executable are absent. No
   runtime validation is claimed. Session 3890 added an active-queue
   reciprocal-link guard before the `q->next`/`popped->prev` publication: the
   queue head must have a null predecessor, and a non-head current node must
   be pointed to by its predecessor. The prescribed build still fails with
   `No rule to make target PatchesLib`; `build/Debug/N64Recomp.exe` is absent.
   This is a source-level ownership invariant only; no allocator runtime
   result is claimed. Restore the patch pipeline and run the allocator smoke
   before adding another guard.

   ORIGIN: the active-queue insertion path publishes reciprocal `next` and
   `prev` links; a mismatched predecessor is not legitimate queue state.
4. **M3 heap guard validation — prior metadata/queue guards.** Sessions 3852–3859
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
5. **M5 target-phase parity — closed at current scope.** s3820/s3823/s3844
   supplied independent retail and validated port target coverage and exact
   hangar zero-payload parity. Do not repeat standalone qualification or the
   retail zero-writer census unless the route/build changes.
6. **Generated-symbol renaming sweep — parked.** Resume only after M5 has no
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
| `H-M5-RemainingCandidates-8556Absent` | Single-source retail result at s3865: `0x80085564`, `0x8009785C`, and `0x8008556C` had qualified hangar candidate-span writer rows but zero post-target samples; they are not established as nonzero image producers. |
| `H-M5-RemainingCandidates-29e8Absent` | Single-source retail result at s3869: `0x80029E8C`, `0x80035124`, and `0x80004520` had no qualified candidate-span writer rows or post-value samples after positive controls; they do not own the measured target edge. |
| `H-M5-RemainingCandidates-84e8Absent` | Single-source retail result at s3870: `0x80084E48`, `0x8008509C`, and `0x800852E0` had qualified title/hangar candidate-span writer rows but zero post-target scalar samples; they are not established as nonzero image producers. |
| `H-M5-RemainingCandidates-84cAbsent` | Single-source retail result at s3871: `0x80084C0C`, `0x80084D58`, and `0x80084FAC` had no qualified candidate-span writer rows or post-target samples after positive controls; they do not own the measured target edge. |
| `H-M5-RemainingCandidates-8589Absent` | Single-source retail result at s3872: `0x80085898` and `0x8008589C` had qualified title/hangar candidate-span writer rows but zero post-target scalar samples; `0x80066450` had one hangar writer row and zero post-target samples. They are not established as nonzero image producers. |
| `H-M5-RemainingCandidates-01adAbsent` | Single-source retail result at s3874: `0x80001AD0`, `0x80001AD8`, and `0x80001AE0` had qualified title/hangar candidate-span writer rows but zero post-target scalar samples. They are not established as nonzero image producers; the paired port arm did not reach target controls. |
| `H-M5-RemainingCandidates-01aeAbsent` | Paired result at s3875: `0x80001AE8`, `0x80001AF4`, and `0x80001B78` had qualified title/hangar candidate-span writer rows but zero post-target samples; port target/image-DMA controls passed with no crash/abort. They are not established as nonzero image producers. |
| `H-M5-RemainingCandidates-01b7-3a18Absent` | Paired result at s3876: `0x80003A10` and `0x80003A18` had qualified title/hangar candidate-span rows (31/77 each), while `0x80001B7C` had qualified title rows (1660) but no hangar row; all three had zero post-target samples. H2 is selected for these PCs only; they are not established as nonzero image producers. |
| `H-M5-RemainingCandidates-3a3cAbsent` | Repeatable single-source retail result at s3877: `0x80003A3C`, `0x80003A40`, and `0x80003A44` had qualified title/hangar candidate-span rows but zero post-target scalar samples. H2 is selected for these PCs only; the paired port arm crashed before controls, so no port conclusion is claimed. |
| `H-M5-RemainingCandidates-3a48Absent` | Paired result at s3878: `0x80003A48`, `0x80003A50`, and `0x80003AFC` had qualified title/hangar candidate-span rows but zero post-target scalar samples; port reached 2,857 image-DMA joins with no crash/abort. H2 is selected for these PCs only. |
| `H-M5-RemainingCandidates-3b98-4ab0Absent` | Paired result at s3879: `0x80003B98`, `0x800044C8`, and `0x80004AB0` had qualified title/hangar candidate-span writer rows but zero post-target scalar samples; port reached 2,986 image-DMA joins with no crash/abort. H2 is selected for these PCs only. |
| `H-M5-RemainingCandidates-4be8-4e8cAbsent` | Paired result at s3882: `0x80004BE8`, `0x80004E74`, and `0x80004E8C` had qualified title/hangar candidate-span writer rows but zero post-target scalar samples; port reached 3,073 image-DMA joins with zero crash/abort markers. H2 is selected for these PCs only. |
| `H-M5-RemainingCandidates-4e90-4f2cAbsent` | Retail result at s3883: `0x80004E90`, `0x80004E94`, and `0x80004F2C` had qualified title/hangar candidate-span writer rows (14/38 each) but zero post-target scalar samples; H2 is selected for these PCs only. The port crashed before ABI/image-DMA controls, so no paired port conclusion is claimed. |
| `H-M5-RemainingCandidates-6647-9752Absent` | Paired result at s3884: `0x80066474`, `0x80097524`, and `0x8009752C` each had one qualified hangar candidate-span writer row but zero post-target scalar samples; H2 is selected for these PCs only. The port reached 2,085 image-DMA joins with zero crash/abort markers. |
| `H-M5-RemainingCandidates-9753Absent` | Paired result at s3885: `0x80097534`, `0x8009753C`, and `0x80097540` had no qualified candidate-span writer rows or post-target scalar samples after positive controls; H3 is selected for these PCs only. The port reached 2,854 image-DMA joins with no crash/abort markers. |
| `H-M5-RemainingCandidates-9754Absent` | Paired result at s3886: `0x80097544`, `0x80097548`, and `0x8009754C` each had one qualified hangar candidate-span writer row but zero post-target scalar samples or rows after positive controls; H2 is selected for these PCs only. The port reached 2,996 image-DMA joins and 3,000 ABI events with no crash/abort markers. |
| `H-M5-RemainingCandidates-9755-5578` | Paired result at s3887: `0x80097554` had one qualified hangar candidate-span writer row but zero post-target scalar samples or rows, selecting H2 for that PC; `0x80055780` and `0x8005578C` had no qualified candidate-span rows or post-target samples, selecting H3 for those PCs. The port reached 3,034 image-DMA joins and 3,038 ABI events with no crash or abort markers. |
| `H-M5-TaskSubmitCallerSplit` | Single-source oracle result at s3850: `0x80019DEC` directly passes the reused task descriptor `0x80149470` to `0x80033FCC`; `0x80019D68` passes stable `0x800377C8` and is not the same route. Unique stage ownership remains open. |
| `H-M3-HeapSpanGuard` | Code landed; validation blocked by absent MIPS toolchain/configured targets. |
| `H-M3-FreeListReciprocalLinks` | Code landed in s3866; validation blocked by absent MIPS toolchain/configured targets. |

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

- **3865:** The first paired attempt was invalid because the port crashed
  during startup before its phase controls; it was SIGKILLed with the orphaned
  retail arm and supplied no paired result. The fixed retry passed the retail
  whole-RDRAM positive control, title 1024, hangar 512, and oracle shutdown.
  `0x80085564`, `0x8009785C`, and `0x8008556C` each had qualified hangar
  candidate-span writer rows, but zero post-target scalar samples. The port
  independently reached 2,858 image-DMA joins with zero crash/abort markers.
  This selects H2 for these three PCs only and leaves the remaining writer
  classes open.

- **3866:** Audited the free-list reciprocal-link idiom in
  `patches/heap_guards.c`. Traversed `next` links now require
  `next->prev == current`, and the published free-list head now requires a
  null predecessor before dereference. ORIGIN: `func_8002221C` and allocator
  link stores publish these fields; malformed reciprocal links are not
  legitimate allocator state. The direct prerequisite check found no MIPS
  compiler or linker, no `build/Debug/N64Recomp.exe`, and no configured
  `PatchesLib` target; the requested build returned `No rule to make target
  PatchesLib`. This is a code change with validation blocked, not allocator
  behavior evidence.

- **3867:** Rechecked the prescribed M3 validation prerequisites before any
  build or smoke. `mips64-elf-gcc`, `mips64-elf-ld`, and
  `build/Debug/N64Recomp.exe` were absent; the configured target inventory
  contained `RogueSquadron64Recomp` but no `PatchesLib`; and
  `cmake --build build --config Debug --target PatchesLib` exited 2 with
  `No rule to make target PatchesLib`. This selects H3 for the validation
  discriminator only. It provides no allocator behavior evidence, so the next
  runnable unit returns to the ranked M5 candidate-writer arm.

- **3869:** Paired the retail oracle and port arm for candidate PCs
  `0x80029E8C`, `0x80035124`, and `0x80004520`. Retail whole-RDRAM, title
  1024, hangar 512, and shutdown controls all passed; none of the three PCs
  appeared in the phase-gated candidate-span writer census or post-value
  samples. Port reached 2,720 image-DMA joins with zero crash/abort markers.
  This selects H3 for these three PCs only. The next bounded representatives
  are `0x80084E48`, `0x8008509C`, and `0x800852E0`.

  ORIGIN: diagnostic-only phase-gated writer and scalar-store attribution; no
  guest or host state was rewritten, skipped, or guarded.

- **3870:** Paired the retail oracle and port arm for candidate PCs
  `0x80084E48`, `0x8008509C`, and `0x800852E0`. Retail whole-RDRAM, title
  1024, hangar 512, and shutdown controls all passed. Each PC had qualified
  phase-gated candidate-span writer rows in title and hangar, but none had a
  post-target scalar sample. The port reached 3,057 image-DMA joins with zero
  crash/abort markers. This selects H2 for these PCs only: they write the
  watched span but are not established as legitimate nonzero image producers.
  The next bounded representatives are `0x80084C0C`, `0x80084D58`, and
  `0x80084FAC`.

  ORIGIN: diagnostic-only phase-gated writer and scalar-store attribution; no
  guest or host state was rewritten, skipped, or guarded.

- **3871:** Paired the retail oracle and port arm for candidate PCs
  `0x80084C0C`, `0x80084D58`, and `0x80084FAC`. Retail whole-RDRAM, title
  1024, hangar 512, and shutdown controls all passed. None of the three PCs
  produced a phase-gated candidate-span writer row or post-target scalar
  sample, selecting H3 for these PCs only. The port reached 2,611 image-DMA
  joins with zero crash/abort markers. The next bounded representatives are
  `0x80085898`, `0x8008589C`, and `0x80066450`.

  ORIGIN: diagnostic-only phase-gated writer and scalar-store attribution; no
  guest or host state was rewritten, skipped, or guarded.

- **3872:** Paired the retail oracle and port arm for candidate PCs
  `0x80085898`, `0x8008589C`, and `0x80066450`. Retail whole-RDRAM, title
  1024, hangar 512, and shutdown controls all passed. The first two PCs had
  qualified title/hangar candidate-span writer rows at 105/233 each and the
  third had one hangar row; all three had zero post-target scalar samples.
  The port reached 3,024 image-DMA joins with zero crash/abort markers. This
  selects H2 for these PCs only; the next bounded representatives are
  `0x80001AD0`, `0x80001AD8`, and `0x80001AE0`.

  ORIGIN: diagnostic-only phase-gated writer and scalar-store attribution; no
  guest or host state was rewritten, skipped, or guarded.

- **3874:** The retail oracle passed the whole-RDRAM positive control, title
  1024, hangar 512, and clean shutdown. PCs `0x80001AD0`, `0x80001AD8`, and
  `0x80001AE0` each had qualified candidate-span writer rows in title/hangar
  (1680/358) but zero post-target scalar samples, selecting H2 for these PCs
  only. The port arm reached neither target-VI nor image-DMA controls before
  the watchdog, so no paired port conclusion is claimed. The next measured
  representatives are `0x80001AE8`, `0x80001AF4`, and `0x80001B78`.

  ORIGIN: independent retail phase-gated writer-PC and post-store scalar
  attribution; no guest or host state was rewritten, skipped, or guarded.

- **3873:** Landed the next M3 reciprocal-link guard in `patches/heap_guards.c`.
  Before dequeueing a valid free-list head, the patch now requires either a
  null successor or a complete valid successor whose `prev` points back to the
  head. The source-level discriminator is the reciprocal-link predicate; the
  MIPS patch build and allocator smoke remain unrun because the toolchain and
  `PatchesLib` target are absent. No runtime allocator result is claimed.

  ORIGIN: `func_8002221C` and the free-list link stores publish the successor
  and reciprocal predecessor; a mismatched pair is malformed allocator state,
  not a legitimate value.

- **3875:** The paired retail/port arm passed its positive controls. Retail
  reached title 1024, hangar 512, and clean shutdown; port reached 174 phase
  observations, 2,076 ABI rows, and 2,071 image-DMA joins with zero
  crash/abort markers. PCs `0x80001AE8`, `0x80001AF4`, and `0x80001B78`
  each wrote the candidate span in title/hangar, at 1680/358, 1680/358,
  and 1677/338 rows respectively, while each had zero post-target samples.
  H2 is selected for these three PCs only; the remaining writer classes stay
  open.

  ORIGIN: independent retail phase-gated writer-PC and post-target
  attribution, paired with the port's image-DMA joins; no guest or host state
  was rewritten, skipped, or guarded.

- **3876:** The paired retail/port arm passed whole-RDRAM, title 1024, hangar
  512, and oracle-shutdown controls; port reached 2,864 image-DMA joins with
  zero crash/abort markers. `0x80003A10` and `0x80003A18` had qualified
  candidate-span writer rows in title/hangar (31/77 each). `0x80001B7C` had
  qualified title rows (1660) but no hangar row. All three had zero post-target
  scalar samples, selecting H2 for these PCs only. The next representatives
  are `0x80003A3C`, `0x80003A40`, and `0x80003A44`.

  ORIGIN: independent retail phase-gated writer-PC and post-target
  attribution, paired with the port's image-DMA joins; no guest or host state
  was rewritten, skipped, or guarded.

- **3877:** Two attempts passed the retail whole-RDRAM, title 1024, hangar
  512, and shutdown controls. The selected PCs `0x80003A3C`, `0x80003A40`,
  and `0x80003A44` each had qualified title/hangar candidate-span rows but
  zero post-target scalar samples, selecting H2 for these PCs only. The port
  crashed before ABI/image-DMA controls on both attempts at
  `spTaskSchedulerThread+9556` / guest PC `0x8000834C`; no paired conclusion
  is claimed. The next representatives are `0x80003A48`, `0x80003A50`, and
  `0x80003AFC`.

  ORIGIN: independent retail phase-gated writer-PC and post-target
  attribution; no guest or host state was rewritten, skipped, or guarded.

- **3878:** The paired retail/port arm passed the positive controls. Retail
  reached title 1024, hangar 512, and shutdown; `0x80003A48`, `0x80003A50`,
  and `0x80003AFC` each had qualified title/hangar candidate-span writer rows
  but zero post-target scalar samples. Port reached 2,857 image-DMA joins
  with zero crash/abort markers. H2 is selected for these PCs only. The next
  representatives are `0x80003B98`, `0x800044C8`, and `0x80004AB0`.

  ORIGIN: independent retail phase-gated writer-PC and post-target
  attribution, paired with the port's image-DMA joins; no guest or host state
  was rewritten, skipped, or guarded.

- **3879:** The paired retail/port arm passed whole-RDRAM, title 1024, hangar
  512, and shutdown controls; port reached 2,986 image-DMA joins with zero
  crash/abort markers. `0x80003B98`, `0x800044C8`, and `0x80004AB0` each had
  qualified title/hangar candidate-span writer rows but zero post-target scalar
  samples, selecting H2 for these PCs only. The next representatives are
  `0x80004BE8`, `0x80004E74`, and `0x80004E8C`.

  ORIGIN: independent retail phase-gated writer-PC and post-target attribution,
  paired with the port's image-DMA joins; no guest or host state was rewritten,
  skipped, or guarded.

- **3880:** Added an M3 guard in `patches/heap_guards.c` before active-queue
  link stores. It rejects a popped free-list block that aliases the queue
  sentinel, active head, or current queue node; this is a code-level ownership
  invariant, not runtime evidence. The prescribed `PatchesLib` build failed
  immediately with `No rule to make target PatchesLib`, so the guard was not
  runtime-validated.

  ORIGIN: free-list dequeue and active-queue link stores publish ownership;
  a block cannot legitimately remain free while already active.

- **3881:** Repeated the configured M3 validation build. CMake failed
  immediately with `No rule to make target PatchesLib`; direct checks also
  found no `mips64-elf-gcc`, `mips64-elf-ld`, or `build/Debug/N64Recomp.exe`.
  This confirms the environment block only. The alias guard has no allocator
  smoke or runtime validation result.

  ORIGIN: build-system/toolchain prerequisite check; no guest or host state
  was rewritten, skipped, or guarded.

- **3883:** The corrected paired candidate-span arm passed retail whole-RDRAM,
  title 1024, hangar 512, and shutdown controls. `0x80004E90`, `0x80004E94`,
  and `0x80004F2C` each produced qualified candidate-span writer rows at 14/38
  title/hangar, while post-target scalar attribution recorded zero samples for
  each. H2 is selected for these PCs only; H1 is ruled out at this scope. The
  port crashed before ABI/image-DMA controls at `spTaskSchedulerThread+9556` /
  guest PC `0x8000834C`, so no paired port conclusion is claimed. The next
  representatives are `0x80066474`, `0x80097524`, and `0x8009752C`.

  ORIGIN: independent retail phase-gated writer-PC and post-target attribution;
  no guest or host state was rewritten, skipped, or guarded.

- **3884:** The paired candidate-span arm passed whole-RDRAM, title 1024,
  hangar 512, and shutdown controls. `0x80066474`, `0x80097524`, and
  `0x8009752C` each produced one qualified hangar candidate-span writer row but
  zero post-target scalar samples, selecting H2 for these PCs only. The port
  reached 2,085 image-DMA joins with zero crash or abort markers. The next
  representatives are `0x80097534`, `0x8009753C`, and `0x80097540`.

  ORIGIN: independent retail phase-gated writer-PC and post-target attribution,
  paired with port image-DMA joins; no guest or host state was rewritten,
  skipped, or guarded.

- **3888:** The paired candidate-span arm passed whole-RDRAM, title 1024,
  hangar 512, and oracle-shutdown controls. `0x8006EFAC`, `0x80006C2C`, and
  `0x80006C34` had no qualified candidate-span writer rows or post-target
  scalar samples, selecting H3 for these PCs only. The port reached 2,999 ABI
  events and 2,992 image-DMA joins with zero crash or abort markers. The next
  representatives are `0x80003A48`, `0x80003A50`, and `0x80003AFC`.

  ORIGIN: independent retail phase-gated writer-PC and post-target attribution,
  paired with port image-DMA joins; no guest or host state was rewritten,
  skipped, or guarded.

- **3885:** The paired candidate-span arm passed whole-RDRAM, title 1024,
  hangar 512, and shutdown controls. `0x80097534`, `0x8009753C`, and
  `0x80097540` had no qualified candidate-span writer rows or post-target
  scalar samples, selecting H3 for these PCs only. The port reached 2,854
  image-DMA joins with no crash or abort markers. The next representatives are
  `0x80097544`, `0x80097548`, and `0x8009754C`.

  ORIGIN: independent retail phase-gated writer-PC and post-target attribution,
  paired with port image-DMA joins; no guest or host state was rewritten,
  skipped, or guarded.

- **3886:** The paired candidate-span arm passed whole-RDRAM, title 1024,
  hangar 512, and shutdown controls. `0x80097544`, `0x80097548`, and
  `0x8009754C` each produced one qualified hangar candidate-span writer row
  but zero post-target scalar samples or rows, selecting H2 for these PCs
  only. The port reached 2,996 image-DMA joins and 3,000 ABI events with no
  crash or abort markers. The next representatives are `0x80097554`,
  `0x80055780`, and `0x8005578C`.

  ORIGIN: independent retail phase-gated writer-PC and post-target attribution,
  paired with port image-DMA joins; no guest or host state was rewritten,
  skipped, or guarded.

- **3887:** The paired candidate-span arm passed whole-RDRAM, title 1024,
  hangar 512, and oracle-shutdown controls. `0x80097554` had one qualified
  hangar candidate-span writer row but zero post-target scalar samples or rows,
  selecting H2 for that PC only. `0x80055780` and `0x8005578C` had no qualified
  candidate-span writer rows or post-target samples, selecting H3 for those PCs
  only. The port reached 3,034 image-DMA joins and 3,038 ABI events with zero
  crash or abort markers. The next representatives are `0x8006EFAC`,
  `0x80006C2C`, and `0x80006C34`.

  ORIGIN: independent retail phase-gated writer-PC and post-target attribution,
  paired with port image-DMA joins; no guest or host state was rewritten,
  skipped, or guarded.

- **3890:** Landed the next regeneration-safe M3 guard-class change in
  `patches/heap_guards.c`. Before active-queue link stores, the guard checks
  the queue-head predecessor and the current-node reciprocal predecessor link.
  The prescribed `PatchesLib` build returned `No rule to make target
  PatchesLib`; `mips64-elf-gcc`, `mips64-elf-ld`, and
  `build/Debug/N64Recomp.exe` were not available. No allocator runtime
  behavior is claimed. The next work unit is restoring the patch pipeline and
  running its allocator smoke.

  ORIGIN: the active-queue insertion stores a linked `next`/`prev` pair;
  malformed reciprocal ownership is not legitimate allocator state. No guest
  or host state was rewritten, skipped, or guarded by the run itself.

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
