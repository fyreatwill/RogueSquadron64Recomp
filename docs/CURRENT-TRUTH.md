# Rogue Squadron 64 Recomp — current truth

Front matter for [`PORTING-STATE.md`](../PORTING-STATE.md). Durable history is
in [`PROJECT-OVERVIEW.md`](PROJECT-OVERVIEW.md); the ledger is authoritative
for session detail. Reviewed through s2075 (2026-08-20).

## Current state

- Overlay dispatch is fixed enough for mission entry and post-sec2 outdoor
  presentation. The original boot/menu overlay explanation is closed.
- The known-good route reaches title VI `1024 @ 0x00790400` and hangar VI
  `512 @ 0x006AB400` when `ROGUESQ_SPIN_YIELD=1` yields both menu spins. Yield
  remains environment-gated and default-off.
- s2051 requalified only the title leg: sequential forced-LLE/audio/C88=1
  arms reached title VI 1024 with spin yield and held at VI 640 without it.
  s2052 then added the previously hangar-capable
  `ROGUESQ_LLE_UNGATED=1` + `ROGUESQ_LLE_SOLO=1` tuple and reproduced the
  full ordered chain: title VI 1024 at 11.9s, 16 post-title
  `menuControllerInput` calls, four `menuInput` spin markers, and hangar VI
  512 at 21.0s. This selected the recipe-level LLE-mode hypothesis; s2054's
  four-arm table now selects interaction H-I for the two flags.
- Product multi-header freelist restore is ON. Garbage-CIMG and wrap-drop
  mitigations are OFF. Any future mitigation must name its writer, state
  legitimacy, and carry an `ORIGIN:` line.
- The six-site `bltzal $zero` PIC link-register class and the ten-site
  `anyAudioSlotActive` spin census are closed. Do not reopen them without a
  new site or discriminator.
- The hangar drain is understood through the active-voice and shutdown
  boundary. Looping voices legitimately retain status `0x02`; disabling the
  host in-loop tick lets the ROM drain return; shutdown call 3 then reaches a
  status-`0x03` wait without the service worker's zeroing path.
- `docs/M5-AUDIO-PLAN.md` governs incremental audio de-stubbing. The opt-in
  Factor 5 audio-image arm is not defaulted on. Two nonzero hangar DMA buffers
  reach `queue_samples` byte-for-byte, but complete playback and task/bridge
  semantics remain unproven.
- The stub audio arm returns `Broke` with no DMEM changes or audio DMA. In the
  same qualified route, the opt-in image arm returns `Broke` on all 122
  phase-keyed task rows while changing DMEM on all rows, failing its reserved
  canary on all rows, and producing 413 DMA-range rows (124 touching DMEM
  `0x6F0`). It nevertheless produced 19 nonzero title PCM source/consumer
  pairs; every one of the 121 source/consumer pairs matched on full-span FNV,
  byte count, and nonzero-byte count, while all 77 hangar pairs were zero.
  Task completion/slot validity remains open; host-boundary mutation is not
  selected.
- s2063 replaced the sampled DMA/PCM census with a phase-keyed exact join over
  every target-phase image task. The final route reached title `1024 @
  0x00790400` and hangar `512 @ 0x006AB400` with live task, input, and no-crash
  controls. Across 1,011 task rows and 3,729 DMA ranges, every DMA payload was
  zero; 1,013 source/consumer PCM pairs matched each other, with 19 nonzero
  title pairs and zero hangar pairs. Of 943 task rows with exact source and
  consumer joins, every joined DMA/source/consumer payload was zero. This
  selects H-ImageDmaStagingOnly and refutes a nonzero image-DMA PCM feed at
  this scope; the `Broke`/canary/DMEM contract remains open.
- s2064's bounded source audit found three generated `factor5_ucode_b` output
  loops (`L_146C`, `L_1D24`, and `L_1F40`) that intentionally cover DMEM
  `0xE50..0xFCF`, including the host canary gap `0xF80..0xF8F`. All other
  generated store families and image DMA-read destinations stay outside the
  gap. The only reachable `Broke` edge in the image function is the guest
  `break 0` at `L_1328`, after its final DMA write; the main-ucode `L_1090`
  iteration-cap fixup does not apply to `_b`. This selects the generated-guest
  writer origin and refutes a synthetic cap or image-DMA staging origin at
  source scope, but is single-source evidence and does not yet prove that the
  host's reserved-gap assumption matches the retail task ABI.
- s2065's complete generated-DMA table found five logical write paths and
  twelve logical read paths. The image reads only staged `data_ptr`/`data_size`
  fields; it never reads `output_buff` or `yield_data_ptr`. The canary span is
  the full source of the `L_1E48` `0x180`-byte DMA write, but that write's
  RDRAM destination is derived from DMEM audio state, as is the separate
  `L_1314` write. This selects H-OutputRouteUnevaluable at source scope: the
  generated writer is proven, but scratch versus output staging versus task-ABI
  mismatch cannot be selected without the live task/value relationship.
- s2066 first exposed a configuration error in the prescribed retail command:
  without Rice video it passed the whole-RDRAM and candidate-band watches but
  stayed at VI 320. The corrected Rice witness passed both watches (4,657,999
  whole-RDRAM writes; 4,647,999 band writes), reached title
  `1024 @ 0x00790400`, and reached hangar `512 @ 0x006AB400`. The port's first
  capture reached both target phases and emitted 4,105 task/row controls and
  9,878 DMA-range rows, but later aborted in `pi.cpp:do_rom_read` on an odd ROM
  DMA address; two zero-grace retries died before title in separate known
  crash families. Its admissible no-crash contract therefore failed. The
  observed rows had `output_buff=0` and `yield_ptr=0` on all 4,105 rows,
  nonzero `data_ptr`, zero overlap flags, only `0xCB0/0x198`, `0x6F0`, and one
  `0xC30` DMA-range family, and no `0xE50/0x180` row. This keeps
  H-OutputRouteUnevaluable selected: the corrected oracle qualifies the route,
  but the port task/value join is not admissible and does not select an ABI
  explanation.
- s2067 reran the existing crosswalk after the corrected Rice oracle witness.
  The oracle passed the whole-RDRAM control with 4,667,615 writes, the watched
  `0x166000..0x17A000` band with 4,657,615 writes, and both target route
  anchors. The port reached title `1024 @ 0x00790400` and hangar
  `512 @ 0x006AB400` without a crash/abort marker before the explicit SIGKILL,
  and emitted 3,076 ABI rows, 3,076 DMA rows, and 11,520 DMA ranges. Every
  target row had `output_buff=0`, `yield_ptr=0`, a nonzero `data_ptr`,
  `exit=1`, `changed>0`, and `canary_ok=0`; every observed output/yield/data
  overlap flag and every DMA payload was zero. The exact table contained
  2,172 `0xE50/0x180` ranges and 3,076 `0xCB0/0x198` ranges. This selects
  H-ImageTaskAbiMismatch at live contract scope and refutes
  H-ImageOutputField and H-ImageDataStruct. The retail writer witness remains
  band-scoped: the exact CB0 spans lie inside the watched band and the named
  MusyX PCs fired, while the E50 spans lie above it; exact E50 ownership is the
  next M5 discriminator. The task/exit result is single-source port evidence
  paired with the independent route/writer witness; no guest or host behavior
  changed.
- s2068 completed the exact-span retail writer attribution with three
  identical Rice-oracle arms, one PC histogram per target watch. Every arm
  passed the whole-RDRAM positive control (59,267--59,409 writes), reached
  title VI 1024 and hangar VI 512, and fired title-CB0 (408), hangar-CB0
  (1,125), and title E50-envelope (47,734--47,876) watches. CB0 was dominated
  by `0x800078EC` (408 title; 816 hangar), with hangar-only `0x80007670` and
  small helper counts. E50 had named audio-region writers including
  `0x8008F7D4` inside `acquireSampleStreamBlock`, `0x80091374` inside
  `musyxSynthFrame`, and `0x8008FB64/68/78` inside
  `fillSampleStreamRange`. This selects H-E50-RetailOutput at exact-span
  retail ownership scope and refutes H-CB0Only and H-NoExactOwner; it does not
  by itself prove that the port's zero-payload task output is valid final PCM.
- s2069's diagnostic-only canary A/B was completed on the fully qualified
  route in s2070. The corrected Rice oracle passed the whole-RDRAM control
  with 59,274 writes, printed title VI `1024 @ 0x00790400` and hangar VI
  `512 @ 0x006AB400`, and recorded 47,741 writes in the exact E50 envelope.
  The port emitted 5,710 target task rows, balanced 2,855/2,855 between
  canary-on/off, with live target-VI and input controls and no crash/abort
  marker before the required SIGKILL. Every row returned `exit=1`, changed
  DMEM, and retained `output_buff=0`/`yield_ptr=0`; on rows had
  `canary_ok=0`, off rows had `canary_ok=1`. It emitted 1,068 exact
  `0xE50/0x180` ranges per arm; every payload was the same zero-only
  `25E26BC5` span. Title PCM had 2,154 source/consumer rows with 14 matched
  nonzero pairs; both hangar intervals had matched source/consumer rows and
  zero nonzero pairs. Source-span keys overlapped in 17 classes. This selects
  H-CanaryObserver at the declared output-contract scope and refutes
  H-CanaryPoison: canary-off produced no improvement in exit, exact-E50
  payload, or PCM output. The small prefill-relative `dmem_changed` shift is
  not treated as a functional task improvement; the reserved-gap/ABI
  interpretation and the image `Broke`/zero-payload boundary remain open.
  The A/B and task result are single-source port evidence; the oracle is the
  independent route/E50-write witness. Default canary prefill, task fields,
  dispatch, routing, and guest behavior remain unchanged.
- s2072's corrected Rice oracle witness passed the whole-RDRAM control with
  57,353 writes, reached title VI `1024 @ 0x00790400` and hangar VI
  `512 @ 0x006AB400`, and recorded 47,353 exact-E50 writes. The first
  phase-gated requested-PC attempt was positive-controlled but produced no
  named rows because all five writers ran at 10.5--10.6s, before the title
  VI callback at 17.3s. The fixed requested-PC path captured one post-store
  value for each named writer: `0x0002FFFF`, `0x0001FFFF`, `0xB02F5600`,
  `0x00000100`, and `0x8019A3D0`, at exact E50 addresses. The final range
  snapshot had 5,721 nonzero bytes and FNV `0xA177ADED`. These values are
  control/metadata/pointer-like rather than a direct match for the port's
  zero-only `0x25E26BC5` span, selecting H-E50-RetailIntermediate and
  refuting H-E50-PortPayloadMatch at named-writer value scope. The final
  retail E50 role and the image task/exit ABI remain open.
- s2073's corrected Rice oracle gate-value witness passed the whole-RDRAM
  positive control with 10,017 writes, recorded 17 writes to `0xA0F50`, and
  reached title VI `1024 @ 0x00790400` and hangar VI `512 @ 0x006AB400`.
  Every requested writer produced a post-store row. Values were
  `0x8008EA34=0`, `0x8008EB40=1`, `0x8008ED48=0`, `0x8008EB7C=0`, and
  `0x8008EC88=1`; the aggregate was 11 zero and 6 nonzero stores. This
  selects H-RetailGateMixed and refutes H-RetailGateActive as a uniform
  nonzero contract and H-RetailGateBypass as a uniform zero contract. The
  independent retail result authorizes one writer-specific opt-in gate arm;
  no port or guest behavior changed in s2073.
- s2074 built one Debug binary and ran the prescribed qualified route with the
  existing Factor 5 image arm in both gate arms. The unchanged control reached
  title VI `1024 @ 0x00790400` and hangar VI `512 @ 0x006AB400`, with 132
  audio-task dispatch rows, 1,024 gate rows, and the `0x8008EC88` writer
  reporting `gate=0` in both target phases; it had no crash marker. The
  `ROGUESQ_M5_C88_VALUE=1` arm never reached title: the concurrent attempt
  crashed in `fillSampleStreamRange+6464` at guest PC `0x8000B650` after
  decision 1663, and an alone retry crashed in `waitForAnyAudioSlot+336` at
  guest PC `0x80095D54` after decision 356. Neither treatment run produced
  the gate writer or target-phase task/slot/PCM rows. This selects
  H-GateArmMissing as a route qualification failure, not H-GateWriterNoEffect
  or any downstream task/PCM hypothesis; it is single-source port evidence.
  The writer-specific gate arm is not admissible for another cross-run A/B
  until the wait/slot contract has an independent retail witness.
- s2075 supplied that independent retail witness with the corrected Rice
  oracle. The whole-RDRAM control recorded 10,040 writes; PIF traces showed
  eleven scheduled Start transitions; title VI `1024 @ 0x00790400` and hangar
  VI `512 @ 0x006AB400` both fired. The physical slot table at `0x154620`
  produced 21,060 reads and 40 writes, and status polling recorded repeated
  `0 -> 1 -> 2 -> 3 -> 0` transitions. The actual retail `0x8009B7EC`
  writer fired three `0x03 -> 0x00` edges, while `0x80095D54` and
  `0x8009B30C` never executed on this qualified route. This selects
  H-RetailWaitCallsiteUnreached at the requested wait-PC scope and refutes a
  retail null for the slot table; it does not authorize a port wait change or
  another gate arm yet.
- Retail ground truth independently reaches title and hangar, passes the
  whole-RDRAM positive control, and executes the menu/audio/status watch
  points. The port is never its own witness for a null result.
- s2047's C88=1, forced-LLE, opt-in run reached title with live preflight,
  host-input, service, and audio controls, but not `menuControllerInput` or
  hangar VI 512; its bridge/PCM rows remained inadmissible. s2052's route arm
  reached both anchors for 180 seconds with no missing functions or aborts,
  making the phase-keyed callback rows admissible for the next witness.
- s2049's independent retail run passed the whole-RDRAM control and reached
  title VI 1024 and hangar VI 512. The port C88=1 qualification passed
  preflight, `[pad-sdl]`/`[pad-host]`, title VI 1024, caller, gate, and service
  controls, but emitted no `menuControllerInput` and no VI 512. This selects
  the title-side guest-route boundary (R2); its bridge and PCM rows remain
  inadmissible.
- s2050's C88=1/unset pair did not reach the title anchor. Both sequential
  130-second arms passed visual/input preflight, emitted 11 host Start rises
  and the caller/post-wait controls, then held VI width 640 with no
  `menuControllerInput`, VI 1024, or VI 512. The wrapper flagged the missing
  post-key transition in both arms. This selects G4, a route/recipe
  qualification failure, and does not select C88 polarity or causality.
- s2051's sequential C88=1 pair passed the same preflight. Spin-on emitted
  three `menuInit` yields and reached title VI 1024 at 11.9s; spin-off emitted
  zero yields and held VI 640. s2052 added the prior hangar-capable LLE-mode
  tuple and reached `menuControllerInput`, `menuInput`, and VI 512, so the
  route-level boundary is closed and the callback-side rows are admissible.
- s2053's bridge/sanity join was superseded by s2055's paired witness. On
  the qualified `11` route, s2055 emitted 86 source and 86 consumer rows:
  every target-phase pair matched on RDRAM address, 384 samples, 768 bytes,
  full-span FNV, and nonzero-byte count. Title had 19 nonzero pairs followed
  by zero pairs; hangar pairs were zero. The wrapper reported a late-key
  Accessibility warning, but both target VIs were reached with 55 real audio
  task rows, 1,024 gate rows, zero missing functions, and no aborts.
- s2054's four-arm flag table separates the route tuple. With the qualified
  recipe held fixed, only `LLE_UNGATED=1, LLE_SOLO=1` reached the full title VI
  1024 -> `menuControllerInput`/`menuInput` -> hangar VI 512 chain. `10`
  reached neither target, `01` reached title only, and `00` reached neither.
  The independent retail oracle passed its whole-RDRAM control and both target
  VIs. The accepted table was run sequentially because the first concurrent
  launch made `11`/`10` crash in `waitForAnyAudioSlot` and dropped the `00`
  result; those concurrent rows are invalid and are not flag evidence.
- s2056's phase-valid C88 table selects H-R: `reapplyDisplayMode` writes
  `0 -> 1` in the opt-in arm and `0 -> 0` in the unset arm, and the raw gate
  correspondingly takes active versus skip branches. Both arms nevertheless
  reached title VI 1024 and hangar VI 512 with live host Start rises. The
  first unset attempt died in the known `waitForAnyAudioSlot` family and was
  rejected; the unchanged retry supplied the admissible comparison. The
  route-side callback counts differed (16/4 menu-controller/menu-input rows
  versus 1/0), so C88 is upstream-correlated but not sufficient to explain the
  handoff. This is single-source port evidence; the oracle independently
  qualified the target route.
- s2057's qualified C88=1 run held title VI 1024 and hangar VI 512 for 180s
  with no missing functions, aborts, or crash markers. In hangar phase 10 it
  observed five slot-0 status-3 reads, then the exact service store at
  `0x8009B7EC` changing guest `0x80154620` from `0x03` to `0x00`; the service
  exit independently read `0x00`. The separate s2008 and s2022 rows agree on
  the same slot/address and old/new values. This selects the worker-clears
  portion of H-S and refutes H-N, H-W, and H-J. Shutdown calls 1 and 2 both
  returned, but both preceded the phase-10 status-3 interval; a return after
  this store remains open.
- s2057's callback controls remained live: 123 audio-task dispatch rows, 121
  ABI rows, and 118 phase-keyed PCM source rows paired with 118 consumer rows;
  all 118 full-span joins matched and all sampled PCM was zero. The oracle's
  independent watch saw two executions at `0x8009B7EC` and 11 slot-table
  writes, while the port reached both target VIs.
- s2058's qualified route again reached title VI 1024 and hangar VI 512 with
  live input, audio-task/ABI, and PCM source/consumer controls. A 512-phase
  Start reached shutdown call 3 before any phase-10 status-3 worker store:
  the call entered with slot 0 status `0x02`, the legitimate writer at
  `0x8009B30C` changed guest `0x80154620` to `0x03`, and shutdown remained in
  the `0x03` spin with no exit. The scorer reported FAIL because its generic
  stationary-phase key check expected a VI transition, but the direct
  `[pad-host]`, shutdown-entry, and persistent-status controls fired; the
  ordered edge rows are admissible single-source port evidence; that schedule
  did not measure a post-store return.
- s2059 left hangar input idle until after the phase-10 worker store, then
  delivered a later 512-phase Start. The same run reached title VI 1024 and
  hangar VI 512, recorded the `0x8009B7EC` `0x03 -> 0x00` store first, and
  then recorded shutdown call 3 entry and exit with status `0x00`. This
  selects H-PostStoreReturn and closes the store-to-shutdown return boundary
  at this scope. The generic scorer's stationary-phase warning does not
  overturn the direct input, store, and shutdown controls.
- s2060's focus-isolated C88 A/B kept direct PID input live without any
  `raise_game` call. Both arms reached title VI 1024 and hangar VI 512 with
  `[pad-host]` controls. C88=1 wrote gate `0x01` and emitted 16
  `menuControllerInput` plus 4 `menuInput` rows; C88 unset wrote `0x00` and
  emitted 1/0. The retail oracle independently passed the whole-RDRAM
  control, title/hangar VIs, PIF input, and relevant menu PCs. This selects
  H-GateRoute and refutes focus and callback-convergence explanations at this
  scope; the scorer's Accessibility warning was a false negative because its
  stationary 640-key check did not model direct PID injection.
- s2061's corrected retail oracle passed the whole-RDRAM threshold, PIF Start
  reads, title VI 1024, hangar VI 512 at the hangar origin, and menu PCs
  `0x800B8014`/`0x800B8050`. On that qualified route, the stub arm had 125
  dispatch rows, 122 clean `Broke` task rows, zero DMEM changes, zero audio
  DMA ranges, and zero PCM. The image arm had 126 dispatch rows, 122 task
  rows with `changed>0` and `canary_ok=0`, 413 DMA-range rows, and the 19
  nonzero title PCM pairs described above. Both arms had the same live
  `[pad-host]`, target-VI, status `01 -> 02 -> 03 -> 00`, and no-crash
  controls. This is single-source port A/B evidence: it refutes a pure stub
  or host-bridge explanation, refutes clean image-task validity, and selects
  an image-task exit/canary/output-contract boundary for the next M5 unit.
- s2062's independent retail writer attribution passed the whole-RDRAM
  positive control, PIF Start reads, title VI 1024, hangar VI 512, and menu
  PCs. The image-arm destination band `0x166000..0x17A000` received
  4,240,706 retail writes, including high-volume PCs inside the named MusyX
  mixer/command-list path (`0x80090F8C`, `0x80091078`, `0x800923B8`). This
  selects H-RetailAudioWriter and refutes a wrong-destination null at this
  band; it does not prove that the whole band is final PCM or resolve the
  image task's `Broke`/canary contract.
- The generated-symbol sweep is effectively closed: the remaining 57
  placeholder names are genuine reverse-engineering holds or intentional
  non-sync entries, not a metadata sweep.

## Active backlog

This is the single monotonic backlog; historical item numbers in the ledger
are not active work items.

1. **M5 Factor 5 image task/exit contract.** s2067 selects
   H-ImageTaskAbiMismatch at live contract scope, s2070 selects
   H-CanaryObserver at the canary output scope, and s2072 selects
   H-E50-RetailIntermediate at named-writer value scope. The exact E50
   snapshot is nonzero in retail but does not match the port's zero-only
   class; this still does not identify the final E50 role or authorize routing
   output. s2073 selected a mixed retail gate contract, but s2074's
   `ROGUESQ_M5_C88_VALUE=1` treatment failed before its writer in both the
   concurrent arm and an alone retry: the control reached both target phases,
   while the treatment died in the known audio wait/render crash families at
   VI 640. H-GateArmMissing is selected as a qualification failure; no gate,
   task, slot, or PCM null is admissible from that treatment. s2075 closed the
   independent retail slot-table prerequisite but showed that the named port
   crash PC is not a retail call site. The next unit must build one phase-gated
   port census of the treatment-only wait path, joining `waitForAnyAudioSlot`,
   its dominant slot readers, status writers, and the C88 treatment's first
   failure. Do not change output routing, reverse a task field, remove the
   canary reservation, or alter waits/guards.
2. **M3 crash work.** Only complete idiom-class audits with a named
   discriminator. The dormant `slotDispatcherIter+872` class has 7659 clean
   hangar calls in its guarded run; no mitigation is authorized.
3. **Hangar visual artifact.** Malformed-triangle H2 is refuted by writer
   attestation; consumer-mode H1 is refuted by the RT64 census. H3 remains
   unavailable because the oracle cannot screenshot the LLE path. Do not
   repeat the `0xD60` scan.
4. **Generated-symbol renaming sweep.** Park until M5 and any required
   status/PCM boundary are closed. The remaining 57 names are not a sync
   backlog.

## Durable boundaries

### Route and rendering

Factor 5 custom opcode mappings and ground-truth requirements are in
[`F5-UCODE-REFERENCE.md`](F5-UCODE-REFERENCE.md) and
[`tools/oracle/README.md`](../tools/oracle/README.md). The runtime's own null
result cannot establish whether a value is game-owned or host-owned.

Forced LLE is the route gate under the common wrapper: s2024/s2025 reached
title with forced LLE while the matching HLE arm stopped at VI 640. The later
LLE crash does not erase its earlier phase-valid controls. The known menu
spin-yield fix is a diagnostic aid, not a default behavior change.

s2054 closes the flag-level ambiguity at the recipe boundary. The accepted
sequential table selected an interaction: `11` reached title and hangar,
`01` reached title but not hangar, and `10`/`00` reached neither. This is
phase-valid port evidence with `menuControllerInput` and `menuInput` as the
independent route line; the retail oracle independently qualified the target
VI route. It does not explain the audio callback or PCM boundary.

s2051's sequential pair independently requalified that title-side split:
the yield-on arm emitted three `menuInit` spin markers and reached VI 1024 at
11.9s, while yield-off emitted zero markers and stayed at VI 640. Both arms
passed visual/input preflight and produced host Start rises. Neither emitted
`menuControllerInput` or reached VI 512; the scheduled post-title keys were
therefore a handoff result, not an admissible C88 or PCM comparison. s2052
added the prior hangar-capable `ROGUESQ_LLE_UNGATED=1` and
`ROGUESQ_LLE_SOLO=1` tuple and reached `menuControllerInput`, four
`menuInput` spin markers, and VI 512. This selects the tuple at recipe level,
not either flag in isolation.

### M5 status and service

The current generated tree reaches title and hangar and emits the
regeneration-stable seven-site status census. The retail oracle independently
records the status sequence `00 -> 01 -> 02 -> 03 -> 00` and the retail writer
cluster. Static registration/linkage and the chosen indirect `get_function`
witness are closed explanations.

On the port, direct `serviceVoicePoolFrame` entry/exit and its gate/loop are
live. s2056's qualified C88=1 arm reached a live slot-0 interval where a
service entry saw `0x02`, exited with `0x03`, and subsequent service calls
observed `0x03`. s2057 then observed five phase-10 status-3 reads followed by
the service's exact `0x8009B7EC` store at slot 0, guest address `0x80154620`,
with `old=0x03`, `new=0x00`; the independent s2008 writer and s2022 store
rows agree, and the service exit read `0x00`. s2058 then showed, as
single-source port evidence, that an input-
driven shutdown can enter while the slot is still `0x02`: the legitimate
`0x8009B30C` writer changes it to `0x03`, after which call 3 remains in its
status-3 spin with no exit. s2059 then left input idle until the worker store
ran and recorded a later shutdown call 3 entry and exit with status `0x00`.
The port status sequence is therefore `00 -> 01 -> 02 -> 03 -> 00` at this
scope, and the store-to-shutdown return is now selected. Do not force a
status byte or add a skip.

s2075 independently qualified the same retail slot table before another port
arm. With the whole-RDRAM positive control, PIF Start traces, title and hangar
VI anchors, the table at physical `0x154620` produced 21,060 reads and 40
writes, and status polling captured repeated `00 -> 01 -> 02 -> 03 -> 00`
cycles. Retail `0x8009B7EC` executed three times for the `03 -> 00` edges;
`0x8009B30C` and the port crash PC `0x80095D54` did not execute. This selects
H-RetailWaitCallsiteUnreached at the requested wait-PC scope and keeps the
port-side treatment-only wait path open. No wait or guard behavior changed.

### M5 audio and guest gate

The stock `aspMain` path is not the game's MusyX contract. The opt-in Factor 5
image arm is deliberately isolated behind `ROGUESQ_AUDIO_UCODE=1`; broad DMEM
activity is real but its image/task ABI is not proven. s2055's new
`ROGUESQ_LOG_PCM_BOUNDARY` witness joins `queue_audio_buffer` to
`queue_samples` at full byte span: all 86 source/consumer pairs in title and
hangar matched on guest address, count, FNV, and nonzero-byte count. Title
content changed from 19 nonzero buffers to zero; hangar content was zero. This
selects H-P and refutes host-boundary mutation, callback absence, and phase/join
error for this route, but does not prove playback or the guest gate.

Retail executes the named display-mode writer cluster. The port fixup currently
records `0 -> 0` at `0x8008EC88`, and the raw gate consumer skips on zero. In
s2056, the opt-in `1` arm made the same writer and raw consumer take the active
path, while the unset retry kept `0` and the skip path; both arms still reached
the two target VIs. This selects H-R at the current scope: C88 is causal for
the guest gate, but not sufficient for the route handoff. The retail-value `1`
arm remains opt-in and does not authorize changing the legitimate guest writer.
The value/route conclusion is single-source port evidence; the oracle supplied
the independent route qualification. The earlier all-zero PCM result applied
to that prior arm and is not a claim about every later image run.

s2057 repeated the paired witness on the qualified C88=1 route with 118
phase-keyed source rows and 118 consumer rows. Every full-span join matched
on guest address, sample count, byte count, FNV, and nonzero-byte count; the
PCM sanity rows remained all-zero. This independently keeps the guest
source/consumer boundary selected while leaving production/playback open.

s2060 then skipped only the harness's window-raise calls in both C88 arms;
direct PID key injection remained live, and both arms reached title 1024 and
hangar 512. The C88=1 writer produced gate `0x01` in both target phases and
the route emitted 16/4 `menuControllerInput`/`menuInput` rows; the unset
writer produced `0x00` and 1/0 rows. This is single-source port A/B evidence
for H-GateRoute after H-Focus and H-StateOnly were tested; the retail oracle
provided the independent route/input/menu-PC witness. It does not prove the
Factor 5 image's task ABI or nonzero PCM.

s2061 then held that route and compared the default stub with the opt-in image
in one run sequence. Both arms reached title 1024 and hangar 512 with eight
direct `[pad-host]` rows, 121 paired PCM source/consumer rows, and the same
status writer sequence. The stub had `changed=0`, `canary_ok=1`,
`dma_count=0`, and zero PCM. The image had `changed>0` and `canary_ok=0` on
all 122 task rows, `dma_count>0` on all 122 rows, and 19 nonzero title PCM
pairs followed by zero hangar pairs. Source and consumer matched on every
full-span row, so H-HostBridge is refuted at this scope; `exit=1` on every
image row and the canary failure refute H-ImageValid. The originally expected
H-StubBoundary all-zero PCM clause is also superseded: the image does produce
nonzero title PCM, but its task/output contract is still unresolved. This is
single-source port evidence; the oracle independently qualifies only the
route and menu/input PCs.

s2062 then asked the retail ROM whether the image arm's broad candidate RDRAM
destination band was untouched, generic, or audio-owned. The independent
oracle passed the same route controls and recorded 4,240,706 writes in
`0x166000..0x17A000`; its bounded writer-PC census included high-volume
instructions inside `musyxMixActiveVoices`/`musyxBuildVoiceCommandList` and
the voice-trigger path. This selects H-RetailAudioWriter at the band scope,
but leaves H-WorkBufferNotPCM open for the band's exact subranges. The next
M5 unit must therefore narrow the image DMA/output contract rather than treat
the whole band as proven PCM.

s2063 then joined the image task's exact DMEM-to-RDRAM ranges to both PCM
boundaries. This supersedes the broad-band-only wording because it was
previously believable: s2062 proved only that retail MusyX code writes the
band, while s2061 had no same-task payload join. The complete phase-keyed port
run reached both target VIs and recorded 3,729 zero-payload DMA ranges across
1,011 task rows; 943 task rows had exact source and consumer joins, all with
zero DMA/source/consumer payloads, while 19 nonzero title PCM pairs were
unmatched by image DMA. This selects H-ImageDmaStagingOnly and refutes
H-ImageDmaFeedsPcm at this scope, but remains single-source port evidence for
the task boundary; the independent oracle still supplies only band ownership
and route qualification.

s2064 then audited the generated image function and the shared RSP memory/DMA
helpers. `L_146C`, `L_1D24`, and `L_1F40` each reach the exact `0xF80..0xF8F`
canary interval as part of an `0xE50..0xFCF` DMEM stream; the scalar stores,
other vector stores, and all image DMA-read destinations do not. The image
function's only reachable `Broke` return is the generated `break 0` at
`L_1328`, reached after the final `L_1314` DMA write. The fixup's synthetic
`L_1090` cap and its `L_10E8` audit anchor are gated to `factor5_ucode(` and
therefore do not apply to `factor5_ucode_b(`. This selects
the generated-writer portion of H-CanaryLegitimateTaskOutput at source scope
and refutes a synthetic-cap or DMA-staging origin; it is single-source
generated-tree evidence, not yet an independent retail validation of the host
gap reservation. s2065 completed the ABI table and narrowed that conclusion:
the writer origin remains selected, but no generated instruction consumes the
OSTask `output_buff` or `yield_data_ptr`, and the two output-looking RDRAM
destinations are indirect. The host-gap legitimacy and output classification
therefore remain unevaluable from generated source alone.

s2068 then supplied the missing independent E50 ownership line. Three
identical Rice-oracle arms all passed the whole-RDRAM control and both route
anchors. The title and hangar CB0 watches were dominated by `0x800078EC`, while
the E50 envelope included PCs inside `acquireSampleStreamBlock`,
`musyxSynthFrame`, and `fillSampleStreamRange`. This selects exact-span retail
audio ownership for E50 and refutes CB0-only ownership or an exact-watch null;
it does not turn the port's zero-payload image task into proven PCM.

s2069 then added the host canary A/B and source-span hash fields without
changing the default prefill, task fields, dispatch, or output routing. The
independent oracle qualified the retail route and E50 writer, but the port
retry used spin-yield without C88=1 and emitted only CB0 ranges. Its on/off
rows had the same `Broke` result but different canary comparisons and DMEM
change counts; the missing E50 rows, mostly-zero PCM, and odd-ROM-DMA abort
leave all three canary hypotheses pending until the full C88=1 recipe is run.

s2070 then supplied the full C88=1 tuple and selected H-CanaryObserver at
output-contract scope: canary-off did not improve the image task's `Broke`
result, exact-E50 payload, or PCM joins. The port task ABI and zero-payload
origin remained open. s2071's corrected retail oracle route independently
passed both VI anchors and the whole-RDRAM control, and its exact-E50
post-store sample differed from the port's zero-only class, but the bounded
value table was dominated by zero and metadata/control words and did not
capture values at the named audio PCs. This favors H-E50-RetailIntermediate at
bounded value scope without proving the final snapshot's role; no output
routing or guest behavior change is authorized.

s2072 repaired the named-PC observation linkage without changing the port. Its
positive-controlled Rice run reached title and hangar, and the requested-PC
path captured one post-step value for each exact-span writer. The values were
`0x0002FFFF`, `0x0001FFFF`, `0xB02F5600`, `0x00000100`, and `0x8019A3D0`;
the final snapshot remained nonzero with FNV `0xA177ADED`, unlike the port's
zero-only `0x25E26BC5` class. The first phase-gated attempt produced no named
rows because the writers ran before the title VI callback; the fixed targeted
path preserves the generic phase gate while handling that pre-transition
one-shot case. This selects H-E50-RetailIntermediate at named-writer value
scope and leaves the final E50 role and image task/exit ABI open.

s2073 then ran the corrected Rice oracle with the whole-RDRAM positive control,
exact gate watch, and both target VI anchors. All five requested gate writers
were observed and supplied post-store values: `0x8008EA34=0`,
`0x8008EB40=1`, `0x8008ED48=0`, `0x8008EB7C=0`, and `0x8008EC88=1`; the
aggregate was 11 zero and 6 nonzero stores. This selects
H-RetailGateMixed and refutes uniform-active and uniform-bypass contracts at
the retail writer/value scope. It is the independent prerequisite for the
next one-writer guest-gate arm; it does not authorize any output, task-ABI,
canary, wait, or guard change.

### M3, M4, and generated symbols

The `-0x25A4` pointer-chase family, six-site PIC class, ten-site audio-slot
class, and dormant slot-dispatch census are closed at their stated scopes.
M3 work resumes only as a systematic idiom-class audit or with a new
discriminator. M4 accumulator/beam evidence rules out the old shade-lane
theory, but is not pixel ground truth. The remaining 57 generated placeholders
need semantic reverse engineering, not a synchronization sweep.

## Superseded conclusions

Detailed overturned claims are archived in `PROJECT-OVERVIEW.md` §§26, 35,
36, 37, and 38. The important recent transitions are:

- The s1888–s1917 “flaky 640 crash” line was superseded by the two-source
  true-stall result and then by the menu spin-yield route control.
- The earlier missing-input, missing-wait-return, and audio-specific
  continuation claims were superseded by the s2044–s2046 shared wait,
  post-wait branch, and caller-edge tables. They were believable because the
  relevant rows were previously absent; the same-run controls now fire.
- s2030's task/DMEM result did not prove the audio ABI or PCM path. s2031–s2033
  moved the boundary to the guest gate writer/value; s2034–s2040 showed a
  repeatable but GUI-confounded C88 split rather than causal permission to
  reverse it.
- s2041–s2043 showed that title-side controls can be live without a phase-valid
  callback route. s2047 reached title but not hangar, so its bridge/PCM rows
  remained inadmissible. s2052 reproduced the prior hangar-capable LLE-mode
  tuple and reached both anchors; s2053 joined the old callback rows by phase
  and appeared H2-shaped in title but H4-shaped in hangar. s2055 supersedes
  that callback-boundary split: both target phases had paired source and
  consumer rows with identical full-span values. The old split was believable
  because the bridge logger used stdout and had no consumer-side guest-address
  or byte-span join; a missing hangar row was therefore mistaken for a missing
  callback. The remaining fact is content-level: title starts nonzero then
  becomes zero, while hangar is zero.
- s2050 did not overturn s2049's phase-valid single-arm observation: both new
  arms stopped before title 1024, so no C88 route comparison was admissible.
  The same-run controls made that a route/recipe failure, not evidence for
  either C88 polarity; s2051's yield-on title result shows the failure was not
  universal across route recipes, but did not identify the missing handoff
  condition. s2052 narrowed that condition to the prior LLE-mode tuple at
  recipe level; s2053's callback join did not separate `UNGATED` from `SOLO`.
  s2054's four-arm table closes that ambiguity and selects interaction H-I. The
  earlier wording was believable because s2052 had only a sufficient `11` arm.
- s2056 narrows the earlier C88 wording from unresolved causality to H-R. The
  first unset arm was a known early `waitForAnyAudioSlot` death, so it was not
  used; the unchanged retry reached both target VIs and showed the writer/raw
  gate split while retaining live input. The prior GUI/focus concern remained
  believable because the route callback counts still differed, and the wrapper
  emitted a late Accessibility warning.
- s2057 supersedes the wording that the status-zero worker store was
  unmeasured. It was believable after s2056 because that run had a live
  status-3 interval but no service-store join. The new regeneration-stable
  census recorded the same-slot `0x03 -> 0x00` service store and a post-store
  zero at service exit, while its shutdown-return rows were earlier than the
  status-3 interval; only the store edge was therefore closed at s2057.
- s2059 supersedes the remaining wording that a shutdown return after the
  worker store was unmeasured. It was believable because s2058's input reached
  call 3 before the status-3 worker edge and the call stayed in its spin. The
  delayed 512-phase input in s2059 produced the store first, then shutdown
  call 3 entered and exited with status `0x00`; the generic scorer warning was
  about a stationary phase, while direct input, store, and shutdown controls
  all fired.
- s2060 supersedes focus as an explanation for the C88/menu callback split.
  Focus was believable because the normal regression harness raises the game
  before each key and its scorer reported Accessibility/undriven warnings.
  The opt-in no-focus branch skipped every raise while retaining direct PID
  injection; both arms still had live input and both target VIs, while the
  gate value and callback counts remained different. The remaining M5 work is
  therefore task/slot/PCM completion, not another focus retry.
- s2061 supersedes the wording that the opt-in image's sampled PCM remained
  all-zero and that the first comparison could select only an all-zero
  `H-StubBoundary`. That wording was believable because the prior paired
  source/consumer witnesses were zero in the relevant capture and the image
  task ABI was already unproven. The new same-route A/B recorded 19 matched
  nonzero title pairs, but also recorded `exit=1` and `canary_ok=0` on all 122
  image task rows. It therefore refutes clean image validity and host-bridge
  mutation without proving the image's task/output ABI.
- s2062 supersedes the unqualified wrong-destination branch for the candidate
  image DMA band. That branch was believable because s2061 had only port-side
  DMA rows and no independent retail writer attribution. The retail oracle's
  positive-controlled, phase-qualified writer census now shows frequent
  writes from named MusyX mixer/command-list PCs, while the exact PCM
  subrange and image-task return contract remain open.
- s2063 supersedes the broad-band-only image-DMA wording. That wording was
  believable because s2062 established retail ownership of the band but did
  not join its writes to the port's PCM boundaries. The complete phase-keyed
  port table recorded zero payload in all 3,729 DMA ranges and zero-only
  source/consumer joins for 943 task rows, while 19 nonzero title PCM pairs
  remained unmatched by image DMA. This selects H-ImageDmaStagingOnly and
  refutes H-ImageDmaFeedsPcm at this scope; the task exit/canary ABI remains
  open and the task-side result is single-source port evidence.
- s2065 narrows s2064's source-scope wording from “generated writer proves
  task output” to “generated writer is identified, output role is unknown.”
  The stronger wording was believable because the canary-covering stream is
  generated guest data and is immediately DMA-written. The complete table
  shows that `output_buff` and `yield_data_ptr` are never consumed and that
  both candidate RDRAM destinations are indirect DMEM-derived values; source
  alone therefore selects H-OutputRouteUnevaluable, not scratch, output
  staging, or ABI mismatch.
- s2066 supersedes the initial unqualified retail null from this work unit.
  That null was believable because the prescribed command contained all of
  the watches and input schedule, but the oracle README's required Rice video
  plugin was omitted; the measured run stayed at VI 320. Adding the documented
  Rice plugin passed the positive control and reached both target origins.
  The corrected ground truth does not supersede the port-side null: its first
  port capture later aborted in `do_rom_read`, and the zero-grace retries died
  before target phases, so the task/value join remains unevaluable rather than
  an ABI mismatch.
- s2067 supersedes the s2066 wording that the live port task/value join was
  unevaluable. That wording was believable because the prior capture aborted
  before a canary-covering E50 row and failed the no-crash contract. The new
  capture reached both target phases, supplied exact E50 and CB0 rows, and
  showed zero field overlaps alongside `exit=1`, DMEM changes, and
  `canary_ok=0` on every target row. It therefore selects the live
  ABI/staging mismatch and refutes output-field or data-struct overlap at this
  scope; exact retail writer ownership of the E50 envelope remains open
  because the independent watch in this run covered only the lower candidate
  band.
- s2068 supersedes the s2067 wording that exact E50 ownership remained open.
  That wording was believable because s2067's independent watch covered only
  the lower candidate band. The corrected exact-span witness passed its
  whole-RDRAM control and both route anchors, and its E50 histogram contained
  PCs inside named retail audio functions, while the CB0 histograms were
  dominated by `0x800078EC`. The E50 retail ownership line is now selected;
  the port task's zero payload and ABI/exit defect remain unresolved.
- s2069 does not supersede the pending canary hypotheses. Its first port arm
  was believable as a recipe because it followed NEXT exactly, but the wrapper
  omitted the documented spin-yield gate and stopped at VI 640. The corrected
  retry added spin-yield and reached both anchors, yet still omitted the
  qualified C88=1 value, emitted no E50 rows, and aborted on the known odd-ROM
  DMA assertion. Those controls make the on/off fields a real diagnostic
  result, but not an admissible E50/output conclusion; the next full-tuple run
  must remeasure the same table.
- s2070 supersedes the wording that the canary hypotheses were pending at the
  output-contract scope. That wording was believable because s2069 had no
  C88=1 arm, no exact E50 rows, and a known host abort. The corrected witness
  reached both anchors without a crash marker and supplied balanced on/off
  task rows, exact E50 ranges, and PCM joins. Canary-off did not improve the
  `Broke` result, exact E50 payload, or PCM output, so H-CanaryPoison is
  refuted and H-CanaryObserver is selected at this scope. The task ABI and
  zero-payload `Broke` origin remain open; the selection does not authorize
  removing the reservation or changing output routing.
- s2071 supersedes the wording that exact-E50 retail ownership alone could
  support a final-output interpretation. That wording was believable because
  s2068 attached named MusyX PCs to the exact span, while s2070 supplied only
  the port's zero-only value class. The corrected, positive-controlled retail
  witness reached both target VIs and produced a bounded post-store table
  dominated by zero and metadata/control words, with a nonzero final snapshot
  that was not stable across the invasive sampler retries. It refutes a direct
  port-payload match and favors H-E50-RetailIntermediate at bounded value
  scope, but leaves named-audio-PC payload values and the final E50 role open.
- s2072 supersedes the wording that the named audio PCs had no usable
  post-store value witness. That wording was believable because the prior
  bounded sampler's generic table had already marked those PCs seen before its
  phase gate. The same-run detail trace showed their exact-span stores precede
  the title VI callback; an explicit requested-PC path then captured one
  post-step value per PC while preserving the generic phase gate and all route
  controls. The values are metadata/control/pointer-like and differ from the
  port's zero-only class, so the named-writer value boundary is selected, but
  the final E50 role and task ABI remain open.
- s2073 supersedes the wording that the retail gate had one uniform value
  contract. That wording was believable because the port's `reapplyDisplayMode`
  force-zero arm and the earlier C88 route comparison focused on one store.
  The positive-controlled retail table observed all five requested writers and
  found `0,1,0,0,1` at `0x800A0F50`, selecting H-RetailGateMixed. The result
  authorizes only a writer-specific gate test; it does not establish that the
  gate is sufficient for image-task completion or PCM output.
- s2074 supersedes the wording that the authorized writer-specific gate arm
  was ready for task/slot/PCM interpretation. That wording was believable
  because s2073 had independently qualified the retail writer and the
  unchanged port route had previously reached both target phases. In the same
  build, the default arm reached title and hangar, but the `C88_VALUE=1` arm
  crashed before title in two runs: once in `fillSampleStreamRange+6464` and
  once in `waitForAnyAudioSlot+336`. Neither treatment run reached the
  writer or target phases, so the comparison selects H-GateArmMissing as a
  route qualification failure and proves no downstream gate/task hypothesis.
  The result is single-source port evidence; the next unit must obtain the
  independent retail wait/slot contract before another treatment arm.
- s2075 supersedes only that pending prerequisite. It was believable because
  s2074's treatment died at the port's `waitForAnyAudioSlot+336`, and the
  retail witness had not yet joined the status table to its writers. The
  corrected Rice run passed the whole-RDRAM, PIF, title, and hangar controls,
  observed the retail table's repeated status cycle, and attributed its
  `03 -> 00` stores to `0x8009B7EC`; neither `0x80095D54` nor `0x8009B30C`
  executed. The retail table is therefore real, but the named wait call site
  is not a retail route boundary; the port treatment-only wait path still
  requires a port census before any gate arm is interpreted.
- The old “generated tree cannot provide a phase-valid census” provenance
  block is closed by s2016. The old “call 3 was not reached” claim is closed by
  s2007. The old “worker boundary is selected” wording is narrowed by s2028/
  s2029 to the observed legitimate writer/reaper ordering; s2057 measured
  the status-zero worker store and s2059 measured a shutdown return after that
  store.

## Evidence ledger summary

History through s1879 is in `PROJECT-OVERVIEW.md` §§33–35. The VI-1024 and
spin-yield chain is in §36. The M5 status/audio and route archive through s2047
is in §37–38 and remains in `PORTING-STATE.md` as the primary ledger.

Durable milestones are: overlay-dispatch recovery; hangar reachability;
bltzal link repair; audio-drain writer mapping; the M5 plan; opt-in
DMA-to-queue mapping; shutdown call-3 reachability; the retail status sequence
and writer attribution; the guest-gate boundary; and the callback-side
source/consumer join. s2054 selected the interacting `11` LLE-mode tuple for
the full title-to-hangar chain. s2055 paired every target-phase source and
consumer row; s2056 then selected H-R for the C88 gate-to-route boundary and
observed a live port status-3 interval. s2057 selected the worker-clears
portion of the status-3 edge with independent s2008/s2022 rows and the retail
writer-PC watch; s2059 then selected the later shutdown return after that
store. s2060 ruled out harness focus as the callback-count explanation while
preserving the C88 gate split. s2062 then selected H-RetailAudioWriter for the
candidate `0x166000..0x17A000` band from the independent retail writer census;
s2063 then selected H-ImageDmaStagingOnly from the complete zero-payload task
joins. s2064 selected the generated-writer portion of
H-CanaryLegitimateTaskOutput at source scope: the image function's generated
work/output loops, not a fixup cap or image DMA staging, reach `0xF80..0xF8F`,
and its natural `L_1328` break supplies `Broke`. The
exact host task-ABI interpretation remains open. s2065 narrowed the source
claim: the complete DMA table shows that `output_buff` and `yield_data_ptr`
are never read, and both candidate write destinations are DMEM-derived rather
than direct OSTask fields. The C88 and callback conclusions remain
single-source port evidence; the independent oracle supplied route/phase
qualification. s2067 then selected H-ImageTaskAbiMismatch at live contract
scope: both target phases had complete exact E50/CB0 rows, no task-field
overlap, zero payloads, `exit=1`, and canary failure on every row. Exact E50
writer ownership was then selected by s2068's exact-span retail witness: E50
is written by named audio-region functions, while CB0 is dominated by
`0x800078EC`. The task ABI and complete playback remain open. The oracle and
port both independently reach both target anchors, so this is not a
retail-route absence.
s2069 added a host canary A/B and source-span witness but was recipe-incomplete
for E50 because C88=1 was unset; the task ABI, canary interpretation, and
complete playback remain open pending the full tuple. s2070 supplied that
tuple and selected H-CanaryObserver: canary-off left `Broke`, exact-E50
payload, and PCM output unchanged. s2071 then ran the corrected retail
post-store value witness with the whole-RDRAM and VI controls. It recorded
57,552 whole-RDRAM writes, 47,552 exact-E50 writes, 401 bounded post-store
samples, 255 zero words, and a final snapshot of 5,745 nonzero bytes with FNV
`0xA4EF5852`; the named audio-PC value join remained absent. s2072 repaired
that join: the positive-controlled 57,353-write run reached both target VIs,
recorded 47,353 exact-E50 writes, and captured one value per named writer.
The values were `0x0002FFFF`/`0x0001FFFF`/`0xB02F5600`/`0x00000100`/
`0x8019A3D0`, while the final snapshot had 5,721 nonzero bytes and FNV
`0xA177ADED`. This refutes H-E50-PortPayloadMatch and favors
H-E50-RetailIntermediate at named-writer value scope, while leaving the final
E50 role and image task/exit ABI open.
s2073 then ran the corrected Rice gate-value witness. The positive-controlled
10,017-write run reached both target VIs, recorded 17 writes to `0xA0F50`,
and captured post-store values `0,1,0,0,1` for the requested PCs
`0x8008EA34`, `0x8008EB40`, `0x8008ED48`, `0x8008EB7C`, and `0x8008EC88`.
This selects H-RetailGateMixed and refutes uniform-active and uniform-bypass
contracts at retail writer/value scope. It authorizes the next one-writer
gate arm but leaves task ABI, output routing, canary, waits, and guards
unchanged.
s2074 then ran that writer-specific arm from one Debug build. The unchanged
control passed title and hangar phase controls, with 132 audio-task dispatch
rows and two `0x8008EC88` writer rows at `gate=0`; the treatment failed before
title in a concurrent run at `fillSampleStreamRange+6464` and in an alone
retry at `waitForAnyAudioSlot+336`. Neither treatment run reached the gate
writer or a target phase, so H-GateArmMissing is selected as a qualification
failure and no task/slot/PCM conclusion is drawn. This is single-source port
evidence; no guest or host behavior changed.
s2075 then supplied the missing retail slot-table witness. The corrected Rice
oracle passed the whole-RDRAM control with 10,040 writes, showed eleven PIF
Start transitions, and reached title `1024 @ 0x00790400` and hangar
`512 @ 0x006AB400`. The physical `0x154620` table produced 21,060 reads and
40 writes; status polling captured repeated `00 -> 01 -> 02 -> 03 -> 00`
cycles, and `0x8009B7EC` supplied three observed `03 -> 00` writer edges.
The requested `0x80095D54` wait PC and `0x8009B30C` writer had zero hits.
This selects H-RetailWaitCallsiteUnreached at the named-PC scope and leaves
the port treatment-only wait path open; no port behavior changed.

## Method and safety rules

- Ask the retail oracle for ground truth before adding an instrument. With
  debugger watches, arm the whole-RDRAM positive control first; use the
  debugger-off `--vi-poll` route for phase-valid status reads when needed.
- A null result is worthless without a same-run positive control. Batch every
  A/B arm in one build and run. Scope counters to VI phases; never compare an
  animating scene by stopwatch.
- Build every arm of the discriminating table in one iteration. A diagnostic
  field without a measurement that can select a hypothesis is not a work unit.
- Read `F5-UCODE-REFERENCE.md` before interpreting a Factor 5 display list.
  Regenerate in order: `make_elf.py`, N64Recomp, `fixup_game_funcs.py`, then
  CMake. Diagnostics in generated output belong in the fixup scripts.
- Kill runs with SIGKILL, never SIGTERM. Run from `build/` with the ROM
  present. Capture paths must not start with `.` in the final component.
- Do not run `git submodule update`, `git checkout -- lib/...`, `git clean`, or
  `git reset --hard`. If `lib/` changes, export submodule patches in the same
  iteration.
- A mitigation is not an explanation. Before adding a skip, allow, guard, or
  restore, name the writer, state whether the value is legitimate, and add an
  `ORIGIN:` line.
- Passive breadcrumb runs belong in `scratch/agent/soak_queue/`; do not spend
  an iteration babysitting a repeat soak.
