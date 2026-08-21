# Rogue Squadron 64 Recomp — current truth

Front matter for [`PORTING-STATE.md`](../PORTING-STATE.md). Durable history is
in [`PROJECT-OVERVIEW.md`](PROJECT-OVERVIEW.md); the ledger remains
authoritative for exact commands and probe rows. Maintained in Session 2120
(2026-08-21); behavioral and source evidence is current through s2120.

This file is intentionally compact. The s2080–s2108 archive is in
`PROJECT-OVERVIEW.md` §40.

## Current state

- Overlay dispatch is fixed enough for mission entry and post-sec2 outdoor
  presentation. The original boot/menu overlay explanation is closed.
- The qualified route reaches title VI `1024 @ 0x00790400` and hangar VI
  `512 @ 0x006AB400` with `ROGUESQ_SPIN_YIELD=1`,
  `ROGUESQ_LLE_UNGATED=1`, and `ROGUESQ_LLE_SOLO=1`. Spin yield remains
  environment-gated and default-off.
- Product multi-header freelist restore is on. Garbage-CIMG and wrap-drop
  mitigations are off. Any future mitigation must name its writer, state
  whether the value is legitimate, and include an `ORIGIN:` line.
- `docs/M5-AUDIO-PLAN.md` controls incremental audio work. The default audio
  path is a silent `Broke` stub. The Factor 5 image arm is opt-in through
  `ROGUESQ_AUDIO_UCODE=1` and is not defaulted on.
- The image arm performs real DMEM work and generated DMA writes, then returns
  `Broke` and fails the reserved host canary. The s2113 contract witness
  records the generated completion edge as guest PC `0x1328`, host exit
  `Broke`, task `output_buff=0`, and the phase-keyed post-DMA/PCM joins.
- In the route-qualified hangar sample, stage-2 `0x6F0`/`0x300` rows matched
  nonzero DMA payloads and PCM source/consumer spans exactly. The same scope
  had `output_buff=0`, `canary_ok=0`, and `exit=1`. This selects
  `H-ImageDestIsPCM` only at the sampled stage-2 boundary; it is not
  permission to change the task ABI or output routing.
- The s2113 image-arm table independently matched two nonzero phase-10
  stage-2 spans (`nz=621` and `639`) to actual dmem-to-RDRAM DMA ranges and
  exact PCM source/consumer spans, with completion before both PCM edges and
  no ordering violation. This rejects `H-WritebackLoss` and `H-NoValidOutput`
  at that sampled boundary and selects `H-TaskExitMapping` for the legitimate
  `break 0`/`Broke` edge. `output_buff=0` remains an ABI-semantics question,
  not evidence of a failed route.
- The required same-run stub/image A/B did not reach target phases in one
  pair: the image arm reached title/hangar while the stub arm crashed in
  phase 6; an earlier pair had the inverse pre-target crash. The successful
  image contract result is therefore single-arm evidence, not a cross-run A/B
  conclusion. No output or exit mapping change is authorized.
- The s2114 paired validation and its explicit-LLE retry both failed before
  target-phase coverage: the first pair bus-faulted after the 640-wide phase,
  while the retry's image arm exited pre-target and its stub arm remained at
  640-wide until SIGKILL. The phase logger fired only pre-target controls, so
  this adds no contract evidence and does not select any ABI hypothesis.
- The s2115 pair again split before the contract discriminator: the stub arm
  reached title `1024 @ 0x00790400` and hangar `512 @ 0x006AB400`, while the
  image arm's positive LLE/audio controls fired (194 LLE tasks, 42 audio
  dispatches) before a pre-target SIGSEGV in `waitForAnyAudioSlot+1060`, last
  guest PC `0x8000834c`. This is another coverage failure; no ABI hypothesis
  is selected.
- The s2116 four-arm C88 coverage contrast reached title `1024 @ 0x00790400`
  and hangar `512 @ 0x006AB400` in both image arms and in the C88=0 stub arm.
  The C88=1 stub arm alone crashed pre-target at
  `waitForAnyAudioSlot+1060` with last guest PC `0x80095d54`. Both image arms
  passed positive LLE/audio controls and emitted target task rows, so C88 did
  not split image-arm admission in this recipe. Per the planned discriminator
  this selects `H-RouteRecipeFailure` because one stub control missed target
  coverage; it does not select an image C88 hypothesis and reopens the C88=0
  contract A/B.
- The s2117 prescribed C88=0 contract pair was a coverage failure. The stub
  control reached title `1024 @ 0x00790400` and hangar `512 @ 0x006AB400`,
  with 3006 LLE tasks, 87 stub dispatch controls, and target stub rows. The
  image arm passed its LLE/audio positive controls (557 LLE tasks and 48 real
  audio dispatches) but stopped in the pre-target 640-wide phase at
  `renderFlatMeshFaceGroup+17288`, guest PC `0x8000e7fc`, after a bus error.
  It emitted no target ABI, DMA, join, or PCM rows. This selects no contract
  hypothesis; absent image rows are coverage failure, not evidence for a
  destination, writeback, or output-validity claim.
- The s2118 prescribed C88=0 pair reached title and hangar in both arms. The
  stub control passed positive controls with 2859 LLE tasks and 85 stub
  dispatches; its shared title-phase rows showed the silent contract
  (`dma_count=0`, `canary_ok=1`, `break_pc=0`, `exit=1`). The image arm passed
  positive controls with 4354 LLE tasks and 108 real dispatches. In hangar
  phase 10 it produced two nonzero stage-2 spans (`nz=621` and `639`) whose
  generated `0x6F0`/`0x300` DMA ranges and PCM source/consumer rows matched by
  guest span, byte count, full-span hash, and nonzero count; the matched join
  completed before both PCM edges with no ordering violation. Image rows
  recorded `output_buff=0`, `canary_ok=0`, `break_pc=0x1328`, and `exit=1`.
  This same-build target comparison selects `H-TaskExitMapping` and rejects
  `H-OutputRoute`, `H-WritebackLoss`, and `H-NoValidOutput` at the sampled
  boundary. The stub later crashed after hangar in `do_rom_read`; that does
  not erase the already-observed target rows. No output or exit mapping
  change is authorized.
- The s2119 retail oracle gate census passed its independent whole-RDRAM
  positive control (`38511` writes), reached title `1024 @ 0x00790400` and
  hangar `512 @ 0x006AB400`, and recorded `17` writes to physical `0xA0F50`.
  The target post-store samples contained both `0x00000000` and
  `0x01000000`; the observed writer-PC samples were `0x8008EB7C` (zero),
  `0x8008ED48` (zero), and `0x8008EC88` (nonzero). The auxiliary countdown
  watch at `0x14998A` wrote once; the worker flag at `0x14974C` wrote `17824`
  times with three nonzero values. This is single-source retail evidence:
  it rejects `H-GateNeverLive` and selects `H-GateMixed`, but does not yet
  identify which port writer controls the live task route.
- The s2120 same-build retry supplied the independent port line. Both C88 arms
  reached title and hangar, and both showed the named
  `reapplyDisplayMode:reapply-success` writer at `0x8008EC88` with final gate
  0 versus 1. C88=0 produced two nonzero phase-10 stage-2 spans (`nz=621`,
  `639`) and one exact source/consumer PCM join; C88=1 produced no nonzero
  stage or phase-10 PCM row. This selects `H-C88-ReversedOrSuppressing` at
  the sampled route: the named writer is causal, but gate 1 suppresses the
  observed nonzero image/PCM activity. The first s2120 pair was a coverage
  failure because its C88=0 arm crashed before title; it is not evidence.
- The title path is separately selected as `H-InputZero`: title-stage input,
  transform, and DMA payloads were zero. A hangar sample had nonzero input,
  transform, and matching DMA payload, rejecting transform annihilation and
  DMA write loss for that sample.
- The image-stage writer reaches the host canary span through three guest
  loops. The only reachable image-side `Broke` edge is the generated
  `break 0` after the final DMA write. This does not establish the meaning of
  every task-field destination.
- C88 testing with explicit 0 versus 1 reached both target phases in both
  arms in the s2120 retry. C88=0 stored gate 0 and produced the sampled
  nonzero stage/PCM join; C88=1 stored gate 1 and produced no nonzero
  stage/PCM row. Together with the retail writer-PC census, this selects
  `H-C88-ReversedOrSuppressing` at sampled port gate scope, not a default
  behavior change.
- Retail independently observed the live `0x8008EB40` B40 writer. In the
  phase-keyed port/host route tables, both arms fired B40 write/return and the
  same early reapply entry/success edges; B40=0 stored 0 while B40=1 stored 1.
  The s2111 whole-tree census covered 71 generated `lbu` sites. Both arms
  reached title VI `1024 @ 0x00790400` and hangar VI `512 @ 0x006AB400`. In
  both target phases the unique read/branch table matched exactly: every
  observed value was 0, with the same guest PCs, branch PCs, directions, and
  route ordinals. The phase-7 route origin differed (`0x0062B800` versus
  `0x00695C00`) and the VI transitions differed only in timing. This refutes
  `H-B40-Consumer` at the sampled route boundary and selects
  `H-RecipeVariance`; the phase-7 origin/state writer remains open.
- The s2112 phase-keyed route-state table was positive in both arms. At phase
  7, callsite, `reapplyDisplayMode` entry, and route rows matched on all four
  arguments, `a1_gate`, state bytes `0x80141AD0`/`0x8013B038`/`0x80141AD1`,
  route ordinal, and boundary VI state; both arms had origin `0x00695C00`.
  Both later recorded `audio_nonzero=0` and function exit `0`. Independent VI
  traces differed in timing and later phase count only, so this pair selects
  `H-RecipeTiming` and does not identify a phase-7 state writer.

## Active backlog

The backlog is one monotonic sequence. Closed investigations are not active
work items.

1. **M5 key-on early-return ground truth.** The gate writer arm is resolved at
   the sampled route as `H-C88-ReversedOrSuppressing`; no runtime change is
   authorized. Before touching the eight generated `musyxKeyOnVoice` divide /
   overflow early-return sites, run one retail oracle census with a whole-RDRAM
   positive control, hangar VI coverage, and all eight `--watch-pc` addresses.
   A hit identifies a retail-reached site and its execution predecessor; a
   covered zero-hit result leaves the class unproven and keeps every guard.
   Do not remove or rewrite any key-on guard in this step.
2. **M3 crash work.** Only systematic idiom-class audits with a named
   discriminator. The dormant `slotDispatcherIter+872` class has 7659 clean
   hangar calls in its guarded run; no mitigation is authorized.
3. **Hangar visual artifact.** Malformed-triangle H2 is refuted by writer
   attestation and consumer-mode H1 by the RT64 census. H3 is unavailable
   because the oracle cannot screenshot the LLE path. Do not repeat the
   `0xD60` scan.

## Durable boundaries

### Route and rendering

Factor 5 custom opcode mappings and independent-ground-truth requirements are
in [`F5-UCODE-REFERENCE.md`](F5-UCODE-REFERENCE.md) and
[`tools/oracle/README.md`](../tools/oracle/README.md). The runtime cannot be
its own witness for a null result.

Forced LLE is the route gate under the common wrapper. The accepted four-arm
table selected `LLE_UNGATED=1, LLE_SOLO=1`: `11` reaches title and hangar,
`01` reaches title only, and `10`/`00` reach neither. This is recipe-level
port evidence, not an explanation of the audio callback or PCM boundary.
Menu spin yield is a diagnostic route aid, not a default behavior change.

The route history is preserved in `PROJECT-OVERVIEW.md` §§36–41. s2093–s2096
closed the wrapper, task-thread, SP external-delivery, and guest-receive route
at the qualified recipe scope. The next route question is specifically the
B40 reader/branch after the selected pre-title split, not a reopening of the SP
queue result.

### M5 status and service

The generated tree reaches both target phases and the status census. Direct
service entry/exit and the service gate/loop are live. The port observes the
legitimate slot-0 sequence through the service store at `0x8009B7EC`, guest
address `0x80154620`, including `0x03 -> 0x00`. A later input-driven shutdown
call 3 exits after that store with status `0x00`; the earlier `0x02 -> 0x03`
spin is not a missing writer.

The retail oracle independently observes the same status-table cycle and the
`0x8009B7EC` writer. It does not execute the port crash labels
`0x8000B650`/`0x80095D54`; that is a PC-scope boundary, not permission to
change the port wait or guard behavior.

### M5 audio and guest gate

The stock `aspMain` contract is not the game's MusyX contract. The opt-in
Factor 5 image arm is isolated because its generated task function performs
real DMEM activity but does not yet satisfy the host task contract. The
phase-keyed source/consumer witness matches guest address, byte count, full
span hash, and nonzero-byte count at the sampled hangar stage.

The retail E50 envelope is written by named audio-region functions including
`acquireSampleStreamBlock`, `musyxSynthFrame`, and
`fillSampleStreamRange`. Retail exact-writer values are control,
metadata, or pointer-like values rather than the port's zero-only image
range. Retail display-gate writers are mixed; only named writer-specific
arms are authorized.

The generated image source/field audit maps `0x6F0..0x9F0` to transformed
`0x3F0`/`0x570` blocks and maps `0xCB0..0xE48` to a control/metadata block.
Their exact destinations come from task-local DMEM fields. Static code does
not prove the runtime ABI meaning of every field, and no output or task
contract change is authorized.

The s2115 image arm executed positive LLE/audio dispatch controls but died in
the pre-target `waitForAnyAudioSlot+1060` path; the stub arm reached both
target phases and produced the expected stub/PCM rows. The s2116 four-arm
contrast repaired target coverage for both image C88 values and C88=0 stub,
but not for C88=1 stub. Both image arms emitted target stage/contract rows;
the C88=0 pair was then compared against the matching stub control before
interpreting `output_buff=0`, canary failure, or task exit semantics.

The s2118 pair supplied the missing target coverage. The shared title phase
provided same-phase stub/image control rows, and the image hangar phase
supplied the nonzero stage-to-PCM join. The generated `break 0` edge at guest
PC `0x1328` therefore selects the task-exit mapping at this sampled boundary;
`output_buff=0` remains an ABI-semantics question and is not a routing fix.

The s2119 retail oracle supplied the independent gate line. Its whole-RDRAM
control fired, the run reached the hangar, and physical `0xA0F50` had both zero
and nonzero post-store values from multiple writer PCs. The s2120 paired port
arm then matched the named `0x8008EC88` writer to final gate 0 versus 1 and to
the C88=0-only nonzero stage/PCM result. Together these lines select
`H-C88-ReversedOrSuppressing` at the sampled route. No blanket gate flip or
task-contract change is authorized.

The s2110 route table was positive in both arms: B40 write/return and the first
two reapply pairs matched, while only B40=1 reached the later reapply entry in
that run. s2111's full-target paired run reached the same title/hangar route
in both arms. Its independent read census matched by guest PC, branch, value,
and route ordinal; host VI lines also matched phase order with a timing/origin
variation. The B40-dependent route-admission claim is superseded at the s2111
recipe scope; the remaining M5 question is the phase-7 state/origin producer,
not another B40 read-site census.
The s2112 caller/entry/route table matched at phase 7 in both arms, and both
arms later returned from `reapplyAudioConfig` with zero. The prior phase-7
origin split was not reproduced in this paired recipe; VI timing and later
phase count varied, selecting recipe variance at this scope without proving
the old divergence impossible in every recipe.

### M3, M4, and generated symbols

The `-0x25A4` pointer-chase family, six-site PIC class, ten-site audio-slot
class, dormant slot-dispatch census, and generated-symbol synchronization
sweep are closed at their stated scopes. M3 resumes only as an idiom-class
audit or with a new discriminator. M4 accumulator/beam evidence rules out
the old shade-lane theory but is not pixel ground truth. The remaining
generated placeholders are semantic holds or intentional non-sync entries.

## Superseded conclusions

Detailed history and exact reasons are in `PROJECT-OVERVIEW.md` §§26 and
35–40 and the ledger. The recent reversals that matter operationally are:

- “640 is a flaky crash,” missing-input, missing-wait-return, and unqualified
  PCM-null claims were believable because the relevant rows were absent.
  Same-run controls and the accepted LLE/spin recipe later reached both
  target phases.
- The old title/hangar callback split and global zero-payload image-DMA claim
  were believable because joins lacked guest address/full-span identity or
  had not sampled a nonzero hangar task. The corrected stage/PCM table and
  s2100 hangar sample supersede them at their earlier broad scopes.
- The old clean-stub, canary-poison, final-E50, and uniform-gate explanations
  were believable because the first image and retail runs lacked a complete
  task/consumer or writer-specific table. Those controls now show real image
  DMEM activity, a mixed retail gate, and a sampled nonzero hangar join, but
  they do not authorize a runtime change.
- The old retail voice-field interpretation was believable because a pointer
  entry was treated as a physical array base. Generated source and retail
  root observations show separate voice-array and command-list structures.
- The old “B40 was unreached” interpretation was believable because a shared
  logger saturated on raw-gate rows. The independent B40 witness fires in
  both arms; the remaining issue is route admission.
- The s2108 “no B40 downstream hypothesis is selected” conclusion and s2110's
  `H-B40-RouteRequired` result were believable because those reduced pairs
  lacked a control target-phase route. s2111's same-build pair reached title
  and hangar in both arms, and its complete generated read/branch table was
  identical with B40 values already 0 after reapply. Those earlier claims are
  superseded at the s2111 recipe scope; they remain historical results for
  their unqualified earlier scopes.
- The s2111 phase-7 origin difference was believable as a state-producer issue
  because the two arms had different host route origins. s2112's complete
  phase-7 rows matched, both arms reached title and hangar, and independent VI
  traces differed only in timing. This supersedes the producer selection at
  the s2112 paired-recipe scope, not as a universal claim about all recipes.
- The s2117 “no contract hypothesis selected” result was believable because
  its image arm stopped in the pre-target 640 phase and emitted no target
  rows. s2118 reached the shared title control and the image hangar rows,
  supplying the missing coverage and superseding that result at the current
  recipe scope.
- `0x8000B650` is a shared last-guest-PC breadcrumb, not evidence that retail
  executes the port's fill/wait function. The generated crosswalk and
  independent retail PC watch establish that scope only.

## Evidence ledger summary

History through s1879 is in `PROJECT-OVERVIEW.md` §§33–35. The VI-1024 and
spin-yield chain is in §36; the M5 archive through s2047 is in §§37–38; the
late route/fill boundary is in §39; the s2080–s2108 archive is in §40; and the
s2110–s2112 route/read/state results remain in the ledger and current front
matter.
The exact commands, counts, failed retries, and session headings remain in
`PORTING-STATE.md`. The current selected hypotheses are scoped above and
must not be widened from single-source or single-arm observations. s2115's
paired coverage result added no ABI selection; s2116's four-arm table added
coverage selection only; s2118 closed the sampled C88=0 contract boundary;
s2119 supplied retail mixed-writer evidence; and s2120's paired port arm
selected the causal writer and reversed/suppressing gate polarity at the
sampled route.

## Method and safety rules

- Ask the retail oracle for ground truth before adding an instrument. Arm its
  whole-RDRAM positive control first; use physical-address watches and
  phase-gated VI callbacks.
- A null is worthless without a same-run positive control. Batch all desired
  counters and every A/B arm in one build/run. Scope counters and log budgets
  to the relevant phase.
- Read `F5-UCODE-REFERENCE.md` before interpreting a Factor 5 display list.
  Regenerate in order: `make_elf.py`, N64Recomp, `fixup_game_funcs.py`, then
  CMake. Diagnostics in generated output belong in fixup scripts.
- Kill runs with SIGKILL, never SIGTERM. Run from `build/` with the ROM
  present. Capture paths must not start with `.` in the final component.
- Do not run `git submodule update`, `git checkout -- lib/...`, `git clean`,
  or `git reset --hard`. If `lib/` changes, export submodule patches in the
  same iteration.
- A mitigation is not an explanation. Name the writer, state legitimacy,
  and add an `ORIGIN:` line before landing a skip, allow, guard, or restore.
- Never add a diagnostic field without a whole discriminating table and an
  outcome that selects among hypotheses. A repeated join key or counter is
  not a work unit.
