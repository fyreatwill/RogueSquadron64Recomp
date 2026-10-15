# Rogue Squadron 64 Recomp — current truth

Compact operational state for [PORTING-STATE.md](../PORTING-STATE.md). Compacted
at s4798 (61 KB -> ~15 KB); the verbatim s4740-s4797 headline log, the old
"Current state" and "Active frontier" sections are archived in
[PROJECT-OVERVIEW.md](PROJECT-OVERVIEW.md) under "Archive: CURRENT-TRUTH headline
log s4740-s4797 ...". Git history preserves the pre-compaction file.

## Headline (as of s4897; compacted s4898)

- **Digest of s4822–s4897 (verbatim bullets archived in
  [PROJECT-OVERVIEW.md](PROJECT-OVERVIEW.md) under "Archive: CURRENT-TRUTH
  headline log s4822-s4897"; detail in each session's `docs/M5-S*.md` note):**
  - **Latest (s4897):** the Rice retail oracle passed whole-RDRAM, title and
    hangar controls and watched the full `musyxRenderVoiceSamples` range:
    it fires in title and hangar, as do the two voice `+0x34` writer PCs,
    while exact `0x800903F0` stays absent. This selects an internal boundary
    before the old exact consumer; no runtime mitigation authorized. See
    `docs/M5-S4897-RETAIL-VOICE-RANGE.md`. Next planned: s4898 retrace/
    audio-done/synth cadence join (see `scratch/agent/NEXT.md`).
  - **Shutdown/teardown (s4889–s4895):** retail shows wait -> synth
    deregistration -> reapply; the port skipped synth deregistration at the
    boot gate-0 teardown (s4889). s4890 landed a named, regen-replayable
    first-teardown deregistration fix (`ROGUESQ_S4889_FIRST_DEREG=0` rolls
    back). s4891 retired the default synth-registration dedup mitigation
    (`ROGUESQ_S4875_DEDUP=1` rollback arm). s4893/s4894: callback-table
    deregistrations do NOT prove `shutdownAudioEngine` ran; its `kind=0/2`
    markers were zero, so the route does not reach it (H3). s4892: A12
    default yield is behavior-neutral (H2).
  - **OSTask `data_size` (s4886–s4887):** retail writer `0x80091784` matches
    publications (176 ds=2, 14 ds=1); port is 3,926 ds=1 / 3 ds=2 / 5 ds=3 —
    a cadence difference, not a publication mismatch.
  - **Rename sweep (s4888, s4896):** only `func_8000040C` and `func_800E9AE0`
    remain; neither passes the three rename gates. Sweep parked pending a new
    mapping source or generated snapshot.
  - **Idiom-class audits closed (s4837–s4848, s4883–s4885):** branch-likely,
    HI16/LO16, variable shift, 64-bit shift, HI/LO move, 32-bit multiply,
    `sync`, and zero-extended `0x80000000u` (90 sites) are all classified.
    s4840–s4842 traced a live conditional-move defect to N64Recomp itself.
    s4883 named and fixed the startup SIGSEGV `spTaskSchedulerThread+9632`:
    a stale zero-extended s3293 probe skipped by an idempotence marker.
  - **Retail-entry boundary (s4844–s4845):** closed as route-absent
    (target PC `0x800903f0` never hit pre-title; oracle setup qualified).
  - **M5 qualification history (s4822–s4859):** Step 1 qualified on the
    corrected same-build pair (s4831); Step 11 producer/clear route
    qualified with the generic writer (s4836), many other arms route-invalid;
    A10 guard class legitimate on covered route (s4852); A13 drain boundary
    requalified (s4858); A16 AI-shim caller boundary closed (s4859); host
    queue edge made truthful (s4856–s4857).
  - **Mission/VI-640 (s4796–s4803):** the VI-640 stall is a presentation-side
    symptom and blocks the mission route (plus input, s4774);
    `ROGUESQ_OVL2C_DROP` was dead code since s4773; splice emits sprites.

## Current state (durable)

- **M5 retail voice-render boundary (s4897):** the independent qualified
  route reached title and hangar, and the full execution range
  `0x8008FFAC:0x80090640` plus writers `0x80090C80` and `0x800921E8` fired in
  both phases. The exact `0x800903F0` consumer remained absent. The old
  single-PC null is therefore refined to an internal pre-consumer boundary;
  do not add a skip or guard from this result. See
  `docs/M5-S4897-RETAIL-VOICE-RANGE.md`.

- **M5 callback teardown reachability (s4894 correction):** the qualified
  route passed title/hangar, 758 SP returns, 44 PCM sources, 259 PCM consumers
  and audio returns, and no crash/abort. Its seven `[s4771-cb]` rows were all
  `kind=1` callback-registration rows; there were zero `kind=0`
  `shutdownAudioEngine` entries and zero `kind=2` returns. The generated
  return marker compiled and remained absent, selecting route-level H3: this
  route does not reach `shutdownAudioEngine`. Six callback-table deregistration
  pairs and downstream audio work remain independently real, but do not prove
  that function ran.

- **M5 first-teardown deregistration (s4890):** a same-build default/rollback
  capture selected the bounded one-shot change. When gate `0` reapply saw an
  existing legitimate `0x8009123C`, default deregistered it once; rollback did
  not. Default/rollback both reached title/hangar, recorded 670/676 SP
  completions and 329 PCM rows, and had no crash/abort. Callback snapshots
  showed one synth entry after the default pre-reapply deregistration versus
  the duplicate retained by rollback until normal teardown. Rollback is
  `ROGUESQ_S4889_FIRST_DEREG=0`.

- **M5 double synth teardown order (s4889):** retail independently shows
  `waitForMusyXAudioTaskDone` -> `findAndZeroTableSlotMatching` for
  `0x8009123C` -> `reapplyAudioConfig` in four cycles. The port probe shows
  its first `musyxNoopStub` at gate `0` followed directly by reapply; the next
  teardown at gate `1` waits, deregisters the synth callback, and re-applies.
  The gate-zero branch is the named cause of the unmatched first registration.
  This named the origin fixed by s4890; it is not a general callback-table
  mitigation.

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
- **M5 Step 11 s4836 writer result:** the phase-scoped generic writer table is
  qualified on both default and `ROGUESQ_AUDIO_SPIN2_YIELD=0` arms. The exact
  producer/clear PCs are `0x80091680`/`0x800912F8`; the named clear logger is a
  stale/missing generated anchor, not evidence that the clear is absent. The
  observer crash was diagnostic-only and is fixed by host-thread identification.
- **M5 A12 s4892:** default `ROGUESQ_AUDIO_SPIN2_YIELD=1` and rollback `=0`
  both passed the producer-arm, wait-return, task/SP, PCM, title, and hangar
  controls with no crash/abort. The 43/43 producer/wait witness totals select
  route-neutral behavior; retain the rollback arm but make no A12 change.
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
- **M3 branch-likely delay slots are closed (s4837).** Static census and
  control-shape pass cover all 893 sites; no annulment defect was found. See
  `docs/M3-S4837-BLIKELY-CENSUS.md`. Reachability of every site on the
  qualified route was not claimed.
- **M3 variable shifts are closed (s4839).** Static source census and
  register-aware semantic pass cover all 469 direct sites; no width, count-mask,
  signedness, or intervening-write defect was found. See
  `docs/M3-S4839-VARIABLE-SHIFT-CENSUS.md`.
- **M3 conditional moves are statically mistranslated (s4840).** All 179
  generated `movz`/`movn` sites emit `do_break`, including 115 nonzero
  destinations; the raw decoder independently validates all 144 `.word`
  encodings. s4841's static CFG finds one reachable nonzero-destination site;
  runtime impact remains open and no fix is yet authorised.
- **M3 conditional-move provenance (s4842):** the reachable site is a valid
  source instruction but is unsupported by the current N64Recomp operation
  tables, not altered by the fixup pass. A recompiler-side implementation and
  route qualification remain separate future work; do not hand-edit generated
  output.
- **M3 HI/LO moves are closed (s4846).** The retail-ELF decode and generated
  lowering agree at all nonzero-destination decoded sites; zero-destination
  rows and 26 stale/unavailable annotations are confined to data-like or
  unreachable generated regions. No guard or recompiler change is authorized.
- **M3 64-bit shifts are closed (s4847).** The complete retail-ELF/raw-decode
  and generated-lowering census found no reachable nonzero-destination defect;
  no guard or recompiler change is authorized.
- **M3 32-bit multiplication is closed (s4848).** All decoded `mult`/`multu`
  rows have the expected lowering; 27 stale annotation rows are not
  multiplication words in the retail ELF. Do not repeat this census without a
  new recompiler or annotation-provenance hypothesis.
- **External retail-entry boundary (s4845):** the Rice/input oracle route is
  qualified through title and hangar, with whole-RDRAM control positive, but
  `0x800903F0` has zero execution hits. The retail handoff is absent on this
  route; do not repeat the setup without a new route or PC discriminator.
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

- **s4879:** synth-register dedup (tools/apply_s4878_synth_dedup.py) is now DEFAULT ON (`ROGUESQ_S4875_DEDUP=0` disables): 0.99 vs 1.97 synth entries/msg, 2/3 DEDUP=1 runs alive at 100 s, 1 startup SIGSEGV (known intermittent family, unattributed). s4880 RESULT: arm1(dedup on) 0/5 crashes vs arm0 2/5 -> dedup NOT the cause; crash = zero-extended guest ptr 0x80128d44 in MEM_BU base reg (x9=0x100128d47); writer still unnamed (s4881).

## Parked and closed

- M3 `jal rs_free` audit closed s4502; wild-width writeback is a named
  garbage-region SETCIMG writer — no skip without an origin proof.
- VI-640 crash families and broad M3 guard classes parked; a mitigation needs an
  `ORIGIN:` line naming the writer and whether the value is legitimate.
- External retail-entry parked (s4845): Rice/input route is qualified through
  title and hangar but has zero `0x800903F0` hits; do not repeat without a new
  route or PC discriminator.
- Hangar pillar stubs (no pixel reference; Rice retail hangar frames are wrong,
  s4645/s4731); 0x1F0D74 width-1161 premise (generic heap/DMA reuse, s4728);
  overlay-registration chunked-load H2 (s4673); right-edge col-511 noise.
- M3 patch-runtime qualification blocked on `mips64-elf-gcc`, `mips64-elf-ld`,
  `PatchesLib`.
- Generated-symbol renaming exhausted (s4646/s4795).

## Superseded conclusions to avoid repeating

- **s4893's claim that the qualified route reached `shutdownAudioEngine`** is
  superseded by s4894. It was believable because the shared `[s4771-cb]`
  helper emitted seven/nine rows alongside deregistration and downstream
  controls, but s4894 decoded the discriminator: those rows were `kind=1`
  registration events, not the `kind=0` shutdown-entry event. The generated
  function contained the new `kind=2` return marker and emitted none. Do not
  treat callback-table activity as shutdownAudioEngine execution.

## Superseded conclusions to avoid repeating

- **"Port retrace delivery is bimodal/bursty (0/2 per VI) vs retail's steady 1" (s4899-s4900).** Believable because per-update_screen rows showed R=0 in 4341 and R=2 in 4294 VIs. Overturned s4901: update_screen runs 2x per true origin change; per origin change the port is steady at 2 (retail 1), so the gap is 2:1 frame pacing, not burstiness.
- **"M5 needs human authorization for the data_size writer trace; no de-stub step remains" (s4863).** Believable because every M5-AUDIO-PLAN step was closed and the trace looked like a new build+run. Overturned s4864: builds/runs are already permitted by ITERATION.md, and the data_size 1-vs-2 question is still an open, cheap discriminating experiment.
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

0. **M5 retrace pacing vs update_screen (s4899 result, next):** s4899's joined
   per-VI table (docs/M5-S4899-CADENCE-JOIN.md) closed the cadence join: synth
   entries == retrace-queue returns == audio-done messages (hangar R=9217 T=9217
   A=9224 S=9216 over 9237 update_screens); chain `R A W T S`; no double synth
   per retrace, no independent audio-done delivery. The visible "1 vs 2 per VI"
   is bimodal aliasing (R=0 in 4341 VIs, R=2 in 4294). Remaining question:
   does retail run synth at ~1 per retrace with the SAME retrace:update_screen
   ratio, or does the port deliver/handle retraces at half the retail VI rate?
   Measure in one unit (retrace returns per VI-origin change) on both sides.
   **s4900 answer:** retail (oracle, control passed) = 1,302 hits / 1,301 origin changes, 94% of intervals exactly 1 (steady). Mean agrees with port; shape differs (port 0/2 bimodal per update_screen).
   **s4902 answer (single-source):** port swaps at ~30 Hz (wall dt med 33.35 ms) over true 60 Hz retraces (16.4 ms apart) => H-vi-rate refuted. Swap lands 0-11 ms (med 3.8) after the 2nd retrace, not ~0 => leans H-slow-frame over a strict divider. Next: timestamp gfx-task-done vs R1/R2 (scratch/agent/NEXT.md).
   **s4903 answer (4,641 rows):** gfx task begins R1+0.1 ms, dp_complete at R1+20.7 (begin->done med 20.6 ms wall, p10 19.6/p90 21.7) > 16.4 ms retrace; swap 0.1 ms after done. => 30 Hz is H-slow-frame-gfx (host send_dl latency); H-divider and H-slow-frame-other refuted. Next: split the 20.6 ms inside send_dl (scratch/agent/NEXT.md).
   **s4904 answer (two concurrent arms, 3,780 sends each):** send_dl mean 23.2 ms = RT64 State::fullSync 11.3 + RDP submit (procDL minus fullSync) 7.0 + LLE RSP 4.8 (+fbwait 0.8). Logging env vars irrelevant (arms identical). H-debug-overhead, H-present-wait refuted; LLE RSP not dominant. 30 Hz = host RT64 cost > 16.4 ms retrace. Next: is fullSync cost reducible/scene-driven (see scratch/agent/NEXT.md), or is 30 Hz acceptable and the retail-1 vs port-2 retrace gap now explained.
   **s4905 split of fullSync (11 ms/frame):** render fb-pair loop 5.2 + present-early tail 3.5 + texture evict/profilers 1.9; GPU waits ~0, uploads 0.05, flush/submit 0. Resolution multiplier had no effect (unqualified: no control). Timers: `ROGUESQ_S4267=1`, `ROGUESQ_RESMULT`. Next: split those three buckets, or park 30 Hz as host-bound and return to M5.
   **s4907 (supersedes the "host-bound, PARKED" reading below):** the build is CMAKE_BUILD_TYPE=Debug = bare `-g` = -O0, and RT64 was never optimised (s38 only fixed the ucode TUs). `updateScreen` 3.9 ms is NOT a present wait (usAdvance 0 ms, control passed); it was present.storage resize 1.6 + XXH3 1.1 ms on 344 KB at ~0.3 GB/s. `ROGUESQ_RT64_OPT` (default ON; CMakeLists `target_compile_options(rt64 PRIVATE -O2)`) cut sendDl ~23 -> ~8.5 ms/task and fullSync ~11 -> ~1.9 ms (concurrent A/B, both reached hangar, 0 crashes; -O0 binary kept as build/RogueSquadron64Recomp_O0). Task rate stayed 30/s, so the remaining 30 Hz limiter is elsewhere (guest code at -O0 or the frame limiter), untested; see NEXT.md. Do NOT globally raise optimisation of recompiled guest code without the s67 DCE caveat (-O1/-O2 DCE'd an IMEM region). Shader-regen gotcha: a global flag change regenerates shaders and `xcrun metal` is missing here; recover with `zsh scratch/agent/s4907_touch_shaders.sh`.
   **s4908 (single-source, control passed):** VI-queue recv thread blocked ~98% of wall (60 VI recvs/s, 30 swaps/s); a 10 ms sleep per osViSwapBuffer did NOT lower swap rate (blocked ms fell -370, CPU 690->495 ms/s). => H-guest-O0 refuted for the swap thread; limiter is a 2-VI wait in game logic (H-frame-limiter). Knob: `ROGUESQ_S4908=1`, `ROGUESQ_S4908_SLEEP_MS`. Next: find the guest wait that consumes the second VI message (scratch/agent/NEXT.md).
   **s4911 (single-source, control passed):** all VI-queue recvs share ONE guest site (viRetraceHandlerThread+2188, 60 iter/s) -- no divider there. The 30 Hz element is the gfx thread (tid 3): submitGfxFrame 30/s, waitForPostSwapAck (0x8001C260, mq 0x80128CF0) blocks 60/s ~810 ms/s. Knob: host-ra table under `ROGUESQ_S4908=1` (`[s4911]` rows). Next: read waitForPostSwapAck C + log sender of mq 0x80128CF0 (NEXT.md).
   **s4912 (two sources: C + run):** waitForPostSwapAck loops recv until byte 0x8011A8C8 is cleared, and that byte is cleared only by advanceVideoFrame AFTER it signals the frame-sync msg. Recvs/call flip 1 -> 2 mid-run (not a fixed design count). H-design-2ack refuted; H-late-ack (flag clear lands after first wake) leads.
   **s4913 (control passed; a ^3-swizzle bug was caught by it):** flag A (0x8011A8C8) at the first ack wake is 1 in 36/36 two-recv waitForPostSwapAck calls and 0 in 239/239 one-recv calls => H-late-ack is the mechanism of the 2nd-VI wait (= the 30 Hz). But A drops 1->0 between the wakes with NO entry of clearPostSwapPendingFlags (3 calls / 12k events); the only set/clear byte stores in funcs_*.c are those two functions => the clearer is unnamed. Title-phase window only. Knob `ROGUESQ_S4913=1`; tools/apply_s4913_marks.py. Next: name the writer of 0x8011A8C8 (NEXT.md).
   **s4909 (single-source):** VI-queue recv trace: same thread (tid 0) blocks twice per swap, swap <=0.45 ms after 2nd recv; guest PCs not distinguished. Fits host-slow frame; no guest divider evidenced. Next: default rt64 -O2 and re-measure swaps/s (scratch/agent/NEXT.md).
   **s4910 (control passed):** with RT64 at -O2 (default) swaps still 30-31/s over 60 VI recvs/s; +10 ms sleep in osViSwapBuffer absorbed by the VI wait (blk ms -350) with no swap change. Frame now fits < 1 retrace (s4907 sendDl ~8.5 ms) => H-host-slow refuted; leading: guest 2-retrace wait (intended 30 fps or a gate closed one VI). Next: capture guest ra at each VI-queue recv for tid 0 (thread-local guest PC) to see which two guest call sites block.
   **s4906 final split (control passed: 2 ms sleep -> ctlSleep 2.3 ms/frame, fsTiles +2.2, fsRender +1.9):** per-frame fullSync ~12.9 = fb-pair tile loads (fsTiles) 3.1 + renderAndSynchronize 3.2 + hashTracking/advanceFramebufferRenderer 2.3 + present-early `updateScreen` 3.9 (+~0.4 misc). texture evict itself ~0, script ~0, render-target resize ~0. 30 Hz is host-bound; PARKED. Only open lead: updateScreen 3.9 ms may be a swapchain acquire/vsync wait rather than work (not tested). Timers: ROGUESQ_S4267=1, ROGUESQ_S4267_SLEEP=1 (control). Resume M5 audio de-stub (docs/M5-AUDIO-PLAN.md).
   **s4901 answer:** per TRUE fb-origin change (osViSwapBuffer fb change) the port is steady at 2 retrace returns (hangar 4642/4644; title-640 285/325), retail steady at 1. The 0/2 was update_screen aliasing (2 update_screens per origin change). Real gap = 2:1 frame pacing (single-source each side). NEXT: swap rate in Hz port vs retail + the game's frame-limiter/retrace-per-frame variable (slow-frame vs divider vs VI-rate).

0. **M5 callback teardown boundary (s4894):** the qualified route does not
   reach `shutdownAudioEngine`; s4894's generated entry/return marker and the
   callback-registration kind control distinguish this from a non-return. Do
   not repeat the same route or add more return fields. Revisit only with a
   genuinely new callsite/route discriminator; otherwise proceed to the
   generated-symbol sweep after its required last-15-session preflight.

1. **M5 double synth walk (s4874-s4875, closed by s4890):** the port's
   duplicate callback origin was the gate-zero first-teardown gap. s4890's
   one-shot deregistration fixes the named origin; retain s4878's dedup only as
   rollback context while testing its retirement.

1. (s4896) The available generated tree still has only `func_8000040C` and
   `func_800E9AE0` placeholders. The former has no companion semantic mapping;
   the latter is an intentional companion placeholder with no caller because of
   a documented false split reference. No rename is authorized. Keep the
   generated-symbol-renaming-sweep is parked until a new snapshot or mapping
   source supplies a candidate with companion mapping, live callers/body, and
   exact span agreement. Next take the external retail-entry boundary with a
   genuinely new discriminator; do not repeat the prior `0x800903F0` watch.
2. (s4887) The qualified same-build port capture closes the OSTask `data_size` boundary as H-port-cadence: writer/ABI values agree, while port is 1-dominant and retail is 2-dominant. The blind retail `0x80091084` watch remains unusable; do not repeat it. M5 task-family work is closed; continue the M5 retrace/audio cadence boundary before the generated-symbol renaming sweep.

(s4836: Step 11's generic writer table qualified arm/clear and wait-return rows
on both arms after removing the observer crash; do not repeat the A/B.)
(s4837: branch-likely census matched all 893 generated sites; do not repeat
the class. Continue the next complete M3 idiom census.)
(s4846: HI/LO move census matched all decoded nonzero-destination sites; do not
repeat the class. Continue with the next complete M3 idiom census.)
(s4847: 64-bit shift census matched all 162 reachable nonzero-destination rows;
do not repeat the class. Continue with the next complete M3 idiom census.)
(s4848: 32-bit multiplication census matched all 643 decoded rows; 27 stale
annotation rows were raw-word mismatches, with the positive control passing.
Do not repeat the class.)
(s4838: HI16/LO16 census matched all 3,015 canonical pairs; do not repeat the
class. Continue with the next complete M3 idiom census only when M5 has no new
discriminator.)
(s4839: variable-shift census matched all 469 direct sites; do not repeat the
class. Continue with the next complete M3 idiom census.)
(s4840: conditional-move census found all 179 sites emitted as do_break;
s4841's CFG found one reachable nonzero-destination site; s4842 traced it to
N64Recomp's missing conditional-move operation support. Do not repeat the
fixup audit.)
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

0. **M5 host queue validation:** s4856 changed the host bridge to reject failed
  SDL queue calls from the PCM consumer join. Run the phase-gated source,
  host-error, queue-delta, and consumer controls before interpreting the
  Step 10 boundary. **Closed s4857:** both arms had zero host errors and
  matching nonzero source/consumer PCM joins; do not repeat without a new
  host discriminator.
0. **M5 A16 AI shim caller qualification:** closed s4859 as
   H-A16-unreached. The qualified image route reached title/hangar, completed
   SP work, and produced nonzero PCM, but only `set-next` entered the AI shim
   (`1024` phase rows); `get-status` and `get-length` were both zero. Retail
   independently reached title/hangar and showed nonzero AI length plus busy
   status. Do not change the status/length shims or repeat this caller probe.
   Select the next M5 contract boundary with a fresh route discriminator.
0. **M5 task-family retail/port qualification (s4887):** the independent Rice-route
   capture passed the whole-RDRAM control (10,000 writes) and reached hangar
   origin `0x006AB400`. Retail store PC `0x80091784` fired 703 times; 190
   phase-gated type-2 publications at `0x80033FCC` matched sampled writer
   values (176 `data_size=2`, 14 `data_size=1`). The candidate upstream watch
   `0x80091084` fired zero times. s4887's corrected same-build port capture
   passed route-order, SP, hangar, and PCM controls; ABI rows were 3,926
   size-1, 3 size-2, and 5 size-3, matching the observed writer values.
   This selects H-port-cadence and closes the boundary; no runtime behavior
   change is authorized. Do not repeat the blind upstream watch.
0. **M5 task family (s4860):** the qualified route publishes one stable audio task family (0x80149470, type 2, ucode 0x80099FE0, data_ptr 0x80171CE0 title / 0x80171E70 hangar, data_size mostly 1), joined to 2104 SP completions and 79 nonzero PCM rows; s4854's "rows absent" was a control artifact. s4861 retail oracle (hangar only, control passed): same task 0x80149470 type 2, zero output, data_size 1-2 (retail 194x2/22x1, port mostly 1), data_ptr slot differs (ring slot). Class matches; ratio unexplained (single-source). s4862: retail data_size ratio reproduced (title 572x2/53x1, hangar 188x2/22x1, control passed, port now shares data_ptr slots): retail ~90% size 2, port 1-dominant — a real, unexplained difference (single-source on port side). Next: name the OSTask data_size writer on both sides (see NEXT.md). s4863: data_size = frame-batch counter 0x80149760 (stored at 0x80091784 in musyxSynthFrame, OSTask+0x34); no host-shim writer; likely cadence (single-source static). M5 plan has no step left; BLOCKED for direction. s4870: synth chunk loop bound = AI-ring index (byte 0x801496F0, writer runAiAudioStreamPlaybackLoop 0x8008EE6C) delta per synth entry: retail +2, port +1 (cap hw 0x8014974E=3 never binds). Next: who posts value-1 msgs to queue 0x80149670 and what wakes the synth (single-source retail). s4871: messages per synth entry retail 1.91 (1345/704, control passed) vs port 0.50 (steady, run-lifetime): port wakes synth ~2x per AI-done message. Next: per-entry caller/r31 of 0x8009123C on both sides (two registrations?). s4872: retail single caller 0x80019B74 (VI-retrace callback walk); port retrace walk ~117/s = ~2x VI updates, AI-done ~59/s = 1x VI updates (strict 1,0 alternation) - cadence difference, not two registrations. Next: who posts retrace-queue messages in the port (2/VI?) and the AI-done driver (1/VI vs retail ~2/retrace); join retail VI updates per retrace.
0. **M5 port-task-load contract:** s4854 found both the port-load control and
   rows absent despite positive title/hangar, SP, action, and PCM controls.
   This is a single-source route result; do not infer a task-contract defect
   or repeat the same control without a new route discriminator.
0. **M5 task-contract qualification:** s4855 was route-invalid: the image
   harness crashed at `0x400128d47` before title/hangar, so task-contract,
   lifetime, and PCM controls were absent. Revisit only with a new route
   discriminator; do not classify the absent rows as a contract mismatch.
0. **M5 descriptor target:** s4853 found the exact `0x800377C8` descriptor
   control unreached despite title/hangar, SP, action, and PCM positive
   controls. Do not repeat the same target; select the next M5 contract
   boundary with a route-specific control.
0. **M5 A10 guard-class qualification:** closed s4852 as H-A10-legitimate.
   The same-build default/guard-off pair had qualified route-order SP controls,
   32 writers, 262 identical audit/traversal rows, title/hangar, and nonzero
   PCM in both arms. No guard relaxation is authorized; do not repeat this A/B.
1. **M5 next behavior validation:** Step 1 and Step 11 are qualified by s4831
   and s4836, and the Step 8 A10 guard class is closed by s4852. Select the
   next unqualified M5 contract boundary with a fresh positive control; do not
   repeat the invalid request-only route or the A10 A/B.
1. **M3 multiplication class:** closed s4848. The 643 decoded rows all have
   expected signed/unsigned lowerings; 27 stale annotation/ELF mismatches are
   not live multiplication instructions. Do not repeat without new provenance
   evidence.
1. **External retail-entry boundary:** s4845's single-PC null is superseded
   by s4897's qualified range capture. The route reaches the voice-render
   range and both selected writers, but not `0x800903F0`; the remaining work
   is an M5 internal boundary/cadence discriminator, not route qualification.
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

- s4873: port VI thread is the only poster of VI queue 0x80114388 (1/VI; trace 2321 enq vs 2304 update_screen) and posts AI-done 1/VI by design; synth entries still 2.0 per VI message (strict 1,0). AI_EVENT_HZ=115 doubles msgs (control) but not synth entries. Doubling is inside the guest retrace handler / recv shim. Next: log osRecvMesg returns (calls at 0x800198F4/0x80019928) per walk.
