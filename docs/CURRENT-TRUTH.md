# Rogue Squadron 64 Recomp — current truth

Compact operational handoff, maintained at Session 5577 (2026-10-19).
`PORTING-STATE.md` is the chronological ledger. Durable background and the
archived renaming sweep are in `docs/PROJECT-OVERVIEW.md`; per-session
evidence is in the named `docs/*AUDIT.md` files and soak results.

## Headline

The qualified image route boots through attribution, N64 logo, intro, Factor 5
logo, title (`0x00790400`, VI 1024), hangar (`0x006AB400`, VI 512), and mission
origins (`0x00690400` and later `0x00620400`, VI 512). Mission input reaches
flight code and changes the vehicle state. The default audio route is active;
`ROGUESQ_AUDIO_UCODE=0` is the silent control.

The M6 keyed mission endurance gate is now closed: two independent runs reached
mission only after a preceding hangar origin and held for the requested 900 s.
Run s5394b held 904 s and s5394c held 900 s; both stayed alive, recorded zero
30-second VI-origin stalls, and emitted zero crash/abort markers. This is route
endurance evidence, not proof that every mission subsystem or render artifact is
correct.

M5 audio de-stubbing is closed for the qualified route. The image arm produces
nonzero PCM, completes its task/SP contract, reaches title/hangar/mission, and
passed the keyed mission runs plus the long mission hold. The silent arm
remains a same-build rollback/control. Details and validation rows are in
`docs/M5-AUDIO-PLAN.md` (especially s4963/s4968).

The M4 accumulator comparison remains parked at the cross-arm gate. Session 5575
tested a new phase/image/mapped-PC/task-total event-shape key. Both arms passed
all four controls and both had active lane rows, but zero key classes joined
(retail 656 classes, port 6). H3 remains selected: the task-total bucket is not
portable, so no writer or value conclusion follows. Session 5570
relaxed the nonportable phase/image/progress join by pairing ordered groups and
binning within-group ranks. Both mapped PCs aligned one group and 16/16 bins,
but every lane mask was empty in both arms; this is an absent discriminator, not
evidence of agreement. Session 5562
implemented and qualified the image/progress-bearing retail schema: the oracle
arm emitted 941,343 normalized rows with whole-RDRAM, VI, mapped-PC, and image
controls. The existing port capture is legacy and emitted zero rows, so the
batched comparison selected H3; no writer or mitigation is inferred. The next
discriminator is the matching port schema (phase epoch, image identity, mapped
IMEM PC, task-local progress/end) before another comparison. Details of
s5321-s5395 are archived in `docs/PROJECT-OVERVIEW.md` (CURRENT-TRUTH
compaction).

Session 5577 reran the repaired lldb-attach plume loop on the qualified default
route with a 120-second per-attempt title gate. The injected SIGSEGV positive
control passed; all four game attempts stayed at `phase=3`, width 640, origin
`0x696100`, with zero title-origin controls, zero lldb crash stops, and zero
plume breadcrumbs. The earlier 45-second pass was also too short to reach the
known ~80-second title transition. This selects the attach/tooling reachability
hypothesis for this recipe, not plume absence: stop repeating lldb and use the
in-process crash handler on the next unit.

Session 5574 audited `fake_func_800AE3E4`. The generated tree and independent
syms table agree on its exact 12-byte placeholder span, while the companion
maps provide no semantic mission name and show overlapping overlay context at
`0x800AE3EC`. H2 selected: it is a non-callable/data-gap fragment and remains
unchanged. The generated-symbol sweep is exhausted; the M4 boundary revisit is
now parked after two new schema attempts. The next unit returns to M6's
secondary title-boot plume question under lldb.

Session 5573 audited the next remaining generated placeholder,
`fake_func_8006ACA4`. The generated tree is already synchronized to
`data_gap_8006ACA4`; its exact 12-byte span is a non-callable fragment before
`transformObjectColliderCenter`, and the independent syms table agrees. H2
selected; no rename or runtime change is authorized. The next candidate is
`fake_func_800AE3E4`.

Session 5572 audited the next remaining generated placeholder,
`fake_func_8000337C`. The generated tree is already synchronized to
`data_gap_8000337C`; the companion map explicitly calls its exact 4-byte span
a non-callable fragment before `setVideoReadyFlag`, and the independent syms
table agrees. H3 selected; no rename or runtime change is authorized. The next
live placeholder by address is `fake_func_8006ACA4`.

Session 5571 audited the first remaining live generated placeholder,
`fake_func_800027B8`. Its two-instruction span is a non-callable fragment
between `getOsResetType` and `processPolledControllerData`; the companion map
and independent syms table agree on the exact 8-byte `data_gap_800027B8` span.
H2 selected; no rename or runtime change is authorized. The next candidate is
the following live placeholder after checking synchronization surfaces.

## Durable state

- **RSP task-entry null-contract guard (s5395).** The two public task callback
  entrypoints now reject a null `OSTask` before dereferencing it. The writer is
  the host runtime callback boundary (`recomp::rsp::run_task`); null is not a
  legitimate guest task value. Debug compilation passes. The direct null arm
  has no in-game harness, so reachability remains a static contract result.

- **SDL_QUIT shutdown (s5382, verified).** The `quick_exit` fix works: old binary rc=134 SIGABRT, new rc=0 on the same SIGTERM->SDL_QUIT recipe (`tools/verify_sdl_quit.sh`). Closed.

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
  HI/LO, MMIO-KSEG1 lui bases (s5350, `docs/M3-MMIO-LUI-AUDIT.md`), delay-slot operand hazard (s5345, `docs/M3-DELAY-SLOT-HAZARD-AUDIT.md`), 64-bit shift, 32-bit multiply, 64-bit mul/div, and relevant pointer
  idiom classes are closed. Re-open only with new recompiler or provenance
  evidence, and audit a whole idiom class rather than a single crash.
- **M3 `$sp` adjustment balance (s5558).** A whole-tree census found 4,854
  generated self-adjustments across 1,751 functions. After collapsing the
  duplicated delay-slot epilogues, 1,727 functions balance; the 24 remaining
  candidates are intentional non-returning workers or invalid/data-gap
  fragments. No reachable ordinary function has an unmatched frame adjustment.
  See `docs/M3-SP-ADJUSTMENT-AUDIT.md`.
- **M3 late `$ra` writes (s5559).** A whole-tree census found 25 raw rows
  around `jr $ra`; all collapse to invalid/data-gap material, Factor 5 voice
  `bltzal`/delay-slot fragments, or one intentional computed/tail return.
  The ordinary saved-`ra` control is intact; no reachable ordinary function
  clobbers a saved return address after its last call. See
  `docs/M3-RA-RETURN-IDIOM-AUDIT.md` and
  `tools/audit_ra_return_idiom.py`.
- **M3 `$at`/`r1` branch joins (s5560).** The whole-tree census found 2,681
  multi-predecessor joins and 413 touching `$at`; 25 apparent use-before-write
  candidates all belong to explicit data-gap/invalid records or malformed
  cross-function fragments. The ordinary `loadOverlay` join control fired and
  no reachable complete function remained. See
  `docs/M3-AT-BRANCH-JOIN-AUDIT.md` and
  `tools/audit_at_branch_join.py`.
- **M3 conditional moves (s5561).** The whole-tree census found 179 `movz`/
  `movn` occurrences at 149 guest PCs: 115 exact guarded translations and 64
  `$zero`-destination discards, with zero condition, assignment, or missing
  translation mismatches. The ordinary and invalid/data-gap positive controls
  passed. See `docs/M3-CONDITIONAL-MOVE-AUDIT.md` and
  `tools/audit_conditional_move.py`.
- Native hangar artifacts remain localized: rim band, holo spikes, stale right
  edge, Factor 5 overlay splice, accumulator origin, pillar references,
  `0x1F0D74`, and odd PI DMA are parked. No mitigation is authorized without
  naming the writer and establishing value legitimacy.
- The retail-entry byte thread was resolved as a port census byte-swizzle bug;
  it is not a current divergence. The retail-entry and M4 accumulator
  revisits remain parked unless a genuinely new discriminator appears.
- Heap/copy/message-queue/PI-DMA and audited host-wrapper pointer classes are
  closed on the qualified route with positive controls. The fresh MIPS
  source-to-ELF step is UNBLOCKED (2026-10-17): a real `mips64-elf-gcc` 14.2.0 + binutils 2.40
  are installed (~/toolchains/mips64-elf, symlinked into /opt/homebrew/bin; clang kept as
  `mips64-elf-clang`; `patches/` plain `make` uses them). Check with
  `/opt/homebrew/bin/mips64-elf-gcc --version` (full path if PATH lacks Homebrew). [older text follows:] The existing
  `patches.elf` is usable for a separate host-side qualification, but Session
  5340 corrected the earlier claim that the direct command already compiled
  cleanly: N64Recomp regenerated 11 functions, then Clang rejected the
  generated call to `findAndUnlinkSmallestEntry` because `funcs.h` declares
  only the entrypoint. Supplying that prototype externally makes Clang and
  `ar` pass; `nm` shows `allocateDisplayListBuffer` defined and the helper
  unresolved as expected for a host object. This does not replace the missing
  cross-compiler for a fresh source qualification. Session 5341 made the
  declaration repair regeneration-safe in `tools/fixup_patches_host.py`,
  wired it into the CMake N64Recomp rule, and reran the existing-ELF
  qualification without an external shim: generation, Clang compilation,
  archiving, and the `nm` positive control all passed. This qualifies only the
  existing ELF-to-host artifact path; fresh source qualification still
  requires the missing cross-compiler.

- **PatchesLib is shadowed on macOS (s5366).** `libPatchesLib.a` and
  `libRecompiledFuncs.a` both define `allocateDisplayListBuffer`; ld64 never
  pulls the patch member, so C and asm patch exes are byte-identical and the
  live heap guards are the fixup-inlined `s_alloc_tail_guard*` ones. Check with
  `tools/check_patches_shadowed.sh`. Patch-layer claims in older entries are
  unsupported for this build; forcing the patch in (-force_load) would drop the
  extra inlined guards and is a behaviour change needing its own A/B.

- **allocDLB guard census (s5378, single run).** Route to mission (`0x00690400`, 12288 entries) showed `slot0/g2bad/g3bad` all 0 on every `[a5370]` row. No same-run positive control for the guard branches, so this does not show the guards are dead. Route reaches hangar in ~1/3-3/5 launches (flaky; s5376/s5378).

### Generated symbols

The generated-symbol sweep is now exhausted: Session 5402 confirmed that the
remaining mission-overlay placeholder `func_800E9AE0` has an exact body span,
but the companion map supplies no semantic name and no live caller. Session 5397 synchronized the distinct
menu-overlay `fake_func_800B47C4` preamble to
`menuControllerInputPreamble`; its generated span, syms size, and following
`menuControllerInput` boundary agree. Session 5336 rechecked the stale
`0x800927B0` NEXT item and found every generated, registration, project-map,
fixup, and companion surface already synchronized. Preserve names that are
already synchronized, data symbols, and unmaterialized host-wrapper entries.
Only rename a real generated placeholder when the companion map and generated
tree agree. Session 5398 synchronized the exact entry-local `0x8000040C` /
`0x34` span to the existing `clearMemory16ByteBlocks` syms mapping; the
companion `make_elf.py` remains address-coded for this hard-coded entry, so no
new semantic name was inferred. Session 5399 synchronized the exact `0xC`
span at `0x800B58B4` to the existing `playerAwingInitPreamble` syms mapping;
the committed generated tree was already synchronized, while a stale
placeholder existed only in a pre-existing dirty sibling worktree. Audit
files are `docs/RENAME-S*.md`.
Session 5400 audited `fake_func_800B75C4`: the generated 0xC-byte instruction
fragment ends before `playerYwingInit`, while the companion map retains the fake
symbol and the independent syms table calls the exact span `data_gap_800B75C4`.
H2 selected; no semantic rename is authorized. See `docs/RENAME-S5400.md`.
Session 5401 applied the same exact-span test to `fake_func_800B89F4`: the
generated record is an invalid-C gap filler, the companion map identifies a
split before `playerVwingInit`, and the independent syms table classifies the
same 0xC-byte span as `data_gap_800B89F4`. H2 selected; no semantic rename is
authorized. See `docs/RENAME-S5401.md`.
Session 5402 applied the exact-span test to `fake_func_800AF6A8`: the
generated record is a trap-only invalid-C gap filler, the companion map starts
`cutsceneTypeStrings` at `0x800AF6B0`, and the independent syms table classifies
`0x800AF6A8..0x800AF6B0` as `data_gap_800AF6A8` (size `0x8`). H2 selected; no
semantic rename is authorized. See `docs/RENAME-S5402.md`.

Session 5404's offline M4 pass re-ran the existing retail parser with positive
controls: 2,083/2,083 task joins, 3,020,766 mid-task records, 1,222 tasks with
transient `-32768` lanes, and zero task-end lanes. It confirmed that the prior
exact join is structurally impossible because task serials are local, the port
capture is one long task, and framebuffer origins alternate. The usable next
discriminator is phase epoch + ucode image identity + mapped IMEM PC +
task-local normalized progress; no writer or mitigation is inferred. See
`docs/REVISIT-S5404-M4-NORMALIZED-BOUNDARY-DESIGN.md`.

Session 5405 ran the batched normalized-boundary gate in
`tools/analyze_m4_normalized.py` with a self-test and the existing s5354
retail capture plus an existing port log. Retail passed whole-RDRAM, VI, and
mapped-PC controls and supplied 2,580,925 mapped-PC rows; the available port
log supplied zero normalized rows. Neither arm's available record format
contains an explicit ucode image identity, so H3 is selected. This is an
instrument/schema result only: no accumulator writer or mitigation is
authorized. Session 5563 added the regeneration-safe port-side witness and
Session 5565 replaced its callback ordinal with the observed per-task dispatch
counter, recorded task totals, and capped retained rows at 4096 per VI phase.
The keyed run reached mission at 84 s and stayed alive for 151 s with zero VI
stalls and zero crash markers. It emitted 21,512 bounded rows with one image ID
and both mapped PCs. H3 remains selected: the port capture has no whole-RDRAM
positive control and shares fewer than 20 normalized rows at either mapped PC
with the qualified retail capture. No writer or mitigation conclusion follows.

Session 5568 added the missing port whole-RDRAM positive control and explicit
VI width/origin fields to each normalized row, through the regeneration-safe
fixup. The corrected keyed capture reached mission at 106 s, verified alive
through the hold, and had zero VI stalls or crash/abort markers. All retail and
port controls passed in the same analyzer run (`retail_rows=2,573,768`,
`port_rows=21,514`; whole-RDRAM, VI, mapped-PC, and image all true), but exact
phase/image/PC/progress joins remained below 20 rows for both mapped PCs, so H3
still holds. The initial arm crashed before any control because the generated
artifact still had the old three-argument callback; the fixup migration and
rebuild corrected that integration defect. No accumulator writer or mitigation
is inferred. The next M4 angle must relax only the structurally nonportable
exact join (e.g. within-phase rank/lane comparison) rather than repeat this
schema capture.

Session 5575 ran `tools/analyze_m4_event_shape.py` against the same qualified
captures. Both arms passed whole-RDRAM, VI, mapped-PC, and image controls and
the lane field was active in both; the new task-total-bucket key formed zero
shared classes (656 retail versus 6 port). H3 remains selected, so no writer or
mitigation conclusion follows. See `docs/M4-S5575-EVENT-SHAPE.md`.

Session 5570 ran `tools/analyze_m4_ranked.py` against those same captures. The
analyzer passed retail and port whole-RDRAM, VI, mapped-PC, and image controls,
filtered the shared hangar VI phase, paired the ordered phase/image groups by
within-arm ordinal, and compared 16 rank bins per mapped PC. One group aligned
at each PC and all 32 bin comparisons were equal, but all retail and port lane
masks were empty. The lane discriminator therefore selected H3 (no active
masks), not H1; no accumulator writer or mitigation is inferred. The new
comparison is not a reason to repeat the same capture.

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

- (s5590) "s5589 lldb soak 0 crashes / bad=0": not evidence; believable because the summary printed bad=0 and rc=0, but titles=0/3 means the game never booted past launch (getcwd EPERM under lldb).

- (s5585) "Project needs a human direction decision now" (s5584 BLOCKED): overturned as premature; believable because every other thread was closed, but the queued extended-hold soak had not yet run.

- (s5473) "mission-end condition cannot be read: objdump is not permitted" (s5472 BLOCKED.md). Believable because the headless allowlist really denied mips64-elf-objdump and no generated C exists for the overlay function; false because the need was a disassembly, which a stdlib script over the ELF supplies.
- (s5470) "requestMissionTransitionMode has no jal callers => reached via function pointers / a condition in runInMissionFrame at funcs_42.c:12256" (docs/M6-PHASE-MACHINE.md, s5469 NEXT.md). Believable because grep found no jal and the bt showed runInMissionFrame as caller. Actually the call is the jalr in the event-table loop; a0=2 is the event id, not a computed condition.
- s5423 hypothesis H1 "renderer/DL path drops flown terrain geometry before the RDP" is refuted by s5424: the flown RDP stream has 2.40M tri vs hangar 349k at the same ~1.7 tri/submission. It was believable because flown frames show only sky and the hangar renders fine. Live pair now: H4 (RT64 clip/cull/depth rejects it) vs H3 (partial fb dump).

- s5423 caveat: "M6 endurance closed / flown hold clean" proves no crash/stall only; it was believable because the detectors (VI stall, crash markers, fbhash) cannot see a frame that is alive but nearly empty. Flight frames show sky only, so render fidelity in flight is OPEN.

- "The patch layer (asm or C) provides the live heap guards" (s5365 and older
  entries) is overturned by s5366: ld64 never links the patch member. It was
  believable because Zelda-style link order (PatchesLib first) is meant to
  make overrides win. s5367 adds that the patch is NOT redundant: it has
  stricter predicates than the inlined guards.

- The claim that retail never had a mid-task `0x8000` VACC lane came from a
  signed/unsigned decoder error; corrected retail evidence found such lanes in
  all sampled 512-wide tasks while task-end remained zero. No mitigation
  follows.
- The port's modal `0x03` entry byte was caused by an unswizzled host byte
  census. Corrected reads match retail (`0x00` dominant, `0x03` absent).
- Earlier “M5 fully closed” claims were too broad until the keyed mission and
  long-hold rows; those rows now close the qualified route.
- The s5351 claim that oracle-driving past attract needs human authorization
  was wrong. It was believable because s5326/s5329 attempts missed the hangar,
  but s5330's in-process autopilot route works and s5335 reached the hangar in
  both arms; the real wall is the retail/port key-domain mismatch, which is
  offline-resolvable.
- The s5372 claim that the nohangar failure needs a human direction decision was
  wrong. It was believable because s5369/s5370/s5371 all failed to reach the
  hangar, but s5099 reached it 3/3 earlier the same day, the recipes differ only
  in env flags, and the control run was never executed. Pending s5373 verdict.
- Earlier route-blocked and host-load conclusions are historical. Use the soak
  queue and current `NEXT.md`; do not revive stale backlogs without a new
  measurement.

## M6 flown-hold update (s5420)
Flown 1200 s hold: 0 crash/0 stall again, but the "static cycle" seen after ~10-12 min is the TITLE screen (VI width 1024 origin 0x790400 from 634 s): the mission ended and the game fell back to title/attract. Not a hang. Cause of mission end unknown (death vs objective vs autopilot 'r'). ROGUESQ_FB_DUMP_DIR dumps PPMs but assumes stride 320 (garbled at other widths).

## Next steps (single monotonic backlog)

- **s5607 (TOP):** s5604_mwin_{a,b} folded (full logs: scratch/agent/m6/<tag>/run.log, not soak_results). Poke control fired; flagword 0x8010C9E0 cycles 0->4->0->1->0 repeatedly (gate 0x8010CA20 0->4->6->0), mission never ends (no 0x6AB400, alive 301 s, 0 crashes). 0x690400/0x620400 alternation is baseline double-buffering. Next: static readers of 0x8010C9E0 / writers of 0x8010CA20 to explain the re-arming cycle.
- **s5606:** 800C7738 and 800C776C are identical flag-setters (bit 0x4 / 0x8 of 0x8010C9E0 if 0x8010CA20==0); lv0 win and loss gates both call 7738, so win/loss is NOT decided there (single-source static). ROGUESQ_MISSION_WIN now logs `flagword` transitions after the poke. Fold s5604_mwin_{a,b}; see NEXT.md for the a/b/c outcome split.
- **s5605 (TOP):** s5604 gate block refuted (range artifact: retries narrowed `ITER_START_HEAD..HEAD` to docs-only commits). ROGUESQ_MISSION_WIN now also pokes get(3)=0x80138068 to 9 (lv0 end gate per M6-OBJECTIVE-COUNTER-WRITERS.md); mask 0x130B15 is HUD-only. Needs a rebuild, re-queued soaks, and a read of 800C7738 vs 800C776C (win vs loss). Single-source static.

- **s5604 (TOP):** s5602_plume_c folded (3/4 titles, clean; 36 clean boots). Landed `ROGUESQ_MISSION_WIN=<n>` (main.cpp, test-only): sets objective-complete mask byte 0x130B15 to 0xFF at mission origin 0x690400. Soaks `s5604_mwin_{a,b}` queued; control = `[mission-win]` log line. Hypothesis only: that byte decides success (activateObjectiveCompleteFlag writer, single-source). If mission outcome is unchanged, trace readers / use gObjectiveBooleans 0x801388A0. Loss counter 0x80138064 = gObjectiveCounts[1].
- **s5603 (TOP):** s5602_plume_{a,b} folded: control MET both (titles 4/4, alive 4/4, bad=0 each) -> 8/8 fast default-build title boots clean, no SIGSEGV/si_addr=0x58. With the 20/20 lldb-attach boots (s5592) that is 28 clean boots; P(0/28 | p=1/7) ~1.4%, so the plume is probably dissolved by the poke_be32 overflow fix (s5597) - still a hypothesis (no writer ever named for the old crash). `s5602_plume_c` is still queued (loop runs it); fold it, then move to M6 second-mission blocker (mission-1 win needed, s5596) or M5 de-stub doc check.
- **s5602 (superseded by s5603, believable because the recipe looked right):** s5601_plume_fast folded as a NULL (control failed, 0/12 reached title in 24 s). Queued s5602_plume_{a,b,c}.
- **s5601 (superseded by s5602, believable because rc=0/bad=0 looked like a clean result):** s5597_plume_asan hit the 600 s cap (2 of 3 boots, clean). Queued `s5601_plume_fast` (default build, N=12 fast title boots). Fold it: any CRASHMARK/BREADCRUMB -> lldb attach backtrace, name writer; all clean -> plume probably dissolved by the poke_be32 overflow fix (hypothesis, not proof).
- **s5600 (superseded TOP):** s5599 ASan hangar holds folded: a (mission_t=255s) and b (110s), 300 s holds, alive, 0 stalls, 0 asan.* files -> ASan-armed first-mission CLOSED (n=2). Mission 2 is blocked (autopilot cannot win mission 1, s5596), so next = title-boot plume SIGSEGV (si_addr=0x58) lldb loop until recurrence.
- **s5599:** queued `soak_queue/s5599_asan_hangar_{a,b}` (ASan build_asan, keyed hangar->mission, 300 s hold past onset; `m6_god_common.sh` now honours `BUILD=`). Fold the verdicts: control = origin 0x00690400 + alive at end; any `asan.*` = real finding (name writer, fix root cause). Both clean with control -> ASan first-mission closed; then second-mission (needs mission-1 win, s5596) or the title-boot plume loop. POKE_WRAP A/B closed (s5598: no difference, default drop kept). No conclusion overturned this session.

- **s5597 (TOP):** ASan arm landed (`tools/build_asan.sh` -> build_asan/) and caught a real overflow: `poke_be32(0x101C)` in `factor5_gfx_runner` wrote 0x1C bytes past gfx `dmem` into the adjacent audio DMEM global every gfx task (3/3 boots). Fixed in src/main/main.cpp (default drops OOB bytes; `ROGUESQ_POKE_WRAP=1` = wrap arm). Post-fix ASan title boots n=2 clean, 0 reports. Plume SIGSEGV (si_addr=0x58) NOT proven related. Next: fold queued `s5597_plume_asan`; run a concurrent default-vs-`ROGUESQ_POKE_WRAP=1` title+hangar pair on build/ (check whether the 0x01C read matters); then keep ASan arm for hangar/mission holds (build_asan is slow) to catch any further first-hit.

- **s5596 (TOP):** second-mission gate surveyed (static, single-source): bit 0x02000000 of 0x130B58 gates initMission arm A (0x8003E2B4, B40=0x14); the normal title->hangar->mission route uses arm B (0x8003E378 via cinematicLoopBody), so the s5515/s5517 "never set" is expected and the bit is NOT the mission-2 gate. Mission 2 needs a mission-1 win, which the key autopilot cannot produce - named blocker. Next: ASan arm for the title-boot plume SIGSEGV (si_addr=0x58).
- **s5595 (TOP):** s5594 hangar_long_k,l folded: both clean (hold 903 s, vi_stalls30s=0, crashlines=0). First-mission endurance 10/10 (title and hangar routes). Do NOT queue more first-mission holds. Next: second-mission route investigation (flag 0x130B58 bit 0x02000000, s5515) - offline survey of who sets it, then a keyed route or an ASan arm.

- **s5594 (TOP):** long_i (a tag-reuse replay of c) and long_j (20 min) clean: 8 long title->mission holds, 0 crash/stall. Queued s5594_hangar_long_{k,l} (hangar route, 15 min). Clean -> pivot to ASan arm or second-mission route (s5515 flag 0x130B58).

- **s5593 (TOP):** s5592 m6_long_g,h folded: both clean (hold 905/901 s, alive, vi_stalls30s=0, crashlines=0; mission_cycles 4/1). With s5551 d / s5554 a-c that is 6/6 long mission holds clean. Not covered: flaky hangar route, second mission. Queued s5592_m6_long_i (15 min) and s5593_m6_long_j (20 min). If both clean: pivot to second-mission route or ASan arm.
- **s5592:** s5590 attach e,f folded: control=PASS, 20/20 attached title boots clean (lldb stops were only SIGSTOP/SIGKILL; no SIGSEGV, no si_addr=0x58). Plume NOT closed (single-source; P(0/20 at 1/7)~4.6%) but lldb attach is a working instrument; stop burning iterations on it. Pivot to M6: fold s5592_m6_long_{g,h,i} (>=10 min mission holds, queued). Any CRASH/stall -> backtrace, name writer, root-cause fix. (s5591's "attach recipes queued, fold them" item below is DONE.)

- **s5591 (TOP):** lldb LAUNCH confirmed dead in loop context (c,d getcwd EPERM too). Attach recipes s5590_plume_attach_{e,f} queued (10 boots each, control = injected SIGSEGV). Fold their summaries; after ~20 clean boots pivot to M6 mission-hold soaks.
- **s5590 (superseded by s5591):** s5589_plume_lldb_{a,b} were launch-failure NULLS (titles=0/3; game SIGABRT on `getcwd failed: Operation not permitted` under lldb) - they say nothing about the plume. Generator now mirrors s5406 invocation; lldb_{c,d} queued. If c/d also hit getcwd EPERM, cause is the loop context (TCC) -> switch to lldb attach (s5453 pattern).
- (s5589, demoted) hold_d folded: TITLE+ALIVE@+120, 0 crash; 4/4 clean total (P(0/4 | p=1/7)~54%, plume NOT closed, no BLOCKED needed). Queued s5589_plume_lldb_{a,b} (3 boots each, run under `lldb -b` with launch, not attach - s5577's attach loop failed on tooling; if no TITLE lines, that hypothesis recurs). Generator: tools/agent/gen_plume_lldb_soak.py. After ~20 clean boots pivot to M6 mission holds.

- **s5586 (TOP):** s5584 soak still pending (loop runs it after this iteration). Fold it next; no new work until it lands.

- **s5585 (TOP):** unblock: the s5584 BLOCKED (human direction) was premature, since its soak had not run. BLOCKED.md archived; NEXT = fold s5584_plume_title_hold. Re-escalate only if it is 0/4 crashes with alive120 4/4. OPEN DEPENDENCY (human): declare goal met or name a new target.
- (s5584 superseded by s5585, believable because the soak was queued and the author saw no other candidate): pivot found no engineering change; queued s5584_plume_title_hold (N=4, 120 s past title); BLOCKED for human direction (BLOCKED.md).
- **s5582:** s5581 a/b = 8/8 titles clean; LLE trio total 12/12, 0 crashes. M5 closed; crash handler already complete. Loop BLOCKED awaiting direction (see scratch/agent/BLOCKED.md). (s5583: block refuted; M6 holds already closed, do not repeat. Next: LLE-trio title loop held 120 s past first title.)

- **s5581 (TOP, pending):** s5580 returned 4/4 titles, 0 crashes (LLE trio confirmed as the title-route
  ingredient). Queued `s5581_plume_lle4_a/_b` (8 more boots). Crash seen -> lldb variant, real backtrace;
  12/12 clean -> hold past title before kill (runs currently end at first title origin).

- **s5580 (TOP, pending):** s5579 was a TOOLING NULL (recipe lacked the zsh re-exec guard;
  ${0:A:h} unbound -> paths became /scratch, game never launched, rc=0 in 0 s). Re-queued as
  `soak_queue/s5580_plume_lle4.sh` with the guard. Same decision table as below. Rule: every
  recipe's line 2 must be the zsh re-exec guard; a 0 s rc=0 soak is a null, not a pass.
- (s5579 original text follows) Queued `soak_queue/s5579_plume_lle4.sh` (s5578 loop + LLE
  trio, cheap tail-based poll, N=4). No result yet - read SOAK-RESULTS.md first.
  Titles >=2/4 -> queue an lldb variant to catch the si_addr=0x58 SIGSEGV; 0/4 at
  `0x696100` -> title-route regression since s5463, diff env against the s5463
  recipe; titles but no crash -> raise N. The s5578 claim that the LLE trio is the
  missing ingredient is still single-source until this lands.

- **s5578 (superseded by s5579 as top):** The no-lldb default-route loop (3 attempts, 120 s) also stayed
  at origin `0x696100`, 0 titles, no crash marker, so lldb is NOT the blocker
  (overturns the implicit s5577 assumption that dropping lldb would reach title;
  it was believable because the lldb control was the only thing that differed
  from the older title-reaching loops - it was not, the LLE env trio was).
  Single-source: the title-reaching s5453/s5463 recipes also set
  ROGUESQ_LLE_FORCE=1 LLE_UNGATED=1 LLE_SOLO=1. Next: queue the same loop with
  that trio, count title origins, then attach lldb on the arm that reaches title.
  Use a cheap poll (logs hit 70 MB per 120 s).

- **s5577 (superseded by s5578):** The default-route lldb control passed, but the corrected
  four-attempt loop reached title origin 0/4 and remained at origin `0x696100`
  through 120 seconds. Stop repeating lldb: run the qualified default route
  without a debugger, retain the in-process crash handler and phase logging,
  and require title origin `0x00790400` before interpreting a null plume
  breadcrumb. A crash marker/backtrace names the writer; clean title boots
  close only this recurrence attempt.

- **s5575:** M4 is parked after two new schema discriminators: the s5570
  rank-bin key had empty lane masks, and the s5575 task-total-bucket key had
  zero shared classes despite positive controls and active lanes. Do not repeat
  either comparison. Run the M6 secondary title-boot plume experiment: verify
  the macOS screen is unlocked, loop the qualified title boot under lldb, and
  when the ~1/7 SIGSEGV recurs capture the real backtrace and writer. If no
  recurrence occurs in the bounded loop, record that passive result and keep
  M4 parked; do not add another indirect join field.

- **s5573:** `fake_func_8006ACA4` is an exact 12-byte non-callable gap
  before `transformObjectColliderCenter`; the companion map and independent
  syms table agree on `data_gap_8006ACA4`. Continue the bounded sweep with
  `fake_func_800AE3E4`; do not infer semantic names from address-only or
  companion fake entries.
- **s5572:** The generated placeholder `fake_func_8000337C` is an exact 4-byte
  non-callable gap before `setVideoReadyFlag`; the companion map and
  independent syms table agree. No rename or runtime change is authorized.
- **s5571:** The first generated-symbol candidate, `fake_func_800027B8`,
  is an exact 8-byte non-callable gap and remains unchanged. Continue the
  bounded sweep with the next live placeholder; do not infer semantic names
  from address-only or companion fake entries.
- **s5570:** The ranked/lane comparison passes all controls and aligns
  ordered groups at both mapped PCs, but every lane mask is empty in both arms.
  H3 remains selected: the lane witness did not fire, so no writer or value
  conclusion follows. Do not rerun the schema or ranked comparison. The next
  bounded unit is the generated-symbol sweep: inspect one remaining real
  placeholder against the companion map, generated span, and independent syms
  table; rename only if all three agree, otherwise record a gap/data decision.
- **s5561 (TOP):** Conditional-move candidates audited and closed: 149 unique
  sites, zero semantic mismatches, and both positive controls passed. M3
  idiom-class work is now exhausted for the currently listed classes. Next:
  implement the new M4 normalized-boundary schema (phase epoch, ucode image
  identity, mapped IMEM PC, and task-local progress/end observations) before
  attempting another accumulator comparison; do not infer a writer from the
  existing structurally unjoinable records.
- **s5559:** Late `$ra` writes audited and closed as invalid/data-gap, Factor 5
  control-flow, or intentional tail-return material.
- **s5558:** `$sp` adjustment balance audited and closed as an artifact/worker
  class. No conclusions overturned.
- **s5557 (TOP):** M3 class `$zero`-destination writes audited: 0 `ctx->r0` refs in generated C (control: r2 55248), dead by construction (`docs/M3-ZERO-REG-WRITE-AUDIT.md`). Next: another unlisted class. No conclusions overturned.
- **s5556:** s5554 long_c folded: clean (900 s hold, 0 crash, 0 stall, mission_cycles=2). 3/3 fifteen-minute holds clean => M6 first-mission endurance MET (priority 3b closed). Next unit: priority-3 M3 idiom-class audit (pick a class absent from the closed list in the M3 section; grep-enumerate, classify every site, guard or prove dead). No conclusions overturned.
- (s5553, now item 2): s5551 long_d folded: 4/4 long mission holds clean (722-725 s, 0 crash/stall). `tools/m6_cycles.sh` (selftest-controlled) shows long_c/long_d re-entered hangar->mission after the mission-end fall-back to title (1 cycle each, long_a 0), no failure. `mission_cycles=` now in m6_god_common.sh summaries. Next: queue 3 holds with HOLD~900 to obtain >=2 cycles/run; any CRASH/stall -> lldb backtrace.

- (s5552 TOP) s5551 long_a and long_c folded: clean (hold 722/723 s, 0 stalls, 0 crash lines). With s5549 long_b the >=3-run, >=10 min first-mission endurance bar is met (3/3 clean). long_d still queued. Next: fold long_d, then extend the route past mission 1 or disambiguate the origin alternation with a phase-gated marker.
- (s5550) s5548 hangar_a/b/c folded: 3/3 clean. s5549_m6_long_a rc=137 at 600 s was the loop's stale 600 s cap (loop.sh started 08:43, before the 1000 default), NOT a game failure: mission verified at 130 s, 0 crash lines in 411k log lines, origins still cycling at kill. 12-min hold still unmeasured. Fixed by a `# SOAK_TIMEOUT=1100` header on soak_queue/s5549_m6_long_b.sh (per-recipe cap, loop.sh:253). Next: fold long_b; check whether the tail 0x720400/0x790400 alternation is mission or title fallback.
- (s5551 TOP) s5549_m6_long_b folded: clean 722 s mission hold (0 stalls, 0 crash lines, fbhash distinct 14721/16160). Queued soak_queue/s5551_m6_long_{a,c,d} (same recipe) to reach the >=3-run bar; lldb plume loop stays redundant (16/16 clean). No conclusions overturned.
- (s5549 TOP) s5548 hangar a/b folded: 2/2 clean (mission onset 83/81 s, 441 s hold, 0 stalls, 0 crash lines); hangar_c still queued. SOAK_TIMEOUT raised 600->1000 (tools/agent/loop.sh) and `soak_queue/s5549_m6_long_{a,b}` queued (HOLD=720, ~12 min after onset) = the >=10 min hold. Fold verdicts from SOAK-RESULTS.md; crash/stall -> lldb backtrace + name writer; all clean -> title-boot plume SIGSEGV loop under lldb, then item-4 renaming sweep. No conclusions overturned.
- (s5547) Regen determinism CLOSED: make_elf ELF byte-identical; fresh N64Recomp + replay compiles to asm identical to live (only cosmetic `;`/indent, 296 lines, 3 files). RecompiledFuncs.s4204-fresh snapshot is stale vs current N64Recomp (movz/movn forms) - use scratch_s5547_regen as the fresh baseline. Next: M6 mission-hold endurance soaks (priority 3b).
- (s5545 TOP) Replay residual ~39 -> 15: funcs_4/27/24 closed. Left: funcs_29 4, funcs_20 3, funcs_9/8/5/25 2 each. Then compile-prove.
- (s5546 TOP) Replay residual 15 -> 0: scratch replay is text-identical to the live RecompiledFuncs (control still flags). Next: full-chain regen + cmake in a separate build dir and boot check.
- (s5542) Replay residual ~393 -> ~120: block-move rules in fixup_live_replay.py; funcs_24 309 -> 35. Next: s4534 phase-gate removal + order leftovers, then funcs_23 (53), funcs_4, funcs_27.
- (s5541) Replay residual ~410 -> ~393: fixup_live_replay.py move_lines() ports s5223/lowfield/s4873 order + funcs_24 MEM_W swap. funcs_24 309 = helper-block order (s4867/s4864/s5228) + live-only diag inserts; next: block-move rule, then funcs_23/4/27.
- (s5537) Blanket static-RENAMES replay made residual WORSE (600 -> 758); reverted; live renames were batch-scoped. Derive old->new map from live-vs-replay diff instead.
- (s5536 TOP) Replay residual 831 -> 600 (18 files): strip_diag_layers now also drops untagged header decls and exempts funcs_23/24. Left: funcs_24 325 / funcs_0 74 / funcs_23 53 / funcs_26 41 / funcs_1 25. funcs_0 gap = rename sweep (func_8000040C vs clearMemory16ByteBlocks) not in replay: wire tools/rename* next, then classify inline s4694/s4340/m5 blocks in funcs_26/1/4, then compile-prove at <~300.
- (s5535) tools/strip_diag_layers.py now in replay: residual 1,008 -> 831; live is partially stripped (~7 live-only lines still carry s4222/s4299/s4601 hooks => hand-assembled, single-source). Next: classify the 831 (s4340/s5223/s4899/s4223/s3556, ~201 untagged).
- (s5538 TOP) Replay residual is 600 lines / 18 files (funcs_24 325, funcs_0 74, funcs_23 53, funcs_26 41). Identifier drift is NOT the cause: only 7 distinct token pairs differ, 3 real (funcs.h renames clearMemory16ByteBlocks, menuControllerInputPreamble, playerAwingInitPreamble). The rest is scratch-only multi-line diagnostic blocks (rs64_phase_ord, s3556, s4714, s4223_stk, rs64_filter_voice_*_probe, s4298, s4471, s4694, rs64_m5_callback_writer_event) in funcs_0/1/26/27, plus live-only hand patches in funcs_4/5/23 (alloc_tail_guard2, swap_ack_wait). Next: extend strip_diag_layers.py for those blocks, script the funcs_4/5 patches, add the 3 renames, then funcs_24. Census: scratch/agent/s5538_classes.py. (Supersedes the s5534 "untagged live-only lines" framing below.)
- (s5534 superseded by s5538) Replay residual 1,598 -> 1,008 lines: tools/fixup_movz_movn.py was missing from s5532_determinism.sh (now wired). Left: scratch-only s4299/s4222/s4601 diagnostics (live lacks them; hypothesis: unscripted strip - find or script it), ~201 live-only untagged lines + one-off live-only tags. Classes: `zsh scratch/agent/s5534_classes.sh`. Then compile-prove scratch tree when < ~300.
- (s5533 TOP) Regen determinism: scratch replay now COMPLETES (fixup rc=0, failures=0) and differs from live by 1,598 lines in 53 files (was ~171k). 36 marker-present scripts wired; s5228/s4340 ordering, s3285-vs-s5034 deforce/reforce, dir-arg scripts, and s4340 scoped to funcs_23/24 fixed. Residual categories: `zsh scratch/agent/s5533_residual.sh`. Next: explain the residual (scratch-only s4299/s4222/s4601 ~190 lines; ~1.3k untagged), then build the scratch tree to prove it compiles. The s5532 note (stops at s5228) is superseded.

- (s5530 TOP) Renaming-sweep dry-run: 0 companion-backed "selected" function renames remain (only D_/fake_func_ gaps). Mechanical sweep exhausted; loop BLOCKED awaiting direction. Fallback unit lldb plume loop is redundant (16/16 clean, see backlog line). s5531 unblock re-scoped NEXT to regen-determinism check. OPEN DEPENDENCY (human): decide whether to declare project goal met / pick a new direction.

- (s5529 TOP) s5527 hangar c folded: 3/3 hangar-route holds clean (0 crash/0 stall). 'Render fidelity in flight' was already closed by s5490 (terrain+HUD visible, tricount 3.7M) - dropped as a work unit. M6 closed on both routes; NEXT: item-4 renaming sweep.
- (s5528) s5527 hangar soaks a,b folded: 0 crash, 0 VI stall, 440 s holds, control mission_t=81s present; c pending (replication only). NEXT: render fidelity in flight.
- (s5525) FORCE_CINE_A0 f1/f2 change B40 and initMission a0 (0x0A->0x32/0xD3/0xE3) with no crash; origin stays 0x690400 and [mfst] names are identical (f2 shows none). s5526: initMission reads NO a0 (static, funcs_42.c) - a0 values are leftovers; second-mission forcing via cine-arg/B40/save byte CLOSED. NEXT: pivot to M6 endurance soaks (title->mission, >=10 min hold, >=3 runs). Arms: scratch/agent/s5525_*.sh.

- **s5523 (newest)**: B40 = cinematicLoopBody a0 (0x13 on the title cinematic, 0 for both mission inits; ra unusable, =0). Next: find who supplies that a0 and force it (see scratch/agent/NEXT.md). Single-source.
- **s5523 (TOP):** s5520 b40w folded: B40 is reset at 0x800A5E5C = cinematicLoopBody (0x800A5D80) storing its a0 (0x13 / loop index s0 / B40 itself) — B40 is a mainGameLoop state byte, so every B40/gCurrentLevel/cine-arg/save-slot poke is clobbered by design (dynamic ordering log + static caller args). Next: log ra+a0 at the two initMission (0x800FA250) call sites and cinematicLoopBody entry in ONE build to find what the real mission index is.
- **s5521 (TOP):** s5519 f7 folded: identical to base/f2 (save byte not the selector). The override sets B40=7 at DC2C but initMission reads 0, so a later guest store resets it. Built a `[b40w]` logger on all 10 B40 stores; fold `s5520_b40w_{f7,base}` next and name the resetting pc.
- **s5519:** built `ROGUESQ_FORCE_SAVE_MISSION` override + `[saveslot]` log in applySaveSlotToMissionState (fixup script + live funcs_17.c); arms `s5519_save_{base,f2,f7}` queued. Fold from scratch/agent/m6/<tag>/run.log: `[saveslot]` in base = control; differing `[mfst]` names in f2/f7 = save byte selects content. Not yet run.
- **s5518 (TOP):** s5517 hangar replications a,b folded: in both, control 0x3470 fired (watchpoint 1 hit) and flag word 0x130B58 hit only with new value 0 (attached at mission t=105/106, ~570/660 hangar-origin 0x006AB400 lines, 0 crashes). With s5515 that is 3/3 runs where bit 0x02000000 is never set => flag-word thread CLOSED (H2). Run c still queued, will only add replication. Next: pivot to second-mission selection by other means or more M6 holds.
- **s5517:** m6_wp_flag.sh is already hangar-gated (s5514 passed origin 0x006AB400, 551 lines), so s5515 covers the hangar route; replications s5517_wpflag_hangar_{a,b,c} queued.
- **s5516 (TOP):** M6 title->mission endurance census: 31 keyed holds, 251 min, 0 crashes / 0 stalls / 0 early deaths -> goal met on that route. Remaining M6 coverage is the hangar route (flaky ~3/5) and a second mission: run m6_wp_flag on the hangar route (positive control 0x3470) to see if flag bit 0x02000000 is set there.
- **s5515 (TOP):** s5514 write-watch folded: control (0x3470) fired in-run; flag word 0x130B58 got 2 writes, both value 0, over the whole mission hold => bit 0x02000000 is never set on the title->mission route (H3). Whatever gates the second mission content is not this bit on this route; next: find which route/state sets it (retail oracle or hangar route) or pivot to M6 endurance holds.
- **s5514 (TOP):** lldb write-watch on guest word 0x130B58 (B40 block flag word 0x18) built (`scratch/agent/m6_wp_flag.sh`, control = 0x3470 swap-counter watch) and queued as `soak_queue/s5514_wp_flag.sh`; not yet run. Next: fold the soak, check the control hit, name the PC/caller that sets bit 0x02000000 (H3 = zero transitions with control firing). No conclusions overturned this session.
- **s5513 (TOP):** s5508 arms folded: no arm shows a new manifest name (base 6 loads dbg_data/data, f7 12 same names, f2 0), so the B40/initMission override selects no content. Static scan: no constant-built writer of bit 0x02000000 in the flag word exists; $s3 = global 0x80130B40, flag word = 0x80130B58, passed to menuInit 0x800C58A0 (single-source, stale generated copy). Next: runtime write-watch on 0x80130B58 logging PC + old/new at the bit-25 set, with a positive control on any write.
- **s5511 (TOP):** mainGameLoop's initMission arm (gate: bit 0x02000000 of word 0x18($s3), 0x8003E250) hardcodes B40=0x14 at 0x8003E284 before initMission, so B40 is NOT a selector (static, single-source); s5508-s5510 B40 theories closed. Next: static grep for writers of bit 0x02000000 in 0x18($s3) and what feeds the mission pick. See NEXT.md.
- **s5508 (TOP):** static trace: initMission (0x800FA250) writes gCurrentLevel=B40 (0x800FA388), so B40 IS the level index feeding gCurrentLevel and the level-config getters; the s5504-s5506 "selector refuted" verdicts judged by mission VI origin (framebuffer address - content-blind), so they are doubtful (single-source). Built entry-time override ROGUESQ_FORCE_INITMISSION_SEL + `[mfst]` manifest-name log; arms s5508_im_base/f2/f7 queued - fold from scratch/agent/m6/<tag>/run.log: differing [mfst] name sets => B40 selects content. See PORTING-STATE s5508.
- **s5507 (superseded by s5508):** s5506 cine-arg arms folded: forcing mainGameLoop's 0x13 a0 to 2/7 (control `[cine-arg]` fired) left mission origin set identical (0x690400 present, no crash) -> that arg is not the mission selector (single run per arm). Third refuted selector after gCurrentLevel (s5504) and B40 poke (s5505). Next: static trace of applySaveSlotToMissionState (0x8006DC2C) / table 0x800CD404[sel] -> menuOverlayInit 0x800C5B8C to find where mission content (level asset id) is loaded; then hook that write, not a poll. See NEXT.md.
- **M6 mission-end facts (s5464-s5498, detail archived in PROJECT-OVERVIEW):** the ~frame 7000-8000 mission end in keyed holds is a legitimate MISSION FAILED results screen (loss counter 0x80138064>=3 written by updateDestructionDebrisNpc from DAT data) followed by fall-back to title; godmode and no-key runs end the same way, so it is not HP/autopilot driven. Flight render is correct. Earlier unkeyed 'mission holds' (s5409-s5413) were the attract loop (retracted s5414); key delivery was solved s5416.
- **Older backlog (s5370-s5507):** lldb attach works (launch fails getcwd EPERM); plume title-boot SIGSEGV closed as guarded/unreproduced (16/16 clean lldb loops); hangar route flaky ~3/5; PatchesLib shadowed (s5366); M4 closed as legitimate (s5354); SDL_QUIT quick_exit fix verified.
- **Selector theories refuted (single-source each):** gCurrentLevel poke (s5504), B40 poke (s5505), cine-arg 0x13 literal (s5506); s5509-s5511 show B40 is a mainGameLoop state byte, initMission arm hardcodes B40=0x14.

## Evidence index

Use `PORTING-STATE.md` for exact session details; never read it whole. Use
`docs/PROJECT-OVERVIEW.md` for migrated durable history, `docs/M5-AUDIO-PLAN.md`
for audio inventory and validation, `docs/F5-UCODE-REFERENCE.md` for the
microcode contract, and `scratch/agent/SOAK-RESULTS.md` for queued soak
verdicts. The next iteration must read this file, `scratch/agent/NEXT.md`, and
the tail of the soak results before acting.


- s5520: forced save slot (f2) does not change initMission B40 or [mfst] names; save byte is not the mission selector (f7 pending).

- s5540: tools/fixup_live_replay.py ports renames/MEM_W/guard2/swap-ack; residual ~410 (funcs_24 325, funcs_23 53, funcs_4 10, funcs_27 6). Next: funcs_24, then funcs_23.
- s5539: strip_diag_layers strips balanced scratch-only blocks; replay residual 600 -> ~440 (funcs_24 325, funcs_23 53, funcs_4 16, funcs_5 11, funcs_0 8, funcs_27 6, funcs.h 6). Next: port funcs_4/5 live patches into a fixup script, 3 funcs.h renames + funcs_0:5690 MEM_W order, then funcs_24.

- s5543: regen-determinism replay residual total ~92 (funcs_24 7 whitespace-only; funcs_23 53, funcs_4 10, funcs_27 6 next).
- s5544: funcs_23 replay residual 0; total ~39 (funcs_4 10, funcs_24 7, funcs_27 6, funcs_29 4, funcs_20 3, 4x2).

- s5587: s5584 plume title hold folded: 1/4 runs completed (600 s cap), 0 crashes, run1 alive +120 s. Remaining 3 queued as s5587_plume_hold_{b,c,d} (N=1 each). Plume thread open until they land.

- s5598: POKE_WRAP A/B (default drop vs wrap): identical origin sequences, both alive 100 s, 0 crashes (single-source, origin-only). Keep default drop. s5597 ASan title boots: 2 boots, 0 ASan reports. Next: ASan-armed keyed hangar/mission hold.
