# Rogue Squadron 64 Recomp — current truth

Compact operational handoff, maintained as of Session 5635 (2026-10-20).
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
- **M6 active thread: why the mission fails (objective booleans).** See the
  next section. Mission 2 needs a mission-1 win, which the autopilot cannot
  produce (s5596 named blocker).
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

## Next steps (single monotonic backlog)

0a. **s5657:** [vsnap] instrument built (rsp.cpp) + soak s5657_vsnap_a queued: rail-count timeline of the voice-read range at every audio task; wide hash = positive control.
0a. **s5655:** rail data (0x8000/0x7FF8) in voice-read range 1B2C60.. is REAL guest data (byte-order artifact refuted, s5655 offline un-swap) with ZERO host writers incl. RSP DMA-out (s5653). s5654 store census had val=0 always (hook pre-store); s5655 reads datum back; soak s5655_vstore_b queued — look for `[vstore-rail]` PCs. See NEXT.md.
0. **s5650 RESULT (single-source, vout_b pending): hit tasks rms ~13k clipping vs nohit ~5k => voice reaches mix loudly; H-D3a selected, H-D3b refuted; loud may be garbage, not speech. NEXT s5651: dump hit-task output PCM + input buffer, decode offline.** (older: s5650 fold of queued s5649_vout_{a,b}; [vcmd-out] instrument built s5649) (s5649 text follows) **(s5649): D3 split** - s5648 REFUTED D2 (ucode DMA-reads the +0x198 voice buffer: 2561 overlapping reads/12000 tasks, control any==reads); now compare output peak/rms on hit vs non-hit tasks and dump buffer bytes for ADPCM decode; fold queued `s5648_vcmd_{a,b}`. (old line follows) **D2 vs D3** - log whether any ucode cmd-list DRAM address falls inside the voice buffers (positive control: mark-everything); see NEXT.md. (s5644/s5646 soaks folded.) Older: fold `s5644_vdown_{a,b}` ([vdown] log; NEXT.md). Fold `s5637_voiceln_{a,b,c}` ([voiceln] log, see NEXT.md). 1. **Fold `s5633_force2_b`** (queued) for completeness of the R refutation.
2. **Test the s5635 dialogue lead:** confirm at runtime whether
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
