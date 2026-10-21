# Rogue Squadron 64 Recomp — current truth

Compact operational handoff, maintained as of Session 5783 (2026-10-21).
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

## Active M6 thread: objective booleans and the 0x64 fail arm

State as of s5635 (all static claims single-source unless noted):

- The unpoked mission end at ~+342 s is the LOSE arm: boolean 0x64/0x65 set,
  b14=2, gate 0->4->6, same-level restart (s5627). Failure is
  nondeterministic, 2 of 7 runs overall.
- Static: the 0x64 fail arm needs `bool[1]==1`, `bool[7]==1`,
  `bool[0x63]==0`, `bool[0x65]==0` (s5628); ids 1/7 are not set via the single
  setObjectiveBoolean (0x800C7540) site that was logged.
- Instrument: `[ccosnap]` boolean-array snapshot (fixed s5629 with a
  `(gpr)(int32_t)` cast; s5628 snapshots invalid); `[cco]`/`[objbool]` logs
  carry wall time and rate-limited counts (s5625); `ROGUESQ_LOG_HUDBIT=1`.
- Hypotheses: S (static bool 7) and T-fixed (fixed-time) refuted s5630 — the
  2/2 surviving runs never set bool 7; D (event-set bool 7) leads. O
  (run-dependent id base) replaced by R s5632: the per-run id shift (3->1,
  D->B; 0x20/0x7F/0x80/0x47/0x48/0x3C/0x3B fixed) is a legitimate
  `randMod(3)+1` pick at 0x80102158 (funcs_43.c ~19200-19207). **R refuted
  s5634:** env-gated force of the draw (s5633) with `[objdraw] forced=1`
  control fired: force0_{a,b} (id forced to 1) 0/2 fail, force2_a clean, so
  `bool[1]==1` is not sufficient. `s5633_force2_b` still queued.
- **s5635 lead:** the only static constant-id-7 setObjectiveBoolean caller is
  `sayWhoaHim_v0x1FC` (funcs_48.c:4395, a voice-line script entry). Bool 7 is a
  dialogue flag, so the fail arm links to the voice/dialogue path — which is
  exactly what G2 reports as missing (no dialogue). Single-source static.
- **s5642:** s5641_spath soaks show tickSpeechSubsystem -> enqueueSpeechClip -> allocAndConfigureNewVoice all run (30/30 in one run); alloc has early-outs (B094/B0A8/B0D8, `a0 < *0x80154670`). `[aloc]` instrument built, soaks s5642_aloc_{a,b} queued.
- **s5644:** queue 0x80154650 is a pool lock (recv/unlock pairs), NOT a consumer queue. Real consumer = serviceVoicePoolFrame -> serviceStreamingVoice (slot+0x11AC queue) -> consumeVoiceSamples. `[vdown]` instrument built (tools/apply_s5644_voicedown_log.py); soaks s5644_vdown_{a,b} queued.
- **s5643 (2 soaks, a/b, [aloc] control = entry+[spath] lines present):** allocAndConfigureNewVoice entry cnt(0x80154670)=0x222 >= every clip id, all 4 first slot-used bytes 0 => no pool bail; reach_B1F4 (initMusyXVoiceSlot) and reach_B220 (findVoiceSlotByAge) fired 16/16 (a) and 17/17 (b); label_B230 bail never. Selects H-C3: the port DOES allocate and start speech voices (osSendMesg to queue 0x80154650 at B218). Refutes H-C1/C2/C4. Missing dialogue is DOWNSTREAM of alloc (audio-thread consumer of 0x80154650 / voice slot 0x1200 state / sample DMA / ucode mix). Two soaks agree.
- **s5641 voice funnel (2 soaks, single-source):** `playObjectiveVoiceLine2` IS entered and each call reaches `playSpeechClip` through every early-out gate; playSpeechClip is a 16-entry ring enqueue that drains (g72 16->13->16). "Script never requests voice" is refuted. Gap is now the consumer `tickSpeechSubsystem` (0x80067300) -> enqueueSpeechClip -> allocAndConfigureNewVoice; `[spath]` instrument built, soaks s5641_spath_{a,b} queued (NEXT.md).
- Parked side branches: hudbit4 chain (s5617-s5623, setHudEnableBit4/8 only
  via lvN_checkComplexObjectives + script stubs; `ra` always 0); mission-win
  pokes (`ROGUESQ_MISSION_WIN`, `_REAL`, `_NOPOKE`; the one s5612 B14=1 win
  never reproduced, 0/4). Machinery reference (B14 result code, gate
  0x8010CA20, flagword 0x8010C9E0, 7738/776C setters) is in PROJECT-OVERVIEW.

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
- **s5777 "spline jal 0x800B0D9C stays parked":** believable because that schedule logged 3 calls and no ret2. Superseded s5778: under climb it is the debris site for 7/9 life losses, and those losses start at `[killset]` 0x800B08DC (slot 0x0001→0x0008). The "no ret2 on that jal" part still holds.
- **s5771 "both kill-setter guest PCs stay zero":** believable because mission origin, `[mtm]`, and `[phase]` fired and both counters were zero. That route was godmode and never decremented lives (hp stayed 150, one a0=2). On the death route both setters run, and 0x800B0348 precedes every bit1 (s5773).
- **s5761 "slotwatch_god null/zero hits" (wp_hits=8):** believable because the summary printed a nonzero hit count and the run stayed alive; actually list-echo lines, and the death route was never reached (no lives-watch fire). Void, not a result.
- **s5760 "state word = 0x137F3C" (and its soak null):** 0x137F3C is craft+0x180 (rewritten 207x/run with constant 0x10000 by computeCraftSelectTurnFromInput); the slot-table address was mis-derived by 0x18, and the recipe lacked the death env so no deaths occurred. Believable because the static a1 base was read from the wrong lui/addiu pair. Correct: 0x137F24 (s5761).
- (s5728) "Suppressing bool 7 will show whether it drives the fail arm" — believable because bool 7 was the leading hypothesis; superseded s5729: in the s5728 window bool 7 is never set, so the experiment tested nothing (control failed).
- (s5692) "A level-init forwarded-a0 site may pass a0=7 and set bool 7" — believable because the three sites forward the caller's a0 unlogged; refuted by 0 id=7 lines in 56 existing [objbool] logs.
- s5682: "record +0xD0 = ship velocity" (s5681 guess) refuted - field is constant while position moves.
- (s5661) "Unaligned stores may write the voice-range rails" (H1 of s5659): believable because those were the only store forms the census had not hooked; refuted by s5660 (narrow=6 of 17.8M, positive control all>0). The rails are float bit patterns from aligned game stores.
- s5645 premise "consumeVoiceSamples reads the sample bytes" - overturned s5646 (pure counter); believable because its name and position in the voice pipeline suggest it moves data.
- "Speech DMA may yield zeros" (D1) - overturned s5647; believable because the voice is audibly absent.

Each: the wrong claim, why it was believable, what replaced it.

- (s5634) Hypothesis R "the fail arm follows the randMod(3) objective draw":
  believable because the shifted ids were real RNG picks; refuted when forcing
  id 1 with a firing control gave 0/2 failures.
- (s5632) Hypothesis O "run-dependent objective id base": believable because
  ids shifted uniformly by -2; they are legitimate `randMod(3)+1` picks.
- (s5628 [ccosnap]) snapshots invalid: believable because the instrument
  printed plausible arrays; the address was zero-extended and read wrong
  memory.
- (s5604-s5611) "gate 4 / B14=1 = mission win": believable because the poke
  changed the gate; s5612 showed get(2)/get(3) drive the LOSE arm (B14=2) and
  only get(10)>=6 reaches the win setter. Older notes also had win/loss
  reversed (s5610).
- (s5612) "WIN_REAL produces a mission win": single run; 0 of 4 later runs
  reproduced B14=1.
- (s5604 gate block) refuted as a range artifact: retries narrowed
  `ITER_START_HEAD..HEAD` to docs-only commits.
- (s5590) "s5589 lldb soak 0 crashes / bad=0": believable because summary said
  bad=0 and rc=0; titles=0/3 — the game never booted (getcwd EPERM under lldb).
- (s5601/s5602) plume nulls read as clean: believable because rc=0/bad=0 and
  the recipe looked right; controls failed (0/12 titles in 24 s).
- (s5577/s5578) "lldb is the title blocker": believable because the debugger
  was the only visible difference; the missing ingredient was the LLE env trio.
- (s5584, s5530, s5372, s5351) "needs a human direction decision": each
  premature — believable because other threads looked closed or runs had
  failed, but a queued soak / control run / offline route had not been tried.
- (s5473) "mission-end condition cannot be read: objdump not permitted":
  believable because the headless allowlist denied mips64-elf-objdump; a
  stdlib script over the ELF supplies the disassembly.
- (s5470) "requestMissionTransitionMode reached via a condition in
  runInMissionFrame": believable because grep found no `jal` and the bt showed
  that caller; the call is the `jalr` in the event-table loop and a0=2 is the
  event id.
- (s5504-s5508) mission-selector verdicts judged by VI origin: believable
  because origins differ per scene; origins are content-blind.
- (s5423) H1 "renderer drops flown terrain before the RDP": believable because
  flown frames showed only sky; flown RDP stream had 2.40M tri. Flight render
  later shown correct (s5490). Also: "endurance closed" proves no crash/stall
  only — detectors cannot see an alive-but-empty frame.
- (s5409-s5413) unkeyed "mission holds" were the attract loop (retracted
  s5414); key delivery solved s5416.
- (s5365 and older) "the patch layer provides the live heap guards":
  believable because Zelda-style link order makes overrides win; ld64 never
  links the patch member (s5366).
- Retail "never had a mid-task `0x8000` VACC lane": signed/unsigned decoder
  error; retail has such lanes in all sampled 512-wide tasks.
- Port's modal `0x03` entry byte: an unswizzled host byte census.
- Earlier "M5 fully closed" claims were too broad until the keyed mission and
  long-hold rows; and M5 closed proves non-silent PCM, not fidelity.
- Older route-blocked and host-load conclusions are historical; do not revive
  stale backlogs without a new measurement.

- **s5675 G1 soaks (no keys sent):** `s5675_g1fly_{a,b}` looked like two 'nohangar x4' flown-mission failures, i.e. a flaky hangar route. Actually `m6_god_common.sh` re-sets ROGUESQ_AUTOPILOT from its own `$AP` after XENV, and STOP=0 emptied `$AP`, so no keys were ever injected. Fixed in s5676 via `AP_OVERRIDE`. Believable because the hangar route is known flaky (~3/5) and 8/8 failures read as more of the same. The s5676 fix was itself ordered wrong (s5677 also keyless) - fixed s5678; lesson: the control is the "[autopilot] armed" log line, not keys.log `mission t=`.

## Next steps (single monotonic backlog)

- **s5786:** the s5784 life loss is lv0_checkComplexObjectives's own fail rule: `getObjectiveCount(2) >= 3` -> setHudEnableBit4 + speech 0x229 -> mtm(2) (backtrace + speech id; jal pc inferred; single run). Timer/0x64/0x65 refuted. Next: log every increment of objective counter 2 (caller + value), compare with `s5786_hudb_noalt`; find what counter 2 counts (friendlies lost?) and whether our input causes it. Instrument: `tools/apply_s5786_hudbit4_dump.py`.
- **s5787/s5788:** s5787 objcount arms logged 0 lines (control failed; game logs are in scratch/agent/m6/<tag>/run.log). s5788 added a `getObjectiveCount` change-log as positive control; arms s5788_get_fire/nofire queued. s5789: get-log control passed; counter 2 rises 0->3 with set/increase never entered (both arms). Inline writers to check: datItemSetObjectiveBooleanCount, applyDatObjectiveTriggerEffect, updateNpcEffectIntensity, executeActorType1Effect (static scan, unconfirmed).
- **s5785:** the s5784 3->2 life loss follows `[mtm] a0=2` preceded by a `setHudEnableBit4` mask store (pc 0x800C775C val=4) ~190 s into the mission; `[killset]`/`[bit8call]` = 0 (debris refuted; controls: strings compiled, s5778 fired 16). Overlay reload only decrements afterwards. Single-source. Next: identify the script caller of setHudEnableBit4 (host backtrace on pc==0x800C775C, dump objective bools/timer) - see NEXT.md. (s5784: ALT_HOLD validated, 421 s alive.)

_s5782 (top):_ terrain sampler 0x80068D5C = 2D cell grid (struct 0x80136DC0; record byte +3 vs scaled y). ret=1 iff ys > cell b3; player flies ys -130..-80 over records with b3 -126..-82; deaths follow ret=1 bands (single-source, 1 run). y=0 hypothesis refuted. Next = what b3 means (rest of the sampler 0x80069284+ branches) and whether retail spawn ys is higher (NEXT.md). Slug g1-record-byte0.
_s5781 (top):_ byte0=1 has one writer: terrain sample jal 0x80068D5C (a2=0x80138058) nonzero at 0x800FF3B4. Offline: the player rises y -2.88->-0.32 at +3.6/s identically in 3 deaths (s5738_snapa snaps) and dies at y~-0.3 (single-source). Next = terrain height at that xz vs y (NEXT.md). Slug g1-record-byte0.

_s5780:_ sp+0x175 is written by the `sb` at 0x800FFC60 from orientation record byte0, always 1 (40/40 logged stores, flag=1, idx 0; 4/4 visible bit8calls directly preceded by it; log capped at 40 so 5 later bit8calls unpaired). H-written-const; not stack leftover. `tools/apply_s5780_sp175_store.py`. Next = find who sets record byte0=1 for the player (the fill that precedes this) and which collision test drives it. Slug g1-record-byte0.

_s5779 :_ bit 0x8 is the physics jal (H-phys, 7/7, `scratch/agent/m6/s5777_althold/run.log`; s5778 log kept at `s5778_althold_kept/run.log`). Cinematic jal never ran. Do not retag the callers and do not tune `ROGUESQ_ALT_HOLD`. Next = log the only writer of stack byte sp+0x175 (`sb` 0x800FFC60: index, source byte, flag sp+0x497) on the same recipe and pair each line to `[bit8call]` 0x800B2A58. Slug g1-sp175-src.

_s5778:_ altitude hold does not stop the life loss (H-hold-still-dies). acted 0→2960 with sy=+1; 8/9 drops started at `[killset]` 0x800B08DC. s5779 named that caller. The 9th class is the closed return-2 path.

_s5777:_ the return-2 normal is a real terrain impact (H-legit, 5/5). Geometry stays closed. The altitude-hold run was s5778 and selected H-hold-still-dies.

_s5776:_ the death-route return of 2 is the terrain fill (3/3 `byte0=1`). s5777 closed the geometry question. Spline jal 0x800B0D9C remains parked.

_s5774:_ debris callers named (run.log `s5774_debris`, n=6). 4/6 player deaths are jal 0x800B2EC4 when the orientation function returns 2; 2/6 are jal 0x800B0D9C. s5776: the return-2 deaths are the terrain fill. Do not rerun the census.

_s5773:_ unpiloted level-select fail is the three-death chain (guest `[bit1]`/`[lives]` plus host `[livesbyte]`). Immediate flag writer is `spawnSceneDebrisAndEffectCluster` at 0x800B0348 (player slot 0x80137DBC, halfword -> 0x0190). Caller named in s5774.

_s5755:_ [mtmst] fold (single run): bit1 of mask 0x8010C9E0 has ONE writer, pc 0x800B1140 (funcs_30), once per mission start; no store ever sets an end/fail bit in godmode 420 s. Next = find callers/guards of requestMissionTransitionMode (0x800FB2B0). Single-source (mtmb dir missing). (s5756: godmode suppresses the fail arms, so the godmode mtm runs cannot see the end path; non-god mtm soaks s5756_nogoda/b queued, GODV=0.)
_s5757:_ non-god mtm soaks folded: [hudbit] never fires while [objbool] does (control live) => setHudEnableBit4 is not the unpiloted end path; mtm(a0=1) is the event-table path, identical to godmode. Bit1 writer (funcs_30 0x800B1140) now logs [bit1ctx]; soak s5757_bit1ctx queued.
_s5758:_ s5757_bit1ctx folded: bit1 writer 0x800B1140 runs 6x/447 s with s1=0x80137DBC (player slot 0), terrain=y+0.125 (sane), clamp skipped, bit set unconditionally => designed spawn event, benign (refutes terrain-garbage and other-object hypotheses; single-source). New lead: 0x800EE85C (funcs_40 tickSongFadeTimer, mask bit 0x100, x4) and 0x800FB2B0 val=3 (x2) in same log; id 8 handler is a no-op when 0x8010CA20!=1.
_s5759:_ CORRECTS s5758: bit1 (writer 0x800B1140) is the death-settle completion in a per-craft timer tick (0x800B1024), not a spawn; bit1->mtm(1)=lives--; `[mtmst] 0x800FB2B0 val=3` = lives 0 game over; 3 bit1/cycle in s5757 log. See docs/M6-S5759-DEATH-CHAIN.md. Next = find the writer of slot state bits 0x8/0x10 (kill source) via lldb write-watch on the AP/god route (NEXT.md).
_s5769 (top):_ s5768 summary zeros were FALSE (BPHIT printf broke on a newline; lldb log shows setter-1 x6, mtm x6 alternating, NPC setter x0). Fixed + requeued as s5769_setterbp; read BPHIT a0 values next.
_s5770 (top):_ the fixed launcher installed LLDB breakpoints before initial continue and completed a 421 s mission hold with runtime controls live (`[mtm]` 11, `[phase]` present), but none of the three symbolic breakpoints stopped (`stop reason = breakpoint` 0; `bp_scene=0`, `bp_npc=0`, `bp_mtm=0`). The earlier s5768 “breakpoints fired” claim was only a single-source LLDB stop-log interpretation and is now void: the runtime `requestMissionTransitionMode` log does not prove the host symbol breakpoint is on the executed dispatch. Next = use generated-code/guest-PC instrumentation at the two setter PCs plus the mtm guest PC, with the same mission/lives controls; do not infer H3 from absent symbolic stops.
_s5771 (top):_ regeneration-persistent guest-PC census added at 0x800B0348 (`funcs_29.c`, `$s2`) and 0x800B08DC (`funcs_29.c`, `$s0`), then built and run on the 0x00690400 mission route for 421 s. Positive controls passed: mission onset at 60 s, `[mtm]` emitted 11 lines, and `[phase]` was live. Both `[killset]` counters were zero; no lives-decrement line was independently captured, so this is a single-source setter-null, not a complete H3 selection. Next = instrument the known 0x800B1140 bit-1 writer together with an explicit lives-byte decrement control; only a bit1 hit immediately preceding a lives decrement can close the chain.

_s5768:_ Queued soak_queue/s5768_setterbp.sh (lldb breakpoints on both kill-bit setters + requestMissionTransitionMode control; BPHIT lines in run.log). Fold bp_scene/bp_npc/bp_mtm from the summary; a0==0x80137DBC = player. Slug g1-nonhealth-fail.
_s5767 (top):_ OVERTURNS s5766 'turn float': 0x137F3C = obj0+0x180 IS the slot-state flag halfword (reader funcs_30 0x800B1E7C; writers are halfword bit-RMW, incl. 0x800AE800 `&0xFFFD`). Kill-bit setters are only 0x800B0348 (sets 0x10, spawnSceneDebrisAndEffectCluster) and 0x800B08DC (sets 0x8, spawnNpcDestructionDebris). Earlier watches ran on level-select where the region is select data; gate on mission origin. Slug g1-nonhealth-fail.
_s5766 (top):_ s5765_slotwatch_3C folded: lives control did NOT fire (no death that run => void for deaths); wp2 0x137F3C = per-frame turn float written 247/252 times by computeCraftSelectTurnFromInput (sh 0x180(s1)), NOT the slot-state flag. Slot-state address unknown again: derive it from the generated reader code (grep the lhu/andi 0x8/0x10 test), not arithmetic. Slug g1-nonhealth-fail.
_s5765 (top):_ s5763_slotwatch_kill folded: natural deaths DO occur on the level-select route (god3 dead#1-3, lives 3->0 by requestMissionTransitionMode via wp4 = control passed); forcekill gate (origin 62BD00 + valid hp) never opened - hp record valid only at 0x690400/0x620400 - hook moot. Slot-state flag halfword is **0x137F3C** (slot0; slot1 0x1381DC): a1=0x8013800C, lhu a1+slot*0x2A0-0xD0 - the s5761 'corrected' 0x137F24 was an arithmetic slip (it is craft float data written by playerXwingInit). s5760's address was right. Soak s5765_slotwatch_3C queued; fold = bt of the write that sets 0x8/0x10 before each lives-- hit. Slug g1-nonhealth-fail.
_s5764 (top):_ Added `ROGUESQ_FORCEKILL_MS=N` (main.cpp god3 thread; needs GODMODE=1+GODMODE3=2) to force a real death; queued soak s5763_slotwatch_kill (s5762 recipe + forced kill). Fold: `[forcekill]` lines + wp4 lives-- hit as control, then bt of wp2 writes. Slug g1-nonhealth-fail.
_s5763 (prev):_ s5762_slotwatch_lvsel folded: wp4 control fired (lives written by requestMissionTransitionMode/applySaveSlot/initPlayerMissionState/postLevelStatScreen) but NO death occurred; slot state 0x137F24 written only by playerXwingInit, 0x1381C4 only by initMission rs_memset. H1/H2/H3 undiscriminated. Next: force a real death (damage/crash env) with the same watches, require a lives-- hit as control. Slug g1-nonhealth-fail.
_s5762 (top):_ s5761_slotwatch_god folded: VOID. Plain 690400 route has no deaths; lives watch (0x130B10, the death positive control) never fired, run.log has 0 lives/death lines; summary `wp_hits` counts `watchpoint list` echo lines, not stops. Requeued as s5762_slotwatch_lvsel (level-select route MISSION_RE=62BD00, no god, 420 s). Fold: wp4 must fire, then bt of wp2/wp3 writes with 0x8/0x10. Slug g1-nonhealth-fail.
_s5761 (superseded by s5762 for the run itself; address stays valid):_ slot state halfword = phys 0x137F24 (+slot*0x2A0; a1=0x80137FF4, lhu a1-0xD0, funcs_30.c 0x800B1DF8-1E7C). Soak s5761_slotwatch_god (death env GODMODE3=2+HOLD_MS=1800; watches slot0/slot1/lives) queued to name the 0x10/0x8 setter. Fold: bt at first 0x8/0x10 write before each lives-- hit. Slug g1-nonhealth-fail.
_s5747:_ static fail-arm census (docs/M6-S5747-FAIL-ARM-CENSUS.md): bool-7 arm needs a dialogue flag; observed fail likely via bool 0x6D arm or another arg-2 caller. Next = entry log in requestMissionTransitionMode (NEXT.md).
_s5752:_ mtm backtrace folded: requestMissionTransitionMode is invoked ONLY via runInMissionFrame's event table (jalr 0x800FA820; table 0x8010B350 {id,fn}, pending mask word 0x8010C9E0); a0 = event bit id, not a mode. Next = dump table + log mask transitions (NEXT.md).
_s5750:_ mtm a0==2 backtrace patch built, soaks s5750_mtma/b queued. Next = fold their BACKTRACE frames (NEXT.md).
_s5746:_ s5745_crawlshot folded: real window clean, crawl band = fbd-only RDRAM artifact (G3 crawl item retired); fbd PPMs now labelled. Next = Next steps #4 (win mission 1; non-health fail condition per s5733).
_s5745:_ s5744 lvsel hp-watch: no hp->0/lives write on a 3rd route; g1-gameover-cause parked. Next = s5745_crawlshot (G3 crawl band: real window vs fbd), then MUST land a runtime change (NEXT.md).
_s5743:_ s5742 lldb hp-watch on plain route: no death, 0 hp/lives writes (wp1 control ok). Death arm is route-specific (s5738 used level-select keys, mission 62BD00); next = lldb watch on THAT route (NEXT.md).
- **s5740 (top):** s5739_hpwatch_a was a NULL, not a result: TRAPSWAP=12300 is an update_screen-scale number, but the osViSwapBuffer counter is #4864 at mission onset (update_screen #11691) and ended at #8000, so the trap never fired and no watchpoint was armed (no positive control). Requeued as s5740_hpwatch_a/b with TRAPSWAP=5200. Fold: need the 0x3470 control hit, then the top bt frame at the hp write. Slug g1-gameover-cause.
- **s5742 (top):** s5741 hp-watch folded: hp 0x137E7C has ONE writer (updatePlayerCraftPhysics swc1, 1252/1252 hits), no hp->0 and no death in 2x482 s of the plain route; deaths (every ~7.5 s) were only seen in arms with GODMODE3=2+AUTOPILOT_HOLD_MS=1800. Queued s5742_hpwatch_god (same watch under that env; script now takes XENV). Fold: top bt frame at hp->0 / lives decrement. Slug g1-gameover-cause.
- **s5741 (superseded by s5742):** s5740 hp-watch folded: control passed; hp float 0x137E7C went 150->130->130.03 written by updatePlayerCraftPhysics swc1 (0x800B29F8/0x800B1FA0); no death inside the 150 s hold so hp->0 writer still unmeasured. s5741_hpwatch_{a,b} (480 s hold) queued; fold them next (NEXT.md).
- **s5739 (superseded by s5740 above for the watch itself):** s5738 snaps folded: run a ring identical x3 deaths (constant-velocity, y -2.88->-0.32), run b turning with y plateau -5.02 at death => no y-threshold/terrain rule; kill source open (H2 flag/timer). Queued lldb write-watch hp 0x137E7C/lives 0x130B10 (s5739_hpwatch_a) to name the PC. Slug g1-gameover-cause.
- **s5738 (top):** s5737_phase{a,b} folded: lives (0x130B10 byte0) start 3, each death (phase 0->1, 6.6 s) decrements, lives 0 -> phase 6 game over -> reload; deaths recur ~7.5 s after respawn, hp goes 150->0 in one step (instant kill, 6/6), so GAME OVER on idle autopilot is the game's own rule, the open question is the instant-kill source (terrain crash vs port defect). Landed `[snap]` player-record ring in GODMODE3 thread; queued s5738_snap{a,b}. Slug g1-gameover-cause.
- **s5732 (top):** landed ROGUESQ_GODMODE3 (1=20us host-thread revive, 2=log-only trajectory); queued s5732_g3a/g3b. Fold: a cycles 0 => H-LATE; a cycles >0 => H-OTHER (find results-state writer). Slug g1-gameover-cause.
- **s5736 (top):** 0x138060 block clear = `initMission` (0x800FA250) memset 512B; callers 0x8003E2B4/0x8003E378 (game-mode state fn, gate bit 0x02000000 of r19+0x18). Clear is a consequence of mission (re)load. Next: writers of that bit (docs/M6-S5736-OBJC-CLEAR-WRITER.md). Single-source static.
- **s5737 (top):** bit 0x02000000 premise retired (static + s5515/5517/5596: arm B is the normal route). Added `[phase]` watch (0x10CA20 phase, 0x130B10 lives, 0x130B14 B14) to GODMODE3 thread; queued s5737_phase{a,b} (a=log only, b=revive). Fold: phase 1 + lives-- before phase 3 => death path (game-legit, autopilot dies); phase 3 with hp>0 => objective/timer/speech path. Slug g1-gameover-cause.
- **s5735 :** s5734_objc{a,b} folded: +0x64 never exceeds 2 and +0x60 resets from 2/3/4, both zeroed in the same tick (block clear at mission teardown) => 'loss counter==3' REFUTED (single-source, n=2). Next: name the PC/ra of the clear and its upstream condition. Slug g1-gameover-cause.
- **s5734 :** added [objc] watch of 0x138060.. to GODMODE3 thread; soaks s5734_objc{a,b} queued. Fold: loss counter reaching 3 with hp>0 => scripted loss, not health.
- **s5731 (top):** s5730_dead{a,b} folded: health reaches 0 (`[god-dead] dead=1 cur=0.00`) before every mission exit (6/6 exits in arm a; control: 12/24 god-dead lines). Selects health-death over non-health fail condition (the s5730 'mission end is GAME OVER' item below stays true; its cause is now health=0). Post-hoc revive is too late (cycles 3->1, single run each). Next: per-frame health>=1 clamp before damage resolve + log the results-state writer at the death transition; both arms one iteration. Slug g1-gameover-cause.
- **s5730 (top):** s5728_supc/supd folded: suppressing bool 0x1A / 0x5,0x3C leaves mission_cycles at 2-3 (controls OK) => those bools are not the fail driver. The cycle end is the game's own GAME OVER results screen (fbd frame 9000 of supc: time 0:00, kills 3/27). Landed `[god-dead]` probe + ROGUESQ_GODMODE2 revive; fold s5730_dead{a,b}: a = does health reach <=0 before Game Over; b = does reviving prevent Game Over/cycling (then flight outlives 226 s). Slug g1-gameover-cause.
- **s5729 (top):** s5728 a/b folded: bool 7 never fires (ids per cycle: 0x61,0x62,0x5,0x3C, then 0x1A ~31 s later), b's `[objbool-sup]` control absent => H-B7 untestable; a/b cycles=2 vs 3 earlier (noise). Queued s5728_supc (0x1A) and supd (0x5,0x3C). Fold them; if cycles unchanged, find the mission-end writer that sends the game to SELECT GAME (0x63/0x64/0x65 never pass through setObjectiveBoolean).
- **s5728 (top):** s5727_flysteer folded: steer+fire real-input flight 541 s clean, but mission fails->SELECT GAME menu 3x (single run); no win. Landed ROGUESQ_SUPPRESS_BOOL (tools/apply_s5728_boolsuppress.py); queued s5728_sup{a,b,c}: fold mission_cycles with bool 7 suppressed vs baseline. Slug g1-bool7-suppress.
- **s5727 (top):** s5726_flynopause folded: real-input route (no `start`) holds live mission-1 flight for the full 545 s, 0 stalls, 0 crashes, frames distinct (single run). Next: s5727_flysteer (steer+fire) for goal progress/win.
- **s5726 (top):** CORRECTION to s5724/s5725 below: the 'Rebel-logo cinematic that no key skips' was the PAUSE menu (start key in the recipe). s5725_introkeys reached live X-wing flight on mission 1 from real input (frame 11000 HUD, single run). Queued s5726_flynopause (no start key). Slug g1-level-select.
- **s5725 (top):** s5724_introlong folded: 545 s hold clean (0 stalls/crashes), Rebel-logo cinematic still animating (8227/10884 distinct frames), no hand-off to flight; a/start keys did not skip it (single run). Queued s5725_introkeys (z/start/b). Slug g1-level-select.
- **s5724 (top):** s5723_introa folded: real-input route reached mission-1 intro at t=19 s, 303 s hold clean (0 stalls, 0 crashes, controls OK); frames show crawl (garbage-pixel band across bottom third of the w640 frame, G3 unresolved) then Rebel-logo cinematic. No hand-off to flight inside 303 s (single run). Queued s5724_introlong (HOLD=540). Fold: reaches flight (then drive a real-input win) or loops/freezes (softlock datum). Slug g1-level-select.
- **s5723 (top):** s5722_cleanhg{a,b} 'nomission' was a GATE DEFECT (gate greps only 0x690400): the real-input route reaches the mission-1 intro (STAR WARS logo -> crawl -> planet flyover, origin 0x62BD00 then 0x644D00/0x6A2900, w640, animating, no crash). Supersedes s5722's 'hangar loop never reaches mission'. Gate now has WAITN/MISSION_RE knobs; s5723_introa queued. Open: does the cinematic hand off to gameplay; crawl/flyover frames render duplicated top+bottom in fbd (G3, unconfirmed). Slug g1-level-select.
- **s5722 (top):** s5721_clean{a,b} folded: clean save => B2F=0, unlockMask=2, cursor pinned 0 (one level unlocked; s5720's B2F=9 was forced-run save pollution). Real `a` picks level 0 at t~170 s, then hangar-class origins 0x656400/0x6AB400 loop, never 0x690400 in 150 s (gate verdict nomission, not a crash). Queued s5722_cleanhg{a,b} (adds `a,start` pairs after t=175). Fold `origin=0x690400` reached or not. Slug g1-level-select.
- **s5721 (top):** s5720_real{a,b} were INVALID for the unforced test: save polluted by forced runs (B2F=9). Added ROGUESQ_NO_SAVE_WRITE (pi.cpp, patch exported); s5721_clean{a,b} queued on a clean save. Fold `[lvsel] B2F=` (expect != 9) and cursor-vs-key ticks; ALL forced/probe recipes must now set ROGUESQ_NO_SAVE_WRITE=1. Slug g1-level-select.
- **s5720 (top):** s5716_lvl9a/b folded clean (alive 300 s, crashlines=0, vi_stalls30s=0, control a1=0x200). Forced lvl1-9 all clean. Queued s5720_real{a,b} (unforced, real keys): fold [lvsel] cursor/state; cursor is clamped to B2F so next is win-to-unlock via real input. Slug g1-level-select.
- **s5719 (top):** s5716_lvl8a/b folded: alive 300 s, crashlines=0, vi_stalls30s=0, control a1=0x100 (==1<<8) (single-run each). Forced lvl1-8 clean; only lvl9 (s5716_lvl9{a,b}) queued; then design the real-input level-select route. Slug g1-level-select.
- **s5718 (top):** s5715_lvl5a/b folded: alive 300 s, crashlines=0, vi_stalls30s=0, control a1=0x20 (==1<<5) (single-run each). Forced lvl1-7 clean; only lvl8/9 (s5716) remain queued; then design the real-input level-select route. Slug g1-level-select.
Closed next-step diary s5650-s5717 (forced levels, G2 PCM, B40, stick/altitude correlation) is in PORTING-STATE. Do not revive it from this file.

2zz. **s5694 (verdict, supersedes the 2z hypotheses):** s5693_htab soaks: controls pass; port registers only `lv2_initializeObjectTracking`'s 16 handlers (0x801026CC..0x80102A00), which arm and fire; sayWhoaHim_v0x1FC (0x80108388) belongs to level F's init and is absent because the soak mission is level 2. Bool 7 is a level-F bool, not a port defect. Next: follow a FIRED lv2 voice handler (say2PickingUpMultipleSignalsTies_v0xA4 fired) into playObjectiveVoiceLine1/audio - the real G2 dialogue path. Soak logs: data in scratch/agent/m6/<tag>/run.log.
2z. **s5693:** `sayWhoaHim_v0x1FC` has NO direct caller; it is a callback registered by `lvf_initializeObjectTracking` into the 48-entry handle table 0x8010C6E0 (addBooleanCountHandle) and fired by `checkObjectiveHandles` (0x800FA0F0 jalr) when a boolean/count condition holds (static, single-source). Instrument `[hreg]/[hchk]/[hent]/[hfire]` built (tools/apply_s5693_handletable_log.py); soaks `s5693_htab_{a,b}` queued - fold them first (NEXT.md decision table).
2. **s5692:** forwarded-a0 init sites (0x801010D4/0x801073F4/0x80103E70) refuted as bool-7 source: 0 id=7 in 56 [objbool] logs (same logs show positive-control ids; offline, capped 400 calls/run). Bool 7 has one setter, sayWhoaHim_v0x1FC, never called in port (s5637). Next: static census of its callers incl. ROM data tables, then one entry log. (s5690 context: bool writers fully enumerated; no writer sets id 7 in-run.) Older text: **Test the s5635 dialogue lead:** confirm at runtime whether
   `sayWhoaHim_v0x1FC` (or another voice-script path) sets bool 7 in failing
   runs and not in surviving ones — log entry + bool 7 transition in one build
   with a positive control. If bool 7 rides the voice path, check whether the
   missing dialogue (G2) changes the timing/outcome versus retail.
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

### s5638 update (G2 voice)
s5637 voice-line soaks a/b: playObjectiveVoiceLine1 (39 static callers) and sayWhoaHim_v0x1FC fired 0 times in 420 s missions (single-source; [objbool] control active). Mission dialogue is never requested by the port; next: instrument all callers (NEXT.md, slug g2-voice-never-requested). The 0x64-vs-0x1FC hypotheses A/B/C of s5635 are unevaluated, not refuted.

### s5639 update
[vcaller] folded (s5640): control fired, 0/35 Line1 callers fired — but lv2 uses playObjectiveVoiceLine2, so this is a wrong-function null (voice-request question still open). [speech] log on playSpeechClip + Line2 built; soaks s5640_speech_{a,b} queued. See NEXT.md.

- **s5645 (2 soaks, controls OK):** voice pool is alive downstream: all 23 speech/voice allocs land on slot 0x80153420, serviceStreamingVoice runs it, slot+0x11AC completions arrive (ok=20 empty=0), consumeVoiceSamples runs, tuple advances, stream id 7 starts. "Never requested / no completion" hypotheses refuted. Gap is sample DATA or ucode mix. NB: game logs are scratch/agent/m6/<tag>/run.log, not soak_results/*.log.
- **s5646:** consumeVoiceSamples does NOT read sample bytes (pure counter at slot+0x11D4/0x11DD) - s5645 NEXT premise was wrong. [vbuf] slot-pointer census (tools/apply_s5646_voicebuf_log.py) built; soaks s5646_vbuf_{a,b} queued; FOLDED s5647 (below).
- **s5647 (2 soaks, control `nz800=1354` OK):** voice slot 0x80153420 pointer targets (+0x198 buffer, +0x11C0 ring, +0xB84) are nonzero and CHANGE between dumps (n=1/40/200/1000; +0x198 header text -> PCM-like words). Refutes D1 (DMA yields zeros). Voice data exists in RDRAM; loss is at ucode cmd-list read (D2) or AI ring/gain (D3). Caveat: not proven to be speech vs SFX.

- **s5648:** [vcmd] (rsp.cpp, scans ucode DMA-read ring vs slot-0x80153420 pointer targets) REFUTES D2: mixer reads the +0x198 voice buffer (2561 overlapping reads / 12000 tasks; control passed). Single run; loss is after the read (decode/mix/gain/AI). A first attempt using task->data_ptr as a cmd list was invalid (data_size=1).
- s5652: vdump fold — hit-task voice-buffer reads are ~all 0x8000/0x7FF8 rail words (190/200 records): garbage source (H-G1), not speech; writer of that RDRAM range unnamed — next: log source addr + find writer.
- s5651: hit-loud replicated (s5649_vout_a); ROGUESQ_VDUMP raw dump built, soak s5651_vdump_a queued — next: offline spectrum analysis (NEXT.md).
- s5653: vsrc instrument built (source d/l + host-writer tracking); soak s5653_vsrc_a queued — fold per NEXT.md.
- s5656 (single-source): rail-range game stores are 28 total from inflate_fast/player layout/anim/particles (float bit patterns, not clamp values) — the voice-read range [1B2C60,1B3600) is shared game heap; census cannot explain the 190/200 rail records. Next: snapshot the range at boot vs at first voice read (pre-existing data vs uninstrumented stores).


### s5663 update (G2 voice)
s5662_pidma_a: speech payload IS PI-streamed in 0x400 chunks into a ring inside the voice slot (0x80153420+0x1A0); H3 (no fill) dead. Slot +0x198/+0x1210 -> 0x801B2C60 is ordinary heap (6,722/11,320 post-enqueue PI DMAs overlap the range), unfilled by the clip. Live: H5 (ring->0x801B2C60 decode never runs) vs H4 (a2 wrong upstream). Single-source. Next: trace a2 origin and writers of 0x801B2C60 after initMusyXVoiceSlot.

s5664: H4 refuted statically — slot+0x1210 = *(0x80154674) = rs_malloc(streamSampleCountToByteSize(0x10E0)) from initMusyXVoiceTable (0x8009BC4C). 0x801B2C60 is a legit malloc block, uninitialised. Live: H5 decode never runs / H6 late fill / H7 block overlapped by other allocs (PI DMAs overlap the range). Single-source (static).

### s5665 update (G2 voice)
Only decodeAndFillVoiceBlock (0x8009C904) writes slot+0x198 buffer; gates listed in PORTING-STATE s5665. [dgate]/[dec] built, soaks s5665_dgate_{a,b} queued. Static, single-source.

### s5667 update (G2 voice)
runVoiceLatticeFilter is pure integer fixed-point (no FPU); float-lowering hypothesis dead. Instrument apply_s5667_lattice_log.py built; soaks s5667_lat_{a,b} queued; fold [lat-in]/[lat-out] lines (see PORTING-STATE s5667 outcome table).

### s5666 update (G2 voice)
s5665_dgate_{a,b} (2 soaks, controls OK): decodeAndFillVoiceBlock RUNS on slot 0x80153420 from n=1, gates open, dst strides 0x140 through 0x801B2C60.. => H5 refuted; the guest itself fills the buffer, and the rail-saturated content is decoder OUTPUT. Suspect now: runVoiceLatticeFilter (0x8009D980) math - float->int conversion lowering (NaN/inf -> 0x80000000?), coefficients, or filter state. Next: log its float inputs/coeffs/outputs (NEXT.md).


s5691: static census of all 179 setObjectiveBoolean sites: only sayWhoaHim_v0x1FC sets 7; draw ids (base+1..3) never 7; three level-init sites forward caller a0 (unclassified). Next: log a0 there (NEXT.md).

- s5698 (G1): lvN init is reached via initializeObjectiveTracking (jalr table[gCurrentLevel*16]) <- initMission <- mainGameLoop. `ra=0` in recomp logs is an artifact (generated jal never sets r31) — do not infer thread dispatch from it. Next: find B40 writers (see NEXT.md).

- s5707: s5705 unlock3/5 soaks INVALID (hook ran after mask build; a1/a2 unchanged). Fixed; s5706_mask3/5 queued (G1 level-select).

- s5714: the lvl7 "w=442/443 wild SetColorImage" is a 1-row pass whose writeback width = drawColorRect.right (rt64_state.cpp:2203); colorImg.width is a clean 512. SKIP_WILD_W there skips a legit 1-row writeback. Wild-width thread CLOSED; s5712 history-desync fix confirmed n=3.

- **s5733:** tight-thread revive (g3a) did NOT stop mission cycling (origin still alternates); H-LATE refuted, H-OTHER selected (n=1/arm). Next: write-watch the exit/results-state word (NEXT.md), slug g1-gameover-cause.

- s5743 lvsel hp-watch was void (mission gate in s5739_hpwatch.sh single-quoted, never matched); fixed, requeued as s5744.

- s5748/s5749: [mtm] entry log works (control fired) but both soaks saw only a0=1 calls, and ra is always 0 (recomp doesn't maintain r31) -> use host backtrace_symbols_fd on a0==2 instead of ra; need a route that reaches a0=2.
- s5750: host backtrace on first 3 a0==2 entries landed (tools/apply_s5750_mtm_bt.py, ROGUESQ_LOG_MTM=1); soaks s5750_mtma/b queued, results pending. Fold: frames naming checkComplexObjectives/setHudEnableBit4 => bool arms; other => another writer; no a0==2 at all => a0=2 was lldb-only (recheck s5470 capture). Nothing overturned this session.

- s5751: a0==2 never fires on the keyed route (9 [mtm] entries, all a0=1 ra=0); backtrace re-aimed at any a0, soaks s5751_mtma/b queued. Game stderr is in scratch/agent/m6/<tag>/run.log.

- s5753: [mtm] table-dump + mask-change logger built (ROGUESQ_LOG_MTM); soaks s5753_mtma/b queued; verdict pending (see NEXT.md).
- s5753 folded (s5754): MASK sampler was post-dispatch => blind; per-store [mtmst] logger landed, soaks s5754_mtma/b queued. mtm table: ids 1-3 -> 0x800FB190; only a0=1 seen in godmode.


## s5787 note
Objective-count writer log built (tools/apply_s5787_objcount_log.py, in fixup); soaks s5787_cnt_fire/nofire queued; NEXT.md reads them. No result yet.

- s5790: [objwr] entry logs for the 4 candidate counter-2 writers built (tools/apply_s5790_inline_writer_log.py); s5790_wr_fire/nofire queued; fold results next (NEXT.md).
- s5790 RESULT (fire arm, single-run): counter 2 is incremented by datItemSetObjectiveBooleanCount calls with a2=2,a0=a1=0 (each rise preceded by one); updateNpcEffectIntensity/applyDatObjectiveTriggerEffect refuted. Next: caller + body of that path.
- s5791 RESULT (single run, fire arm; nofire arm of s5790 matches): counter-2 writer's caller is `updateDestructionDebrisNpc` (funcs_16.c:20649) - NPC-destruction cleanup feeding datItemSetObjectiveBooleanCount from the NPC's DAT descriptor (+0x70..+0x84). Counters are data-driven destroyed-NPC tallies; 3 events -> lv0 fail. Supersedes the s5790 'null-arg fall-through' guess. Next: identify the destroyed NPC type + destroyer.
- s5792 RESULT (single run, nofire-style autopilot): counter 2 = class-2 NPC tally (descriptor+0x70==2); victims = 3 static ground NPCs (descs 0x80319a9c/cdc/e5c), destroyed over ~110 s one at a time, not at spawn, and NOT via dealDamagetoDatItem (2 junk calls only). Writer that flags them destroyed is still unnamed; H1 retail-by-design vs H2 our-bug open. Instrument: tools/apply_s5792_npc_victim.py.
- s5793 RESULT (2 runs agree): class-2 victims die by REAL projectile hits: updateDestructionDebrisNpc is a message handler; msg 5 = hit record (shooter id +2, damage +6=12); hp 1000 at desc+0x6C+4*diff; ~84 hits/75 s per victim from per-victim shooters (ids 0x64/0xEF/0x130); sender = projectile update at MIPS 0x8005D35C (host symbol audioCueDispatcherNpcHandler, misnamed). Not timer, not collision flag. s5794: shooters identified (single run, 12 ids): 11 = npcProbeDriod (0x800CABD4) live nodes, 1 = npcWingmanUpdate; ids are per-run; H4 (stale slot) refuted. Open: H2' - do probe droids legitimately target class-2 objects in retail (read npcProbeDriod target pick / oracle). Tools: tools/apply_s5794_shooter.py, tools/apply_s5793_npc_diff.py, recipe scratch/agent/s5793_npcd.sh.
