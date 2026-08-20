# Rogue Squadron 64 Recomp — current truth

Front matter for [`PORTING-STATE.md`](../PORTING-STATE.md). Durable history is
in [`PROJECT-OVERVIEW.md`](PROJECT-OVERVIEW.md); the ledger is authoritative
for session detail. Reviewed through s2046 (2026-08-20).

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
- s2030 completed the step-2 opt-in comparison with the independent retail
  gate control. The unset arm's phase-valid audio rows returned `Broke` with
  `dmem_changed=0`, `canary_ok=1`, and `dma_count=0`; the opt-in arm returned
  `Broke` after changing DMEM at `0x340..0xFCF`, failed the reserved-gap
  canary, and reached hangar VI 512 with audio DMAs, including two nonzero
  `0x6F0` payloads in its first hangar row. Both arms produced only all-zero
  PCM, and the phase-valid port gate read `0` with `musyx-gate1` taking its
  skip path. This selects the guest gate/consumer boundary as the immediate
  next M5 question; the image/task ABI remains unvalidated and the opt-in
  arm stays off by default.
- s2031 completed the phase-gated guest gate/consumer census. The retail
  oracle's whole-RDRAM control reached its 10,000-hit cap, retail reached VI
  1024 and the hangar VI 512 route, the physical `0xA0F50` watch recorded 17
  writes from the established `0x8008EA34`/`0x8008EB40` boot pair and
  `0x8008ED48`/`0x8008EB7C`/`0x8008EC88` transition cluster, and the
  `0x14998A` wait-word watch recorded zero writes. The fixed port run had
  24/24 s2006 controls, phase-valid `factor5_ucode_b` task/DMA rows at VI
  1024 and hangar VI 512, and all sampled PCM remained zero. In the target
  phases the named `reapplyDisplayMode` writer at `0x8008EC88` stored zero
  twice, while the raw gate consumer emitted 511 skip rows per target phase
  (`gate=0`, `branch=1`); gate-1 and wait consumers did not run. This closes
  the missing-control and wait-boundary explanations for this route. The
  port/retail value discrepancy at `0x8008EC88` remains the next question:
  the retail instruction sets `$v0=1`, while the existing port fixup forces
  that store to zero. No value was changed in s2031.
- s2032 completed the retail caller/order discriminator before any store
  change. The whole-RDRAM control reached its 10,000-hit cap, the physical
  `0xA0F50` watch recorded 17 writes, and retail reached the 1024-width title
  phase and 512-width hangar phase. The execution watches recorded ten hits
  each at `0x8008EB7C` and `0x8008EC88`; their local `exec-prev` rows were the
  expected `0x8008EB78`/self and `0x8008EC84`/self pairs. Together with the
  static site mapping, this selects the ordinary repeated reapply order (A)
  at the named sites over an alternate/late writer order (B). The narrow watch
  does not expose an external caller beyond the local predecessor/self pattern
  or report old/new byte values, so it does not authorize reversing the port's
  force-zero.
- s2033 completed the C88 value A/B with the independent retail control. The
  retail oracle again passed its whole-RDRAM control (10,017 writes), recorded
  17 physical `0xA0F50` writes and ten executions each at `0x8008EB7C` and
  `0x8008EC88`, and reached title `1024 @ 0x00790400` plus hangar `512 @
  0x006AB400`. The corrected port A/B used one build: the unset arm reached
  title `1024 @ 0x00790400`, passed 24/24 `s2006-svc` entry/exit controls, and
  emitted one phase-valid C88 writer row plus 511 raw-gate skip rows; the
  C88=1 arm passed the same 24/24 pre-phase service controls and 74 real audio
  task-dispatch rows but remained at VI 640 through a 75-second serial
  reproduction, with no phase-valid C88/raw-gate/task/PCM rows. The initial
  concurrent recipe was invalid because its comma-separated key list was not
  parsed by `probe.sh`; the corrected control also exposed a macOS frontmost
  race that prevented its hangar transition. This selects B: restoring the
  legitimate retail value at `reapplyDisplayMode` is destabilizing or
  insufficient on the port route before the downstream gate/task boundary.
  It does not prove the stall's mechanism or authorize changing the default.
- s2034 attempted the existing reachability witness in one same-build
  concurrent pair and then corrected single-window reruns. Every arm passed
  the required 24/24 `s2006-svc` entry/exit control and reached
  `reapplyDisplayMode` 2/2, but every arm stayed at VI 640 and produced no
  phase-valid VI-1024 title/hangar rows. The C88=1 arm's phase-6 PCM became
  nonzero while the unset arm stayed all-zero, but that downstream difference
  is not phase-valid. This is a common-route/recipe failure for s2034, not a
  selection between H1 and H2; the phase-valid s2033 B result remains active.
- s2035 explicitly cleared `ROGUESQ_M5_C88_VALUE` and reran the control with
  forced LLE, opt-in audio, spin yield, and the corrected eleven-Start
  schedule. The arm again stayed at VI 640, but its same-run controls were
  live: `s2006-svc` entry/exit was 24/24, `reapplyDisplayMode` was 2/2, and
  the driver produced post-640 SDL/host Start transitions. This provisionally
  selected H2, a common VI-640 route failure, over H3's missing-input-control
  explanation. s2036 supersedes that route selection; the C88 value A/B
  remains phase-invalid and unchanged.
- s2036 reran the unset-C88 arm through the preflighted, width-relative
  `tools/regress.sh` route. Input and visual preflight were both `ok`; the
  eleven scheduled Starts produced post-640 host edges, and the run reached
  title VI `1024 @ 0x00790400` at 13.9s and hangar VI `512 @ 0x006AB400` at
  22.3s. The same run emitted `s2006-svc` 24/24, two phase-valid
  `reapplyDisplayMode` writer rows, 111 logged real audio-task dispatch rows,
  and no crash. `regress_score.py` returned `FAIL` only because its final-key
  heuristic expected a transition after the last key at 23.9s, although both
  target transitions had already occurred; the phase/control table selects
  H1, route recovery, and supersedes the s2035 common-route explanation.
  The C88 value remains unset and the retail-value arm is still untested in a
  phase-valid A/B.
- s2037 ran the unset-C88 versus `ROGUESQ_M5_C88_VALUE=1` arms concurrently
  from one fresh build. Both preflights were `input=ok visual=ok`, both had
  post-640 host Start edges and 24/24 `s2006-svc` entry/exit controls, so the
  scorer's final-key FAIL is a harness heuristic rather than H4. The unset arm
  reached title VI 1024 but not hangar VI 512 in 90s; its phase-valid writer
  was `0 -> 0` and its 511 raw-gate rows were `gate=0, branch=1`. The C88=1
  arm reached title VI 1024 and hangar VI 512; its writer was `0 -> 1` in
  both target phases, with phase-8 raw/gate-1 rows and phase-10 raw/gate-1
  rows. Both arms logged 81 total audio-task dispatch rows and all observed
  target PCM samples were zero. This is an inverse route split against the
  planned H1/H2/H3 table, not a causal selection: it is single-source
  port-side evidence and concurrent GUI arbitration remains a confound. The
  next M5 unit must qualify reproducibility with a post-title schedule whose
  final key precedes the expected transition, then repeat the phase/control
  comparison without changing the writer.
- s2038 completed that post-title qualification from one fresh build. Both
  arms passed `input=ok visual=ok`, post-640 host-input edges, and 24/24
  `s2006-svc` controls. Unset-C88 reached title VI 1024 but not hangar: its
  writer was `0 -> 0`, its 511 phase-8 raw-gate rows were `gate=0,
  branch=1`, and its target PCM samples were all zero. C88=1 reached hangar
  VI 512: its writer was `0 -> 1` in both target phases and its phase-8 and
  phase-10 consumers took gate-1 rows; target PCM samples were still all
  zero. This reproduces the inverse route split at the phase/control level,
  but it remains single-source port evidence with concurrent GUI arbitration
  unresolved, so the retail-value store stays opt-in and unchanged. The
  C88=1 arm then hit the known RT64 `moveWord` assertion at guest PC
  `0x8000834c`, after the target table was live. The gate/task join is now
  sufficient for the callback-side PCM witness.
- s2039 could not make the callback-side PCM witness phase-valid. The initial
  five-Start C88=1 arm, a 90-second retry with the same schedule, and an
  eleven-Start arm all passed `input=ok visual=ok`, emitted five or eleven
  post-640 host Start edges, the 24/24 `s2006-svc` control, and real audio-task
  dispatch, but stayed at VI 640 with no title/hangar anchor and no
  `[pcm-bridge]` row. A same-schedule C88=1 control with `ROGUESQ_LOG_ALL`
  unset had the same VI-640 result. This is phase-valid positive-control
  evidence for H4 route failure, single-source port evidence; it does not
  select a PCM null or make the logging overhead the cause. The next M5 unit
  must compare C88=1 against the unset arm under the longer route schedule.
- s2040 completed that same-build eleven-Start comparison. The C88=1 arm
  reached title VI 1024 and hangar VI 512, passed the 24/24 service control,
  and produced `0 -> 1` reapply-writer rows plus gate-one consumer rows. The
  unset arm reached title VI 1024 but not hangar, passed the same service
  control, and produced `0 -> 0` plus 511 gate-zero skip rows. Both arms
  emitted real audio-task rows; the result is another inverse, single-source
  port split with concurrent GUI arbitration unresolved. It does not select
  the planned route hypotheses, but the C88=1 arm is phase-valid for the
  callback-side PCM witness.
- s2041 ran the C88=1 callback-side witness with forced LLE, opt-in Factor 5
  audio, and all passive controls. Preflight was `input=ok visual=ok`; the
  run reached title VI `1024 @ 0x00790400` at 14.0s but never reached the
  hangar VI `512 @ 0x006AB400` anchor. The scorer marked the route FAIL because
  the width-640 keys fired without a following VI transition, so this is H5
  route failure rather than a PCM verdict. The controls were live: 24/24
  `s2006-svc` entry/exit pairs, 123 real audio-task rows, one phase-8
  `0 -> 1` writer row, 116 phase-8 gate-one rows, 88 phase-8 bridge rows
  (19 with `nz=768`), and 40 phase-8 `pcm-sanity` rows all with
  `all_zero=1`. No phase-10 rows existed; title-only PCM rows are not
  interpreted. The next arm uses the known title-to-hangar phase-relative
  schedule.
- s2042 ran the title-to-hangar width-1024 key schedule once, then reran a
  fixed form that retained those keys while extending the eleven-Start route.
  Both C88=1 arms reached title VI `1024 @ 0x00790400` but neither reached
  hangar VI `512 @ 0x006AB400`; the raw phase rows and verdict transitions
  agree on the missing anchor. Both had live 24/24 `s2006-svc` controls, real
  audio-task rows, the `0 -> 1` writer, gate-one rows, callback bridge rows,
  and PCM sanity rows. The host input witness saw all title A/Start events,
  so the scorer's “undriven” wording is contradicted by same-run input
  evidence. This is H5 route failure, not a PCM result; the next unit must
  isolate the title-to-hangar route with a phase-gated `probe.sh` schedule.
- s2043 ran that C88=1 route arm with a phase gate, then its required fixed
  form with the documented boot-relative eleven-Start schedule. The initial
  arm never opened VI 1024, and the fixed arm also stopped at VI 640 origin
  `0x00696100`; the fixed arm nevertheless logged 11/11 `pad-host` Start rows
  at width 640, `reapplyDisplayMode` 2/2, and the existing 24/24 service
  controls. It also reached `waitForAnyAudioSlot` once before title, while no
  VI-1024 or VI-512 anchor appeared. An independent retail-oracle control
  passed its 10,000-hit whole-RDRAM positive control and reached title 1024 at
  17.3s plus hangar-origin 512 at 38.4s. This rules out missing host Start
  delivery as the complete explanation for the port's pre-title stop, but it
  does not select the guest menu route versus the opt-in-audio wait boundary;
  bridge and PCM rows remain inadmissible. The next M5 unit is the
  `waitForAnyAudioSlot` audio-arm discriminator.
- s2044 ran that discriminator from one build. Both port arms reached the same
  VI-640 `waitForAnyAudioSlot` caller and passed 24/24 service controls, but
  neither reached VI 1024 or 512. The opt-in arm had 11 host Start rows and
  the stub arm 2, so the stub input control was live but shallower. W2 is
  selected (shared pre-title route); input depth/focus remains a confound and
  phase-invalid PCM is ignored.
- s2045 ran the required same-build pair with the new post-wait census. The
  independent retail oracle passed the whole-RDRAM control, reached title 1024
  and hangar 512, and hit the three requested execution watches: one each at
  `runMenuModelViewerScreen` and `menuControllerInput`, plus 5154 at
  `anyAudioSlotActive`. On the port, both audio-on and stub arms passed the
  post-wait positive-control rows and logged the complete sequence:
  `runMenuModelViewerScreen` entry/return, `waitForAnyAudioSlot`
  entry/loop/branch/return, and `menuOverlayInit` post-wait return/branch.
  Both still stopped at VI 640 with no title or hangar anchor. The wait loop
  sampled different pump counts (`0xE6` audio-on versus `0x72` stub), but its
  return and post-wait branch values matched. This selects P1, a shared
  post-wait route boundary, over an audio-arm-specific continuation or a
  missing wait return; it is single-source port evidence, with the retail
  watch only confirming that the corresponding retail path is live. Audio-on
  PCM became nonzero later while stub PCM stayed all-zero, but that is after
  the shared route and is not a callback verdict. Input depth/focus remains a
  confound.
- s2046's retail oracle passed its 10,000-write control, both target VI
  anchors, and all three execution watches. After fixing an invalid circular
  VI-1024/key gate, the VI-640-gated port pair passed input in both arms
  (7 `[pad-host]` rises each) and produced identical caller tables through
  `menuOverlayInit` return, with no `menuControllerInput`, service row, VI
  target, or PCM-admissible phase. The shared three-row VI producer control
  and matching edges select Q4, a guest-to-VI handoff boundary, over an
  audio-specific continuation or missing wait return.
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

1. **M5 phase-valid route qualification.** s2046 found identical
   post-wait caller/return edges and matching input/VI-producer controls in
   both arms, but no `menuControllerInput`, service rows, or target VI. The
   next unit must use the existing caller table with the whole-pass
   `tools/regress.sh` phase scheduler and a known width-640-to-1024-to-512
   key schedule, with no new wait counters. A live 1024 request/anchor moves
   the boundary to the callback-side PCM witness; a continued common 640 route
   keeps the shared handoff open. No bridge or PCM result is admissible
   without both target VI anchors.
2. **M5 callback-side PCM witness.** Once the route is phase-valid, keep
   `ROGUESQ_M5_C88_VALUE=1` opt-in and use the existing bridge/sanity table.
   Nonzero bridge bytes plus `all_zero=0` selects upstream-valid PCM;
   nonzero bridge bytes plus all-zero sanity selects the device boundary;
   zero bridge bytes selects the task/ABI boundary; no bridge with live
   gate/task controls selects guest AI submit/queue.
3. **M5 gate-writer value causality.** Keep `ROGUESQ_M5_C88_VALUE=1` opt-in
   and the retail-value writer unchanged. The phase-valid s2038 split is
   now reproduced in s2040, but remains single-source because both arms
   shared GUI focus and the unset arm lacked the hangar anchor. Revisit only
   with a genuinely focus-isolated discriminator, not another reactive store
   reversal.
4. **M5 service store edge.** Park unless a future audio arm supplies a live
   slot-0 status-3 interval. If it does, use the existing s2022 store rows to
   join the worker clear path and proceed to the seven-site callback join.
5. **M3 crash work.** Only perform complete idiom-class audits with a named
   discriminator. The dormant `slotDispatcherIter+872` SIGBUS has 7659 clean
   hangar calls in the guarded run; do not add a mitigation. Revisit only with
   a mission-entry recipe or a new crash of that signature.
6. **Hangar visual artifact.** Malformed-triangle H2 is refuted by writer
   attestation; consumer-mode H1 is refuted by the RT64 census (single-source
   against pixel state). H3 remains unavailable because the oracle cannot
   screenshot the LLE path. Do not repeat the `0xD60` scan.
7. **Generated-symbol renaming sweep.** Remains parked until the M5 arm and
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

**M5 width-relative route control.** s2035's unset-C88 control was not a
complete common-route failure. s2036 passed both preflight checks, produced
post-640 host Start edges, and reached the title and hangar anchors under the
same forced-LLE/opt-in-audio configuration. s2037 then showed an inverse
single-source split, but its final scheduled key followed the relevant
transition. s2038 fixed that schedule: both arms passed the input/visual and
post-640 controls, the unset arm reached title, and C88=1 reached hangar with
the matching `0 -> 0`/gate-zero versus `0 -> 1`/gate-one table. The unset
scorer FAIL is therefore not an H4 selection. The split is reproducible as a
port observation but not yet a causal store explanation because concurrent GUI
arbitration remains live. s2040 reproduced the same shape with both arms
passing 24/24 service controls, C88=1 reaching both target phases, and unset
reaching title only. The next boundary was the callback-side PCM census, using
the phase-valid C88=1 arm. s2041 and s2042 then showed that a single C88=1 arm
can stop at title despite live host input and title-side controls; s2042's
fixed schedule added more Start events without producing VI 512. The next
boundary is therefore route isolation, not a writer reversal or PCM
interpretation.

**M5 shared pre-title route.** s2044's same-build opt-in/stub pair both
reached the `waitForAnyAudioSlot` call, `menu-exit`, and mission handoff at
VI 640, with 24/24 service controls; neither reached VI 1024 or VI 512. The
opt-in arm had 11 host Start rows and the stub 2, so the shared route is
selected but input depth is not equivalent. This is a route boundary, not
evidence that the wait itself spins or that the audio image is valid.

**M5 post-wait route boundary.** s2045's same-build census was positive in
both arms: each entered and returned from `waitForAnyAudioSlot`, and each
reached the same `menuOverlayInit` post-wait return/branch rows before
stopping at VI 640. The loop's sampled pump count differed (`0xE6` versus
`0x72`), but the observed return/branch values did not. This closes the
missing-return and arm-specific-postwait hypotheses for the measured path;
the caller/route edge after that branch remains open. The retail oracle's
execution watches are an independent path-live control, not proof of the
port's caller identity. s2046 added the missing static caller/return identity
in a regeneration-safe table. After correcting the circular 1024 gate, both
arms had the same six caller rows, seven input rises, and three VI-producer
rows, but no `menuControllerInput`, service row, or target anchor. This
selects a shared guest-to-VI handoff boundary (Q4) and closes the measured
audio-specific-continuation and missing-wait-return explanations; it does not
make the service or PCM null phase-valid.

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

**M5 opt-in RSP boundary.** s2030's final same-build route pair passed the
same 24/24 `s2006-svc` entry/exit controls. The stub arm reached VI 1024 but
not hangar 512; its phase-valid row had `arm=musyx_stub`, `exit=1` (`Broke`),
`dmem_changed=0`, `canary_ok=1`, and `dma_count=0`. The opt-in arm reached
VI 1024 and VI 512 at origin `0x006AB400`; its phase-valid rows had
`arm=factor5_ucode_b`, `exit=1`, DMEM changes beginning at `0x340` and
extending through `0xFCF`, `canary_ok=0`, and audio DMA rows. Its first
hangar row included two nonzero `0x6F0` payloads, but all sampled
`pcm-sanity` rows in both arms had `all_zero=1` and no `all_zero=0` row fired.
The phase-valid port gate witness read byte `0` and `musyx-gate1` took its
skip path; the independent s2030 retail oracle passed 10,011 whole-RDRAM
writes, reached VI 1024, and recorded the established `0xA0F50` writer PCs.
The s2031 same-run census then supplied the missing gate controls: 24 s2006
controls, two phase-valid `0x8008EC88` writer rows, 511 raw-gate skip rows in
each target phase, and phase-valid opt-in task/DMA rows. The gate-1 and wait
consumers were not reached because the raw gate stayed zero. This rules out
an incomplete-control or wait-boundary interpretation for the observed route
and selects the existing `0x8008EC88` force-zero versus retail-value contract
as the next discriminator. The canary/PCM result leaves the MusyX image/task
ABI unproven; it is not a mitigation or permission to skip the gate.

**M5 guest gate/consumer contract.** s2031's retail oracle and port census
are independently phase-valid. Retail executed the exact writer cluster,
including `0x8008EC88`, while the port's phase-valid writer row reported
`0 -> 0` at that site; the generated MIPS sequence immediately before the
retail store sets `$v0=1`, and the current fixup intentionally replaces the
store with zero for the stubbed engine. The port raw consumer then read zero
and took its skip branch 511 times in each title/hangar target phase. No
gate-1 or wait row fired, while the opt-in task returned through the
Factor-5 arm and PCM stayed zero. This selects the writer/value divergence
as the next M5 boundary, not a missing wait consumer or a missing positive
control. The store remains unchanged pending caller/order tracing.

s2032 then supplied the named-site order line: the retail execution watch saw
the repeated `0x8008EB7C`/`0x8008EC88` pair with the expected local
predecessor/self histogram in both sites, while the independent whole-RDRAM
and physical-byte watches were live through title and hangar. This selects the
ordinary reapply order at the named sites; it leaves any external caller
detail, the retail byte value, and the port-side consumer outcome for the
one-writer C88 A/B.

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
- s2030 supersedes the ranked step-2 opt-in validation as the next unit. The
  wording was believable because the existing arm had only been attributed
  by dispatch and DMA probes; the same-build phase table now proves normal
  `Broke` returns and real DMEM/DMA activity, but no nonzero PCM, while the
  guest gate remains zero and skipped. s2031 supersedes that next-unit choice:
  its retail and port phase controls are live, the port writer at
  `0x8008EC88` records `0 -> 0`, and the raw consumer takes the zero branch;
  the remaining question is the existing force-zero versus the retail store
  value and caller/order, not whether the gate census was exercised. The
  image/task ABI remains open rather than being promoted or blamed from a
  single null.
- s2032 supersedes s2031's caller/order uncertainty as the complete next
  question. That uncertainty was believable because s2031 had only static
  value mapping and port-side rows; the live retail oracle now records the
  repeated `0x8008EB7C`/`0x8008EC88` execution cluster with its expected local
  predecessor/self pattern and all phase controls. The remaining discriminator
  is the value arm itself, not an alternate writer path. The oracle still does
  not expose old/new bytes, so this does not reverse the store by itself.
- s2033 supersedes s2032's one-writer A/B as the active next question. The
  wording that the value arm could be judged from downstream gate/task/PCM
  rows was believable because the unset control reached the title census and
  the retail site is live. The corrected A/B instead found a repeatable
  C88=1 VI-640 stall with the same pre-phase controls and no downstream
  phase-valid rows; the next measurement must locate the stall relative to
  `reapplyDisplayMode`, not reverse another gate or infer a PCM null.
- s2034 does not supersede s2033's selected B result: its concurrent and
  single-window arms all failed the VI-1024 phase anchor, even though the
  required service and reapply controls fired. The new wording is limited to
  a common-route/recipe failure because the control was not phase-valid; the
  next unit must qualify that control before interpreting writer reachability.
- s2035 supersedes s2034's control-qualification wording as the immediate
  next question. That wording was believable because s2034's concurrent and
  corrected single-window arms were both phase-invalid. The explicit `env -u`
  control now repeats the VI-640 stall while its service, reapply, and
  post-640 host-input controls are live, selecting a common route boundary
  and ruling out an inherited C88 arm or a missing input positive control.
- s2036 supersedes s2035's common-route explanation as a complete result. The
  wording was believable because s2035 had the same service, writer, and
  host-input controls but no VI-1024 anchor. The preflighted width-relative
  run now reaches VI 1024 and VI 512 with those controls live; the harness
  FAIL is explained by its final-key-after-transition heuristic. The C88=1
  arm still needs a same-build phase-valid comparison.
- s2037 supersedes s2036's expectation that the unset arm is a sufficient
  control for a straightforward value A/B. That expectation was believable
  because s2036 reached both title and hangar anchors with live controls, but
  the concurrent same-build pair instead reached hangar only in the C88=1 arm
  and showed the matching gate-zero versus gate-one split. Because the result
  is single-source port evidence and concurrent GUI arbitration remains a
  confound, it does not select an inverse causal story or authorize changing
  the writer; the next unit is a post-title schedule qualification.
- s2038 supersedes s2037's immediate next-unit wording that a post-title
  schedule still had to qualify whether the inverse split could be observed.
  That wording was believable because s2037's final key came after its
  relevant transition and its scorer reported an input failure. The corrected
  schedule reproduced the phase-valid writer/gate split with both preflight and
  post-640 host controls, while C88=1 reached hangar before a known RT64
  `moveWord` assertion. The result remains single-source and concurrent-focus
  confounded, so it does not reverse the legitimate writer; the next unit is
  the existing callback-side PCM census.
- s2039 supersedes s2038's immediate callback-census wording as a runnable
  next step. That wording was believable because the C88=1 arm had reached
  the phase-10 gate in s2038, but the fresh five-Start, 90-second retry, and
  eleven-Start arms all stopped at VI 640 with live service/audio controls;
  the no-`LOG_ALL` control stopped there too. This leaves the callback
  question unmeasured and promotes the C88=1 versus unset route comparison.
- s2040 supersedes s2039's immediate route-retry wording. The retry was
  believable because all three s2039 C88=1 attempts stopped at VI 640 with
  live pre-target controls. The fresh same-build pair instead reached both
  target phases in the C88=1 arm and title in the unset arm, with the expected
  writer/gate split, so the C88=1 callback witness is runnable again. The
  inverse split remains single-source and GUI-focus confounded; it is not a
  causal authorization to change the writer.
- s2041 supersedes the unqualified claim that the eleven width-640 schedule
  is sufficient to make the C88=1 callback witness phase-valid. The wording
  was believable because s2040's C88=1 arm reached title and hangar with the
  same schedule, but the fresh single arm reached title only and the scorer
  recorded a missing post-key VI transition. Its title-side controls proved
  the instrument was live, not that the PCM boundary was reached. The next
  recipe adds the known title-to-hangar width-1024 key schedule and keeps the
  no-PCM-interpretation rule until both anchors exist.
- s2042 supersedes the claim that adding the known width-1024 key schedule is
  sufficient to make the callback witness phase-valid. That claim was
  believable because the schedule was the documented correction after s2041;
  the fresh arm and its extended eleven-Start rerun both reached title only.
  `pad-host` recorded the title A/Start events in both runs, while the raw
  `[phase]` rows and verdict transitions independently showed no VI-512
  anchor. The regress scorer's undriven diagnosis is therefore not selected;
  the next unit must isolate the route wrapper or guest title-to-hangar
  boundary.
- s2043 supersedes s2042's immediate post-1024 route-isolation recipe as the
  next measurement. That recipe was believable because s2042 had a title
  anchor and live host A/Start rows, but the fresh phase-gated arm never
  reached title; its fixed boot-relative form supplied the missing input
  control and still stopped at VI 640 inside `waitForAnyAudioSlot`. The result
  promotes the opt-in-audio wait boundary without selecting its cause; no
  PCM or writer-value conclusion follows.
- s2044 supersedes the claim that the wait caller is audio-arm-specific: the
  same-build pair reaches the same wait/menu/mission sequence in both arms.
  The stub's two versus opt-in's eleven host Start rows leave input depth as a
  confound; next is the post-wait branch census, not a PCM or writer change.
- s2045 supersedes the claim that the post-wait boundary was unmeasured. The
  new census had positive controls in both arms and observed wait entry,
  return, and the same `menuOverlayInit` post-wait branch. This closes the
  missing-return and audio-arm-specific-continuation explanations for the
  measured path; the caller/route edge after that branch remains unmeasured.

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
s2030–s2033 closed the opt-in task/guest gate census and selected the
phase-valid C88 writer A/B as the next boundary; the original writer value
remains legitimate guest state and the opt-in arm remains off by default.
s2034–s2038 qualified and repeated that A/B, producing a single-source,
GUI-confounded inverse route split and making the C88=1 callback PCM witness
the next boundary. s2039–s2042 showed that witness was not phase-valid on
fresh C88=1 routes despite live input, service, task, gate, bridge, and PCM
controls; no PCM conclusion follows. s2043 then selected the pre-title
audio-wait boundary after a fixed eleven-Start control. s2044 showed both
audio arms share the VI-640 wait/menu/mission route, with input depth still a
confound. s2045 added positive post-wait entry/return/branch rows in both
arms and selected the shared post-wait route boundary (P1); the later
arms and selected the shared post-wait route boundary (P1); s2046 then
joined static caller/return edges and selected the common guest-to-VI handoff
boundary (Q4) after a corrected VI-640-gated key control. The later
audio-on/nonzero versus stub/all-zero PCM split remains phase-invalid.

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
