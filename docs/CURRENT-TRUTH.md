# Rogue Squadron 64 Recomp — current truth

Front matter for [`PORTING-STATE.md`](../PORTING-STATE.md). Durable history is
in [`PROJECT-OVERVIEW.md`](PROJECT-OVERVIEW.md); the ledger is authoritative
for session detail. Reviewed through s2029 (2026-08-20).

## Current state

- Overlay dispatch is fixed enough for mission entry and post-sec2 outdoor
  presentation. The original boot/menu explanation is closed.
- Product multi-header freelist restore is ON. Garbage-CIMG and wrap-drop
  mitigations are OFF. Any future mitigation must carry an `ORIGIN:` naming
  its writer and stating whether the value is legitimate.
- The phase-gated baseline reached VI 1024 and hangar VI 512 in the known-good
  s844 and s1949-era recipes. A fresh s2016 run of the current 45-file
  generated tree also reached VI 1024 and hangar VI 512, with the existing
  status-writer census live. The later crash at guest PC `0x8000B650` is a
  separate runtime boundary; generated-tree provenance is no longer a
  prerequisite for the port-side census.
- `ROGUESQ_SPIN_YIELD=1` remains an environment-gated diagnostic aid. It
  yields runnable menu spins so host VI/SI external messages can drain; it is
  not a default behavior change. With the matching menu-input yield and the
  eleven-Start schedule, the port reaches the hangar SELECT LEVEL / AMBUSH AT
  MOS EISLEY frame.
- The six-site `bltzal $zero` PIC link-register class and the ten-site
  `anyAudioSlotActive` spin census are closed. Do not reopen them without a
  new site or a new discriminator.
- The hangar drain is understood through the active-voice and shutdown
  boundary: looping voices legitimately retain status `0x02`; disabling the
  host's in-loop tick lets the ROM drain return; shutdown call 3 then spins
  at status `0x03` while waiting for the service worker's zeroing path.
- `docs/M5-AUDIO-PLAN.md` is the governing de-stubbing design. The opt-in
  Factor 5 audio-image arm is not defaulted on. Two nonzero hangar DMA
  buffers are proven to reach `queue_samples` byte-for-byte, but complete
  playback and task/bridge semantics remain unproven.
- The generated-symbol sweep is effectively closed: the remaining 57
  placeholder names are genuine reverse-engineering holds or intentional
  non-sync entries, not a metadata sweep.
- The s2011 provenance check found no phase-valid generated tree available for
  an authorized rebuild. The current external tree has 45 generated function
  files and uncommitted companion/symbol edits; s2016 now supplies the missing
  phase-valid runtime observation without reconciling those files. The s2012
  and s2013 debugger-off retail-oracle runs
  both reached VI 1024 and hangar VI 512 while polling slot 0
  through `0x00 → 0x01 → 0x02 → 0x03 → 0x00`. This closes the retail
  status-value branch, but not host writer/thread attribution.
- The s2014 debugger-on Rice oracle passed its whole-RDRAM control (10,000
  callbacks before the tool's positive-control cap), then reached VI 1024 and
  hangar VI 512 while watching physical `0xA0F50`. It recorded the expected
  retail writer PCs: boot `0x8008EA34`/`0x8008EB40`, followed by repeated
  `0x8008ED48`/`0x8008EB7C`/`0x8008EC88` transition clusters. The watch
  logger reports PCs and phase but not old/new byte values; existing exact
  store mapping supplies that missing value detail. Retail gate-writer
  attribution is selected, while the port-side writer/thread join remains
  open.
- The s2015 block was refuted in s2016. The current external tree and the
  already-built binary expose the complete s2008 seven-site census; one fresh
  phase-gated run reached VI 1024 and hangar VI 512 and emitted slot-0 rows,
  including `0x8009B2C4` changing `0x01` to `0x00` during shutdown call 3.
  No owner authorization or companion-file reconciliation was needed. The
  seven-site writer/thread join remains unselected because the run crashed at
  the known `0x8000B650` boundary before the worker-side control became live.
- The s2017 recipe audit removed the input-route explanation for the missing
  worker control: the prescribed tap recipe, a phase-relative retry, and the
  archived 400-ms hold/mixed-probe recipe all reached the phase-valid title /
  hangar route. All three emitted slot-0 status rows and shutdown call 3, but
  none emitted the unconditional `serviceVoicePoolFrame` entry/exit rows or
  the `0x8009B7EC` control. This is a positive-control failure, not H1/H2/H3
  evidence.
- The s2018 source/binary crosswalk places `serviceVoicePoolFrame` in the
  base `section_3_text_funcs` table (`ROM 0x1040`, `RAM 0x80000440`), where
  offset `0x9B168` maps to guest `0x8009B5A8`. The generated definition, base
  table entry, and linked `_serviceVoicePoolFrame` symbol are present, but
  there is no named incoming reference or direct branch to that host symbol
  in the current 45-file tree/binary. The static missing-registration/linkage
  H2 explanation is refuted; H1 and H3 remain unselected because the caller
  path itself is not present in this crosswalk.
- The s2019 runtime-resolution witness refuted the indirect `get_function`
  lookup as the observable mechanism: both independent controls
  (`[dma-ring-caller]` and `[tickfunc-caller]`) were zero in the same
  phase-valid VI 1024 and 512 run; the direct service entry diagnostic fired
  its bounded pre-title rows, confirming the phase gate was live. Combined
  with the s2018 static crosswalk that refuted static linkage/registration,
  both arms of the missing-registration hypothesis are closed. Only a runtime
  caller-path or audio-side gate before the function remains open. The s2020
  checkpoint formally restated this as discrimination language for the gate.
- The s2021 clean-regenerated tree built successfully and its same-run direct
  witness emitted 2,096 phase-valid `serviceVoicePoolFrame` entries and
  2,096 exits. The bounded pre-phase control emitted zero rows, while the
  independent s2006 entry/exit control and the existing service-entry control
  also fired. Every s2020 row had `thr=0`, `status=0x00`, and `ra=0`, yielding
  the unusable derived call site `0xFFFFFFF8`; the expected retail predecessor
  `0x80019B74` was not observed. No `0x8009B7EC` store edge fired. This
  selects the planned D4 service-body boundary: the target is reached and
  returns, but its worker-side clear path is not reached. The zero `ra` is an
  attribution failure, not yet evidence of a specific caller mismatch.
- The s2022 three-edge body census refined D4 in one phase-valid run. Its
  independent s2020 entry/exit controls emitted 1,988/1,988 rows, while all
  1,988 s2022 branch rows had gate `0x800A5121=0x01`, `path=body`; all 1,988
  loop rows were slot 0 with status `0x00` and `zero_skip=1`; the independent
  s2022 store edge emitted zero rows. The s2006 entry/exit controls each
  emitted 24 rows. This selects H2: the port reaches the service body, but
  the observed slot/status predicate skips before the status-zero store. The
  run later hit the known PI `do_rom_read` abort. A separate retail-oracle
  run passed its whole-RDRAM control (10,000 callbacks), reached VI 3585 and
  hangar VI 512, and independently recorded 3,033 executions each at
  `0x8009B5D8`/`0x8009B624` and two at `0x8009B7EC`, plus 15 writes to the
   exact status word; this is the second line for the retail body contract.
- The s2023 status-writer capture was not phase-valid after clean
  regeneration. The no-yield arm remained at VI 640 for more than four
  minutes; the `ROGUESQ_SPIN_YIELD=1` correction instead aborted in
  `RT64::RenderTarget::copyFromTarget` before VI 1024. Both arms had live
  s2020/s2022 body controls but no s2008 writer positive-control row, so H1,
  H2, and H3 remain unresolved and the missing writer is a census-anchor
  failure, not status evidence.
- The s2024 route-recovery A/B first repeated the no-input direct no-LLE arm:
  forced-LLE crashed in `RT64::Interpreter::processRDPLists` with last guest
  PC `0x8000B650` after VI 640, while no-LLE stayed at VI 640. The fixed
  same-window rerun used the eleven-Start boot schedule for the direct arm.
  The forced-LLE runner then reached VI 1024 at 48.9s; the direct no-LLE
  `tools/probe.sh` arm delivered all eleven key sends but stayed at VI 640
  through its 120s timeout. The fixed arms emitted 3,884 and 13,494
  s2020/s2022 body rows respectively, but no s2008 positive-control row (the
  lone `n=0` helper row is not that control). This refutes the three s2024
  outcomes as written: no-LLE-only success, a common pre-1024 failure, and
  two phase-valid arms. It selects an inverse LLE/route split provisionally;
  the different wrappers and input schedules still confound LLE itself.
- The s2025 same-wrapper A/B isolated that split. With the same
  `tools/probe.sh`, eleven-Start schedule, binary, and passive controls, the
  forced-LLE arm reached VI 1024 at 14.5s and VI 512 at 26.6s; the HLE arm
  never reached VI 1024 in 120s and remained at VI 640. The LLE arm later
  hit the known PI `do_rom_read` crash at guest PC `0x80001B08`; the HLE arm
  had no crash. The LLE arm's phase-valid service census emitted 409 matched
  s2020/s2022 entries, all slot-0 status `0x00`, plus the real s2008 writer
  `0x8009B2C4` changing `0x01` to `0x00` during shutdown call 3. The HLE arm
  emitted only the non-control `0x8009BBF0` helper row. This selects H1:
  forced LLE is the route gate under the common wrapper; it does not show a
  status-3 interval or the worker-side clear path.
- The s2026 stale-gate diagnosis was corrected in s2027. The valid s2027
  unset/default-on versus `ROGUESQ_DRAIN_INLOOP_TICK=0` pair reached VI 1024
  and VI 512 in both arms and emitted the s2006 positive control. Both arms
  reached shutdown call 3 and recorded the same `0x8009B2C4` `0x01 -> 0x00`
  writer; both service tables remained status `0x00`/`zero_skip=1`, with no
  status-3 interval, worker entry, or `0x8009B7EC` store. This selects H2 of
  the planned table: the drain toggle is not the missing worker dispatch.
  The on arm and off arm later hit the known `do_rom_read` boundary at guest
  PC `0x80001B08`; that terminal crash is after the phase-valid table and does
  not erase the result. The first s2027 pair, which explicitly set the on arm
  to `1` contrary to the prescribed unset/default arm, is invalid and is not
  evidence.
- The s2028 A11 worker/status census passed its same-run controls: s2006
  service entry/exit emitted 24/24 rows, s2008 emitted five writer rows, and
  the A11 phase/width fields were live. In the phase-valid hangar row,
  shutdown call 3 entered with slot 0 at `0x01`; the game writer at
  `0x8009B2C4` changed it from `0x01` to `0x00` before the shutdown return.
  There was no status-3 read, shutdown spin, worker entry/store, or
  `0x8009B7EC` service-store row. The only worker-dispatch row targeted
  `0x8000569C`, not `serviceVoicePoolFrame` at `0x8009B5A8`. This selects H3:
  writer/reaper ordering pre-empts the status-3 interval in this port path;
  it does not authorize forcing the byte to zero. The capture later hit the
  known PI `do_rom_read` crash at guest PC `0x80001B08`, after the table was
  complete. A same-iteration retail-oracle run independently passed its
  whole-RDRAM control, reached the retail hangar route, and watched the
  corresponding `0x8009B2C4`/`0x8009B7EC` writer family.
- The s2029 regeneration-stable stop/reaper join passed its same-run controls:
  24 bounded s2006 controls, 393 service entries, five status-writer rows, and
  four stop call/entry/exit pairs. In the phase-valid call-3 row, direct site
  `0x8009BCD4` stopped slot 0 at record `0x80154620` with status `0x01`;
  `stopVoiceSlotSynced` then executed the sole `0x8009B2C4` `0x01 -> 0x00`
  writer before returning, and shutdown returned with status `0x00`. No
  status-3 scan, hidden writer, service entry/store, or `0x8009B3A8` call fired
  in that phase. This selects W1, legitimate writer/reaper ordering, for the
  observed port route; the terminal PI `do_rom_read` crash at guest PC
  `0x80001B08` occurred after the table. The independent s2029 retail oracle
  again passed its whole-RDRAM control, reached VI 1024 and hangar VI 512, and
  watched the exact status table and retail writer cluster.

## Active investigation and ranked next steps

1. **M5 opt-in RSP arm.** Execute step 2 of `M5-AUDIO-PLAN.md`: validate the
   existing `ROGUESQ_AUDIO_UCODE=1` arm against the unset stub in one build and
   phase-gated comparison. Require direct task dispatch/exit, DMEM canary,
   slot transition, and PCM nonzero/silence fields; do not promote the image
   or change default audio.
2. **M5 service store edge.** Park unless a future audio arm supplies a live
   slot-0 status-3 interval. If it does, use the existing s2022 store rows to
   join the worker clear path and proceed to the seven-site callback join.
3. **M5 callback-side PCM witness (only if #1 produces a task result).**
   Phase-gate a callback census at the exact two nonzero bridge rows. Do not
   infer a bridge defect from old rate-limited `pcm-sanity` rows.
4. **M3 crash work.** Only perform complete idiom-class audits with a named
   discriminator. The dormant `slotDispatcherIter+872` SIGBUS has 7659 clean
   hangar calls in the guarded run; do not add a mitigation. Revisit only with
   a mission-entry recipe or a new crash of that signature.
5. **Hangar visual artifact.** Malformed-triangle H2 is refuted by writer
   attestation; consumer-mode H1 is refuted by the RT64 census (single-source
   against pixel state). H3 remains unavailable because the oracle cannot
   screenshot the LLE path. Do not repeat the `0xD60` scan.
6. **Generated-symbol renaming sweep.** Remains parked until the M5 arm and
   any required status/PCM boundary are closed; do not use it to outrun the
   audio contract.

## Durable boundaries

**Generated-tree provenance.** The s2008 writer census is regeneration-stable
and its retail controls are valid. The s2016 run independently established
that the current 45-file generated tree reaches VI 1024 and hangar VI 512,
while the census emitted slot-0 rows. The exact s2007 snapshot and owner
authorization to reconcile companion files are therefore not prerequisites
for the port-side writer/thread join. The s2017 hold-based run adds a
crash-free late-route witness, but the join remains unevaluable because the
service positive control is absent. s2023's clean regeneration built, but its
forced-LLE recipe stalled at VI 640 or aborted in RT64 before VI 1024. s2024's
   fixed forced-LLE arm reached VI 1024, while its same-window direct no-LLE arm
   stayed at VI 640. s2025 then reproduced the split with the same wrapper and
   schedule, selecting forced LLE as the route gate; the LLE arm's later PI
   crash does not erase its earlier phase-valid census.

**M5 service dispatch boundary.** s2018 and s2019 close the static
registration/linkage and observed `get_function` arms. s2021 then supplied a
different same-run line: the direct target emitted 2,096 phase-valid entries
and exits, while the bounded pre-phase control remained zero. s2022 refined
that line: 1,988 entries/exits had a live `0x800A5121` gate and reached the
slot loop, but every observed slot-0 status was `0x00` and took the
`0x8009B630` zero-status skip; no independent `0x8009B7EC` store row fired.
The target's `ctx->r31` was zero on every sampled phase-valid entry, so no
guest caller can yet be attributed; `0xFFFFFFF8` is an invalid derived call
site, not a selected retail mismatch. This selects the port-side slot/status
predicate as the next boundary, not the gate or registration path. The
same-run result is port-side; the retail oracle independently proves that the
retail branch/loop and store PCs are executed, so the missing store is not a
retail-body absence. s2028 adds the finer port boundary: call 3's
`0x8009B2C4` writer changes slot 0 from `0x01` to `0x00` before the scan, so
the service's zero-status skip is downstream of a writer/reaper ordering
event, not an observed status-3 dispatch failure. s2029 then joined the
writer to its direct caller and stop body: call 3 uses `0x8009BCD4`, the slot
record is the same `0x80154620`, and `0x8009B2C4` performs the only call-3
transition before stop returns. This selects the legitimate W1 writer/reaper
contract for this route and parks the service-store edge until a live status-3
interval exists.

**M5 status transition.** Shutdown call 3 enters and returns in the s2007
capture. The s2012 and s2013 debugger-off retail oracles both reached VI 1024
and hangar VI 512, then observed slot 0 at `0x00`, `0x01`, `0x02`,
`0x03`, and `0x00` again. The s2022 debugger-on Rice oracle independently
recorded the retail branch/loop/store execution PCs and 15 writes to the
exact status word. The status-2 stop path legitimately writes `0x03` at
`0x8009B30C`, while `serviceVoicePoolFrame` (`0x8009B7EC` among its stores)
is the legitimate worker-side zeroing path. The value branch is settled;
   s2022 selects the port-side status-writer/read join because the port service
   reads zero before its skip and never reaches the store. The s2025
   phase-valid LLE arm adds the same-run route control: 409 service rows still
   read slot 0 as `0x00`, while the named `0x8009B2C4` writer records `0x01 ->
   0x00` during shutdown call 3. No status-3 service interval or worker store
   was observed, so the next boundary is the drain/shutdown writer ordering
   contract, not a permission to force the byte to zero. s2028's call-3 row
   supplies the first phase-valid join: the `0x8009B2C4` writer performs the
   `0x01 -> 0x00` transition before shutdown exits, with no intervening
   status-3 read. s2029 supplies the writer-side contract: the transition occurs
   inside `stopVoiceSlotSynced` reached from shutdown's `0x8009BCD4` call, with
   matching slot/address and stop before/after values. The absence of a status-3
   interval is therefore an observed ordering result, not permission to force a
   status value or skip the shutdown scan.

**M5 opt-in audio.** Both arms receive the same `M_AUDTASK` descriptor and
the selected image matches `aspMainTextStart`/`aspMainDataStart`. Treatment
DMEM writes are real image activity, not yet a corruption diagnosis. Two
nonzero `0x6F0`/`0x300` buffers match at the DMA writer and `queue_samples`;
the default dispatch and guest gates remain unchanged.

**M5 retail gate writers.** The s2014 whole-RDRAM control and debugger-on Rice
watch are both live: the control reached its 10,000-callback cap and the target
run reached VI 1024 and hangar VI 512. Retail PCs `0x8008EA34`/`0x8008EB40`
map to the named boot display-mode gate stores; repeated
`0x8008EB7C`/`0x8008EC88` map to the reapply pair, and `0x8008ED48` is the
zeroing path in the MusyX no-op/shutdown cluster. The logger does not expose
old/new bytes, so the exact values for the later PCs remain static-source
mapping rather than a new oracle field. This closes retail writer attribution,
not the port-side thread join.

**Drain and voice records.** The hangar table at `0x801714D0` has 18 live
voice records. `musyxRenderVoiceSamples` legitimately writes status `0x02`.
`desc+0x14` supplies loop length to `slot+0x40`; it is not a key-on flag or
sample rate. The host in-loop tick re-fades all 18 live voices and prevents
the diagnostic drain from idling when enabled. With it disabled, the ROM
drain returns and the later shutdown boundary is exposed.

**VI and frontend.** The active boot descriptor is the index-0 320 record;
`osTvType=1` maps to `rsViModeType=0`. VI 640-to-1024 is generated state plus
host VI submission. The s1942/s1949 spin results are archived in
`PROJECT-OVERVIEW.md` §36; do not repeat their A/B recipes.

**M4 accumulator and hangar beam.** Factor 5 reference data, paired combiner
evidence, VMADH/VGE capture, Rice watches, and generated DMEM-source analysis
rule out the old shade-lane theory. `L_17F0` restages a spec-accurate Fill
Triangle into DMEM `0xD60`; the observed `0xFFFF8000`/`0x00008000` values are
triangle X/Y. The hangar capture found no live Y=`0x8000` triangle. The beam
consumer census is coherent but is not pixel ground truth.

**M3 dispatcher.** The dormant `slotDispatcherIter+872` class has matching
caller/stack contracts and 7659 guarded hangar calls with zero invalid-SP
events. This is hangar-context evidence only; no guard or mitigation is
authorized by it.

**Overlay and rendering safety.** Factor 5 custom opcode mappings and the
oracle requirements are in `docs/F5-UCODE-REFERENCE.md` and
`tools/oracle/README.md`. Read them before interpreting a display-list or
RDP anomaly. The runtime's own null result cannot be its ground truth.

## Superseded conclusions

Detailed overturned claims are archived in `PROJECT-OVERVIEW.md` §§26, 35,
36, and 37. Important recent supersessions:

- s1888–s1917's “640 stall is a flaky crash family” was superseded by the
  two-source true-stall result at s1918.
- s1942–s1947's title-only and input-delivery explanations were superseded by
  the menu-input spin yield and s1949 hangar reachability result.
- s1975–s1992's successive audio-slot hypotheses were superseded by the
  voice-record, loop-length, fade, and in-loop-tick writer mappings.
- s1993–s1997's post-drain hypotheses were superseded by the shutdown call-3
  and service-worker boundary.
- s2006's “call 3 was not reached” was superseded by s2007; s2008–s2009 then
  established that the then-preserved snapshots were not phase-valid witnesses
  for the next status question. s2016 refuted the stronger claim that the
  current generated tree cannot provide a phase-valid census run: it reached
  VI 1024 and hangar VI 512, then emitted the existing status-writer rows.
- s2016's “the process crashed before the worker control” is superseded as a
  complete explanation by s2017's crash-free hold-based capture. The wording
  was believable because the earlier phase-valid run did die before the
  service rows; the fixed route now shows the more durable boundary is absent
  service dispatch, not merely an early crash.
- s2017's “registration/dispatch audit” work unit is superseded as a complete
  discriminator by s2018. The crosswalk refuted a static registration/linkage
  defect, but it had no incoming caller to distinguish unobserved runtime
  dispatch from an audio-gated path; the next unit must witness target
  resolution in the same phase-valid run.
- s2019's planned `get_function` discriminator is superseded as the next
  measurement because its two same-run controls were both zero. The null was
  believable because the target is a known runtime lookup boundary, but the
  direct service entry control fired pre-title and the phase gates were live;
  the next unit must witness the direct service entry and caller instead of
  treating an unexercised lookup helper as a map result. s2020 restated this
  formally: both the static (s2018) and indirect-dispatch (s2019) arms of the
  registration hypothesis are refuted; the direct-entry discriminator (D1-D4
  table in s2020/NEXT.md) is the required next measurement.
- s2020's direct-entry discriminator is superseded by s2021: the phase-valid
  target entry and exit fired, but the pre-phase control and `0x8009B7EC`
  store edge did not. The wording that a live phase-valid entry would move
  directly to the writer/thread join was believable because D1 was the
  intended live-path arm; the missing store is now the selected D4
  service-body boundary, and the next unit must distinguish the body gate from
  the slot/status predicate.
- s2021's generic “service-body boundary” is superseded as a complete
  explanation by s2022. The earlier wording was believable because the
  target entry/exit controls were live while the old store control was empty;
  the batched body census now shows the gate is nonzero and the loop is live,
  with slot 0 status `0x00` taking the zero-status skip on every sampled row.
  The next unit must identify the writer/read join for that status byte rather
  than add another service-entry witness.
- s2023's complete “the clean regenerated route cannot become phase-valid”
  explanation is superseded by the fixed s2024 A/B. It was believable because
  both s2023 recipe arms stopped before VI 1024 and lacked the s2008 control;
  the corrected same-window run reached VI 1024 in the forced-LLE arm. The
  direct no-LLE arm still stalled at VI 640, so the remaining issue was an
  unisolated LLE/route split rather than a universal phase failure. s2025's
  same-wrapper A/B is the superseding result: forced LLE reached VI 1024 and
  HLE remained at VI 640, selecting the LLE route gate. The earlier wording
  was believable because the wrappers differed; the common-wrapper control
  removes that confound.
- s2026's initial drain-tick pair is superseded as an A/B because binary-string
  inspection showed the executable did not contain the requested environment
  gate; the result was believable because the fixup script already documented
  the toggle, but the generated tree had not received that later fixup. The
  corrected rebuild then supplied a live tick-on arm, while tick-off crashed
  in `matchKeywordWithPriority+88` before its phase control, leaving H1–H4
  unselected rather than proving a status boundary.
- s2027 supersedes s2026's incomplete drain comparison. The first s2027 pair
  explicitly set the on arm to `1`, so it was invalid against the prescribed
  unset/default treatment. The corrected pair reached VI 1024/512 and the
  s2006 control in both arms; both reached shutdown call 3 and showed the same
  status-zero writer, while neither showed status 3, worker entry, or the
  service store. The earlier pre-phase-anchor wording was believable because
  the first corrected-looking arm did fail before VI 1024, but the fixed
  unset/default pair closes that route issue and selects the worker boundary.
- s2028 supersedes s2027's “worker boundary” as the complete explanation. The
  wording was believable because both s2027 arms lacked worker entry/store
  evidence while the service body was already known to read zero. The batched
  A11 table now shows the missing status-3 interval itself: call 3 starts at
  `0x01`, the named game writer `0x8009B2C4` changes it to `0x00`, and shutdown
  returns without a status-3 read. The next discriminator is the writer/reaper
  caller and slot contract, not another worker-entry witness.
- s2029 supersedes s2028's “writer/reaper ordering” as an incomplete
  explanation. That wording was believable because A11 already showed the
  `0x01 -> 0x00` writer before shutdown return, but it did not identify the
  caller or prove that the writer targeted the scanned record. The new table
  joins shutdown call 3, direct site `0x8009BCD4`, stop entry/exit, matching
  record `0x80154620`, and the sole `0x8009B2C4` store. It selects legitimate
  W1 ordering for this route and leaves the opt-in audio task/PCM contract as
  the next M5 discriminator.

## Evidence ledger summary

Per-session history through s1879 is in `PROJECT-OVERVIEW.md` §§33–35.
s1880–s1959 and the VI-1024 chain are in §36. s1961–s2009 are archived in
§37 and remain in `PORTING-STATE.md` as the primary ledger; s2011–s2013 record
the provenance block and its blocker-free retail status re-scope. s2014 adds
the phase-valid retail gate-PC capture and closes retail writer attribution;
the port-side join remains unresolved. s2016 refutes the provenance block while
leaving the join open. s2017 isolates the missing service positive control as
the next M5 boundary. s2018 refutes a static registration/linkage defect for
the base-text service function but leaves runtime target resolution open. s2019
shows that the chosen `get_function` witness mechanism and both its controls
were unexercised in the phase-valid port route. s2021 establishes direct
service entry/exit and s2022 refines the body/store boundary to the port
slot/status predicate because the gate and loop are live but every sampled
slot-0 status is zero. s2025 selects forced LLE as the route gate under the
common wrapper and leaves the port-side writer/read boundary at the drain /
shutdown scheduling question. s2028 closes the first A11 worker/status table
with H3: the call-3 `0x8009B2C4` writer changes slot 0 from `0x01` to `0x00`
before the scan, with no status-3 or service-store edge. The durable milestones
are: hangar reachability,
bltzal link repair, audio-drain writer mapping, M5 plan, opt-in DMA-to-queue
mapping, shutdown call-3 reachability, the repeated retail status-value
sequence, retail gate-writer attribution, and the unresolved port-side
writer/read join. s2026 adds the stale-gate diagnosis, s2027 completes the
corrected drain A/B, and s2028 selects the writer/reaper ordering boundary with
a phase-valid A11 table. s2029 closes the first writer/reaper join: the
call-3 stop caller, slot record, before/after status, and named guest writer
match, while no status-3/service-store edge is live. The retail oracle was
independently live in s2029, so the port census is not being used as its own
ground truth.

## Method and safety rules

- A null result is worthless without a same-run positive control. Batch all A/B
  arms in one build and run; scope counters to the VI phase; never compare
  animating scenes by stopwatch.
- Ask the retail oracle for ground truth before building an instrument. Arm
  its whole-RDRAM positive control first when debugger watches are enabled;
  debugger-off `--vi-poll` is the phase-valid route for status-table reads
  when PC watches stall at VI 640. Keep the two roles separate.
- Read `docs/F5-UCODE-REFERENCE.md` before reasoning about Factor 5 display
  lists. Regen in order: `make_elf.py`, N64Recomp, `fixup_game_funcs.py`,
  then CMake. Diagnostics in generated output must be fixed in the scripts.
- Kill runs with SIGKILL. Run from `build/` with the ROM present. Capture paths
  must not start with `.` in the final component.
- Do not run `git submodule update`, `git checkout -- lib/...`, `git clean`,
  or `git reset --hard`. If `lib/` changes, export submodule patches in the
  same iteration.
- A mitigation is not an explanation. Before adding a skip/guard/restore,
  name the writer and state whether the value is legitimate with `ORIGIN:`.
- Passive soak breadcrumbs belong in the soak queue; do not spend an
  iteration babysitting a repeat soak.
