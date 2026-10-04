# Rogue Squadron 64 Recomp — current truth

Compact operational state for [PORTING-STATE.md](../PORTING-STATE.md). Durable
background is in [PROJECT-OVERVIEW.md](PROJECT-OVERVIEW.md); the audio
inventory and de-stubbing contract are in [M5-AUDIO-PLAN.md](M5-AUDIO-PLAN.md).
Updated for session 3946 (2026-10-04).

## Current state

The validated native route boots through attribution, N64 logo, intro
cinematic, star flare, Factor 5 logo, title VI 1024 (`0x00790400`), and hangar
VI 512 (`0x006AB400`) with real-audio/LLE/spin-yield/autopilot controls.
Hangar geometry and color artifacts remain. `ROGUESQ_AUDIO_UCODE=0` selects
the silent `Broke` control; real audio is not production-complete.

The active M5 boundary is source payload, not rendering. Qualified retail and
port hangar-phase source spans are zero (`FNV=0x762B22A5`). Retail's shutdown
snapshot can retain 12 nonzero bytes, but its phase-gated hangar snapshot is
408 bytes, nonzero=0. The port descriptor `0x1798B0 -> DMEM 0xCB0` is written
by legitimate zero-valued `0x800078EC` fill activity. Session 3818 found that
sequence 664 at physical `0x179A44` is the final observed writer and every
matching input DMA had zero payload. No nonzero hangar producer is established.

The generated scalar-store census, central host/RSP writer census, native
page-fault census, and nine bounded exact-offset load candidates are closed at
their measured scopes. Do not infer a zero producer from null attribution;
target fault attribution was absent or an arm crashed before target.

## Next steps

Work only the first applicable item. This is one monotonic backlog.

1. **M3 heap guard validation — open external dependency, not a loop stop.**
   Session 3942 added the empty-queue tail-alias guard to
   `patches/heap_guards.c`. ORIGIN is the free-list dequeue publishing
   `popped`; when the published active-queue head is null, `popped == tail`
   is an ownership collision, not legitimate allocator state, so the guard
   returns before queue-link stores. The ordinary host target built
   successfully, but `PatchesLib` is not configured (`No rule to make target
   'PatchesLib'`), so MIPS/runtime qualification remains unavailable. Session
   3943 reran both checks: the ordinary Debug target completed, while
   `PatchesLib` again failed immediately and neither `mips64-elf-gcc` nor
   `mips64-elf-ld` was on PATH. Do not claim this guard is runtime-validated;
   validate the accumulated patch when a human supplies the toolchain.

2. **M5 candidate-writer qualification — continue the bounded retail census.**
   Session 3937 tested `0x80005054`, `0x80005058`, and `0x8000505C`. Retail
   whole-RDRAM, title VI 1024, hangar VI 512, and oracle-completion controls
   all passed. None of the three candidates executed in the qualified target
   phase or produced post-target rows/scalar samples, selecting H3 for this
   bounded class only. The paired port reached hangar with 3,015 image-DMA
   joins and no crash/abort; qualified payload remained
   `FNV=0x762B22A5`, nonzero=0. Session 3938 tested `0x80005060`,
   `0x80005064`, and `0x80005068`: retail whole-RDRAM, title VI 1024,
   hangar VI 512, and oracle-completion controls passed; all three candidates
   had zero target-phase execution, post-target rows, and scalar samples,
   selecting H3 for this bounded class only. The paired port reached hangar
   with 2,866 image-DMA joins and no crash/abort; qualified payload remained
   `FNV=0x762B22A5`, nonzero=0. Continue with the next adjacent unclassified
   candidates; this is not global writer absence. Session 3939 tested
   `0x8000506C`, `0x80005070`, and `0x80005074`: retail whole-RDRAM,
   title-1024, hangar-512, and oracle-completion controls passed; all three
   candidates had zero target-phase execution, post-target rows, and scalar
   samples, selecting H3 for this bounded class only. The paired port reached
   hangar with 3,022 image-DMA joins and no crash/abort; qualified payload
   remained `FNV=0x762B22A5`, nonzero=0. Continue with the next adjacent
   unclassified candidates; this is not global writer absence.
   Session 3940 tested `0x80005078`, `0x8000507C`, and `0x80005080`: retail
   whole-RDRAM, title-1024, hangar-512, and oracle-completion controls passed;
   all three candidates had zero target-phase execution, post-target rows, and
   scalar samples, selecting H3 for this bounded class only. The paired port
   reached hangar with 3,030 image-DMA joins and no crash/abort; qualified
   payload remained `FNV=0x762B22A5`, nonzero=0. Continue with the next
   adjacent unclassified candidates; this is not global writer absence.
   Session 3944 tested `0x80005090`, `0x80005094`, and `0x80005098`: retail
   whole-RDRAM, title-1024, hangar-512, and oracle-completion controls passed;
   all three candidates had zero target-phase execution, post-target rows, and
   scalar samples, selecting H3 for this bounded class only. The paired port
   reached hangar with 2,969 image-DMA joins and no crash or abort; qualified
   payload remained `FNV=0x762B22A5`, nonzero=0. Continue with the next adjacent
   unclassified candidates; this is not global writer absence.
   Session 3941 tested `0x80005084`, `0x80005088`, and `0x8000508C`: retail
   whole-RDRAM, title-1024, hangar-512, and oracle-completion controls passed;
   all three candidates had zero target-phase execution, post-target rows, and
   scalar samples, selecting H3 for this bounded class only. The paired port
   reached hangar with 3,060 image-DMA joins and no crash/abort; qualified
   payload remained `FNV=0x762B22A5`, nonzero=0. Continue with the next
   adjacent unclassified candidates; this is not global writer absence.
   Session 3945 tested `0x8000509C`, `0x800050A0`, and `0x800050A4`: retail
   whole-RDRAM, title-1024, hangar-512, and oracle-completion controls passed;
   all three candidates had zero target-phase execution, post-target rows, and
   scalar samples, selecting H3 for this bounded class only. The paired port
   reached hangar with 2,999 image-DMA joins and no crash or abort; qualified
   payload remained `FNV=0x762B22A5`, nonzero=0. Continue with the next
   adjacent unclassified candidates; this is not global writer absence.

   Session 3946 tested `0x800050A8`, `0x800050AC`, and `0x800050B0`: retail
   whole-RDRAM, title-1024, hangar-512, and oracle-completion controls passed;
   all three candidates had zero target-phase execution, post-target rows, and
   scalar samples, selecting H3 for this bounded class only. The paired port
   reached hangar with 2,831 image-DMA joins and no crash or abort; qualified
   payload remained `FNV=0x762B22A5`, nonzero=0. Continue with the next
   adjacent unclassified candidates; this is not global writer absence.

3. **M3 prior guard classes — validate the accumulated patch before extending.**
   Session 3907 extended `patches/heap_guards.c`'s reciprocal-link audit from
   the free-list head pair to the complete bounded chain, rejecting cycles and
   foreign successor/predecessor links before dequeue. The change preserves
   valid chains but remains unvalidated because this checkout lacks
   `mips64-elf-gcc`/`mips64-elf-ld`; the local Apple clang rejects the MIPS
   flags. Session 3899 confirmed CMake skips the patch pipeline because this checkout
   lacks `mips64-elf-gcc`/`mips64-elf-ld`; session 3900 also found no local
   alternate MIPS backend or toolchain. A local N64Recomp binary exists, but it
   cannot produce `patches.elf`. Session 3914 added the next complete
   active-queue idiom guard: a bounded walk now proves the terminal node is
   reachable from the published queue head and has reciprocal predecessors
   before the append stores. The full host target still builds, but this
   checkout has no `PatchesLib` target and the MIPS guard remains unvalidated;
   validate the accumulated patch when a human provides the toolchain. Session
   3915 reran the required validation: `PatchesLib` is still not a configured
   target (`No rule to make target 'PatchesLib'`), while the ordinary host
   target completes successfully. This is H3 environment evidence only; no
   allocator or MIPS-runtime claim is made. Session 3921 added the bounded
   empty-head insertion guard: if the published active-queue head is null but
   the tail successor is non-null, the append returns before publishing links.
   ORIGIN is the active-queue append writer; a successor contradicts the
   legitimate empty-queue state. The ordinary host target still builds, but
   `PatchesLib` remains unconfigured and MIPS validation is unavailable, so
   this is code landed with no runtime result. Validate the accumulated patch
   when a human provides the toolchain.
   Session 3928 added the bounded active-queue ownership-alias audit: the
   popped free-list block must not already be reachable from the published
   active-queue head before queue-link stores. ORIGIN is the free-list dequeue
   writer publishing `popped`; an existing queue-owned node is not legitimate
   allocator ownership. `PatchesLib` remains unconfigured, so this is code
   landed with H3 environment evidence only; the ordinary host target builds.
   Session 3935 added the tail-anchor audit: for a non-empty published queue,
   the node reached through `heap_tail_loc->next` must be the head with a null
   predecessor or point back to `heap_tail_loc`; otherwise the append returns
   before link stores. ORIGIN is `heap_tail_loc` and the append writer; a
   detached predecessor is not legitimate queue state. The ordinary host
   target still builds, while `PatchesLib` remains unavailable (`No rule to
   make target 'PatchesLib'`), so this is H4 environment evidence only. Do not
   add another M3 guard until the accumulated patch can be built and runtime-
   qualified.

4. **M5 audio contract qualification — remaining retail candidate-writer
   class.** Session 3900's phase-gated run passed the retail whole-RDRAM,
   title-1024, and hangar-512 controls; candidate PCs `0x80003B98`,
   `0x800044C8`, and `0x80004AB0` produced no retail rows. The paired port
   reached hangar with 3,026 image-DMA joins and no crash/abort. This closes
   that bounded class as H2 only. Session 3901's phase-gated run passed the retail whole-RDRAM,
   title-1024, and hangar-512 controls; all three PCs executed in phase but had
   zero post-target rows/samples. The paired port reached hangar with 2,836
   image-DMA joins and no crash/abort. This closes that bounded class as H2 only;
   session 3902 repeated the same discriminator for `0x80004D68`,
   `0x80004D74`, and `0x80004D78`: each executed in the qualified title phase,
   but each had zero post-target rows/samples. Retail whole-RDRAM reached
   33,193,803 writes, both target VI gates and oracle completion; the paired port
   reached hangar with 2,835 image-DMA joins and no crash/abort. This closes
   that bounded class as H2 only. Continue with `0x80004D7C`, `0x80004D84`,
   `0x80004E74`: all executed, only `0x80004E74` had a target-span phase row,
   and all had zero post-target rows/samples. Retail controls again passed;
   the paired port produced phase-5 image-DMA joins with zero payload and no
   crash/abort. This closes that bounded class as H2 only. Continue with
   `0x80004E8C`, `0x80004E90`, and `0x80004E94` all executed in the
   qualified target phase but had zero post-target rows/samples. The retail
   controls passed; the paired port reached hangar with 2,831 image-DMA joins,
   no crash/abort, and zero-valued qualified image payload. This closes that
   bounded class as H2 only. Continue with the next adjacent unclassified
   candidates; do not infer global writer absence. Session 3905 tested
   `0x80004F30`, `0x80004F34`, and `0x80004F38`: each executed during the
   qualified target phase, but all had zero post-target rows and scalar
   samples. Retail controls passed; the paired port reached hangar with
   2,800 image-DMA joins, no crash/abort, and zero-valued qualified image
   payload. This closes that bounded class as H2 only.
   Session 3906 tested `0x80004F3C`, `0x80004F44`, and `0x80004F48`: all
   executed during the qualified target phase, but each had zero post-target
   rows and scalar samples. Retail controls passed; the paired port reached
   hangar with 2,850 image-DMA joins and no crash/abort, with qualified image
   payload `FNV=0x762B22A5`, nonzero=0. This closes that bounded class as H2
   only. Continue with the next adjacent unclassified candidates.
   Session 3908 tested `0x80004F4C`, `0x80004F50`, and `0x80004F54`: all
   three executed during the qualified target phase, but each had zero
   post-target rows and scalar samples. Retail whole-RDRAM, title-1024, and
   hangar-512 controls passed; the paired port reached hangar with 2,856
   image-DMA joins and no crash/abort, with qualified image payload
   `FNV=0x762B22A5`, nonzero=0. This closes that bounded class as H2 only;
   continue with the next adjacent unclassified candidates.
   Session 3909 tested `0x80004F58`, `0x80004F5C`, and `0x80004F60`: retail
   whole-RDRAM, title-1024, and hangar-512 controls passed, but none of the
   three candidates executed in the qualified target phase and each had zero
   post-target rows and scalar samples. This closes that bounded class as H3
   only. The paired port arm crashed at about 55 ms in `spTaskSchedulerThread`
   before target phase, so it supplies no image-DMA evidence for this run.
   Continue with the next adjacent unclassified candidates only if the port
   pre-target crash is treated as a separate parked defect.
   Session 3910 tested `0x80004F64`, `0x80004F68`, and `0x80004F6C`: retail
   whole-RDRAM, title-1024, and hangar-512 controls passed and the oracle
   completed, but none of the three candidates executed in the qualified target
   phase and each had zero post-target rows/scalar samples. This closes that
   bounded class as H3 only. The paired port arm again crashed pre-target in
   `spTaskSchedulerThread` at width 320, so it supplies no image-DMA evidence.
   Continue with the next adjacent unclassified candidates while treating the
   port pre-target crash as a separate parked defect.
   Session 3911 tested `0x80004F70`, `0x80004F74`, and `0x80004F78`: retail
   whole-RDRAM, title-1024, hangar-512, and completion controls passed, but
   none executed in the qualified target phase and each had zero post-target
   rows and scalar samples. This selects H3 only for this bounded class. The
   paired port reached hangar with 2,815 image-DMA joins and no crash/abort;
   qualified image payload remained `FNV=0x762B22A5`, nonzero=0. Continue
   with the next adjacent unclassified candidates; the port caveat remains
   separate from the retail writer result.
   Session 3912 tested `0x80004F7C`, `0x80004F80`, and `0x80004F84`: retail
   controls passed, but none executed in the qualified target phase and each
   had zero post-target rows/scalar samples. This selects H3 only for this
   bounded class. The paired port reached phase 3 without crash/abort but
   recorded zero image-DMA joins, so it supplies no port payload conclusion.
   Session 3913 tested `0x80004F88`, `0x80004F8C`, and `0x80004F90`: retail
   positive controls passed (whole-RDRAM threshold, title 1024, hangar 512,
   and oracle completion), but none executed in the qualified target phase
   and each had zero post-target rows and scalar samples. This selects H3 only
   for this bounded class. The paired port reached hangar with 2,849
   image-DMA joins and no crash/abort; qualified image payload remained
   `FNV=0x762B22A5`, nonzero=0. Continue with the next adjacent unclassified
   candidates; this is not global writer absence.
   Session 3915 left `0x80004F94`, `0x80004F98`, and `0x80004F9C` as the next
   runnable candidate set after the M3 validation checkpoint remained
   unavailable. Session 3916 ran that set: retail positive controls passed
   (whole-RDRAM threshold, title 1024, hangar 512, and oracle completion),
   but all three PCs had zero target-phase execution, candidate-span rows,
   post-target rows, and scalar samples. This selects H3 for this bounded
   class only. The paired port reached hangar with 2,869 image-DMA joins and
   no crash/abort; qualified image payload remained `FNV=0x762B22A5`,
   nonzero=0. Continue with the next adjacent unclassified candidates; this
   is not global writer absence.
   Session 3917 corrected a one-level wrapper substitution defect before
   rerunning `0x80004FA0`, `0x80004FA4`, and `0x80004FA8`: the first invocation
   had executed the prior fixed oracle PCs and was discarded as
   non-discriminating. The corrected run passed retail whole-RDRAM, title-1024,
   hangar-512, and completion controls; all three candidates had zero
   target-phase execution, candidate-span rows, post-target rows, and scalar
   samples. This selects H3 for this bounded class only. The paired port
   reached hangar with 2,851 image-DMA joins and no crash/abort; qualified
   payload remained `FNV=0x762B22A5`, nonzero=0. Continue with the next
   adjacent unclassified candidates; this is not global writer absence.
   Session 3918 tested `0x80004FAC`, `0x80004FB0`, and `0x80004FB4`: retail
   whole-RDRAM, title-1024, hangar-512, and completion controls passed, but all
   three PCs had zero target-phase execution, candidate-span rows, post-target
   rows, and scalar samples. This selects H3 for this bounded class only. The
   paired port reached title and hangar with 2,264 image-DMA joins and no
   crash/abort; qualified image payload remained `FNV=0x762B22A5`, nonzero=0.
   Continue with the next adjacent unclassified candidates; this is not global
   writer absence.
   Session 3919 tested `0x80004FB8`, `0x80004FBC`, and `0x80004FC0`: retail
   positive controls passed (whole-RDRAM threshold, title 1024, hangar 512,
   and oracle completion), but all three PCs had zero target-phase execution,
   candidate-span rows, post-target rows, and scalar samples. This selects H3
   for this bounded class only. The paired port reached hangar with 2,845
   image-DMA joins and no crash/abort; qualified image payload remained
   `FNV=0x762B22A5`, nonzero=0. Continue with the next adjacent unclassified
   candidates; this is not global writer absence.
   Session 3920 tested `0x80004FC4`, `0x80004FC8`, and `0x80004FCC`: retail
   positive controls passed (whole-RDRAM threshold, title 1024, hangar 512,
   and oracle completion), but all three PCs had zero target-phase execution,
   candidate-span rows, post-target rows, and scalar samples. This selects H3
   for this bounded class only. The paired port reached hangar with 3,025
   image-DMA joins and no crash/abort; qualified image payload remained
   `FNV=0x762B22A5`, nonzero=0. Continue with the next adjacent unclassified
   candidates; this is not global writer absence.
   Session 3891's same-build silent/image pair passed independent
   retail whole-RDRAM, title-1024, and hangar-512 controls. Both arms reached
   hangar; the image arm changed DMEM, reached break `0x1328`, and issued two
   DMEM-to-RDRAM DMAs, but both payloads and PCM source/consumer joins were
   zero. This selects H-ContractGap over H-AudioDegeneracy at this scope.
   Do not add a writeback guard from this result.

5. **M5 image task/output edge — classify remaining retail writers.** The
   qualified port input and separate writeback-DMA edge are real, while the
   dominant retail `0x800078EC` activity is zero-fill, not an image producer.
   Sessions 3861–3896 classified many measured PCs as H2 (candidate-span
   writer rows but no post-value scalar attribution) or H3 (no candidate-span
   rows), always with positive controls and no global absence claim. The next
   bounded representatives are
   `0x80004FE8`, `0x80004FEC`, and `0x80004FF0`. Session 3925 tested
   `0x80004FE8`, `0x80004FEC`, and `0x80004FF0`: retail whole-RDRAM,
   title-1024, hangar-512, and oracle-completion controls passed; all three
   candidates had zero target-phase execution, post-target rows, and scalar
   samples. The paired port reached phase 5 with 2,850 image-DMA joins and no
   crash/abort; qualified image payload remained `FNV=0x762B22A5`, nonzero=0.
   This selects H3 for this bounded class only. Continue with
   `0x80004FF4`, `0x80004FF8`, and `0x80004FFC`; this is not global writer
   absence. Session 3926 tested `0x80004FF4`, `0x80004FF8`, and
   `0x80004FFC`: retail whole-RDRAM, title-1024, hangar-512, and
   oracle-completion controls passed; all three candidates had zero
   target-phase execution, post-target rows, and scalar samples. This
   selects H3 for this bounded class only. The paired port arm crashed
   pre-target in `spTaskSchedulerThread` at last guest PC `0x8000834c`, so it
   supplies no image-DMA or payload conclusion. Continue with
   `0x80005000`, `0x80005004`, and `0x80005008`; this is not global writer
   absence. Session 3927 tested `0x80005000`, `0x80005004`, and
   `0x80005008`: retail whole-RDRAM, title-1024, hangar-512, and
   oracle-completion controls passed; all three candidates had zero
   target-phase execution, candidate-span rows, post-target rows, and scalar
   samples. This selects H3 for this bounded class only. The paired port
   reached hangar with 3,047 image-DMA joins and no crash/abort; qualified
   image payload remained `FNV=0x762B22A5`, nonzero=0. Continue with
   `0x8000500C`, `0x80005010`, and `0x80005014`; this is not global writer
   absence. Session 3930 tested `0x8000500C`, `0x80005010`, and
   `0x80005014`: retail positive controls passed; all three candidates had
   zero target-phase execution, post-target rows, and scalar samples. This
   selects H3 for this bounded class only. The paired port arm crashed
   pre-target in `spTaskSchedulerThread` at last guest PC `0x8000834c`, so it
   supplies no image-DMA or payload conclusion. Continue with
   `0x80005018`, `0x8000501C`, and `0x80005020`. Session 3923 tested
   `0x80004FD0`, `0x80004FD4`, and `0x80004FD8`: retail whole-RDRAM,
   title-1024, hangar-512, and oracle-completion controls passed; all three
   candidates had zero target-phase post-target rows and scalar samples, and
   the phase writer census showed no candidate execution. This selects H3 for
   this bounded class only. The paired port reached phase 5 with 3,008
   image-DMA joins and no crash/abort; qualified payload remained
   `FNV=0x762B22A5`, nonzero=0. Continue with the next adjacent unclassified
   candidates; this is not global writer absence. The M3 validation checkpoint
   remains unavailable in this checkout, so continue with this runnable
   discriminator while treating the M3 result as environment evidence only.

   Session 3931 tested `0x80005018`, `0x8000501C`, and `0x80005020`: retail
   whole-RDRAM, title-1024, hangar-512, and oracle-completion controls passed;
   all three candidates had zero target-phase execution, post-target rows, and
   scalar samples. This selects H3 for this bounded class only. The paired
   port reached hangar with 2,880 image-DMA joins and no crash/abort;
   qualified image payload remained `FNV=0x762B22A5`, nonzero=0. Continue
   with the next adjacent unclassified candidates; this is not global writer
   absence.

   Session 3932 tested `0x80005024`, `0x80005028`, and `0x8000502C`: retail
   whole-RDRAM, title-1024, hangar-512, and oracle-completion controls passed;
   all three candidates had zero target-phase execution, post-target rows, and
   scalar samples. This selects H3 for this bounded class only. The paired
   port reached hangar with 2,846 image-DMA joins and no crash/abort;
   qualified image payload remained `FNV=0x762B22A5`, nonzero=0. Continue
   with `0x80005030`, `0x80005034`, and `0x80005038`; this is not global
   writer absence.

   Session 3933 tested `0x80005030`, `0x80005034`, and `0x80005038` after
   correcting the local binary path in the paired harness. Retail
   whole-RDRAM, title-1024, hangar-512, and oracle-completion controls all
   passed; all three candidates had zero target-phase execution, post-target
   rows, and scalar samples. This selects H3 for this bounded class only.
   The paired port reached phase 5 with 2,067 image-DMA joins and no
   crash/abort; qualified payload remained `FNV=0x762B22A5`, nonzero=0.
   Continue with `0x8000503C`, `0x80005040`, and `0x80005044`; this is not
   global writer absence.

   Session 3934 tested `0x8000503C`, `0x80005040`, and `0x80005044`: retail
   whole-RDRAM, title-1024, hangar-512, and oracle-completion controls all
   passed; all three candidates had zero qualified target-phase execution,
   post-target rows, and scalar samples. This selects H3 for this bounded
   class only. The paired port reached hangar with 2,866 image-DMA joins and
   no crash/abort; qualified payload remained `FNV=0x762B22A5`, nonzero=0.
   Continue with `0x80005048`, `0x8000504C`, and `0x80005050`; this is not
   global writer absence.

6. **M3 prior guard classes.** Metadata-slot, block-span, alias, active-head,
   and the expanded reciprocal-link guards are landed in
   `patches/heap_guards.c` but have no runtime result. The same
   missing-toolchain/build-target blocker applies; the tail-anchor audit is
   now also accumulated and must not be extended before validation.

7. **M5 target-phase parity is closed at current scope.** Do not repeat
   standalone qualification, paired target-VI controls, or the retail
   zero-writer census unless the route or build changes.

8. **Generated-symbol renaming sweep is parked.** Resume only after M5 has no
   applicable discriminator and M3 has a toolchain or a new discriminator.
   Keep HYPOTHESIS-ID `generated-symbol-renaming-sweep`; mapping edits do not
   evade the engineering-change stall gate.

## Live hypothesis table

| Hypothesis | Status |
|---|---|
| `H-M5-ProducerAbsent` | Selected for measured pre-input classes; only legitimate zero-fill writer observed. |
| `H-M5-ClearIsExpected` | Selected: `0x8008F2CC` clears object `0x801797B0`, length `0x298`. |
| `H-M5-RetailWriterPortEdgeAbsent` | Selected at measured target phases; no qualified retail target-buffer edge. |
| `H-M5-FamilyDisconnectedOutput` | Selected at s3835 scope; retail lacks access to the watched alternate-object span while port emits family stores. |
| `H-M5-TargetPhaseAudioDmaAbsent` | Selected at s3829; no target-phase `rs64_m5_audio_source_dma`. |
| `H-M5-TaskOutputFieldsEmptySeparateWriteback` | Selected at s3840 port scope. |
| `H-M5-RetailTaskStageRole` | Selected at s3846; exact task-generation-to-destination join remains open. |
| `H-M5-RetailDestinationAbsentTargetPhase` | Selected at s3855 for `0x1798B0..0x179A48`; lifetime writers are outside target buckets. |
| `H-M5-800078ECZeroFill` | Selected at s3857; sampled writes are zero-valued. |
| `H-M5-CandidateWriterClass` | Selected H2 for the bounded s3900–s3904 and s3908 sets through `0x80004F54`, and H3 for `0x80004F58`/`0x80004F5C`/`0x80004F60`/`0x80004F64`/`0x80004F68`/`0x80004F6C`/`0x80004F70`/`0x80004F74`/`0x80004F78`/`0x80004F7C`/`0x80004F80`/`0x80004F84`/`0x80004F94`/`0x80004F98`/`0x80004F9C`; this is not global writer absence. |
| `H-M5-CandidateWriterClass` | Selected H3 for `0x80004FA0`/`0x80004FA4`/`0x80004FA8`; this is not global writer absence. |
| `H-M5-CandidateWriterClass` | Selected H3 for `0x80004FAC`/`0x80004FB0`/`0x80004FB4`; this is not global writer absence. |
| `H-M5-CandidateWriterClass` | Selected H3 for `0x80004FB8`/`0x80004FBC`/`0x80004FC0`; this is not global writer absence. |
| `H-M5-CandidateWriterClass` | Selected H3 for `0x80004FC4`/`0x80004FC8`/`0x80004FCC`; this is not global writer absence. |
| `H-M5-CandidateWriterClass` | Selected H3 for `0x80004FD0`/`0x80004FD4`/`0x80004FD8`; this is not global writer absence. |
| `H-M5-CandidateWriterClass` | Selected H3 for `0x80004FDC`/`0x80004FE0`/`0x80004FE4`; this is not global writer absence. |
| `H-M5-CandidateWriterClass` | Selected H3 for `0x80004FF4`/`0x80004FF8`/`0x80004FFC`; this is not global writer absence. |
| `H-M5-CandidateWriterClass` | Selected H3 for `0x80005000`/`0x80005004`/`0x80005008`; this is not global writer absence. |
| `H-M5-CandidateWriterClass` | Selected H3 for `0x80005024`/`0x80005028`/`0x8000502C`; this is not global writer absence. |
| `H-M5-CandidateWriterClass` | Selected H3 for `0x8000503C`/`0x80005040`/`0x80005044`; this is not global writer absence. |
| `H-M5-CandidateWriterClass` | Selected H3 for `0x80005048`/`0x8000504C`/`0x80005050`; this is not global writer absence. |
| `H-M5-CandidateWriterClass` | Selected H3 for `0x80005054`/`0x80005058`/`0x8000505C`; this is not global writer absence. |
| `H-M3-HeapSpanGuard` | Code landed; validation blocked by absent tools/configured target. |
| `H-M3-FreeListReciprocalLinks` | Code landed; validation blocked by absent tools/configured target. |
| `H-M3-ActiveQueueReachability` | Code landed in s3914; validation blocked by absent MIPS toolchain and configured patch target. |
| `H-M3-ActiveQueueOwnershipAlias` | Code landed in s3928; s3929 reproduced the absent configured patch target, while the ordinary host target passed. Validation remains blocked by the MIPS toolchain/configuration. |

The s3922 M3 validation attempt confirmed the same build-system/toolchain
boundary without runtime evidence; do not treat a successful host build as
validation of MIPS patch behavior.

The many bounded candidate-PC results are intentionally summarized here:
each selected H2/H3 only for its named PC set, never as a global producer
absence. The full evidence and exact counts remain in the append-only ledger.

## Durable evidence boundary

- Retail reaches title/hangar and relevant writer PCs, while the paired port
  reaches image-DMA joins without crash/abort when the arm completes.
- Retail writes the candidate image-stage span during target phases, but the
  measured writer classes produce no qualified post-target scalar payload.
- Port task `0x80171E70`, size 1, joins the exact input DMA at matching
  generations; payloads are zero. Separate writeback joins are real.
- The repaired clear witness is `0x8008F2CC`, object `0x801797B0`, length
  `0x298`.
- The s3891 image arm proves the RSP task and two output-DMA edges execute;
  their zero payload does not identify the missing upstream writer.

Sessions 1–3927 remain in the append-only ledger. Use bounded `grep`/`sed`
windows for `PORTING-STATE.md`; never read it whole.

## Superseded conclusions

The original overlay/menu-only explanation, intrinsic VI-640 flakiness,
missing-input and wait-return explanations, global-zero image-DMA theory,
route-wide PCM-gap theory, and force-zero default policy are superseded at
their measured scopes. They were believable before qualified routes,
same-build controls, or independent retail attribution existed.

The s3579–s3584 `0x800078EC` stored-value inference is unsupported because
retail executed a byte store while the oracle read an aligned word containing
neighboring bytes. Request-only SP-yield conclusions are limited to the old
diagnostic arm. The old cinematic-pool/audio-slot interpretation was
superseded by the MusyX voice-table measurement.

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

Regeneration order is `make_elf.py -> N64Recomp -> fixup_game_funcs.py ->
CMake`. Never hand-edit generated functions for behavior changes. If `lib/`
changes, run `./submodule-patches/export.sh` and commit refreshed patches.
Never run submodule update, checkout, clean, or hard reset commands. Kill runs
with SIGKILL and run from `build/`. A mitigation-shaped change needs an
`ORIGIN:` line naming the writer and stating whether its value is legitimate.

## Evidence index

See [M5-AUDIO-PLAN.md](M5-AUDIO-PLAN.md),
[M5-S3801-IMAGE-STAGE-BOUNDARY.md](M5-S3801-IMAGE-STAGE-BOUNDARY.md),
[M5-S3802-SOURCE-WRITER-CENSUS.md](M5-S3802-SOURCE-WRITER-CENSUS.md), and
[M5-S3824-FAMILY-ROUTE-OBJECT-JOIN.md](M5-S3824-FAMILY-ROUTE-OBJECT-JOIN.md).
Detailed counts and session-specific notes remain in `PORTING-STATE.md`.
