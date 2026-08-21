# Rogue Squadron 64 Recomp — current truth

Front matter for [`PORTING-STATE.md`](../PORTING-STATE.md). Durable history is
in [`PROJECT-OVERVIEW.md`](PROJECT-OVERVIEW.md); the ledger remains authoritative
for exact commands and probe rows. Maintained in Session 2079 (2026-08-20);
behavioral evidence is current through s2078.

## Current state

- Overlay dispatch is fixed enough for mission entry and post-sec2 outdoor
  presentation. The original boot/menu overlay explanation is closed.
- The qualified route reaches title VI `1024 @ 0x00790400` and hangar VI
  `512 @ 0x006AB400` with `ROGUESQ_SPIN_YIELD=1`,
  `ROGUESQ_LLE_UNGATED=1`, and `ROGUESQ_LLE_SOLO=1`. Spin yield is still
  environment-gated and default-off.
- Product multi-header freelist restore is ON. Garbage-CIMG and wrap-drop
  mitigations are OFF. A future mitigation must name its writer, state whether
  the value is legitimate, and include an `ORIGIN:` line.
- `docs/M5-AUDIO-PLAN.md` controls the incremental audio work. The default
  audio path is a silent `Broke` stub; the Factor 5 image arm is opt-in behind
  `ROGUESQ_AUDIO_UCODE=1` and is not defaulted on.
- The image arm changes DMEM and emits generated DMA writes but returns
  `Broke`, fails the reserved host canary, and has a zero-payload image-DMA
  join at the current scope. It still produces matched nonzero title PCM
  source/consumer pairs in some runs; hangar PCM remains zero. The task ABI,
  final E50 role, and complete playback contract are unresolved. No output
  routing, task-field, canary, wait, guard, or guest-gate change is authorized.
- The generated image writer reaches the host canary span through three
  guest output loops. The only reachable image-side `Broke` edge is the
  generated `break 0` after its final DMA write. The source audit does not
  establish whether the destination is output staging, scratch, or an ABI
  mismatch.
- Retail ground truth independently passes the whole-RDRAM positive control,
  reaches title and hangar, and shows slot-0 status `00 -> 01 -> 02 -> 03 ->
  00`. Exact E50 writes are owned by named retail audio-region functions;
  their sampled values are intermediate/control-like and do not match the
  port's zero-only image range.
- The port status/service boundary is understood at the observed scope:
  looping voices legitimately retain `0x02`; the service worker legitimately
  stores `0x03 -> 0x00`; a later shutdown call 3 returns after that store.
  Do not force a status byte or add a skip.
- s2078's independent retail PC watch found zero hits at `0x8000B650` and
  `0x80095D54`, while neighboring wait/tick/status PCs were active. This
  selects `H-PortOnlyFillBoundary` at requested-PC scope. It does not say
  whether the port marker is stale guest-PC state or a host copy/readback
  fault; the next unit is the bounded source/metadata crosswalk in `NEXT.md`.
- The six-site `bltzal $zero` PIC link-register class, ten-site
  `anyAudioSlotActive` spin census, dormant slot-dispatch census, and the
  generated-symbol synchronization sweep are closed at their stated scopes.
  Reopen only with a new site or discriminator.

## Active backlog

The backlog is one monotonic sequence. Closed investigations are not retained
as active work items.

1. **M5 Factor 5 image task/exit contract.** First perform the pending bounded
   port crosswalk: reconcile the generated `fillSampleStreamRange` symbol
   range and its `+336`/`+6464` labels with the separate `0x8000B650` marker and
   existing host-boundary breadcrumbs. This is source/metadata only. Depending
   on the exact table, the next unit may add one regeneration-stable boundary
   witness; it may not change waits, guards, task fields, output routing,
   canary handling, or gate stores.
2. **M3 crash work.** Only systematic idiom-class audits with a named
   discriminator. The dormant `slotDispatcherIter+872` class has 7659 clean
   hangar calls in its guarded run; no mitigation is authorized.
3. **Hangar visual artifact.** Malformed-triangle H2 is refuted by writer
   attestation and consumer-mode H1 by the RT64 census. H3 remains unavailable
   because the oracle cannot screenshot the LLE path. Do not repeat the
   `0xD60` scan.

## Durable boundaries

### Route and rendering

Factor 5 custom opcode mappings and independent-ground-truth requirements are
in [`F5-UCODE-REFERENCE.md`](F5-UCODE-REFERENCE.md) and
[`tools/oracle/README.md`](../tools/oracle/README.md). The runtime cannot be
its own witness for a null result.

Forced LLE is the route gate under the common wrapper. The accepted four-arm
table selected the interaction `LLE_UNGATED=1, LLE_SOLO=1`: `11` reaches title
and hangar, `01` reaches title only, and `10`/`00` reach neither. The result is
recipe-level port evidence, not an explanation of the audio callback or PCM
boundary. The menu spin-yield setting is a diagnostic route aid, not a default
behavior change.

The route history is preserved in PROJECT-OVERVIEW.md §39. In particular,
s2050–s2054 separate recipe qualification from C88 causality; s2055–s2060
qualify the source/consumer join, status service, shutdown return, and focus
boundary; and s2061–s2073 move the unresolved work to the image task/exit,
E50, and gate contracts.

### M5 status and service

The current generated tree reaches both target phases and emits the
regeneration-stable status census. Direct service entry/exit and the service
gate/loop are live. The port has observed the legitimate sequence through the
slot-0 service store at `0x8009B7EC`, guest address `0x80154620`, with
`old=0x03` and `new=0x00`. A later input-driven shutdown call 3 enters and
exits after that store with status `0x00`; the earlier pre-store `0x02 -> 0x03`
shutdown spin is not a missing writer.

The retail oracle independently observes the same status-table cycle and the
`0x8009B7EC` writer. It does not execute the port crash labels
`0x8000B650`/`0x80095D54`; that is a PC-scope boundary, not permission to
change the port's wait or guard behavior.

### M5 audio and guest gate

The stock `aspMain` contract is not the game's MusyX contract. The opt-in
Factor 5 image arm is isolated because its generated task function performs
real DMEM activity but does not yet satisfy the host task contract. The
phase-keyed source/consumer witness matches guest address, byte count, full
span hash, and nonzero-byte count. This closes host-boundary mutation and
callback absence for the observed route, but does not prove playback.

The retail E50 envelope is written by named audio-region functions including
`acquireSampleStreamBlock`, `musyxSynthFrame`, and `fillSampleStreamRange`.
The independent post-store witness captured control/metadata/pointer-like
values (`0x0002FFFF`, `0x0001FFFF`, `0xB02F5600`, `0x00000100`, and
`0x8019A3D0`) rather than the port's zero-only `0x25E26BC5` class. The retail
gate is mixed (`0,1,0,0,1` across the requested writers), so only the named
writer-specific gate arm was authorized. Its port treatment was not route
qualified and is not admissible for task/PCM interpretation.

### M3, M4, and generated symbols

The `-0x25A4` pointer-chase family, six-site PIC class, ten-site audio-slot
class, and dormant slot-dispatch census are closed at their stated scopes.
M3 resumes only as an idiom-class audit or with a new discriminator. M4
accumulator/beam evidence rules out the old shade-lane theory but is not pixel
ground truth. The remaining generated placeholders are genuine semantic holds
or intentional non-sync entries; the synchronization sweep is closed.

## Superseded conclusions

Detailed history is in PROJECT-OVERVIEW.md §§26 and 35–39 and in the ledger.
The maintenance compaction retains the reasons for the recent reversals here:

- The old “640 stall is a flaky crash” and missing-input/wait-return claims
  were believable because the relevant rows were absent. Same-run caller,
  VI-producer, input, and wait controls later fired; the accepted LLE/spin
  recipe reached both target phases.
- The old title/hangar callback split was believable because bridge rows were
  not joined by guest address and full byte span. s2055's phase-keyed source
  and consumer table matched every target-phase pair, leaving a content-level
  zero/nonzero boundary instead.
- The old all-zero-PCM wording was believable because the first paired runs
  were zero. s2061/s2070 showed matched nonzero title pairs in the image arm,
  while `Broke`, canary failure, and zero image payload remained. This refutes
  a pure stub or clean-image explanation, not the task ABI hypothesis.
- The old broad-band image-DMA interpretation was believable because retail
  ownership was known only for `0x166000..0x17A000`. s2063's complete exact
  port join found zero DMA payload and unmatched nonzero PCM pairs; s2068 then
  independently attributed the exact E50 envelope to retail audio writers.
- The old canary-poison hypothesis was believable because the generated output
  loops cover the reserved gap. s2070's same-route canary A/B left task exit,
  E50 payload, and PCM unchanged; the canary is therefore an observer at this
  scope, not an authorized removal target.
- The old uniform retail gate contract was believable because earlier port
  probes focused on one writer. s2073 observed all five values and selected a
  mixed contract; the s2074 treatment then failed before its gate writer in
  two crash families, so no downstream conclusion was drawn.
- The old claim that the port treatment wait path was unmeasured was
  believable because s2074 died before a complete census. s2076 showed the
  wait entered and returned, slot 0 stayed `0x00`, and the later crash carried
  the `0x8000B650` marker. s2078's independent retail PC null rules out treating
  that marker as a retail shared call site, but leaves the host/guest boundary
  open.

## Evidence ledger summary

History through s1879 is in PROJECT-OVERVIEW.md §§33–35. The VI-1024 and
spin-yield chain is in §36; the M5 archive through s2047 is in §§37–38. Section
39 records the durable s2050–s2078 route, status, audio, gate, and retail-PC
milestones migrated during this maintenance pass. The chronological ledger is
still the source for exact run commands, counts, and rejected retries.

## Method and safety rules

- Ask the retail oracle for ground truth before adding an instrument. Arm its
  whole-RDRAM positive control first; use phase-gated VI callbacks and
  physical-address watches.
- A null is worthless without a same-run positive control. Batch every A/B
  arm in one build and run. Scope counters to the relevant VI phase.
- Read `F5-UCODE-REFERENCE.md` before interpreting a Factor 5 display list.
  Regenerate in order: `make_elf.py`, N64Recomp, `fixup_game_funcs.py`, then
  CMake. Diagnostics in generated output belong in fixup scripts.
- Kill runs with SIGKILL, never SIGTERM. Run from `build/` with the ROM present.
  Capture paths must not start with `.` in the final component.
- Do not run `git submodule update`, `git checkout -- lib/...`, `git clean`, or
  `git reset --hard`. If `lib/` changes, export submodule patches in the same
  iteration.
- A mitigation is not an explanation. Name the writer, state legitimacy, and
  add an `ORIGIN:` line before landing a skip, allow, guard, or restore.
- Passive breadcrumb runs belong in `scratch/agent/soak_queue/`; do not spend
  an iteration babysitting a repeat soak.
