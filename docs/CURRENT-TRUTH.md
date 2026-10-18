# Rogue Squadron 64 Recomp — current truth

Compact operational handoff, maintained at Session 5396 (2026-10-17).
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

The sweep is paused after the remaining mission-overlay placeholder
`func_800E9AE0`: its exact body span is known, but the companion map supplies
no semantic name and no live caller. Session 5336 rechecked the stale
`0x800927B0` NEXT item and found every generated, registration, project-map,
fixup, and companion surface already synchronized. Preserve names that are
already synchronized, data symbols, and unmaterialized host-wrapper entries.
Only rename a real generated placeholder when the companion map and generated
tree agree. Audit files are `docs/RENAME-S*.md`.

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

## Next steps (single monotonic backlog)

0. (s5396) Resume the bounded generated-symbol renaming sweep. Select one real
   placeholder outside the already-audited `func_800E9AE0`, and rename it only
   if the companion map and generated tree agree on the same function span and
   semantic name. Record the candidate census and agreement test in a new
   `docs/RENAME-S5396.md`; leave it unchanged if the evidence is incomplete.

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

### s5394 M6 key delivery
Dead keys in s5377/s5392/s5393 = crash-report modal on screen; kill UserNotificationCenter before key-driven soaks. After that `m6_keyed_hold.sh s5394a 600`: 1 run, 600 s hold clean (0 stalls, 0 crash lines), single-source. Next: >=2 more holds, then 10+ min each; capture a backtrace on any failure.
