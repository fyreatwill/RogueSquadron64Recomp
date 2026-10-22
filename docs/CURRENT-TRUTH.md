# Rogue Squadron 64 Recomp — current truth

Compact operational handoff, maintained as of Session 5816 (2026-10-21).
`PORTING-STATE.md` is the chronological ledger. Durable background, closed
audit detail, and the per-thread histories moved out of this file are in
`docs/PROJECT-OVERVIEW.md` (latest: "Migrated from CURRENT-TRUTH (s5636)");
per-session evidence is in the named `docs/*AUDIT.md` files and soak results.

## Headline

- **Route.** The qualified image route boots through attribution, N64 logo,
  intro, Factor 5 logo, title (`0x00790400`, VI 1024), hangar (`0x006AB400`,
  VI 512), and mission origins (`0x00690400` / `0x00620400`, VI 512; the
  alternation is baseline double-buffering). Mission input reaches flight code.
  The default audio route is active; `ROGUESQ_AUDIO_UCODE=0` is the silent
  control.
- **M6 first-mission endurance: CLOSED.** Gate closed s5394 (904 s / 900 s
  holds); since then 31 keyed title->mission holds (251 min) and 10/10 long
  holds incl. the hangar route, all 0 crash / 0 stall. This is route
  endurance, not proof every mission subsystem is correct. Keyed holds end in a
  legitimate MISSION FAILED screen (idle autopilot loses; loss counter
  0x80138064) and fall back to title — not a hang.
- **M6 death thread (s5779-s5783): RESOLVED as a test-input artifact.** The
  life losses via `[bit8call]` -> `updatePlayerCraftPhysics` -> terrain sampler
  (`sampleTerrainAtNpcPosition`, ret=1 iff scaled y > cell byte3) happened only
  when our synthetic input climbed the craft into the level ceiling: s5777's
  `ROGUESQ_ALT_HOLD` latched target y=0.000 pre-spawn and held stick-up
  forever (fixed s5783), and s5738's schedule has scripted `su` steps.
  s5783_noalt (same route, no vertical input, 421 s): 0 deaths, craft sinks to
  ys -370, sampler never ret=1 (single run; controls fired). Port sampler/physics
  behave as designed; no mitigation. The unpoked LOSE at ~+342 s (s5627) is a
  separate, still-unexplained path. Next: G1 mission progression with real input.
- **M5 audio de-stubbing: CLOSED** for the qualified route (non-silent PCM,
  task/SP contract, keyed mission and long-hold rows; `docs/M5-AUDIO-PLAN.md`).
  **Audio FIDELITY is OPEN** (rung G2, `tools/agent/ITERATION.md` 3c): owner
  report 2026-10-19 — every SFX recognizable but behind a heavy fuzzy/noise
  layer, and no dialogue/voice at all. Owner has watched several missions
  besides Mos Eisley play (rung G1).
- **M4 accumulator comparison: PARKED** at the cross-arm gate after the s5570
  rank-bin (empty lane masks) and s5575 task-total-bucket (0 shared classes)
  discriminators; H3 selected, no writer or mitigation inferred. Do not repeat
  either comparison or add another indirect join field.
- **Generated-symbol sweep: EXHAUSTED** (s5574; 0 companion-backed renames
  left). **M3 listed idiom classes: EXHAUSTED** (s5561). **Regen determinism:
  CLOSED** (s5547). **Title-boot plume SIGSEGV (si_addr=0x58): probably
  dissolved** by the s5597 `poke_be32` overflow fix (28 clean boots,
  P(0/28 | p=1/7) ~1.4%; hypothesis, no writer named).

- **G1 lv0 evidence chain (s5799-s5813, detail migrated):** projectile-direction block is live (H8b/H10b: firing object's mesh attachment); real-input holds are stable 600 s with no win (s5804/s5805); counter 1 (class-1 NPC kills) climbs only via npcProbeDriod teardown (8 sets), 47/54 class-1 NPCs get msg 2 (silent destroy) vs 8 msg 5 (counted) (s5811-s5813). See s5814 note below.
- **G1 bit-3 setters (s5817):** slot +0x14 bit 3 is set only by destroyNpcSlotByIndex (13 callers, each its own update fn; bulk = effects/debris/audio cues) and a grid setter that never touches NPCs. Class-1 NPC subset: npcGroundTroopUpdate 45, npcProbeDriod 56, npcWakeUpdate 17, npcWingmanUpdate 4 of 3032 sets. No external setter. Open: are those destroys legitimate (health<=0) or early?
- **G1 class-1 destroy cause (s5818, single-run):** all 50 npcGroundTroopUpdate self-destroys in a 400 s invuln hold came via funcs_39.c branch 0x800E8450: `isNpcWithinActiveReferenceRange(npc)==0` for 21 consecutive updates (+0x67 counter), health positive, no objective bool/counter gate. Open: is the range check/reference (isPointXzWithinRangeOfRef, thr float 0x8003A7D4, ref = craft record 0 or 0x800AEA18 when 0x80130B39!=0) correct in the port, i.e. are NPCs despawned only because the reference is wrong/stale?
## Active M6 thread (summary; detail migrated)
- Unpoked mission end ~+342 s is the LOSE arm (bool 0x64/0x65, b14=2, same-level restart; s5627). Hypotheses S/T/R/O refuted; bool 7 is a level-F dialogue flag (sayWhoaHim_v0x1FC), not a port defect (s5694). Voice requests, alloc, pool and decode all run in the port (s5641-s5666); missing dialogue is downstream, at decoder output (G2).

## Durable state

- **Native hangar artifacts parked:** rim band, holo spikes, stale right edge,
  Factor 5 overlay splice, accumulator origin, pillar references, `0x1F0D74`,
  odd PI DMA. No mitigation without naming the writer and establishing value
  legitimacy.
- **PatchesLib is shadowed on macOS (s5366):** ld64 never pulls the patch
  `allocateDisplayListBuffer`; live heap guards are the fixup-inlined
  `s_alloc_tail_guard*` (`tools/check_patches_shadowed.sh`). Patch-layer claims
  in older entries are unsupported for this build; `-force_load` is a
  behaviour change needing its own A/B.
- **allocDLB guards** (s5378): all counters 0 on a mission route but no
  positive control, so not shown dead.
- **Hangar route is flaky** (~1/3-3/5 launches reach hangar).
- **MIPS cross toolchain installed** (2026-10-17, `mips64-elf-gcc` 14.2.0 in
  `/opt/homebrew/bin`; check with full path). Fresh source-to-ELF patch
  qualification is unblocked but not yet done; the existing-ELF -> host path is
  qualified via `tools/fixup_patches_host.py` (s5341).
- **ASan arm:** `tools/build_asan.sh` -> `build_asan/` (slow); keyed holds with
  `BUILD=` in `m6_god_common.sh`.
- **Tooling caveats:** `ROGUESQ_FB_DUMP_DIR` assumes stride 320 (garbled at
  other widths). lldb LAUNCH fails in loop context (getcwd EPERM); lldb ATTACH
  works. Every soak recipe's line 2 must be the zsh re-exec guard; a 0 s rc=0
  soak is a null. `# SOAK_TIMEOUT=<s>` header sets a per-recipe cap. Full logs
  are `scratch/agent/m6/<tag>/run.log`.
- Closed reference material (RSP null guard, SDL_QUIT, M5 contract, M3 audit
  list, symbol sweep, M4 schema history, regen determinism, plume history,
  second-mission selector refutations): PROJECT-OVERVIEW s5636 section.

## Operational rules

- **Audio output routing (owner feature, 2026-10-19; code inside d1c534be5).**
  `build/audio_device.txt` (gitignored) pins the output device by
  case-insensitive name substring; owner set `MacBook Pro Speakers` so test
  runs play on muted laptop speakers. `ROGUESQ_AUDIO_DEVICE` overrides it;
  `default` follows the system output. F9 cycles outputs live and rewrites the
  file. Do not delete or change the file, and do not treat `[audio-route]`
  lines as M5 evidence.
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
- Re-open a closed M3 class only with new recompiler/provenance evidence, and
  audit a whole idiom class rather than a single crash.
- Static `jal` does not maintain r31 in generated code: an `ra` log column is
  always 0 and cannot identify callers.
- A VI origin is a framebuffer address and is content-blind; do not judge
  mission/content selection by origin alone (s5508).

## Superseded conclusions worth retaining
- **s5800 lookup attribution:** believable because the prior bounded read conflated a nearby generated-code address with the call site; superseded s5801 after the exact `jal` was checked. `0x800CA3E4` is `getObjectMeshTransformOrLocal`, while `lookupHmtTextureByName` is `0x80058360` and is not called by the direction producer. The upstream position-difference conclusion remains valid, but its semantic source changed to an active object/mesh transform path.
- **s5799 H8a "no target-position subtraction in the producer":** believable
  because the runtime `[pblk]` writer table ended at the cross/normalize and
  jitter intermediates; superseded s5800 after the caller was read statically
  and showed `lookupHmtTextureByName` position minus droid position upstream.
  The s5799 live-writer and non-stale conclusions remain valid.
Older superseded items (s5634-s5777: R/O hypotheses, ccosnap, mission-win pokes, lldb/plume nulls, voice-DMA guesses, slotwatch addresses) migrated to PROJECT-OVERVIEW 'Migrated from CURRENT-TRUTH (s5815)'. Pattern for all: a null without a same-run control, or a mis-derived address, read as a result.
- **'Prerequisite gate (+0x28/+0x2C>=+0x30) or 0x80130B39 holds counter 1 at 8' (s5808 candidate):** believable because applyDat's gate and the b39 skip were the only visible conditional paths. s5809 measured gate fields 0 and b39=0 with only 2 trigger calls, so neither blocks; the missing increments are never attempted.

## s5814/s5816 note (G1 lv0)
Class-1 NPC msg 2 (47 of 54) = `slotDispatcherIter` -> `destroyNpcSlotByIndex`; msg 5 (8) = handler-chain kill. **s5816 corrected the mechanism:** slot byte +0x1A is a reentrancy depth counter (inc before / dec after the update call; post-update value is 1 in 99.99% of 2.88M visits), NOT a lifetime countdown, so there is no timeout. Destroy runs when depth returns to 0 and +0x14&8 is set; bit 8 is a destroy-REQUEST flag (set post-update only 3083 times in 405 s). The s5814 "timeout" reading was believable because the +0x1A/+0x14&8 pair sits right at the destroy branch. Next: name the writers of slot +0x14 bit 3 for class-1 NPCs.

## Next steps (single monotonic backlog)

- **s5831 (top, single-run):** tally of messages by descriptor class at updateDestructionDebrisNpc: cls1 zero (control cls0/2/3 >100k msgs); msg-5 hits (dmg 12) land on cls0 (6) and cls2 (236). Class-1 NPCs never use that function; next: tally at slotDispatcherIter by slot +0x70.
- **s5830 (top):** msg-2 question closed (out-of-range despawn, 4 lines). Next: damage path to class-1 NPCs (NEXT.md).
- **s5828 (top, measured, single-run):** [spawn1] now prints id=desc+0x78 + descriptor words (words 4-6 = float x,y,z). 10 class-1 spawns, ids 2B,1F,18,19,20,21,28,29,2A,2D, all within ~40 u of idle player; only 2 counted. Id space >= 0x18..0x2D (22), so s5827's bound is loose; unreached ids ARE spawned and torn down silently. Next: what decides counted (msg 5) vs silent (msg 2) teardown for class-1.
- **s5827 (offline, single-source):** counter 1 is per distinct bool id: 44 class-1 spawns -> 8 sets with 8 distinct ids (0x18..0x2B range, ~20 ids). 21 needs nearly every id once = reach more distinct NPCs. Next: map id -> descriptor position from lv0 DAT vs the 8 reached.
- **s5826 (top, offline, 4 logs):** s5824's mission end was the FAIL arm (counter 2 reached 3: class-2 descs 0x80319e5c/cce/a9c all destroyed; only e5c dies in no-fire runs), not a win; ctr1=8 alone ends nothing (s5825_aonly alive). Win arms need get(1)>=21 or get(10)>=6, neither near. Next: who destroys cce/a9c (fire vs other) and where class-1 count 21 / counter 10 would come from.
- **s5825 (top, single-run per arm):** B-only 6, Z-only 6, A-only 8 ctr1 sets, same schedule: fire keys are NOT needed for counter-1 kills; they come from approach alone. Qualifies s5824's fire attribution. Next: why only s5824 ended the mission at 8; find the win check.
- **s5824 (top, single-run):** real input, NPC_INVULN unset (scratch/agent/g1_fire.sh): objective counter 1 rose 2→8 (first kill during A/B phase, none in A-only control) and the mission then ended (endMissionCleanup, origin 0x620400) with no memory poke. Fire-does-nothing refuted. B vs Z attribution unseparated (approach accumulates). Crash at end is the known s5818 instrument (needs regen). Next: B-only vs Z-only runs; identify what 8 means / win condition.
- **s5823 (top, measured, single-run, with in/out control):** 29/29 ground-troop self-destroys (via=3) coincide in the same VI with an out-of-range result, d2 151-198 vs thr 144. Despawn-by-design confirmed; a second destroy path is not needed. Next: ship fire (find the fire button, hold with A) and watch counter 1 / hp<=0 kills rise past 8 (g1_approach.sh variant).
- **s5821 (top, measured, 2 identical-schedule runs):** the player ship does NOT move from stick input (su/sr/sd held 40 s each: pos frozen at (42.70,-6.5,44.99)); it moves ONLY while A (0x8000) is held, ~2.2 u/s along (x,z) (el 361->380: (42.7,45.0)->(73.8,87.8)); the s5820 tap schedule (150 ms/3 s) was ~5% duty, hence 'barely moves'. Ship also moves during the z/start title-nav presses (el 79-125) then freezes. Next: hold A continuously with the NPC bearing, re-test the ground-troop range gate (ROGUESQ_LOG_PLPOS=1, ROGUESQ_AUTOPILOT_HOLD_MS=2500, scratch/agent/g1_pos.sh). Mission-end crash fix in apply_s5818 (cap 300) is NOT in the current build (live RecompiledFuncs already fixup-stamped; needs full regen) - keep holds <350 s.
- **s5819 (top, measured, single-run):** ground-troop out-of-range despawn is by design as implemented: ref == player craft (0x80137DC0), sane coords, NPC d2~187 vs threshold 144 (scaled 0.25) while player idles. Next: fly toward the NPC (stick-forward schedule) and check destroys drop / counted kills rise (g1_inv1.sh variant).
- **s5811 (top, measured, single-run, 8/8 ids backtraced):** the 8 counter-1 sets come from npcProbeDriod's NPC-teardown path (after unregisterAndFreeNpcSlot/popNpcSlotFromTail, funcs_36.c:23881 and :24901; args from descriptor +0x70/74/78/7C/80/84), NOT a DAT trigger table. Counter 1 = class-1 (+0x70==1) NPC teardowns. Next: count class-1 descriptors SPAWNED vs torn down in lv0 (NEXT.md).
- **s5810 (measured, measured, single-run):** updateDestructionDebrisNpc is NOT the counter-1 feeder: 175 spawns tallied classes 0/2/3 only, zero class-1 (+0x70==1) and zero +0x80==1 descriptors; yet the 8 a2==1 `[ctr1]` sets still fire from another caller (ids 0x18,19,2B,1D,1B,1C,29,2A, st10=110..112; `ra` log is stale). Supersedes s5808's NPC-descriptor reading for counter 1. Next: backtrace the 8 sets to name the caller, then count that caller's sources in the lv0 DAT (NEXT.md).
- **s5809 (top, measured):** unbudgeted `[ctr1]` log (405 s hold, NPC_INVULN=1): exactly the 8 known bool ids write counter 1 (0->8), none after; applyDatObjectiveTriggerEffect ran only 2x with prereq fields 0 (gate open); 0x80130B39==0. H-gate and the b39 skip are refuted (single run). Open: H-supply (only 8 counter-1 sources in lv0 DAT) vs H-port-skip (other handlers unreached). Next: one-shot NPC-descriptor scan listing a2==1 entries + npcPredictedRangeCheck call count (NEXT.md).
- **s5808 (static, single-source, now partly measured):** counter 1 is descriptor-driven (datItem adds a3 to counter a2 per NPC descriptor; setObjectiveBoolean touches no counter), so 'one increment per new bool' is wrong. Only 8 bool ids ever set.
- **s5807 (top):** with ROGUESQ_NPC_INVULN=1 objective bools advance (…1E, 2A, 29) and counter 1 climbs to 8 then plateaus (s5806_inv1 and an 1800 s hold s5807_inv1long, both alive, 0 stall/crash, no win). lv0 success arms: get(1)>=21 (arm D, needs B6A4==0,B6A8==0) and get(10)>=6 (arm C); get(2)>=3/get(3)>=9 are fail-ish. Bool-gate hypothesis refuted; static read is single-source. Next: log counter store sites + dump lv0 DAT items targeting idx 1/10 (NEXT.md).
Closed diary s5694-s5806 (death thread, kill-setter hunt, level-select, bool-7 voice lead, NPC_INVULN lever) migrated to PROJECT-OVERVIEW. Key survivors: bool 7 is a level-F bool (not a port defect, s5694); deaths on the idle route follow terrain-sampler ret=1 from synthetic climb input (resolved s5783); `ROGUESQ_NPC_INVULN=1` is a test-only lever that advances objective bools but does not win.
3. **Name the bool[1]/bool[7] writers** for the 0x64 fail arm (neither is set
   via the one logged setObjectiveBoolean site); fold with `[ccosnap]`.
4. **Give the mission soak real or invulnerable flying** so mission 1 can be
   won (idle autopilot fails it, s5627); mission-2 endurance depends on it.
5. **G2 audio fidelity:** diagnose the fuzzy/noise layer and the absent
   dialogue/voice path (owner report 2026-10-19); requires retail-comparison
   evidence, not just non-silent PCM.
6. **Fresh MIPS source-to-ELF patch qualification** now that the cross
   toolchain is installed (optional; existing ELF path already qualified).
7. **Plume recurrence watch (passive):** any CRASHMARK/BREADCRUMB or
   si_addr=0x58 in a future soak -> lldb attach backtrace, name the writer.
   Do not spend iterations on more clean-boot loops.
8. **Parked, re-open only with a genuinely new discriminator:** M4
   accumulator, retail-entry byte, native hangar artifacts, hudbit4 chain,
   mission-win pokes, PatchesLib `-force_load` A/B.
9. **OPEN DEPENDENCY (human):** declare the project goal met or name a new
   target (raised s5530/s5585; still open).

## Evidence index

Use `PORTING-STATE.md` for exact session details; never read it whole. Use
`docs/PROJECT-OVERVIEW.md` for migrated durable history, `docs/M5-AUDIO-PLAN.md`
for audio inventory and validation, `docs/F5-UCODE-REFERENCE.md` for the
microcode contract, `docs/M6-OBJECTIVE-COUNTER-WRITERS.md` and
`docs/M6-PHASE-MACHINE.md` for mission logic, and
`scratch/agent/SOAK-RESULTS.md` for queued soak verdicts. The next iteration
must read this file, `scratch/agent/NEXT.md`, and the tail of the soak results
before acting.

Voice-path (s5637-s5666), mission-transition (s5748-s5754), counter-2 (s5787-s5797) and misc update diaries migrated to PROJECT-OVERVIEW 'Migrated from CURRENT-TRUTH (s5815)'. Net: voice data exists in RDRAM and decodeAndFillVoiceBlock runs, but the buffer content is rail-saturated decoder OUTPUT (suspect runVoiceLatticeFilter 0x8009D980, s5666); counter 2 = class-2 NPC tally fed by updateDestructionDebrisNpc, victims die to real projectile hits (s5793).

- s5820: g1_fly soak ended the mission cleanly (origin 0x620400 at ~353 s) but crashed in our own s5818 instrument during endMissionCleanup (fixed in apply_s5818_destroy_health.py, not rebuilt). Autopilot stick barely moves the player (~0.05 u/update); 'does approaching keep troops alive' is still open.

- s5822: holding A (ship loops, idle->moving) takes ground-troop gtdest from 0 (idle) to 27 in 130 s; d2 at destroy not observed ([rng] cap 20/result spent early). Despawn-by-design consistent but not selected vs a motion/collision destroy path. Next: key the [rng] log to gtdest (full regen).

- **s5829 (single-run + code read):** class-1 descriptor words don't discriminate counted (0x18,0x19, deterministic across runs) from silent; counted sets come via npcProbeDriod copy 2 (L_800CBCBC, msg-5 death-effect arm), the +0x6C gate (copy 1) never fired. Next: find the msg-2 sender for class-1 NPCs.
