# Rogue Squadron 64 Recomp — current truth

Front matter for [`PORTING-STATE.md`](../PORTING-STATE.md). Durable history is
in [`PROJECT-OVERVIEW.md`](PROJECT-OVERVIEW.md); the ledger is authoritative
for session detail. Reviewed through s2050 (2026-08-20).

## Current state

- Overlay dispatch is fixed enough for mission entry and post-sec2 outdoor
  presentation. The original boot/menu overlay explanation is closed.
- The known-good route reaches title VI `1024 @ 0x00790400` and hangar VI
  `512 @ 0x006AB400` when `ROGUESQ_SPIN_YIELD=1` yields both menu spins. Yield
  remains environment-gated and default-off.
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
- The stub audio arm returns `Broke` with no DMEM changes or audio DMA. The
  opt-in arm returns `Broke` after DMEM activity and audio DMA, including
  nonzero `0x6F0` payloads, but sampled PCM is still all-zero. The guest gate
  and its consumer remain the immediate contract boundary.
- Retail ground truth independently reaches title and hangar, passes the
  whole-RDRAM positive control, and executes the menu/audio/status watch
  points. The port is never its own witness for a null result.
- s2047's C88=1, forced-LLE, opt-in run reached title with live preflight,
  host-input, service, and audio controls, but not `menuControllerInput` or
  hangar VI 512. No bridge or PCM row from that run is admissible as a
  callback verdict.
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
- The generated-symbol sweep is effectively closed: the remaining 57
  placeholder names are genuine reverse-engineering holds or intentional
  non-sync entries, not a metadata sweep.

## Active backlog

This is the single monotonic backlog; historical item numbers in the ledger
are not active work items.

1. **M5 title-to-hangar route qualification.** s2050 selected G4: both C88
   arms stopped at VI 640 before the title anchor, despite host-input and
   caller controls. Re-establish a phase-valid title-1024 control with the
   spin-yield on/off route requalification in `NEXT.md`; do not interpret the
   C88 pair until one arm reaches title 1024. A live menu/512 request without
   the anchor selects a presentation handoff; both anchors make the PCM
   witness admissible.
2. **M5 callback-side PCM witness.** Only after item 1 is phase-valid, retain
   C88=1 and use the existing bridge/sanity table. Nonzero bridge bytes with
   `all_zero=0` selects upstream-valid PCM; nonzero bridge bytes with
   all-zero sanity selects the device boundary; zero bridge bytes selects the
   task/ABI boundary; no bridge with live gate/task controls selects guest
   submit/queue.
3. **M5 guest-gate value causality.** Keep the retail-value writer unchanged.
   The C88=1/unset split is repeatable port evidence but GUI/focus-confounded;
   revisit only with a genuinely focus-isolated, phase-valid discriminator.
4. **M5 service store edge.** Park unless an audio arm supplies a live
   slot-0 status-3 interval. Then use the existing store rows to join worker
   clear, slot ownership, and callback reachability.
5. **M3 crash work.** Only complete idiom-class audits with a named
   discriminator. The dormant `slotDispatcherIter+872` class has 7659 clean
   hangar calls in its guarded run; no mitigation is authorized.
6. **Hangar visual artifact.** Malformed-triangle H2 is refuted by writer
   attestation; consumer-mode H1 is refuted by the RT64 census. H3 remains
   unavailable because the oracle cannot screenshot the LLE path. Do not
   repeat the `0xD60` scan.
7. **Generated-symbol renaming sweep.** Park until M5 and any required
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

### M5 status and service

The current generated tree reaches title and hangar and emits the
regeneration-stable seven-site status census. The retail oracle independently
records the status sequence `00 -> 01 -> 02 -> 03 -> 00` and the retail writer
cluster. Static registration/linkage and the chosen indirect `get_function`
witness are closed explanations.

On the port, direct `serviceVoicePoolFrame` entry/exit and its gate/loop are
live, but sampled slot 0 is `00` and takes the zero-status skip. During
shutdown call 3, `stopVoiceSlotSynced` reaches the matching slot record and
the legitimate `0x8009B2C4` writer changes status `01 -> 00` before the scan
returns. No status-3/service-store interval has been observed, so the worker
store edge is parked. Do not force a status byte or add a skip.

### M5 audio and guest gate

The stock `aspMain` path is not the game's MusyX contract. The opt-in Factor 5
image arm is deliberately isolated behind `ROGUESQ_AUDIO_UCODE=1`; broad DMEM
activity is real but its image/task ABI is not proven. Two nonzero `0x6F0`
buffers match at the DMA writer and `queue_samples`; this does not establish
complete playback.

Retail executes the named display-mode writer cluster. The port fixup currently
records `0 -> 0` at `0x8008EC88`, and the raw gate consumer skips on zero. The
retail-value `1` arm remains opt-in and does not authorize changing the
legitimate guest writer. The repeated C88 A/B is single-source port evidence
with GUI arbitration unresolved. s2049's explicit C88=1 run recorded the
reapply writer and gate controls in the title phase, but still had no
`menuControllerInput` or VI 512; this is a route result, not causality for the
guest value.

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
  callback route. s2047 now reaches title but not hangar, so its bridge/PCM
  rows remain inadmissible. The active boundary is the title-to-hangar route,
  not a PCM null.
- s2050 did not overturn s2049's phase-valid single-arm observation: both new
  arms stopped before title 1024, so no C88 route comparison was admissible.
  The same-run controls make this a route/recipe failure, not evidence for
  either C88 polarity.
- The old “generated tree cannot provide a phase-valid census” provenance
  block is closed by s2016. The old “call 3 was not reached” claim is closed by
  s2007. The old “worker boundary is selected” wording is narrowed by s2028/
  s2029 to the observed legitimate writer/reaper ordering; the status-3 worker
  edge remains unmeasured.

## Evidence ledger summary

History through s1879 is in `PROJECT-OVERVIEW.md` §§33–35. The VI-1024 and
spin-yield chain is in §36. The M5 status/audio and route archive through s2047
is in §37–38 and remains in `PORTING-STATE.md` as the primary ledger.

Durable milestones are: overlay-dispatch recovery; hangar reachability;
bltzal link repair; audio-drain writer mapping; the M5 plan; opt-in
DMA-to-queue mapping; shutdown call-3 reachability; the retail status sequence
and writer attribution; the guest-gate boundary; and the unresolved
title-to-hangar and port-side writer/read joins. s2049 is the latest phase-valid
port observation: title yes, host input and controls live, hangar/menu handoff
no, PCM inadmissible. s2050's two arms were pre-title and therefore do not
replace that observation. Retail independently reaches both target anchors,
so this is not a retail-route absence.

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
