# Rogue Squadron 64 Recomp — current truth

Front matter for [`PORTING-STATE.md`](../PORTING-STATE.md). Durable history is
in [`PROJECT-OVERVIEW.md`](PROJECT-OVERVIEW.md); the ledger remains
authoritative for exact commands and probe rows. Maintained in Session 2111
(2026-08-21); behavioral and source evidence is current through s2111.

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
  `Broke` and fails the reserved host canary. Its complete task-exit,
  writeback, output-routing, and playback contracts remain unresolved.
- In the route-qualified hangar sample, stage-2 `0x6F0`/`0x300` rows matched
  nonzero DMA payloads and PCM source/consumer spans exactly. The same scope
  had `output_buff=0`, `canary_ok=0`, and `exit=1`. This selects
  `H-ImageDestIsPCM` only at the sampled stage-2 boundary; it is not
  permission to change the task ABI or output routing.
- The title path is separately selected as `H-InputZero`: title-stage input,
  transform, and DMA payloads were zero. A hangar sample had nonzero input,
  transform, and matching DMA payload, rejecting transform annihilation and
  DMA write loss for that sample.
- The image-stage writer reaches the host canary span through three guest
  loops. The only reachable image-side `Broke` edge is the generated
  `break 0` after the final DMA write. This does not establish the meaning of
  every task-field destination.
- C88 testing with explicit 0 versus 1 reached both target phases in both
  arms. C88=0 stored gate 0 and produced the sampled nonzero PCM join; C88=1
  stored gate 1 and produced no nonzero stage/PCM row. This selects
  `H-C88-ReversedOrSuppressing` at sampled port gate scope, not retail
  polarity or a default behavior change.
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

## Active backlog

The backlog is one monotonic sequence. Closed investigations are not active
work items.

1. **M5 route variance: identify the phase-7 state/origin producer.** Audit
   the complete argument/state table at the phase-7 reapply entry and its
   predecessor, preserving the B40 value arm, explicit C88=0, route controls,
   ABI/DMA/stage, slot, PCM, ordering, and VI controls. Do not change any
   gate store, branch, dispatch, output routing, task field, canary, wait,
   guard, or queue policy.
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

The s2110 route table was positive in both arms: B40 write/return and the first
two reapply pairs matched, while only B40=1 reached the later reapply entry in
that run. s2111's full-target paired run reached the same title/hangar route
in both arms. Its independent read census matched by guest PC, branch, value,
and route ordinal; host VI lines also matched phase order with a timing/origin
variation. The B40-dependent route-admission claim is superseded at the s2111
recipe scope; the remaining M5 question is the phase-7 state/origin producer,
not another B40 read-site census.

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
- `0x8000B650` is a shared last-guest-PC breadcrumb, not evidence that retail
  executes the port's fill/wait function. The generated crosswalk and
  independent retail PC watch establish that scope only.

## Evidence ledger summary

History through s1879 is in `PROJECT-OVERVIEW.md` §§33–35. The VI-1024 and
spin-yield chain is in §36; the M5 archive through s2047 is in §§37–38; the
late route/fill boundary is in §39; the s2080–s2108 archive is in §40; and the
s2110–s2111 route/read results remain in the ledger and current front matter.
The exact commands, counts, failed retries, and session headings remain in
`PORTING-STATE.md`. The current selected hypotheses are scoped above and
must not be widened from single-source or single-arm observations.

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
