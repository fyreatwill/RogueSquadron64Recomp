# Rogue Squadron 64 Recomp — current truth

Front matter for [`PORTING-STATE.md`](../PORTING-STATE.md). Durable history is
in [`PROJECT-OVERVIEW.md`](PROJECT-OVERVIEW.md); the ledger is authoritative
for session detail. Reviewed through s2056 (2026-08-20).

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
- The stub audio arm returns `Broke` with no DMEM changes or audio DMA. The
  opt-in arm returns `Broke` after DMEM activity and audio DMA, including
  nonzero `0x6F0` payloads, but sampled PCM is still all-zero. The guest gate
  and its consumer remain the immediate contract boundary.
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
- The generated-symbol sweep is effectively closed: the remaining 57
  placeholder names are genuine reverse-engineering holds or intentional
  non-sync entries, not a metadata sweep.

## Active backlog

This is the single monotonic backlog; historical item numbers in the ledger
are not active work items.

1. **M5 service store edge.** The qualified C88=1 arm now supplies a live
   slot-0 status-3 interval. Add a regeneration-stable worker/store census to
   join the status-3 read, worker entry/exit, status-zero store, slot
   ownership, and callback reachability. Do not force a status byte or add a
   skip.
2. **M5 guest-gate handoff boundary.** H-R is selected at the current scope:
   C88 causally controls the raw gate, but not the title-to-hangar anchors.
   Revisit only with a genuinely focus-isolated discriminator that explains
   the menu callback-count difference; keep the retail writer unchanged.
3. **M3 crash work.** Only complete idiom-class audits with a named
   discriminator. The dormant `slotDispatcherIter+872` class has 7659 clean
   hangar calls in its guarded run; no mitigation is authorized.
4. **Hangar visual artifact.** Malformed-triangle H2 is refuted by writer
   attestation; consumer-mode H1 is refuted by the RT64 census. H3 remains
   unavailable because the oracle cannot screenshot the LLE path. Do not
   repeat the `0xD60` scan.
5. **Generated-symbol renaming sweep.** Park until M5 and any required
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
observed `0x03`; no status-zero worker store or clean reaping return was shown
in that run. During shutdown call 3, `stopVoiceSlotSynced` reaches the matching
slot record and the legitimate `0x8009B2C4` writer changes status `01 -> 00`
before the scan returns. The worker store edge is now unparked, but remains
unexplained. Do not force a status byte or add a skip.

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
the independent route qualification. PCM remained all-zero at the paired
source/consumer boundary in both arms.

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
- The old “generated tree cannot provide a phase-valid census” provenance
  block is closed by s2016. The old “call 3 was not reached” claim is closed by
  s2007. The old “worker boundary is selected” wording is narrowed by s2028/
  s2029 to the observed legitimate writer/reaper ordering; s2056 now measures
  a live status-3 interval, but the status-zero worker store remains
  unmeasured.

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
observed a live port status-3 interval. The C88 and callback conclusions are
single-source port evidence; the independent oracle supplied route/phase
ground truth. The status-zero worker store, task ABI, and complete playback
remain open. The oracle and port both independently reach both target anchors,
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
