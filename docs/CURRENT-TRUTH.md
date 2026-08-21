# Rogue Squadron 64 Recomp — current truth

Front matter for [`PORTING-STATE.md`](../PORTING-STATE.md). Durable history is
in [`PROJECT-OVERVIEW.md`](PROJECT-OVERVIEW.md); the ledger remains authoritative
for exact commands and probe rows. Maintained in Session 2092 (2026-08-20);
behavioral and source evidence is current through s2092.

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
- s2088's fixed retail oracle run passed the whole-RDRAM positive control
  (`102276129` writes), reached title `1024 @ 0x00790400` and hangar
  `512 @ 0x006AB400`, and sampled both exact candidate writers after the
  phase gate. `0x800921E8` wrote physical `0x00171504 = 0xB03910A0` and
  `0x80090C80` wrote physical `0x001747A4 = 0`; both destinations are in
  RDRAM and the values match the generated descriptor/zero roles. Their
  same-title-phase separation is `0x32A0`, not divisible by the `0x88`
  voice stride. This selects `H-WrongSlotBase` at the sampled pair scope
  and rejects `H-InvalidWriter` there, but does not distinguish a relocated
  retail base from a wrong field interpretation. No runtime behavior changed.
- s2089's phase-keyed retail table passed the whole-RDRAM positive control
  (`102271482` callbacks), reached title `1024 @ 0x00790400` and hangar
  `512 @ 0x006AB400`, and produced rows for all three requested PCs. The
  pointer publisher `0x8008F0EC` wrote `0x801714D0` at physical
  `0x001496F8` in both sampled rows, with no observed relocation.
  `0x800921E8` produced 16 rows on the physical `base + index*0x88 + 0x34`
  lattice (indices 0 through 8) with descriptor values `0xB03910A0` and
  `0xB03698D8`; all 16 `0x80090C80` rows were off that lattice, with
  residues 16 through 120 and zero/control-like values. That comparison was
  useful retail address evidence but not yet a field attribution. s2090's
  generated-source and companion-symbol crosswalk shows why: `0x800921E8`
  loads the voice-array entry `0x801496F8` and forms
  `base + (a0 & 0xFFFF)*0x88 + 0x34`, while `0x80090C80` is in
  `musyxKeyOnVoice` and forms its destination from the command-list globals
  `0x80149750` (head) and `0x80149760` (count), not from the voice-array
  entry. This selects `H-AlternateStructure` at generated source scope and
 supersedes the s2089 `H-WrongField` interpretation; the exact retail
 command-list root still needs independent qualification.
- s2091's corrected retail oracle table passed the whole-RDRAM positive control
  (`100291817` writes), reached title `1024 @ 0x00790400` and hangar
  `512 @ 0x006AB400`, and retained rows for all three requested PCs. The
  command-list publisher `0x80091074` wrote both `0x80171CE0` and
  `0x80173B20` to physical `0x149750`; the exact `0x80090C80` rows fit
  `head + count*0xA10 + inner*0x50 + 0x44` under those observed roots, while
  `0x800921E8` continued to land on the separate `0x88` voice-array lattice.
  This selects `H-ReallocatedCommandRoot` at root-stability scope and confirms
  the generated command-list formula at retail/source scope; it rejects
  `H-RetailVoiceArrayDivergence` and `H-OracleWriterMismatch`. The two roots
  are a ground-truth rotation result, not proof of heap corruption or a reason
  to change the port. No runtime behavior changed.
- s2092's corrected retail oracle table passed the whole-RDRAM positive control
  (`31543` writes), reached title `1024 @ 0x00790400` and hangar
  `512 @ 0x006AB400`, and sampled all three requested target ranges in one
  phase-gated run. The gate range had 17 writes from five PCs:
  `0x8008EA34`/`0x8008EB40` once each and
  `0x8008EB7C`/`0x8008EC88`/`0x8008ED48` five times each. Target-phase
  post-store rows showed gate values 0 for `0x8008EB7C` and `0x8008ED48`,
  and 1 for `0x8008EC88` (the raw aligned words were `0x00000000` and
  `0x01000000`). The countdown range `0x0014998A` had zero writes; the
  flag range `0x0014974C` had 13281 writes with post-store words
  `0x00010003` (129), `0x00000003` (131), and `0x01010003` (1).
  Its phase-gated post-value PC census was led by `0x800917A8` and
  `0x800916DC` (128 samples each), with one sample each from
  `0x80091680`, `0x800912F8`, `0x80091928`, `0x8008F20C`, and
  `0x8008F490`.
  Generated `funcs_23.c` and `fixup_game_funcs.py` independently map every
  gate PC to the named `setDisplayMode`, `reapplyDisplayMode`, or
  `musyxNoopStub` anchor. This selects `H-RetailGateWriterMatch` at the
  gate/source scope, rejects `H-PortOnlyGateContract` and
  `H-GeneratedAnchorMismatch` there, and leaves the countdown/flag completion
  contract unresolved. No gate, RSP, wait, guard, or host behavior changed.
- s2084's retail run passed the whole-RDRAM positive control, reached title and
  hangar, and again found neighboring requested PCs active while
  `0x8000B650` and `0x80095D54` stayed at zero. The new regeneration-stable
  all-phase table fired in the port's target hangar phase: seven
  `callsite-0x800903F0` rows were followed by seven `entry` rows, while the
  other three generated callsites stayed quiet. The existing target-only
  source witness emitted seven rows as well. With the host control, target VI
  phases, and 132 host rows present, this selects `H-TargetEntry` and closes
  the source-runtime reachability gap at this scope. The observed source
  arguments were ASCII-like wild values and the run crashed in `do_rom_read`
  after the rows; no mitigation or causal host conclusion is authorized.
- s2085's same-run source/host span join retained the retail whole-RDRAM
  positive control, both target VI phases, the host control, and all seven
  target-phase source rows. Every source interval began above the 8 MiB RDRAM
  domain (`0x6C676672`, `0x77696E67`, `0x6C63745D`, `0x6C676B82`,
  `0x7769738F`, `0x6C677092`, `0x776978B7`); all seven were invalid and none
  intersected a same-phase host range. This selects
  `H-SourceArgsAlreadyOutOfRange` at the source-entry scope. It does not say
  whether the values are legitimate ABI arguments or corruption upstream of
  the call, and it authorizes no host or guest mitigation.
- s2086's first retail recipe was unevaluable because it omitted the video
  plugin and stayed at 320 VI; the fixed Rice recipe passed the whole-RDRAM
  control, reached title `1024 @ 0x00790400` and hangar `512 @ 0x006AB400`,
  and kept both PC watches armed. Retail executed `0x8008FAAC` 68,624 times
  (exec-prev `0x800902CC` 68,443, `0x8009024C` 162, and `0x8002BEEC` 19),
  but never executed the exact `0x800903F0` callsite. The generated
  crosswalk shows that caller derives `a1` from voice-slot `+0x34` plus an
  aligned sample offset, derives `a2` as an aligned byte extent, and passes
  `a3` as the slot's `+0x34` base. The callee copies `a1`/`a2` into range
  endpoints and extent arithmetic and does not load through `a1`; companion
  symbols identify this as the per-voice resample path into an output buffer.
  This selects `H-CalleePointerContract` at ABI scope, refuting a scalar/tag
  relabel and an alternate-register explanation. The exact port-only
  `0x800903F0` path remains unqualified by retail and its upstream writer is
  still open; no runtime behavior changed.
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
  fault; s2080's source/metadata crosswalk resolves the symbol-scope question
  while leaving the host causal boundary open.
- s2080's bounded source/metadata crosswalk selects `H-StaleLastGuestPC` at
  the requested symbol scope. TOML, generated definition, and companion
  mapping agree that `fillSampleStreamRange` is
  `[0x8008FAAC,0x8008FFAC)`, with size `0x500`; `+336` is
  `0x8008FBFC` inside it, while `+6464` is `0x800913EC` outside it and
  `0x8000B650` is far outside it. The source attribution of `0x8000B650` as
  `beginFrameDLChunk`'s return breadcrumb explains the shared marker. This
  does not identify a causal host copy/readback fault.
- The six-site `bltzal $zero` PIC link-register class, ten-site
  `anyAudioSlotActive` spin census, dormant slot-dispatch census, and the
  generated-symbol synchronization sweep are closed at their stated scopes.
  Reopen only with a new site or discriminator.

## Active backlog

The backlog is one monotonic sequence. Closed investigations are not retained
as active work items.

1. **M5 opt-in Factor 5 audio-arm validation.** Build one binary and run the
   default silent-stub control and `ROGUESQ_AUDIO_UCODE=1` treatment from the
   same eleven-Start driver, concurrently where possible. Phase-gate both at
   title `1024 @ 0x00790400` and hangar `512 @ 0x006AB400`; collect direct
   `M_AUDTASK` dispatch, exit reason, DMEM canary, slot-status transition, and
   PCM nonzero evidence. A treatment that exits non-`Broke` with an intact
   canary and valid slot/PCM transition selects the current image arm for the
   next M5 step. Dispatch with `Broke`, canary failure, or no valid slot/PCM
   selects an unresolved task ABI/exit boundary. Missing target phases or a
   treatment-only route failure is unevaluable. No gate reversal, wait, guard,
   host, or default-dispatch change is authorized.
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

s2092's independent retail table now qualifies that boundary at the exact
`0x800A0F50` address: all five gate PCs match generated `funcs_23.c` and
`fixup_game_funcs.py` anchors, while the nearby countdown word has no retail
writes and the worker-flag word has named writers with post-store values
`0x00000003`, `0x00010003`, and `0x01010003`. Retail therefore confirms the
gate writer/source mapping but does not yet establish the port's task-exit or
PCM contract. The next M5 step is the same-build default-stub versus opt-in
Factor 5 image-arm dispatch comparison; no gate or wait change is authorized.

The s2080 crosswalk separates the generated fill function from the shared
crash marker: `fillSampleStreamRange` occupies `0x8008FAAC..0x8008FFAC`,
`+336` is in-range, and `+6464` is not. `0x8000B650` is the return breadcrumb
of `beginFrameDLChunk`, not an instruction in this function. Historical
RT64 `copyToRAM` failures carrying the same marker remain host-boundary
observations, not proof that the fill function caused them. s2084's table now
shows a target-phase source entry at the active `0x800903F0` edge; its
arguments include values such as `0x6C676672` and `0x77696E67`. s2085's join
shows all seven source intervals are outside the RDRAM domain and have no
same-phase host-range intersection; source/host causality is therefore not
admissible until the caller/callee argument semantics are established.
s2086's static ABI crosswalk now establishes that `fillSampleStreamRange`
consumes `a1` as an address/range endpoint and `a2` as an extent: the callee
uses them in allocator-boundary comparisons and node updates, without a
direct load through `a1`. `musyxRenderVoiceSamples` constructs `a1` from the
voice slot's `+0x34` base and an aligned sample offset, and the companion
mapping describes the path as writing into an output buffer. Retail reaches
the callee through `0x8009024C`/`0x800902CC` but not the port-active
`0x800903F0` edge, so the next boundary is the `+0x34` writer rather than the
callee's parameter labeling.

- s2087's static census identifies the two candidate generated voice-array
  `+0x34` stores: `musyxKeyOnVoice` `0x80090C80` copies source `+0x38`, and
  `musyxInitVoiceFromSample` `0x800921E8` stores sample-descriptor `+0x4`
  into `MEM_W[0x801496F8] + voiceIdx*0x88 + 0x34`. The required retail runs
  passed the whole-RDRAM control and both target VI phases, but the original
  physical watch used the pointer-table address as if it were the dynamic
  array base; its exact hits crosswalk to unrelated song-structure `+0x134`
  stores. The oracle pointer-watch post-step arm then remained at 320 VI and
  is unevaluable. No voice-base hypothesis is selected and no runtime change
  is authorized.

The s2087 physical-address correction is durable: `0x801496F8` is a pointer
entry, and the voice slots are at its dynamically allocated value plus
`voiceIdx*0x88`. Exact watches at pointer-table-derived addresses hit
unrelated song-structure `+0x134` stores (`startSongSequence` and
`advanceSongRegion`); they are not retail voice-slot evidence. The oracle's
pointer-watch post-step arm did not preserve the qualified route, so the
dynamic base remains open.

s2088's corrected oracle arm is the first qualified exact-writer address/value
evidence: both candidate PCs fire after title phase entry, both destinations
are physical RDRAM addresses, and the `0x800921E8` value is a ROM-mapped sample
descriptor while the `0x80090C80` value is zero. The two destinations differ by
`0x32A0` (`40 mod 0x88`) in that same phase, so they do not share one observed
0x88 lattice. s2089's repeated table then captured the pointer publisher and
showed that the pointer remained `0x801714D0`; the `0x800921E8` samples occupy
the expected lattice while the `0x80090C80` samples do not. This is still a
retail/source boundary result, not permission to rewrite the port field or to
treat the off-lattice writer as corruption. s2090 resolves the generated
source side of that boundary: `musyxKeyOnVoice` receives a voice-slot pointer
from `musyxBuildVoiceCommandList`, copies its `+0x38`, and stores it at a
command-list-derived `+0x34`; `musyxInitVoiceFromSample` receives
`(voiceIdx, sampleDesc, adsrFlag)` from `startStreamedSampleVoice` and
`soundMacroOpPlaySampleKeymap`, then stores `sampleDesc+0x4` into the dynamic
voice-array slot. s2091 closes the retail/source formula join: the command-list
publisher wrote roots `0x80171CE0` and `0x80173B20`, and the retained
`0x80090C80` destinations fit the generated formula under those roots. The
root rotates across the retail run, but the writer is not a voice-array
divergence and no port field or audio behavior change is authorized.

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
- The old interpretation of `fillSampleStreamRange+336`/`+6464` and
  `0x8000B650` as one guest-side function boundary was believable because the
  crash labels and shared last-PC marker co-occurred. s2080's exact generated,
  TOML, and companion table shows `+6464` and `0x8000B650` are outside the
  declared function interval, while the marker belongs to a different
  breadcrumbed function. The host copy/readback relationship remains open.
- The s2081 interpretation that zero source rows were caused by a stale
  `funcs_23.c` anchor was believable because the generated definition had
  moved and the fixup report showed no patch. s2082's regeneration report
  patched `funcs_24.c` x1 and the generated file contains the new witness, but
  the target-phase run still produced zero source rows while host controls
  fired. The anchor defect is therefore repaired; source-runtime reachability
  remains a witness gap, not proof that the host operation is causal.
- The s2082 `H-WitnessGap` conclusion was believable because the target-only
  source witness stayed silent even though the host control and target VI
  phases fired. s2084's same-run all-phase table passed the positive controls,
  reached target phase 12, and recorded seven callsite-to-entry pairs at
  `0x800903F0`; the gap was an over-narrow phase filter, not evidence that the
  function was never called. The host/source causal join is still unresolved.
- The s2087 assumption that physical `0x1496F8 + voiceIdx*0x88 + 0x34`
  directly named the retail voice fields was believable because the companion
  mapping described `0x801496F8` as the voice-array base pointer and supplied
  the 0x88 stride. The generated code resolves that symbol as a pointer entry;
  exact watches instead hit unrelated song-structure `+0x134` stores. The
  dynamic retail allocation must be resolved before any writer attribution.
- The s2089 `H-WrongField` attribution for `0x80090C80` was believable because
  its qualified destinations were persistently off the `0x88` lattice while
  `0x800921E8` landed on it. The s2090 source crosswalk shows the two stores
  intentionally target different structures: `0x80090C80` derives its
  destination from the command-list head/count, whereas `0x800921E8` uses the
  voice-array entry. The lattice comparison therefore cannot identify a
  wrong voice field; only the retail command-list-root join remains open.
- The first s2088 oracle run appeared qualified because its whole-RDRAM
  control and target VI phases fired, but requested `--post-value-pc` samples
  bypassed the phase gate in the tool and were taken before title entry. The
  source audit exposed that `post_value_requested_index(pc)` admitted those
  rows before `g_post_value_armed`; the fixed arm removed that bypass and
  produced the qualified pair above.

## Evidence ledger summary

History through s1879 is in PROJECT-OVERVIEW.md §§33–35. The VI-1024 and
spin-yield chain is in §36; the M5 archive through s2047 is in §§37–38. Section
39 records the durable s2050–s2078 route, status, audio, gate, and retail-PC
milestones migrated during this maintenance pass; s2080 adds the fill-function
source crosswalk, s2081 adds the host-boundary witness gap, s2082 repairs the
generated source anchor, s2084 closes the target-phase reachability gap, and
s2085 rejects the source/host span join at this scope because all source
arguments are out of range, s2086 establishes the caller/callee ABI scope
while leaving the voice-slot writer boundary open, s2087 identifies the
static voice writers while rejecting the pointer-table physical watch as a
valid retail field witness, and s2088 qualifies the exact writer pair but
finds a non-lattice destination separation. s2089 adds the repeated
phase-keyed pointer/writer table and initially selects `H-WrongField` at its
qualified retail-table scope. s2090's source/companion crosswalk supersedes
that field attribution with `H-AlternateStructure` at generated-source scope.
s2091's corrected oracle table observes both command-list roots and matches the
`0x80090C80` destinations to the generated formula, selecting rotating-root
behavior at retail root scope and closing the source/retail formula join.
s2092's corrected eleven-Start oracle table qualifies the gate/countdown/flag
table with post-store values and reconciles all five gate PCs to generated and
fixup anchors; it leaves the countdown and completion contract open and selects
the opt-in image-arm A/B as the next M5 unit.
The chronological ledger is still the source for exact run commands, counts,
and rejected retries.

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
