# Rogue Squadron 64 Recomp — current truth

Front matter for [`PORTING-STATE.md`](../PORTING-STATE.md). Durable history is
in [`PROJECT-OVERVIEW.md`](PROJECT-OVERVIEW.md); the ledger is authoritative
for session detail. Reviewed through s2011 (2026-08-20).

## Current state

- Overlay dispatch is fixed enough for mission entry and post-sec2 outdoor
  presentation. The original boot/menu explanation is closed.
- Product multi-header freelist restore is ON. Garbage-CIMG and wrap-drop
  mitigations are OFF. Any future mitigation must carry an `ORIGIN:` naming
  its writer and stating whether the value is legitimate.
- The phase-gated baseline reached VI 1024 and hangar VI 512 in the known-good
  s844 and s1949-era recipes. The later 45-file generated snapshot reaches VI
  0, 320, and 640 but not 1024; the fresh 51-file tree crashes earlier. The
  status-table census is therefore blocked on generated-tree provenance, not
  on a status-value null.
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
  files and uncommitted companion/symbol edits; the s2009 retry exited while
  waiting for VI 1024. The status-writer census remains blocked on human input.

## Active investigation and ranked next steps

1. **M5 generated-tree provenance repair (human input required).** Obtain the
   phase-valid s2007 generated tree, including `funcs_*.c`, `funcs.h`,
   `recomp_overlays.inl`, and `lookup.cpp`, or explicitly authorize
   reconciliation of the four pending companion symbol files. The s2011
   read-only check found 45 current generated files and no phase-valid local
   artifact; `s2009-provenance.log` records that the process died while
   waiting for VI 1024. After the artifact or authorization arrives, force a
   full rebuild and rerun the existing phase-gated control. VI 1024 selects a
   usable baseline; another pre-1024 crash or VI-640 stall keeps the status
   census blocked. Do not change status, audio, spin, PI, or mitigation code.
2. **M5 status-table writer/transition census (only after #1).** Run the
   seven-site join of writer PC, slot/index, old/new byte, thread, shutdown
   call, and service/callback edge. Slot 0 `0x03` then clear selects
   transient-cleared; another slot selects other-slot; no `0x03` with live
   controls selects never-written. The retail oracle and `0x8009B7EC` writer
   are positive controls.
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
and its retail controls are valid, but neither candidate generated tree is a
phase-valid witness. A live VI-enqueue counter is only a positive control; it
does not substitute for the VI-1024 phase marker.

**M5 status transition.** Shutdown call 3 enters and returns in the s2007
capture. Its first sampled spin row is already status `0x00`; no status-3 row
was observed. The status-2 stop path legitimately writes `0x03` at
`0x8009B30C`, while `serviceVoicePoolFrame` (`0x8009B7EC` among its stores)
is the legitimate worker-side zeroing path. The transition cannot be
interpreted until a phase-valid generated tree runs the all-writer census.

**M5 opt-in audio.** Both arms receive the same `M_AUDTASK` descriptor and
the selected image matches `aspMainTextStart`/`aspMainDataStart`. Treatment
DMEM writes are real image activity, not yet a corruption diagnosis. Two
nonzero `0x6F0`/`0x300` buffers match at the DMA writer and `queue_samples`;
the default dispatch and guest gates remain unchanged.

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
  established that the current generated snapshots are not phase-valid
  witnesses for the next status question.

## Evidence ledger summary

Per-session history through s1879 is in `PROJECT-OVERVIEW.md` §§33–35.
s1880–s1959 and the VI-1024 chain are in §36. s1961–s2009 are archived in
§37 and remain in `PORTING-STATE.md` as the primary ledger; s2011 records the
current provenance block. The durable
milestones are: hangar reachability, bltzal link repair, audio-drain writer
mapping, M5 plan, opt-in DMA-to-queue mapping, shutdown call-3 reachability,
and the unresolved generated-tree provenance boundary.

## Method and safety rules

- A null result is worthless without a same-run positive control. Batch all A/B
  arms in one build and run; scope counters to the VI phase; never compare
  animating scenes by stopwatch.
- Ask the retail oracle for ground truth before building an instrument. Arm
  its whole-RDRAM positive control first, then use physical-address watches
  with PC attribution. The oracle currently reaches boot and attract only.
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
