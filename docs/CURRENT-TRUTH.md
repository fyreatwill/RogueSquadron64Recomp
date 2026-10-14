# Rogue Squadron 64 Recomp — current truth

Compact operational state for [PORTING-STATE.md](../PORTING-STATE.md). Compacted
at s4798 (61 KB -> ~15 KB); the verbatim s4740-s4797 headline log, the old
"Current state" and "Active frontier" sections are archived in
[PROJECT-OVERVIEW.md](PROJECT-OVERVIEW.md) under "Archive: CURRENT-TRUTH headline
log s4740-s4797 ...". Git history preserves the pre-compaction file.

## Headline (as of s4834)

- **s4834 clear-site discriminator was route-invalid twice.** Both same-build
  default/rollback attempts reached VI 640, title 1024, 64 SP completions, and
  the existing second-wait arm/return rows, but crashed before hangar. PCM and
  phase-scoped gate controls were absent, so no Step 11 hypothesis is selected.

- **s4833 stabilized the M5 Step 11 route but did not qualify the clear edge.**
  The corrected same-build default/rollback pair used `STUB_MISSING_FUNCS=1`
  and the phase-gated autopilot; both arms reached title 1024 and hangar 512,
  with 64 SP completions, nonzero PCM source/consumer rows, and no crash or
  abort. Both emitted 40 second-wait arm rows and three wait-return rows, but
  neither emitted a `waitmusyx-spin2-clear` row. The two arms therefore show
  no yield-dependent route difference, while the required producer-clear
  discriminator remains unevaluable. The harness's broad witness label must
  not be read as proof of a clear.

- **s4832 Step 11 remains unevaluable after correcting the wait-witness driver.** The converted same-build default/rollback driver initially reached title and hangar with SP/PCM controls but had not armed `ROGUESQ_LOG_WAITMUSYX_SPIN2`, so its zero wait count is invalid. The fixed rerun stopped before VI 640 in default and crashed in rollback (36 rows); neither emitted phase/gate/wait witnesses. No Step 11 hypothesis is selected. The oracle precheck was blocked by a missing debugger-core dylib, so no new retail null is claimed.

- **s4831 M5 Step 1 is qualified on the corrected same-build pair.** The
  corrected harness compared Factor 5 image (`ROGUESQ_AUDIO_UCODE=1`) against
  the silent control (`=0`) using the documented multi-press autopilot. Both
  arms reached title 1024 and hangar 512 with 64 SP completions and no
  crash/abort. Phase-5 PCM source samples were nonzero in the image arm
  (`nz=768`) and zero in the silent arm (`nz=0`), selecting image downstream
  activity rather than a route-only explanation. The prior s4823/s4829
  request-only pair remains invalid for Step 1; do not repeat it.

- **s4830 A9/A10 replay passed its fixup discriminator but not whole-file
  identity:** the pristine generated copy replayed with `failures=0`, A10
  reported 44/44 sites, and A9 reported 13 sites plus its writer. All four
  selected files differed from the live tree because the live files retain
  later diagnostic patches (for example s4784/s4700 and s4597/s4601); this is
  replay drift, not evidence that either A9 or A10 failed to replay.

- **s4829 M5 Step 11 A/B is route-invalid at the wait discriminator:** the
  corrected same-build default/rollback pair reached title and hangar, with
  SP completion and nonzero PCM source/consumer controls in both arms and no
  crash. Both arms showed second-spin arm and loop-return activity, but neither
  showed the required producer-clear/seed witness or a wait-contract return;
  both loop returns reported `yields=0`. The route therefore does not exercise
  the A12 second-wait difference, so no yield-safe or yield-causal conclusion
  is selected.

- **s4828 crash-path capture:** the corrected same-build default/request-only
  pair again produced the task-validity positive control: 64 matching start
  and 64 pre-conversion enqueue rows per arm, all in-range, with no rejected
  pointer or `0x400128d47`. Both arms reached phase 3 / VI-640 and stopped at
  the same gate; neither emitted a native crash marker. This retains
  intermittent route instability as the only selected explanation for the
  absent crash and rules out the validated conversion/start/enqueue path in
  this run. Do not repeat this capture without a new discriminator.

- **s4826 host-boundary audit:** a corrected same-build default/request-only
  pair qualified the task-validity positive control. Both arms showed the same
  in-range task pointers and fields at `osSpTaskStartGo` and pre-conversion
  enqueue; neither emitted a rejected pointer or `0x400128d47`. The pair still
  stopped at the VI-640 gate (64 SP completions each), so no request-only
  lifecycle conclusion is selected and the intermittent malformed-pointer
  crash remains unobserved. The conversion/start/enqueue path is not the
  source in this capture; a native crash capture is still required.

- **s4825 startup-boundary audit:** the default and request-only arms share
  the first SP task, queue/message, type-0x81 dispatch, LLE task, and one SP
  completion. Request-only crashes before any `[sp-yielded-ab]` row, so its
  `osSpTaskYielded` exchange did not run. The `0x8000834c` breadcrumb is the
  `drainMeshReleaseQueue` return delay slot and is stale attribution. This
  selects a common pre-VI-640 scheduler/host boundary, not request-only
  lifecycle causality; exact pointer writer remains open. See
  `docs/M5-S4825-STARTUP-BOUNDARY-AUDIT.md`.

- **`ROGUESQ_OVL2C_DROP` was dead code since s4773 (s4802).** The splice route preceded the drop branch, so every DROP=0/1 A/B compared the splice with itself. Now `ROGUESQ_OVL2C_MODE` 0=splice (default) 1=drop 2=none (`tools/apply_s4805_ovl2c_mode.py`, fixup synced). s4806 three-arm run (single run each, cross-run caveat): routing 0x2C cuts phase-3 RDP submissions ~3x (513k vs 1.53M unrouted), but phases 5/6 are identical in all arms (~254k / ~955k) and the splice adds no measurable texrects at the mission origin. The old "0xBD arrival <=> runaway" claim does not extend to phase 6. VI-640 phase 3 lasts ~50 s in every run (s4803); transient `stalled=1` lines there are normal.

- **VI-640 stall = presentation-side symptom (s4797, same-run `sample` control).**
  At a live `vi-fs stalled=1`, `update_screen` ordinals advance and the Gfx
  thread is active in `RT64::State::updateScreen`/`processDisplayLists`, while
  guest MAIN is parked in `submitGfxFrame -> waitForPostSwapAck`; the synth
  thread is separately in its message wait. Rejects audio-main-wait and
  producer-thread-stalled. The stall is nondeterministic (s4794: 2/5 runs stay
  at VI 640 for 200 s, 2/5 reach VI 1024 at 55/77 s, 1/5 startup crash; s4791/
  s4792 load-sensitive, single-source). No mitigation authorised.
- **Mission route is blocked by that stall (s4796) and by input (s4774).**
  Overlay-0x2C splice (resident `OVL2C_1DB0`, built and validated s4773) is
  unevaluable: no driver has reached mission origin `0x00690400` with `res=0x2C`
  rows since s4759. Old "zero res=0x2C" nulls were void: the `[ovl-route]`
  logger had no 0x2C branch until s4787.
- **Rename sweep closed (s4795).** 8 remaining placeholders are deliberate
  `fake_func_*` boundaries; table in `docs/RENAME-S4795-AUDIT.md`.

- **s4803: splice emits sprites.** Offline frame-split phase-6 diff: m1 (drop) texrects are a strict subset of m0 (splice); m0 adds up to ~119 small sprites/frame by frame 130. s4804: retail s4733 rdp.bin contains NO mission frames (its >=100-texrect frames are menu text, 0 sprites <=8x10), so splice correctness vs retail is unevaluable until a retail mission capture exists.
- **s4823: M5 Step 1 qualification remains route-invalid.** The same-build two-arm
  harness passed its VI-640/SP positive controls in both arms, but neither arm
  reached title/hangar; it returned `H-DiscriminatorIncomplete`. Default had 4
  completion-wins rows (`returned=0`, `pending_after=1`); request-only had 7
  request-only rows (`returned=1`, `pending_after=0`) and E70/E80F rows. No
  audio or request-only conclusion is selected.
- **s4824: the documented qualified tuple is also route-invalid before VI 640.**
  After adding `AUTOPILOT + real-audio + LLE / ungated / solo / spin-yield` to the
  A/B harness, default stopped at VI 320 after 10 SP completions; request-only
  hit the known `spTaskSchedulerThread+8972` startup segfault
  (`si_addr=0x400128d47`) after one completion. Neither arm reached the VI-640
  control, so Step 1 remains unevaluable and the request-only lifecycle is not
  implicated. The harness now carries the documented tuple by default.
- **s4822: M5 Step 1 qualification remains route-invalid.** The existing two-arm
  harness reached its VI-640 positive control with 64 SP completions per arm,
  but neither arm reached title/hangar; it returned `H-DiscriminatorIncomplete`.
  A rerun with the documented qualified `AUTOPILOT + real-audio + LLE /
  ungated / solo / spin-yield` tuple failed earlier: default stopped at VI 320
  after 15 SP completions, while request-only hit the known
  `spTaskSchedulerThread+9632` startup crash (36 crash rows). No audio arm or
  SP-lifecycle hypothesis is selected.

## Current state (durable)

- **M5 A9 voice-array base guards (s4805):** 0 bad of ~2.4M checks at 10/13 sites on title+hangar (forced-bad control fired in the same build); writer `0x8008F0EC` publishes in-range `rs_malloc` bases. Guards are inert here; 3 sites (`0x8009236C`, `0x800923C0`, `0x800924F4`) unreached. Tool `tools/apply_s4805_m5_a9.py`; env `ROGUESQ_LOG_M5_A9`, `ROGUESQ_A9_FORCE_BAD=N`.

- Qualified native route: attribution, N64 logo, intro cinematic, Factor 5 logo,
  title VI 1024 (`0x00790400`), hangar VI 512 (`0x006AB400`) on the real-audio /
  LLE / ungated / solo / spin-yield route. Mission origin is `0x00690400` (512).
  Retail RDP is obtainable (hangar ≈1244 tris, 205 KB RDP). Port hangar geometry
  and colour artifacts remain localised (rim band, blue holo spikes, right-edge
  garbage = benign stale RDRAM, s4643).
- **M5 audio:** no longer a zero-output stub; nonzero PCM, AI byte order fixed.
  Step 1 image-versus-silent qualification is closed on the corrected route
  (s4831). Steps 4-13 qualified or closed on the covered route (key-on early-return valid
  s4678, status-03 writer legitimate s4680, A10 song-tempo guards valid s4681,
  AI/SDL bridge valid s4682, A11 wait cap s4691, A12 countdown wait s4692, A13
  drain default-off + timeout guard s4693). Plan: `docs/M5-AUDIO-PLAN.md`.
  A14 needs `ROGUESQ_A14_YIELD` default on; B40 default flipped to pass-through
  (s4701; rollback `ROGUESQ_M5_B40_VALUE=0`; after regen verify funcs_23.c shows
  `== '0') ? 0 : ctx->r2`). Second MusyX wait gate (`0x8014974C`) yields by
  default (s4765; rollback `ROGUESQ_AUDIO_SPIN2_YIELD=0`).
- **M5 Step 11 s4833 route result:** the route-stabilizing tuple reaches the
  qualified title/hangar phases in both yield arms. The wait logger records
  arm and return activity but no clear-site row in either arm; do not repeat
  the same A/B without a new clear-site discriminator.
- **M5 Step 11 s4834 discriminator:** the fixup source now logs every
  phase-scoped byte store overlapping physical `0x14974C` with guest PC, value,
  and thread, and the named clear row records pre/post values. Two captures
  were route-invalid before hangar; no writer-origin conclusion is selected.
- **musyxSynthFrame `+5808` crash family: closed for idle title/hangar (s4786).**
  Cause: synth ticking over the audio arena freed by the retail-legitimate
  `musyxNoopStub` teardown (s4782/s4783: retail never ticks the synth between
  free burst and re-init; the port's synth is a separate host thread and does).
  Fix: `ROGUESQ_S4562_PAUSE=4` default-on (`tools/apply_s4562_synth_pause.py`,
  rollback `=0`; hold pause until guest `initSampleStreamBlockCache` return
  `0x8008F958`); 544 s soak 0 crashes. Installed funcs_24.c once silently lost
  PAUSE=2/3 code, so PAUSE=2/3 negatives after a regen are void.
- Callback table (s4762-s4772): `musyxSynthFrame` is registered twice and
  first-match deregistration leaves a live duplicate; dispatch is all-live-slot
  (s4770); the covered route never reaches `shutdownAudioEngine` (s4771/s4772,
  single static caller `0x8008ECB8`). Do not change deregistration or dispatch.
- **Early (~3.3 s) `+9668` bus error was our own `ROGUESQ_LOG_VOICE_TRIGGER_CHAIN`
  unsigned-literal bug (s4696)**, fixed via `S32()`; older recipes that armed it
  are suspect.
- **M3 idiom classes are ALL closed** (trap/break/syscall/cop0, unaligned/ll-sc/cache (s4820) s4818, integer div/divu/ddiv/ddivu s4813, float->int TRUNC/CVT s4814, float compare/NaN s4815, ctc1/cfc1 FCSR s4816, MEM_B/BU/H/HU/W/WU, LD, lwl/lwr,
  SDL/SDR/SWL/SWR, FPR lwc1/swc1/ldc1/sdc1, LL/SC, jalr/jr indirect calls,
  backward self-referential walks, `rs_free` idiom to s4502). Tools
  `tools/census_*.py`; tables `docs/M3-S46xx-*-CENSUS.md`. No guard without a
  named writer plus legitimacy proof.
- **Runaway-DL cause (s4746-s4749):** DL op `0xBD` (TexrectGen) → overlay `0x2C`
  (real 0x240-byte VU image, ROM `0x27368`, dest `0x1DB0`) is unrouted, so the
  window entry restarts the task. Present ⇔ arrival ⇔ runaway (150/150 vs 0/550).
  Runaways: phase 3 (VI 640) and ~65% of phase 7 (mission). Splice effect on
  ship/HUD is untested (see Next steps #2). s4753: ship/HUD/radar/terrain do
  render at mission origin without the splice.
- **M4 accumulator-origin boundary: parked.** Port VMADH, VGE, store arms all
  closed on the port (s4626-s4651); retail oracle (Rice/HLE) has no RSP
  witness and no retail hangar pixels exist (s4652, s4689), so H-source is
  unevaluable.
- **Odd PI DMA:** port writes ASCII `lcre` into a cart record via FE98; the bad
  input is `0x800903F0` reading `late` from voice `+0x34` = tail of "xbkplate"
  written into a name table that voice index 30 (past the 18-slot array) lands
  in, because count 32 is published before the new base with the mixer running
  (s4577/s4580/s4708). No odd event on any canonical hangar route (s4622-s4625);
  external retail-entry handoff capture was route-absent (s4690).
- **Attached-mesh `rs_free` NULL gap** (`attachedMeshOverlayNpcHandler`
  `0x8005427C`, free at `0x80054344`): statically confirmed (s4654); retail
  handler first executes at 512-wide attract origins, not boot/title (s4656);
  mission contract unevaluated.
- **Regeneration:** full regen is unsafe since s4204 (newer N64Recomp +
  `fixup_game_funcs.py` aborts at the E088 anchor). Use `tools/apply_s*.py`.
  Safe fresh-copy fixer `tools/fixup_game_funcs_vendored.py <scratch copy>` is
  qualified in scratch only (s4649/s4653); never regenerate over
  `../N64Recomp/RecompiledFuncs` until the external fixer is repaired.
  `spTaskSchedulerThread+9632` startup crash (guest PC `0x8000834c`) is
  intermittent, not DROP-caused, not load-gated (s4790).

## Parked and closed

- M3 `jal rs_free` audit closed s4502; wild-width writeback is a named
  garbage-region SETCIMG writer — no skip without an origin proof.
- VI-640 crash families and broad M3 guard classes parked; a mitigation needs an
  `ORIGIN:` line naming the writer and whether the value is legitimate.
- External retail-entry parked (s4690); do not repeat without a new route
  discriminator.
- Hangar pillar stubs (no pixel reference; Rice retail hangar frames are wrong,
  s4645/s4731); 0x1F0D74 width-1161 premise (generic heap/DMA reuse, s4728);
  overlay-registration chunked-load H2 (s4673); right-edge col-511 noise.
- M3 patch-runtime qualification blocked on `mips64-elf-gcc`, `mips64-elf-ld`,
  `PatchesLib`.
- Generated-symbol renaming exhausted (s4646/s4795).

## Superseded conclusions to avoid repeating

## Superseded conclusions to avoid repeating

- **"Loop must wait for the owner to choose a target / no retail framebuffer reference known" (s4729).** Believable because M5, M3, the rename sweep and 0x1F0D74 were all closed and the BLOCKED question was framed around a missing reference. Overturned s4730: the retail hangar RDP capture (`s4514_rdp_hangar512.bin`, 166 MB) and oracle video-plugin runs already existed, and choosing a target is in-scope prioritization.
- **"Mission entry needs an owner-supplied recipe or savestate" (s4719-s4721).** Believable because ~10 button-press variants (s4657-s4720) never left the hangar/viewer/attract. Overturned s4722 as unproven: every variant varied button input only; forcing the mode variable in RDRAM was never tried, and the oracle reliably reaches the hangar unaided.

- “The early (~3.3 s, VI 640) `musyxSynthFrame_s4562_impl+9668` bus error /
  `0x400149714` family is a host-thread race or uninitialised voice state”
  (s4672/s4695 and the line-141/198 notes above) was wrong. It was our own
  `ROGUESQ_LOG_VOICE_TRIGGER_CHAIN` diagnostic: `MEM_W(-0X68EC, 0X80150000)`
  uses an unsigned literal, so address math yields 0x100149714 (not
  sign-extended) = read past RDRAM. Believable because it was intermittent
  (depends on what the host happens to have mapped there) and every recipe
  armed the flag. s4696: vtc=1 3/3 crash, vtc=0 0/3; after S32() fix (fixup
  source + `MEM_W(0X2038, 0X80140000)` in tickAudioSequencerFrame, same class)
  vtc=1 0/3. Any older "bus-error family" attribution in recipes that armed the
  flag is suspect.

- “M5 audio plan steps 1–10 are closed or conditionally unnecessary” was too
  broad for the current code. Nonzero PCM proves route activity, not that the
  remaining task-contract, state-ownership, wait-gate, safety-exit, and MORT
  boundaries are correct; use `docs/M5-AUDIO-PLAN.md` as the active sequence.

- `0x80007640` is not the live target writer; `0x80007670` is. The former is
  retained only as a same-run execution control.
- The five records are not in the flat `0x165D9C` source span or its 17
  visible pointer targets. Derived or alternate sourcing remains open.
- The odd DMA is not established as an audio-mixer-thread issue. Instrument-
  free arms still reach the `pi.cpp` odd-address assertion, and the bad call
  was issued by tid 1.
- The count-32 voice case is not explained by a simple bad index or an
  inert chunk-2 record. Those interpretations were tested and closed.

## Next steps

(s4834: the writer table was built, but two attempts reached only title before
crashing; retry after a new route discriminator.)
(s4833: route-stabilizing Step 11 A/B reached title/hangar in both arms, but
the clear-site witness was absent in both. Do not repeat the same A/B; make the
clear-site instrumentation itself discriminating.)
(s4831: corrected image-versus-silent pair reached title/hangar in both arms;
image PCM was nonzero while silent PCM was zero. Step 1 is qualified; advance
to the next M5 plan item.)

(s4830: pristine replay had failures=0 and both A9/A10 reports, but selected generated files differed from the live tree due to later diagnostics; classify replay as behavior-valid but whole-file comparison drift.)
(s4829: Step 11 reached title/hangar but lacked the producer-clear/seed and wait-return controls in both arms; pivot to the next M5 validation rather than repeating this route.)
(s4821: M3 indirect-jump census closed the jr/jalr class; next M3 candidates: branch-likely delay slots, HI16/LO16 pairs.)
(s4812: M5 Step 11 / A12 has a mission row: loop copies not entered (producer arm 40/40, loop rows 0), blind-spin rollback stalls at VI 640; M5 plan has no unqualified covered-route step. Next unit: M3 idiom-class audit.)
(s4811: scratch regen via vendored fixer gives failures=0 and A9/A10 tag counts match live exactly 3/15/96/11; residual diffs are post-s4653 diagnostic probes s4700/s4784 + S32() spelling. Regen chain item closed.)
(s4826: task-boundary witnesses were positive at start and enqueue in both arms, with no malformed pointer; the next capture must target the intermittent native crash path.)

Single monotonic backlog (renumbered s4798). RSPRecomp allow-rule dependency is
resolved (s4755: the tool ran; the old block was false).

0. **M5 Step 11 validation:** s4834's writer table is complete, but two
   same-build captures stopped before hangar with no PCM/gate controls. Do not
   interpret the writer null. Find one new route discriminator or stabilizing
   change, then rerun the same-build pair.
1. **M5 next behavior validation:** Step 1 is qualified by s4831. Continue at
   the next not-yet-qualified M5 plan row with a same-build rollback/control;
   do not repeat the invalid request-only route.
1. **M5 A10 replay (s4830):** the pristine-copy replay ran end to end with `failures=0`; A10 reports 44/44 and A9 reports 13 sites plus the writer. The four whole-file comparisons differ because the live tree contains later diagnostic patches absent from the s4648-fresh replay input, so the replay is valid for these two fixes but not byte-identical to the accumulated live tree. Do not repeat the replay without a new comparison target. A10 guards remain dead on covered routes; no removal is authorised.
1. **VI-640 stall: not reproducible (s4801):** 0/24 stalls since s4794 on the SAME binary (mtime predates s4794); the s4793 recipe's t=20 `sample` call is not the trigger (4+4 A/B, all reach VI 1024 at ~50 s). Cause is an unrecorded external condition. Park; if it recurs in any run, immediately capture `vi-fs stalled=1` state plus `ps`/display/load context. Meanwhile advance M5 plan.
2. **Overlay-0x2C splice evaluation:** mission origin is reached unattended at ~98 s
   (s4802/s4806), no driver needed. Frame-align done (s4803/s4804): no retail mission reference exists; parked pending oracle mission capture.
3. **M5 callback teardown:** park unless a route that reaches
   `shutdownAudioEngine` appears; keep M5 plan going otherwise.
4. **Attached-mesh mission watches:** the s4724 recipe reaches a mission; could
   revisit the `rs_free` NULL contract with mission-phase watches.
5. **Parked, do not repeat without a new discriminator:** M4 accumulator
   boundary, odd-PI DMA, col-511 noise, pillar stubs, 0x1F0D74, external
   retail-entry, rename sweep (see Parked section).

Operational notes: keep soaks <=4 concurrent; every game-launching recipe must
`pkill -KILL -x RogueSquadron64Recomp` in cleanup. Under host load 7-20 the
default recipe stalls at VI 640 or startup-crashes; judge only state-gated
(`vi-fs stalled=1`) samples, never wall-clock ones.

## Evidence and operating rules

Retail oracle watches are physical-address ground truth. Whole-RDRAM, VI, target-PC, and adjacent-range controls must qualify every null. Phase-gate animated comparisons on VI transitions. Batch all counters and A/B arms in one build/run. Use [F5-UCODE-REFERENCE.md](F5-UCODE-REFERENCE.md), not standard F3DEX assumptions. Keep safety guards separate from explanations.

Regeneration order is `make_elf.py -> N64Recomp -> fixup_game_funcs.py -> CMake`; never hand-edit generated functions for behavior. If `lib/` changes, export submodule patches in the same session. Never run submodule update, checkout, clean, or hard reset. Kill runs with SIGKILL and run from `build/` with the ROM present. Any mitigation-shaped change needs an `ORIGIN:` line.

See [PROJECT-OVERVIEW.md](PROJECT-OVERVIEW.md) for the evidence archives and [M5-AUDIO-PLAN.md](M5-AUDIO-PLAN.md) for the audio plan.
- s4817: mult/dmult lowering census closed (docs/M3-S4817-MULT-CENSUS.md)
- s4818: trap/break/syscall/cop0, unaligned/ll-sc/cache (s4820) census closed (docs/M3-S4818-TRAP-CENSUS.md); lvj_checkComplexObjectives syscall proven dead s4819 (data after an immediate return); remaining: M5 passive items
