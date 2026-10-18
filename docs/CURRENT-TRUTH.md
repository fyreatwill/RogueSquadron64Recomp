# Rogue Squadron 64 Recomp — current truth

Compact operational handoff, maintained at Session 5405 (2026-10-17).
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

The current bounded work is a parked-boundary revisit. Sessions 5321 and 5325
confirm that the qualified port's transient M4 `0x8000` state appears in
stages 10/11 and is absent in stages 12/13 and task end, but the stage hooks
are not comparable to the retail instruction-PC samples. The M4 discriminator
is therefore unevaluable without a complete task-keyed sampler at a shared
boundary; no accumulator mitigation follows. Session 5325 validated the
retail oracle's whole-RDRAM positive control and recorded the exact shared-
boundary design in `docs/REVISIT-S5325-M4-SHARED-BOUNDARY-DESIGN.md`.
Session 5326 made the cxd4 sampler stride configurable and added generated
Factor 5 PCs to the port hooks; both sampler controls were live, but neither
driven arm reached the target hangar phase, so that attempt selected H3. Session
5329's missing boundary was caused by its window-key schedule, not a missing
capability. Session 5330 used the source-documented in-process autopilot route
(`3:start,6:start,9:start,12:start,16:a,20:a,24:start,28:a`) with the
validated LLE route. The rebuilt port passed the phase control at
1024/`0x00790400` and reached the required shared 512 boundary at
`0x006AB400` in 23.8 seconds; the M4 gate emitted 464 records. The M4
task-keyed comparison is resumed, but no accumulator conclusion is drawn
until the cxd4 and port tables join at that boundary.

Session 5395 added null guards at both host-facing RSP task entrypoints:
`rs64_run_lle_gfx` now returns `-1` for a null task and `get_rsp_microcode`
returns the existing unknown-task stub. The normal Debug target builds. This
is a host callback-contract guard, not evidence of a guest writer or a route
defect; no runtime null reach was observed because the available SDL verifier
failed to start the child route (`rc=126`, no SDL_QUIT line).
Session 5331 ran that comparison attempt. The oracle whole-RDRAM/VI controls
passed, and the port again reached `0x006AB400`/512, but the port output
exposed only aggregate M4 counts; it lacked actual RSP-PC, task-serial, and
step-bucket keys. H3 remained selected at that point.
Session 5332 added a regeneration-surviving key path. In the phase-gated port
run, the same-run hook control fired and 4,091 target rows carried nonzero
task serial `961`, generated PCs `0x112C`/`0x17F0`, and increasing per-task
step values at `0x006AB400`/512. The task serial did not vary because the
target was one long graphics task, so this proves field availability and
rules out H3, but does not yet select H1/H2 or authorize a mitigation.
Session 5335 ran the corrected cxd4 retail arm and the port arm with same-run
positive controls. Retail produced 10,000 whole-RDRAM hits, live VI controls,
2,091 graphics task joins, and 1,215 tasks with transient `-32768` VACC lanes;
the port produced 4,096 target rows. The exact join remained unavailable:
retail PCs were `0x0088..0x0FE8`, while port rows used `0x112C`/`0x17F0`, and
the phase origins were `0x006AB800` versus `0x006AB400`. H3 is selected for
this discriminator; no writer or mitigation follows. See
`docs/REVISIT-S5335-M4-COMPARISON.md`.

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
authorized. The next implementation must add real image identity and task
progress/end observations to the port and cxd4 arms before another comparison.

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

> s5447 (TOP): s5446 guard soak 10/10 titles clean, 0 crash ((6/7)^10=0.21, weak). Breadcrumb `[s5446-scratchfb-guard]` added; s5447_plume_guard_crumb queued - read summary `guard_fired_runs` (fired>0 = mechanism proven). Then resume M6 mission/results endurance.
> s5446 (TOP): plume SIGSEGV si_addr=0x58 writer named from an old backtrace (bisect run4.log): scratch-fb branch of PresentQueue::threadPresent with VI::fbSize()==(0,0) -> null texture -> clearColorTarget. Guard landed in lib/rt64 (patch exported); soak s5446_plume_scratchfb_guard queued (weak evidence, base rate ~1/7). Lldb stays unusable; the in-process crash handler backtrace is the tool.
> s5445: flight endurance CLOSED clean - s5444_nostart_a/b 480 s holds, 0 crash / 0 stall / animating (12131 distinct of 13322 frames); ~10 clean runs total. z-only flight never ends the mission. Active item: title-boot plume SIGSEGV (si_addr=0x58) lldb loop (NEXT.md, slug m6-title-boot-plume-sigsegv); plain flight-endurance soaks are retired, and reaching the results screen needs a different recipe. Superseded: the s5444 res_late soaks as evidence about results-screen behaviour - they were recipe-defective (cap overrun, start=pause); rc=137 made them look like hangs.

> s5442: var_d/e clean, log cap confirmed (65 MB); m6_post_late_a/b queued. s5441: var_c clean (3/3 var soaks, 0 crash/stall). s4234-ENTRY cap confirmed working, but run.log was still 905 MB from [tricnt]/[rt64drawn] (1.2M lines/phase); now capped at 4000 lines/phase in rt64_render_context.cpp. var_d/e queued to confirm size drop. Then vary the hangar route / 1200 s holds with variation.

> s5440: s5439 var_a/var_b clean (0 crash/stall; var_a hit the 600 s cap with no summary). Cause of slow/huge runs: [s4234-ENTRY] log flood (1 GB run.log) - now capped in apply_s4234_entryprobe.py/apply_s4278_headwriter.py + live funcs_24.c. Check var_c run.log size on the new binary.

> s5437: M6 keyed hold 3/3 clean (s5436_a, s5437_b, s5437_c: 1217-1226 s, 0 crash, 0 stall, post-results restarts; single recipe).
> s5438: flight-1 vs flight-2 comparison done. Frame md5 is useless on animating scenes (0/65 equal across runs, 0 repeats within runs); a visual montage shows flight 2 rendering like flight 1 (single-source), so "second flight renders differently" is not supported. Helpers: scratch/agent/m6/{compare_flights.sh,frame_stats.py,ppm2png.py}. Next (top of backlog): vary the route (hangar route, alternate key schedule), >=3 runs of >=600 s, per scratch/agent/NEXT.md.

> Next-steps order (s5425): (1) one run with tricnt + fb dump + RT64 drawn-tri count at processDisplayLists to split H4/H3 (scratch/agent/NEXT.md); (2) only after that, further M6 endurance soaks.
> s5424 (TOP): flown RDP stream carries 2.4M tri over the 200 s hold (hangar 349k tri / 200k subs; same ~1.7 tri/submission), so geometry reaches the RDP submit (single-source, s5424_tri). Missing terrain is downstream: RT64 draw/clip/depth/fb-readback or the fb dump. Next: NEXT.md.
> s5423: flown frames (s5421_nor fbd 10000/20000, viewed via tools/ppm2png.py) show only sky + green craft icon + partial reticle, no terrain/objects (single-source). Discriminate H1 renderer drops geometry / H2 empty sky / H3 partial dump with per-frame RDP tri count flight vs hangar + mission-start frame dumps; see scratch/agent/NEXT.md.

> s5419: first FLOWN 1200 s hold (autopilot caps now 512 ev/8192 chars) clean: 0 crash, 0 stall; BUT fbhash shows a 4x repeating static two-frame cycle (~87 s period) from ~12 min on, so the mission is likely ended/parked (single-source, unresolved). Next: dump a frame at that point, replicate, vary pattern.
> s5418: replicated x2 (1205 s each, 0 crash/stall, fbhash maxrun 317/318) => 3/3 clean unflown holds; autopilot now supports l/r/sl/sr/su/sd flight keys (built, untested). Next: flown hold.
> s5417: keyed mission hold 1204 s clean (0 crash, 0 VI stall, fbhash maxrun=320 distinct=33446; single run, plus 2x483 s without fbhash). Next: repeat x2 for a 3-run sample, then add in-mission input (flight keys) since z/start autopilot does not fly.

0. (s5407) lldb is UNUSABLE here: launch mode never runs the game (0 bytes stdout in 30 s), attach mode hangs at `process attach` and freezes the game (suspected macOS debugger authorization; unconfirmed - a human can run `DevToolsSecurity -status` / approve the prompt). s5406 titles=0/10 is a tooling null, not crash evidence. Plume crash: rely on the in-process `[plume-null-color-attachment]` breadcrumb (0/18 boots). Next M6 work = keyed mission endurance (recipe s5377 hit the 600 s cap; split into <=540 s segments).
0--. (s5413) v3_a/b = first detector-controlled mission holds: 0 crash/0 stall over ~450 s each (2/2, v3_c pending). Template now also records fbhash maxrun/distinct (frozen-frame check, with control); v4_{a,b,c} queued - read `fbhash` line in keys.log first. Next: if distinct is large and 0 crash across v4, escalate to a second mission transition / longer composite holds; any frozen-frame -> name writer.
0-. (s5412) v3_a/b died at 0 s: the detector self-test sequence stopped at t=36 (max gap 30 < the 31-33 firing window), so ctl=0 and the recipe aborted by design. Fixed (sequence to 39; template and v3_a/b/c regenerated and re-queued). Superseded: s5411 implied v3 would be the first valid run; it could not have been. First detector-controlled data = the next v3 verdicts; v2 "0 stall" stays unproven, and the "M6 gate closed" claim at the top is provisional until then.
0a. (s5410) m6_mission_v2_{a,b}: 2/2 clean ~440 s mission holds (0 crash, 0 stall). Single-source; stall detector lacks a positive control and VI row counter also matches debug lines - fix the detector (count only [phase]/VI lines) before trusting "0 stalls"; verify in-flight vs briefing; await v2_c.
0b. (s5409) seg_a/b "nohangar" was a recipe bug (padded-origin grep; mission 0x690400 WAS reached, 0 CRASH). Re-enqueued as `m6_mission_v2_{a,b,c}.sh`; check whether mission-onset precedes keys (attract?). (s5408) Enqueued `m6_mission_seg_{a,b,c}.sh` (<=555 s keyed mission holds, crash+stall logging). Read their SOAK-RESULTS lines first. Caveat from s5394: dead keys can be a crash-report modal on screen (kill UserNotificationCenter) - the recipes do NOT do this, so an all-nohangar result means check for that before blaming the route.

0. (s5405) The normalized gate selected H3: retail controls/rows are live, but
the available port log has zero normalized rows and both existing schemas lack
explicit ucode image identity. Implement those observations before rerunning;
no writer or mitigation follows. See `tools/analyze_m4_normalized.py`.
0. (s5404) Designed a normalized M4 boundary key after the exact task-key join
   was shown structurally impossible: phase epoch, ucode image identity,
   mapped IMEM PC, and task-local progress bucket. The next unit must implement
   both arms with positive controls and a >=20-row threshold; no mitigation is
   authorized. See `docs/REVISIT-S5404-M4-NORMALIZED-BOUNDARY-DESIGN.md`.
0. (s5402) Audited `func_800E9AE0`: the generated 0x114-byte callable span,
   companion false-split note, overlay entry, and independent syms mapping
   agree, but no semantic name or live caller exists. H2 selected; no rename.
   See `docs/RENAME-S5402-MISSION-AUDIT.md`. The generated-symbol sweep is exhausted; next
   work must revisit a parked retail-entry or M4 boundary with a new
   discriminator.

0. (s5401) Audited `fake_func_800B89F4`: generated body, companion fake/real
   boundary, overlay entry, and syms classification agree on a 0xC-byte
   data/splat fragment before `playerVwingInit`; H2 selected, no rename. See
   `docs/RENAME-S5401.md`. Next candidate must pass the same exact-span/name
   test.

0. (s5400) Audited `fake_func_800B75C4`: generated body, entry table,
   companion fake/real boundary, and syms classification agree on a 0xC-byte
   split/data fragment before `playerYwingInit`; H2 selected, no rename. See
   `docs/RENAME-S5400.md`. Next candidate must pass the same exact-span/name test.

0. (s5399) Audited `fake_func_800B58B4`: generated body, entry table,
   companion fake/real boundary, and syms size agree, and the committed
   generated tree was already named `playerAwingInitPreamble`; H3 selected,
   no generated change. See `docs/RENAME-S5399.md`. Next candidate must pass
   the same exact-span/name test.

0. (s5398) Completed the bounded generated-symbol renaming sweep for
   `func_8000040C`: generated body, entry table, companion hard-coded
   `0x34`-byte span, and syms mapping agree; renamed it to
   `clearMemory16ByteBlocks`. See `docs/RENAME-S5398.md`. Next candidate must
   pass the same exact-span/name test.

0. (s5389) The s5388 indirect-site audit is a DUPLICATE of s4821/s4998/s5357 (class closed; no raw indirect lowering exists). Backlog exhausted; BLOCKED for a human-chosen direction (BLOCKED.md). No conclusions overturned.

0. (s5388) Direction block s5387 re-scoped (not escalated): NEXT.md = offline audit of all unguarded indirect-call/jr-ra sites (option a). Open dependency: human may redirect to a new milestone (mission gameplay/audio/render fidelity) or authorize rename sweep. No conclusions overturned.

0. (s5383) Title-boot SIGSEGV si_addr=0x58 (plume MetalFramebuffer ctor, ~1/7 launches): diagnostic print `[plume-null-color-attachment]` + backtrace landed (build-only, unexercised, no positive control possible). Grep future run logs for it; the first hit names the createFramebuffer caller. Do not guard until the writer is named. (s5386) s5385 soak hit the 600 s cap (rc=137) after 11 of 16 boots: 10/11 reached title (origin=0x00790400, positive control), 0 breadcrumb, 0 CRASH/SIGSEGV. With s5384 that is 18 title boots clean; at a 1/7 rate p(all clean)=(6/7)^18~0.06, so the crash rate is probably well below 1/7 or the trigger changed. STOP plume soaking; a 16-boot recipe needs ~60 s/boot, so cap recipes at ~8 boots per 600 s. (s5385) s5384 soak 8/8 titles, 0 breadcrumb, 0 crash = uninformative null (p~0.29 at 1/7); extended to 16 boots via soak_queue/s5385_plume_null_watch16.sh, read its summary first. (s5384) Queued scratch/agent/soak_queue/s5384_plume_null_watch.sh (8 title boots, exits nonzero on breadcrumb/crash); read its summary in SOAK-RESULTS.md first. No overturned conclusions this session.

0. (s5376) Hangar route n=5 interactive: 3/5 hangar (try4 title-boot SIGSEGV si_addr=0x58, 37 CRASH lines; try5 key-timing miss); with s5375 5/7 vs soak 0/2. Route is flaky, not proven soak-only focus. Next: classify run4.log crash, add retry-on-no-hangar to the census recipe.

0. (s5375) Hangar route: 18:30 binary reaches hangar 2/2 interactively; s5373 soak 0/2 was host/soak-context, not a build regression (n=2, single-source). Next: n=5 interactive vs soak of the same recipe, then redo the mission census.
- s5374 (first): s5373 control FAILED (s5099 recipe verbatim, 18:30 binary: title reached, hangar 0/2, 0 CRASH). The s5371 env delta is cleared as cause. Separate H1 (18:30 build regressed title->hangar; deltas 2bb94123, 8c27834d, 6392e160, s5368/s5370 census patches) from H2 (host focus/key delivery) by building the s5099-era commit (git log around 01:28 on 2026-10-17) in a separate build dir and running both binaries with the identical recipe in one iteration. Not blocked on a human.

0. (s5379) CLOSED: a5370 census validated by positive control (`tools/apply_s5379_census_ctl.py`, ROGUESQ_A5370_CTL=1 -> slot0=96 g2=92 g2bad=0 at ent=6144); normal arm and s5378 mission run slot0=0, so allocDLB tail guards are unreachable on the title->mission route. g3 counter has no control (never fired even forced). The s5379 norm-arm SIGABRT is classified (s5380): SDL_QUIT -> exit() -> terminate in static destruction, a shutdown artifact, not a guest crash (single-source).

0. (s5370) Path census (`tools/apply_s5370_path_census.py`): on boot/title, ent=12288 with
   slot0=0 -- cached slot 0x801163B0 never empty, so head/walk guard sites are unreachable by
   construction. Mission still unmeasured (s5371: manual run_a5370.sh failed again, nohangar at
   199 s; same title-window numbers). Queued `soak_queue/s5371_path_census_mission.sh` (the
   s4964 route + census env); read its SOAK-RESULTS line + `[a5370]` rows in its run1.log.
   slot0=0 at mission closes the thread. See scratch/agent/NEXT.md.

1. M4 CLOSED as legitimate (s5354): retail cxd4 at the mapped PCs 0x012C/0x07F0
   shows transient `-32768` VACC lanes in 657/657 hangar (512-wide) graphics
   tasks (61,195 + 54,382 samples), task-end zero in all 2,172 tasks -- the
   same shape as the port. No accumulator mitigation; nothing to name. Re-open
   only if a port task-END record ever shows `-32768`.
2. M5 and the M3 j/jal idiom list are exhausted (s5349); do not revive
   without a new discriminator. Re-open M3 only as a complete idiom-class audit.
3. s5381: SDL_QUIT path now `quick_exit` (was `exit()` -> static-destruction std::terminate SIGABRT, s5380 single-source). Build-only; verify on the next run logging "SDL_QUIT received" (no CRASH after it). Any SIGABRT with that line is now a regression, not a guest crash.
   The generated-symbol sweep is parked; re-open only if a new placeholder
   candidate or companion-map evidence appears.
4. Patch-layer guard sites are UNREACHED on the hangar route (s5368). A
   counter-only 0x100-alignment census (`tools/apply_s5368_align100_counter.py`,
   run `scratch/patchq/ab/run_a100.sh`) shows `allocateDisplayListBuffer` entered
   >=4096 times in each of two concurrent arms that both reached hangar 512
   (~2100 phase-5 log lines each), yet the free-list head sites (guard2) and the
   walk loop-back site (guard3) executed 0 times; the forced-true control arm
   (`ROGUESQ_A100_CTL=1`) also printed 0, so the sites themselves are not
   reached (entry counter is the same-run reach control). Consequence: the
   0x100-alignment question is moot for hangar; the free-list walk guards are
   dead there. Next: same binary on the mission route (NEXT.md); if still 0,
   the inlined walk guards are dead on the whole qualified route -- document
   and stop guarding that path.

Session 5354 detail: retail run `tools/oracle/run_m4_retail_pcs.sh`
(RS64_RSP_MID_STRIDE=1 + new RS64_RSP_MID_PCS filter; rdplog video,
README press schedule reaches 512 @ `0x6ab400` at 38.4 s), analyzed by
`tools/analyze_m4_pc_phase.py` (phase join = Nth RSD1 gfx task == Nth
`[rdp] sync=`; 2172==2172 control). See `docs/REVISIT-S5354-M4-RETAIL-PCS.md`.

## Evidence index

Use `PORTING-STATE.md` for exact session details; never read it whole. Use
`docs/PROJECT-OVERVIEW.md` for migrated durable history, `docs/M5-AUDIO-PLAN.md`
for audio inventory and validation, `docs/F5-UCODE-REFERENCE.md` for the
microcode contract, and `scratch/agent/SOAK-RESULTS.md` for queued soak
verdicts. The next iteration must read this file, `scratch/agent/NEXT.md`, and
the tail of the soak results before acting.

## Session 5343 status

Open dependency (NOT blocking): fresh PatchesLib source qualification needs a
MIPS64 ELF cross-toolchain (INSTALLED 2026-10-17: mips64-elf-gcc 14.2.0, see Durable state; absent s5337/s5342/s5343 only). Existing-artifact qualification stands. The unblock iteration (s5344)
re-scoped the loop to an offline delay-slot/branch-operand hazard audit
(`scratch/agent/NEXT.md`).

- s5351: no un-run work unit remains; loop BLOCKED pending human choice (BLOCKED.md).
- s5355: backlog still exhausted; BLOCKED.md asks human to pick toolchain install / new target / stop.
- s5349: the 2 residual uncovered j/jal targets are dead (constant-false bltzal into data gap; overlay header word). M3 idiom list exhausted.
- s5348: direct j/jal into overlay-aliased VMAs CLOSED (19,974 j/jal; 84 cross-section calls into vrams covered by 2-3 sections: 84/84 emitted as LOOKUP_FUNC, 0 direct; tools/audit_overlay_alias_calls.py --generated; positive control = 6,238 unambiguous cross-section calls correctly detected as direct). Residual: 2 data-misclassified targets (jal 0x8334B334 @8009D978, j 0x80000000 @800A5130) fail only if executed.
- s5347: lwl/lwr/ldl/ldr/swl/swr/sdl/sdr split-pair class CLOSED (930 halves: 459 adjacent, 4 straight, 0 split by branch/target, 4 lone libc halves; tools/audit_lwl_lwr_split.py, self-tested). ELF overlays alias VMAs; next class: direct j/jal into aliased VMAs.
- s5346: branch-in-delay-slot and branch-likely+mem-slot idiom classes are EMPTY in the main ELF (0/40,028; tools/audit_delay_slot_branch_in_slot.py, self-tested). Closed. Next M3 class: lwl/lwr pairs straddling a branch target (closed s5347).
- s5356: unblock re-scoped loop to offline M3 indirect-control-flow idiom audit (NEXT.md); toolchain remains open dependency.
- s5357: indirect-idiom table done (177 jump tables, 0 defects, positive control 4/4; docs/M3-S5357-INDIRECT-IDIOM-TABLE.md). Backlog exhausted; only the toolchain dependency (human) remains.
- s5358: toolchain re-checked absent; BLOCKED.md asks human (install toolchain / new target / stop).
- s5359: unblock iteration confirmed block (route 4); human to confirm/permit a MIPS-capable clang or install a toolchain.
- s5362: toolchain re-measured absent; BLOCKED.md re-asks human (install / new target / stop).

## s5377 note
Title-boot SIGSEGV si_addr=0x58 (1/7 launches, single-source) is in plume MetalFramebuffer ctor (null attachment texture at the 640 mode switch); renderer-side, unguarded, writer unnamed. s5377_census_mission_retry soak queued.

- (s5390) Direction block s5389 re-scoped: NEXT.md = render-fidelity framebuffer diff at mission origin (port vs oracle). Indirect-site audit is a triple duplicate; do not redo. MIPS toolchain remains an open human-gated dependency.

- (s5391) M6: `scratch/agent/m6_hold.sh` added. r1: autopilot route reaches hangar at 24 s, 880 s hold with 0 crash/0 stall, but autopilot never enters the mission. Next: keyed route to mission (s5378 recipe), >=3 holds of >=10 min.

## s5392 note (M6 keyed route)
`scratch/agent/m6_keyed_hold.sh` (keyed title->hangar->mission hold harness) exists. First run: 0/5 launches reached hangar; all parked at origin 0x696100 with ~110k `[s3290-stall]` lines, no CRASH (single-source). Key delivery is unverified (no positive control) — next work unit is NEXT.md. Next-steps #1: make the keyed route reach the mission, then >=3 holds of >=10 min.


### s5393 M6 correction
0x696100 and 0x690400 appear in UNKEYED launches at ~76 s / ~97 s and the game returns to title by ~167 s: that is the attract loop, so origin 0x690400 alone does NOT prove a playable mission. Keys (winctl) have not reached the game since s5377 (positive control s5393 failed with trusted=yes, rc=0); a macOS RS64_patch_c crash modal was on screen. `[pad-sdl] site=key` is not a valid key witness (0 in good s5099 run). Next: NEXT.md.

### s5414 M6 retraction
v2/v3/v4 "clean mission holds" (s5409-s5413) are the unkeyed ATTRACT loop: v4_a frame hashes repeat bit-identically 4x (period ~4000 swaps, ~167 s phase cycle), no hangar origin 0x6AB400. Not evidence of mission stability. Recipe now rejects attract (ATTRACT-ONLY, rc=1). Real M6 blocker remains key delivery (s5393/s5394): get winctl keys to the game, then hold the hangar->mission route.

### s5394 M6 key delivery
Dead keys in s5377/s5392/s5393 = crash-report modal on screen; kill UserNotificationCenter before key-driven soaks. After that `m6_keyed_hold.sh s5394a 600`: 1 run, 600 s hold clean (0 stalls, 0 crash lines), single-source. Next: >=2 more holds, then 10+ min each; capture a backtrace on any failure.

- (s5411) M6 stall detector fixed: counts `[vi] update_screen` rows with a synthetic positive control; earlier v2 "0 stall" results were against a spam-masked detector. v3 a/b/c queued.

- (s5415) Keyed control s5415a: modal cleared, winctl trusted=yes, title 0x790400 reached, hangar 0x6AB400 NOT reached in att1 (nohangar). Dead keys not explained by the crash modal alone. Next: NEXT.md (in-run SDL key witness, H1 vs H2 split).

## s5416 note (key delivery SOLVED)
winctl keys never reach SDL: macOS refuses to activate the game from the harness (lsappinfo isfrontmost=NULL; SDL_AddEventWatch witness [keywitness] saw 0 key/focus events with a same-run positive control). Not a title->hangar regression. Use in-process `ROGUESQ_AUTOPILOT` (m6_keyed_hold.sh now does): s5416a reached hangar, mission t=81 s, 204 s hold clean (single run). m6_keyed_ap_{a,b,c} queued. Supersedes the s5393/s5394/s5415 'dead keys' open questions.

## M6 flown-hold resolution (s5421/unblock)
The s5420 mission-exit-to-title at ~634 s was caused by the autopilot 'r' key. Control arm (no 'r', NOR=1) stayed in the mission (origins 0x620400/0x690400) for the full 1105 s hold, 0 crash/0 stall; the 'r' arm returned to title (0x790400). Do not use 'r' in flown holds.

## s5426 addendum (flown render fidelity)
RT64 parser accepts ~100% of submitted flown triangles (mission 3,709,507/3,710,659). H4 narrowed to post-parse GPU drops; H3 untested because FB_DUMP_DIR needs a pre-created directory (mkdir -p). Next: mkdir fbd, re-run, view mission frames.

## s5427 addendum
Mission framebuffer dump viewed (fbd now mkdir'd by m6_keyed_hold.sh): frames show sky, ~10px horizon sliver, green ship, HUD; title control renders fine. H3 (partial readback) refuted. Open: pitched-up camera (A) vs post-parse terrain loss (B) vs terrain never submitted (C) — single-source, see NEXT.md for the finer-cadence dump.

- **s5428 mission render (single-source, visual):** horizon moves with pitch and sand ground renders; earlier "ground ~10px" was camera framing. Terrain relief in free flight still unchecked (see NEXT.md). Dump interval: ROGUESQ_FB_DUMP_EVERY / FBD_EVERY.

- **s5429 flown render (single-source, visual):** 613 s hold clean; dune relief renders at VI 3000/6000/9000 (A selected, B/C refuted for terrain). The mission ends in MISSION FAILED between VI 9000 and 12000 (autopilot does not fly), so later hold time is the results screen. Next: make the hold a real flight (flight keys) or stop treating hold length as flight time; see NEXT.md.

- **s5430 (single-source, visual):** 310 s keyed hold, dumps every 10 swaps: no Mission Failed frame by swap 7470; goals overlay appears 3x (periodic HUD vs restart unresolved). See NEXT.md.

- s5430 follow-up: mission start = logo crawl + wingman flyby (swaps 2250-2450) then flight; no restart observed. Goals-overlay recurrence still open.

- s5431 (single-source, visual): 568 s keyed hold, dumps/20 swaps: flight ~swaps 2800-4400 then persistent MISSION GOALS screen to swap 16400 (emblem animating, not frozen); preceded by flight => not a restart. s5432: z-only autopilot (start only for t<=74 s) still hits the goals screen (~swap 8000), so `start`-pause is refuted as sole cause; B (mission-end flow) vs C (ship death) open. **s5433 (visual, single-source; 480 s z-only hold, dumps/4 swaps): the "goals screen" IS the MISSION FAILED results screen ("AMBUSH AT MOS E..., MISSION FAILED, 2 SHIPS REMAINING"), reached by a fade-to-black at ~swap 8100 from steady sky-only flight (no explosion/damage frame, HUD intact) then "MISSION" banner then results; a 300 s hold (7689 swaps) ended before onset, flight intact. So it is the game's legitimate mission-fail flow for a non-playing autopilot (objective/timer/out-of-bounds; exact trigger not read from RAM), not a recomp fault, restart or freeze. Supersedes the "goals screen unexplained" reading above.** **s5434 (909 s hold, 27078 swaps, 0 crash, 0 VI stall): results screen (this time banner "GAME OVER", completion time 0:00) persists unchanged from ~swap 8000 to the end => it waits for input; z-only autopilot does not advance it. Next: send start/other keys at the results screen to test post-results flow (title/hangar/retry).**

- **s5435 (visual+fbhash, single run):** s5434's 'terminal results screen' was a harness artifact (autopilot schedule ended at t=254 s). With `scratch/agent/m6_keyed_hold_post.sh` (a/start after LATE=520 s) the results screen advances: briefing -> flight -> hangar -> flight again over 900 s, 0 crash, 0 stall. Next: repeat x3 for endurance across mission transitions. Supersedes the s5434 'waits for input; autopilot cannot advance' reading.
- s5439: queued 3 stick/fire variation soaks (m6_keyed_var_*); verdicts pending in SOAK-RESULTS.md.

- (s5443) m6_post_late_a/b (LATE=200, 480 s) clean but stayed in flight (no VI mode change after 78.5 s; dumps at swap 7000/10000 are flight): mission-transition endurance is UNTESTED. Queued m6_res_late_a/b (LATE=340, 540 s). Single-source (visual+fbhash).

<!-- s5444: res_late soaks invalid (600 s cap overrun; `start`=pause -> MISSION GOALS overlay). Re-queued m6_res_nostart_a/b with HOLD=480, late keys `a` only. Read their summaries next. -->
