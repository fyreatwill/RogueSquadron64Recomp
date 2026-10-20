# Rogue Squadron 64 Recomp — current truth

Compact operational handoff, maintained as of Session 5668 (2026-10-20).
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

1a000. **s5687:** G2 evidence consolidated in docs/G2-AUDIO-FIDELITY-CLOSURE.md (noise causes s5668+s5672 fixed; rate/format/spectrum/dialogue refuted). G2 closed pending owner listen. Next: Next steps #2 (bool 7 voice path), slug g1-bool7-voice-path.
0d. **s5669 (PCM-level confirmation):** s5669_pcm_a: 0/330 AI-callback rows have rail samples, hf_ratio ~0.23 in mission; speech clips now enqueue (loadSpeechFile/enqueueSpeechClip x6, voices allocated x6). The noise layer's rail component is gone at the output. NEXT: owner listen / retail-oracle AI PCM hf_ratio compare for residual noise, and confirm speech clip PCM non-rail in voice buffer (slug g2-voice-never-requested -> g2-speech-audible).
0e. **s5670:** ROGUESQ_LOG_PCM_DENSE run: 6/6 speech-enqueue windows have mean|PCM| 1.8-15x the preceding level (control windows: median 1.0, p90 1.38, 2% >=1.8) -> speech reaches AI output (single-run, correlational). Open: owner listen; hf_ratio vs retail oracle (H-c).
0i. **s5674:** ROGUESQ_PCM_RAW dump + tools/speech_window_spectrum.py: 6/6 speech-enqueue windows are rail-free, >98% energy <3 kHz (>8 kHz <=0.001), rms ~11x control (3.5-5.6k vs 328) -> band-limited voice-like, not noise (H-e2 refuted; single-run). Intelligibility vs masking (H-e1/H-e3) needs a listen: scratch/agent/m6/s5674_raw/wav/enq*.wav. NEXT: owner listen; if OK close G2 -> G1.
0h. **s5673:** s5673_dense_new on DRAIN=2048 default: 6/6 speech-enqueue windows 1.9-4.6x (control p90 1.33) -> speech still reaches AI output with correct cadence; H-d2/H-d3 refuted (single run, correlational). tools/speech_window_ratio.py. NEXT: owner listen; else voice-solo PCM dump decoded offline.
0g. **s5672 (G2 fuzz ROOT CAUSE, two arms + default verify):** per-VI OS_EVENT_AI gave guest 11.4k audio frames/s vs 22047 needed; SDL queue empty at 72% of buffers (underrun crackle). ROGUESQ_AI_EVENT_DRAIN now defaults to 2048 (0=legacy): zero-queue 3/24064, 21.87k fps, 16 ms latency. NEXT: owner listen; then dialogue path (g2-voice-never-requested) re-measure with correct cadence.
0f. **s5671:** oracle `[ai-hf]` (same hf_ratio metric as port `[pcm-noise]`): retail title median 0.200 (p90 0.477), hangar 0.156 (p90 0.292); port title phases 0.20-0.24 (p90 0.43-0.54), mission 0.185 -> port AI PCM spectrum matches retail (H-c1 refuted; single-metric, two-run). NEXT: host sink (dacrate retail vs port, SDL device spec/resample) + owner listen.
0c. **s5668 (G2 noise ROOT CAUSE, lattice-level confirmed):** N64Recomp src/recompilation.cpp:874 emits at most one label per instruction, so junk out-of-function branch targets make real labels lag; audioCompandS16 (0x8009DD7C) mis-jumped and returned +-0x7FFF for every input -> saturated voice lattice coefficients -> ~85% rail output. Fixed by tools/fixup_label_realign.py (hooked at end of fixup_game_funcs_vendored.py). s5668_fix_a: rails 0 in 44/46 lattice calls, smooth output. NEXT: PCM-level confirmation (ROGUESQ_LOG_PCM_SANITY / AI ring noise floor, fixed vs s5667 build) and then the dialogue path (g2-voice-never-requested) - voice decode no longer saturates, so re-measure whether speech now plays. Only-lattice-level evidence so far (single-source).
0b. **s5660:** only unhooked game store forms are swl/swr/sdl/sdr (421 sites; many are data-as-code). Hooked via tools/apply_s5660_unaligned_store_census.py -> rs64_s5660_ustore; soak `s5660_vwriter_a` queued (look for `[ustore-all]` control and `[vstore] w=L/R/l/r`). See NEXT.md.
0a. **s5659 (single-source):** vsnap_b: rails in voice-read range go 2 -> ~1081 (of ~1232 halfwords) in a ~18-task burst (tasks 1789-1806) right after the FIRST enqueueSpeechClip/allocAndConfigureNewVoice (phase 5); clean through task 1528. Fill is at voice start, writer unnamed (not the 28 instrumented stores, not RSP DMA-out). Next: log every write form (swl/swr/sdc1/host memcpy/PI DMA) overlapping the range between task 1528 and 1806, with PC.
0. **s5662:** H3 needs NO new build: `ROGUESQ_LOG_DMA` already logs every PI DMA (s5658 run never armed it). Soak `s5662_pidma_a` queued; fold = PI dests after first `enqueueSpeechClip` vs [1B2C60,29DFB8): overlap => filled-then-clobbered, elsewhere => H4 (bad descriptor address), none => H3 (speech load skipped). Prior datum (single-source, s5653): the 30 logged host writers in that range were `zmemcpy`, not PI.
0a. **s5661:** s5660_vwriter_a folded: unaligned stores (swl/swr/sdl/sdr) are NOT the rail writer (narrow=6 of 17.8M stores, control all>0; the 9 rail-word PCs are aligned float stores, 2nd source after s5656). Range [1B2C60,1B3600) is shared heap floats read by audio as samples. NEXT: H3 - does the speech clip's destination buffer ever get a PI/inflate fill? (NEXT.md, slug g2-voice-never-requested).
0a. **s5658:** s5657 vsnap starved (80-line budget eaten by wide-hash control by task 1007; rails 0/swz<=2 early). Rebuilt rail-count-keyed; s5658_vsnap_b queued.
0a. **s5657:** [vsnap] instrument built (rsp.cpp) + soak s5657_vsnap_a queued: rail-count timeline of the voice-read range at every audio task; wide hash = positive control.
0ab. **s5696 (G1, offline, 3 logs):** every mission phase has gCurrentLevel=1 (B40=1) after the cine-arg 0x13 write; the win-poke cycle replays it (phase 9 = 1 again). 'lv2_*' = gCurrentLevel 1 (naming inference, single-source). Next: static trace of the init-table indexer (ROM 0x10B050) to name the index source.
0aa. **s5695 (G2 dialogue request path, two runs):** lv2 voice handler (0xA4) -> playObjectiveVoiceLine2 -> playSpeechClip (all gates pass) -> enqueueSpeechClip -> loadSpeechFile -> allocAndConfigureNewVoice, 14-18 clips/run in s5693_htab logs. The s5637 'dialogue never requested' claim is superseded (it counted Line1 callers only). Next: G1, reach a non-level-2 mission.
0a. **s5655:** rail data (0x8000/0x7FF8) in voice-read range 1B2C60.. is REAL guest data (byte-order artifact refuted, s5655 offline un-swap) with ZERO host writers incl. RSP DMA-out (s5653). s5654 store census had val=0 always (hook pre-store); s5655 reads datum back; soak s5655_vstore_b queued — look for `[vstore-rail]` PCs. See NEXT.md.
0. **s5650 RESULT (single-source, vout_b pending): hit tasks rms ~13k clipping vs nohit ~5k => voice reaches mix loudly; H-D3a selected, H-D3b refuted; loud may be garbage, not speech. NEXT s5651: dump hit-task output PCM + input buffer, decode offline.** (older: s5650 fold of queued s5649_vout_{a,b}; [vcmd-out] instrument built s5649) (s5649 text follows) **(s5649): D3 split** - s5648 REFUTED D2 (ucode DMA-reads the +0x198 voice buffer: 2561 overlapping reads/12000 tasks, control any==reads); now compare output peak/rms on hit vs non-hit tasks and dump buffer bytes for ADPCM decode; fold queued `s5648_vcmd_{a,b}`. (old line follows) **D2 vs D3** - log whether any ucode cmd-list DRAM address falls inside the voice buffers (positive control: mark-everything); see NEXT.md. (s5644/s5646 soaks folded.) Older: fold `s5644_vdown_{a,b}` ([vdown] log; NEXT.md). Fold `s5637_voiceln_{a,b,c}` ([voiceln] log, see NEXT.md). 1. **Fold `s5633_force2_b`** (queued) for completeness of the R refutation.
1a00. **s5685/s5686 (DONE):** ROGUESQ_ALT_HOLD closed-loop y hold works (acted>0) but mission_cycles ctrl=0, hold_a=2, hold_b=0, godrefills=20 all -> damage/re-entries NOT altitude-driven (H2, single-source). G1 autopilot thread parked; next rung G2 audio fidelity (title-music PCM port vs retail oracle).
1a0. **s5684 (RAN, single-source):** stick_y reaches the ship: mean dpos.y -0.19/-0.006/+0.12 for sy=-1/0/+1 (n=54/490/55); dpos.x weakly tracks sx; record vel still uncorrelated. Next: closed-loop altitude autopilot using sy. **s5683 (BUILT, soak s5683_pd2 queued; fold with tools/pd2_corr.py):** pd2 per-poll ship pos/vel dump now arms only on nonzero stick (600 polls). **s5682 (RAN):** record +0xD0 is constant, NOT velocity (H-p4b refuted); ship pos x/z move, y static in an input-free window (single-source). Next: correlate dpos with stick and +0xDC/E0. **s5681:** target 8034f680 (record +0x04) has position-shaped vec3 +0x4C/50/54; integration unconfirmed. Superseded: the s5681 guess that +0xD0 is velocity - believable because it is a float vec3 beside the position, but it never changed.
1a. **s5680:** `ROGUESQ_PLAYER_DUMP=1` + `tools/pdump_fields.py`: player record 0x137DB8 holds stick echoes (+0xDC/+0xE0, control OK) and a vec3 (+0xD0..D8) tracking steering, but NO integrated position/altitude (single run) -> position is in the ship object the record points to; next: dump pointed-to objects (NEXT.md).
1b. **s5679 result (first valid G1 arms):** controls OK (`[autopilot] armed: 236 events`, `[pad-host]` lines, fbrun/mcycles controls). a (fire+steer) vs b (steer-only), 300 s mission hold each: a had 18 pad-host edges incl. a=1 (btn 0x8000) at mission origin 0x690400, godrefills=20, mission_cycles=2; b had 9 edges, 0 a=1, godrefills=5, cycles=0; neither crashed or stalled (vi_stalls=0). Last a frame (fbd/fb_0011000) shows the ship pitched into terrain = blind steering flies into the ground, so a's extra damage/re-entries are plausibly crashes, not progress (single-source: frames + counters, no RDRAM state). Next: state-aware autopilot (read ship pos/pitch from RDRAM) or G2/G3. Prior arms s5675-s5677 void (AP_OVERRIDE ordering).
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
