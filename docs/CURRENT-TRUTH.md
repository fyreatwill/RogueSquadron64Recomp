# Rogue Squadron 64 Recomp — current truth

Front matter for [`PORTING-STATE.md`](../PORTING-STATE.md). Durable history is
in [`PROJECT-OVERVIEW.md`](PROJECT-OVERVIEW.md); the ledger is authoritative
for session detail. Reviewed through s2018 (2026-08-20).

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

## Active investigation and ranked next steps

1. **M5 runtime service-dispatch witness (unblocked).** The s2018 crosswalk
   refutes a static map/link defect but cannot observe an incoming call. Ask
   the retail oracle for a phase-valid execution watch at `0x8009B5A8` with a
   whole-RDRAM write control, then add one `get_function` target-resolution
   witness and run the existing phase-valid port recipe. Keep status, audio,
   spin, PI, guard, and mitigation behavior unchanged. A target resolve that
   returns the linked function and is followed by its entry selects a live
   service path; a target resolve with a missing/wrong map result selects a
   runtime map defect; a positive-control run with no target request, together
   with a retail PC hit and the existing audio-gate rows, selects an audio
   gate before dispatch. Do not run another status join until one row is
   selected.
2. **M5 port-side writer/thread census (blocked on #1).** Once the service
   control is live in the same run, use the existing seven-site join: writer
   PC, slot/index, old/new byte, host thread, shutdown call, service
   entry/exit, callback edge, and `0x8009B7EC`. Slot 0 `0x03` then clear
   selects transient-cleared; another slot selects other-slot; no `0x03` with
   live controls selects never-written.
3. **M5 callback-side PCM witness (only if #2 requires it).** Phase-gate a
   callback census at the exact two nonzero bridge rows. Do not infer a bridge
   defect from the old rate-limited `pcm-sanity` rows or change default audio.
4. **M3 crash work.** Only perform complete idiom-class audits with a named
   discriminator. The dormant `slotDispatcherIter+872` SIGBUS has 7659 clean
   hangar calls in the guarded run; do not add a mitigation. Revisit only with
   a mission-entry recipe or a new crash of that signature.
5. **Hangar visual artifact.** Malformed-triangle H2 is refuted by writer
   attestation; consumer-mode H1 is refuted by the RT64 census (single-source
   against pixel state). H3 remains unavailable because the oracle cannot
   screenshot the LLE path. Do not repeat the `0xD60` scan.
6. **M5 audio execution.** Continue only from `M5-AUDIO-PLAN.md`, after the
   provenance/status boundary is settled. The proven DMA-to-`queue_samples`
   mapping is not permission to promote the opt-in image.

## Durable boundaries

**Generated-tree provenance.** The s2008 writer census is regeneration-stable
and its retail controls are valid. The s2016 run independently established
that the current 45-file generated tree reaches VI 1024 and hangar VI 512,
while the census emitted slot-0 rows. The exact s2007 snapshot and owner
authorization to reconcile companion files are therefore not prerequisites
for the port-side writer/thread join. The s2017 hold-based run adds a
crash-free late-route witness, but the join remains unevaluable because the
service positive control is absent.

**M5 service dispatch boundary.** This is a single-source port observation
from three same-binary captures: the unconditional `serviceVoicePoolFrame`
entry/exit census and the named `0x8009B7EC` store control both remain at zero,
while VI 1024/512, shutdown call 3, and slot-0 `0x8009B2C4` rows fire. It
rules out a simple phase-gate or crash-before-worker explanation for those
captures, but does not yet distinguish missing registration, an unobserved
caller path, or an audio-side gate before the call. The s2018 source/binary
crosswalk independently shows that the function is base text, not an overlay:
the section-3 table entry and linked symbol are present, while no named caller
or direct host branch exists. This closes the static registration/linkage
variant only; runtime target resolution remains unobserved.

**M5 status transition.** Shutdown call 3 enters and returns in the s2007
capture. The s2012 and s2013 debugger-off retail oracles both reached VI 1024
and hangar VI 512, then observed slot 0 at `0x00`, `0x01`, `0x02`,
`0x03`, and `0x00` again. The status-2 stop path legitimately writes `0x03`
at `0x8009B30C`, while `serviceVoicePoolFrame` (`0x8009B7EC` among its
stores) is the legitimate worker-side zeroing path. The value branch is
settled in this single-source retail execution line; the port-side
writer/thread join now has a phase-valid generated-tree witness but remains
unselected.

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

## Evidence ledger summary

Per-session history through s1879 is in `PROJECT-OVERVIEW.md` §§33–35.
s1880–s1959 and the VI-1024 chain are in §36. s1961–s2009 are archived in
§37 and remain in `PORTING-STATE.md` as the primary ledger; s2011–s2013 record
the provenance block and its blocker-free retail status re-scope. s2014 adds
the phase-valid retail gate-PC capture and closes retail writer attribution;
the port-side join remains unresolved. s2016 refutes the provenance block while
leaving the join open. s2017 isolates the missing service positive control as
the next M5 boundary. s2018 refutes a static registration/linkage defect for
the base-text service function but leaves runtime target resolution open. The
durable milestones are: hangar
reachability, bltzal link repair, audio-drain writer mapping, M5 plan, opt-in
DMA-to-queue mapping, shutdown call-3 reachability, the repeated retail
status-value sequence, retail gate-writer attribution, and the unresolved
port-side writer/thread join.

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
