# Rogue Squadron 64 Recomp — current truth

Compact operational handoff, maintained at Session 5336 (2026-10-17).
`PORTING-STATE.md` is the chronological ledger. Durable background and the
archived renaming sweep are in `docs/PROJECT-OVERVIEW.md`; per-session
evidence is in the named `docs/*AUDIT.md` files and soak results.

## Headline

The qualified image route boots through attribution, N64 logo, intro, Factor 5
logo, title (`0x00790400`, VI 1024), hangar (`0x006AB400`, VI 512), and mission
origins (`0x00690400` and later `0x00620400`, VI 512). Mission input reaches
flight code and changes the vehicle state. The default audio route is active;
`ROGUESQ_AUDIO_UCODE=0` is the silent control.

M5 audio de-stubbing is closed for the qualified route. The image arm produces
nonzero PCM, completes its task/SP contract, reaches title/hangar/mission, and
passed the keyed mission runs plus the long mission hold. The silent arm
remains a same-build rollback/control. Details and validation rows are in
`docs/M5-AUDIO-PLAN.md` (especially s4963/s4968).

The current bounded work is a parked-boundary revisit. Sessions 5321 and 5325
confirm that the qualified port's transient M4 `0x8000` state appears in
stages 10/11 and is absent in stages 12/13 and task end, but the stage hooks
are not comparable to the retail instruction-PC samples. The M4 discriminator
is therefore unevaluable without a complete task-keyed sampler at a shared
boundary; no accumulator mitigation follows. Session 5325 validated the
retail oracle's whole-RDRAM positive control and recorded the exact shared-
boundary design in `docs/REVISIT-S5325-M4-SHARED-BOUNDARY-DESIGN.md`.
Session 5326 made the cxd4 sampler stride configurable and added generated
Factor 5 PCs to the port hooks; both sampler controls were live, but neither
driven arm reached the target hangar phase, so that attempt selected H3. Session
5329's missing boundary was caused by its window-key schedule, not a missing
capability. Session 5330 used the source-documented in-process autopilot route
(`3:start,6:start,9:start,12:start,16:a,20:a,24:start,28:a`) with the
validated LLE route. The rebuilt port passed the phase control at
1024/`0x00790400` and reached the required shared 512 boundary at
`0x006AB400` in 23.8 seconds; the M4 gate emitted 464 records. The M4
task-keyed comparison is resumed, but no accumulator conclusion is drawn
until the cxd4 and port tables join at that boundary.
Session 5331 ran that comparison attempt. The oracle whole-RDRAM/VI controls
passed, and the port again reached `0x006AB400`/512, but the port output
exposed only aggregate M4 counts; it lacked actual RSP-PC, task-serial, and
step-bucket keys. H3 remained selected at that point.
Session 5332 added a regeneration-surviving key path. In the phase-gated port
run, the same-run hook control fired and 4,091 target rows carried nonzero
task serial `961`, generated PCs `0x112C`/`0x17F0`, and increasing per-task
step values at `0x006AB400`/512. The task serial did not vary because the
target was one long graphics task, so this proves field availability and
rules out H3, but does not yet select H1/H2 or authorize a mitigation.
Session 5335 ran the corrected cxd4 retail arm and the port arm with same-run
positive controls. Retail produced 10,000 whole-RDRAM hits, live VI controls,
2,091 graphics task joins, and 1,215 tasks with transient `-32768` VACC lanes;
the port produced 4,096 target rows. The exact join remained unavailable:
retail PCs were `0x0088..0x0FE8`, while port rows used `0x112C`/`0x17F0`, and
the phase origins were `0x006AB800` versus `0x006AB400`. H3 is selected for
this discriminator; no writer or mitigation follows. See
`docs/REVISIT-S5335-M4-COMPARISON.md`.

## Durable state

### M5 audio

- Default `M_AUDTASK` dispatch selects the Factor 5 image; stock `aspMain` and
  `unknown_task_stub` are not valid RS64 de-stubbing targets.
- The task uses declared `ucode_data_size`; host PCM byte order and queue-size
  edges are fixed and qualified. `Broke` alone is not evidence of working
  audio; the complete dispatch → task fields → DMEM/DMA → SP completion →
  service/slot/voice → PCM → route chain is the required contract.
- Mission qualification is stable: three keyed runs reached mission with
  non-silent PCM and no crash/abort; the long-hold run reached the route
  repeatedly and survived to its watchdog kill. No further M5 step is open.
- Keep the named guest writers, slot/status guards, wait caps, DMEM lock, and
  SP completion behavior. Do not force gate, slot, or writeback values without
  independent retail writer evidence and an `ORIGIN:` statement.

### M3, rendering, and boundaries

- The audited trap/break/syscall/cop0, unaligned/LLSC/cache, division,
  float/FCSR, width, indirect-call, self-walk, branch-likely, variable-shift,
  HI/LO, 64-bit shift, 32-bit multiply, 64-bit mul/div, and relevant pointer
  idiom classes are closed. Re-open only with new recompiler or provenance
  evidence, and audit a whole idiom class rather than a single crash.
- Native hangar artifacts remain localized: rim band, holo spikes, stale right
  edge, Factor 5 overlay splice, accumulator origin, pillar references,
  `0x1F0D74`, and odd PI DMA are parked. No mitigation is authorized without
  naming the writer and establishing value legitimacy.
- The retail-entry byte thread was resolved as a port census byte-swizzle bug;
  it is not a current divergence. The retail-entry and M4 accumulator
  revisits remain parked unless a genuinely new discriminator appears.
- Heap/copy/message-queue/PI-DMA and audited host-wrapper pointer classes are
  closed on the qualified route with positive controls. The MIPS GCC toolchain
  is absent, so PatchesLib qualification remains blocked until supplied.

### Generated symbols

The sweep is paused after the remaining mission-overlay placeholder
`func_800E9AE0`: its exact body span is known, but the companion map supplies
no semantic name and no live caller. Session 5336 rechecked the stale
`0x800927B0` NEXT item and found every generated, registration, project-map,
fixup, and companion surface already synchronized. Preserve names that are
already synchronized, data symbols, and unmaterialized host-wrapper entries.
Only rename a real generated placeholder when the companion map and generated
tree agree. Audit files are `docs/RENAME-S*.md`.

## Operational rules

- Read `docs/F5-UCODE-REFERENCE.md` before interpreting Factor 5 commands or
  display-list anomalies. The retail oracle is independent ground truth and
  needs whole-RDRAM, VI, and phase positive controls before a null matters.
- Batch counters and all A/B arms in one build/run. Gate animated comparisons
  on VI transitions, not wall-clock time; scope budgets to the phase.
- A null result is worthless without a positive control in the same run. Two
  independent evidence lines are required before changing current truth.
- Ground truth must be consulted before building an instrument. The runtime
  cannot witness itself. A mitigation is not an explanation.
- Generated changes belong in fixup tooling. Regeneration order is
  `make_elf.py -> N64Recomp -> fixup_game_funcs.py -> cmake`.
- Run from `build/` with the ROM present, capture output to a file, and kill
  test process groups with SIGKILL. Never reset, clean, checkout, or update a
  submodule; export submodule patches after any `lib/` edit.
- Do not repeat an experiment after three consecutive non-discriminating
  iterations. A diagnostic field alone is not a work unit.

## Superseded conclusions worth retaining

- The claim that retail never had a mid-task `0x8000` VACC lane came from a
  signed/unsigned decoder error; corrected retail evidence found such lanes in
  all sampled 512-wide tasks while task-end remained zero. No mitigation
  follows.
- The port's modal `0x03` entry byte was caused by an unswizzled host byte
  census. Corrected reads match retail (`0x00` dominant, `0x03` absent).
- Earlier “M5 fully closed” claims were too broad until the keyed mission and
  long-hold rows; those rows now close the qualified route.
- Earlier route-blocked and host-load conclusions are historical. Use the soak
  queue and current `NEXT.md`; do not revive stale backlogs without a new
  measurement.

## Next steps (single monotonic backlog)

1. Keep the M4 accumulator boundary parked: the current retail and port key
   domains do not align, so do not normalize PCs/origins or infer a writer.
   Re-open only with an independently justified shared key mapping.
2. The generated-symbol sweep is parked; re-open only if a new placeholder
   candidate or companion-map evidence appears.
3. Re-open M3 only as a complete idiom-class audit selected by a new
   discriminator. Do not chase passive recurrence breadcrumbs.
4. Check for the MIPS GCC/LD toolchain before attempting PatchesLib
   qualification; both are absent in Session 5336. When supplied, record
   generation, compile, and link outcomes.

## Evidence index

Use `PORTING-STATE.md` for exact session details; never read it whole. Use
`docs/PROJECT-OVERVIEW.md` for migrated durable history, `docs/M5-AUDIO-PLAN.md`
for audio inventory and validation, `docs/F5-UCODE-REFERENCE.md` for the
microcode contract, and `scratch/agent/SOAK-RESULTS.md` for queued soak
verdicts. The next iteration must read this file, `scratch/agent/NEXT.md`, and
the tail of the soak results before acting.
