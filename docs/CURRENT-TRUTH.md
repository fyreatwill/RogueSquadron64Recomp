# Rogue Squadron 64 Recomp — current truth

Front matter for `PORTING-STATE.md`, which is chronological and contains superseded conclusions.
New here, or back after a break? Read **`docs/PROJECT-OVERVIEW.md`** first — what the project is, how the four layers fit together, and the hurdle classes that have cost the most time.
Session tags: `s1` = 2026-07-09/10 build + overlay work, `s2`–`s9` = the `## LLE session N` headings, `s10`–`s32` = the `## Session N` headings.

## USER DIRECTIVE (2026-08-04, human-set — overrides Next-steps ordering until satisfied)
Priority order for upcoming iterations, set after the 300-session review:
1. **Maintenance** (Step 0 of ITERATION.md triggers it at 60,000 bytes): compact per the Maintenance
   section of tools/agent/ITERATION.md; a >=200-net-line shrink counts as ADVANCED. History: s295-330
   ran 5 passes (668→459 lines by s330); s346 ran a 6th (670→~470 lines) migrating the closed s297-337
   M5 gate-reversal arc to PROJECT-OVERVIEW §9; s355 ran a 7th migrating the closed s339-353 M5
   gate-promotion/step5-rate/drainMeshReleaseQueue-tail-scan arc to PROJECT-OVERVIEW §10; s364 ran an
   8th (689→~480 lines) folding the closed s354-362 guard-hunting arc into one summary item; s371 ran a
   9th (692→~487 lines) migrating the now-fully-closed s354-370 M5 Step 5 guard-hunting arc (Thread A,
   Thread B, heapWalker GUARD5) to PROJECT-OVERVIEW §11. Full per-session detail in git log. 35 KB
   remains a stretch target, not a hard floor -- the "Current truth" env-var/timeline prose and the
   Regeneration section's Standing warnings stay intact deliberately; both are used every iteration.
2. **M5 audio de-stubbing**: design doc + steps 1-4 DONE — title-reach restored and confirmed 3/3
   (s343-344, full arc: PROJECT-OVERVIEW §10). Step 5 (both threads plus a heapWalker background-noise
   site) is **fully CLOSED** as of s370 — full detail: PROJECT-OVERVIEW §11. Step 6 (PCM sanity-check,
   `M5-AUDIO-PLAN.md` §4) is **ANSWERED s371: real PCM is 100% silent**, and s373 answered WHY:
   **structurally impossible for voices to be populated**, root-caused to the same C88 force-zero
   patch that s343 needs to keep title-reach working. Fixed a real host-bridge bug found en route
   (`queue_samples` was silently dropping half of every buffer's bytes to `SDL_QueueAudio` — see
   Overturned conclusions) and added `ROGUESQ_LOG_PCM_SANITY`; two soaks logged 13,832 total calls (7
   via the s327 direct-pump path, 13,825 via genuine RSP-dispatched `real_ucode=1`) and **every single
   sampled call was all-zero** — hypothesis 2 (silent-but-not-crashing) confirmed, not merely
   plausible. s374 reopened (Option A) WHY reversing the C88 site causes the pre-title hang: a
   bounded source-only pass found a specific, previously-undocumented single-token-mutex-deadlock
   candidate (`HYPOTHESIS-ID m5-audio-destub-c88-pretitle-hang`, iteration 1) — not yet build-soak
   confirmed. Detail: Next-steps item -228; live status/decision trees: NEXT.md.
3. **M3 crash work only as systematic idiom-class audits** (the s282–s288 `-0x25A4` model), never
   reactive single-crash chases. Breadcrumbs are passive: enqueue soaks to scratch/agent/soak_queue/
   (the loop runs them between iterations), consume scratch/agent/SOAK-RESULTS.md.
Sanctioned tooling work unit, counts as ADVANCED whenever picked up: backport function-scoped matching (the BREADCRUMB10+ slice idiom) to the ~100 file-scoped-only guard patches in fixup_game_funcs.py, per the 2026-08-04 analysis in that file's header comment.

## Current truth (established by session 295; unchanged, reviewed through s372)

    cd build && ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 \
      ROGUESQ_STUB_MISSING_FUNCS=1 ./RogueSquadron64Recomp

Metal shader rebuilds need full Xcode on PATH:
`export DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer` (bare CLT has no `metal`).

- `ROGUESQ_LLE_SOLO=1` is not optional: without it the runner runs LLE **and then falls through to
  HLE for the same task** (s9).
- Default-ON, no longer worth naming: `ROGUESQ_VI_FOLLOW_DRAW=3` (s23), `ROGUESQ_SHADE_WRAP=1`
  per-pixel (s24→s26), `ROGUESQ_FIX_ZERO_SHADE` (s20), `ROGUESQ_FIX_SAMPLE_BOUNDS` (s15),
  `ROGUESQ_VI_FULLSYNC` (s11), PresentEarly fallthrough + forceAdvance +
  `ROGUESQ_PRESENT_EARLY_FORCE` (s21), deferred-range coalescing (opt out with
  `ROGUESQ_NO_DPC_MERGE=1`, s10), **s78 wild/OOB FB refuse** in `FramebufferManager::get`
  (width>1280 or past 8MB — same family as s72 writeback; does **not** unfreeze present),
  **s182 `[fbsync-oob-skip]` guard** in `State::fullSync`'s color/depth read-into-`fbStorage`
  blocks (`rt64_state.cpp`) — s78's refuse gate returns a `refuseFb` that still carries the wild
  width/height, and this downstream RDRAM read had no bounds check of its own; same family as
  s72/s78.
- Default-OFF, keep them off: `ROGUESQ_FIX_DXT` (s22/s23), `ROGUESQ_FIX_DXT_I` (s27, null on
  hangar band), `ROGUESQ_FLATTEN_I4` / `FLATTEN_RGBA16` / `FLATTEN_CI4` (attribution probes),
  `ROGUESQ_SHADE_ONLY_MONO` (s30, pad-only), `ROGUESQ_SHADE_WRAP=3` (s31), `ROGUESQ_SHADOW2`,
  `ROGUESQ_RING_RESYNC`. Diagnostics: `ROGUESQ_DUMP_IMEM_DMA=1` (s47, lib-side) dumps every skipped
  IMEM DMA to `build/imem_dma_dump.bin` (`scratch/s47_parse_imemdump.py` decodes).
  `ROGUESQ_LOG_RUNNER=1` prints a per-task RDP-opcode histogram (1-in-32 sampled by default --
  `ROGUESQ_LOG_RUNNER_ALL=1`, s64, prints every task unsampled; the sampled mode misattributes
  31 tasks' counts onto whichever task is next sampled). `ROGUESQ_LOG_SEQ=1` dumps a task's raw
  pre-translation DL bytes -- not valid for "does this task emit SYNC_FULL" (needs the
  post-translation histogram above, s64).
- Deleted from the code (s44): `ROGUESQ_DPC_WRAP` / `ROGUESQ_WRAP_DEDUP` (s11), `ROGUESQ_FORCE_PAL15`
  (s14), `ROGUESQ_FORCE_SHADE_WHITE` (s19). `ROGUESQ_MAX_FBPAIRS` (default 8192) engages 0 times
  since s11 but is KEPT deliberately -- OOM insurance for future FULL_SYNC-less phases (M3
  missions), turns a 22 GB Metal abort into a capped workload (s44).

Unattended timeline (VI width, ±1 s over 9 runs, s18; content counts s9/s20/s22/s23):

| t | VI | scene |
|---|---|---|
| 0.0 s | 0 → 320 | boot |
| 1.7 s | 640 | attribution → N64 logo → cinematic geometry → star flare → **Factor 5 logo**, all correct (content in 24/60 frames over ~2–44 s) |
| ~46.5 s | 1024 | **title screen** — logo, pilot, X-wing, START/OPTIONS; 5/5 content frames, ~20.9k colours |
| ~72 s | 640 | transition |
| ~90 s | 512, origin 0x690400 | **outdoor scene** — sky, clouds, horizon, sand; 6/6 content frames |

**s39/`-O2` harness note:** the game now progresses further per unit time, so the old
`PROBE_KEYS="3:start 7:start 11:a 15:a 19:a"` schedule overshoots the hangar into a later exterior
scene that shares VI origin **0x6AB400** — origin alone no longer identifies the hangar. Use
`"3:start 7:start"`. The phase timeline below is unchanged (transitions are not render-rate bound).

Driven from the title with `PROBE_KEYS_FROM_PHASE=1` (s23, scene names corrected s48):

| t | VI | scene |
|---|---|---|
| 46.7 s | 1024 | clean title |
| ~50 s | 1024 | **SELECT GAME** (photographic hangar backdrop, AAA save, ERASE GAME) — waits for input indefinitely |
| +1 press | 512, origin 0x6AB400, colour 0x656000/0x6AB000 | **level-select war room → SELECT LEVEL — "AMBUSH AT MOS EISLEY"** with X-wing hologram (the scene s12–s47 called the "main-menu hangar"; see s48 below) |
| ~93 s | 640 | transition — process died here in the undriven-era observation and in every crashing run of the post-s86 family; on later crash-free runs the process instead survives past here |
| leave SELECT YOUR CRAFT (1 Start press) | 512→640, origin 0x6AB400→0x6A2900ish | **s162: a Chapter-1 mission-intro cutscene** — gold "STAR WARS" logo bumper → "Chapter 1"/"THE RED…" crawl text → black → desert-planet horizon widening into a fast dive toward a hangar structure (establishing shot, not gameplay). The s75/s76/s161 "hangar-flight" label for this window was an unverified inference from title-yellow color decay, not from the picture itself — **see the s150 overturned-conclusion entry below: it is the SAME craft-select scene under a corrupting camera move, not gameplay.** |
| ~+90-115s post-leave | varies | **graphics-task-submission stall** — `[vi-fs-decision]` reports `stalled=1 pairs=0` continuously, RDP `fs` counter frozen. Not a crash; a staggered subsystem shutdown (s178): the per-frame graphics-task producer stops being invoked at all while heap-free-walking keeps running to the end of the log. s180's source-confirmed candidate mechanism: a `[thr-resume-skip]` scheduler event (the s84 UAF guard) fires immediately before stall onset in one reproduction, but s183 reached and sustained the stall a 2nd time with **zero** `[thr-resume-skip]` fires — this weakens (does not confirm) s180's mechanism as the general cause. Open, unresolved as of s183; the last dedicated session on this thread. Full detail: `PORTING-STATE` Sessions 176-183. |

Menu state machine (s48, extended through s75; hold/crash triage s76-s114): title —start→ SELECT
GAME —start→ war room / SELECT LEVEL —start→ **AVAILABLE CRAFT** (war-room craft holograms; `a` does
**not** show a level description card, s61–s69). With process alive 65s+ post-`a` (s72/s73): black
~5s → capital-ship flash → stable **SELECT YOUR CRAFT** (hangar pad + full X-wing; `a` no-ops, s74;
camera orbits). A single Start leaves the menu — **OVERTURNED s150 (see Overturned conclusions)**:
same craft-select scene under a corrupting camera move, not a new environment; what actually leaves
SELECT YOUR CRAFT is reopened as unanswered. VI stays on the 0x6AB400/0x656400 pair throughout —
**origin cannot identify these menu scenes**, only phases (the round level-select war room and
SELECT LEVEL share 0x6AB400; a separate outdoor scene at 0x690400 does too for its phase). ~20 crash
classes closed getting through this chase (mechanisms/tags: `docs/PROJECT-OVERVIEW.md` §3/§7/§9).

Remaining visual defects, all parked as M4 except where noted: outdoor 512 zero-shade masked not
fixed (`baseFixed = −32768` root cause unknown, s19/s20); S=0 triangles in the 640 attribution phase,
uninvestigated (s18); `[dpc-behind]` ring-wrap drops with `DPC_WRAP` off (not a black-screen cause,
s11). Hangar floor multi-hue band, hangar dimness, and the post-leave black/SIGBUS chain are all
FIXED (M1 closed s48; `SHADE_WRAP` s25; ImemOverrun s69 + depth-writeback SIGBUS s72) — mechanisms in
`docs/PROJECT-OVERVIEW.md` §3.

Stability: clean through s27 driven hangar soaks and s49's post-clip-fix regression sweep. 0
`UnhandledJumpTarget`, 0 `[defer-drop]`, 0 `[dmem-race]`, 0 asserts. `[missing-func]` clean in every
soaked phase to date except s49's undriven outdoor-512 stretch (3 addresses, M4 item -6). Post-`a`
process now soaks well past 65s without death.

## Goal stack — work strictly top-down

A milestone is done only when its definition-of-done is met **and documented here**. The
autonomous loop (`tools/agent/loop.sh`, contract in `tools/agent/ITERATION.md`) always draws its
work unit from the top open milestone, so this ladder is what keeps it from idling.

**M1 — hangar band root cause and fix: DONE (s48).** Mechanism and fix recipe:
`docs/PROJECT-OVERVIEW.md` §3 ("Fixing the hangar band"). Full detail: PORTING-STATE s45–s48.

**M2 — post-clip-fix regression sweep: DONE (s49).** New stability baseline: 1138 tasks,
fanjal=9448, 0 cull-census-identity violations (scales with capture window, not a fixed constant).
Stability 0 except 3 gracefully-stubbed `[missing-func]` addresses in the undriven outdoor stretch,
never soaked before — parked as M4 (identified s53, fixed s54, runtime check outstanding — see
step 2 below). Full detail: PORTING-STATE s49.

**M3 — first gameplay: OPENED (s50), still open.** AVAILABLE CRAFT and SELECT YOUR CRAFT are both
reachable and stable; ~20 crash classes closed s50-s294 (mechanisms: `docs/PROJECT-OVERVIEW.md` §3
arc + §9 closed lineages; per-class catalog: §7). "Single Start leaves SELECT YOUR CRAFT into
hangar-flight" (s75) was **OVERTURNED s150** — same craft-select scene under a corrupting camera
move; what a leave-key actually leads to is unresolved. *Done when:* 60s of in-mission rendering,
craft visibly responds to synthetic input, stability counters 0, phase timeline covers the mission.

**M4 — parked correctness items**, one work unit each: outdoor `baseFixed = −32768` zero-shade root
cause; S=0 triangles in the 640 attribution phase; the I4 `sample=64x128` anomaly if M1 didn't
consume it; the 3 `[missing-func]` addresses in the undriven outdoor-512 stretch (root-caused and
fixed s53/54, see Next-steps item -6, **runtime confirmation still outstanding**).

**M5 — audio de-stubbing (investigation first, not code).** The MusyX audio ucode already
recompiles (`factor5_ucode_b_recompiled.c` sits in the build as a never-called artifact). First
work unit: a design doc only — how audio tasks would run LLE alongside gfx (they share the `dmem[]`
serialization built in s5), what bridges RSP audio output to SDL, and what the audio-gate byte
reversal implies. **Gate M5 behind M2**: audio re-enters exactly the shared-state territory that
cost three sessions before the recursive mutex.

## Next steps, in order of expected value (s295)

Numbering convention (fixed s295, was previously three colliding sequences): items are
numbered highest-magnitude-negative (top, newest/highest priority) counting up to -1 (bottom,
oldest). Current top is -228 (s374); the next new item takes -229 and is inserted at the top.

-228. **(s374) M5 pre-title-hang mechanism, OPTION A first pass: found a specific, previously-
    undocumented single-token-mutex-deadlock candidate — not yet build-soak confirmed.**
    `HYPOTHESIS-ID m5-audio-destub-c88-pretitle-hang`, iteration 1/3 of its budget. Source-only pass
    (per NEXT.md's own instruction not to build blind): `waitForAnyAudioSlot`
    (`N64Recomp/RecompiledFuncs/funcs_15.c:7217`) is called from `cinematicLoopBody`'s
    gate-independent, timer-triggered cutscene-teardown block (`funcs_27.c:108288`) — squarely
    inside the pre-title boot window. Under gate=1 (the C88-reversed state under test), its
    per-iteration `tickMusyXIfActive` call reaches `factor5MutexAcquire` for the first time ever,
    blocking on `osRecvMesg_recomp` against a single-token queue (`initFactor5Mutex`,
    `funcs_24.c:5703-5745`, `count=1`) that is unconditionally destroyed and recreated EVERY VIDEO
    FRAME by `reapplyAudioConfig`→`initFactor5Mutex` (`funcs_24.c:5070`), itself called every frame
    from `reapplyDisplayMode`→`runVideoFrameTick` (already established s373). Under gate=0
    (baseline) this per-frame churn is inert; under gate=1 it's live for the first time in the
    project's history — a live queue-recreation race against a blocking receive. The existing
    `waitForAnyAudioSlot` 500000-iteration safety guard (s301) is structurally unable to catch this:
    it only checks after a full loop-body iteration completes, and one blocking `osRecvMesg_recomp`
    means the loop never completes even a second iteration. Explains the s342 log signature (VI
    stuck at 640, but `[voice-active-gate-hb]`/`[voice-cursor-hb]` heartbeats kept incrementing for
    the full 600s) because those heartbeats live in `musyxMixActiveVoices`
    (`funcs_24.c:2477`), on the separate, gate-independent, VI-retrace-driven `musyxSynthFrame`
    path — not on `waitForAnyAudioSlot`'s call chain, so a deadlock there wouldn't stop them.
    **Not yet resolved from source**: whether `runVideoFrameTick` and `cinematicLoopBody` run on the
    same cooperative thread context (i.e. whether the race is even physically reachable), and how
    the OS-thread scheduler (`lib/N64ModernRuntime`) behaves when a message queue is recreated while
    a receiver may be blocked on it. Also still open: item -227's original "what specifically drives
    VI 640→1024 in the gate=0 baseline" — no such site was located in the traced call chains; may be
    moot if the deadlock is confirmed (any main-thread deadlock blocks downstream progression
    regardless of the specific trigger), stays as fallback if the deadlock trace comes back negative.
    Next step (already specified): env-gated enter/exit+timestamp logging around
    `factor5MutexAcquire`/`Release`/`initFactor5Mutex`, specifically bracketing the
    `osRecvMesg_recomp` call at `funcs_24.c:5781`; one build, one C88-reversed soak; check whether
    the log freezes mid-`osRecvMesg_recomp` at the exact moment VI sticks at 640 — the discriminating
    measurement. Full detail: `PORTING-STATE` Session 374; exact commands: NEXT.md.

-227. **(s373) M5 Step 6 "why is PCM silent" ANSWERED via source trace, no new soak needed:
    voice population is structurally blocked by the same gate the boot-hang fix requires.**
    Source-read `reapplyDisplayMode` (`N64Recomp/RecompiledFuncs/funcs_23.c:9805-10024`) end to end,
    cross-referencing the already-documented s300/s304/s342-343 facts instead of re-deriving them:
    (1) s300 established `tickMusyXIfActive` — the ONLY place `tickActiveSongs`/
    `tickAndReap3DAudioVoices` (the functions that add/tick voices) get called — fully short-circuits
    on a single `beq` when the gate byte at `0x800A0F50` reads 0. (2) This session's read of
    `reapplyDisplayMode` confirms it unconditionally zeros that exact byte at function entry
    (`0x8008EB7C: sb $zero,0xF50($at)`, line 9838) on EVERY call, and `reapplyDisplayMode` is called
    every video frame (established s304, `runVideoFrameTick`). (3) The function then conditionally
    (only when `reapplyAudioConfig` returns 0, the common case) runs a full song/voice/streaming reset
    — `resetSongSubsystemCounter`, `initSongSequencerPools`, `resetMusyXEngineState`,
    `clearStreamedVoiceFlags`, `reset3DAudioLists` (lines 9905-10009) — and would restore the gate to 1
    at its tail (`0x8008EC88`, line 10020) — except that exact address is the site
    `fixup_game_funcs.py` force-zeros (`MEM_B(0XF50,ctx->r1) = 0` instead of `= ctx->r2`), confirmed
    still the current, required baseline (s343: reversing it is why title-reach broke 0/5 times,
    s342). **Net: every single video frame this build re-disables audio, wipes any voice/song/stream
    state that might have accumulated, and never durably re-enables the gate** — so
    `tickMusyXIfActive`'s voice-population path never gets a real window to run. This is not a
    separate bug from s371's all-zero-PCM finding; it's the same mechanism, traced one level further:
    the RSP ucode was never even fed voices to mix, so producing exact zeros is the mix step behaving
    correctly on empty input (**Hypothesis 1 confirmed; Hypotheses 2/3 — mixing internally gated off,
    wrong buffer read — are now unnecessary to test**, since the ucode never receives real voice data
    to begin with). **Not chased further this session**: WHY reversing the C88 site specifically
    causes the pre-title hang was never root-caused even across the original 41-session s297-337
    gate-reversal arc (closed on empirical revert, not mechanism) — reopening that is a large,
    separate investigation, not a Step 6 follow-on; see NEXT.md for the explicit decision this opens.

-226. **(s371) M5 Step 6 ANSWERED: real PCM is 100% silent even under genuine RSP-dispatched
    real ucode; found and fixed a real, previously-undetected host-bridge bug along the way.**
    Before writing the planned sanity counter, confirmed NEXT.md's own open question (sample vs.
    byte count) by reading `queue_samples` (`src/main/main.cpp:677-681`) against
    `ultramodern::queue_audio_buffer` (`lib/N64ModernRuntime/ultramodern/src/audio.cpp:25-36`)
    together — found the callback's parameter was named/treated as a byte count but actually
    receives a SAMPLE count, and the old code passed it straight to `SDL_QueueAudio`'s byte-length
    argument with no `*sizeof(int16_t)` conversion: every call queued only HALF the correct number
    of bytes, silently dropping the back half of every PCM buffer, unconditionally, since this
    bridge was written. Fixed (multiply by `sizeof(int16_t)`); overturns M5-AUDIO-PLAN.md §4's
    claim that this bridge was "already fully implemented and functional" (see Overturned
    conclusions). Added `ROGUESQ_LOG_PCM_SANITY` (`[pcm-sanity]`) in the same edit/build. Two soaks:
    `verify1` crashed pre-title via the s327 emergency direct-pump path (7 `[pcm-sanity]` calls, all
    `all_zero=1`; its crash signature is byte-for-byte the already-cataloged s367
    `musyxSynthFrame+4652`/`0x8000834c` background noise, confirming the fix introduced no new
    crash). `verify2` reached title (45.6s) and ran ~84s into a 120s hold under GENUINE
    RSP-dispatched real ucode (`[audtask-dispatch]` confirms `real_ucode=1` actively firing) before
    an unrelated crash (`trackResourceListWithMappingTables+1228`, very likely the same "Apple
    `dladdr` fallback" background-noise family already at n=2 with a 4-byte-different offset,
    logged as a data point for the next M3 audit, not chased) — logging 13,825 `[pcm-sanity]` calls,
    **100% all-zero**, sampled every 256th per the standing convention. Net across both runs:
    13,832 total logged calls, 0 non-zero. **Hypothesis 2 (silent-but-not-crashing) CONFIRMED**, a
    positive-controlled result (thousands of instrument fires plus an independent
    `real_ucode=1`-dispatch confirmation in the same run) — not a null result. Full detail:
    `PORTING-STATE` Session 371.

-225..-210. **(s354-370) M5 Step 5 guard-hunting arc — Thread A (`coalesceFreeHeapBlocks`), Thread B
    (`drainMeshReleaseQueue` linked-list corruption), and a heapWalker background-noise site (GUARD5)
    all CLOSED.** Full blow-by-blow (every guard site, fire count, and soak-tooling lesson): `docs/
    PROJECT-OVERVIEW.md` §11; raw detail `PORTING-STATE` Sessions 354-370. One-paragraph summary:
    Thread A (`m5-audio-destub-coalesce-heap-guard-verify`) opened s354 on an independent
    `coalesceFreeHeapBlocks+3452` repeat; s358 found the guard's own bail target re-entered the loop
    instead of exiting it, fixed; closed s366 with 6/6 non-recurrence soaks post-fix. Thread B
    (`m5-audio-destub-linkedlist-corruption-source`) opened on s352's `bad_v1=0x00010001` lead
    (byte-identical across 2 sessions, ~1-in-4-billion coincidence odds) and found THREE distinct
    unguarded pointer families across `drainMeshReleaseQueue`'s five structurally identical tail-scan
    loops (tail-cursor read+write pairs s354-361; head-pointer read+clear-write pairs s363; a third
    "previous tail" family s365), plus a s366 full-function audit confirming coverage exhaustive;
    closed s368 with `s367`'s verify pair both crashing OUTSIDE the function after it completed and
    returned normally, every guard family positive-controlled (fired) in the same runs. A heapWalker
    background-noise crash surfaced by those soaks (`heapWalker+1696`, `last-guest-pc=0x8000834c` —
    coincidentally `drainMeshReleaseQueue`'s own return checkpoint, not a link between the bugs)
    reached n=4 by s368, crossing the catalog's 3rd-hit confirmation trigger; s368-369 binary-analysis
    (hand-extending `s193_disasm.py`, `otool`/`nm`/`objdump`/`dwarfdump` still sandbox-blocked) mapped
    it to guest address `0x80007A3C` + 4 unrolled siblings, the same unvalidated-pointer idiom already
    guarded 4x elsewhere in `heapWalker` — guarded as GUARD5, closed s370 with 2/2 non-recurrence (one
    full clean 302s hold recovered from raw logs after an 8.7 GB `run.log` defeated the soak wrapper's
    own timeout — new lesson: an `rc=137`/empty-wrapper-log verdict is not automatically
    uninformative, check the raw launcher/run.log before discarding). **Net as of s370: no M5 Step 5
    or escalated-background-noise threads remain open** — next M5 work is Step 6 (item -226).

-209..-195. **Sixteen sessions (s339-353) covering the M5 gate-promotion, step-5 crash-rate-comparison,
    and `drainMeshReleaseQueue` tail-scan-cluster arcs — all CLOSED/superseded, folded here.**
    (1) VI=640 `pairs=0` stall resolution (s339): source-proved
    `submitGfxFrame` cannot produce a `FramebufferPair` and `cinematicLoopBody`'s self-loop calls the
    real `SET_COLOR_IMAGE` producer exactly once — not a stall, an ordinary one-time RDP-state prologue.
    (2) Audio-gate promotion arc (s340-344): promoted both audio gates to permanent default (s340, on a
    since-overturned validation basis — see Overturned Conclusions); found `reapplyDisplayMode`'s
    reversal alone deterministically blocks title-reach, 0/5 (s342); reverted just that gate, restoring
    title-reach (confirmed 3/3 by s344) but surfacing a new `tickWrappingTimerAccumulatorList`
    div-by-zero in the post-title window, PARKED at 1/3 recurrence
    (`m5-audio-destub-tickwrap-divzero-craftselect`, reopens on `last-guest-pc=0x80054744`). Current
    gate state unchanged since s343: fixup regex matches ONLY `reapplyDisplayMode` (`0x8008EC88`,
    force-zeroed); `setDisplayMode` (`0x8008EB40`) stays reversed. (3) Step-5 crash-rate-comparison
    methodology arc (s341, s344-347): fixed 2 methodology bugs (a `[keys]`-log misattribution, an
    unbounded per-node log blowup), then a 4-run batch found the post-title crash rate high (~75%) but
    diffuse across symbols, 0/4 hits on the two named target families — closed s352, when a 16-log
    offline re-analysis found the crash TIMING (not symbols) was bimodal (two deterministic
    VI-transition windows) and a corrupted-pointer value (`bad_v1=0x00010001`) reproduced
    byte-identically across 2 independent sessions/builds (~1-in-4-billion coincidence odds) — this
    became Thread B's origin lead, see item -225..-210. (4) `drainMeshReleaseQueue` tail-scan cluster
    (s348-351, s353): found and GUARDED 3 distinct crash sites within one function's dense unguarded
    linked-list tail-scan idiom (`processSceneNode`'s content-pointer field s348; a 2nd read site via
    BREADCRUMB15 s349-350; a write-through-v1 sibling site s351); landed a ring-buffer breadcrumb
    instrument s353 (0/2 informative on its own verify pair). The `[scene-node-content-guard]` guard
    from (4) is now known steady-state-benign, not corruption evidence — see Overturned Conclusions.
    Full detail: `docs/PROJECT-OVERVIEW.md` §10; raw detail `PORTING-STATE` Sessions 339-353.

-160..-194. **(s297-337) M5 audio de-stubbing: the full gate-byte-reversal and VI=640-stall
    measurement-chasing arc, 41 sessions of instrumentation each superseded by the next, closed by
    item -209..-195's (s339) source proof.** Chased a "missing call count" through 2 diagnostic-cap bugs
    to a false 14-call gap (closed s325: the gap was the bug itself), found and fixed the `setDisplayMode`
    VI=320 hang (a spin loop starved of `musyxSynthFrame` pumps, s326/327, confirmed 3/3 s328), then
    chased `reapplyDisplayMode`'s VI=640 stall through 5 reachability probes to `cinematicLoopBody`'s
    internal self-loop, resolved s339 (see item -209..-195 and PROJECT-OVERVIEW §10). Along the way:
    `initMusyXEngine`'s gate found to be dead code, never called (s306, see Overturned Conclusions).
    Full paragraph migrated to `docs/PROJECT-OVERVIEW.md` §9 (s346 maintenance pass); full raw detail:
    `PORTING-STATE` Sessions 297-337.

-159..-14 (excluding -20, kept below). **Ten closed investigation lineages (nine from s314, plus
    the s297-337 M5 gate-reversal arc folded in s346), s99-s337 — all CLOSED, no outstanding action.**
    Whack-a-mole guard-gap chases (`composeNpcOrientationMatrix`, `renderUnlitMeshFaces`, `heapWalker`,
    `heapFreeListDequeue`, `-0x25A4` hangar-list-pointer family, breadcrumbs B2-B14), the
    audio-array-corruption race fix (s145/147/148), the `submitDmaRequestBatch` indirect-caller find
    (s101), the CALayer/campose SIGSEGV hunt, the regen-pipeline-idempotency root cause, and the M5
    audio gate/VI=640-stall chase (item -160..-194 above). One-paragraph-per-lineage summaries:
    `docs/PROJECT-OVERVIEW.md` §9; full raw detail: `PORTING-STATE` Sessions 99-337.

-20. **Regen-pipeline reliability bug (s120, confirmed intermittent not deterministic).** Root cause:
    `N64Recomp` skips rewriting any `RecompiledFuncs/funcs_*.c` file that already exists on disk, so
    any patch whose regex anchor survives its own insertion stacks a duplicate on the next
    `fixup_game_funcs.py` run unless the file is deleted first. Deleting all `funcs_*.c` before every
    regen is mandatory but **not sufficient by itself** -- residual intermittency's root cause is
    still unknown. **Standing rule**: audit the patch report for anything other than the expected `xN`
    count after every `fixup_game_funcs.py` run. Full detail: `PORTING-STATE` Sessions 120, 121, 126.

-11. **M3 — `advancePlayerAnimationPhase` SIGBUS: PARKED (s89).** 3 consecutive non-recurrences since s88's correctly-targeted instrument, against 8 prior crashing soaks. `ROGUESQ_LOG_ANIM_CB=1` still live if it recurs.

-10. **M3 — Metal-shader-compiler SIGSEGV reproducibility** (s83 spline1: SIGSEGV inside `Metal.framework`'s `MTLCompilerFSCache`, no source on our side). Still one data point.

-9. **M3 — confirm the s83 spline div0 guard actually engages.** 0/5 fires so far (still 0 after s88/s89/s90); real fix by code inspection (genuine 0/0 IEEE division) but no same-run positive control yet.

-8. **M3 — characterize `frameStartReset` SIGBUS.** 3 occurrences (s85, s108, s156 — the 3rd, `+532`, at a call chain byte-identical to `composeNpcOrientationMatrix`'s own, raising a shared-dispatcher hypothesis); no located faulting instruction in any of the 3.

-7. **M3 — HOLD_S=60 craft stick (M3 DoD body)** once earlier items clear: `PROBE_MODE=start_only HOLD_S=60` marks 10/25/40, document the phase timeline. Gate already keeps black off; residual S1 `fs` freeze (~3769-3872 plateau) may still stall animation.

-6. **M4 — confirm the s53 missing-func fix at runtime** (s54 applied + built it; only the game-run check remains). Undriven outdoor-512 stretch; `grep -c "\[missing-func\]"` should go 3→0. Not load-gated (s60/s61). Full detail: PORTING-STATE s53, s54.

-5. Past the first sustained mission hold: expect further new failure classes (mission overlay DMA → missing-func/UnhandledJumpTarget, new VI phase, overlays 12/44 splice, texture corruption). Each new failure is its own work unit.

-3. **Sibling-repo housekeeping (flagged s54, not autonomous):** `~/Documents/Tools/rogue_squadron64` carries uncommitted symbol-file edits including s54's `mission_overlay.txt` fix. Ask the user before committing there.

-2. **Band-row coverage history** (settled, s41-49): s40's `col`-write probe fails its control.

-1. **GPU->CPU present PNG** via `NativeTarget::copyToRAM` -- a convenience, not a blocker.

**Done, do not redo:** optimising the ucode vector path (s38: `-O0`→`-O2` gave 41x; SIMD/RSPRecomp vector work unnecessary at 4.5ms/task without new justification); the ucode-performance-bottleneck→DL-submission-collapse→RDP-census→draw-loss chain (s33-s37); coverage attribution/format-mismatch analysis (`LOG_BBOX`/`LOG_UPLOAD` — every band draw is I4 `tlut=0`); the s27-s31 I4-decode line (`FIX_DXT_I`, `I4_SHADE_MONO`, `SHADE_ONLY_MONO`, restricted `FLATTEN_I4`) — aimed at a texture that doesn't paint those pixels.

## Regeneration and build pipeline

Game functions (s1) — all four steps, in order:

1. `cd ~/Documents/Tools/rogue_squadron64 && python3 tools/make_elf.py`
2. `cd ~/Documents/Tools/N64Recomp && ./build/N64Recomp rogue_squadron.toml`
3. `python3 ~/Documents/Tools/N64Recomp/fixup_game_funcs.py` — **required**, and the only thing that
   re-applies the hand-edits, idempotently:
   - writes to `$zero` (`0 = expr;`) commented out (~2700 sites; the recompiler emits invalid C)
   - `fake_func_*` gap fillers with gotos to nonexistent labels → `__builtin_trap()`
   - real functions with cross-function branches (shared asm tails: `lvj_checkComplexObjectives`,
     `audioCompandS16`, `applyVoiceDelayFilter`, `__OSGlobalIntMask`) → each bad goto becomes
     `__builtin_trap()`; a runtime SIGTRAP means one of those was taken
   - audio-engine gate stores → 0 in `funcs_23.c` for `setDisplayMode`/`reapplyDisplayMode` only (gate
     byte 0x800A0F50) — without this the scheduler wedges in `waitForMusyXAudioTaskDone`.
     `initMusyXEngine`'s own site was reversed s302 (M5 step 4); the guest's real write takes effect
     there now, validated 0/2 family #1 recurrence over 2 soaks
   - the `jr $t9` return idiom in `funcs_4.c` (`convertMat3x4ToN64Mtx`, 0x80018D80) → plain `return`
     instead of `LOOKUP_FUNC(ctx->r25)`
   - `musyxKeyOnVoice` `break 6/7` div-by-zero guards → early `return`, keyed on the exact `do_break`
     constants 2148076780..2148077008
   - `evalCubicSplineAtTime` (s83) zero-width-interval div0 guard at `0x8001906C` (`funcs_4.c`) —
     `f1.fl==0` → log first 20 as `[spline-div0]` + `f4.fl=0` instead of `DIV_S` producing NaN
4. `cd build && cmake --build . -j8`

RSP ucode (only when a ucode toml changes): `~/Documents/Tools/N64Recomp/build/RSPRecomp` on
`factor5_rsp.toml` / `factor5_boot_rsp.toml` → `build/factor5_ucode/*.c`, then
`tools/fixup_factor5_ucode.py`. **s47: before the fixup, also run
`python3 tools/make_clip_composite.py` + RSPRecomp on `factor5_rsp_ovl4.toml`** — fixup 6 splices
the clip-overlay translation from `factor5_ucode_ovl4_recompiled.c` and hard-fails without it
(build/ is gitignored, so a fresh checkout must regenerate it). `factor5b_rsp.toml` (ROM 0x9ABE0)
is the **MusyX audio** ucode; `factor5_ucode_b_recompiled.c` stays in the build as a never-called
artifact (s5).

Standing warnings:
- `lib/N64ModernRuntime` and `lib/rt64` carry **uncommitted working-tree patches**:
  `librecomp/src/pi.cpp` `do_dma` → `load_overlays_by_start`, `overlays.cpp` `it < upper`,
  `librecomp/src/rsp.cpp` `rs64_dmem_lock/unlock` hooks (the shared-DMEM serialization, s5), and the
  whole RT64 assert-guard chain (s2b/s3/s7/s9/s12). **Never `git submodule update --force`.**
- The ROM must sit next to the executable in `build/`; run from anywhere else and the binary silently
  takes the "place your ROM" path and gives a dead VI (s8).
- Hand-edited diagnostics in `build/factor5_ucode/*.c` survive a cmake build but **not** an RSPRecomp
  regen — add them to `tools/fixup_factor5_ucode.py` to keep them. Diagnostics in `RecompiledFuncs`
  are wiped by regen entirely.
- The settings.json Bash allowlist matches the FIRST WORD of the command: `VAR=1 tools/probe.sh …`
  is denied despite `Bash(tools/:*)` — prefix such commands with `env` (allowlisted) instead (s44).
- Harness: `clang -O1 -fobjc-arc -framework Cocoa -framework CoreGraphics -o build/winctl tools/winctl.m`;
  capture with `tools/probe.sh` / `tools/regress.sh`. Kill runs with SIGKILL, not SIGTERM — the TERM
  path aborts in SDL_QUIT cleanup and leaves a crash dialog over the next run's capture (s9).
  Python decoders need `scratch/venv/bin/python` (PIL is gone from system python, s18).
- `regress.sh` preflight must not write probe images as `.*` hidden names: `screencapture` refuses
  final path components starting with `.` (exit 0, no file) and falsely reports visual=denied (s26).
- ~~Screen Recording permission is intermittent~~ — **overturned s32**: capture and synthetic input
  both work (74/74 `screencapture -l` succeeded, stable CGWindow id). `could not create image from
  window` means the **window id is wrong**, not missing permission — check via `winctl find <pid>`
  (`winctl trusted` reports Accessibility state; `winctl list` is not a subcommand).
- `winctl activate` is a cooperative request modern macOS **ignores while another app holds focus** —
  keys then drop silently with `trusted`=yes (s45; the real cause of the old "no GUI session"
  failures). `probe.sh`/`regress.sh` raise via System Events `set frontmost` (`raise_game()`) instead
  — use them rather than `winctl` directly for driven runs.

## Overturned conclusions — do not act on these

`## LLE stabilization session 2 (2026-07-12)` sits out of order in the log, between s7 and s8: its conclusions are among the oldest in the file, not the newest.

- **(s348/350→s352)** "`[scene-node-content-guard]` firing is evidence of the same corruption class as
  the other step-5 guards" — s352's raw-log re-read found this guard fires at the SAME node address
  (`0x80183ECC`) with the SAME zeroed content, thousands of times per run, harmlessly, across 3
  independent sessions — a steady-state signature (legitimately-empty/placeholder node revisited every
  frame), not a corruption signature. Believable: it's a real guard catching a real out-of-range read,
  and 0/4 crash-repeat since it landed (item -209..-195 range, s348) looked like validated-by-non-recurrence; the n=0-vs-
  n=1957+ distinction (one-shot-before-crash vs. steady-state-thousands-of-hits) just hadn't been
  checked against the OTHER guards' firing shape until s352 compared them side by side. Does not
  overturn the guard's correctness (it still needs to stay in place), only its evidentiary weight for
  the step-5 corruption-source hunt. PORTING-STATE 348, 350, 352; CURRENT-TRUTH item -209..-195.
- **(s339→s340→s342)** "The VI=640 `pairs=0` plateau is a benign, locked-camera mission cutscene" (s339)
  and "s340's 2/2 clean soaks validate promoting both audio gate reversals together" (s340) — s342
  found both soaks (and s341's 2 follow-ups) never left the pre-title attribution/logo screen: 0
  `[keys]` lines in all 4 raw logs, and `run_mission_keys.sh`'s wait-for-VI=1024 gate mechanically
  cannot reach its `SCHEDULE`/`HOLD_S` logic without first seeing VI=1024, which never happened.
  Believable: the soaks genuinely were crash-free for the full 600s with audio/DMA/voice counters
  visibly live throughout (a real same-run positive control) — it just never occurred to check whether
  the `[keys]` schedule had actually fired. The underlying `pairs=0` mechanism (item -209..-195 range,
  s339's source trace, PROJECT-OVERVIEW §10) is not overturned, only its context: it onsets pre-title,
  not mid-mission-cutscene, and is
  specific to `reapplyDisplayMode`'s gate site, not `setDisplayMode`'s. PORTING-STATE 339, 340, 342.
- **(s107/108→s316→s318)** Two linked overturns in the gate1/2/3 tick-producer mechanism chase: (1)
  "the 3 near-identical countdown/period gates fire `tickAllActiveSongs`/`tickAudioSequencerFrame`" was
  never validated with a positive control across 4 sessions (s108/s311/s312 measured only gate1's raw
  inputs, never its branch outcome) — s316 instrumented all 3 and found NONE ever takes "call,"
  contradicting the functions' own 37-call count. (2) That "never calls" reading was itself overturned
  by s318: the diagnostic re-read the shared countdown fresh (`MEM_W`) instead of the register
  (`ctx->r2`) the real branch decision uses, racing against the true value. Direct measurement of
  `ctx->r2` showed gate1 takes "call" on 19/40 and gate2 on 4/4. Believable both times: the disassembly
  pattern matched exactly, and the read-once-for-branch/re-read-once-for-print pattern is easy to write
  without noticing it reintroduces a race. PORTING-STATE 316, 318.
- **(s222→s223)** "no soak reaches mesh-heavy content" — a 4-soak sample-size artifact; a re-run
  reached space-combat content before freezing. The freeze itself is real, still reproduces (now a
  flat fill, not a torn polygon). PORTING-STATE 223.
- **(s216-218→s219)** "shared corrupt literal `0x0000000300000000` at x0/x8, WRITTEN somewhere" — that
  register is the process's constant RDRAM host base pointer, present by construction in every
  `MEM_W` fault, not written corruption; the wild operand is the *other* register (byte-identical at 3
  sightings, all the same `renderUnlitMeshFaces` bug, vs. an unrelated 4th `heapWalker` bug).
  PORTING-STATE 219.
- **(s75/76→s150)** "single Start from SELECT YOUR CRAFT leaves into a distinct hangar-flight scene" —
  dense capture + an independent prior run + a code-level check (crash backtraces stay entirely in
  hangar-menu code) show it's the same craft-select scene under a corrupting camera move. Reopens
  "what leaves SELECT YOUR CRAFT" as unanswered. PORTING-STATE 150.
- **(s2-31→various, ~15 claims, grouped)** Build/pixel-getting era, each overturned within 1-2
  sessions: Z-buffers misread as colour buffers; texrect output called invisible; RDP "emitting
  nothing" (real bug: a function-local ring high-water mark); `DPC_WRAP`/fbpair-cap misdiagnosed for
  missing FULL_SYNC (PROJECT-OVERVIEW §4.6); `PRIM_ALPHA_FF` called necessary for text; a
  sampling-artifact black-screen; misattributed texture dumps, floor-band line-mask/palette/dxt
  theories (M1's real cause: s44-49), fog-color attribution, S=0-triangle phase, stale-TMEM-at-draw
  (§4.1), and 1024-phase black screen (present-starvation, not zero-shade). PORTING-STATE 2-31.
- **(s62-69, grouped)** "RSP task submission stays healthy through the freeze" — a 1-in-32 throttled
  sample missed the crashing tail; an unsampled histogram showed 100% `ImemOverrun` exits.
  "Self-restarting the end-of-IMEM perspective-divide branch un-freezes tasks" — instrument fired 0
  times; the real site was `CLIP_1FBC`→`L_1650`. PORTING-STATE 62-69.
- **(s12-48, grouped — real causes already stated in "Current truth" above)** "0x6AB400 is the
  main-menu hangar" (believable: the partial render looked coherent for 36 sessions); stray
  briefing-room/SELECT-LEVEL origin+timing claims; hangar dimness/floor-band misattributed to a
  magnitude-erasing shade census (real cause: M1 s44-49); "no complete clip overlay in ROM" (a stray
  census conflated fall-through hits with real dispatch). All overturned s47/s48. PORTING-STATE 12-48.
- **(s70-82, ~9 claims, grouped)** The post-`a` SIGBUS/black-screen self-correction chain — UAF
  theories, what survives past it, Start-press counting, `fs`/present-stall theories — all resolved by
  the s84 UAF fix and s82 sane-width gate. PORTING-STATE 70-82.
- **(s87→s88)** "8th crash class is self-recursion in `advancePlayerAnimationPhase`" — that call site
  belongs to a different, unreached function; constant stack depth across 3296 calls, no recursion.
  PORTING-STATE 88.
- **(s302→s306)** "reversing `initMusyXEngine`'s gate-byte site validated safely (0/2 family #1
  recurrence)" — a positive-controlled entry counter found `initMusyXEngine` is never called at all;
  the clean result reflects dead code, not a validated gate=1 state. Gate=1 still never exercised by
  any soak. PORTING-STATE 306.
- **(s307→s309→s313→s315)** A chain of "stop points converge" claims in the audio-tick investigation,
  each overturned by a closer same-run measurement: "the RSP-task freeze and audio-tick freeze land at
  the same point (task #39/tick #19), one shared upstream resource" (s307) — `main.cpp` source-read
  found separate code paths, audio ticks stopping 18 tasks/1930 log lines earlier (s309). "The 3
  tick-producers and RSP `M_AUDTASK` all stop together at call #19/20 (a SOFT stop)" (s307/310/311) —
  a widened print-cap soak found `update3DAudioFrame` fires 40/40 (the real hard-stop boundary), the
  tick-producers stop 3 calls earlier at 37/37, and only `M_AUDTASK` genuinely stopped at 20/20 (s313).
  Then "`M_AUDTASK` genuinely stops at 20/20" itself — its diagnostic lived outside the game-code patch
  file and had the identical unwidened flat-cap bug s313 had just fixed elsewhere; widening found it
  also fires 40/40 (s315). Net: 2 real stop points (37/37 and 40/40), not 1 or 3. Believable each time:
  similar small round numbers read as simultaneous unless line numbers are diffed. PORTING-STATE 309,
  313, 315.
- **(M5-AUDIO-PLAN.md §4→s371)** "The host bridge (`queue_samples`/`SDL_QueueAudio` wiring) is
  already fully implemented and functional... nothing needs to be built here" — a source read found
  a real bug: `queue_samples`'s parameter was named/treated as a byte count but
  `ultramodern::queue_audio_buffer` actually passes a sample count, and the old code passed it
  straight through as `SDL_QueueAudio`'s byte length with no `*sizeof(int16_t)` conversion — every
  call queued only half the correct number of bytes, silently dropping the back half of every PCM
  buffer, since this bridge was written. Believable: the wiring genuinely compiles, links, and calls
  through cleanly end-to-end, so eyeballing the call graph reads as "functional" — the defect is a
  unit-mismatch one level down, only visible by checking the actual value each side produces/expects,
  not by tracing that a call happens. Fixed s371 (`src/main/main.cpp`'s `queue_samples`). PORTING-STATE
  371.

### Dead ends — labelled as such in the log, do not retry

- **(s2b-s4, grouped)** `RDP_ADDRESS_MASK`→0x7FFFFF (aliased legitimate extended-RDRAM handles onto
  low memory); a chunk-replay hack in `dma_rdram_to_dmem` (legit trig reads right after a swap);
  widening the DMA shadow to 0x37658 (legit dynamic data); blanket ucode-image shadow `shadow2` (2
  addresses are legitimately rewritten); `ROGUESQ_RING_RESYNC=1` (no measurable change);
  `dmem[0x153]=0xFF` forced segment reload (made failures worse).
- Bulk moves of unmapped symbols out of `main_overlay.txt` (s9): splits the enclosing function
  (PROJECT-OVERVIEW §4.5), producing a SIGBUS. Use `tools/overlay_symbol_probe.py <0xADDR>` first, one
  validated batch at a time.
- Present-side snap-down/`findMostRecentContaining` fallbacks (s9, neither ever fired); `ROGUESQ_VIEW_RDRAM=1` (s9, window never appears, broken in this fork); `ROGUESQ_WRAP_DEDUP=1` (s10, removes ~33000 redundant submissions, same Metal assert still hits); `ROGUESQ_FORCE_PAL15=1` (s14, clears floor band but corrupts ceiling banners sharing pal=15).
- **(s85→s91)** "`do_rom_read` corrupted `physical_addr` is nondeterministic garbage" — the exact same
  DMA call recurred byte-for-byte 3 times across 3 sessions; reclassified deterministic, reproducible.

## Method traps

Mechanism already generalized in PROJECT-OVERVIEW.md §4 → pointer only here, session tag is the
specific instance in PORTING-STATE:
- §4.1 instruments-that-lie: `fbPair.projections` over-count (s32), `[loadblock]` sampled-log miscount (s18/s19), stale TMEM at draw-record time (s19), capture harness outliving the process, `window_burst.sh` 60/60 false-positive (s9).
- §4.2 attribution errors: colour match ≠ attribution, fog #C8C0A0 (s18); plausible decoded image ≠ phase ID (s17).
- §4.3 cross-run comparison: knob effects/nulls manufactured by camera drift, "7.30%" constant misread as an effect (s18); phase timing varies tens of seconds run-to-run, gate on `PROBE_PHASE_WIDTH`/`PROBE_KEYS_FROM_PHASE=1` not a stopwatch (s17 → s18/s23).
- §4.6 missing protocol events: pair/buffer/wrap counters measured instead of FULL_SYNC arrivals (s11).

Not yet generalized in PROJECT-OVERVIEW: instrument-specific traps (crash-free-soak-isn't-evidence,
orphaned background soaks, sparse-screenshot false regressions, unvalidated suppression instruments,
`dpc_bridge` walker desync, histogram-drain timing, camera motion confounding aggregates) migrated to
`docs/PROJECT-OVERVIEW.md` §8 (s314 maintenance pass).
- **crash-signature blindness (s344)**: a soak-recipe verdict of "did any `[CRASH]` marker fire" is not
  evidence for a SPECIFIC target crash unless `last-guest-pc`/`pc-symbol` is checked against it — RS64
  has ~20+ independent, already-catalogued, nondeterministically-firing crash families, so a bare
  presence check will false-positive-confirm the wrong bug. Same session also found a `[keys]`-log-file
  bug (grepping the game's `run.log` for driver-emitted `[keys]` lines, which only ever land in the
  launcher's own log) that made 2 real, fully key/stick-driven soaks misreport as having driven no
  input at all. Item -200.
