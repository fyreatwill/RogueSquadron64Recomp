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

The M4 accumulator comparison (s5321-s5405) is parked: the port/retail join is
structurally impossible with current schemas (no ucode image identity, local task
serials); H3 selected, no writer or mitigation authorized. Next discriminator would
be phase epoch + image identity + mapped IMEM PC + normalized task progress
(`docs/REVISIT-S5404-M4-NORMALIZED-BOUNDARY-DESIGN.md`, `tools/analyze_m4_normalized.py`).
Details of s5321-s5395 are archived in `docs/PROJECT-OVERVIEW.md` (CURRENT-TRUTH compaction).

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

