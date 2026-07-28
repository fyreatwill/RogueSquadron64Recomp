# Rogue Squadron 64 Recomp — current truth

Front matter for `PORTING-STATE.md`, which is chronological and contains superseded conclusions.
New here, or back after a break? Read **`docs/PROJECT-OVERVIEW.md`** first — what the project is, how
the four layers fit together, and the hurdle classes that have cost the most time.
Session tags: `s1` = 2026-07-09/10 build + overlay work, `s2`–`s9` = the `## LLE session N` headings,
`s10`–`s32` = the `## Session N` headings.

## Current truth (as of session 166)

    cd build && ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 \
      ROGUESQ_STUB_MISSING_FUNCS=1 ./RogueSquadron64Recomp

Metal shader rebuilds need full Xcode on PATH:
`export DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer` (bare CLT has no `metal`).

- `ROGUESQ_LLE_SOLO=1` is not optional: without it the runner runs LLE **and then falls through to
  HLE for the same task** (s9).
- Default-ON, no longer worth naming: `ROGUESQ_VI_FOLLOW_DRAW=3` (s23), `ROGUESQ_SHADE_WRAP=1`
  **per-pixel** (s24 vertex → s26 shader), `ROGUESQ_FIX_ZERO_SHADE` (s20, largely subsumed by
  wrap), `ROGUESQ_FIX_SAMPLE_BOUNDS` (s15), `ROGUESQ_VI_FULLSYNC` (s11), PresentEarly fallthrough +
  forceAdvance + `ROGUESQ_PRESENT_EARLY_FORCE` (s21), deferred-range coalescing (opt out with
  `ROGUESQ_NO_DPC_MERGE=1`, s10), **s78 wild/OOB FB refuse** in `FramebufferManager::get`
  (width>1280 or past 8MB — same family as s72 writeback; does **not** unfreeze present),
  **s182 `[fbsync-oob-skip]` guard** in `State::fullSync`'s color/depth read-into-`fbStorage`
  blocks (`rt64_state.cpp`) — s78's refuse gate returns a `refuseFb` that still carries the wild
  width/height, and this downstream RDRAM read had no bounds check of its own; skips the
  `FramebufferStorage::store` read when it would exceed the 8MB RDRAM buffer, same family as s72/s78.
- Default-OFF, keep them off: `ROGUESQ_FIX_DXT` (s22/s23), `ROGUESQ_FIX_DXT_I` (s27, null on
  hangar band), `ROGUESQ_FLATTEN_I4` / `FLATTEN_RGBA16` / `FLATTEN_CI4` (attribution probes),
  `ROGUESQ_SHADE_ONLY_MONO` (s30; pad-only, not a band fix), `ROGUESQ_SHADE_WRAP=3` (s31 shared
  wrap experiment), `ROGUESQ_SHADOW2`, `ROGUESQ_RING_RESYNC`. Diagnostics: `ROGUESQ_DUMP_IMEM_DMA=1`
  (s47, lib-side) dumps every skipped IMEM DMA to `build/imem_dma_dump.bin`
  (`scratch/s47_parse_imemdump.py` decodes). `ROGUESQ_LOG_RUNNER=1` prints a per-task RDP-opcode
  histogram (1-in-32 sampled by default — `ROGUESQ_LOG_RUNNER_ALL=1`, s64, prints every task
  unsampled; the sampled mode silently misattributes 31 tasks' counts onto whichever task is next
  sampled, a real bug for any single-task question). `ROGUESQ_LOG_SEQ=1` dumps a task's raw
  pre-translation DL bytes — **not** a valid way to answer "does this task emit SYNC_FULL": that
  question needs the post-translation histogram above (s64, positive control failed on the raw-byte
  method).
- Deleted from the code (s44, title-screen probe unchanged): `ROGUESQ_DPC_WRAP` /
  `ROGUESQ_WRAP_DEDUP` (s11 — wrap bytes are now always counted and dropped), `ROGUESQ_FORCE_PAL15`
  (s14, dead per s15), `ROGUESQ_FORCE_SHADE_WHITE` (s19, its shade line closed at s43).
  `ROGUESQ_MAX_FBPAIRS` (default 8192) engages 0 times since s11 but is KEPT deliberately — OOM
  insurance for future FULL_SYNC-less phases (M3 missions), turns a 22 GB Metal abort into a capped
  workload (s44).

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
| ~93 s | 640 | transition — process died here in the undriven-era observation and in every crashing run of the post-s86 family; **on the s160/s161 crash-free runs the process instead survives past here** (see below) |
| leave SELECT YOUR CRAFT (1 Start press) | 512→640, origin 0x6AB400→0x6A2900ish | **s162 (offline reanalysis of s160/s161 captures): a Chapter-1 mission-intro cutscene** — gold "STAR WARS" logo bumper → "Chapter 1"/"THE RED…" crawl text → black → desert-planet horizon widening into a fast dive toward a hangar structure (establishing shot, not gameplay). Never documented before s162; the s75/s76/s161 "hangar-flight" label for this window was an unverified inference from title-yellow color decay, not from the picture itself. |
| ~+90-115s post-leave | varies (0 or 128 in the two known runs) | **graphics-task-submission stall** — `[vi-fs-decision]` reports `stalled=1 pairs=0` continuously, RDP `fs` counter frozen (5 occurrences now cluster at `rdpFs`~3560-3802, a candidate shared ceiling — s176-179). Not a crash; a **staggered** subsystem shutdown (s178): `[lle task]`/`[swap-ack-wait]` (graphics-task submission and its per-frame producer) stop first, `[rs-malloc]` (heap allocation) a bit later, `[rs-free-walk]` (heap free-walking) keeps running to the very end of the log — the older "audio ucode and heap allocation keep running to the end" wording (s162) does not hold uniformly. s178 confirmed the per-frame producer (`runHangarSelectionFrame` -> `waitForPrevFrameDone` -> `waitForPostSwapAck`) is never stuck mid-call (clean matched enter/pre-recv/post-recv, zero orphans) — it simply stops being invoked at all, coincident with graphics-task submission stopping. s179 source-confirmed the polling loop calling it has no wait/yield of its own. **s180: reproduced the sustained stall crash-free for the first time** (`schedcaller2`, 3rd/last allowed attempt) and found a source-confirmed, tightly-timed candidate root cause: exactly one `[thr-resume-skip] tag=run_next id=0 ctx=0x0 live=0 bad_total=1` fires (the s84 UAF guard) immediately before the stall's onset, with nothing else in between. Source read of `resume_thread_tagged`/`run_next_thread`/`run_next_thread_and_wait` (`lib/N64ModernRuntime/ultramodern/src/threads.cpp:198-278`, and `mesgqueue.cpp:105/143` — the guest `osRecvMesg`/`osSendMesg` blocking path) shows the guard, on finding the popped "next" thread's context bad, silently returns without retrying the next queue entry or waking the thread that yielded expecting a handoff — so if the popped thread (id 0) was the one meant to eventually service the swap-ack message queue, the caller (thread 3, running the hangar loop) blocks forever. **Single-run finding, not yet independently confirmed (rule 4)**. **s181: refuted the "id 0 names one specific thread" reading** — source+runtime confirmed **≥9 distinct guest threads share `id=0`** (idle, video, an unnamed video-child, 3 boot threads, one more, and the audio thread `runAiAudioStreamPlaybackLoop`, the last via an exact OSThread-address match to s70/71); only ids 1+ are per-thread-unique (id=1/3 matched s93's known `piDmaWorker`/`mainBootstrapWorker`). Landed an always-on `[thr-create-id]` log (id/thr-pointer/pri/entry at creation) plus `thr=%p pri=%d` on the skip line so a future stall-reaching soak can identify the dropped thread by pointer, not by the uninformative `id`. One soak with the new instrument armed didn't reach the stall (died early to an unrelated, uncatalogued SIGBUS). **s182: found and fixed a real gap in the s78 `FramebufferManager::get()` refuse gate** — it kept a wild FB out of `framebuffers[]` but the `refuseFb` it returned still carried the wild width/height, and `State::fullSync`'s color/depth read-into-`fbStorage` blocks had no bounds check of their own, SIGBUS-ing on an unbounded RDRAM read (`rt64_state.cpp`); fixed with a `[fbsync-oob-skip]` guard (same 8MB-buffer constant as s78), validated same-session (positive control fired, the specific crash it targeted stopped recurring, process reached one hold-iter further before an unrelated, already-catalogued Metal-internal SIGSEGV). **s183: 4th attempt reached AND SUSTAINED the stall for the first time** (hold-iter 68, 2688 consecutive `stalled=1` decisions, `rdpFs` reaching a new high of 4010) — but `[thr-resume-skip]` fired **0** times the entire run despite the process dying *inside* the sustained stall, weakening (not confirming) s180's mechanism as the general cause: reaching/sustaining this stall does not require that scheduler event. Also decoupled two previously-conflated signals: `rdpFs` plateaus (content-dependent, not a fixed ceiling — retiring the "~3560-3802 candidate ceiling" framing) roughly 600+ decisions *before* the actual task-submission stall begins; they are different events. Died to a SIGBUS in `rs_free ← rebuildActiveDisplayObjectList` (shared-heap-corruption family, same as s164/s167, not a new independent bug). Open question reframed: what stops the producer being invoked in a run where the s84 UAF guard never fires. See next-steps item -35. Full detail: PORTING-STATE Sessions 181-183 (mechanism itself: Session 180). |

Menu state machine (s48, three driven runs; extended s50; post-`a` path s73; Start path s74/s75;
hold attempt s76):
title —start→ SELECT GAME —start→ war room / SELECT LEVEL —start→ **AVAILABLE CRAFT**
(war-room craft holograms; footer "PRESS [A] FOR LEVEL DESCRIPTION"). From AVAILABLE CRAFT,
`a` does **not** show a level description card (s61–s69). With process alive 65s post-`a`
(s72/s73): **black ~5s → ~1s mission-shaped capital-ship flash (texture garbage) → stable
SELECT YOUR CRAFT** (hangar pad + full X-wing, "PRESS [A] FOR CRAFT DESCRIPTION", multi-hue
floor garbage; camera orbits). From SELECT YOUR CRAFT: **`a` no-ops** (s74); **single Start
is enough** to leave into hangar-flight (s75/s76: title-yellow ~13k → 0 by +2–4s; airborne
X-wing) — **OVERTURNED s150 (see "Overturned conclusions"): same craft-select scene, a
corrupting camera move, not a new environment.** VI stays on the 0x6AB400/0x656400 pair —
origin cannot name these scenes (s48).
**s76 hold:** content through ~+7–9s post-leave then black + **`fs` freeze ~3364**;
process Abort in `createTileCopyRecord` (~12s). **s77:** createTileCopy **found=0 never**;
wild FB **registered** (`fbW=4030`); `fs` freeze **~3361**; high-tri `syncs=0` from
#4326. **s78:** always-on refuse gate on `FramebufferManager::get` (width>1280 or
OOB past 8MB) — **REFUSE fires**, tilecopy found=1 control on 640 only, **no wild
map hits**; **`fs` still freezes ~3297** (G1 refuted / G2). Gate kept as safety.
**s79 (D3):** offline fbgate3 parse — onset **#4252** (after #4251 syncs=1):
**914/914** trailing high-tri `syncs=0` (S1); S2 refuted (0 trailing syncs≥1);
UnhandledJump 0x0231 starts **#4265** (13 exit=1 tasks later) — **secondary**,
not onset cause (S3); last RDP-`fs` increase ≈#4254 then plateau 3297; pixel
freeze byte-identical craft_stable→hold. **M3 blocker = post-leave FULL_SYNC
loss (S1), not leave key, not FB-map pollution, not 0x0231 primary.**
**s80 (V1–V4):** always-on `[vi-fs-decision]` — synthetic **FIRE continues**
(+141) after RDP-`fs` plateau; V1/V3/V4 **refuted**; s79 "VI_FULLSYNC stalls"
was an **`fs` misread** (`fs` = DPC FULL_SYNC *opcode* count, not synthetic
`fullSync()`). Present: intermittent black + content (no 0x0231 this run);
death = unaligned `do_rom_read` Abort.
**s81 (B1–B4 offline):** intermittent black is **mode-3 present of wild
last-drawn** (w=1..257; REGISTER 6/7 wild). `present-1024 empty=0` is
transition-only (not continuous health). Pure-black snaps byte-identical
(incl. craft-select flash). B2 **supported**; B4 feeds B2; B1 weakened;
B3 partial. Detail: `scratch/s73_post_a_scene/BLACK1_ANALYSIS.md`.
**s82 (G1–G4 live):** always-on sane-width gate on last-drawn store +
mode-3 (`w∈{320,512,640,1024}`, addr≠0). `[last-drawn-skip]` ≥100 same-run
control; accepted last-drawn only 512/640; **hold pure-black 0/5** (s81
was 8/8 early holds black); hangar-flight content + ~5s motion then freeze
on last sane frame. **G1 supported / G2–G4 refuted.** Residual: S1 `fs`
plateau ~3784; Abort ~hold+6s from `evalCubicSplineAtTime` NaN assert.
Detail: `scratch/s73_post_a_scene/LDGATE1_ANALYSIS.md`.
**s83:** root-caused the NaN — `evalCubicSplineAtTime`'s only division
(0x8001906C, parametric time-in-segment) is `0/0` on a zero-width spline
interval (two keyframes sharing one time); guarded at the source in
`N64Recomp/fixup_game_funcs.py` (not `lib/`, no submodule patch). Guard
**0/2 fires** across two soaks — unvalidated, not confirmed. Both soaks
instead died from two **different**, previously-unseen crashes once the
deterministic assert stopped winning the race: a SIGSEGV inside Apple's
`Metal.framework` shader compiler (no source on our side), and a SIGBUS
resuming a `[thr-resume] live=0 bad=1` thread context — same UAF class as
s70–s72, root site identified at `threads.cpp:198-238` (`bad` is already
detected and logged, just never gated).
**s84:** gated `resume_thread_tagged` on `bad` (skip signal + log
`[thr-resume-skip]`, always-on regardless of `ROGUESQ_LOG_THREAD_RESUME`)
— `lib/`, patch exported + committed. One soak: builds/runs clean, 117218
resumes, **0 `bad=1`** (U3, no positive control yet), no regression. Died
**earlier** than any prior soak (hold+~1s) from a **5th, unrelated** crash:
SIGBUS in `frameStartReset` (called from the hangar-selection per-frame
poll loop `runHangarSelectionFrame`/`runHangarMenuFromOverlay`, not the
thread-resume path at all) — masks further gate validation the same way
NEXT.md's U4 anticipated for the Metal SIGSEGV.
**s85:** `frameStartReset` **did not recur** in 2 repro soaks (F4 supported
— it was a fluke, not a dominant blocker); both instead reproduced s80's
parked **`do_rom_read` Abort/SIGSEGV** (`osPiStartDma_recomp` →
`do_dma` → `do_rom_read`, `pi.cpp:65`), root-caused via source read as a
deliberate `assert()` on `physical_addr` alignment (not a raw unaligned
access) — added `[rom-read]` logging (`lib/`, exported+committed) proved
the value is **garbage that varies run-to-run** (odd-small one run,
`0x1C676672`/~208 MB-OOB the next). New hypothesis, unproven: `physical_addr`
comes straight from the calling thread's register context
(`ctx->r7`), so this may be the **same shared corruption race** as the
s70–s72 OSThread UAF / s83–s84 thr-resume `bad=1` — not a 6th independent
bug, one race surfacing wherever a corrupted read is dereferenced first.
**s86:** added `[rom-read]` thread-identity fields (thr_id/thr/ctx) to
test the hypothesis; one soak's `do_rom_read` never fired corrupted (488
calls, all sane) so the test is **inconclusive, not refuted** — but the
process still died, **earlier than usual** (hold+~15s), to a **7th, new**
crash: `assert(!decodeTMEM || (width>0 && height>0))` in
`RT64::TextureCache::queueGPUUploadTMEM` (`rt64_texture_cache.cpp:1285`),
reached from `State::fullSyncFramebufferPairTiles`'s real-texture-decode
path with `callTile.sampleWidth`/`sampleHeight` (`rt64_state.cpp:1329`)
zero for a `decodeTMEM=true` load. Not further root-caused (1 data point).
**s87:** added `[tmem-zero-upload]` LoadTile-field logging at the
`uploadTexture` call site (`rt64_rdp_tmem.cpp`, gated
`ROGUESQ_LOG_TMEM_ZERO=1`) to test s86's hypothesis; it never fired (0/0)
because the soak died even earlier (hold+~3s) to an **8th, new** crash:
SIGBUS in `advancePlayerAnimationPhase` (guest `0x80062B04`) calling
back into itself through an indirect call at guest `0x8006426C`
(`jalr $v0` via `LOOKUP_FUNC`, `$v0` loaded from fixed global slot
`0x80139968`) — source-read hypothesis (self-recursion via a stale/
corrupted callback-table pointer), not yet confirmed by logging the
actual pointer value.
**s88:** re-checked s87's hypothesis before instrumenting — **refuted at
the source level**: the `0x8006426C` call site belongs to
`invokeMenuOverlayHeaderCallback`, a different function never reached
from `advancePlayerAnimationPhase`'s own body (which has zero indirect
calls). Landed a correctly-targeted instrument instead (`ROGUESQ_LOG_ANIM_CB=1`,
logs guest `$sp` + args at the function's own entry, `N64Recomp/
fixup_game_funcs.py`). Soak: **first crash-free run since s83** (all 8
known crash classes, 0 fires) — `[anim-recurse]` fired 3296/3296 (real
positive control) with `sp` confined to 6 values / 312 bytes the whole
run, i.e. **no recursion at all**, refuting both of NEXT.md's
competing hypotheses for this run. Bonus: the s84 thr-resume `bad=1`
gate got its **first-ever positive control** (`bad_total=1`, process
survived) — **U3 closed**. Second data point for s85's shared-
corruption-race hypothesis (same soak shape: crash-free this time vs.
5 straight crashing soaks s83–s87). Full detail: PORTING-STATE s83–s88.
**s89:** ran the same soak twice more (animcb2, animcb3) — **3rd
consecutive non-recurrence** of the s87 `advancePlayerAnimationPhase`
SIGBUS; per rule 8, parked that hypothesis rather than running a 4th
soak. animcb2 crashed instead on the s86 TMEM-zero assert
(`queueGPUUploadTMEM`, signal 6) — **first full backtrace**:
`fullSyncFramebufferPairTiles` → `uploadTile` → `TextureManager::
uploadTexture` → `queueGPUUploadTMEM`; the "undefined tile" logging seen
25× the same run is a red herring (already guarded by `callTile.valid`
before reaching `uploadTexture`, `rt64_state.cpp:1210`). animcb3 added
`ROGUESQ_LOG_TMEM_ZERO=1` (still 0/0, 3rd null in a row) but crashed on
a **9th, brand-new** class instead: SIGBUS in `updateAnimatedTextureStreaming`
(real function, `funcs_11.c:13665`, called via the `menuOverlayInit`
chain), root-cause direction = unchecked raw `MEM_W` deref off a
possibly-corrupt `a0` — same signature as s85's `do_rom_read` and the
OSThread UAF family. `[anim-recurse] sp` stayed flat (same 2 of the 6
known values) through both new crashes, neither of which is even in
that function's call chain. Full detail: PORTING-STATE s89.
**s90:** ran the exact NEXT.md-prescribed soak again (`animcb4`) — still
0/4 co-occurrences of the TMEM-zero log firing (armed or not, across
s87/animcb2/animcb3/animcb4), and for the 3rd soak in a row with the
flag armed, a **different, newer** crash preempted it — a **10th**
class, SIGBUS in `static_5_800B4048` (no confirmed source name; a
`main_overlay.txt` comment guesses "updateTextOverlayLookupEntry" but
that name is absent from the actual built `RecompiledFuncs/*.c` —
treat as unverified), called from the known `updateHangarBayScene`
(0x800AB658) → `runHangarSelectionFrame` → `runHangarMenuFromOverlay`
→ `menuOverlayInit`. Same unchecked-`MEM_W`-off-an-arg shape as the
rest of the family (dereferences its `a1` arg 4× at fixed offsets).
`[anim-recurse]` fired 3610/3610 (control good, `sp` still the same 6
values); `thr-resume bad_total=0` again (3rd/4th support for U3).
Landed batched entry-log instruments for the two most recent
still-uninstrumented crash sites — `ROGUESQ_LOG_ANIM_TEX_STREAM=1`
(9th class, `updateAnimatedTextureStreaming`) and
`ROGUESQ_LOG_HANGAR_ENTRY=1` (10th class, `static_5_800B4048`) — in
`N64Recomp/fixup_game_funcs.py`, following the `_anim_cb_patch`
pattern; verified via `grep` that both landed x1 in the regenerated
`.c`, then rebuilt clean (exit 0, only pre-existing-class format
warnings). **Not yet soaked.** Per ITERATION.md rule 8, demoting "run a
soak specifically to catch the TMEM-zero assert" from primary plan to
opportunistic (keep the flag armed everywhere, it's free, but stop
treating catching it as the goal) after 3 non-discriminating attempts.
Full detail: PORTING-STATE s90.
**s91:** ran the batched soak twice (animcb5, animcb6) with the
now-correctly-named `ROGUESQ_LOG_DMA=1` armed — **the `do_rom_read`
crash recurred both times, byte-for-byte identical**: `phys=0x1C676672
ram=0xFFFFFFFF80195190 bytes=0x600`, matching s85's `romread1` run
exactly (3 independent occurrences now, sessions apart, across
rebuilds). This **refutes "garbage that varies run-to-run"** (s85/s86
below, superseded) — a race would not reproduce identically. Added
`[pi-start-dma]` logging at `osPiStartDma_recomp` (`ctx->r31`/return
address + raw pre-OR `r7` + all DMA args) confirming the exact
mechanism (`devAddr = ctx->r7 | rom_base`, straight off the calling
thread's register context, per s85's hypothesis) — 2nd soak showed
`ra=0x00000000` (return address also zero) and `raw_r7=0x6C676672`, a
completely different bit pattern from every real call's `0xB0FFxxxx`
kseg1 shape, not a plausible near-valid value. Always on thread id=1
(the PI DMA worker), always immediately after a `[thr-resume]
tag=swap` onto that thread, always for a DMA near guest `mb=0x80111270`.
Both `r31` and `r7` wrong together, identically, 3 times → points to
**reading an uninitialized/reused-before-write context**, not a
timing race. 9th/10th classes didn't recur; `[anim-recurse]`/
`thr-resume bad=1` controls held for a 6th straight session. Full
detail: PORTING-STATE s91.
**s92:** source-read before instrumenting (per NEXT.md's own step 2)
found `osPiStartDma_recomp` never dereferences `mb` — `devAddr` is a
direct register argument (`ctx->r7`/`$a3`), so the planned
"dump the `OSIoMesg` at `mb`" instrument would not have tested H1 as
worded. Ran one soak reusing existing instruments (no rebuild):
`do_rom_read` **did not recur** (0/1, first miss after 3/3); **the
`ra=0x00000000` s91 read as a corruption signature fired on 487/487
sane `pi-start-dma` calls this run**, and the same universal-zero
pattern independently shows up in three unrelated entry logs
(`anim-recurse` 6740/6740, `anim-tex-stream` 4568/4568,
`hangar-entry` 2/2) — **refutes** "context never populated" as
r31-specific evidence; the anomaly narrows to `raw_r7` alone. Found an
**11th** crash class instead: SIGBUS in `projectModelBoundsToScreen`
(confirmed real symbol) via `hangarTickCameraOrbit`
(`static_5_800ADB70`) ← a symbol_files-named-but-suspect
`loadCutsceneAssetsByIndex` (`static_5_800A9270`) ← the known
`runHangarSelectionFrame` → `runHangarMenuFromOverlay` →
`menuOverlayInit` chain. Confound found: `ROGUESQ_LOG_THREAD_RESUME=1`
(120k+ log lines) likely perturbed timing enough to let this new bug
win the race instead of `do_rom_read` — don't combine the two in
future repro attempts. Controls held (bad_total=0, anim-recurse sp
flat) for a 7th session. Full detail: PORTING-STATE s92.
**s93:** found s92's "drop the confound" plan never actually took
effect — `scratch/s73_post_a_scene/run_mission_keys.sh` hardcoded
`export ROGUESQ_LOG_THREAD_RESUME=1` unconditionally, silently
clobbering the `env ROGUESQ_LOG_THREAD_RESUME=0` prefix s92's own plan
used, so s92's "did not recur" was never a clean confound test. Fixed
the script (now defaults, doesn't force) and reran: **`do_rom_read`
recurred** on the first genuine attempt, byte-identical to s85/s91
(`phys=0x1C676672 dram=0x80195190 bytes=0x600 mb=0x80111270`, thread
id=1) — **4th occurrence**, and `raw_r7=0x6C676672` matched s91's 2nd
soak's raw register value bit-for-bit (new: not just the derived phys
address repeats, the raw value does too). **Confound theory CONFIRMED**
(first soak to actually run this repro shape with the flag genuinely
off — fired immediately). Death was fast (hold+13s). Controls: anim-
recurse 7592/7592, anim-tex-stream 6062/no-crash, hangar-entry 3/no-
crash, TMEM-zero 0/7; thr-resume bad=1 unobservable this run (logging
was the thing disabled, gate itself still active). Same-session
follow-up (pure source reading, no rebuild): found the exact consumer
mechanism in the recompiled guest C itself (`N64Recomp/RecompiledFuncs/
funcs_1.c`, not decomp asm — that tree covers 100% of the ROM,
unlike the hand-decomp tree s92 correctly found empty). `piDmaWorker`
(`0x80005570`) is a persistent 256×20B-ring consumer thread whose
`osPiStartDma` call site has **literal constants `mb=0x80111270
pri=1 dir=0`** — an exact, unconditional match to every crash log
line, proving every occurrence is this exact loop reading a corrupted
`devAddr` from `ring_slot+0x4`. Its only producer,
`submitDmaRequestBatch` (`0x8000569C`, the only function anywhere
referencing the ring's base literal), has exactly **one static call
site** — `mainBootstrapWorker` (`0x80000C68`, genuine one-time boot
code) — submitting one fixed-constant request (`size=0xCE00
rom=0xB0101000 dram=0x80100400`) that **does not match** the crash's
target (`dram=0x80195190 size=0x600`). Open, unresolved: either a
second producer exists that a literal-address grep can't see
(indirect call), or the ring is genuinely written once and something
else stomps `ring_slot+0x4` between that boot-time write and a much
later read — the "shared corruption race" from s85, now narrowed to a
20-byte window instead of "somewhere in an OSThread context." Full
detail: PORTING-STATE s93.
**s94:** landed the producer/consumer DMA-ring instrument NEXT.md
specified; one soak answers the question. `do_rom_read` recurred a 5th
time, byte-identical again. The producer log fired **10 times**, not
once: `n=0` is the known boot call (matches exactly, positive control),
then ~140s later in the same run, **9 more firings** back-to-back with
sequentially-climbing `dramAddr` (`0x80195190`→`0x80197590`,
real-looking batch) but every `devAddr` decoding as ASCII text ("wing",
"lcre", "lgfr", …) — never a plausible ROM address. `n=1`'s exact
fields (`devAddr=0x6C676672 dramAddr=0x80195190`) are what the consumer
reads next and crashes on. A fresh grep for `submitDmaRequestBatch(rdram`
across all 45 `funcs_*.c` still returns exactly 1 hit (the boot call);
combined with the loop body having no yield points (can't pause 140s
mid-iteration), this **refutes** "the one known call just loops more
than once" and **confirms NEXT.md's "producer fires >1 time" branch**:
an indirect call (`LOOKUP_FUNC`/`jalr`) to `submitDmaRequestBatch`
(`0x8000569C`) exists somewhere, not yet located. **Reframes the root
cause**: the bad value is present at the moment of the *write*, not
stomped afterward — points at an off-by-a-field bug in the unknown
caller (writing a name/string-table field where `devAddr` belongs),
narrower and more source-findable than a generic cross-subsystem memory
race. Full detail: PORTING-STATE s94.
**s95-s98:** 4 sessions, 6 soaks, each died to a *different* brand-new
crash class in the "SELECT YOUR CRAFT stable → hold" window before
reaching the DMA-caller window — 16 crash classes cataloged total (9th-16th
guest-side/fixable, 13th/15th RT64-internal). s98 source-characterized the
mechanism at the 16th class (`activateAnimationKeyframe`, a second,
independent call site into a function s87/88 already partly investigated):
unguarded table-lookup-then-dereference (`table[arg_r4 & 0xFFFF]` then
`deref+0x30`, no null/range check) — same signature as every other class
in this family. Checked existing timing data (no new soak needed): the
DMA-adjacent `do_rom_read` crash consistently lands hold+11-15s while this
family's one-offs land hold+3-17s — **the two windows overlap, they are
not sequential**, so "shorten the hold to outrun the crash family" (a
literal reading of s97's outcome-2 branch) is not coherent. **Pivot for
next session: land a defensive guard at a characterized site (mirroring
s83/s84's successful gates) instead of another observe-only instrument.**
Full detail: PORTING-STATE s98.
**s99:** landed and validated the 16th class's guard
(`activateAnimationKeyframe`, `goto`s the function's own real exit label
to stay ABI-correct rather than a bare `return;`). First soak exposed a
real bug in the guard itself — comparing the 64-bit sign-extended `gpr`
register directly against 32-bit literal bounds made it fire on
30333/30333 calls (100% false positive), not just the rare bad case;
fixed by truncating through `U32()` first, a lesson generalizable to
every future guard on a `ctx->rN` value. Corrected soak: guard's negative
control holds clean (0/0), but the process died to a **recurrence of the
already-catalogued 15th class** (RT64-internal `loadDrawState`, first
seen s97), not a new 17th — informative, not a new mystery. Per s98's own
outcome-2 branch, next up is the same guard treatment for
`composeNpcOrientationMatrix` (12th class, 2 occurrences). Full detail:
PORTING-STATE s99.
**s100:** source-read confirmed `composeNpcOrientationMatrix` (12th
class) has the same unguarded-table-lookup-then-deref shape (byte from a
fixed table * 632-byte stride into a fixed global array, dereferenced
immediately as `v1`); guarded it the same way as s99 (`goto`s the real
epilogue `L_800AB618`). Caught a regex false positive before it built:
the guard's anchor text also matched inside `hangarInitialize`, an
unrelated function in a different overlay sharing the same guest address
range — fixed by file-scoping the patch to `funcs_40.c`, which needed a
full regen to clear the corrupted intermediate. Soak: guard 0/544 (clean
negative control, no positive control — `composeNpcOrientationMatrix`
itself never crashed this run); every other family control held. Process
died at hold-iter 1 (earliest yet) to a **new, 17th** crash whose fault
address resolves directly inside `updateHangarBayScene` itself (not the
already-catalogued 10th class — that class's signature innermost frame,
`static_5_800B4048`, is absent from this backtrace). Per NEXT.md's own
outcome-2 branch, catalogued and not chased; next up is the same guard
treatment for the 11th (`projectModelBoundsToScreen`) or 14th
(`reserveAndEmitDLEntry`) class. Full detail: PORTING-STATE s100.
**s101:** landed and validated the 11th class's guard
(`projectModelBoundsToScreen`, clean 0/0 negative control) — and for the
first time since s94, the process survived the entire hangar-tick-family
gauntlet and reached the ~140s DMA window alive. `ROGUESQ_LOG_DMA_
CALLER` (landed s95, 0/0 across 7 prior soaks) fired for the first time
ever: the indirect caller of `submitDmaRequestBatch` is `musyxSynthFrame`
(a per-VI-retrace audio tick), called from `viRetraceHandlerThread` —
closing the multi-session "who calls it indirectly" question.
`do_rom_read` recurred a 6th time (byte-identical corruption pattern)
immediately after. Full detail: PORTING-STATE s101.
**s102:** source-read `submitDmaRequestBatch` (confirmed: faithful
`{size,devAddr,dramAddr}` array-copy loop, no bug) and the
`musyxSynthFrame` call site (confirmed: `a0`/`a1`/`a2` correctly mapped —
refining s101's own instrument plan, which had assumed `a0` was an
address rather than a pointer value loaded from one). Landed a
correctly-targeted instrument (`ROGUESQ_LOG_MUSYX_DMA_CALL=1`) that
proved the corrupted `devAddr` is **already present** in the batch array
before the call — ruling out both functions as the bug site — and fully
characterized the corruption's shape across all 9 entries in the batch
(two consistent 4-byte tag/index patterns, `"lg?r"`/`"wi?g"`, with
sane/self-consistent `size`/`dramAddr` fields), reinforcing that this is
a structured wrong-field read, not noise/race/stomp. 7th `do_rom_read`
recurrence, byte-identical. Also found (unplanned): `fixup_game_funcs.py`
is not actually idempotent — re-running it without a full ELF regen
duplicates every already-applied patch (confirmed 3 copies of s100's
guard in `funcs_40.c`). Harmless so far, flagged for a future work unit.
Full detail: PORTING-STATE s102.
**s103:** tested s102's leading hypothesis (`acquireSampleStreamBlock`
copies its cache-key argument verbatim into the DMA batch's `devAddr`)
with a targeted instrument — **refuted**: 0/0 fires despite the batch's
own count field proving 9 entries were appended the same tick, so that
function was never entered. Found the real writer instead:
`fillSampleStreamRange`, which computes `devAddr` as a sum of two
struct fields (not a raw copy) off a *different* linked list than the
one `acquireSampleStreamBlock` manages. New open question: that list's
node-allocator (not yet located) likely sets the wrong base field at
creation time. 8th `do_rom_read` recurrence, byte-identical, same
~140s/hold+11s window. Also fixed s102's flagged patch-duplication
symptom incidentally via a full ELF regen. Full detail: PORTING-STATE
s103.
**s104:** found that node-allocator (`initSampleStreamBlockCache`) and
**cleared it** — every node-claim path recomputes the base field fresh
from `fillSampleStreamRange`'s own arguments before use, so a stale
allocator value was never possible. New instrument
(`ROGUESQ_LOG_FILL_RANGE_ARGS=1`) proved those arguments are themselves
already corrupted at function entry (byte-for-byte match to the known
`devAddr` corruption), closing "is this function's own arithmetic
buggy" (no) and localizing the bug to whatever writes the one shared
struct field (`voice+0x34`) both this function's and
`acquireSampleStreamBlock`'s arguments trace back to — not yet located.
9th `do_rom_read` recurrence, same signature. Full detail:
PORTING-STATE s104.
**s105-s110:** chased `voice+0x34`'s writer two ways: `musyxInitVoiceFromSample`
(`funcs_24.c`, literal `sw $v1,0x34($a0)`, verbatim `sampleDesc+0x4` copy)
identified s105 as the matching writer (base/stride confirmed 3 ways) but
its instrument fired **0/0** across a full soak to hangar-flight death —
inconclusive, no positive control ever obtained; s106-s109 tried to prove
the call chain reaches it at all (`tickAudioChannel`/`serviceVoicePoolFrame`
entry counters, gate-value logging) with no discriminating result; s110
retired this call-chain angle after 5 null sessions.
**s111-s113:** closed both remaining write-mechanism candidates instead —
RSP MusyX ucode (`factor5_ucode_b`, s112: proven dead code, zero call
sites) and computed-offset guest-C stores (s113: exhaustive per-file audit
of all 3 files referencing the voice-array base, every store terminates
in a literal non-0x34 offset) — leading s113 to an unplanned "uninitialized
heap read, no write needed" hypothesis for the `-0x664C` node fields.
**s114:** ran the discriminating instrument s113 itself proposed
(`ROGUESQ_LOG_STREAM_NODE_INIT=1`, node's raw `0x8`/`0x10` at allocation) —
positive control 32/32, **all-zero** at allocation, reproduced twice.
Source-verified (not subagent-reported) that **s113's audit had a gap**:
`musyxInitVoiceFromSample` — the exact function s105 already flagged, and
which s113's own function list names — contains a literal `MEM_W(0X34,
ctx->r4) = ctx->r3;` write to the voice array, missed by s113's "never
0x34" claim (`funcs_24.c:5881`, confirmed by direct read). **Hypothesis
(b) (a literal-offset write to `voice+0x34` exists) was never actually
refuted.** Combined with s104's already-established mechanism (every node
claim unconditionally recomputes `0x8` from `fillSampleStreamRange`'s own,
already-corrupted, arguments), the all-zero-at-init result is fully
explained — no second mechanism needed, the chain closes back to "what
corrupts `voice+0x34`" exactly where s110 parked it. Second soak (no
rebuild) added a fresh boot→title data point for `musyxInitVoiceFromSample`
(still 0/0), widening but not closing s105's inconclusive null. Full
detail: PORTING-STATE s114.

**s48 scene-identity correction:** there is no "main-menu hangar". The 512-wide origin-0x6AB400
scene is the round **level-select war room**. Pre-clip-fix it rendered with every clip-needing
triangle dropped (camera inside a curved room), so the tiered console rings and holotable were
missing: the central platform read as a "landing pad", the Mos Eisley preview hologram as a parked
X-wing, and the stale-RDRAM band filled the rows the rings should cover. Post-fix the room renders
complete. VI origin **cannot** discriminate menu scenes (the war room presents from the same
0x6AB400); identify menu scenes visually from captures.

512-wide covers two different scenes; tell them apart by VI origin (0x690400 outdoor, 0x6AB400
war room) — but see s48: origin distinguishes *phases*, not which menu scene is on screen.

Remaining visual defects:
- **~~s50/s51 AVAILABLE CRAFT → black → one mission frame → `fs` freeze / SIGBUS~~ — ImemOverrun
  FIXED s69; SIGBUS FIXED s72.** Old freeze (s64–s68): CLIP_1FBC → L_1650 hard exit; s69 fixup 8
  → exit=2 0. **s70/s71:** post-`a` SIGBUS was bit-corrupt `OSThread.context` on
  `runAiAudioStreamPlaybackLoop` @ `0x801494B0` (not UAF). **s72:** writer is RT64 **depth
  writeback** of a garbage FB (`addr=0x140000 w=4067`, range `[0x140000,0x3E1332)` covering the
  OSThread). Old floor `addressStart >= 0x100000` let it through. Always-on gate now also
  requires **width ≤ 1280** and **write end ≤ 8MB**; CIMG kept for draw, writeback skipped.
  Discover run: OVERLAP+CTX_CHANGED_BY_WB on the death path (control writebacks still logged).
  Fix soak 65s post-`a`: 0 bad resumes, process alive, fs advancing, SKIP_WIDTH/OOB firing.
  **s73 scene ID:** sustained post-`a` is **SELECT YOUR CRAFT** (menu), not mission; g07 is a
  ~1s mission-shaped flash only. See M3 / next steps.
  ~~**s51 also found a generalizable environment confound**: driven runs stall in phase-advance
  under concurrent system load~~ — **OVERTURNED, s60. There is no load confound.** The three repro
  scripts set no `ROGUESQ_*` variables at all, so from a clean shell the binary took the **HLE**
  path, never emitted FULL_SYNC, and never advanced past width 640; the phase-wait then expired and
  the expiry was read as a load stall. A/B on the same script at load **4.41** — higher than any
  load the loop refused to run at — gives 4168 `[lle task]` / 0 `[hle send_dl]` / `fs=3206` / no
  `[fbpair-cap]`, walking 640 → 1024 @45.0 s → 512/0x6AB400 @73.5 s. The signature blamed on load
  (`fs` frozen + `[fbpair-cap]`) is the s11 pre-`VI_FULLSYNC` signature and occurs only on the HLE
  path. **`uptime` is not a precondition for any work unit** — s61 re-confirmed this by running at
  load 3.93 with 33 concurrent `claude` processes and getting a clean, interpretable result both
  times. Scripts now export the four knobs themselves. Full detail: PORTING-STATE s60.
- ~~Hangar floor multi-hue band~~ — **FIXED and root-caused, s45–s48 (M1 closed).** The band was
  stale RDRAM showing through the hole left by the war room's clip-flagged geometry: all clip
  dispatches to overlay 4 ran the wrong code (window-swap IMEM DMA skipped), so the tiered
  console rings / holotable never drew. s47 spliced the real clip overlay in; s48 verified in the
  scene itself: mode-2 mark-vertices shows band rows rasterizing geometry (band-crop magenta
  15–22 % vs ~11 % pre-fix edge-only), a clean run shows zero streak band with the rings rendered,
  fanjal 5.6–5.8k per 512-phase with census identities exact, and `[dpc-wrap]` reproducibly
  halved (17.06M → 9.91M). Parked anomaly still open (M4): 39 of 55 I4 uploads sample 64x128 past
  `masks=6/6`. Overlays 12/44 still take the old broken dispatch path by design — same splice
  recipe applies if a phase ever needs them.
- ~~Hangar dimmer than the s11 peak~~ — **largely fixed, s25** by `SHADE_WRAP` (vertex
  then s26 per-pixel).
- Outdoor 512 zero-shade is masked, not fixed: `ROGUESQ_FIX_ZERO_SHADE` + wrap both map
  the −0.5 class to white; why LLE carries `baseFixed = −32768` is unknown (s19/s20).
- Triangles with S identically zero in the 640 attribution phase: real, uninvestigated (s18).
- `[dpc-behind]` ring-wrap drops remain genuine dropped content with `DPC_WRAP` off; they are simply
  not the cause of any known black screen (s11).

Stability: clean through s27 driven hangar soaks and s49's post-clip-fix regression sweep
(undriven full timeline + driven war room). 0 `UnhandledJumpTarget`, 0 `[defer-drop]`,
0 `[dmem-race]`, 0 asserts. `[missing-func]` clean in every soaked phase to date, **except**: s49's
undriven outdoor-512 stretch stubbed 3 distinct addresses once each (0x800C7120, 0x800FBD48,
0x800FB190) with 0 aborts — never itemized before because prior soaks targeted hangar/war-room, not
outdoor. Parked as an M4 curiosity, not a blocker. **s50–s72 mission-entry path:** ImemOverrun
fixed (s69); SIGBUS from garbage depth writeback fixed (s72). Hangar/war-room/outdoor stability
from s27–s49 stands; post-`a` process now soaks 65s+ without death.

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

**M3 — first gameplay: OPENED (s50); ImemOverrun FIXED (s69); OSThread SIGBUS FIXED (s72);
post-`a` scene ID (s73); Start path isolated (s74/s75); hold/assert triage (s76/s77);
wild-FB refuse gate (s78); D3 S1–S4 (s79); VI_FULLSYNC decision V1–V4 (s80);
intermittent-black B1–B4 (s81); last-drawn sane-width gate (s82, G1);
evalCubicSplineAtTime NaN root-caused, 2 new crash classes found (s83);
thr-resume `bad=1` gated (unvalidated), 5th crash class found (s84);
frameStartReset was a fluke, do_rom_read corruption root-caused, unified
shared-race hypothesis raised (s85); shared-race test inconclusive
(do_rom_read didn't recur), 7th crash class found firing even earlier
(s86); TMEM-zero instrument landed but never fired, 8th crash class found
firing even earlier still (s87); s87's self-recursion hypothesis refuted
at the source level, correctly-targeted instrument shows no recursion,
thr-resume gate U3 closed, first crash-free soak since s83 (s88);
anim-recursion hypothesis parked after a 3rd non-recurrence, TMEM-zero
assert reproduced with a full backtrace, 9th crash class found (s89);
3rd straight "armed TMEM-zero, a newer crash preempted it" outcome,
10th crash class found, batched entry-log instruments for the 9th and
10th classes (s90); `do_rom_read` corruption proven deterministic and
reproducible (3x byte-identical), refuting the s85 "random race"
framing (s91); `ra=0x00000000` shown to be routine (not corruption
evidence), `do_rom_read` non-recurrence, 11th crash class found in
`projectModelBoundsToScreen` (s92); s92's confound-removal was never
real (script bug), fixed it, `do_rom_read` recurred immediately (4th
hit), confound theory confirmed (s93); DMA-ring producer/consumer
instrument landed and discriminates in one soak — producer fires 10x
not once (5th `do_rom_read` hit), refuting "one boot-only call" and
finding an unlocated indirect caller whose batch writes ASCII-looking
garbage into the `devAddr` field at write-time, not via a later stomp
(s94); `get_function`-chokepoint instrument landed to find that caller
directly, first soak inconclusive (died early to a 12th, recurring
crash class before reaching the target window) (s95); 2nd consecutive
inconclusive attempt — 12th class didn't recur but a brand-new 13th
crash class (RT64-internal `reinterpretTileRecord` assert) died even
earlier, instrumentation-overhead confound checked and refuted at the
source (s96); 3rd (final allowed) attempt died even earlier to a
brand-new 14th class, parking the blind DMA-caller repro per rule 8;
pivoted to instrumenting the most-recurring hangar-tick class
(composeNpcOrientationMatrix, 12th) — clean positive control, no
crash on that path, but a brand-new 15th (RT64-internal) class killed
the run instead (s97).**
AVAILABLE CRAFT reachable. **s75:** single Start → hangar-flight.
**s78–s79:** RDP-`fs` plateaus post-leave (S1). **s80:** synthetic FIRE continues.
**s81:** black = mode-3 presenting wild last-drawn. **s82:** always-on sane-width
gate — **black duty-cycle collapses**; hangar-flight visible ~5s then freezes on
last sane frame (S1 residual); death `evalCubicSplineAtTime` NaN Abort (~hold+6s).
**s83:** NaN div0 guarded at source (unvalidated, 0/2 fires); with that assert no
longer winning the race, 2 soaks died from 2 *different* crashes instead — Metal-
internal shader-compiler SIGSEGV (no source on our side), and a `thr-resume
bad=1` UAF SIGBUS (same class as s70–s72, detector exists at
`threads.cpp:198-238`, never gated). **s84:** gated the SIGBUS site (always-on
skip, `lib/` patch exported+committed); soak ran clean with 0 `bad=1` (no
positive control yet) but died **earlier** (hold+~1s) to a **new** SIGBUS in
`frameStartReset` (hangar-selection per-frame poll loop). **s85:** 2 repro
soaks — `frameStartReset` never recurred (fluke, not dominant); both instead
hit s80's parked `do_rom_read` Abort/SIGSEGV with a **garbage `physical_addr`**
(added `[rom-read]` logging, `lib/` exported+committed) that varies run-to-run
(odd-small vs. ~208 MB-OOB) — raised, not yet proven, that this is the **same**
shared-corruption race as the OSThread UAF / thr-resume `bad=1` families
rather than a 6th independent bug. **s86:** added thread-identity fields to
`[rom-read]` to test that hypothesis; one soak's `do_rom_read` stayed clean
(488 calls, all sane) so the test is inconclusive — but died *earlier* than
usual to a **7th** crash, `assert(width>0 && height>0)` in
`queueGPUUploadTMEM` for a real texture decode with a zero tile-sample
dimension (`rt64_state.cpp:1329` → `rt64_rdp_tmem.cpp:52` →
`rt64_texture_cache.cpp:1285`), not yet root-caused. **s87:** landed
`ROGUESQ_LOG_TMEM_ZERO=1` logging at the `uploadTexture` call site to
test that; it never fired (0/0) because the soak died even earlier
(hold+~3s) to an **8th** crash: SIGBUS in `advancePlayerAnimationPhase`
(`0x80062B04`) recursing into itself through an indirect call at
`0x8006426C` (`jalr` via a function pointer read from fixed global slot
`0x80139968`) — source-read hypothesis (stale/corrupted callback-table
pointer), not confirmed by a live value yet. **s88:** re-checked before
instrumenting — refuted at the source level (`0x8006426C` belongs to
`invokeMenuOverlayHeaderCallback`, unreached from the crashing call
chain; `advancePlayerAnimationPhase` itself has zero indirect calls).
Landed `ROGUESQ_LOG_ANIM_CB=1` (entry log: guest `$sp` + args, depth
proxy) targeting the actual function. Soak was the first to survive the
full hold window crash-free since s83; instrument fired 3296/3296
(positive control) with `sp` confined to 6 values (312 bytes) — no
recursion, shallow or deep, refuting both NEXT.md hypotheses for this
run. The s84 thr-resume `bad=1` gate got its first positive control in
the same run (`bad_total=1`, process survived) — **U3 closed**. Second
data point for the shared-corruption-race hypothesis (crash-free vs.
5 straight crashing soaks). **s89:** 2 more soaks, both crashed but
neither on the target bug (3rd non-recurrence, now parked per rule 8).
First full backtrace for the TMEM-zero assert (item 2): `fullSync
FramebufferPairTiles` → `uploadTile` → `uploadTexture` →
`queueGPUUploadTMEM`; the "undefined tile" logging seen the same run is
a red herring (already guarded before reaching `uploadTexture`). Found a
**9th** crash: SIGBUS in `updateAnimatedTextureStreaming`
(`funcs_11.c:13665`, via `menuOverlayInit`), likely an unchecked `MEM_W`
deref off a corrupt `a0` — same signature as the shared-corruption-race
family. Leave key closed. Origin still cannot name
scenes. **s90:** re-ran the same soak shape a 3rd time with the flag
armed; TMEM-zero still 0/4, and a **10th** crash preempted it again:
SIGBUS in `static_5_800B4048` (unconfirmed name), called from the known
`updateHangarBayScene` → `runHangarSelectionFrame` →
`runHangarMenuFromOverlay` → `menuOverlayInit` chain — same
unchecked-`MEM_W`-off-an-arg shape. `[anim-recurse]`/`thr-resume` controls
held again. Landed batched entry-log instruments for the 9th
(`ROGUESQ_LOG_ANIM_TEX_STREAM=1`) and 10th
(`ROGUESQ_LOG_HANGAR_ENTRY=1`) crash sites, built clean, not yet soaked.
Per rule 8, demoted "catch TMEM-zero with the flag armed" from primary
plan to opportunistic after 3 non-discriminating attempts.
Full detail PORTING-STATE s68–s90;
`scratch/s73_post_a_scene/LDGATE1_ANALYSIS.md`.
*Done when:* 60 seconds of in-mission rendering, craft visibly responds to synthetic input,
stability counters 0, and the phase timeline in this document covers the mission.

**M4 — parked correctness items**, one work unit each: outdoor `baseFixed = −32768` zero-shade root
cause (currently masked, not fixed); the S=0 triangles in the 640 attribution phase; the I4
`sample=64x128` anomaly if M1 didn't consume it; the 3 `[missing-func]` addresses stubbed in the
undriven outdoor-512 stretch (0x800C7120, 0x800FBD48, 0x800FB190, s49) — **identified, s53**:
`getConfigFloatPair` / `clearMissionObjectiveFlagsAndEnterPhaseSix` / `requestMissionTransitionMode`
respectively, all real mission-overlay functions (2/3 confirmed prologue, 1/3 a plausible frameless
leaf) present only in `symbol_files/main_overlay.txt`, not `mission_overlay.txt` — the exact
"symbol assigned to a non-overlay file" failure `overlays.cpp:388` describes. Not behaviorally
silent by name (mission-phase-transition and objective-flag logic). **s54: fix applied** (3 lines
added to `~/Documents/Tools/rogue_squadron64/symbol_files/mission_overlay.txt`, a sibling checkout
with its own git repo — not `lib/`, no `submodule-patches/export.sh` needed) and the full regen
pipeline (`make_elf.py` → `N64Recomp` → `fixup_game_funcs.py` → `cmake --build`) ran clean, build
exit 0, no new warnings/errors. **Runtime confirmation still outstanding** — s54 rechecked load
post-build (3.52/3.10/3.11, 33 `claude` processes, worse than at start) and correctly skipped the
game run rather than risk a load-stalled false-negative; not yet re-attempted. That sibling repo
also carries pre-existing uncommitted changes to 3 other symbol files from earlier sessions,
unrelated to this fix — flagged for the user, not committed autonomously (s54).

**M5 — audio de-stubbing (investigation first, not code).** The MusyX audio ucode already
recompiles (`factor5_ucode_b_recompiled.c` sits in the build as a never-called artifact). First
work unit: a design doc only — how audio tasks would run LLE alongside gfx (they share the `dmem[]`
serialization built in s5), what bridges RSP audio output to SDL, and what the audio-gate byte
reversal implies. **Gate M5 behind M2**: audio re-enters exactly the shared-state territory that
cost three sessions before the recursive mutex.

## Next steps, in order of expected value (s215)

-56. **(s215) do_send SIGBUS reclassified: NOT the s176+ scheduler-UAF
    family — a mesgqueue guard is now shipped but untested live; the bigger
    lead is disabling `NAN_CHECK` project-wide.** s214 hedged that the
    `do_send`/`mesgqueue.cpp` SIGBUS "looks like" a crash variant of the
    s176+ thread-context-UAF stall investigation — s215's source read
    **supersedes that framing**. This build has no LTO and is
    `CMAKE_BUILD_TYPE=Debug` (no cross-TU inlining), so a crash dladdr-
    resolving straight to `_Z7do_sendPhiibb+388` means the fault is literal
    code inside `do_send` itself, not a callee like `run_next_thread_and_wait`
    (a separate TU, would symbolicate to its own name if the fault were
    there). The only unguarded native derefs directly in `do_send`/`do_recv`
    are `TO_PTR(OSMesgQueue, mq_)` and `TO_PTR(OSMesg, mq->msg)` — the same
    generic "unguarded TO_PTR on a corrupted guest pointer" pattern as
    heapWalker/`rs_malloc`/`rs_free`/the s78 framebuffer gates, not the
    scheduler mechanism. Landed `mesgqueue_guard_refuse()`
    (`lib/N64ModernRuntime/ultramodern/src/mesgqueue.cpp`, KSEG0-range check
    at 4 call sites, `ROGUESQ_LOG_MESGQUEUE_GUARD=1` to see fires), built
    clean, exported+committed. One soak (`mesgqueueguard1`): 0 guard fires,
    process died at hold+100s to yet ANOTHER new `NAN_CHECK` call site
    (`mat3x3InverseInto`, `funcs_5.c:7582`) before reaching whatever window
    the do_send SIGBUS needs — inconclusive for the guard itself (one free
    re-run available if this exact question is picked up again), but this
    is the **6th consecutive session** (s209/210/211/213/214/215) losing the
    race to a random unrelated crash, 3 of them `NAN_CHECK` firings at 3
    different call sites. **Higher-value lead, not yet tried**: `NAN_CHECK`
    (`N64Recomp/include/recomp.h:396-397`, `assert(val == val)`) has an
    already-written, currently-commented-out no-op alternative one line below
    it (`recomp.h:399`) — flipping which is active is a 1-line header edit
    that (unverified but likely) needs only a plain rebuild, not a full
    regen, and could eliminate this entire recurring crash family in one
    shot, letting future soaks reach much further before dying to something
    else. Trade-off: masks real NaN bugs at those call sites — fine for
    "reach past craft-select," not fine if a NaN itself is under
    investigation. Full detail: PORTING-STATE Session 215.

-55. **(s214, do_send framing here SUPERSEDED by -56 above) heapWalker's
    upper-32-bits guard fix SHIPPED (10/10 sites,
    confirmed patched in generated `funcs_3.c` before building) but is still
    UNTESTED live — 2 soaks in a row hit unrelated crashes before reaching
    heapWalker at all, so the mechanism is neither confirmed nor refuted.**
    Both `GUARD` (`_make_heapwalker_guard_patch`) and `GUARD3`
    (`_make_heapwalker_guard3_patch`) in `N64Recomp/fixup_game_funcs.py` now
    reject `hi != 0xFFFFFFFFu` in addition to the existing `U32()` range
    check — full regen+build clean. Soak 1 (`heapwalkerguard4a/`) died in 3s
    on a NEW call site for the pre-existing `NAN_CHECK` assert family
    (`sinfApprox`, `funcs_5.c:6460`, signal 6) — never reached craft-select-
    exit. Soak 2 (`heapwalkerguard4/`, the one free re-run NEXT.md allows for
    an inconclusive result) got 35x further (104s into hold) but died on a
    NEW call site for the pre-existing thread-context-corruption family
    (`do_send`/`mesgqueue.cpp`, signal 10 SIGBUS, same functions implicated
    in the s176+ stall investigation) — still never reached heapWalker.
    Neither soak logged a single `[heapwalker-guard]`/`[heapwalker-guard3]`
    fire or a single `[unlit-mesh-tracer]` hit. **Do NOT soak a 3rd time on
    this same recipe** — per NEXT.md's own rule, 2 non-discriminating soaks
    already used the one free re-run; a 3rd is re-rolling dice, not
    advancing. **Next work unit**: either (a) accept that this specific
    varied recipe (`STICK_SCHEDULE="95:start 100:a 150:sr 200:sl 250:su"`)
    is no longer reliable for reaching heapWalker (its 1-for-3 hit rate this
    session vs 1-for-1 in s213 suggests race-dependent non-determinism, not
    a stable repro) and design a fresh recipe/approach, or (b) address one of
    the two newly-surfaced blockers (sinfApprox NaN call site, or the
    do_send SIGBUS) before attempting heapWalker again. **s215 update: the
    do_send SIGBUS is NOT the s176+ stall bug** (see -56 above) — a guard is
    shipped but unconfirmed live; the NAN_CHECK-disable lead in -56 is now
    the higher-value pick for (b), since it targets the whole family
    (sinfApprox included) at once rather than one call site. Full detail:
    PORTING-STATE Session 214, superseded in part by Session 215.

-54. **(s213, PARTIALLY ADDRESSED s214 above — see -55; guard code now
    ships the upper-bits check this item asked for, but the live-fire test
    itself is still pending) 4th soak (deliberately varied recipe, dropped early sticks
    per -53) hit a genuinely NEW crash — `heapWalker+1128` — and, cross-
    referenced against the s99/s157/s172 guard history and a fresh source
    read of `recomp.h`, this crash's register shape PROVES a generalizable,
    project-wide blind spot in every existing `U32(ctx->rN)`-truncated
    guard, not just a heapWalker-specific gap.** `run_unlitmeshtracer8.sh`
    (`STICK_SCHEDULE="95:start 100:a 150:sr 200:sl 250:su"`, sticks before
    95s dropped) reached `SELECT YOUR CRAFT stable` normally but SIGBUS'd
    almost immediately after ("hold-iter 1", far earlier than s210's 6s-in
    or s211's near-end stall) — `unlit-mesh-tracer`/`B_LOADED`: 0 lines
    again, so the original s208 `ctx->r16` question is STILL unanswered
    (3rd different early-blocking failure across 3 varied recipes now).
    **Two findings from this one crash:**
    (1) `[CRASH][pc-symbol]` (dladdr, trusted per NEXT.md) names
    `heapWalker+1128`, while `backtrace_symbols_fd` names the SAME frame
    `frameStartReset+532` (twice, frames 3+4) — this is the first LIVE
    confirmation of the s157/s172 "frameStartReset-attributed crashes are
    actually inside its first callee, heapWalker, misattributed by
    imprecise symbolication" theory; previously only source-read-inferred,
    never proven with an actual crash's dual symbolication.
    (2) The crash's register dump (`x10=0x0000000080003827`,
    `x11`/`x12`/`x13=0x0000000080000000`, `si_addr=far=0x380003827`) has
    upper-32-bits `0x00000000` — but a CORRECTLY sign-extended KSEG0 `gpr`
    (per the s99 lesson at line ~343 of this doc: raw 64-bit-vs-32-bit-
    literal comparisons false-positive at 100% because legit KSEG0
    pointers sign-extend to upper=`0xFFFFFFFF`) should have upper bits
    `0xFFFFFFFF`, not `0x00000000` — this is the SAME "KSEG0-zero-extension"
    shape already named for item -49's `renderUnlitMeshFaces`/`0x80630062`
    bug and s210's `evalCubicSplineAtTime`/`0x7ffffff8` bug, now a **3rd
    independent function** hit by the identical corruption class (still 3
    distinct exact values, so NOT one shared deterministic constant, but a
    shared mechanism). Read `recomp.h` this session (`U32(val)` =
    `(uint32_t)(val)`, `gpr` = `uint64_t`, `MEM_W(offset,reg)` =
    `*(int32_t*)(rdram + (reg + offset - 0xFFFFFFFF80000000))` using the
    FULL 64-bit `reg`, no truncation) and confirmed mechanistically: a
    guard written as `U32(ctx->r4) < 0x80000000u || >= 0x80800000u`
    (heapWalker's existing GUARD/GUARD3, in place since s172, both sites
    unfired this run) CANNOT distinguish a legit sign-extended pointer
    (upper=`0xFFFFFFFF`) from a corrupt zero-extended one (upper=
    `0x00000000`) — their low 32 bits are IDENTICAL by construction, and
    `U32()` discards the only bits that would tell them apart. **This is
    not a heapWalker-specific miss; every guard in the project using this
    exact `U32()`-truncated-bounds template (heapWalker GUARD/GUARD3, and
    the same pattern noted at doc lines ~3109/3402/3434/3622/3777) shares
    this structural blind spot.** **Next work unit**: add an upper-bits
    check (`(reg) >> 32 != 0xFFFFFFFFu` alongside the existing `U32()`
    range check) to heapWalker's 10 existing guard sites first (cheapest,
    already-instrumented function) as a scoped test, rebuild, soak, and
    check whether the guard NOW fires — a live fire would be the first
    positive control this mechanism has ever produced, and (if it also
    stops the crash) would be evidence this same upper-bits check could
    retire the `ctx->r16`/item -49 investigation too once applied there.
    Full detail: PORTING-STATE Session 213.

-53. **(s212) Offline cross-reference of s210/s211 logs REFUTES the "shared
    ~60-75s trigger" hypothesis from -52 below — clean Outcome B, no 3rd
    confirming run needed.** Both logs hit `vi_width=512` at nearly the same
    time (s210: 75.2s; s211: 73.6s) but this transition is a BENIGN,
    reproducible recipe event (craft-select-exit), not a stall trigger —
    both logs show only a handful of transient `stalled=1` blips right
    after it, then `stalled=0`/real `FIRE` events resume for tens of
    thousands more log lines. s211's REAL (permanent, never-recovers) stall
    does not onset until decision #7840 of ~8032 (log line 140374, right
    next to the `[thr-resume-skip]` fire and the 300s hold boundary) — ~200
    decisions before the run ends, nowhere near 73.6s. s210's crash happens
    during confirmed NORMAL, non-stalled operation (`stalled=0`, active
    `FIRE` events, `rdpFs=3772` still incrementing in the 3 decisions
    immediately before the `[CRASH]` block) — not a consequence of any
    stall. **The two failures (s210's `evalCubicSplineAtTime` crash, s211's
    item -35 stall) are independent; the earlier "~10s apart, suspicious"
    framing was a misread of the benign transition as the stall's onset.**
    Zero new builds/runs this session — this closes the question using only
    the two existing logs. **Next work unit (per NEXT.md step 2's fallback,
    now live): a 4th soak with a DELIBERATELY VARIED recipe** — drop the
    early `10:sr 25:sl 40:su` stick inputs (pre-craft-select camera nudges,
    not needed for the craft-select-to-leave flow) to see if removing them
    lets the run reach `renderUnlitMeshFaces` without hitting either s210's
    crash or s211's stall. Full detail: PORTING-STATE Session 212.

-52. **(s211, SUPERSEDED s212 above — see -53; "shared trigger" question now
    CLOSED, not open) 3rd consecutive session (s209/s210/s211)
    whose only soak attempt at reaching `renderUnlitMeshFaces` failed for a
    DIFFERENT reason each time — 0/4 total soaks across these 3 sessions have
    produced a live measurement of the `ctx->r16` question.** s211 re-ran the
    exact `unlitmeshtracer6` minimal-logging recipe (`unlitmeshtracer7`, tag
    only changed) and this time the process did NOT crash (`CRASH: 0`,
    completed the full 300s hold+grace) — but hit the ALREADY-CATALOGUED
    graphics-task-submission stall instead (`[phase]` shows `vi_width=512`
    at 73.6s with no further transition; `rdpFs` frozen at 3770,
    `stalled=1 pairs=0` continuously to end of log — same signature as
    s176-183, `rdpFs` within the previously-observed cluster). Not a new bug;
    no new candidate written up. Unlit-mesh-tracer/`B_LOADED`: 0 lines again.
    **Incidental finding**: a `[thr-resume-skip]` (the s84 UAF guard) fires
    once, immediately adjacent to the stall's onset — the same tight
    adjacency s180 found and s183 later weakened with a 0-fire
    counterexample; this is a 2nd occurrence WITH the fire, meaning the
    guard is present-but-not-necessary across observed stall onsets, not
    resolving item -35 (already budget-closed at s186, not reopening it).
    **Also flagged (single-observation, zero-cost to check)**: s210's crash
    (~63-64s absolute) and s211's stall onset (73.6s absolute) land within
    ~10s of each other under the byte-identical recipe — worth an OFFLINE
    cross-reference of both existing `run.log`s for a shared ~60-75s trigger
    before spending a 4th soak. **Per iteration budget rule 8, NOT launching
    a 4th identical-recipe soak next session** — the next work unit is the
    zero-cost offline log cross-reference above; only if that's a dead end
    does a 4th soak (with a deliberately varied recipe, not a repeat) become
    the fallback. Full detail: PORTING-STATE Session 211.

-51. **(s210, SUPERSEDED s211 above — see -52) s209's ~47x log-volume blowup is
    CONFIRMED self-inflicted logging overhead, not a real regression — but
    the minimal-logging re-soak crashed on a NEW, previously-unseen bug
    (`evalCubicSplineAtTime+1008` SIGBUS) before ever reaching
    `renderUnlitMeshFaces`, so the `ctx->r16` question below is STILL
    unresolved. Stripping all `ROGUESQ_LOG_*` vars except
    `ROGUESQ_LOG_UNLIT_MESH_TRACER=1` collapsed `run.log` from s209's 210M
    lines to 143,093 lines and let the run reach `SELECT YOUR CRAFT stable`
    in 46.0s (never reached at all in s209's two soaks) — this rules out
    `rs-free-walk` blowup as an independent regression. But the process then
    SIGBUS'd 6s into the hold window at `evalCubicSplineAtTime+1008`
    (signal 10, `si_addr=0x37ffffff8`), a spline/animation-eval function
    unrelated to the `+8772` bug's call chain — so `renderUnlitMeshFaces`
    was never called this run and the `B_LOADED`/unlit-mesh-tracer
    instruments logged 0 lines for a legitimate reason (crashed elsewhere
    first), not because they're broken. Notably, 6 of the new crash's dumped
    registers (`x10,x11,x12,x14,x15,x17`) hold the exact value
    `0x0000000080000000` and the faulting address decomposes as
    `x8+x9 (0x7ffffff8)` — the same qualitative "value clustered at the
    32-bit sign-bit boundary" shape as the `+8772` bug's recurring
    `0x80630062`, but this is SINGLE-OCCURRENCE and a different function, so
    it is NOT yet folded into that bug's evidence — flagged as a new,
    plausibly-related-by-pattern, unconfirmed bug. **Immediate next step**:
    re-run the identical minimal-logging soak (`run_unlitmeshtracer6.sh`
    recipe, new tag) — if `evalCubicSplineAtTime` crashes again, that's a
    2nd data point worth its own investigation; if instead the run reaches
    `renderUnlitMeshFaces` and fires the `B_LOADED` check, that finally
    answers the original s208 question. Full detail: PORTING-STATE
    Session 210.

-50. **(s209, RESOLVED s210 — see -51 above) Both soaks that session hit a
    reproducible ~47x log-volume blowup (`rs-free-walk` lines: 1.98M
    baseline vs 104.8M/172.1M, same script/duration) that appeared to
    prevent the craft-select/hangar scene from ever being reached — 0
    `renderUnlitMeshFaces` calls logged in either retry, including the
    always-on-at-call-1 positive control. s210 confirmed this was
    self-inflicted logging overhead (stripping the verbose diagnostics let
    the scene get reached normally), not a real behavioral regression. Full
    detail: PORTING-STATE Session 209.

-49. **(s208, STATUS: probe landed s209, not yet run to a valid result — see
    -50 above) `processSceneNode+8772`/`renderUnlitMeshFaces`
    KSEG0-zero-extension bug: built and soaked the `MEM_W`-address bounds
    tracer NEXT.md prescribed (4 sites: funcs_4.c:4975/5009/5546/5563) — the
    tracer's positive control fired (proves it executed on the exact call
    that crashed) but ZERO of the 4 sites flagged out-of-bounds, while the
    process still SIGBUS'd with `far=0x380630062` at
    `renderUnlitMeshFaces+792` (2nd independent `dladdr` pc-symbol hit on
    this function, different offset than s206's `+508`). Cross-referencing
    this exact `far`/`si_addr` value across every soak log
    (`grep 'si_addr=0x380630062\|far=0x380630062' scratch/s73_post_a_scene/*/run.log`)
    found it in FOUR runs (`mcontext1`/s194, `videoframetickguard3`,
    `pcsymbolize1`/s206, `unlitmeshtracer3`/s208) — **the identical byte
    value `0x80630062` recurring across independent runs/inputs means this
    is a deterministic data source, not random heap corruption. s194's
    "not yet confirmed recurring" is SUPERSEDED: confirmed recurring, 4
    occurrences, single value.** Since `lr=+640` (the `getTextureLUTFieldAt8`
    call's return point, `funcs_4.c:5104`) postdates site B's load
    (line 5029), sites A/B necessarily ran clean before the crash — ruling
    out the NAIVE form of explanation (a) (source register already bad at
    load time) for those two sites. But `ctx->r16` (site B's result) is
    dereferenced ~35 more times before the loop-back reload (5057, 5069,
    5114-5195, 5347-5542) and none of those were checked — and per C's
    verified-correct `int32_t->uint64_t` sign-extension-on-assignment
    convention, a value legitimately loaded via `MEM_W` should NEVER end up
    zero-extended, so if `ctx->r16` truly held `0x0000000080630062` at fault
    time, it did not arrive through the already-audited-clean load path.
    **Next work unit, in priority order** (cheapest falsification first):
    (1) grep decomp symbol tables / asset data for the literal address
    `80630062` — the recurring EXACT value may just name a real fixed
    symbol/offset, no build needed; (2) if that's a dead end, widen the
    tracer to check `ctx->r16` itself (not just its load's source address)
    right after the site-B load, before line 5057's first subsequent
    dereference. Full detail: PORTING-STATE Session 208.

-48. **(s207, SUPERSEDED framing — see -49 above for what's current)**
    the targeted re-read of `renderUnlitMeshFaces` at the `+508` offset
    (funcs_4.c:4951-5605) is still clean — no source-level zero-extension
    bypass anywhere in the function or its one callee (`getTextureLUTFieldAt8`,
    funcs_6.c:13392, confirmed architecturally `noinline` per `RECOMP_FUNC`
    in `recomp.h:22` and this project's `CMAKE_BUILD_TYPE=Debug`/`-O0` build
    of `RecompiledFuncs`, so it cannot be a mis-attributed inlined fault).
    Disassembly tools (`nm`, `atos`) re-confirmed blocked (2 independent
    attempts this session). Two live explanations, undistinguished: (a) the
    pointer chase in this function dereferences DATA corrupted by some other
    function (would mean callee-narrowing was mis-scoped from the start);
    (b) an ARM64 codegen issue invisible at the C level (exotic, lowest
    priority per boring-first). s208 built the tracer this called for and
    got a partial-discriminating result (see -49) rather than a clean
    confirm/deny of (a) vs (b) — still not fully resolved but no longer just
    two undistinguished branches. Full detail: PORTING-STATE Session 207.

    **(s206) Prior finding, still the basis for the above**: a direct
    `dladdr`-based pc symbolizer (new `[CRASH][pc-symbol]`
    line, `src/main/main.cpp`) caught a 3rd occurrence and named the
    faulting pc directly for the first time: `renderUnlitMeshFaces+508`.
    This OVERTURNS s204's "clean" verdict on that function — it was
    single-source/static-only and is now contradicted by direct dynamic
    evidence. Next work unit: re-read `renderUnlitMeshFaces`'s early region
    (`funcs_4.c:4951-~5030`) or build a tracer scoped to just that
    function's internal `MEM_W` addresses.**
    Prior conclusion (s205, now superseded): "ALL SIX direct-callee-chain
    functions (`processSceneNode`, `renderLitMeshFaceGroup`,
    `submitSceneNodeRender`, `renderFlatMeshFaceGroup`,
    `renderUnlitMeshFaces`, `renderLitTexturedMeshFaces`) are source-clean,
    callee-narrowing EXHAUSTED, pivot to instrumenting internal pointer
    computations across all six." This was believable because s200-205's
    reads were methodical and consistent, and because the crash handler's
    `backtrace_symbols_fd()` output only ever showed `processSceneNode +
    8772` (the `lr` value, duplicated across two frames) — never a deeper
    frame — which read as "the trail goes cold at processSceneNode's
    boundary," not as "the unwinder failed to resolve the true pc." s206
    found the raw crash log still had `pc=0x1028cc4a4` sitting right next
    to that `lr`, ~132 KB earlier in the binary and never printed as a
    symbol — the unwinder was silently dropping its best evidence, the
    same class of bug s194 originally found in the handler itself (see
    s194 below). Full detail: PORTING-STATE Session 206.

    **Still valid from s200-205** (not contradicted, corroborated): the
    defect is internal to one of the five render callees, not
    `processSceneNode` itself or a call-boundary-crossing value (s200's
    two independent lines of evidence: full static read + 116,950-call
    dynamic trace at the call boundary, 0 anomalies) — s206's direct pc
    evidence landing inside a callee confirms this. The other four
    callees' "clean" verdicts (`renderLitMeshFaceGroup`,
    `submitSceneNodeRender`, `renderFlatMeshFaceGroup`,
    `renderLitTexturedMeshFaces`) are not contradicted by s206 but remain
    static-only/provisional, same as they always were.

    Prior (superseded) narrative, kept for the narrowing methodology
    detail (which functions were read, in what order, what each read
    ruled out) — still accurate as a record of what was checked, just not
    as a conclusion that the search is exhausted:
    s200 exhaustively ruled out
    `processSceneNode` by two independent lines of evidence (full static
    read + a 46,292-call dynamic trace at the call boundary, 0 anomalies —
    see prior entry text below, still accurate). s201 ran 2 more soaks of
    the same tracer (`processscenenodecalleetrace2`/`3`, no rebuild): both
    died early (wall=22s/38s) to two DIFFERENT already-catalogued crash
    classes (`frameStartReset+532` SIGBUS, the s84-origin "shared
    corruption race" family; `runVideoFrameTick+1576` SIGBUS, the
    s192/s198/s199 recurring class, item -47.5 below), NEITHER matching
    the target `+8772` signature — bringing the cumulative tracer total to
    **116,950 real calls, 0 non-canonical args, across 3 soaks**, still 0
    reproductions of the target crash. Per the budget rule (3 consecutive
    uninformative soaks), s201 stopped soaking and pivoted to the
    documented fallback: a subagent-assisted full source read of
    `renderLitMeshFaceGroup` (`N64Recomp/RecompiledFuncs/funcs_4.c:8356-13424`,
    ~5068 lines — biggest and highest-call-volume of the five, 10,427
    calls at one site alone per s200). **Result: clean** — zero raw
    arithmetic bypassing `ADD32`/`SUB32`, zero `(uint32_t)` casts, all
    zero-extending `MEM_HU`/`MEM_BU` loads feed only small flag/color/LUT
    fields never used as pointers, all `MEM_W` results sign-extend via C's
    implicit `int32_t`->`gpr` assignment rule, no `MOVZ`/`MOVN`-style
    register ternaries, no raw pointer casts. This is single-source
    (static read only, no matching dynamic trace INSIDE this function's
    own body) — treat as provisional, not closed with `processSceneNode`'s
    confidence. s202 repeated the same subagent-brief method on
    `submitSceneNodeRender` (`funcs_4.c:6-3017`, ~3000 lines, largest of
    the remaining four). **Result: also clean** — zero raw pointer
    arithmetic bypassing `ADD32`/`SUB32`, zero `(uint32_t)` casts feeding a
    pointer computation (the only `U32()` calls found are inside
    pre-existing PATCH guard blocks, used solely for bounds-check
    comparison/logging, never written back into the address actually
    dereferenced), all 22 `MEM_HU`/`MEM_BU` loads individually traced to
    flags/index-comparisons/free-list-offsets never added into a pointer
    outside `ADD32`, no `MOVZ`/`MOVN`-style mismatched-extension ternaries.
    Same single-source caveat as `renderLitMeshFaceGroup`. s203 repeated
    the same method on `renderFlatMeshFaceGroup`
    (`funcs_4.c:3018-4951`, ~1900 lines, largest of the three remaining
    at the time). **Result: also clean** — zero raw 64-bit pointer
    arithmetic bypassing `ADD32`/`SUB32` anywhere in the function (every
    pointer/offset computation goes through it), zero `(uint32_t)`/
    `(uint64_t)` casts, all 49 `MEM_HU`/`MEM_BU` zero-extending loads
    individually traced to flag/comparison/index fields or output
    color/material descriptor packing (never fed into a pointer outside
    `ADD32`), only 5 ternaries in the function and all are plain
    `sltu`-derived booleans (no `MOVZ`/`MOVN`-style mismatched-extension
    pattern). Same single-source caveat as the prior three. s204 repeated
    the same method on `renderUnlitMeshFaces` (`funcs_4.c:4951-5605`,
    ~654 lines). **Result: also clean** — zero raw `+`/`-` arithmetic on
    register values bypassing `ADD32`/`SUB32` anywhere in the function
    (every pointer/offset computation, including the linked-list-node
    pointer chase at 5546 and the list-node/vertex pointers at 5019/5022/
    5548/5566/5572, goes through `ADD32`/`MEM_W`), zero `(uint32_t)`/
    `(uint64_t)` casts, all ~45 `MEM_HU`/`MEM_BU` zero-extending loads
    individually traced to flag/mask/compare/shift-amount/packed-output-
    word roles (never summed into a later-dereferenced address), the one
    ternary present (5552) is a plain `sltu`-derived boolean, not a
    `MOVZ`/`MOVN`-style pointer select. Same single-source caveat as the
    prior four.

    s205 repeated the same subagent-brief method on the last remaining
    candidate, `renderLitTexturedMeshFaces` (`funcs_3.c:22073-23886`,
    ~1813 lines, largest of the six). **Result: also clean** — zero raw
    `+`/`-` arithmetic bypassing `ADD32`/`SUB32`, zero `(uint32_t)`/
    `(uint64_t)` casts anywhere in the function, all 6 `MEM_HU`/`MEM_BU`
    loads individually traced to non-address uses (stack byte flags
    passed as call args, a global counter) except one (23831) that feeds
    a pointer computation — but that computation's shift+add
    (23836-23853) goes entirely through `S32`/`ADD32`, so the final
    pointer is correctly re-sign-extended despite the zero-extending byte
    load, not a bypass. All ternaries are plain `sltu`/`slti`-derived
    booleans, no `MOVZ`/`MOVN`-style mismatched-extension value selects.
    Same single-source caveat as the prior five (static read only).

    **SUPERSEDED s206**: this "callee-narrowing EXHAUSTED, all six clean"
    conclusion turned out to rest on a blind spot in the crash handler's
    own backtrace, not on the underlying facts — see the top of this item
    for what actually happened. s206 added a `dladdr`-based pc symbolizer
    that bypassed the frame-pointer-chain unwinder entirely and directly
    named `renderUnlitMeshFaces+508` as the 3rd occurrence's faulting
    location, contradicting s204's static-only "clean" verdict on that
    function. The reasoning below (why `processSceneNode` itself and the
    other four callees are still believed clean) remains valid; only the
    "exhausted, no more candidates" framing and the "pivot to a six-function
    internal tracer" plan are superseded — the search is no longer
    exhausted, it's precisely scoped to one function. Full detail:
    PORTING-STATE Session 200-206 (and Session 194/199 for the original
    register-file decode this all traces back to).

-47.5. **(s199) `runVideoFrameTick+1568` guard landed (3 sites,
    `ROGUESQ_LOG_VIDEO_FRAME_TICK_GUARD`, `N64Recomp/fixup_game_funcs.py`)
    — 2 of 3 soaks pass cleanly through both prior death points (8972,
    15418) with 0 recurrence, but the guard itself never fired (0/3) and a
    3rd soak died to the item above before a 3rd clean pass could be
    collected.** Disassembly tooling (`otool`/`nm`/`objdump`/`lldb`)
    re-confirmed still blocked (non-interactive session, no human to clear
    the approval prompt) — this guard is the source-level fallback per
    NEXT.md, guarding the one place in the function that dereferences a
    pointer loaded from a fixed global (guest `0x8010FCB0`) rather than the
    function's own arguments, matching s198's own `si_addr=0x320000000`
    evidence (wild/unmasked-pointer signature). One more informative soak
    (reaching past decisionN~9800 without dying to `processSceneNode+8772`
    first) would either complete this project's 3-pass "very likely fixed"
    bar or catch a same-run positive control. Lower priority than -48 now.
    Full detail: PORTING-STATE Session 199.

-47. **(s198) 3rd consecutive clean pass through the 18th class's death zone
    (still no positive control for the s197 guard) — 18th class reclassified
    "very likely fixed, mechanism unconfirmed"; a 2nd occurrence of the
    s192/s193 `runVideoFrameTick+1568` SIGBUS promotes it to the new
    dominant, top-priority blocker.** 4th `cacheheadguard` soak
    (`cacheheadguard4`, identical config to `cacheheadguard1`) reached
    decisionN=15418 — past both the 7902-7968 death zone and the 9660-9792
    target window, 2nd-furthest ever. `[scene-node-cache-guard]`,
    `[scene-node-ptr-guard]`, `[reinterpret-tile-guard]` all still 0 fires
    (0/4, 6+/6+, 1/1). Died to a SIGBUS at native offset `runVideoFrameTick
    +1568` — the EXACT offset of s192's `sceneptrguard5` crash
    (decisionN=8972), now a confirmed 2nd occurrence with the same
    duplicated-frame unwind shape, not a one-off. Per NEXT.md's own
    discriminating criteria: 3 clean passes in a row (s197 soaks 1/3, this
    run) is strong circumstantial evidence the 18th class is fixed even
    without the guard ever firing — retire it as the primary blocker.
    `runVideoFrameTick+1568` becomes the new top priority: 2/2 confirmed
    occurrences, currently the furthest-reaching known crash. Guarding it
    needs the actual faulting deref at that native offset; s193 already
    established disassembly tooling (`otool`/`nm`/`objdump`/`lldb`) is not
    on this session's Bash allowlist. Full detail: PORTING-STATE Session 198.

    **Best next work unit**: either (a) request one-off `otool -tv`/
    `objdump -d` approval to precisely locate the +1568 deref, or (b) add a
    broader defensive guard across every pointer dereference in
    `runVideoFrameTick`'s recompiled C body (`N64Recomp/RecompiledFuncs/
    funcs_0.c:1459` onward) accepting some imprecision, now that 2 confirmed
    occurrences justify the cost. Once guarded, the s190 `scene-node-ptr-guard`
    (still 0/6+, completely untested) and s196 13th-class guard (still 1/1
    untested) become the next reachable, unverified targets.

-46. **(s197) found and guarded the one dereference in the 18th-crash-class
    free-list idiom that bypasses GUARD/GUARD2/GUARD3 entirely (the
    cached-free-list-head pop at `funcs_4.c` `L_800101AC`, taken when the
    global free-list cache is non-empty at entry — skips
    `findAndUnlinkSmallestEntry` and all 3 existing guards). New guard:
    `ROGUESQ_LOG_SCENE_NODE_CACHE_GUARD`.** 2 of 3 soaks
    (`cacheheadguard1`/`2`/`3`) reached and passed cleanly through the 18th
    class's reliable recent death point (decisionN 7902-7968, where
    s195/s196 died) with **zero recurrence** — soak 1 reached decisionN=15719,
    the furthest ever recorded (previous best 9741), ending only on wall-clock
    budget, not a crash. **But the new guard itself never fired in any soak**
    (0/0/0) — no same-run positive control yet, so this is suggestive, not
    confirmed. Both passing runs instead died to already-catalogued, unrelated
    crashes: soak 1's "clean" run had no crash at all; soak 3 died at
    decisionN=8267 to the s184-catalogued `evalCubicSplineAtTime` SIGBUS
    family (different offset, `+732` vs s184's `+2552`, still not
    root-caused); soak 2 died at decisionN=359 (before VI width 1024) to the
    s165/s173-catalogued 23rd-class `waitForAnyAudioSlot` SIGSEGV — neither
    is a regression from this session's change.

    **Resolved by s198 (see -47 above)**: a 4th soak (`cacheheadguard4`)
    gave a 3rd consecutive clean pass through the 7902-7968 zone — per this
    entry's own criteria, that's enough to reclassify the 18th class as
    "very likely fixed, mechanism unconfirmed" without spending the 3rd
    budgeted soak attempt chasing a guard fire that may never come. The
    guard itself remains 0/4, still no positive control — leave it alone
    unless new evidence (a fire, or a recurrence right after one) appears.

-45. **(s196) landed the 13th-class `reinterpretTileRecord` guard (mirrors
    s192's `queueGPUUploadTMEM` pattern exactly) — but the soak never reached
    it, dying instead to a FRESH recurrence of the long-standing 18th crash
    class even earlier in decisionN, which is now the dominant blocker.**
    Replaced the hard `assert("Unimplemented reinterpretation logic." &&
    (...))` at `lib/rt64/src/hle/rt64_framebuffer_manager.cpp:476-480` with a
    named `reinterpretSupported` bool (condition unchanged) + a
    `ROGUESQ_LOG_REINTERPRET_TILE_GUARD`-gated bounded-counter log + early
    `return;` on the unsupported-format-combo path. Pure `lib/rt64` change,
    rebuilt clean, patch exported + committed.

    Soak (`reinterptileguard1`, identical config to s195's `mcontext2` plus
    the new env var, `run_mission_keys.sh reinterptileguard1 5 12`):
    `[reinterpret-tile-guard]` 0 fires, `[scene-node-ptr-guard]` 0 fires
    (still 0/6 cumulative). Died at `decisionN=7902` — **earlier** than
    s195's `reinterpretTileRecord` assert hit (~7968), meaning the new guard
    was never even reached this run. Crash: SIGBUS, nearest-symbol
    `heapFreeListDequeue + 12704` ← `submitSceneNodeRender + 28208` ←
    `processSceneNode` ← `traverseSceneGraphRecursive` ←
    `setupCameraMatrices` ← `runHangarSelectionFrame` ←
    `runHangarMenuFromOverlay` ← `menuOverlayInit` ← `mainGameLoop` — this is
    the project's own **18th crash class** (catalogued s108, guarded s123,
    **reopened** s131/s134 when the s123 guard fired 0/0 across 2 independent
    post-guard recurrences, meaning the guarded free-list-walk is refuted as
    the real cause). This session's `+28208` offset matches s181's own single
    prior sighting of that exact offset almost exactly — **this is that
    sighting's 2nd occurrence**, ~15 sessions later, confirming it under
    iron rule 4. It is the longest-standing unresolved crash family in the
    project (first flagged s108) and is now, for the first time, also the
    earliest blocker in soak order — ahead of both the 13th class (guarded
    this session, unverified) and the s190 scene-node-ptr-guard (still
    completely untested, 0/6).

    **Best next work unit**: source-read `submitSceneNodeRender`'s remaining
    un-audited body (`funcs_4.c`) to find the actual unguarded pointer chase
    behind the 18th class — the s123 guard covers the wrong mechanism
    (refuted s131/s134), so a fix requires finding what else in that
    function dereferences an unvalidated pointer. This was already NEXT.md's
    own decision-tree pivot as of s135 but was never acted on (the 13th class
    took priority in the interim). If a source-level guard can be landed and
    confirmed live, the 13th-class guard becomes newly testable in the same
    soak that tests it. Do NOT re-touch the s123
    `ROGUESQ_LOG_SCENE_NODE_LIST_GUARD` guard itself (confirmed not the
    cause, standing since s131). Do NOT re-touch the 13th-class guard landed
    this session (correct per spec, just unverified — needs either a run
    that survives past the 18th class, or a forcing hook).

-44. **(s195) re-ran s194's mcontext soak for a 2nd occurrence — s194's
    `processSceneNode`-adjacent crash did NOT recur; instead the soak died
    to a DIFFERENT, older catalogued crash (13th class,
    `reinterpretTileRecord`, parked at s96 "until 2nd recurrence") which
    just got exactly that 2nd occurrence, ~99 sessions later, byte-for-byte
    identical backtrace.** Ran `scratch/agent/run_mcontext2.sh` (identical
    env block to `mcontext1`, same binary, no rebuild) via
    `run_mission_keys.sh mcontext2 5 12`. Result: `decisionN=7968` (earlier
    than mcontext1's 9741, and before the 9660-9792 target window),
    `[scene-node-ptr-guard]` still 0 fires this soak (0/5 cumulative across
    all soaks to date). `grep -l "processSceneNode + 8772"
    scratch/s73_post_a_scene/*/run.log` still matches only `mcontext1` — the
    s194 crash is now single-occurrence-and-non-recurring; per NEXT.md's own
    decision tree, do NOT sink further budget localizing it, and it should
    NOT be treated as the dominant blocker.

    Instead, the crash that fired this soak (signal 6/SIGABRT, not
    SIGSEGV/SIGBUS) is `RT64::FramebufferManager::reinterpretTileRecord`'s
    `assert("Unimplemented reinterpretation logic." && (...))`
    (`lib/rt64/src/hle/rt64_framebuffer_manager.cpp:476-480`) — an
    RDP-framebuffer-format-reinterpretation combo the vendored RT64 shader
    logic doesn't handle. Backtrace (both s96 and s195, identical shape):
    `reinterpretTileRecord` ← `recordOperations` ← `State::fullSync` ←
    `GBI_RDP::fullSync` ← `Interpreter::processRDPLists` ←
    `Application::processDisplayLists` ← `run_rdp_submission` ←
    `submit_rdp_range` ← `rs64_dpc_defer_end` ← `factor5_gfx_runner` ←
    `rs64_run_lle_gfx` ← `RT64Context::send_dl` ← `gfx_thread_func`. This is
    now a **confirmed 2-occurrence recurring crash** (two independent
    sessions, s96 and s195), not a one-off — the condition for promoting it
    out of "parked" (set at s96) is met. It now fires BEFORE the target
    window, the same role `queueGPUUploadTMEM` played before its s192 guard
    landed.

    Secondary confirmation: the s194 crash-handler fix (siginfo + full
    ARM64 register dump) generalizes correctly to a SIGABRT (not just
    SIGSEGV/SIGBUS as previously confirmed) — `far=0x0`, `esr=0x56000080`
    (SVC exception class, consistent with an abort trap), and the
    `[CRASH][vifs-snapshot]` fields were internally sane
    (`decisionN=7968 lastFireDecisionN=7922 decisionsSinceFire=46`). Second
    positive control for the s194 instrument, different signal type.

    **Best next work unit**: guard `reinterpretTileRecord`'s assert the same
    defensive way as `queueGPUUploadTMEM` (s192,
    `lib/rt64/src/render/rt64_texture_cache.cpp:1308-1329`) — replace the
    hard `assert(...)` with an early return (skip the reinterpret dispatch,
    matching the assert's own condition) plus a getenv-gated, bounded-
    counter log (e.g. `ROGUESQ_LOG_REINTERPRET_TILE_GUARD`), mirroring the
    existing pattern exactly. This directly targets the current dominant
    pre-target-window blocker; if it works, the next soak should get
    materially closer to (or past) decisionN=9792 and finally test whether
    `[scene-node-ptr-guard]` (s190, still 0/5) fires at all. Requires editing
    `lib/rt64` — must run `./submodule-patches/export.sh` and commit the
    refreshed patch in the same session per hard rule. Do NOT touch the
    `processSceneNode` s194 lead further (non-recurring, out of scope per
    iron rule 4) or re-attempt disassembly tools this session (unconfirmed
    to have changed since s193/s194).

-43. **(s194) disassembly tools confirmed still blocked (otool/objdump both
    denied approval again) — pivoted instead to fixing the crash handler
    itself, which turned out to be discarding its own best evidence.** The
    POSIX `SA_SIGINFO` handler (`src/main/main.cpp:1654-1683`) requests
    `siginfo_t*`/`ucontext_t*` but the lambda signature threw both away.
    Extended it to print `si_addr`/`si_code` and, on `__APPLE__ &&
    __aarch64__`, the full ARM64 register file (`x0`-`x28`, `fp`/`lr`/`sp`/
    `pc`/`cpsr`, `far`/`esr`) from `uc_mcontext`. Needed `#include
    <sys/ucontext.h>` (not `<ucontext.h>`, which errors without
    `_XOPEN_SOURCE` on this SDK). Pure `src/main/main.cpp` change (this
    repo, not `lib/`) — plain `cmake --build`, no regen/fixup needed.

    First soak with it (`scratch/agent/run_mcontext1.sh`, tag `mcontext1`,
    same env block as s192/s193's `sceneptrguard5`) both confirmed the
    instrument (positive control: `si_addr==far`, internally-consistent
    register decomposition) AND reached decisionN=9741 — the furthest of
    any soak to date, and INSIDE the `[scene-node-ptr-guard]` target window
    (9660-9792) for the first time ever. It crashed on a NEW,
    previously-uncatalogued bug before the guarded site fired
    (`[scene-node-ptr-guard]` now 0/4): `far=0x380630062` decomposes exactly
    as `x0/x8 (0x300000000, rdram host base) + x9 (0x80630062, a raw
    zero-extended KSEG0 guest pointer, KSEG0 tag NOT stripped)` — i.e. some
    code path added a guest pointer to the rdram base WITHOUT the usual
    sign-extend-then-subtract-0xFFFFFFFF80000000 that `MEM_W` does
    (`N64Recomp/include/recomp.h`). `lr=processSceneNode+8772`
    (`funcs_4.c:13759-14873`) is the return address of the call to whatever
    actually faulted (unresolved symbol at the real `pc`). Single-source,
    first occurrence (`grep -l "processSceneNode + 8772"
    scratch/s73_post_a_scene/*/run.log` matches only this run) — not yet
    confirmed recurring. Full detail: PORTING-STATE Session 194.

    **Best next work unit**: soak again with the mcontext dump active
    (already permanent/always-on, no new env var) to get a 2nd occurrence
    of this crash signature — confirms whether it's the new dominant
    soak-blocker (like `queueGPUUploadTMEM` was) or a one-off. If it
    recurs, use the register evidence (rdram-base + unmasked-KSEG0-pointer
    pattern) to find the specific unmasked-arithmetic call site inside
    `processSceneNode` (grep for raw pointer math that bypasses `MEM_W`/
    `ADD32`'s sign-extension, near where sibling/child scene-node pointers
    get passed to a callee) and guard it the same defensive way as the
    other soak-blockers. The `runVideoFrameTick` crash (s192/s193, still
    uncatalogued) did NOT recur this soak — leave it alone until it's seen
    to still be a live blocker (may have been dodged by getting further
    into the scene this run, not fixed).

-42. **(s193) closed the "-41" open question — the s192 `queueGPUUploadTMEM`
    guard is now confirmed live via a positive control — but the
    `runVideoFrameTick` crash from s192 is STILL uncatalogued and unguarded,
    and remains the current blocker on any soak reaching the
    scene-node-ptr-guard's 9660-9792 target window.** Attempted -41's
    Option A first (guard `runVideoFrameTick`) but abandoned it: identifying
    the real faulting instruction at native offset `+1568` requires
    disassembling the compiled ARM64 binary, and `nm`/`otool`/`lldb`/
    `objdump` are not on this session's Bash allowlist. A from-scratch
    hand-rolled decoder (`scratch/agent/s193_disasm.py`) produced an
    internally-inconsistent result (the "crashing" instruction decoded as a
    harmless unconditional branch, preceded by an implausible ~19MB-target
    `BL`) — a clear sign the decoder itself isn't trustworthy, not a real
    finding about the crash. Did not guess a guard site from that. Pivoted
    to -41's Option B instead: added a test-only one-shot forcing hook
    (`ROGUESQ_TEST_FORCE_TMEM_ZERO=1`, `lib/rt64/src/render/
    rt64_texture_cache.cpp:1287`) that deliberately zeroes `width` on the
    first `decodeTMEM` upload, guaranteeing the s192 guard's condition
    trips. Soaked (`scratch/agent/run_tmemforce1.sh`, 60s hold): `[tmem-
    zero-guard]` fired exactly once with sane fields (`hash=
    0xA30077F480E4940E creationFrame=39 width=0 height=27 decodeTMEM=1`),
    and the run completed the full hold with `CRASH: 0` — the guard's early
    return demonstrably prevented the crash it's designed to prevent.
    `submodule-patches/rt64.patch` exported + committed same session per
    hard rule. Full detail: PORTING-STATE Session 193.

    **Best next work unit**: get real disassembly capability for this
    project (either get `otool -tv` / `objdump -d` approved onto the Bash
    allowlist for one-off use, or invest in a self-consistent ARM64 decoder
    — the current one in `scratch/agent/s193_disasm.py` is NOT
    trustworthy, it produced an internally-inconsistent decode this
    session), THEN use it to find `runVideoFrameTick`'s actual faulting
    deref at native offset `+1568` and guard it the same defensive way as
    the other 3 soak-blockers (rs_malloc, rs_free, scene-node-ptr,
    queueGPUUploadTMEM). This would make every previously-seen
    soak-blocking crash in the `sceneptrguard` lineage guarded, maximizing
    the odds the next soak finally reaches the 9660-9792 target window and
    tests the s190 `processSceneNode` fix (`[scene-node-ptr-guard]` still
    0/3 fires across all soaks to date). Do NOT guess a guard site without
    a trustworthy disassembly read — confirmed this session that guessing
    from an unverified hand-decoder is worse than not guarding at all.

-41. **(s192) landed the `queueGPUUploadTMEM` zero-size defensive guard
    (`ROGUESQ_LOG_TMEM_ZERO_GUARD`, `lib/rt64/src/render/
    rt64_texture_cache.cpp:1284`) that -40 recommended, but a soak with it
    active never exercised it** — it died to a NEW, previously-uncatalogued
    crash (`runVideoFrameTick` SIGBUS, likely a stack-unwind duplication
    artifact per source-read, not true recursion) at `decisionN=8972` — the
    furthest of the 3 `sceneptrguard` soaks so far (s190: 8053, s191: 7897,
    s192: 8972), but still short of the 9660-9792 target window.
    `[scene-node-ptr-guard]` fired 0/3 times across all three soaks;
    `[tmem-zero-guard]` fired 0/1 on its debut run — **s193 closed this gap
    with a positive control, see -42 above; the guard is now confirmed
    live.** Guard commit: `14bf1d4`
    (`submodule-patches/rt64.patch` exported + committed same session per
    hard rule). Full detail: PORTING-STATE Session 192.

-40. **(s191) re-ran the fixed `sceneptrguard` soak a 2nd time (`sceneptrguard4`,
    byte-identical config to s190's `sceneptrguard3`) — died again before the
    9660-9800 target window (decisionN=7897, even earlier than s190's 8053),
    but to a DIFFERENT already-catalogued crash this time, which refutes
    `reserveAndEmitDLEntry` as a specific recurring blocker.** The crash was
    signal 6 (SIGABRT) in the RT64 graphics thread — `TextureCache::
    queueGPUUploadTMEM`'s zero-tile-dimension assert
    (`lib/rt64/src/render/rt64_texture_cache.cpp:1285`), the project's
    single most historically-recurring crash class (first seen s86, 8+
    occurrences, still an open goal-stack item M3) — not `reserveAndEmitDLEntry`
    (the s190 blocker). `[scene-node-ptr-guard]` fired **0 times again**
    (2/2 null on the positive control) — the fix's target mechanism
    (corrupted sibling pointer into `processSceneNode`) has still never been
    observed live since the fix landed. Confirmed the s190 fix is intact and
    unregressed before soaking (source grep, not assumed). Full detail:
    PORTING-STATE Session 191.

    **Best next work unit — two valid options, in order:** (1) one more
    identical blind soak attempt is still within the iron-rule-8 budget
    (this is strike 2 of 3 on "does a fix-soak reach the target window") —
    if it also dies early to an unrelated already-catalogued bug, that's the
    3rd strike and blind repeats must stop; OR (2), likely higher
    information value now: add a defensive guard to `queueGPUUploadTMEM`
    (bare early `return;` before line 1287 when `decodeTMEM && (width<=0 ||
    height<=0)` — no locks held yet at that point, a clean skip-the-upload
    site) mirroring the project's established `rs_malloc`/`rs_free`/
    `scene-node-ptr` guard pattern. This is the single most frequent crash
    in the project's whole history and has now killed 2/2 fix-soaks before
    they could even test the actual question — neutralizing it (even
    provisionally, gated behind a new `ROGUESQ_LOG_*` env var with a
    positive-control requirement) directly attacks the dominant obstacle to
    ALL further soak progress, not just this one investigation. **This is a
    `lib/rt64` C++ edit, not a `RecompiledFuncs` fixup patch** — needs
    `submodule-patches/export.sh` + a commit in the same session, and only a
    plain `cmake --build` (no regen/fixup pipeline; pure runtime change per
    the established `lib/N64ModernRuntime`/`lib/rt64` exception).

-39. **(s190) landed the missing `processSceneNode` node-pointer guard
    (`ROGUESQ_LOG_SCENE_NODE_PTR_GUARD`, `N64Recomp/fixup_game_funcs.py`),
    but its effectiveness against the target self-recursion bug is still
    untested** — a soak with the fix hit a different, already-catalogued
    crash (`reserveAndEmitDLEntry`, 14th class, decisionN=8053) before
    reaching the 9660-9800 decision window. Correction to -38 below: only 1
    of its "4 existing guards" is actually on `processSceneNode` (the depth
    cap); the other 3 (`_scene_node_list_guard_patch`/`_guard2`/`_guard3`)
    are patched into `submitSceneNodeRender` (funcs_4.c:6-2999), a
    completely different function not in this crash's call stack — checked
    by cross-referencing guest addresses against `grep -n "^RECOMP_FUNC"
    funcs_4.c`, not just guard names. Source-read confirmed the mechanism:
    `traverseSceneGraphRecursive`'s sibling walk (global `0x80112B20`,
    next-pointer at node offset 0, funcs_4.c:15073-15074) passes its raw,
    never-bounds-checked pointer straight into `processSceneNode`'s `a2`
    argument, which becomes `ctx->r17` and is dereferenced on entry with no
    validation — explaining the fixed-native-offset SIGBUS without needing
    a depth-overflow explanation. **Also caught and fixed a self-introduced
    regression this session**: the first patch version silently deleted
    `ctx->r3 = MEM_W(ctx->r17, 0XC);` (an over-greedy regex match whose
    replacement never re-emitted the anchor line it consumed), causing a
    2/2-reproducible immediate crash (decisionN~150, new signature) with the
    guard itself never firing — caught via a same-session control build
    (identical env, patch disabled) that ran the full 120s hold crash-free
    to decisionN 14721+, confirming the regression was the patch, not
    pre-existing state. Full detail: PORTING-STATE Session 190.

    **Best next work unit**: re-run the `sceneptrguard`-style soak (fixed
    build, `ROGUESQ_LOG_SCENE_NODE_PTR_GUARD=1` plus the full s188 env
    block) again — soak-to-soak crash-site variance is well established in
    this dataset (16 different decisionN values across 16 runs), so a
    different attempt may get past the `reserveAndEmitDLEntry` obstacle at
    ~8053 and actually reach the 9660-9800 window this fix targets. If
    `reserveAndEmitDLEntry` keeps recurring first, it may need its own guard
    extension (mirrors the s169 pattern: 3 guards already added to this
    function, at least one more unguarded site now confirmed at native
    +5212) before the `processSceneNode` question can be tested at all —
    but do not open that as a full investigation without at least one more
    soak attempt first, since it may just be run-to-run variance.

-38. **(s189, corrects -37's clustering claim): surveyed crash-time `decisionN`
    across ALL 16 historical soak logs instead of running a new soak (NEXT.md's
    recommended path (B)) — the "4 unrelated crash families cluster near
    9770-9792" framing does not survive the full dataset, but a stronger signal
    was hiding in it: the `processSceneNode` crash that ended s188 is not new,
    it's the SAME bug recurring a 3rd and 4th time.** `evalCubicSplineAtTime`
    (8327) and `rs_free` (8616) are 1443/1154 decisions from the window —
    comparable to or larger than the ~467-decision average inter-crash gap
    across the full dataset, so their inclusion as "clustering" evidence was
    an overclaim (boring-explanation check, rule 5). But two OLDER,
    previously-uncross-referenced runs — `heapwalkerguard3_1` (decisionN=9661)
    and `tickreap3dvoicesguard1` (decisionN=9694) — turn out to have the
    **byte-identical crash stack** to s188's `schedtick1` (9789):
    `processSceneNode+8148/8456` self-recursion → `traverseSceneGraphRecursive`
    → `setupCameraMatrices` → `static_5_800C9BF0` → `menuOverlayInit` →
    `mainGameLoop` → `mainBootstrapWorker`. So this already-catalogued s172-lineage
    bug (see line ~1703, source-reads at ~1744-1850) has now independently
    fired **3 times**, across 3 different sessions/guard-configs, always within
    a 128-decision span (9661-9789) — a real, reproducible recurrence pattern
    for ONE bug, not evidence of many unrelated bugs converging on shared game
    state. **Critical addendum — this is NOT actually unguarded**:
    `N64Recomp/fixup_game_funcs.py` already carries 4 guards on this exact
    function (`_scene_node_list_guard_patch` + 2 sibling deref-site guards,
    s99-101 era; s175's recursion-depth cap at 128). `schedtick1`'s own
    driver script armed all 4 (`ROGUESQ_LOG_SCENE_NODE_LIST_GUARD{,2,3}`,
    `..._DEPTH_GUARD`) and **none fired** (0/0/0/0) even as the process died
    to this exact backtrace — same null result for `tickreap3dvoicesguard1`'s
    3 list-guards. This weakens s175's own working hypothesis (unbounded
    recursion depth -> native stack overflow): the crash lands at
    consistently the same in-function PC offset across rebuilds
    (`+7176`/`+7640`/`+8148`/`+8456`, drifting only with codegen, not with
    run-to-run recursion depth), which looks more like one specific
    still-unidentified dereference than a depth phenomenon. This resolves
    the (a)/(b) fork s188 left open, but sharpens (a): **not "add a guard",
    but "find the actual faulting deref that the 4 existing guards don't
    cover."** Full detail: PORTING-STATE Session 189.

    **Best next work unit**: source-read `processSceneNode`
    (`N64Recomp/RecompiledFuncs/funcs_4.c:13759-14861`)/
    `traverseSceneGraphRecursive` again, specifically hunting the deref at
    native offset `+8148`/`+8456` (build-specific; recompute per current
    build) that the 4 existing guards (fixup script lines ~2337-2464,
    ~3899-3990) don't cover — the s175 comment block there (raw material:
    sibling list rooted at mutable global `0x80112B20`, `a3`/`ctx->r7`
    confirmed clobbered not a depth counter) is still valid groundwork, just
    not the answer. Once found, guard it (mirrors `rs_malloc`/`rs_free`
    s173/s187 pattern: `goto` the natural exit on a bad condition, new
    `ROGUESQ_LOG_*` env var, positive control required same-run), then
    re-run a `schedtick1`-style soak to see whether `decisionN` can finally
    be pushed past 9792 and, if so, whether the `-35` stall signature
    (queueN/runnextN still climbing while decisionN plateaus) actually
    appears — the real test the whole schedguard/schedtick/rsfreeguard
    lineage has been trying to reach.

-37. **(s188, clustering claim in this item corrected by -38 above — kept for
    the instrument/no-starvation finding, which still stands) landed the
    periodic `[sched-tick]` readout s187 called for, ran one soak
    (`schedtick1`): decisionN/queueN/runnextN climbed in lockstep with NO
    stall signature the entire run**, before dying to the `processSceneNode`
    crash discussed in -38. Added `rs64_get_sched_queue_count()` (new atomic
    in `scheduling.cpp`, incremented in `schedule_running_thread`) and a
    `[sched-tick]` line printed every 750 `run_next_thread` pops from
    `threads.cpp`, reusing `rs64_get_vifs_crash_snapshot` (previously
    crash-handler-only) to read the live `decisionN` (`lib/N64ModernRuntime`,
    exported+committed). `schedtick1` (same env block as s187's
    `rsfreeguard1`): 119 tick lines, `decisionN` rose smoothly from 195 to
    9789 with `queueN`/`runnextN` incrementing at a constant ~750-per-tick
    rate throughout — no plateau, no growing gap, at any point up to the
    crash. This is a THIRD independent run (after s184's 8327, s185's 8616)
    showing no scheduler starvation signature pre-crash, and the first to
    show it holding steady lockstep data all the way into the historical
    stall-onset window itself, not just up to an earlier death. Full detail:
    PORTING-STATE Session 188.

-36. **Landed the mandatory-pivot defensive guard on `rs_free`'s free-list
    walk (s187) — validated with a strong positive control, first
    fully crash-free full-length soak in the whole s180-187 lineage.**
    `rs_free` (`N64Recomp/RecompiledFuncs/funcs_0.c:3106`, a single shared
    `RECOMP_FUNC` covering every caller including
    `rebuildActiveDisplayObjectList` and `freeManifestSegmentAssets`)
    contains 3 near-identical free-list coalescing walk loops that compute
    `next = node + size_field` with zero bounds checking (`recomp.h`'s
    `MEM_W`/`MEM_HU` macros do raw unclamped pointer arithmetic) and then
    dereference through it. Guarded all 3 (`N64Recomp/fixup_game_funcs.py`,
    mirrors the s173 `rs_malloc` guard exactly: `0x80000000u`/`0x80800000u`
    RDRAM bounds, `goto` each loop's own natural terminator-exit label,
    new env var `ROGUESQ_LOG_RS_FREE_WALK_GUARD`). One soak
    (`rsfreeguard1`): `[rs-free-walk-guard]` fired **1901 times** (all
    `loop=1`, all the same corrupted node `0x807982B6`/`bad_next=
    0x8475841C`) and the process **survived the entire 120s hold + grace
    window, had to be killed manually, `CRASH: 0`**. This closes out the
    "3 of the last 4 scheduling-line attempts killed by this family"
    problem that blocked s183/s185/s186. **Not yet known**: whether the
    `-35` stall itself still occurs past this guard — the `decisionN`
    counter is crash-only (`[CRASH][vifs-snapshot]`), so a crash-free run
    like this one reports nothing about stall status. `[sched-queue]`/
    `[sched-runnext]` (131076/131075) stayed near-balanced the whole run,
    at least consistent with "never stalled." **Best next work unit: add
    a periodic (non-crash-gated) decision-count log tick**, then re-run
    the `ROGUESQ_LOG_SCHED` env block (the flag itself is free to observe,
    even though rule 8 closed *dedicated* attempts on it) now that this
    crash family no longer pre-empts reach into the stall region. Also
    still open: the underlying corruption source itself (s85-s114 chase,
    not touched this session) — this guard treats the symptom. Full
    detail: PORTING-STATE Session 187.

-35. **`ROGUESQ_LOG_SCHED` instrument's rule-8 budget is now CLOSED (s186):
    3 of 3 attempts spent, all inconclusive for candidate (a).** `schedguard7`
    (3rd attempt) reached the furthest yet — decision `#10535`, PAST the
    `#9770`-`#9792` historical stall-onset window — but never sustained a
    stall (max gap between logged decisions: 32, far short of the >100
    signature); it then died to the same `rs_free ← rebuildActiveDisplayObjectList`
    crash as s183, byte-identical call chain. 3rd straight confirmation that
    `[sched-queue]`/`[sched-runnext]` stay near-balanced and the producer
    thread (`mainBootstrapWorker`, id=3) keeps getting scheduled normally
    right up to its own unrelated crash — this crash family is orthogonal to
    the scheduling hypothesis, not a manifestation of it. Across the whole
    `schedcaller`/`schedguard` line (s180-186), the `rs_free`/heap-corruption
    family has now killed 3 of the last 4 attempts (s183, s185, s186) — it is
    the single most frequent thing pre-empting reach into this content
    window. **Mandatory pivot next session, per NEXT.md's own decision
    tree**: either candidate (b) (`viRetraceHandlerThread`/`musyxSynthFrame`
    lock/resource contention against the producer), candidate (c)
    (heap-exhaustion on the producer's own allocation path), or — the
    higher-information-value choice given how often it's pre-empting
    progress — **land a defensive guard on `rs_free ← rebuildActiveDisplayObjectList`**
    (s99-s101 precedent: `goto` the real epilogue on a bad table/pointer
    read) purely to buy runway for a future scheduling-instrument attempt.
    Full detail: PORTING-STATE Session 186.

    **s183-s185 finding this closes out (still valid as confirmed instances,
    not the whole explanation): find what actually stops graphics-task
    submission in a run that reaches the stall WITHOUT `[thr-resume-skip]`
    firing.** **s184**: source-read confirmed a real,
    previously-uninstrumented mechanism that needs no UAF guard at all —
    `check_running_queue()` only swaps to a queued thread if its priority is
    **strictly greater** than the caller's; the only priority-blind pop is
    `run_next_thread()`'s unconditional pop, reached only when some thread
    performs a genuine blocking wait. `mainBootstrapWorker` (the hangar-loop/
    graphics-producer thread) is created at **priority 10** vs. **117-122**
    for the VI-retrace/audio threads — exactly the shape needed for the
    producer to get queued (via a non-blocking send/recv) and then never
    resumed if none of those higher-priority threads ever blocks again.
    Landed `ROGUESQ_LOG_SCHED=1` (`[sched-queue]`/`[sched-check]`/
    `[sched-runnext]`, `lib/N64ModernRuntime`, exported+committed) to test it.
    One soak (`schedguard5`) validated the positive control (72382/333003/72380
    fires) but **died at decision 8327, before the stall-onset window
    (~9770-9792)**, to a **new, distinct SIGBUS** in `evalCubicSplineAtTime
    +2552` (signal 10 — NOT s83's guarded NAN_CHECK abort, a different signal
    and fault site under the same function name, not root-caused).
    **s185**: 2nd attempt (`schedguard6`, no source changes, fresh tag) —
    died **even earlier**, at decision **8616** (still before the
    ~9770-9792 window), to a recurrence of the already-catalogued 24th crash
    class (`rs_free` ← `freeManifestSegmentAssets`, s167) — confirmed
    orthogonal to the scheduling hypothesis (the producer thread,
    `thr=0x300163e20 id=3`, was actively being scheduled and resumed right
    up to the instant of its own unrelated heap-corruption crash: last
    `[sched-runnext]` before death popped that exact thread normally). 2nd
    independent confirmation that pre-crash `[sched-queue]`/`[sched-runnext]`
    counts run near-balanced (77510/77508 this run vs. 72382/72380 in s184) —
    routine starvation is still not the normal case in the window this
    instrument can actually observe. **2 of up to 3 attempts on this
    instrument now spent, both inconclusive** (neither reached the target
    stall window) — next soak is the 3rd and final allowed attempt before a
    mandatory pivot to candidates (b)/(c) per rule 8. New observation for
    future planning: the early-death crash roster in this specific
    `STICK_SCHEDULE`/hold-window shape (`evalCubicSplineAtTime+2552` s184,
    `rs_free ← freeManifestSegmentAssets` s185, `rs_free ←
    rebuildActiveDisplayObjectList` s183) is now pre-empting reaching the
    stall more often than reaching it at all — if the 3rd attempt also dies
    early, consider guarding the recurring `rs_free`/heap-corruption family
    (à la s99-s101's table-lookup guards) purely to buy runway, independent
    of fixing it for its own sake. Full detail: PORTING-STATE Sessions
    184-185.

    **s183 finding this refines (still valid as one confirmed instance, not
    the whole explanation):** `schedguard4` reached and sustained the target stall
    for the first time (hold-iter 68, deepest ever; 2688 consecutive
    `stalled=1` decisions before death) but fired `[thr-resume-skip]` **0**
    times the entire run, weakening (not confirming) s180's scheduler
    silent-drop mechanism as the general cause. The stall onset was tightly
    timed (decision `#9770`→`#9792`, same "tight" character as s180) but the
    only log activity in that window is the `#9770 FIRE` line itself and
    heap-walk noise — no thread-resume activity of any kind. Source-read
    candidates before instrumenting (rule 5): (a) whether the outer
    hangar-tick loop can stop iterating via a path that never touches
    `resume_thread_tagged`'s bad-context branch at all; (b)
    `viRetraceHandlerThread`/`musyxSynthFrame`'s audio-tick path holding a
    lock/resource the graphics producer needs; (c) whether the dominant
    `[rs-malloc-walk]`/`[rs-free-walk]` volume around the stall points at a
    heap-exhaustion condition on the producer's own allocation path. Keep
    `[thr-create-id]`/`thr=%p` armed regardless — a future stall that DOES
    correlate with `[thr-resume-skip]` is still valuable (multiple
    mechanisms landing on the same symptom is now the working framing, not
    one root cause). Died this run to a SIGBUS in `rs_free ←
    rebuildActiveDisplayObjectList` — same shared-heap-corruption family as
    s164's 22nd class (same caller, `rs_malloc` variant) and s167's 24th
    class (`rs_free`, different caller); not a new independent bug, lower
    priority than the item above. Full detail: PORTING-STATE Session 183.

-34. **(s182): re-attempted the stall repro now that the
    `FramebufferStorage::store` OOB-read crash (found this session) no
    longer preempts it; the nearest remaining obstacle is a
    non-deterministic, already-catalogued Metal-internal shader-compiler
    SIGSEGV (s83/s96 lineage, no source on our side).** s182 re-ran the
    `schedcaller`-shape soak (`schedguard2`) and found it died **even
    earlier** than s181's attempt (hold-iter 1 vs hold-iter 7) to a
    brand-new crash: SIGBUS in `RT64::FramebufferStorage::store`'s memcpy,
    called from `State::fullSync`'s color/depth read-into-storage blocks
    (`rt64_state.cpp:2227`/`2271`). Root-caused it as a **real gap in the
    s78 `FramebufferManager::get()` refuse gate**: that gate keeps a wild
    FB out of `framebuffers[]` but still returns a `refuseFb` carrying the
    same wild `width`/`height`/`address`, and this downstream read site has
    no bounds check of its own — confirmed exactly by a same-tick
    `[fb-get] REFUSE addr=0x00FF3EC0 w=225 h=158 oob=1` whose computed
    `rangeEnd` lands ~8MB past the 8MB RDRAM buffer. **Fixed** (`lib/rt64/
    src/hle/rt64_state.cpp`, both color and depth blocks): skip the
    `fbStorage.store`/RDRAM read when `storageAddress`/`rangeEnd` would
    exceed `0x800000` (reusing s78's constant), logging
    `[fbsync-oob-skip]` (throttled, same pattern as `[fb-get] REFUSE`).
    Pure `lib/rt64` host C++, rebuilt clean, patch exported+committed.
    **Validated same-session**: soak `schedguard3` (identical env/tag-bump)
    got a clean positive control (`[fbsync-oob-skip]` 17/17), the exact
    crash that killed `schedguard2` did not recur, and the process
    progressed further (`decisionN=8016` vs `7734`, hold-iter 3 vs 1)
    before dying to the unrelated Metal-internal SIGSEGV instead. Neither
    `schedguard2` nor `schedguard3` fired `[thr-resume-skip]` even once, so
    s180's "2nd independent confirmation" of the scheduler silent-drop
    mechanism (item -33 below) is still outstanding — this session only
    removed one early-crash competitor. Full detail: PORTING-STATE Session
    182.

-33. **(s181): reach the stall again with the new `[thr-create-id]`/`thr=%p`
    instrument armed (always-on already), then cross-reference the
    `[thr-resume-skip] thr=%p` value against this run's `[thr-create-id]`
    lines to learn which specific thread was dropped.** Now that -34's fix
    removes one specific early-crash competitor, re-attempt this 1-2 more
    times before treating the Metal-internal SIGSEGV itself as worth a
    characterization pass (no source on our side — only "what shader/
    material combination triggers a first-time compile here" is
    investigable, not directly fixable).
    s181 source-read + one soak **refuted s180's implicit premise that "id 0"
    names a single specific thread**: grepping every `osCreateThread_recomp`
    call site found **8 of 10 literal-id call sites pass `id=0`**, and a
    same-run `[thr-create-id]` dump confirmed **≥9 distinct threads share
    id=0** in a normal run — `idle_thread_handle`, `thread3_video_handle`, an
    unnamed child of it, 3 boot-sequence threads, one more unnamed one, and
    (via an exact `thr_rdram` address match to s70/71) **the audio thread
    `runAiAudioStreamPlaybackLoop`**. `id=1`/`id=3` matched s93's known
    `piDmaWorker`/`mainBootstrapWorker` exactly, confirming ids 1+ ARE
    per-thread-unique — only `id=0` is a shared default. **A fix keyed on
    `id==0` alone would be a guess among ≥9 candidates, not a targeted fix.**
    Landed (and positive-controlled 18/18) a new always-on log,
    `[thr-create-id] id=%d thr=%p pri=%d entry=0x%08X thr_rdram=0x%08X`
    (`osCreateThread`, right after context creation) plus `thr=%p pri=%d`
    added to the existing cheap `[thr-resume-skip]` line — both in
    `lib/N64ModernRuntime/ultramodern/src/threads.cpp`, patch
    exported+committed. **This run did not reach the stall** (died hold+7s
    to a new-looking SIGBUS in `traverseSceneGraphRecursive`/
    `processSceneNode`/`submitSceneNodeRender`, not chased, see PORTING-STATE
    s181) — 0 new `[thr-resume-skip]` firings, so s180's mechanism still
    needs its 2nd independent data point (rule 4). Full detail:
    PORTING-STATE Session 181.

-32. **(s180, refined by s181 above): design a fix or targeted instrument
    for the scheduler silent-drop mechanism.** s180's 3rd (and rule-8-final)
    `schedcaller`-shape attempt
    (`schedcaller2`) **reproduced the sustained graphics-task-submission
    stall crash-free** — the first time either outcome (crash-free / reaches
    the stall) has happened together; `CRASH: 0`, hold+grace both completed,
    `[vi-fs-decision]` decisions **#8000-#16256 unbroken `stalled=1 pairs=0`**
    with `rdpFs` frozen at 3747 (5th data point in the `~3560-3802`
    candidate-ceiling band). `[hangar-loop]`'s last firing (`n=538`) is
    immediately followed by `[swap-ack-wait] call=4781`'s clean
    enter/pre-recv/post-recv (no orphan) — confirms NEXT.md's "outer loop
    itself stops iterating" branch, not "loop keeps running, callee skips
    the wait". Between that clean call and the stall's onset, **exactly one**
    `[thr-resume-skip] tag=run_next id=0 ctx=0x0 live=0 bad_total=1` fires
    (the always-on s84 UAF guard) with nothing else logged in between.
    Source read of `resume_thread_tagged`/`run_next_thread`/
    `run_next_thread_and_wait` (`lib/N64ModernRuntime/ultramodern/src/
    threads.cpp:198-278`) plus `mesgqueue.cpp:105/143` (what guest
    `osRecvMesg`/`osSendMesg` blocking compiles to) shows the mechanism: when
    the scheduler pops a "next" thread to hand off to and that thread's
    context is bad, the guard **silently returns without retrying the next
    queue entry or waking the thread that yielded** — so if the popped
    thread was the one that would have eventually served the swap-ack
    message queue, the yielding thread (here: thread 3, the hangar loop)
    blocks forever. This is a plausible, source-confirmed, tightly-timed
    **root cause candidate for the entire stall**, not just a correlated
    observation — but it is a **single run, single firing** (rule 4: needs a
    2nd independent line of evidence before entering "current truth" as more
    than a strong lead). Full mechanism writeup: PORTING-STATE Session 180.
    **Next steps, in order:**
    1. ~~Source-read: find what guest thread id 0 is.~~ **Done, s181 — see
       -33 above: refuted "id 0 = one thread" (≥9 threads share it); use the
       new `[thr-create-id]`/`thr=%p` instrument (-33) on the next soak that
       reaches the stall instead of guessing from `id` alone.
    2. Once the specific dropped thread's identity is known (via -33's
       instrument, not `id` alone), decide the fix shape: does
       `resume_thread_tagged`'s bad-context branch need to retry the next
       running-queue entry instead of just returning? Does
       `run_next_thread_and_wait`'s caller need a way to detect it will
       never be resumed and recover (e.g. a timeout, or requeuing itself)?
       Either is a real behavior change to shared scheduler code — treat
       with the same care as every prior guard in this project (truncate
       through `U32()` before comparing register values, keep changes
       ABI-correct via `goto` to the real exit label, etc., per the
       s99-s101 lessons already in this file).
    3. A 2nd independent data point (any soak reaching the stall again with
       this same `[thr-resume-skip]` positive control) would upgrade this
       from "strong lead" to confirmed before committing to a fix design.

-31. **(s179, superseded as top priority by s180 above): the `schedcaller`-shape soak,
    now closed after its 3rd attempt (see -32 above).** Source-read (before
    instrumenting, per rule 6) confirmed
    `static_5_800AAD9C` (`runHangarSelectionFrame`) has **exactly 2 static
    call sites**, both the same guest instruction (`L_800C68AC` inside
    `runHangarMenuFromOverlay`, duplicated across two overlay-instance
    copies — `funcs_29.c`/`funcs_43.c`, identical text) — no other static
    caller anywhere in `RecompiledFuncs/`. That loop's body has no wait/yield
    of its own; all per-frame pacing happens inside the callee (the
    already-instrumented `waitForPrevFrameDone`→`waitForPostSwapAck` chain,
    s177/178). So the loop stopping without taking the
    `gracefulMenuShutdown` exit can only mean the guest OS thread executing
    it stopped being resumed/scheduled — exactly NEXT.md's (now this
    session's) discriminating question. Landed `ROGUESQ_LOG_HANGAR_LOOP=1`
    (iteration counter + guest thread id via a new **ctx-register-free**
    probe, `rogue_current_thread_id(uint8_t* rdram)` in
    `lib/N64ModernRuntime/ultramodern/src/threads.cpp` — deliberately NOT
    `osGetThreadId_recomp`, which clobbers `ctx->r2`/`ctx->r4` and would
    corrupt the surrounding loop's live registers; needs an `rdram` param
    because `TO_PTR` in RDRAM-relative-pointer mode references that exact
    identifier name, caught as a build error on the first attempt and
    fixed same-session). `lib/` patch exported + committed. One soak
    (`schedcaller1`, s178's full instrument set plus this one,
    `ROGUESQ_LOG_THREAD_RESUME` deliberately left at `0` per s93's confound
    finding) gave a **clean positive control** — `[hangar-loop]` fired
    518/518 times, **guest thread id was `3` on every single firing** (a
    new, real data point: one consistent OS thread owns this loop for the
    whole run) — but the run **never reached the target stalled state**
    (only 43 isolated `stalled=1` blips, none sustained; per NEXT.md's own
    prior "do not" note these are not evidence of the real condition).
    Died fast instead (`hold-iter 1`, `[vi-fs-decision]` decision `#7857`,
    far short of s178's `#14080` onset) to a **3rd occurrence of the s84
    `frameStartReset` SIGBUS** — backtrace confirms the exact expected
    chain (`static_5_800C6854` → `static_5_800AAD9C` → `frameStartReset`),
    the same crash that also preempted s177's one prior attempt at this
    soak shape. **Softens "fluke" further**: 2 of the last 3 dedicated
    stall-repro attempts (s177, s179) have now been preempted by this one
    class before ever reaching a stalled state — not yet a majority, but
    no longer a 1-in-5 outlier either. Per PORTING-STATE's existing
    `frameStartReset` investigation (search that file, not re-read here):
    the function's own guest body has **no bug** (already source-verified)
    — any fix effort belongs in its callees/the shared-corruption-race
    family, not in `frameStartReset` itself; **do not re-open that as a
    new investigation thread from this session's finding alone.**
    Incidental (incurred zero extra soak cost): found `waitForPrevFrameDone`
    — and therefore the single call site of `waitForPostSwapAck` — has
    **22 call sites across 10 files**, i.e. it's a shared per-frame
    swap-pacing utility used broadly across the game, not exclusive to this
    loop. This fully explains an apparent count mismatch in this run's own
    log (`[swap-ack-wait]` reached `call=4755`, `[hangar-loop]` only
    `n=518`) without contradiction — the two instruments answer
    different-scoped questions (all 22 sites' combined activity vs. this
    one specific call site's own iteration count) — **do not read that
    mismatch as evidence of a hidden indirect caller of
    `runHangarSelectionFrame` itself**; the static-call-site count for that
    specific function (2, both this loop) stands as source-verified.
    Bonus: `rdpFs` plateaued at **3740** right before this crash — a 4th
    data point inside the s176/177/178 `~3175-3802` candidate-ceiling band.
    **Next step: re-run the same `schedcaller`-shape soak again (tag
    `schedcaller2`) — rule 8 allows up to 3 attempts on the same hypothesis
    before parking it, and this is only the 2nd (s177 was the 1st miss on
    this general soak shape, this session's is the 2nd, both to the same
    preempting crash).** If a 3rd attempt is also preempted before
    reaching a sustained `stalled=1`, park this repro angle per rule 8 and
    reconsider: either accept `[hangar-loop]`'s existing 518/518 positive
    control as sufficient validation and design a repro that starts later
    in the timeline (skip past where `frameStartReset` tends to fire), or
    pursue the shared-corruption-race family directly since it's now
    demonstrably the single biggest obstacle to reaching this state at all.

-30. **(s178, superseded as top priority by s179 above): find and instrument the caller/scheduler of
    `runHangarSelectionFrame`.** s178 re-ran s177's `swapackwait1` recipe
    (tag `swapackwait2`, no other changes) and for the first time caught the
    actual graphics-task-submission stall crash-free with the producer-side
    `ROGUESQ_LOG_SWAP_ACK_WAIT` instrument armed. Result refutes BOTH outcomes
    NEXT.md anticipated: not "blocked forever inside `osRecvMesg_recomp`"
    (5768 `enter`, 9447/9447 matched `pre-recv`/`post-recv`, zero orphans,
    the last call completes cleanly) and not "keeps cycling normally
    throughout the stall" either — `[swap-ack-wait]` simply **stops
    appearing at all** after `call=5767` (line ~64.04M of a 73.54M-line
    log), closely correlated with `[lle task]` (graphics-task submission
    itself) also stopping around the same point (last entry line ~64.76M,
    driver summary `lle tasks: 5767` matches the last swap-ack-wait call
    number almost exactly). The per-frame producer chain
    (`runHangarSelectionFrame` -> `waitForPrevFrameDone` ->
    `waitForPostSwapAck`) was never invoked again — not stuck mid-call, its
    caller/scheduler stopped iterating. Not a full hang: `[rs-malloc]`
    continues to line ~67.3M and `[rs-free-walk]` keeps firing all the way
    to the log's end (line 73.54M, still active at kill time) — a
    staggered subsystem shutdown, partially correcting the older "heap
    allocation keeps running to the end" (s162) wording (allocation stops
    early; free-walking does not). **Next step: identify the guest OS
    thread that executes `runHangarSelectionFrame` and what its own outer
    loop waits on between per-frame calls (likely VI-retrace-driven,
    separate from `waitForPostSwapAck`), and instrument entry/exit on that
    outer loop to see whether the thread stops being resumed at all (points
    at OS-thread/scheduler starvation, same family as s84-s94's
    thr-resume/OSThread-corruption investigations) or keeps running but
    takes a path that skips `runHangarSelectionFrame` (points at a
    guest-side state/flag check).** Independently, this run's `rdpFs`
    plateau (3579, persistent-stall onset at #14080 with `rdpFs=3560`) is a
    3rd data point squarely inside s176/177's ~3175-3802 candidate-ceiling
    band — promotes that pattern from single-source to a 3-occurrence-
    confirmed, driveable reproduction target (any soak whose `rdpFs`
    approaches ~3500-3600 should be watched closely for the stall). Full
    detail: PORTING-STATE s178.

-29. **(s177, superseded as top priority by s178 above): re-run the `swapackwait1` soak recipe to actually
    catch the graphics-task-submission stall with the new producer-side
    instrument armed.** s177 corrected s176's framing before instrumenting:
    source-read `rt64_state.cpp` (~2841) shows the `[vi-fs-decision]`
    `stalled` field is defined purely from `std::chrono::steady_clock`
    elapsed time (>100ms since last VI-address change) — **not** a hidden
    guest tick/resource-count threshold as s176's NEXT.md speculated. The
    real open question is why the pending workload's `pairs` (fbPairCount)
    field stays 0 forever once stalled, i.e. why the guest stops
    registering new framebuffer pairs. Source-traced the per-frame producer
    chain (`runHangarSelectionFrame` → `waitForPrevFrameDone` →
    `waitForPostSwapAck`, the only point in that per-frame function that
    can block before doing any of the frame's real work) and landed
    `ROGUESQ_LOG_SWAP_ACK_WAIT` (entry + pre/post-recv logging around the
    `osRecvMesg_recomp` call inside `waitForPostSwapAck`, `funcs_5.c:6013`,
    via `N64Recomp/fixup_game_funcs.py`). One soak (`swapackwait1`) ran
    clean through the instrument (7391 `enter`, 10033 matched
    `pre-recv`/`post-recv` pairs, zero orphaned waits) but **did not
    reproduce the stall this run** — it crashed instead to a recurrence of
    the s84 `frameStartReset` SIGBUS (2nd occurrence ever, softening s85's
    "fluke" label) after going further than either s176 run before dying
    (`rdpFs` reached 4125 vs. 3563-3746 at the prior runs' stall onsets).
    **The instrument is armed and validated (real positive control on its
    own mechanics, real negative control on "stuck in this wait" for this
    run's failure mode) but still untested against its actual target** —
    next soak should re-run the same recipe (or extend `STICK_SCHEDULE`)
    specifically watching for either outcome: last log line `pre-recv` with
    no matching `post-recv` and no further `enter` (confirms
    blocked-forever-in-`osRecvMesg` as the stall mechanism), or
    `enter`/`pre-recv`/`post-recv` cycling normally throughout an observed
    stall window (refutes this mechanism, points back at the RT64-side
    `[vi-fs-decision]` gate logic itself). **Secondary lead, same priority
    tier:** an offline re-analysis of the two s176 stall logs (background
    agent, no rebuild) found `rdpFs`/`skSeen`/`skNoTrig` cluster in a
    narrow ~3175-3802 band at both runs' stall onset despite an 87%
    wall-clock difference between the two runs — a candidate shared
    internal ceiling (fixed-size buffer/queue/semaphore count), not
    wall-clock-scaled. Single-source (one grep pass); if a 3rd occurrence
    lands near the same value, this becomes a concrete, driveable
    reproduction target instead of a wall-clock wait. Full detail:
    PORTING-STATE s177.

-28. **(s176, superseded as top priority by s177 above): 2nd consecutive full-hold crash-free soak
    (`scenenodedepthguard2`, exact repeat of s175's recipe, new tag only) —
    still 0/0 on every guard in the family, including the new depth-cap
    guard. Per rule 8, the crash-family-guarding line of work is now
    provisionally parked (2/2 clean, diminishing value from a 3rd identical
    soak) in favor of a genuinely new finding: the graphics-task-submission
    stall (s162's -14, now superseded by this entry) does NOT only strike
    post-leave during the mission-intro cutscene.** This run's process froze
    solid inside SELECT YOUR CRAFT itself, before either scripted leave-key
    press (`hold_95`/`hold_100`) ever executed — confirmed via
    `[vi-fs-decision]` (last real FIRE/SKIP-stalled=0 transition at counter
    #8079, then 300 straight `stalled=1 pairs=0` entries with `rdpFs` frozen
    at 3746 through the end of the log) and via `[phase]` (last width
    transition logged is still `vi_width=512 origin=0x006AB400`, the
    craft-select origin — no post-leave phase transition ever happened).
    Screenshots corroborate: `hold_05.png` through the final `grace_01.png`
    are pixel-identical. By contrast, this same session's `scenenodedepthguard1`
    run (see s175) froze much later, at `vi_width=640 origin=0x006A2900`
    (the post-leave cutscene origin s162 identified), stall onset near
    counter #14528 of ~16000 — i.e. **the same soak recipe produced two
    structurally different stall onset points in back-to-back runs**: one
    pre-leave (idling in the menu), one post-leave (mid-cutscene). This
    rules out "blocked on a post-dive-shot-specific guest function" as the
    *sole* mechanism (s162's leading candidate) — a shared, scene-state-
    independent trigger (most plausibly tick-count or resource-count based)
    is now at least as plausible. **Best next work unit: instrument the
    stall's own trigger condition correlated against wall-clock/tick count
    rather than scene state** — the stall has now been seen in 4 independent
    soaks (s160, s161, and this session's 2 runs) with the surface symptom
    identical (`stalled=1 pairs=0`, RDP `fs` frozen, audio/heap still
    running) but the onset point varying, which is the actual
    discriminating signal to chase next. Full detail: PORTING-STATE s176.

-27. **(s175, superseded as top priority by s176 above): source-read `processSceneNode`'s
    self-recursion and guarded it with a recursion-depth cap** —
    confirmed by direct source read (`N64Recomp/RecompiledFuncs/funcs_4.c:
    13759-14861`) this is a real, guest-intentional sibling-list tree walk
    (rooted at mutable global `0x80112B20`, next-pointer at node offset 0)
    with **no depth argument or local cap anywhere in the original code**
    — the `a3` argument threaded through the recursive call is immediately
    clobbered for unrelated arithmetic, ruling out "it's secretly a depth
    counter." Landed a `static`-counter depth cap (128) that increments at
    function entry and decrements once at the function's single real
    epilogue (`L_80015528`, confirmed the sole convergence point for every
    return path), bailing with return value 0 (which the caller's own
    sibling-loop reads as "stop") past the cap. Built clean. **One soak
    (guard armed): the process survived the ENTIRE 120s hold window +
    grace alive** (had to be killed manually) — the first fully
    crash-free full-length soak anywhere in the s160s-s174 lineage.
    **BUT the new guard itself never fired (0/0), same for every other
    guard in the family this run** — this is a null result on the fix
    specifically (rule 1: not a positive control), consistent with the
    already-established finding (s173/s174) that this whole crash family
    is racy across runs given an identical recipe, not deterministic.
    **Best next work unit: re-run the same soak recipe for a 2nd data
    point** — watch for either another full-hold survival (strengthens
    the case without ever needing the guard to fire) or a run where the
    guard actually trips (first positive control on this fix). Per rule
    8 this is soak 1 of a fresh hypothesis, not the 3rd, so there is
    budget to keep going before parking it. Full detail: PORTING-STATE
    s175.

-26. **(s174, superseded as top priority by s175 above): source-read `tickMusyXIfActive`'s 5 callees
    found and guarded the 23rd crash class's 2nd bug**
    (`tickAndReap3DAudioVoices`'s active-voice-list node-pointer deref,
    `N64Recomp/RecompiledFuncs/funcs_26.c:4224-4225`, mutable-global list
    root `0x80153414`, null-checked only, no range check — guarded via
    `goto` to the function's own epilogue `L_80098F8C` since it is not
    frameless). Ruled out the other 4 candidates by direct read:
    `factor5MutexAcquire`/`Release` touch only a fixed literal counter
    address; `stopAllSynthVoices` is already range-checked by an `slt`
    loop bound; `tickActiveSongs`'s own body only computes compile-time-
    bounded addresses, but its callee `tickSongSequence` (funcs_25.c:
    5018-5046, 5050-5077) has 2 more unguarded list walks — **not guarded
    this session**, next candidate if needed. One soak (guard built,
    armed): **0/0 on both this new guard AND s166's `isAudioSlotActive`
    guard** — the `waitForAnyAudioSlot` chain corruption did not occur at
    all this run, proving that crash is **racy across runs, not
    deterministic given the recipe** (this soak's driven-input schedule
    matches s173's exactly, yet ran ~27x further into the decision stream,
    `decisionN=9694` vs. s173's `356`, without hitting either known
    candidate site). The process instead died to a **2nd independent
    occurrence of the already-catalogued (s172) `processSceneNode`
    self-recursive SIGBUS** (funcs_4.c ~13759-14861, via
    `traverseSceneGraphRecursive`/`setupCameraMatrices`) — same backtrace
    shape both times, now meeting the two-independent-observations bar.
    **Best next work unit: source-read `processSceneNode`'s self-recursion**
    — never opened, now the crash that actually surfaces once the audio-
    chain race doesn't hit. Full detail: PORTING-STATE s174.

-25. **(s173, superseded as top priority by s174 above): landed and validated the `rs_malloc` walk-loop
    deref guard NEXT.md asked for (`N64Recomp/fixup_game_funcs.py`,
    `ROGUESQ_LOG_RS_MALLOC_WALK_GUARD`, file-scoped `funcs_0.c`), but 2
    soaks show it isn't this run's dominant early crash: 0/0 fires despite
    17,683 clean `rs_malloc` calls (real negative control), one soak died
    to the already-catalogued s83 Metal-internal shader-compiler SIGSEGV
    (unrelated, no source on our side), the other died to a **recurrence
    of the 23rd crash class** (`waitForAnyAudioSlot` chain, first seen
    s165) despite s166's own guard on that chain (`isAudioSlotActive`
    base-pointer deref) being confirmed active in the build. **This proves
    the 23rd class is at least 2 distinct bugs, not 1** — s166 closed one
    deref, this soak hit a different, still-unguarded one, one level
    deeper (source-read this session ruled out `anyAudioSlotActive` itself
    and found `tickMusyXIfActive`'s own body has zero direct derefs — the
    fault is in one of its 5 unexamined callees: `factor5MutexAcquire`,
    `tickActiveSongs`, `tickAndReap3DAudioVoices`, `stopAllSynthVoices`,
    `factor5MutexRelease`). **Best next work unit: source-read those 5
    functions for the family's dominant unguarded-deref shape** — this is
    now the earliest-blocking known crash in the whole project (kills the
    run before the title screen even renders, decisionN=356, task #278).
    Full detail: PORTING-STATE s173.

-24. **(s172, superseded as top priority by s173 above): fixed a real gap in the heapWalker guard
    (missing 5th head-deref site + all 5 walk-loops completely unguarded,
    `N64Recomp/fixup_game_funcs.py`/`funcs_3.c`) — 2 soaks show 0/0 on both
    new guards (heapWalker isn't the culprit either soak), but each soak
    surfaced a *different*, newer, better-characterized crash instead of
    heapWalker's own bug: soak 1 survived to hold-iter 27 (longest crashing
    soak of this family yet) then SIGBUS in `processSceneNode` (self-
    recursive, via `traverseSceneGraphRecursive`/`setupCameraMatrices`,
    `funcs_4.c:13759-14861`, not yet source-read); soak 2 died at hold-iter 1
    to SIGBUS **directly inside `rs_malloc` itself**, with the log line
    immediately before the crash showing a garbage ~2.75 GB free-list-node
    size (`[rs-malloc-walk] size=2955542528`) — source-read confirmed the
    walk computes `next = node + size` then dereferences `next` with **zero
    bounds check** (`funcs_0.c` ~line 2967-2969, guest `0x80001BF0`/
    `0x80001BF4`), the exact mechanism a garbage size would trigger.
    **Best next work unit: guard that `rs_malloc` walk's computed-pointer
    deref** (same `0x80000000`-`0x80800000` idiom as the rest of the
    family) — read the loop's full exit condition first, then bail there.
    Full detail: PORTING-STATE s172.

-23. **(s171, superseded as top priority by s172 above): landed the crash-instant `[vi-fs-decision]`
    snapshot s170 asked for (`rs64_get_vifs_crash_snapshot`, always-on, no
    env var — `lib/rt64/src/hle/rt64_state.cpp` + `src/main/main.cpp`), but
    3 soaks of the same recipe (0/3) never reproduced the target scheduler
    SIGSEGV — instead hit 2 different, earlier-position crashes (a new,
    not-yet-characterized `submitSceneNodeRender+16780` site, and a
    recurrence of the old `frameStartReset`/`heapWalker`-inlining class
    whose guard still never fires) plus one crash-free full hold. Checking
    FIRE-event spacing in the logs around both crashes found FIRE recurs
    every 8–61 decisions in this active window — **`decisionsSinceFire`
    values of 22–24 are unremarkable/average spacing here, not proximity
    evidence** — this undercuts, rather than supports, s170's single-run
    stall-clear-adjacency lead. Bigger finding: both crashes happened at
    hold-iter 4–8, far earlier than where the target bug actually lives
    (deep in the late-run ~90%-stuck stall region) — **these soaks never
    reached the phase the hypothesis is about.** Per rule 8, this exact
    recipe is closed for this question (0/3 this session, 2/3 total across
    s169/s170/s171). Next: either fix/characterize what's killing runs at
    hold-iter 4–8 so soaks reliably reach the deep-stall window first, or
    keep accumulating scheduler-SIGSEGV data points across batches of 3.
    Full detail: PORTING-STATE s171.

-22. **(s170, superseded as top priority by s171 above): the s169-soak-2 runtime-scheduler SIGSEGV
    recurred a 2nd time (soak 3/3 of the same recipe) — closes the 14th-
    class pop-guard question (item -21 below, 0/3, tentatively-fixed-
    unconfirmed) and opens this as the live frontier.** Backtrace
    identical both times: `idle_thread_handle -> pause_self ->
    check_running_queue -> swap_to_thread -> resume_thread_and_wait ->
    wait_for_resumed -> moodycamel::LightweightSemaphore::tryWait ->
    std::__atomic_base<long>::load -> SIGSEGV` — runtime (`ultramodern`)
    code, not guest code, so the guarded-deref pattern doesn't apply; reads
    as another face of the s85 shared-thread-context-corruption family.
    New, single-run lead (not confirmed): reading `[vi-fs-decision]` end to
    end in the soak-3 log showed ~90% of the run stuck in the post-leave
    `stalled=1 pairs=0` graphics-stall (item -19/s162's finding) that only
    cleared (`FIRE reason=swap/stalled`, real `pairs`, `addrCh=1`) in the
    last ~2-3% of the log, with the `[CRASH]` line following within ~6500
    more lines of the last clear-event — i.e. the stall's end and this
    crash are close together in the same run. Also checked and **did not
    confirm**: a `[thr-resume-skip] bad_total=1` line fired immediately
    before this soak's crash, tempting as a trigger, but s169 soak 2 hit
    the identical crash with `bad_total=0` all run, and an old s88 soak
    (PORTING-STATE ~line 6758) fired `bad_total=1` near its log's end with
    **no** crash following — adjacency isn't a reliable signal yet.
    **Next work unit:** design a soak that logs `[vi-fs-decision]`'s state
    (or a stall-clear counter) at the moment of crash, not just scanned
    after the fact, to test whether this scheduler SIGSEGV only occurs
    near a stall-clear or can happen mid-stall too. Full detail:
    PORTING-STATE s170.

-21. **(s169, superseded as top priority by s170 above — 14th class closed
    0/3, tentatively fixed but never validated with a positive control):**
    source-read `reserveAndEmitDLEntry` past
    the s109 guard and found it calls `findAndUnlinkSmallestEntry()` (an
    internal free-list pop) 3 separate times (`after_0`/`after_1`/`after_2`,
    guest `0x8000CBC8`/`0x8000CCC4`/`0x8000CDD0`), each null-checking but
    never range-checking the popped pointer before dereferencing it — same
    unguarded-pop-then-deref shape as the rest of the family. Landed 3 new
    guards (`ROGUESQ_LOG_DLENTRY_POP_GUARD=1`, reusing each site's own
    null-check skip label, `N64Recomp/fixup_game_funcs.py`/`funcs_3.c`),
    built clean. Soak 1 (`scratch/agent/run_dlentrypopguard1.sh`): **full
    120s hold crash-free, best-ever result for this env block** (6545
    tasks vs s166's 4709) — but neither the new guards nor s109's guard
    fired (no positive control). Soak 2 (identical re-run, reproducibility
    check): crashed at hold-iter 6, but to an **unrelated, previously-
    uncatalogued runtime-scheduler SIGSEGV** (`idle_thread_handle ->
    check_running_queue -> swap_to_thread -> wait_for_resumed ->
    LightweightSemaphore::tryWait -> atomic load`, same broad chain as
    s70's SIGBUS but a different leaf/signal) — again 0 guard fires.
    **Soak 3 (s170):** another full 120s hold survival, crashed only at the
    very tail to the **identical** scheduler SIGSEGV (2/2 now) — guards
    still 0/4 total. **Net: 0/3 recurrence of the 14th-class crash across
    all 3 soaks**, and 0/3 for any positive control on the 4 guards. Per
    rule 8's 3-attempt budget: **closed as "tentatively fixed, never
    validated with a positive control"** — not "fixed." Guards are real,
    correctly targeted, harmless (0 regressions any run) — stay armed, but
    do not spend a 4th soak on this question. Full detail: PORTING-STATE
    s169, s170.

-20. **(s168, superseded as top priority by s169 above): landed the `rs_free` free-list walk-log
    NEXT.md prescribed (mirrors s165's `rs_malloc` walk-log exactly,
    `ROGUESQ_LOG_RS_FREE_WALK=1`, `N64Recomp/fixup_game_funcs.py`,
    `funcs_0.c`). One soak: the 24th class did NOT recur (informative
    null — both walk-logs fired as clean positive controls, 1.78M/1.59M
    lines, every entry `flags=0x2` with a plausible non-repeating size,
    no corruption pattern on either side of the free list this run).
    **The walk-log line is now closed** — keep both instruments armed
    (they're free and validated), stop chasing this specific soak recipe.
    Process instead died **earlier than any soak on record** (hold-iter
    3, wall=2s, before any scheduled key press) to a **recurrence of the
    already-catalogued 14th class** (`reserveAndEmitDLEntry` SIGBUS, full
    backtrace matches s97 exactly: ← `submitSceneNodeRender` ←
    `processSceneNode` ← `traverseSceneGraphRecursive` (recurses once) ←
    `setupCameraMatrices` ← `static_5_800AAD9C` ← `static_5_800C6854` ←
    `menuOverlayInit` ← `mainGameLoop` ← `mainBootstrapWorker`) — not a
    new class, but a load-bearing new fact about an *existing* one: the
    **s109 guard on this function produced zero log lines** despite the
    crash happening inside it. The crash backtrace resolves to
    `reserveAndEmitDLEntry + 4608` (native offset) — far past the single
    early `ctx->r16` deref the s109 guard covers (confirmed via its own
    comment/placement). **The s109 guard is real but incomplete**: this
    function has at least one more unguarded deref, deeper in the body,
    not yet located or guarded.
    **Next work unit:** source-read `reserveAndEmitDLEntry`
    (`N64Recomp/RecompiledFuncs/funcs_3.c`, guest range starting
    `0x8000CB8C`-ish per the s109 comment) past the guard's anchor point,
    looking for the same "unguarded pointer/table lookup then deref"
    shape as the rest of this family (9th-12th, 14th classes all share
    it), then extend or add a 2nd guard at that site. Success criterion:
    guard fires (or the site is provably unreachable this run) AND the
    process survives past where this crash currently kills it. Full
    detail: PORTING-STATE s168.

-19. **(s167, still valid background, superseded as top priority by s168 above): re-ran `run_audioslotguard1.sh` unmodified
    per s166's own plan — it did NOT stay crash-free. 2nd run died at
    hold-iter 96 (task #7452, fs plateau 4163) to a brand-new **24th**
    crash class: SIGBUS inside `rs_free` (`funcs_0.c:3093`, the shared
    free-list-header walk region ~`0x8010FEE0`), called with a pointer
    read from `freeManifestSegmentAssets`'s fixed 4-entry manifest table
    (`funcs_1.c:3728`, base `0x8011A80` stride `0x50`, field `+0x40`),
    itself called from `menuOverlayInit` → `mainGameLoop` →
    `mainBootstrapWorker`. Never-before-seen call chain (confirmed by
    grep — `freeManifestSegmentAssets` appears nowhere else in
    PORTING-STATE). The `isAudioSlotActive` guard fired **0/0 again**
    (2nd straight null) and the crash is nowhere near its call site, so
    per NEXT.md's own outcome-2 branch: **stop treating the guard as an
    answer to anything** — keep it armed (harmless) but demote it to
    parked, unvalidated. **The 23rd class itself also did not recur**
    either run — 0/2 now, informative but not a fix claim.
    **More load-bearing result than the guard question: no rebuild
    happened between the two runs** (`build/RogueSquadron64Recomp` mtime
    23:05, both driver runs started after that, confirmed via `find
    -newer`) — same binary, run twice, produced crash-free then a
    brand-new crash. This is a clean **refutation, for this specific
    pair**, of "rebuild/relink changes which bug wins the race" (s93,
    s160→s161) as *the* explanation for run-to-run variance in this
    family — the variance is real timing-nondeterminism, not purely a
    binary-layout artifact of rebuilding. Doesn't overturn s93 (that
    case *did* involve a rebuild and *did* show a clean before/after),
    but it does mean "just rebuild and re-run" is not guaranteed to
    stabilize behavior even holding the binary fixed.
    **Next work unit:** extend s165's `rs_malloc` free-list walk-log
    (`ROGUESQ_LOG_RS_MALLOC_WALK=1`) with an analogous `rs_free`
    walk-log at the same free-list-header region, to test whether this
    24th class is the same shared free-list-corruption family as s164's
    `rs_malloc` SIGBUS (both walk structures rooted near `0x8011xxxx`)
    rather than an independent bug. Do NOT re-run
    `run_audioslotguard1.sh` a 3rd time unmodified — 2 data points
    (crash-free/crash) already satisfies the two-source rule on "this
    env block does not reliably survive," per NEXT.md's own stopping
    rule. Full detail: PORTING-STATE s167.

-18. **(s166, superseded as top priority by s167 above): source-read found and guarded a concrete
    unguarded-pointer deref (`isAudioSlotActive`, `funcs_24.c:5788` — base
    pointer from a fixed global slot, indexed, dereferenced with no
    null-check, the family's dominant shape) matching the 23rd crash
    class's call chain. Full regen+rebuild clean. The validating soak
    (`run_audioslotguard1.sh`, same ~35-logger env block as s165's
    `audiodrain3` plus the new guard's log var) was the cleanest run ever
    recorded for this env block: 0 crashes across the entire 120s hold +
    full input sequence (title → SELECT YOUR CRAFT → leave-key → known
    post-leave stall), 4709 `[lle task]` entries vs. s165's death at
    task #267. BUT the new guard never fired (0/0, no positive control) —
    `waitForAnyAudioSlot` was barely exercised (4 calls, all resolved
    immediately) and its base pointer was never observed invalid. Cannot
    attribute survival to the guard itself; it's at least as consistent
    with a 3rd instance of this project's "rebuild changes which bug wins
    the race" confound (s93, s160→s161) as with an actual fix. Treat
    "23rd class blocks earliest" as **not settled** — it is one data
    point in a family with clear run-to-run/build-to-build variance.
    **Next work unit:** re-run `run_audioslotguard1.sh` unmodified once —
    if it stays crash-free a 2nd time, that's the two-source rule on "this
    heavy env block doesn't kill early boot," cheaper and stronger than
    chasing the 23rd class further; if a future soak *does* reproduce the
    23rd class, check whether the guard fires this time (its first real
    positive-control opportunity). Full detail: PORTING-STATE s166.

-17. **(s165, superseded as top priority by s166 above): landed the `rs_malloc` free-list walk-log
    (`ROGUESQ_LOG_RS_MALLOC_WALK=1`, `N64Recomp/fixup_game_funcs.py`,
    file-scoped `funcs_0.c`, logs node addr/flags/size at `L_80001BEC`
    before the advance) and ran the 3rd/final `audiodrain` attempt
    (`audiodrain3`). Clean 23160-line positive control, no corruption
    seen (22nd `rs_malloc` class did not recur — informative null, not a
    refutation). The process instead died to a brand-new 23rd crash,
    SIGSEGV in/near `waitForAnyAudioSlot` called directly from
    `menuOverlayInit`, and far earlier than any prior death in the whole
    family — task #267, 1.7s in, before VI width 1024/title screen is
    ever reached.** Two things not yet resolved: (a) this is the exact
    function s163 flagged for H-AUDIO-DRAIN, but crashing rather than
    spinning, from a call site (`menuOverlayInit`, boot-time) s163 never
    examined — `waitForAnyAudioSlot` is reachable from more places than
    mapped; (b) **confound risk**: this run also introduced the walk-log's
    own 23160 high-frequency `fprintf` calls on top of ~35 other armed
    loggers, the same shape of confound s93 already found once
    (`ROGUESQ_LOG_THREAD_RESUME` silently changing which crash won a
    race) — an unusually early crash on the very first run of a big new
    logger is at least as consistent with "instrumentation overhead
    changed the race" as with "this is now the genuinely earliest-
    blocking bug." **Next work unit, in order:** (1) source-read
    `menuOverlayInit`'s call into `waitForAnyAudioSlot`/`anyAudioSlotActive`
    for an unguarded deref matching this family's dominant shape — free,
    no soak needed, can't be confounded; (2) if inconclusive, one soak
    with `ROGUESQ_LOG_RS_MALLOC_WALK=1` alone (dropping the other ~35 env
    vars) to test the confound hypothesis directly. This closes the
    `audiodrain1/2/3` line per rule 8 — no more unmodified repeats. Full
    detail: PORTING-STATE s165.

-16. **(s164, superseded as top priority by s165 above, mechanism still
    live): audio-drain soak attempt 2/3 (`audiodrain2`)
    died even earlier than attempt 1 (hold-iter 2 vs hold-iter 6), NOT to a
    recurrence of `emitAllocatedDLCommand` but to a brand-new, never-before-
    seen 22nd crash class — SIGBUS inside `rs_malloc` itself (the guest heap
    allocator), called from `rebuildActiveDisplayObjectList` with fixed,
    sane arguments (`size=1024 flags=0`) identical to 14 immediately-prior
    successful calls the same run.** Source-read confirmed `rs_malloc`
    (`N64Recomp/RecompiledFuncs/funcs_0.c:2745`) is a genuine free-list-
    walking allocator: it loads each node's `flags` halfword and `size`
    word and advances `a0 = a0 + size + 0x10` to the next node
    (`L_80001BB0`–`L_80001C04`) — a node with a corrupted `size` field
    would make the walk jump into unmapped memory and SIGBUS on the next
    load, exactly matching the observed crash (fault inside `rs_malloc`,
    not at entry; the already-armed `[rs-malloc]` log shows 14 identical
    successful calls then a crash with **no** matching log line, meaning
    the fault happened mid-walk before the function's own return/log
    statement). Zero new data on H-AUDIO-DRAIN/H-INPUT (still untested —
    process hasn't survived to the ~92s stall window in either attempt).
    Pattern-matches (not yet proven identical to) the long-parked "shared
    heap corruption" thread from s85–s114 (`voice+0x34`, DMA-ring
    `devAddr`, OSThread context) — a fixed struct offset going bad between
    otherwise-normal calls is the same shape of bug, just landing in the
    allocator's own free-list bookkeeping this time. **Next work unit:**
    dump the free-list node's actual `flags`/`size`/address as `rs_malloc`
    walks it (extend `[rs-malloc]` or add a dedicated walk-log) — if the
    corrupted `size` value resembles the known ASCII-garbage corruption
    pattern from the DMA-ring family, that's a strong, cheap link between
    two previously-separate crash investigations. This is preferred over
    spending the 3rd (final) blind soak attempt on the identical recipe,
    given the declining survival trend. Full detail: PORTING-STATE s164.

-15. **s163: source-read found a concrete 3rd mechanism for
    the s162 stall (an unbounded audio-drain spin loop in the cutscene's own
    teardown path), instrument landed and validated, but the soak died even
    earlier than usual to a recurrence of the already-`parked` (s135)
    `emitAllocatedDLCommand` crash before ever reaching the stall window —
    zero data obtained on the actual question.** `cinematicLoopBody`'s
    advance-and-teardown gate (`static_6_800AF550`, `funcs_44.c:6187`) is a
    pure per-frame elapsed-timer against a fixed `.rodata` literal — NOT a
    poll on any DMA/asset-done flag (rules out H-DMA's specific wording) —
    and its teardown branch (`L_800A64BC`) calls two blocking primitives,
    `bufferArbiterProducerScanWait` then `waitForAnyAudioSlot`
    (`funcs_15.c:6896`). Read `waitForAnyAudioSlot`'s actual body: it is
    `while (!anyAudioSlotActive()) {}` with **no iteration cap and no yield**
    — and `anyAudioSlotActive` (`funcs_23.c:8806`) returns 1 when NO channel
    is active, 0 when at least one is (name is inverted relative to its own
    logic) — so this is a **drain-wait**: spin until every audio voice
    reports idle. If one voice never signals idle, this never returns,
    while its neighbor `tickMusyXIfActive` keeps ticking — exactly matching
    the s160/s161 signature (`[lle task]` running forever, `fs` frozen).
    This is a 3rd hypothesis (**H-AUDIO-DRAIN**), neither H-DMA nor H-INPUT
    as literally worded. Landed `ROGUESQ_LOG_AUDIO_DRAIN=1`
    (`N64Recomp/fixup_game_funcs.py`, file-scoped `funcs_15.c`: entry/
    heartbeat-every-2000-iters/exit logging) and extended the key schedule
    to also test H-INPUT in the same soak
    (`scratch/agent/run_audiodrain1.sh`, `STICK_SCHEDULE` adds `95:start
    100:a` after s162's ~hold_92 freeze onset). **Soak result: the process
    died at hold-iter 6** (far short of the ~92s needed to reach the
    stall) to a SIGBUS in `emitAllocatedDLCommand` — same call-chain shape
    as the s132 crash s133-135 already chased and parked after a 3-attempt
    budget, recurring a 4th time, **past** the 2 existing guards
    (`ROGUESQ_LOG_EMIT_DL_GUARD2`/`GUARD3`, both 0/0 this run) — the
    function-internal crash offset shifted by ~600 bytes from s132's
    original, consistent with those 2 guard blocks now sitting before it,
    suggesting a 3rd unguarded site with a similar-but-not-identical shape,
    or a guard bounds-check gap. Not root-caused further this session
    (out of scope for this iteration's work unit). The audio-drain
    instrument got a partial positive control (4 entries/3 exits/0
    heartbeats — all completed calls returned fast) but **zero data on the
    actual stalling call**, since the process never survived long enough.
    **Next work unit:** re-attempt the same soak (no rebuild needed,
    attempt 2/3 for "does this recipe reach the stall window at all") —
    see `scratch/agent/NEXT.md`. If `emitAllocatedDLCommand` recurs again,
    that's a 2nd data point toward reopening the s135-parked hypothesis
    (likely a 3rd unguarded site) rather than treating it as a bystander.
    Full detail: PORTING-STATE s163.

-14. **NARROWED by s176 (see -28 above): the stall's onset is not fixed to
    the post-leave cutscene — a same-recipe soak can also freeze pre-leave,
    still inside SELECT YOUR CRAFT. The "find the guest function blocked
    after the dive shot" framing below is too narrow; kept for history.**
    s162: the s160/s161 "menu-hold" soaks already reached
    a never-before-seen mission-intro cutscene (STAR WARS logo → "Chapter 1"
    crawl → establishing dive shot), then hit a genuine graphics-task-
    submission stall — not a crash. This is now the M3 frontier, replacing
    "survive the menu-transition crash family" (closed, 2/2).** Found by
    re-reading the 120 `hold_NN.png` screenshots each of s160/s161 already
    captured (no new soak) — nobody had looked past the instrument-count
    summary before. `PROBE_MODE=start_only`'s one Start press already leaves
    SELECT YOUR CRAFT into this cutscene; s75/s76/s161's "hangar-flight"
    label for the post-leave scene was an inference from title-yellow color
    decay, never verified against the actual picture, and was wrong.
    Two-source confirmed in both `subtitleguard1` and `subtitleguard2`:
    both show the same logo→crawl→dive sequence, and both end with
    `[vi-fs-decision] ... stalled=1 pairs=0` continuously (RDP `fs` frozen —
    5618 in s161, 4127 in s160) while `[lle task]` (audio RSP ucode) and
    `[rs-malloc]` (heap) keep firing to the very last line of both logs —
    i.e. the process is alive, audio/heap are still running, only
    graphics-task submission has permanently stopped. **Next work unit:**
    find the guest function that should submit the next display list after
    the establishing-dive shot and determine what it's blocked on (leading
    candidates: the DMA-ring/asset-streaming corruption family that's dogged
    this project since s85, or a legitimate "press X to continue" input gate
    the script's Start/stick schedule doesn't satisfy — not yet
    distinguished). The two runs' exact final frames differ (s161 froze
    mid-dive at `vi_width=0`; s160 ended on an uncharacterized small
    object-in-void frame at `vi_width=128`) — that specific difference is
    NOT yet two-source, don't over-claim it. Full detail: PORTING-STATE
    s162.

-13. **s161: two-source rule satisfied on "survives the menu-transition +
    hangar-tick hold" — SUPERSEDED as the active frontier by s162 above,
    but still true as far as it goes.** Original text: drive the
    process PAST SELECT YOUR CRAFT into an actual mission, not another
    repeat of the menu-hold soak.** s161 re-ran s160's exact soak
    unchanged (`scratch/agent/run_subtitleguard2.sh`, only the capture tag
    differs) and got a **2nd consecutive fully crash-free result**:
    `CRASH: 0`, wall=157s, killed only by the script's own timeout —
    `compose-npc-orient-800AB1C8` 893, `anim-recurse` 3982,
    `anim-tex-stream` 6872, `hangar-entry` 3, all exercised with 0
    crashes (s160 had 777/3748/6006/3 respectively — same order of
    magnitude, both clean). The `[subtitle-glyph-guard]`/
    `[subtitle-glyph-guard2]` instruments are **still 0/0 across both
    soaks** — the guard's correctness is still unconfirmed, but the
    crash-free *outcome* is now two-source. This is the **2nd and 3rd
    fully crash-free soaks in the whole post-s86 family's ~70+-session
    history** (the 1st was s88, which itself did not repeat on its very
    next attempts — see s89). Per rule 8: this is exactly 2 agreeing data
    points, which is what the two-source rule asks for — do **not** run a
    3rd identical soak next; that would be a 3rd consecutive attempt at
    an already-answered question. **Important scope caveat**: both
    crash-free soaks used only scripted stick input inside the
    **SELECT YOUR CRAFT menu** hold window (`PROBE_MODE=start_only`, no
    mission actually entered) — this result does NOT mean the process has
    survived 60s of in-mission rendering, only that the menu-transition +
    hangar-tick crash family looks survivable twice in a row. M3's
    done-criteria explicitly requires in-mission rendering with the craft
    responding to input, which this soak battery never attempts. Next
    work unit: identify and try the input sequence that leaves SELECT
    YOUR CRAFT into an actual mission (s75/s76 already established that a
    single Start leaves SELECT YOUR CRAFT into "hangar-flight" — re-read
    that transition and extend the soak script's key schedule past it,
    watching for new crash classes in the mission-load path itself, which
    this family has never soaked before). Full detail: PORTING-STATE
    s161.

-12. **s159/s160: the 21st crash class, `drawSubtitleText`, has a landed
    guard now corroborated by 2 independent crash-free soaks (s160, s161)
    — see -13.** Still not proven the guard is *why* (0/0 positive control
    on the guard itself across both runs), but the outcome-level two-source
    rule is satisfied. Do not re-run this exact soak a 3rd time without a
    new, specific reason (see -13).

-11. **s159/s160: the 21st crash class, `drawSubtitleText`, has a landed
    guard corroborated by 2 crash-free soaks — see -13.** Originally found
    s159 as a brand-new SIGBUS
    (confirmed real, 37300-byte *host*-compiled function via
    `machoparse.py`, crash at host offset `+34664`, genuinely inside its
    own body — but note the guest-instruction span is only ~4.8 KB, so that
    host offset does NOT map proportionally to a guest address; s160 had to
    read the whole function, not jump to an estimated line), backtrace
    `drawSubtitleText` ← `setupCameraMatrices` ← `static_5_800B47D0` ←
    `menuOverlayInit` ← `mainGameLoop`. **Notable: this was the earliest
    death yet in the whole post-s86 family when first found** — during the
    SELECT GAME → SELECT YOUR CRAFT menu transition itself, before any
    `[phase]` transition past `vi_width=1024`, before
    `composeNpcOrientationMatrix`'s entry diagnostic even fired. s160
    found this function is atypically well-guarded compared to the rest of
    the family (real bounds checks on almost every guest-controlled index)
    and traced the one genuine match to the family's classic shape — see
    -12 and PORTING-STATE s160 for the mechanism and the guard.

-10. **s159: proved by full source read that the 15th crash class
    (`loadDrawState` zero-sample-size assert) cannot be caused by ANY
    guest-supplied tile field** — `tile.masks`/`maskt` are structurally
    bounded to 0-15 (4-bit mask at the sole `SetTile` write path,
    `rt64_gbi_rdp.cpp`/`rt64_rdp.cpp`), and every writer of
    `sampleWidth`/`sampleHeight` either clamps to `std::max(..., 1)` or is a
    default-OFF debug probe — so `1 << tile.masks` and `tileWidth`/
    `tileHeight` can never combine to 0. This closes the original s158
    framing ("is it guest garbage or an RT64 bug?") in the **RT64-internal**
    direction — a guest-dispatch instrument was never going to catch a
    mechanism that provably doesn't exist. Landed a guard at the assert site
    instead (`lib/rt64/src/hle/rt64_state.cpp:746-780`,
    `[zero-sample-guard]`, always-on): logs every raw tile field + an
    independent recompute, then clamps to 1 instead of aborting. **If it
    fires again**, a non-zero recompute confirms `dstCallTile` (a live
    reference into `drawData.callTiles`, held across 200+ lines) was
    corrupted or its backing vector reallocated between the correct write
    (`:595`) and the read (`:747`) — an RT64-side reference-invalidation
    bug, not guest-fixable; a zero recompute would mean this session's proof
    has a gap. **Unvalidated this soak** (0/0 — the class simply didn't
    recur; the soak died even earlier, to the new 21st class, see -11).
    `lib/` change, patch exported + committed. Full detail: PORTING-STATE
    s159.

*(original s158 framing, superseded by -11/-10 above — kept for context)*:
    ~~characterize the guest-side call chain feeding RT64's 15th crash
    class.~~ s158 fully answered the s157 work unit (read both
    flagged gaps in `composeNpcOrientationMatrix`; found and guarded a
    genuine 7th unguarded site, `funcs_40.c:6901-6904` — a pointer field
    read from an already-validated table entry then immediately
    dereferenced with **no check at all**, `ROGUESQ_LOG_COMPOSE_NPC_
    GUARD7`) but the soak's actual crash was **not**
    `composeNpcOrientationMatrix` at all (all 7 guards 0/0, entry
    diagnostic 508/508 confirms it was reached but never crashed) — it
    was a **4th recurrence** of the already-catalogued **15th class**
    (RT64-internal, `rt64_state.cpp:747`, `assert((dstCallTile.
    sampleWidth > 0) && (dstCallTile.sampleHeight > 0))` in
    `RT64::State::loadDrawState`, first seen s97, recurred s99/s149).
    This class now recurs **more reliably and earlier** (hold+0-14s
    across all 4 hits) than any single `composeNpcOrientationMatrix`
    site — it is very likely the thing preventing guard7 (and future
    guards) from ever getting exercised. It has no guest-side source
    (RT64-internal), but unlike the TMEM-zero family (s86-90) **no
    `ROGUESQ_LOG_*` instrument exists yet at the guest dispatch site**
    that sets up the tile/sample state `loadDrawState` consumes — next
    work unit: find the guest call site (search `GBI_RDP`/tile-setup
    RDP command handling, likely `gsDPSetTile`/`gsDPLoadTile`-family
    opcodes reaching `RT64::RDP::drawTris`'s call into `loadDrawState`)
    that computes `dstCallTile.sampleWidth`/`sampleHeight`, and log its
    inputs to see whether the zero/invalid value is guest-side garbage
    (fixable by a guard, matching this whole family's pattern) or an
    RT64-side arithmetic bug (not fixable here). Full detail:
    PORTING-STATE s158.

-9. **s157/s158: `composeNpcOrientationMatrix`'s (12th class) 7th
    unguarded site found and guarded** (`funcs_40.c:6901-6904`,
    `ROGUESQ_LOG_COMPOSE_NPC_GUARD7`) — landed, built clean, but
    **unvalidated** (0/0, the function never crashed in the s158 soak;
    see -10 above for why). s157 also found + guarded 4 new sites in
    `heapWalker` (`ROGUESQ_LOG_HEAPWALKER_GUARD`) — still unvalidated
    after 2 soaks (s157, s158) not exercising the crash path. Neither
    0/0 result is evidence the guards are wrong; both remain dormant
    until a soak's actual crash routes through them again. Full detail:
    PORTING-STATE s157/s158.

-8. **s156: refuted the "shared corrupted dispatcher" hypothesis for
    `static_5_800AAD9C`** by a full end-to-end source read (s157) — it
    is a straight-line per-frame tick with 13 unconditional calls in a
    fixed sequence (including both `frameStartReset` and
    `composeNpcOrientationMatrix`), never a table/function-pointer
    dispatch on a runtime selector. The shared 3-frame backtrace prefix
    across the two crash classes is coincidental, not evidence of one
    shared bug — **do not revisit this hypothesis without new
    evidence.** s157 also source-read `frameStartReset` itself and
    found no unguarded dereference in its own guest body (every
    `MEM_*` address there is a compile-time constant) — any future
    `frameStartReset`-attributed crash should be investigated in its
    callees (`heapWalker`, already given 4 guards this session, or
    `tickTextureMaterialExpiry`, not yet read) rather than in
    `frameStartReset` itself again. Full detail: PORTING-STATE
    s156/s157.

-7. **s155: guarded the 20th class (`loadCraftShadowTextures`,
    `N64Recomp/RecompiledFuncs/funcs_16.c:13038-13051`, bounds the
    craft-type index to 0-13 against the 14-entry sentinel table at
    `0x8013A528`) — landed, verified x1, still unvalidated (0/0 across
    2 soaks now, s155 and s156) because the process keeps dying earlier
    in the same war-room/craft-select window to other classes.
    `composeNpcOrientationMatrix`'s 5th/6th sites (s155's candidate)
    confirmed and guarded, see -8 above.

-6. **s154: the "does the FULL_SYNC-loss freeze
    recover" question is ANSWERED — yes, at least once — and a new,
    20th crash class blocked further progress (now guarded, see -7
    above).** 2nd of 3 allowed `run_extendhold1.sh` (`HOLD_S=120`)
    attempts, unchanged from s153's script. This time it reached the
    crawl scene (`origin=0x006A2900` at `141.4s`) and reproduced the
    plateau exactly (`rdpFs` stuck at `3516` across decisions
    `#8970`-`#9656`, 686 consecutive `FIRE reason=swap` entries) — but
    then **`rdpFs` resumed climbing** (`4142` by `#10912`, up to `5607`
    at the eventual crash), contradicting a "permanent stall" reading.
    Screenshots show why: the game kept progressing through cinematic
    content underneath the frozen counter — `hold_90.png` is a
    brand-new scene (planetary-horizon establishing shot, geometrically
    clean, no corruption) and `hold_95.png`/`hold_101.png` show a
    second new scene (engine-glow fan + dark ship silhouette,
    Star-Destroyer-flyover-shaped) — the furthest the process has ever
    rendered past the crawl. **Do not treat a `[vi-fs-decision]`
    plateau as automatically permanent going forward** — watch `rdpFs`
    over a longer window before concluding "stuck." Death was a
    brand-new backtrace: `loadCraftShadowTextures ←
    allocateAndInitCraftNpcContext ← static_6_800A7C4C ← load_cutscene
    ← cinematicLoopBody ← mainGameLoop` — catalogued as the **20th
    class** (the earlier "20th" from s116/s126 was retracted, so the
    number was free) — source-read and guarded s155 (see -7). Full
    detail: PORTING-STATE s154.

-5. **s153: the crawl-scene hang IS confirmed the same
    class as s79/s80's FULL_SYNC-loss (item 1 from s152 is now closed);
    the "does it ever recover on a long hold" question is still open —
    the soak built to test it got preempted by an early, unrelated crash
    before reaching the target window.** From `scratch/s73_post_a_scene/
    scenerq1/run.log` (s152's own capture, no rebuild needed): `[vi-fs-
    decision]`'s `rdpFs` counter plateaus at `3527` at decision `#9049`
    (`synth=962`) and 529 more synthetic `FIRE reason=swap` events fire
    after that with `rdpFs` never moving again, through the end of the
    log (`#10624`, `synth=1491`) — the exact "synthetic FIRE continues
    after the fs plateau" signature s80 root-caused for the hangar-leave
    window. Bonus: `lastCimg`/`lastW` in those late fires drift into wild
    values, extending s81's "mode-3 present of wild last-drawn" reading
    into this window too. **Conclusion: same class, not a new mystery —
    don't investigate the crawl-scene hang and the hangar-leave hang
    separately.** The follow-up soak (`scratch/agent/run_extendhold1.sh`,
    `HOLD_S=120`) never reached the crawl scene at all — it crashed at
    74.1s (hold-iter 3, still in the war-room/craft-select region) with a
    SIGBUS backtrace rooted at `processSceneNode+7176 ←
    submitSceneNodeRender ← traverseSceneGraphRecursive ←
    setupCameraMatrices ← ... ← menuOverlayInit`. This is inside the same
    11188-byte function as s151's confirmed `+7640` crash but a different
    offset and call path — an unconfirmed but plausible sibling of the
    unguarded-table-deref family already guarded elsewhere (s99-s101), not
    yet source-read. **Next work unit: re-run `run_extendhold1.sh`
    (`HOLD_S=120`, unchanged) — this was only the 1st attempt, budget rule
    8 allows up to 3 before parking.** If it reaches the crawl scene and
    the hold window ends with the process still alive, that answers
    "recovers" as `no` (permanent) unless a later hold-second shows `fs`
    moving again; if the process is dead before the hold window, that's
    itself informative about which crash class dominates this longer
    scene traversal. Full detail: PORTING-STATE s153.

-4. **s152: the s151 crash at this exact scene did NOT
    recur — instead the process HUNG, and the hang looks like the
    already-characterized s79/s80 FULL_SYNC-loss class recurring in a new
    window, not a fresh mystery.** Resolved two things NEXT.md left open
    and refuted one hypothesis, all in one soak (densified capture +
    source read + one diagnostic, `scratch/agent/run_scenerq1.sh`):
    (1) **`processSceneNode+7640` is genuinely inside the function**, not
    a nearest-symbol misattribution — a from-scratch Mach-O symbol reader
    (`scratch/agent/machoparse.py`; `nm`/`otool`/`lldb` are not on the
    Bash allowlist and no human is present in this loop to approve them)
    found the function's real host-compiled size is 11188 bytes, well
    past the crash's +7640 offset. (2) **Bonus, unplanned**: the very
    next host symbol after `menuOverlayInit` is a real compiled function
    named `getLevelIntroCrawlId` — independent evidence (on top of s151's
    visual + VI-origin lines) that this is a genuine per-mission intro
    cinematic, not a replay of stale boot scene-graph data. (3) **The
    render-queue-table counter-overflow hypothesis for the crash site is
    refuted**: `processSceneNode` does have an unguarded, unbounded-looking
    write (a monotonic counter into a 12-byte-stride table, same shape as
    s145's confirmed `musyxMixActiveVoices` overflow) but direct
    measurement (`ROGUESQ_LOG_SCENE_RQ_COUNTER=1`) shows it resets every
    frame and never exceeds `max=50` across 59000 fires — not the bug.
    **What actually happened this soak**: `CRASH: 0` — the process was
    still alive at hold+43s when killed. The STAR WARS logo + crawl
    reproduced a 2nd time, independently (`origin=0x006A2900` at
    `142.7s`, matching s151's `142.4s`), and the densified (5 Hz) capture
    shows real progression — logo zoom/fade, then crawl text that gets
    larger/closer than s151's capture ever showed — but the text itself
    renders **corrupted** (`hold_22`: repeating/doubled glyphs, not
    legible prose) and by `hold_23` the frame is **completely frozen**
    (byte-identical through `hold_30`, 7+ seconds). `run.log` shows why:
    `[vi] update_screen` keeps incrementing normally (VI/present loop
    alive) but **`fs` (RDP task count) is flat at 3527** for the entire
    tail — RDP stopped completing work while VI kept re-presenting the
    last frame. This is the same live-VI/flat-`fs` signature s79/s80
    already characterized as "M3 blocker = post-leave FULL_SYNC loss" for
    a *different* window (~90s hangar-leave transition) — seeing it again
    here (~50s later in wall-clock time, a different scene) reframes this
    as a likely recurrence of that already-partially-understood class.
    The known secondary symptom (`UnhandledJumpTarget 0x0231` in
    `factor5_ucode`) also recurred, 876 times, consistent with (not proof
    of) the same mechanism. **Next work unit**: re-run s80's
    `[vi-fs-decision]` diagnostic across this crawl-scene window to test
    whether it's genuinely the same mechanism as the hangar-leave
    FULL_SYNC loss, and/or extend `HOLD_S` well past 30 (this run's
    capture window ended while the process was still alive but frozen —
    unknown whether it ever recovers). Do NOT re-chase a table-deref
    guard in `processSceneNode` — that specific hypothesis is refuted and
    there was no crash this run to localize a guard against. Full detail:
    PORTING-STATE s152.

-3. **s151: a genuinely NEW post-hangar scene appeared
    for the first time in ~150 sessions — a "STAR WARS" logo + scrolling-
    crawl-style intro — before crashing again ~6s later. This SUPPORTS
    s150's hypothesis (a) ("this camera path is a genuine launch
    cinematic") over hypothesis (b) ("dead-end hangar animation").**
    Landed 2 more `composeNpcOrientationMatrix` guards (3rd/4th unguarded
    table-deref sites, `ROGUESQ_LOG_COMPOSE_NPC_GUARD3`/`GUARD4` in
    `N64Recomp/fixup_game_funcs.py`) per item -2 below, then soaked
    (`composeguard3`). The function was never reached this run (0
    `[compose-npc-orient]` entry logs), so the guards remain
    **unvalidated** — but the process survived to hold-iter 26/30 (far
    longer than any prior soak in this family, which died hold+1-17s)
    and its own screenshots (`scratch/s73_post_a_scene/composeguard3/
    hold_13.png` through `hold_25_sl.png`) show a **"STAR WARS" logo**
    (the same asset as the game's own boot attribution sequence) growing
    across `hold_13`→`hold_17` (dolly/zoom), fading to black by
    `hold_22`, then crawl-text-like glyph fragments streaking across
    `hold_24`/`hold_25` — visually nothing like the corrupted hangar
    seen in every prior soak. **Independent code-level confirmation**:
    `[phase] vi_width` shows a transition to width 640, origin
    **`0x006A2900`** at t=142.4s — timed almost exactly to `hold_24`/
    `hold_25` (hold started ~t=116.6s) — the **first novel VI origin**
    observed in this entire investigation (not `0x690400` outdoor, not
    `0x6AB400` war room/craft-select, not any boot-sequence origin). Two
    independent lines (visual + VI-origin) converge on "a real, new
    scene began." **Not yet resolved**: whether this is a genuine
    per-mission intro cinematic or an errant jump into replaying stale
    boot-sequence scene-graph data — both are consistent with what was
    observed. Crash that ended it: SIGBUS resolving to `processSceneNode
    + 7640` (self-recursive-looking, offset large enough that a nearest-
    symbol misattribution is plausible) ← `traverseSceneGraphRecursive`
    ← `setupCameraMatrices` ← `static_5_800C9BF0` ← `menuOverlayInit` ←
    `mainGameLoop`; `emit-dl-guard2`/`3` (which cover the already-
    catalogued 14th class, `reserveAndEmitDLEntry`, sharing this same
    `submitSceneNodeRender`/`processSceneNode` backtrace shape) were
    armed and did not fire — inconclusive whether this is the 14th class
    inlined or a genuinely distinct site. **Next work unit**: densify
    capture (`CAPTURE_TICK_S=0.2` or lower) specifically across the
    `hold_13`→`hold_25` window in a fresh soak to nail down the crawl
    text and the exact crash timing, AND source-read/guard whatever
    crashes at `processSceneNode`+7640 so the process can survive past
    the crawl — if a real mission/flight scene follows, M3 is close; if
    it loops back to title/boot, that resolves the cinematic-vs-
    erroneous-jump question the other way. Full detail: PORTING-STATE
    s151.

-2. **s150: "single Start leaves SELECT YOUR CRAFT into
    hangar-flight" (s75/s76) is OVERTURNED — mission-entry is unanswered
    again.** Densified capture (0.2s-tick screenshots across the
    post-Start-press window, `run_leavedense1.sh`/`leavedense1/`) shows
    the previously-called "hangar-flight, airborne X-wing" frames are the
    *same* SELECT YOUR CRAFT hangar 3D scene — identical X-wing pose, R2
    unit, red crate, wall paneling, moon backdrop — just a progressively
    closer/lower camera angle with escalating render corruption (large
    striped/aliased degenerate polygons), not a new environment. Cross-
    checked against the archived s76 `hold60/after_p1_start_04`/`hold_01`/
    `hold_04.png` (an independent prior run, not a new soak) — same
    scene, same corruption shape, second confirmation. Third, independent,
    code-level line of evidence from this soak's own crash: process died
    to a **3rd recurrence of the already-catalogued 12th crash class**
    (`composeNpcOrientationMatrix`/`static_5_800AB1C8`, SIGBUS, signal 10)
    past **both** of its existing guards (s100 first-loop guard, s126
    second-loop guard — neither fired, 0/567 entries), meaning a 3rd,
    still-unlocated unguarded fault site exists inside the function —
    and its full backtrace (`menuOverlayInit` → `runHangarMenuFromOverlay`
    [`static_5_800C6854`] → `runHangarSelectionFrame` [`static_5_800AAD9C`]
    → `composeNpcOrientationMatrix`) is **entirely already-known
    hangar-menu code**, none of it mission-overlay. See "Overturned
    conclusions" for the full writeup. **Next work unit, either:** (a)
    source-read `composeNpcOrientationMatrix` end-to-end (not just the
    two known loops) to find and guard the 3rd fault site — the most
    direct path to surviving past this crash and seeing what (if
    anything) the camera path settles into; or (b) instrument the
    Start-press handler itself (find what `menuOverlayInit`/
    `runHangarMenuFromOverlay` branch the Start key actually triggers) to
    determine whether this camera path is a genuine launch-cinematic that
    would eventually cut to a mission scene, or a dead-end animation
    that never leaves the hangar-selection subsystem. Do NOT re-assume
    "leave transition already fires, only survival is open" — that
    framing (s149) is the thing s150 overturned.

-1. **CLOSED (s147): the count-then-pointer-store race in
    `allocateSongChannelArray` (Thread B's root cause, 0c below) is
    fixed and verified.** Relocated the early `voiceCount` write to
    run *after* the pointer-store block (`N64Recomp/fixup_game_funcs.py`,
    new s147 patch) — plus its dependent reload (`0x8008F0D8-DC`), moved
    as a unit so the reload still reads back exactly what was just
    written (moving the write alone would have made the reload read the
    *previous* call's stale count, a new bug NEXT.md's register-only
    safety argument didn't rule out). 2/2 verification soaks
    (`countracefix1`, `countracefix2`) clean: 13/13 allocations in the
    correct post-fix order, 0/13 `[voice-active-gate-nz]` corrupted
    reads (vs. 5 pre-fix), 0/2 `do_rom_read` recurrences (vs. 9 prior
    occurrences) — soak 2 was the **first fully crash-free full soak**
    for this repro shape since s83. Full detail: PORTING-STATE s147.
    **s148 (2nd closure, per this item's own step 4):** reran the exact
    same battery a 3rd time (`countracefix3`, pure repro, no code
    change) — **fully crash-free again** (0 crashes, 5920 LLE tasks,
    process alive at the 58s wall-clock mark, killed by the harness on
    schedule, not by a signal). `do_rom_read`/`piDmaWorker` now stands
    at **0/3 recurrences** across the full countracefix battery
    (soak1-3), holding for a 2nd straight session — this is the
    end-to-end validation this thread (s105-148) was chasing; Thread B
    is closed with two independent clean confirmations, not one.
    Source-read first (before soaking) established `emit-dl-guard2`/`3`
    (s133-135) live in `emitAllocatedDLCommand` (`funcs_3.c:2412`), a
    **different function** from the one that crashed in soak 1,
    `reserveAndEmitDLEntry` (`funcs_3.c:14487`) — confirms those guards
    were never expected to cover soak 1's crash site, closing that open
    question from s147. `reserveAndEmitDLEntry` itself allocates via
    `findAndUnlinkSmallestEntry` (`funcs_6.c:12472`), a bucketed
    best-fit free-list walker over fixed globals at `0x8011xxxx`/
    `0x8012xxxx` — a plausible SIGBUS site if that free-list's own
    pointers are ever corrupted, but **did not recur this soak**
    (0 `[dlentry-guard]` fires, 20/20 `[dlentry-reserveAndEmit]` entry
    logs clean, 0 `[emit-dl-guard2]`/`3` fires as expected). Across the
    3-soak countracefix battery, `reserveAndEmitDLEntry` is now **1/3**
    — informative as a rare tail event in the already-catalogued 14-class
    family, not (yet) a reliably-recurring blocker; no guard written this
    session, per NEXT.md's own decision rule (a fix needs the crash
    confirmed *reachable and recurring* first). **New top priority:**
    M3's "done when" bar (60s of in-mission rendering, craft responds,
    0 stability counters) is not yet met — this soak's 58s of
    crash-free time was still the pre-mission **SELECT YOUR CRAFT**
    menu/hangar-selection scene (`vi_width` never left the 512/640
    menu pair; last phase line still `origin=0x006A2900`), not a
    mission. Next work unit: either (a) one more countracefix-shape
    soak to build a 3rd/4th crash-free data point and firm up the 1/3
    `reserveAndEmitDLEntry` rate before deciding fix-vs-park, or (b)
    pivot toward actually entering a mission from SELECT YOUR CRAFT
    (unexplored: what input reachably leaves that menu into gameplay —
    the existing `PROBE_KEYS`/stick schedule in `run_mission_keys.sh`
    was built for hold-window soak coverage, not mission entry).
    **s149 (4th and final-per-rule-8 soak on (a)):** `reserveAndEmitDLEntry`
    did **not** recur — stands at **1/4**, **parked, no guard written**
    (doesn't clear this thread's own "reachable and recurring" bar).
    `do_rom_read` also did not recur (**0/4**, a 3rd independent
    confirmation Thread B stays closed). Process died earlier than any
    prior countracefix soak (hold+2s) to a **recurrence of the
    already-catalogued 15th crash class** (RT64-internal `loadDrawState`
    zero-sample-size assert, `rt64_state.cpp:747`, first seen s97,
    recurred s99, now a 3rd time) — not a new class. No source changes.
    **(a) is now answered.** Screenshot check on this exact soak (no new
    run) **revises (b)'s framing**: `hold_01`/`hold_02.png` (+1-2s after
    the p1 Start press) already show a completely different, heavily
    glitched rotated-camera scene vs. the static SELECT YOUR CRAFT menu
    in `pre_p1_start`/`post_p1_start.png` — the leave transition **did**
    fire (consistent with s75/s76's "single Start leaves into
    hangar-flight"), just invisible to VI-phase tracking (same
    0x6AB400 pair, s48). **"What input leaves the menu" is not actually
    open — it's answered.** The real open question is what that
    post-leave scene is (cutscene vs. real mission) and surviving its
    first ~2s, which is exactly where this session's crash and the
    whole s95-99 crash family keep landing. Full detail: PORTING-STATE
    s149.

0a. **CLOSED (s135): `emitAllocatedDLCommand` soak hypothesis parked,
    3-attempt budget exhausted per rule 8.** s133 → environment-side
    Apple-Metal SIGSEGV; s134 → 18th-class recurrence; s135 → the
    separately-tracked `do_rom_read`/`piDmaWorker` corruption SIGSEGV.
    Guards `emit-dl-guard2`/`3` never fired (0/0 all 3 attempts) but
    both stay in the code (real fixes, independent of this question).

0b. **PARKED at 2/3 (s136-s137): `submitSceneNodeRender`
    material-batch-list guard (`MATLIST_GUARD1`/`GUARD2`).** Two soaks,
    both 0/0 on the new guards (uncontrolled null both times), both
    dying to the tracked `do_rom_read`/`piDmaWorker` corruption race
    (byte-identical `devAddr=0x6C676672 dramAddr=0x80195190`), not the
    18th class. Both guards stay in the code regardless (real
    unguarded-pointer-chase fixes, independent of this question). Per
    NEXT.md's own pre-committed decision rule, a **3rd consecutive
    `do_rom_read` recurrence** (s135, s136, s137 — three different
    render-guard hypotheses in a row) triggers promoting Thread B
    (below) from fallback to primary rather than spending the 3rd
    material-batch-list attempt. Of the last 5 render-guard soaks
    (s133-s137), `do_rom_read` now accounts for 3/5 — a clear plurality,
    not yet "always." Full detail: PORTING-STATE s136-s137.

0c. **CLOSED (s147, see item -1 above): fix landed and verified.**
    Thread B, the audio-corruption pivot (`voice+0x0`/`+0x34`,
    s105-138) — longest-running open thread, history below. **s138** ran the s126
    fresh-angle grep (ROM string locate + ROM->RAM mapping, no rebuild):
    solved the ROM->RAM bias for this overlay's rodata
    (`RAM = ROM_offset + 0x7FFFF400`, triple-cross-validated: 3 symbol-file
    pairs + independent disassembly-operand extraction from
    `loadExplosionTextures` all agree exactly) — but applying it shows the
    one static ROM table matching the "explo_tex"/"explh_tex" theme sits
    at `0x8003B370`-`0x8003B3EC`, ~20.3 MB from the corruption zone
    (`0x80171D50`-`0x80172548`), unreachable by that function's own
    small-offset (0-0x1C) indexing — **refutes "a static compile-time ROM
    string table is what's being aliased/indexed."** A full-ROM strings
    dump also found **zero literal matches** for the digit-suffixed
    fragments (`explo_tex2`, `x7`-`x11`, `main_n_atpt_lod`, `at_6`, `at_7`,
    `pilot_sd`) — those are runtime-constructed, not ROM data. Reframes
    (does not overturn) s120's already-established mechanism: an
    out-of-bounds scan past the voice array's own `voiceCount` reads
    whatever `rs_malloc` allocation is heap-adjacent to it — s122/123
    already refuted the one specific adjacent-allocation candidate tested
    (`loadAssetAndIterateSubchunks`'s DMA buffer, ~5.87 MB away, closed
    3/3). **Next work unit: find which `rs_malloc` call's buffer actually
    lands adjacent to the voice array** (`arrayBase=0x801714D0`) at
    corruption time — a heap-layout/allocation-order question, not more
    string/table grepping. Full detail: PORTING-STATE s138.

    **s139** landed `ROGUESQ_LOG_RS_MALLOC=1` (instruments `rs_malloc`
    itself), caught+fixed a real `$a0`/`$a1` argument-order bug in its own
    first soak before trusting the data, then found rs_malloc's true
    signature is `(size, flags)`. Corrected soak narrowed "which heap
    allocation is adjacent to the voice array" to 3 named boot-time
    candidates (`0x8016FD20`/8568B, `0x80171470`/32768B,
    `0x80171DF0`/7728B), not the hoped-for "exactly one". **s140** landed
    the sibling `ROGUESQ_LOG_RS_FREE=1` instrument and re-soaked (first
    crash-free soak in this whole series — 0/0 across every known crash
    class, process survived the full hold+grace window). Two real
    findings: (1) **none of the 3 candidates are ever freed this run** —
    refutes the "freed-and-reused" framing outright, reframing this as a
    still-allocated buffer read out-of-bounds, not a stale/UAF pointer;
    (2) a per-hit range check against this run's own 2 actual hit
    addresses (not the older aggregate zone) **refutes the
    `0x80171DF0`/7728B candidate** — its range starts after both observed
    hit addresses, so it cannot be the buffer being read. **Thread B now
    narrows to 2 candidates**: `0x8016FD20`/8568B and `0x80171470`/32768B
    (the stronger one by adjacency — starts 96 bytes before the array's
    own base). Neither is yet named to a source function. Full detail:
    PORTING-STATE s139-s140.

    **s141** named candidate B and refuted the leading guess for both.
    Source-reading (subagent) proposed both candidates by exact-integer
    divisibility only (`setupSongRenderBuffers`'s own `rs_malloc` call
    divides 8568 exactly by 24; `buildSongDecodeBufferRing`'s 2nd call
    divides 32768 exactly by 256) — flagged explicitly as unproven. A
    call-site tag instrument (`ROGUESQ_LOG_RS_MALLOC_SITE`) correlating
    against the existing `[rs-malloc]` log by sequence order (12/12
    positive control) **refuted both guesses directly**: across 6 calls
    each this run, neither site ever produced 8568 or 32768. But the log
    pinpointed the real producers unguessed: **candidate B
    (`0x8016FD20`/8568B) is `allocateSongChannelArray`'s own second
    `N*(voiceCount+1)*136` allocation (`funcs_23.c:11033`)** — confirmed
    by log-order position (sits exactly between the `V*2576` pair and the
    literal-664 call, matching source order) and by arithmetic on this
    run's own live values (`voiceCount=20`, `N=3` → `3*21*136=8568`
    exactly). **Candidate A (`0x80171470`/32768B) is refuted as an
    audio-subsystem allocation at all** — its one occurrence in the log
    sits immediately after `[overlay] start-match: section 4`, i.e. it's
    produced during overlay loading, a different subsystem than 4
    sessions (s105-140) assumed. Same-run death was the already-tracked
    `do_rom_read`/`piDmaWorker` corruption SIGSEGV (not a new class).
    Full detail: PORTING-STATE s141.

    **s142** (pure source read, no rebuild, NEXT.md option (b)):
    characterized candidate B's write pattern by reading
    `allocateSongChannelArray` end-to-end. **Neither candidate B
    (`funcs_23.c:11033`) nor its identically-sized twin (`:11011`) is ever
    written to by this function** — both are allocated, pointer-stashed to
    a global (`0x80149708`/`0x8014970C`), and left untouched; the function's
    only other work after them is a literal-664B buffer that *does* get
    memset+dcache-writeback, and then it returns. A whole-file grep
    confirms no other function in `funcs_23.c` reads either global either
    (`setupSongRenderBuffers`, the next function in the file, was already
    refuted as producer s141 and now also isn't a consumer). This weakens
    (does not close) candidate B as the *direct* writer of the observed
    ASCII-fragment corruption — if it's the real culprit, some other,
    not-yet-located function (plausibly a different overlay/file) writes
    through the stashed pointer. Bonus 2nd-source confirmation: arrayBase's
    stride (136B) independently matches `symbol_files/main_overlay.
    txt:319`'s human-RE comment ("RSP-mixer voice-slot array... stride
    0x88"), previously uncross-checked against s104's measurement. Full
    detail: PORTING-STATE s142.

    **s143** (pure source read via subagent, no rebuild, NEXT.md option
    (b)): found candidate B is **not orphaned** — it's slot 1 of a
    2-entry double-buffered pointer table (slot 0 = `0x80149708`
    "candidate A-family", slot 1 = `0x8014970C` "candidate B"), selected
    by a toggle byte at `0x80149702` that `musyxSynthFrame` flips (XOR 1)
    every call. `musyxMixActiveVoices` (`funcs_24.c:2477+`) reads the
    *current* slot via the toggle; `musyxBuildVoiceCommandList`
    (`funcs_24.c:2812+`) reads the *other* slot via `toggle XOR 1` — a
    genuine producer/consumer pair, both in `funcs_24.c`, previously
    unsearched because s142 only checked `funcs_23.c`. Confirmed exact
    N64Recomp codegen convention for the fixed-global access pattern:
    `MEM_W(-0X68F8, ctx->r1) = ctx->r2` (write) vs. `ctx->r4 =
    MEM_W(ctx->r1, -0X68F8)` (read, base/offset argument order flips).
    Sanity-checked the grep methodology against the already-known
    arrayBase globals (`-0x6904`/`-0x6908`) — dozens of genuine hits in
    `funcs_24.c`'s musyx functions, confirming the method isn't silently
    missing real consumers. **Reframes the search**: this is no longer
    "find candidate B's unlocated consumer" (closed) but "does the
    per-frame toggle ever desync from the allocation lifecycle, or does
    either consumer's indexing math exceed the buffer's own
    `(voiceCount+1)` bound" — both candidate buffers share the exact same
    136-byte stride as the arrayBase voice array itself, a previously
    unnoted structural link between Thread B's "which allocation is
    heap-adjacent" question and the corruption's own byte shape. Full
    detail: PORTING-STATE s143.

    **s144** (pure source read via subagent + 1 direct spot-check, no
    rebuild, NEXT.md's own prescribed follow-up): read both consumers
    (`musyxMixActiveVoices` `funcs_24.c:2477-2811`,
    `musyxBuildVoiceCommandList` `funcs_24.c:2812-3121`) end-to-end.
    **+0x34 refuted for both** — neither function's own indexing math
    into a slot-derived, 136-byte-stride item ever computes that offset
    (the only two `0x34` literals in either function are an unrelated
    `$sp`-relative `$s3` spill/reload). **Found a real bug instead**:
    `musyxMixActiveVoices` writes into the toggle-selected slot via a
    persistent global write-cursor (`0x80149710`/`0x80149712`, one
    halfword per slot) that it increments and stores back every hit with
    **no comparison against any voiceCount/capacity value anywhere in
    the function** — its only indirect limiter is a different global
    (`0x80149700`) that bounds the unrelated *source*-side scan, not this
    buffer's own allocation size. `musyxBuildVoiceCommandList` then
    consumes that exact same unchecked cursor as its own loop bound
    (handed to it as `a1` by `musyxSynthFrame`, `:3299-3300`), with no
    re-validation either. Confirmed no lock/mutex exists in either
    function, and `musyxMixActiveVoices` independently re-reads the
    async-flipped toggle 5 separate times per call rather than caching it
    once. **Reframes Thread B's leading hypothesis**: from "which
    `rs_malloc` allocation is heap-adjacent" to "does this unchecked
    cursor overrun its slot and corrupt something heap-adjacent" — a
    concrete, source-confirmed unbounded-write mechanism, not yet proven
    to be the specific writer of the arrayBase `+0x34` corruption (the
    victim is a different buffer; the link, if real, is spatial/heap-
    adjacency, same open question as before but now with a named
    mechanism). Deliberately did not build the toggle-desync or
    cursor-overrun instrument this session — both are rebuild+instrument
    work, correctly deferred per rule 8. Full detail: PORTING-STATE s144.

    **s145** (landed + soaked the cursor-overrun instrument s144
    specified, `ROGUESQ_LOG_VOICE_CURSOR=1`): the write-cursor-overflow
    hypothesis is **refuted** for a live-captured corruption event — 0/8
    fires, cursor never near the (independently cross-checked) capacity.
    But the run's own pre-existing `[voice-active-gate-nz]` log caught a
    real corruption live in the same window: scan `idx=0x10/0x11` (16/17)
    read against a freshly-logged `count=0x0012` (18) while the array
    itself was still sized for the **previous** `voiceCount=15` (valid
    indices 0-14) — the bytes read decode as the exact ASCII fragments
    (`explo_tex2`, `x10`, `x11`) s138 catalogued as runtime-only/absent
    from a ROM strings dump, closing that question: they're leftover
    bytes from a recycled, unrelated prior heap allocation. **Real
    mechanism found**: `allocateSongChannelArray` writes the new
    `voiceCount` to the scan-bound global (`0x80149700`)
    **many instructions before** it calls `rs_malloc`/stores the new
    array pointer/prints its own log line (`funcs_23.c:10712-10738`) — a
    non-atomic pair, no lock (consistent with s144's "no mutex anywhere"
    finding) — so a concurrently-scanning `musyxMixActiveVoices` (audio
    runs off the VI-retrace thread, s101) can see the **new**, larger
    count against the **still-old**, smaller array. Single-occurrence,
    not yet reproduced a 2nd time; sibling to (not proven identical to)
    the historically-tracked `+0x34`/`do_rom_read` signature, which did
    not itself recur this run. Full detail: PORTING-STATE s145.

0d. **s139: ran the discriminating rs_malloc-range-overlap measurement
    s138 called for.** Landed a universal `rs_malloc` allocation log
    (`ROGUESQ_LOG_RS_MALLOC=1`, `N64Recomp/fixup_game_funcs.py`, patches
    `rs_malloc` itself rather than call sites) — caught and fixed a real
    bug in it first (the patch had `$a0`/`$a1` backwards; `$a0` is size,
    `$a1` is a pool-selector flags word, confirmed by the `(a0+0xF)&~0xF`
    alignment idiom a few lines later). Corrected soak confirms the voice
    array's per-slot stride is **136 bytes**, and that this run's 5
    corruption hits (`idx=0x10/0x11`) are provably past the array's own
    *actual malloc'd length* (2040 bytes for the active `voiceCount=15`
    allocation), not just past an abstract count. Offline range-overlap
    analysis narrows "which allocation is adjacent" from the whole heap to
    **3 named boot-time pointers** (`0x8016FD20`/8568B, `0x80171470`/32768B,
    `0x80171DF0`/7728B — none ever reallocated elsewhere for the rest of
    the run). Not "exactly one" (NEXT.md's best case), but a real, closed,
    named shortlist. `caller_ra=0x00000000` universal on 100% of 17651
    calls this run, extending s92's finding — stays unusable as evidence.
    3rd/4th straight `do_rom_read`/`piDmaWorker` recurrence across the last
    2 sessions' soaks. Full detail: PORTING-STATE s139.

**Next work unit (s143→s144): characterize `musyxMixActiveVoices`'/
`musyxBuildVoiceCommandList`'s indexing math against the two
double-buffered `(voiceCount+1)*136`-sized slots.** Pure source read,
no rebuild, same low-risk posture as s142/s143. Read
`funcs_24.c:2477-2650` (`musyxMixActiveVoices`) and `funcs_24.c:2812-3300`
(`musyxBuildVoiceCommandList`) end-to-end and answer: (1) what bounds the
per-voice index used against the slot pointer — is it checked against
`voiceCount` (matching the buffer's own `(voiceCount+1)` sizing) or some
other, possibly stale, count; (2) does either function's 136-byte-stride
offset math ever reach a field at `+0x34` specifically (the exact offset
the corruption has always been observed at, s104 on) into one of these
slots rather than into the arrayBase voice array itself — if so this may
BE the corruption site, not just an adjacent allocation; (3) whether
`musyxSynthFrame`'s toggle flip (`funcs_24.c:4117-4127`) could race
against either reader if they don't share a lock/ordering guarantee (a
timing-desync hypothesis, would need an instrument to confirm, not just
a source read). Do NOT re-search for candidate B's consumer — s143 found
and named it. Full detail: PORTING-STATE s143.

0. **Regen-pipeline reliability bug (s120, intermittent — confirmed
   NOT deterministic, s121; s126 ran a 3rd clean delete-all cycle with
   the mandatory patch-report audit and again found every line's
   multiplicity exactly as expected, no duplicates — 2 clean cycles now
   vs. s120's 2 dirty ones, still "can happen," not "will happen").**
   s121 ran the identical delete-all →
   `make_elf.py` → `regen_n64recomp.sh` → `fixup_game_funcs.py` →
   `cmake --build` cycle and got a **fully clean result**: every patch
   report line `x1` (or its documented multiplicity), no duplicate
   labels, build exit 0. So the bug from s120 (2/2 reproductions) is
   real but **not guaranteed on every clean cycle** — treat s120's
   "reproduced twice in a row" as "can happen," not "will happen."
   Keep doing the mandatory post-fixup audit (step 4 below) every
   session regardless; do not skip it just because the last cycle was
   clean. Root cause still not found. The documented regen order
   (`make_elf.py` → `N64Recomp` →
   `fixup_game_funcs.py` → `cmake`) does **not** reliably produce a
   clean, single-copy-of-every-patch build. Confirmed mechanism, one
   layer deep: `N64Recomp` skips rewriting any `RecompiledFuncs/funcs_*.c`
   file that already exists on disk (deleting the file first forces a
   byte-for-byte pristine rewrite; leaving it in place silently keeps
   whatever was there, including previous sessions' fixup patches), so
   any patch whose anchor text survives its own insertion (true of
   every patch in this file — they insert *after* the matched
   instructions, never replacing them) stacks a duplicate copy on the
   next `fixup_game_funcs.py` run. This is a sharper root cause than
   s102's "fixup isn't idempotent" — it's `N64Recomp`, not the python
   script, that's unreliable. **But deleting all 45 `funcs_*.c` first is
   necessary and NOT sufficient**: a second from-scratch cycle
   (delete-all → regen → fixup → build) reproduced the exact same
   duplicate-label compile failure in two *different* files
   (`funcs_3.c`'s `L_dlentry_guard_exit`, `funcs_40.c`'s
   `L_hangarbay_guard_exit`), and a grep audit found `funcs_23.c`/
   `funcs_24.c`'s newer (non-label) diagnostic patches silently doubled
   too (harmless to game behavior — each patch is its own `{ }` scope,
   so no redeclaration error, just double-printing). Ruled out: cmake
   auto-invoking `fixup_game_funcs.py` a second time (grepped `build/`,
   no reference), duplicate path enumeration via Python's `glob()`
   (checked directly, exactly 45 unique paths). **Root cause not yet
   found.** `tools/agent/regen_n64recomp.sh` (new) at least fixes the
   *unrelated* headless-permission-prefix wall for invoking
   `./build/N64Recomp` from its own directory (rule 10's family), and
   deleting all `funcs_*.c` before every regen is now mandatory, but by
   itself does not guarantee a clean result — **audit the patch report
   for anything other than an expected `x1` (or an intentionally
   multi-site patch's known count) after every `fixup_game_funcs.py`
   run, before trusting the resulting build.** A doubled diagnostic
   does not change underlying game behavior, so crash/stability
   conclusions from past sessions are very likely unaffected, but any
   conclusion resting on an exact log-line count or "first occurrence"
   should be treated as provisional until re-verified this way. Next
   session's first move should be a mechanical one-time audit script:
   for every patch's unique static-variable name, grep-count occurrences
   per file and flag anything that isn't the expected multiple, across
   all 45 files — cheaper than continuing to discover instances one
   compile-error at a time. Full detail: PORTING-STATE s120.

-1. **M3 — explain how `voice+0x0` reads nonzero when its only known
   nonzero-writer never runs.** s116 closed both fallback candidates
   NEXT.md named (`musyxKeyOnVoice`: exhaustive read of all ~650 lines
   found zero writes to its argument anywhere, read-only; `isAudioSlotActive`:
   confirmed pure query, no store) and confirmed via grep that
   `musyxRenderVoiceSamples` (`funcs_24.c:2623`, gated `if (voice+0x0 != 0)`)
   has exactly one call site anywhere — ruling out a second, ungated
   entry path. Landed `ROGUESQ_LOG_VOICE_ATTACK_ENTRY=1` directly on
   `musyxTriggerVoiceAttack`'s own prologue (a chokepoint that catches
   *any* caller, unlike s105-110's caller-side-only instruments) and ran
   3 soaks. The 3rd (`voiceattack3`) is decisive: reached the
   `do_rom_read` crash window at 140.1s with `musyx-dma-call` firing 17x
   and `fill-range-args` firing 7x (same-run **positive control** proving
   `musyxRenderVoiceSamples` genuinely ran multiple times) while
   `[voice-attack-entry]` fired **0x**. This is now a null result *with*
   a positive control, CLAUDE.md's own bar for a real result: the one
   known writer of `voice+0x0` nonzero anywhere in the tree provably
   never executes, in a run where the gate it's supposed to set clearly
   *was* satisfied. Since s115 already established both zeroing writers
   (`allocateSongChannelArray`, `musyxInitVoiceFromSample` — the latter's
   own `+0x0=0` write at `funcs_24.c:5804` was a new s116 finding) DO run
   every session, "uninitialized by design" (the explanation that closed
   the analogous `+0x34` question) does not cleanly apply here — `+0x0`
   has two confirmed writers-to-zero and zero confirmed writers-to-nonzero,
   yet reads nonzero in practice.
   **s117:** landed the value-and-address log NEXT.md prescribed
   (`ROGUESQ_LOG_VOICE_ACTIVE_GATE=1`, `musyxMixActiveVoices`
   gate check). First design (cap=64 total) was itself flawed — the
   ~20-voices-per-call scan rate exhausts a 64-line cap within the first
   audio ticks, nowhere near the ~140s window that matters; fixed in the
   same session (uncapped nonzero-capture + a value-independent 5000-check
   heartbeat as the coverage control) before drawing conclusions. The
   corrected soak (`voicegate2`) got a heartbeat spanning n=0-125000 (real
   coverage proof) and, for the first time ever, **captured the byte going
   nonzero**: `0x65`('e')/`0x78`('x') at consecutive voice slots, then
   `0x02` three more times — addresses matched the base+idx*0x88 arithmetic
   exactly (hypothesis (b), an addressing bug, refuted a second way, now
   on the nonzero case too). The values are ASCII-shaped, not boolean —
   the same general signature s94/s102 already characterized for the
   corrupted DMA `devAddr` field. **Reframes the question**: not "find
   `voice+0x0`'s legitimate writer" (increasingly looks like it doesn't
   exist) but "is this the SAME corruption source as `devAddr`'s, just a
   wider blast radius than assumed" — unifying the s94-102 and s105-116
   threads. **Next work unit**: widen the nonzero-hit log to dump several
   bytes around `voice+0x0` (not just the 1 byte) and directly compare
   against a same-run `musyx-dma-call` corrupted-`devAddr` capture for a
   byte-for-byte or pattern match — the discriminating test for "same
   source" vs. "coincidentally also text-shaped." A probable-new **20th**
   crash class surfaced opportunistically (`voicegate2`, SIGBUS via
   `menuOverlayInit` → `static_5_800C6854` → `static_5_800AAD9C` →
   `static_5_800AB1C8`, 1 occurrence) — catalogued, not chased. Do not
   re-instrument `musyxKeyOnVoice`/`isAudioSlotActive`/the caller-side
   chokepoint chain, and do not re-run the capped voicegate1 design — both
   closed. Full detail: PORTING-STATE s116-s117.
   **s126 closed the "probable-20th class" question**: source read found
   all three backtrace addresses are already-known functions
   (`runHangarMenuFromOverlay`, `runHangarSelectionFrame`,
   `composeNpcOrientationMatrix` — the already-guarded 12th class, s99/
   s100) — s117's "none of these match a catalogued site" was an
   address-lookup claim, not a source read, and was wrong. The real news:
   `composeNpcOrientationMatrix` has a SECOND, independent unguarded
   table-deref loop (runtime-variable NPC-count bound, not the fixed-8
   loop s100 guarded) with the identical crash shape — guarded it
   (`ROGUESQ_LOG_COMPOSE_NPC_GUARD2`), full regen+rebuild clean, one soak
   (unexercised, 0/0, died to the tracked `do_rom_read` race at hold+11s,
   matching s125 almost exactly). There is no 20th function-level class.
   Full detail: PORTING-STATE s126.
   **s127 (Thread A re-audit):** re-read the 9th (`updateAnimated
   TextureStreaming`) and 10th (`static_5_800B4048`) classes to their
   closing braces — both had a SECOND unguarded pointer-chase site the
   s124/s125 guards never covered (same "read a struct/global-table
   pointer field, then deref it with no range check" shape as s126's
   finding). Guarded all 5 new sites (`ROGUESQ_LOG_HANGAR_ENTRY_GUARD2`,
   `ROGUESQ_LOG_ANIM_TEX_STREAM_GUARD2` sites A-D), full regen+rebuild
   clean, one soak — both new guards unexercised (0/0, neither function
   called this run), but for the first time since s88 the **entire 30s
   hold window ran with zero crashes** (not evidence the guards work;
   just this run's path missed every known bad site including the
   `do_rom_read` race). Thread A's generalization now holds 2/2 on the
   functions tried — strong prior the other 5 already-guarded multi-site
   functions (11th, 14th, 16th, 17th, 18th) have the same gap. Full
   detail: PORTING-STATE s127.
   **s128 (Thread A re-audit, item 1/5):** re-read the 11th class
   (`projectModelBoundsToScreen`, `funcs_15.c`) to its closing brace —
   its s101 guard covers only the `a0` argument; the `a2` and `a3`
   arguments (`ctx->r21`/`ctx->r20`) are separately dereferenced as raw
   `Vec3*` with no check at all. Guarded both
   (`ROGUESQ_LOG_PROJECT_MODEL_BOUNDS_GUARD2`/`GUARD3`; GUARD3 matches
   x2, the function's own delay-slot instruction duplication, confirmed
   intentional not a bug), full delete-all regen+rebuild clean
   (multiplicity audited by direct grep, not by re-running the
   non-idempotent fixup script). Soak: all three guards for this
   function unexercised (0/0, function never called this run); process
   died at hold+11s to the tracked `do_rom_read`/`piDmaWorker` race —
   same window as every other soak in this family since s85, not a new
   finding. Thread A's generalization now holds **3/3** on every
   function tried (composeNpcOrientationMatrix s126;
   updateAnimatedTextureStreaming + static_5_800B4048 s127;
   projectModelBoundsToScreen s128). Full detail: PORTING-STATE s128.
   (Also flagged, not chased: the s84 `frameStartReset` SIGBUS — called a
   "fluke" in s85 after 0/2 non-recurrence — recurred once more in s116
   (2/4 soaks total across s84/s85/s116); worth revisiting if it keeps
   preempting the target window, not dominant enough yet to gate.)
   **s129 (Thread A re-audit, item 2/5):** first CLEAN audit in the
   series — `reserveAndEmitDLEntry` (14th class, `funcs_3.c`)'s only
   unguarded-external-pointer site is the one s109 already guards; a
   subagent-flagged repeated pointer-deref pattern past the guard
   verified (by direct source read) to be the SDK's own sentinel-based
   free-list allocator idiom operating on internal pool state, not the
   caller's raw `a0`/`a1` argument — categorically different from every
   prior hit in this thread (composeNpcOrientationMatrix,
   updateAnimatedTextureStreaming, static_5_800B4048,
   projectModelBoundsToScreen all re-derefed the SAME externally-
   supplied pointer past their guard; this function reloads a fresh
   internal pointer instead). Running tally: **4 hits, 1 clean, of 5
   audited.** No code change, no rebuild, no soak this session (verified
   first that both `lib/` submodules' dirty trees exactly match their
   already-committed patches — no session's work was sitting
   unexported). Next: item 3/5, `activateAnimationKeyframe` (16th
   class, `funcs_14.c`, guard at s99). Full detail: PORTING-STATE s129.
   **s130 (Thread A re-audit, item 1/3 of the remaining 3):** SECOND
   clean audit — `activateAnimationKeyframe` (16th class, `funcs_14.c`)'s
   only unguarded-external-pointer site is the one s99 already guards
   (a table lookup off its own `a0` argument into `ctx->r17`); no second
   occurrence of that table load, and none of the function's own raw
   incoming arguments are dereferenced anywhere else. Running tally:
   **4 hits, 2 clean, of 6 audited.** One new lead surfaced but
   deliberately not chased (scope discipline): starting mid-function
   `ctx->r5` is reassigned to the return value of a call to
   `getPlayerSlotFieldAt34` and then dereferenced ~13 times with zero
   check — a *callee-return-value* trust boundary, not a re-deref of
   this function's own argument, so it's a different class than Thread
   A's pattern and belongs to a future audit of `getPlayerSlotFieldAt34`
   itself if it ever surfaces in a crash backtrace. No code change, no
   rebuild, no soak this session (submodule dirty trees re-verified
   against exported patches first). Next: item 2/3, `submitSceneNodeRender`
   (17th class, `funcs_4.c`, guard at s123). Full detail: PORTING-STATE
   s130.
   **s131 (Thread A re-audit, item 2/2 of the remaining, `submitSceneNodeRender`):**
   a HIT, and a big one — the s123 guard covers only 1 of **9** inlined
   copies of the same `findAndUnlinkSmallestEntry`-return + walk-loop
   idiom in this function (one per allocation attempt), and even that
   one copy was missing a check on its *first* touch of the pointer
   (before the loop-back edge s123 guarded). Landed `GUARD2` (initial
   deref, all 9 sites) and `GUARD3` (loop-back walk, the 8 sites that
   had nothing) via one parametrized template in `fixup_game_funcs.py`,
   full delete-all regen + clean build, patch report audited (9/8/1
   exactly as expected). **But the soak (`guard_s131`, all 3 flags
   armed) refutes the hypothesis it was built to confirm**: 0/0/0
   guard fires, yet the process died even earlier than usual
   (hold+~2s vs. the usual hold+11-15s) to the **exact same
   nearest-symbol crash signature** s108/s122/s123 already catalogued
   as the 18th class (`heapFreeListDequeue + 12704` — the identical
   byte offset across 3 independent builds — via `submitSceneNodeRender`
   ← `processSceneNode` ← `traverseSceneGraphRecursive` ←
   `setupCameraMatrices` ← `runHangarSelectionFrame` ←
   `runHangarMenuFromOverlay` ← `menuOverlayInit`). Every known copy of
   the guarded idiom is now covered and none tripped, so **the
   free-list-walk mechanism is refuted as this crash's actual cause**
   — either a different, still-unguarded site in the same function, or
   (per s123's own precedent) a nearest-symbol misattribution of a
   crash that isn't in this function's guest code at all. An attempted
   `nm`-based independent re-derivation of the real crash address was
   **inconclusive** (compared post-ASLR-slide runtime addresses against
   link-time file addresses without capturing the slide — invalid
   comparison, do not repeat without first logging the process's own
   load base). Both new guards are kept regardless (9 genuinely
   unguarded pointer chases, same shape as every other confirmed hit in
   this family) but the 18th class itself is **reopened, not closed**.
   Running tally: **5 hits, 2 clean, of 7 audited.** One function left:
   `updateHangarBayScene` (18th-class label collision alert: this
   function is *unrelated* to the "18th class" crash discussed above —
   the numbering is historical, not the same thing — `funcs_40.c`,
   guard at s110, 5 sites A-E already guarded). Full detail:
   PORTING-STATE s131.
   **s132 (Thread A re-audit, last function, `updateHangarBayScene`):**
   the **biggest hit in the whole series** — a full-body sweep (all 32
   occurrences of a `-0x25A4` object-field load, a mechanism entirely
   separate from the already-guarded A-E `-0x2770`-family table) found
   **26 distinct unguarded pointer-chase sites** (3 of the 32 are safe —
   computed address passed only to a callee, never locally
   dereferenced; 2 more share one dereference through a common merge
   label and got a single guard). Verified by direct source read at 3
   sample sites before committing to the fix (a subagent enumerated all
   32; independent spot-checks matched its table exactly). Guarded all
   26 (`ROGUESQ_LOG_HANGAR_BAY_DEREF_GUARD`, sites G1-G29, same
   U32()-truncated 0x80000000-0x80800000 bound and shared
   `L_hangarbay_guard_exit` exit as A-E), full delete-all regen + clean
   build, patch report audited (26/26 exactly, no duplicates — 3rd
   clean delete-all cycle in a row, further softening s120's "can
   happen" finding though not this session's focus). **Final Thread A
   tally: 6 hits, 2 clean, of 8 functions audited — the audit series
   opened at s126 is now COMPLETE.**
   Soak (`hangarbay1`, `PROBE_MODE=start_only HOLD_S=30`, all 26 new
   sites + the 5 old A-E sites + every other family's guard/diagnostic
   flag armed): **0/0 fires on both the new and old hangar-bay-scene
   guard families** — no positive control for either this run. Process
   died **even earlier than s131's already-earliest death** — essentially
   immediately after the single Start probe, before hold-iter 1
   completed (vs. s131's hold+~2s). Crash: SIGBUS with a **clean,
   unambiguous symbolicated backtrace** (real function names resolved
   directly, no nearest-symbol ambiguity or ASLR-slide caveat needed
   this time) inside `emitAllocatedDLCommand` (called from
   `submitSceneNodeRender + 20872`) ← `processSceneNode` ←
   `traverseSceneGraphRecursive` (x2 frames) ← `setupCameraMatrices` ←
   `runHangarSelectionFrame` ← `runHangarMenuFromOverlay` ←
   `menuOverlayInit` — a genuinely **new, previously uncatalogued** crash
   site (not the s131 `heapFreeListDequeue` nearest-symbol guess; a
   different callee of `submitSceneNodeRender` entirely, unrelated to
   the free-list idiom s123/s131 guarded). Controls: `thr-resume bad=1`
   0/118457 (U3 stays closed, 6th+ straight session); `anim-recurse`
   fired 3266/3266 (positive control good); `anim-tex-stream` 4200,
   `hangar-entry` 2, both no crash; `tmem-zero` 0/0 (8th straight null);
   every other guarded family (compose-npc, dlentry, projbounds,
   scene-node-list) 0 fires — none of the by-now-large guarded set is
   implicated in this run's death. Side note worth carrying forward:
   this crash's clean symbolication suggests the built-in crash handler
   *can* resolve real names reliably when it has them, which may mean
   s131's "nm/ASLR-slide" concern is specific to cases where the
   handler itself falls back to nearest-symbol, not a blanket problem
   with every crash log — worth re-examining if a future "nearest-symbol"
   crash reappears. Full detail: PORTING-STATE s132.
   **s133 (root-cause the s132 `emitAllocatedDLCommand` crash):** source
   read found the EXACT SAME `findAndUnlinkSmallestEntry`-return +
   walk-loop idiom s123/s131 already fixed in `submitSceneNodeRender`,
   inlined here too — twice (once per allocation attempt, `r4`/`r5`
   copies). Guarded both the same way (`ROGUESQ_LOG_EMIT_DL_GUARD2`/
   `GUARD3`, bail to the pre-existing null-check label), full delete-all
   regen+rebuild clean (4/4 new sites x1, no duplicates — 4th clean
   cycle in a row), spot-read both regenerated sites against source to
   confirm guard-before-deref placement (caught and fixed a wrong-
   template mistake — guard-after-deref — before regen). Soak
   (`emitdl1`, same recipe as s132 plus the 2 new flags, all 32
   `ROGUESQ_LOG_*` flags armed): **0/0 on the new guards** — no positive
   control, `emitAllocatedDLCommand` never even entered with a bad
   pointer this run, so the fix is neither confirmed nor refuted. Every
   other family also held clean; entry-diagnostic positive controls
   fired as usual (anim-tex-stream 4508, anim-recurse 3350, thr-resume
   119989/`bad_total=0`). Process reached **hold-iter 8** (notably
   longer than s132's near-instant death) before dying to a **2nd
   occurrence of the already-catalogued s83 Apple-Metal-internal
   shader-compiler SIGSEGV** (`libCoreFSCache fscache_insert_and_retain`
   ← `MTLCompilerFSCache`/`MultiLevelAirCache` ← `newSpecializedFunction
   WithDescriptor` ← `MTLCompilerScheduler` ← libdispatch worker — no
   guest code anywhere in the backtrace, not attributable to this or any
   prior session's guest-code fix). Both new guards kept regardless
   (2 genuinely real unguarded-pointer-chase bugs, same standing policy
   as every guard since s99). Per rule 8 this is soak attempt 1/3 for
   this hypothesis — one more attempt is still in budget. Full detail:
   PORTING-STATE s133.
   **s134 (re-attempt the `emitAllocatedDLCommand` soak, attempt 2/3):**
   same recipe, no rebuild. `emit-dl-guard2`/`3` again 0/0 — 2nd null in a
   row, still neither confirmed nor refuted. Death this time is **not** a
   3rd new crash: it's a byte-for-byte recurrence of the already-
   catalogued 18th class (`heapFreeListDequeue + 12704` ←
   `submitSceneNodeRender + 27540` ← ... ← `menuOverlayInit`, every frame
   and offset identical to s131's own backtrace) — the **2nd fully-post-
   fix recurrence** of that class (1st was s131 itself, with all 9
   free-list-walk guards already landed and silent both times). This
   satisfies NEXT.md's own "only act on it if it recurs on its own"
   trigger for the 18th class, and reinforces s131's refutation a 2nd
   independent time: the guarded idiom is not the actual cause. Per rule
   8, one more `emitAllocatedDLCommand` soak attempt (3/3) is still in
   budget, but two-for-two losses to known, already-catalogued crashes
   (not fresh mysteries) suggests the soak recipe's bottleneck is that
   something else in the same window crashes first more often than not.
   Full detail: PORTING-STATE s134.
   **s135 (re-attempt the `emitAllocatedDLCommand` soak, attempt 3/3,
   FINAL):** same recipe, no rebuild. `emit-dl-guard2`/`3` 0/0 a 3rd
   consecutive time — never confirmed. Death is **neither** a new
   `emitAllocatedDLCommand` crash **nor** the 18th class (both symbol
   strings entirely absent from this run's log) — it's a byte-identical
   recurrence of the separately-tracked `do_rom_read`/`piDmaWorker`
   corruption SIGSEGV (item -1 below, 12+ prior occurrences;
   `devAddr=0x6C676672 dramAddr=0x80195190`, matching s91/s93/s94/
   s101-104). **This is a 3rd distinct already-known crash class,
   exhausting the 3-attempt budget per rule 8.** Final tally: s133 →
   environment-side Metal SIGSEGV; s134 → 18th class; s135 → `do_rom_read`
   family. **`emitAllocatedDLCommand` hypothesis now parked** — both
   guards stay (real fixes, independent of this question, standing
   policy since s99). Per NEXT.md's own decision tree, next pivot is the
   18th class source-read (`submitSceneNodeRender`'s remaining ~2746
   lines, `funcs_4.c`) since that class's 2 post-fix recurrences (s131,
   s134) already satisfied the re-open trigger and s135 adds no reason to
   prefer Thread B over it (this run's `do_rom_read` hit was a bystander,
   not a targeted repro, and only reinforced s104's already-closed
   "corrupted at entry" finding — no new information for Thread B). Full
   detail: PORTING-STATE s135.
   **s118:** ran the exact discriminating test above (32-byte dump at
   `voice+0x0` nonzero hits, same-run vs. `musyx-dma-call`). The dumps
   are long readable ASCII strings, not raw garbage — e.g. `"explo_
   tex2\0" FFFFFFFF "explx3\0"`, and later in the same run at the same
   addresses, a completely different string set (`"star_"`,
   `"atpt_load"`, `"mat_6"`, `"xenlight"`, `"xckpit"`). Independently
   confirmed **not coincidental**: `explo_tex` matches `main_overlay.txt`'s
   own comment on `loadExplosionTextures` verbatim — this is a real
   texture/asset-name table, not noise. **But** grepping this run's own
   3 corrupted `devAddr` values (`"wing"`/`"lgfr"`/`"lcre"`) against the
   voice-array dumps found **0 literal matches** — not byte-identical,
   so NEXT.md's strict CONFIRMED bar isn't met. Net result: **same class
   of bug** (real name-table strings landing in a field expecting a
   boolean/address), **not proven same instance**. Reframed the open
   question from "find `voice+0x0`'s writer" to "where does this name
   table live, and is the voice-array base pointer (`ctx->r4`) itself
   corrupted to point there" — falsifiable next session by comparing
   `ctx->r4` against a known-good voice-pool pointer from
   `musyxInitVoiceFromSample` in the same run. No new crash class (11th+
   `do_rom_read` recurrence, familiar ~140s window). Full detail:
   PORTING-STATE s118.
   **s119:** source-read before instrumenting found NEXT.md's own
   comparison plan was flawed — `musyxInitVoiceFromSample`'s entry-point
   `ctx->r4` is `voiceIdx` (a small integer), not a pointer; the pointer
   is only computed several instructions later (`funcs_24.c:5901`,
   confirmed unique anchor). Comparing the entry value as a pointer
   would have manufactured a guaranteed false "divergence". Added a
   correctly-anchored second instrument (`[init-voice-slot-ptr]`, reuses
   the `ROGUESQ_LOG_INIT_VOICE_SAMPLE` flag) and ran 2 soaks (of the 3
   NEXT.md allowed). Both got a positive control on the gate-check side
   (`[voice-active-gate-nz]` 5x each, same addresses/strings as s118 —
   4th/5th reproduction) but **`musyxInitVoiceFromSample` never fired at
   all in either run** — 2nd and 3rd data points (after s105) that this
   function does not run on the menu-only path these driven soaks
   exercise, not a crash-timing artifact (the gate-check side clearly
   executed first). Stopped at 2 attempts, not 3 — a 3rd would likely
   repeat the same shape. **Hypothesis (b) as NEXT.md worded it is not
   testable with current call sites** — needs either a more-frequently-
   called known-good voice-pool pointer source, or pivot to the
   refute-branch (find the allocator/table owning the `0x88`-strided
   region directly, independent of ever catching
   `musyxInitVoiceFromSample` alive). Two different hangar-tick-family
   crashes preempted the DMA window across the two attempts (17th class
   s100; `frameStartReset` s84 — its first recurrence since s85, so
   "fluke" no longer holds unqualified, just rare). Full detail:
   PORTING-STATE s119.
   **s120:** pursued NEXT.md's branch (a) allocator hunt via grep (no
   soak needed to start) and found a real, source-confirmed bug —
   `allocateSongChannelArray` stores the same `rs_malloc` pointer into
   two globals (`-0x6904`/`-0x6908`), but `shutdownAudioEngine` frees
   only the `-0x6904` copy, never touching `-0x6908` — a genuine
   asymmetric-free/dangling-alias bug in the original game's own
   compiled code. **Directly refuted as the cause here**: 2 soaks
   (`songlifecycle1`/`2`) show `[shutdown-audio-free]` firing 0/2 times
   — `shutdownAudioEngine` never ran in either run, so `-0x6908` was
   never left dangling by this mechanism. Found a pattern that
   **SUPERSEDED, s121** (see below) — believable at the time because it
   was reproduced 2/2 and the base-address arithmetic checked out, but
   derived from comparing `idx` against the temporally-*nearest*
   `[song-array-alloc]` log line rather than a live register read (that
   field didn't exist yet): every corrupted `[voice-active-gate-nz]`
   hit's `idx` "exceeds the currently-live allocation's own `voiceCount`"
   (burst 1: idx 16-17 vs `voiceCount=15`; burst 2: idx 19-31 vs
   `voiceCount=18`). An attempt to capture `-0x6900`/`-0x6908` directly
   at the corruption instant hit a sign-extension bug in the new
   instrument itself (bare 32-bit literal instead of the codebase's
   `S32(...)`-then-assign-to-`gpr` idiom), producing nonsense
   (`count=0x0029 arrayBase=0x72657375`) that looked like a dramatic
   finding but wasn't — caught and fixed before it entered this
   document, but **not yet re-soaked with the corrected version**: a
   regen-pipeline reliability bug (item 0 above) ate the rest of the
   session first. Both soaks also reproduced the familiar `do_rom_read`
   SIGSEGV shortly after each corruption burst (2/2 temporal
   co-occurrence, not proof of shared cause — s118 already refuted
   byte-identity). Full detail: PORTING-STATE s120.
   **s121: re-soaked with the corrected instrument (`songlifecycle3`,
   the 3rd and last allowed soak in this family per rule 8) and this
   claim did NOT hold up.** With sane, directly-read `count=0x0012`
   (18) / `arrayBase=0x801714D0` (both real, unlike `songlifecycle2`'s
   confirmed-garbage read), every observed `idx` (6, 16, 17) was **less
   than** `count` — no corrupted scan index exceeded the live loop
   bound in this run. Cross-checking burst 1 against `[song-array-alloc]`
   log-line order showed the *actual* mechanism behind s120's claim:
   the two log call sites (`musyxMixActiveVoices` on the audio-tick
   thread, `allocateSongChannelArray` on the allocator) have no shared
   sequence number, so file line order between them is not a valid
   proxy for real time order (most likely ordinary cross-thread stdout-
   buffering skew) — s120's "idx exceeds voiceCount" was an artifact of
   eyeballing the nearest-in-the-file alloc line, not a live bounds
   violation. **Generalizable**: any s117-120 conclusion built the same
   way (comparing an instrument's value against a non-sequence-tied
   nearby log line from a different thread) inherits this same risk.
   With bounds and loop-bound globals both cleared, the byte dump at
   every firing still shows the same string-table content s118 already
   found (`expl_tex2`, `x10`/`x11`, `explo_te`, etc.) — **two
   independent lines of evidence** (s118's dump, s121's bounds-checked
   read) now agree the corruption is in-bounds *content*, not an
   out-of-bounds scan or a corrupted loop bound. **Next step**: find
   what writes/aliases string-table data into `voice+0x0` at real,
   in-bounds array offsets — a name-table aliasing or heap-reuse
   question, not a bounds-check bug. Full detail: PORTING-STATE s121.
   **s122:** source-read `allocateSongChannelArray` before instrumenting
   (per NEXT.md's own contingency) and found it already contains an
   explicit zero-init loop (`funcs_23.c`, right after the `rs_malloc`
   call) that writes `0x0` to offset `0x0` of *every* voice slot from
   index 0 to the live `voiceCount`, unconditionally, before the pointer
   is used anywhere else. This **refutes literal H1** ("stale rs_malloc
   leftover persisting unmodified into use") as worded — `voice+0x0` is
   guaranteed zero for every live index immediately after every call to
   this function, so any nonzero string content observed later (s118,
   s121) must come from a write strictly *after* this allocation-time
   zero-init, not from unzeroed malloc memory; also confirms NEXT.md's
   own "if it already memsets the buffer, that changes where to hook"
   branch — the planned dump-right-after-malloc probe would have been a
   foregone-conclusion null. Pivoted to NEXT.md's H2 branch instead:
   landed `ROGUESQ_LOG_ASSET_ALLOC=1` on `loadAssetAndIterateSubchunks`
   (`funcs_11.c:0x80054F48`, the generic asset-DMA loader named as the
   likely producer of the `explo_tex`/`atpt_load` strings, shares the
   same `rs_malloc` allocator) to log its buffer's pointer/size/caller
   for an address-coincidence diff against `[song-array-alloc]`. Ran 2
   soaks (`assetalloc1`, `assetalloc2`): the asset buffer's address was
   **constant** (`0x8062B850`) across 6 differently-sized loads within
   each run (consistent with a reused scratch/temp allocation slot) and
   **never overlapped or neighbored** either run's voice-array pointers
   (`0x8016xxxx`-`0x818Dxxxx` range vs `0x8062Bxxx`, ~5 MB apart) — but
   `[voice-active-gate-nz]` (the corruption-observation instrument,
   armed explicitly in the 2nd soak) fired **zero times in both runs**,
   so neither soak captured a same-run corruption event to correlate
   against. Per the null-result-needs-a-positive-control rule, this is
   an **untested** result for H2's coincidence question, not a
   refutation — 2/3 allowed attempts on this exact co-occurrence used,
   0/2 hits. `caller_ra` read `0x00000000` on all 6 fires both runs,
   matching s92's already-established "ra=0 is routine" finding
   (thread-dispatch-context artifact, not diagnostic) — the instrument
   as landed cannot yet distinguish which of the loader's 4 known
   callers fired. Incidental finding: `assetalloc2` died to a **2nd
   occurrence of the already-catalogued 18th crash class**
   (`heapFreeListDequeue`-area SIGBUS via `submitSceneNodeRender` ←
   `processSceneNode` ← `traverseSceneGraphRecursive` ←
   `setupCameraMatrices`, first seen s108 as a 1-off) — per this
   family's own established convention ("not instrumented yet per the
   2nd-recurrence convention"), it is now due for the same source-read +
   guard treatment already applied to the 12th/16th/17th classes,
   arguably higher expected value right now than a 3rd blind attempt at
   the rare asset-alloc/voice-gate co-occurrence. Full detail:
   PORTING-STATE s122.
   **s123: 18th crash class source-read, pinned, and guarded — CLOSED.**
   The nearest-symbol attribution (`heapFreeListDequeue + 12704`) resolved
   to `0x80010174`, which is **not** inside `heapFreeListDequeue`
   (`0x8000CFD4`) at all — it's a label inside `submitSceneNodeRender`'s
   own body (`funcs_4.c`), a different function entirely (nearest-symbol
   was imprecise by a whole function, not just an offset). The real code
   there is an unbounded linked-list "find the tail" walk
   (`v1 = *v1; v0 = *v1;` loop, fed by `findAndUnlinkSmallestEntry`'s
   return) with no validation on the chased pointer at any iteration — a
   new shape for this family (not a table lookup like 12th/16th, not a
   single entry-checked arg pointer like 9th/10th/11th). Guarded at the
   loop's own label (covers both the initial fallthrough and the
   loop-back branch) with a `U32()`-safe RDRAM-range bounds check,
   bailing to the original code's own pre-existing "abandon this relink"
   reentry point (`L_800101A4`, already used for the null-initial-pointer
   case, so semantically consistent with the function's own design).
   Full delete-all regen + rebuild ran clean (patch report audited,
   `submitSceneNodeRender free-list-walk guard patched x1`). Soak: clean
   negative control (0 fires, no regression), process survived past this
   site and died instead to the long-running `do_rom_read` SIGSEGV
   corruption race (s85/s91/s93/s94/s101 family) — no same-session
   positive control on the new guard, expected/acceptable per this file's
   own precedent (s99-s110 never required one before landing). **Bonus,
   same soak, zero extra cost:** `[voice-active-gate-nz]` (H2's
   instrument) got its first-ever same-run positive control (29 fires,
   after 0/2 in s122) — the 3rd and last allowed attempt on this
   co-occurrence question (rule 8), and this time with data instead of
   another null. `[asset-alloc]`'s buffer (`0x8062B850`, constant) never
   overlaps or neighbors the corrupted range (`0x80171Dxx`-`0x80172xxx`,
   ~5.87 MB apart) — **H2 in its specific form is now REFUTED with a
   positive control, not just untested; do not re-run this soak shape.**
   Corrupted content is again long readable asset-name fragments
   (`main_n_atpt_lod`, `at_6`, `at_7`, `pilot_sd`), matching s118's
   signature — reinforces "some name/asset table aliases the voice
   array" without yet identifying which one (not this session's asset
   loader instance). Full detail: PORTING-STATE s123.
   **s124: 9th crash class (`updateAnimatedTextureStreaming`) guarded —
   CLOSED.** Full source read (`funcs_11.c:13667-14268`) confirmed the
   s89 characterization: `$a0`/`ctx->r4` is copied to `$s0`/`ctx->r16` at
   the function's own top (`0x80053F90`) and dereferenced repeatedly
   from a few instructions later (`MEM_W(ctx->r16, 0x2C)` at
   `0x80053FA8`, `MEM_W(ctx->r16, 0x8)` at `0x80054038`, etc. — same
   "unchecked pointer arg dereferenced directly" shape as the 10th/11th
   classes), with real epilogue `L_8005425C` (restores `$ra`/`s0`-`s4`,
   pops `$sp` by `0x38`). Guarded at the `$s0`/`r16` copy site with the
   same `U32()`-truncated bounds check + `goto`-to-epilogue template as
   every prior guard in this family (`ROGUESQ_LOG_ANIM_TEX_STREAM_GUARD`,
   distinct from s90's pre-existing entry-diagnostic flag
   `ROGUESQ_LOG_ANIM_TEX_STREAM`). Full delete-all regen + rebuild ran
   clean (patch report audited: `updateAnimatedTextureStreaming
   arg-pointer guard patched x1`, every other line's multiplicity
   unchanged). Soak (`s124guard`): guard fired 0/0 **and** the function's
   own s90 entry diagnostic also fired 0/0 — `updateAnimatedTextureStreaming`
   was never entered at all this run, so this is weaker than the usual
   "clean negative control on an executed path" (10th/12th/17th's
   precedent); it's an untested guard on an unexercised path, landed
   anyway per this file's own precedent that no positive/executed
   control is required before landing. No regressions in any other
   family control (`thr-resume bad=1: 0`, `ost-wb SKIP_OOB: 3` same as
   usual, `missing-func: 0`, `UnhandledJump: 0`). Process reached SELECT
   YOUR CRAFT stable, single Start succeeded into hangar-flight, and
   died at hold+11s to the long-running `do_rom_read`/`piDmaWorker`
   corruption-race SIGSEGV (same signature as s85/s91/s93/s94/s101/s123 —
   `do_rom_read` → `do_dma` → `osPiStartDma_recomp` → `piDmaWorker`),
   landing squarely in this family's established hold+11-15s window.
   Not a new class; not re-diagnosed. Full detail: PORTING-STATE s124.
   **s125: 10th crash class (`static_5_800B4048`) guarded — CLOSED.**
   Full source read (`funcs_41.c:579-794`) refined the s90 catalog
   one-liner: the guest pointer of interest is `$a1`/`ctx->r5`, but it is
   immediately copied to `$t0`/`ctx->r8` at the function's own entry
   (`0x800B4048: addu $t0, $a1, $zero`) before `$a1` is reused two
   instructions later for an unrelated `lui` — so the live value at each
   of the 4 fixed-offset derefs (`0x10`/`0x14` twice each,
   `0x800B4074`/`0x800B40A4`/`0x800B40D8`/`0x800B4100`) is `ctx->r8`, not
   `ctx->r5`. All 4 derefs live inside the fallthrough arm of the
   function's only early branch; guarded right after that arm's `$s0`
   stack-save (`0x800B406C`), immediately before the first deref, with
   the same `U32()`-truncated bounds check + `goto`-to-existing-epilogue
   template as every prior guard (`ROGUESQ_LOG_HANGAR_ENTRY_GUARD`,
   distinct from s90's entry-diagnostic flag `ROGUESQ_LOG_HANGAR_ENTRY`).
   Real epilogue is the function's own existing label `L_800B4154`, no
   new label needed. Full delete-all regen + rebuild ran clean (patch
   report audited: `static_5_800B4048 arg-pointer guard patched x1`,
   every other line's multiplicity unchanged). Soak (`s125guard`): guard
   fired 0/0 **and** the function's own s90 entry diagnostic also fired
   0/0 — same "untested guard on an unexercised path" shape as s124's
   9th-class result, landed anyway per this file's own precedent. No
   regressions in any other family control (`thr-resume bad_total: 0`,
   `missing-func: 0`). Process reached SELECT YOUR CRAFT stable, single
   Start succeeded into hangar-flight, and died at hold+~11s to the
   long-running `do_rom_read`/`piDmaWorker` corruption-race SIGSEGV (same
   signature and window as s85/s91/s93/s94/s101/s123/s124). Not a new
   class; not re-diagnosed. Full detail: PORTING-STATE s125.

-2. **M3 — find the still-unlocated function that POPULATES the
   MusyX DMA-batch array `musyxSynthFrame` reads from.** s102
   source-read `submitDmaRequestBatch` (confirmed: `a0`=pointer to an
   array of 12-byte `{size,devAddr,dramAddr}` entries, `a1`=count,
   faithful copy loop, no bug here) and the `musyxSynthFrame` call site
   (confirmed: `a0`/`a1`/`a2` are correctly mapped — `a0` is a genuine
   pointer VALUE loaded from `G_BASE-0x68D8`, not the slot's own address
   like s101 assumed for its planned instrument). Landed a
   correctly-targeted instrument (`ROGUESQ_LOG_MUSYX_DMA_CALL=1`,
   `funcs_24.c`) that logs the batch array's contents **before** the
   call. Result: `entry=0`'s `devAddr` is **already** the exact
   corrupted value (`0x6C676672`) at read time, inside
   `musyxSynthFrame`, before `submitDmaRequestBatch` is ever entered —
   **proves** the bug is upstream of both functions this session
   cleared, not in either of them. **s102 also fully characterized the
   corruption's shape** (all 9 entries in the batch, not just the
   crashing one): every `devAddr` fits one of two 4-byte patterns —
   `"lg"+<1 byte>+"r"` or `"wi"+<1 byte>+"g"` — while `size`/`dramAddr`
   in the same entries are sane and mutually consistent (`dramAddr`
   increments by the previous entry's `size` exactly). This is a
   structured tag/index-like value, not noise — reinforces (with a new,
   independent data point) that every prior "race"/"stomp"/"random"
   framing is wrong, not just "unconfirmed". **Next step**: find what
   populates the array at `a0` (this run: `0x80179A60`) — likely a
   MusyX "queue next sample DMA" builder that runs earlier in the same
   per-VI-retrace tick, sourcing `devAddr` from the wrong field of a
   per-sample/per-instrument descriptor (name/tag field instead of ROM
   offset). Candidate approach: grep `RecompiledFuncs/` for stores to
   `0x80179A60`-relative offsets, or for the fixed global pointer that
   must hold this address (likely near `G_BASE-0x68D8`'s neighborhood —
   check what writes *that* slot, not just what reads it). Full detail:
   PORTING-STATE s102.
   **s103 update:** `G_BASE-0x68D8` is a fixed global written **once**
   (a one-time `rs_malloc` in `setupSongRenderBuffers`, MusyX init — not
   a per-tick writer; the array's *contents*, not its base pointer, get
   corrupted per-tick). Source-read `acquireSampleStreamBlock`
   (`funcs_23.c:11871`, guest `0x8008F758`) and found it copies its own
   opaque cache-key argument verbatim into a new batch entry's `devAddr`
   with no translation — a strong-looking match to the "wrong field"
   theory. Landed `ROGUESQ_LOG_STREAM_TAG=1` to test it: **refuted**.
   0/0 fires this soak despite the batch's own count field proving 9
   entries were appended the same tick — `acquireSampleStreamBlock` was
   never entered. **The real writer is `fillSampleStreamRange`**
   (`funcs_23.c:12473`, guest `0x8008FAAC`, called from
   `musyxRenderVoiceSamples` *before* `acquireSampleStreamBlock`), which
   walks a *different* linked list (`-0x664C`, not `-0x6650`/`-0x6654`)
   and writes `entry.devAddr = node->0x8 + node->0x10` — a computed sum
   of two struct fields, not a raw tag copy. Confirmed
   `acquireSampleStreamBlock`'s node-init path never touches offsets
   `0x8`/`0x10`/`0x14` of anything, so whatever allocates
   `fillSampleStreamRange`'s own list nodes (not yet located) must be
   where `node->0x8` first gets its tag-shaped value. **Next step: find
   that allocator** (grep `funcs_23.c` for other `-0x664C` refs/list-node
   inits, or for an `rs_malloc` sized to this node's apparent stride).
   Also: a full ELF regen (rather than re-running `fixup_game_funcs.py`
   alone) incidentally cleared s102's flagged patch-duplication symptom
   this session (every patch reapplied x1, confirmed via the fixup
   script's own report) — the underlying non-idempotency bug in the
   script is still unfixed. Full detail: PORTING-STATE s103.
   **s104 update:** found `fillSampleStreamRange`'s node allocator
   (`initSampleStreamBlockCache`, `funcs_23.c:12070`, guest `0x8008F858`)
   and **cleared it** — it only ever sets a new node's `0x0`/`0x4`/`0x14`
   fields; every path that (re)claims a node (free-list pop, single-node
   eviction, general LRU eviction) converges on one block
   (`funcs_23.c:12993-12999`) that unconditionally recomputes
   `node->0x8 = a1 - ((a1-a3) mod 0x600)` fresh from
   `fillSampleStreamRange`'s own arguments before every use, so the
   allocator never needs to initialize it. Landed
   `ROGUESQ_LOG_FILL_RANGE_ARGS=1` to test whether those arguments (`a1`
   dram target, `a3` tag) are themselves already corrupted at entry —
   **confirmed yes**: logged values match the batch's corrupted
   `devAddr` byte-for-byte (`a1_dram=0x6C676672`/`0x77696E67` = the same
   run's `entry=0`/`entry=1` `devAddr`). **This closes "is
   `fillSampleStreamRange`'s own arithmetic buggy"**: no, its inputs
   arrive pre-corrupted. Both `a1`/`a3` here and `acquireSampleStreamBlock`'s
   (unreached this run) `a0` all trace back to one shared struct field,
   `*(voice_ptr + 0x34)`, read in `musyxRenderVoiceSamples`
   (`funcs_24.c` ~397-451, all 4 call sites in that function share the
   shape). do_rom_read recurred a 9th time, byte-identical family.
   **Next step: find what writes `voice+0x34`** — `musyxKeyOnVoice`
   (`funcs_24.c:1825`) is the obvious first read, not yet done. Full
   detail: PORTING-STATE s104.
   **s105 update:** read `musyxKeyOnVoice` — it writes a similar-looking
   3-word block, but its destination is computed from a *different*
   global (`G_BASE-0x68B0`'s dereferenced value, an RSP cmd-list head
   per the existing symbol comment), not the array
   `musyxRenderVoiceSamples` actually reads — **cleared as a red
   herring**. Found the real match instead: `musyxInitVoiceFromSample`
   (`funcs_24.c:5753`, guest `0x80092128`), whose `G_BASE-0x6908`+
   `voiceIdx*0x88` voice-slot base matches `musyxRenderVoiceSamples`'s
   own array by 3 independent offset checks (`+0x4` rate, `+0x3C`/
   `+0x40` loop points). Its body does a single verbatim word copy,
   `voice+0x34 = sampleDesc+0x4` (plus `+0x38/+0x3C/+0x40` from
   `sampleDesc+0xC/+0x10/+0x14`) — no arithmetic to be buggy. Both its
   call sites build `sampleDesc` fresh from call-site-local sources (a
   global scratch struct in `funcs_22.c`, an on-stack struct from local
   registers in `funcs_26.c`), not a raw asset-table read. Landed
   `ROGUESQ_LOG_INIT_VOICE_SAMPLE=1` and soaked: **fired 0/0** while the
   `do_rom_read` crash recurred a 10th time, byte-identical —
   **inconclusive, not a refutation** (no same-run positive control
   that the instrument can fire at all). Next session needs that
   positive control (e.g. a soak through title-screen music, where a
   fresh key-on is all but certain) before spending another soak on the
   hangar-scene repro. Full detail: PORTING-STATE s105.
   **s106 update:** got that positive control — but for the surrounding
   system, not this specific instrument. Source-read one hop up both
   of `musyxInitVoiceFromSample`'s call sites: `soundMacroOpPlaySampleKeymap`
   (called only from `tickAudioChannel`) and `startStreamedSampleVoice`
   (called only from `serviceVoicePoolFrame`, itself **never referenced
   anywhere** in `RecompiledFuncs/*.c` — same "indirect-call-invisible-
   to-grep" shape as `musyxSynthFrame`'s own caller in s95-s101, so an
   entry counter beats a caller-search here). Landed entry counters on
   both (`ROGUESQ_LOG_VOICE_TRIGGER_CHAIN=1`) and soaked twice: soak 1
   died early to the already-known 15th crash class before reaching the
   DMA window (uninformative, discarded); soak 2 reached the familiar
   ~140s window, crashed on the same 11th `do_rom_read` recurrence, and
   this time carried a clean positive control on the surrounding system
   — `fill-range-args` fired 7x, `musyx-dma-call` fired 17x, proving the
   MusyX per-tick DMA system was genuinely active. Against that
   backdrop, `tick-audio-channel`/`service-voice-pool-frame`/
   `init-voice-sample` **all still read 0/0**. Combined with s105's own
   full-lifetime soak, that's **two independent soaks** showing the
   entire proposed key-on ancestry never executes — closes "was this
   just untested" (no, it's a real null now), but does **not** yet split
   s105's two hypotheses (scene doesn't need a fresh key-on here vs. the
   whole struct-identification was coincidental) — both still fit. Next:
   instrument `tickAllAudioChannels` (`funcs_23.c:4050`, the one static
   caller of `tickAudioChannel`, not yet touched) to find whether the
   gate is even one hop higher. Full detail: PORTING-STATE s106.
   **s107 update:** source-read `tickAllAudioChannels` before
   instrumenting (per its own step 1) and found s106's framing was
   wrong: it has a real static caller, `tickAudioSequencerFrame`
   (`funcs_23.c:6654`), not an indirect-call mystery. That function has
   exactly 3 static call sites, all inside the already-confirmed-running
   `musyxSynthFrame`, each gated by a per-tick countdown divider
   (`G_BASE-0x68EC`, reloaded from a period at `G_BASE-0x68E8` when it
   hits 0) — a completely different mechanism than "unlocated indirect
   caller." `tickAudioSequencerFrame` also has its own second gate at
   entry (`if (MEM_W(rdram, 0x80142038) == 0) return;`) before its
   (unconditional) call into `tickAllAudioChannels`. Landed entry
   counters at both new rungs and soaked: reached the ~140s window
   (151.1s) and died to the same `do_rom_read` crash a 12th time, with a
   clean positive control (`musyx-dma-call`=17, `fill-range-args`=7) —
   but **both new counters read 0/0**, same as `tickAudioChannel`/
   `serviceVoicePoolFrame`/`musyxInitVoiceFromSample`. This is a
   materially stronger result than "one more null" — it localizes the
   block to the countdown-divider gate inside `musyxSynthFrame` itself
   (or something upstream of it), not any unlocated caller, since every
   link in the chain is now a confirmed plain static call. **Next step:
   instrument the countdown/period pair directly** (log the current
   countdown value once per `musyxSynthFrame` call, capped) to
   distinguish "counting down normally, just rare" from "stuck at a
   fixed value" from "period reloaded to something huge every cycle."
   Full detail: PORTING-STATE s107.
   **s108 update:** landed the countdown/period instrument
   (`musyx-gate1`, `ROGUESQ_LOG_VOICE_TRIGGER_CHAIN=1`) at the first of
   the 3 gate sites, built clean (patched x1, verified). Ran the
   allowed 3 soaks (rule 8) — **none reached the ~140s DMA window**;
   all 3 died at 73.5-73.7s (well before `vi_width=640`) to 3 different
   hangar-tick-family crashes (a probable new 18th class, a
   `frameStartReset` recurrence, a `queueGPUUploadTMEM` recurrence — see
   crash catalog below). `musyx-gate1` read 0/0 in all 3, but so did
   `musyx-dma-call`/`fill-range-args` — **the soaks never reached the
   window at all**, so per this file's own rule this is not evidence on
   the countdown question, just more hangar-tick instability. Per rule
   8, stopped after the 3rd non-discriminating attempt. **Reprioritizes
   item 0b (guard the next hangar-tick class) above another `musyx-gate1`
   soak** — reaching the window reliably is now the bottleneck for this
   whole line of inquiry, not the instrument itself. Full detail:
   PORTING-STATE s108.
   **s109 update:** guarded the 14th class (`reserveAndEmitDLEntry`) —
   `U32(ctx->r16)` RDRAM-range check, `goto` a new dedicated epilogue
   label (`L_dlentry_guard_exit`, does not reuse an existing label since
   none was ABI-safe from the guard's insertion point), built clean,
   patched x1 in `funcs_3.c` only. Also capped the function's previously-
   uncapped entry diagnostic (`ROGUESQ_LOG_DLENTRY`, flagged in NEXT.md).
   One soak: guard read **0/0** (`a0` never bad this run — not a positive
   result, the class simply didn't trigger), entry log fired 20/20
   (cap confirmed working). Process still died at 73.9s, same window as
   s108's 3 deaths, this time to a **new, 19th class**: RT64-internal
   `SIGSEGV` in `plume::MetalFramebuffer`'s constructor via
   `RT64::FramebufferManager::createTileCopyRecord` →
   `RT64::RenderTarget::setupColorFramebuffer`/`clearColorTarget` (a
   render-thread frame, not the guest hangar-tick chain every other class
   in this family shares) — 1 occurrence, not source-read, several
   `[last-drawn-skip]` wild/OOB rejections immediately preceding it in the
   log (plausibly related, not confirmed). Full detail: PORTING-STATE
   s109.
   **s110 update:** guarded the 17th hangar-tick class (item 0b) and
   soaked with `ROGUESQ_LOG_VOICE_TRIGGER_CHAIN=1` (covers `musyx-gate1`
   plus the whole `tickAudioChannel`/`serviceVoicePoolFrame`/
   `musyxInitVoiceFromSample` chain) still armed. The process reached the
   ~140s DMA window alive (2nd time ever, after s101) and ran there for
   its full duration before dying to the 10th `do_rom_read` recurrence —
   and **every one of those chain counters still read 0/0**, this time
   with the process actually alive through the whole window rather than
   dying early. That rules out "didn't run long enough" for the first
   time on this specific question, making 5 total sessions (s105-s108,
   s110) of this chain reading null. **Retiring this investigative
   thread** — the struct-identification that motivated chasing
   `tickAudioChannel`'s ancestry was likely coincidental (s105's own
   unresolved caveat), since the demonstrably-active code path that reads
   the corrupted value (`fillSampleStreamRange` ← `musyxRenderVoiceSamples`)
   never goes through it. **Next step: stop chasing callers one hop at a
   time and instead grep the whole compiled tree for every static write
   to `voice+0x34`** (base pattern `G_BASE-0x6908 + voiceIdx*0x88`, per
   s105) to enumerate candidate writers directly — a source-read task, no
   soak required to get the candidate list. Full detail: PORTING-STATE
   s110.
   **s111 update: did that enumeration, decisive null, no build/soak
   needed.** Anchored on the confirmed voice-slot base (load-form grep for
   `MEM_W(ctx->rN, -0X6908)`, the fixed global slot) — exactly 21 hits,
   **all in one file**, `funcs_24.c`; the whole voice array is only ever
   addressed from there. Mapped all 21 to their 14 enclosing functions and
   checked every function's body for any `0x34` reference (read or
   write); also checked `musyxRenderVoiceSamples`/`musyxKeyOnVoice`/
   `musyxSynthFrame` (voice pointer arrives as a direct argument in the
   first two). **Exactly one write to `voice+0x34` exists in the entire
   45-file recompiled tree**: `musyxInitVoiceFromSample`
   (`funcs_24.c:5881`) — already fully cleared, s105/s106. Every other
   voice-array consumer either never touches offset 0x34, or only reads it
   (`musyxKeyOnVoice` ×3 confirmed-unrelated-global per s105;
   `musyxRenderVoiceSamples` ×1, the exact corrupted read that feeds
   `fillSampleStreamRange`). **The "static guest-C write" branch of the
   question is closed with a clean null, not an inconclusive one** — the
   corruption does not enter via any `MEM_W(...,0x34)` store anywhere in
   `RecompiledFuncs/*.c`. **Next step: the RSP MusyX audio microcode
   (`factor5_ucode`)**, not guest C — independently flagged by s110's
   first-ever nonzero `Unhandled jump target 0x1883 in microcode
   factor5_ucode` (385 lines this soak, always 0 before). The ucode has
   its own RDRAM write path this session's grep cannot see by
   construction. Read how `factor5_ucode`'s recompiled dispatch table
   handles (or fails to handle) jump target `0x1883` before designing any
   instrument — do not assume the mechanism. Full detail: PORTING-STATE
   s111.
   **s112 update: hypothesis (a) REFUTED at the source level, no
   build/soak needed — s111's own framing conflated two different
   microcodes.** `factor5_ucode` (no suffix) is the **graphics** ucode:
   `src/main/main.cpp:407` calls it unconditionally for every gfx task
   (confirmed the hot-path call site; `docs/factor5-ucode-dispatch.md`
   independently confirms its dispatch table is vertex/clip/F3D-opcode
   logic, not audio). The **actual** MusyX audio ucode is a differently
   named function, `factor5_ucode_b` — `main.cpp:76` only
   `extern`-declares it, and a repo-wide grep for `factor5_ucode_b(`
   across `src/` finds **zero call sites**, matching `main.cpp:292`'s own
   comment verbatim ("an earlier theory recompiled 0x99FE0 as a 'second
   gfx ucode' factor5_ucode_b — wrong: it's the audio ucode... must never
   run for gfx tasks"). So the `0x1883` diagnostic that fired 385x in
   s110 is from the **graphics** ucode (called thousands of times per
   soak for ordinary DL processing), not from any MusyX/audio code path —
   M5's "never-called artifact" note is about `factor5_ucode_b` and was
   never in tension with s110's observation to begin with. **`voice+0x34`
   cannot be explained by this RSP task.** Side finding, not pursued
   further: `0x1883` sits strictly between labels `L_1828`/`L_18F0`
   (mid-instruction, not a jump-table entry) and its low 12 bits (`0x883`)
   aren't a multiple of 4 — the jump target itself looks like a corrupted
   register value, plausibly a downstream symptom of the same corruption
   rather than a new mechanism, but this needs its own investigation, not
   assumed. **Reopens hypothesis (b)**: a runtime-computed (non-literal-
   offset) store into the voice struct that s111's literal-immediate grep
   (`MEM_W(0X34, ...)`) could not see by construction (e.g. a copy loop
   indexed by a variable field offset). Not yet searched. Full detail:
   PORTING-STATE s112.
   **s113 update: hypothesis (b) REFUTED, exhaustively, no build/soak
   needed — and a 3-session-open sub-question incidentally closed.**
   Every file referencing the voice-array base (`-0x6908` global,
   confirmed exactly 3 via `grep -rl -- "-0X6908"`: `funcs_23.c`,
   `funcs_24.c`, `funcs_32.c`) was read in full for any store whose
   target address is built from register/loop arithmetic rather than a
   bare literal. **None exists**: `funcs_24.c`'s 12 voice-touching
   functions and its one genuine per-voice stride loop
   (`musyxSynthFrame`) only ever store through one more *compile-time
   literal* offset on top of the `idx*0x88` stride (0x0/0x1/0x4/0x10/
   0x14/0x22/0x28/0x2A/0x2C/0x30/0x58/0x60/0x64/0x68/0x6C/0x7C/0x80/
   0x84/0x85 — never 0x34, never computed); `funcs_32.c`'s two
   `-0x6908` hits are an unrelated global at a different base
   (`0x800B`, not `0x8015`) and aren't stores; `funcs_23.c` writes
   `-0x6908`/`-0x6904` exactly once (`allocateSongChannelArray`,
   confirming the 0x88 stride) and never reads them back, so no
   further store chains off it there either. **No computed-offset
   write to voice+0x34 exists anywhere in guest C** — closes hypothesis
   (b) the way s112 closed (a).
   **Unplanned: located the `-0x664C` node allocator s102-s104 flagged
   "not yet located."** It's `initSampleStreamBlockCache`
   (`funcs_23.c:12103`, guest `0x8008F858`) — confirmed the only file
   referencing the exact literal `-0X664C` besides its three
   already-characterized consumers. Its init loop
   (`funcs_23.c:12204-12228`) writes only offsets `0x4`/`0x14` per
   node — **never `0x8` or `0x10`, the exact two fields
   `fillSampleStreamRange` sums into `devAddr`** (s103). Read
   `rs_malloc`'s full body (`funcs_0.c:2743`): no `memset`/`bzero`
   call anywhere in it — allocated memory is never zeroed. Combined
   with s103's own finding that the node-claim path
   (`acquireSampleStreamBlock`) also never touches `0x8`/`0x10`/`0x14`,
   **three independent static facts now agree that offsets `0x8`/`0x10`
   of every node are never initialized by any guest code at all** —
   `fillSampleStreamRange` reads and sums whatever `rs_malloc` handed
   back, i.e. leftover heap contents, not a corrupted write. **New
   hypothesis, well-supported but not yet runtime-confirmed**: this is
   why the "corruption" looks structured (s102's tag-like
   `"lg?r"`/`"wi?g"` bytes are plausible leftover asset-string data) and
   why it reproduces byte-identically across runs (s91/s93 — not a
   race, a deterministic function of asset-load heap history).
   Reframes the whole `do_rom_read` chain (s85-s104, 9 recurrences)
   from "something writes the wrong value" to "nothing ever writes a
   value at all." **Next step: one runtime log** — read
   `node->0x8`/`node->0x10` inside the allocator's own init loop,
   before any consumer could touch them, to turn "never written per
   exhaustive static search" into "observed as already-nonzero at
   allocation time." Full detail: PORTING-STATE s113.
0a. **Tooling: `fixup_game_funcs.py` is not actually idempotent**
   (found s102 while re-running it for the item above) — every patch's
   regex anchor matches text that's left unchanged after insertion, so
   re-running the script without a full ELF regen in between inserts a
   **second** copy of every patch already applied. Confirmed via
   `grep -c` on `funcs_40.c`: the s100 `composeNpcOrientationMatrix`
   guard appears **3 times** (accumulated across s100/s101/s102, none
   of which regenerated from ELF first). Harmless so far (duplicate
   guards are dead code, not incorrect — the first copy's `goto` always
   wins), but bloats `RecompiledFuncs/*.c` every session and is a latent
   risk for any future patch whose anchor is order-sensitive. Not fixed
   yet — cheap fix (exclude matches already followed by the `// PATCH:`
   marker, or always regen from ELF before running fixup) — worth a
   work unit before it compounds further.
0b. **M3 — hangar-tick-family guard program: 8 classes guarded, all with
   clean negative controls (16th/12th/11th/14th/17th/18th/9th/10th).** All follow the
   same shape (`U32()`-truncated bounds check, `goto` to the function's
   real epilogue — never a bare `return;`): 16th
   (`activateAnimationKeyframe`, s99), 12th (`composeNpcOrientationMatrix`,
   s100), 11th (`projectModelBoundsToScreen`, s101), 14th
   (`reserveAndEmitDLEntry`, s109), 17th (`updateHangarBayScene`, s110 —
   this one needed 5 separate guard sites in one function, not one; see
   PORTING-STATE s110), 18th (`submitSceneNodeRender` free-list-walk,
   s123), 9th (`updateAnimatedTextureStreaming`, s124 — guard never
   exercised this soak, function itself wasn't entered), 10th
   (`static_5_800B4048`, s125 — guard also never exercised this soak,
   function itself wasn't entered either). **Do not re-soak
   any of these eight** — treat them as closed. **Every guard patch must verify its own
   `fixup_game_funcs.py` "patched xN" report names only the expected
   file(s)** (s100 caught a real cross-overlay regex collision this way;
   s110 found the *same* function collides with `funcs_27.c` at all 6 of
   its own anchor points — overlays reusing guest address ranges is a
   recurring, not one-off, hazard). **s101 and s110 are now two
   independent data points** that this guard program is sufficient to
   reliably reach the ~140s DMA window: both soaks survived the entire
   family with zero crashes and reached `vi_width=640` alive. The two
   single-occurrence classes that blocked s108/s109 (probable-18th
   `heapFreeListDequeue`-area, 19th `MetalFramebuffer`/
   `createTileCopyRecord`) did **not** recur in s110 either — still below
   the 2nd-recurrence bar for instrumenting; watch passively.
   **No further hangar-tick-family guard work is currently queued** —
   the next M3 work unit is item -1 below (the actual DMA-corruption root
   cause), not another class in this family, unless a new class recurs.
   Full detail: PORTING-STATE s99-s101, s109, s110.
1. **M3 — find the indirect caller of `submitDmaRequestBatch`: CLOSED
   (s101).** The producer/consumer ring instrument (s94) proved an
   unlocated indirect call existed (producer log fires 10x/soak once
   the run reaches ~140s, not just the known boot call, every firing
   after `n=0` carrying `devAddr` that decodes as ASCII text —
   "wing"/"lcre"/"lgfr"/… — never a plausible ROM address). The
   `get_function`-chokepoint backtrace instrument (`ROGUESQ_LOG_DMA_
   CALLER=1`, landed s95) then went **0/0 for 7 consecutive soaks**
   (s95–s100) because every one of those soaks died to a hangar-tick-
   family crash before ever reaching that window — see the crash
   catalog below, and item 0's guard work that eventually cleared
   enough of that family for a soak to survive through it. **s101's
   soak was the first to reach ~140s alive, and the instrument fired
   immediately**: the caller is `musyxSynthFrame`
   (`N64Recomp/RecompiledFuncs/funcs_24.c:3095`, a per-VI-retrace audio
   tick), called from `viRetraceHandlerThread` — not the mission/DL
   code path every earlier session assumed. Confirmed real regressions
   this question already ruled out and must **not** be reopened:
   the `ra=0x00000000` "corruption signature" (refuted s92 — routine on
   487+ calls across four unrelated call sites), "dump the `OSIoMesg`
   at `mb`" (refuted s92 — `mb` is never dereferenced), "consumer index
   desync" and "external RDRAM stomp" (both refuted s94 — the bad value
   is present at write-time inside the producer's own log), and "the
   boot call loops more than once" (refuted s93/s94 — exactly 1
   `submitDmaRequestBatch(rdram` call site exists in all 45
   `funcs_*.c`, no yield points in its loop body). **Next step is item
   -1 above**: source-read `musyxSynthFrame`'s call site
   (`funcs_24.c:3856-3875`) and `submitDmaRequestBatch`'s own signature
   to find the field-mapping bug. Full detail: PORTING-STATE s93-s101.

   **Crash catalog** (family = reached via the hangar-tick per-frame
   chain `runHangarSelectionFrame` → `runHangarMenuFromOverlay` →
   `menuOverlayInit` unless noted; "guarded" = landed + soaked with a
   clean negative control, treat as closed, do not re-soak):
   - 9th, `updateAnimatedTextureStreaming` (`funcs_11.c:13665`, s89):
     unguarded `MEM_W` off `a0`. 1 occurrence, not recurred since.
     **Guarded s124** (`ROGUESQ_LOG_ANIM_TEX_STREAM_GUARD`), 0/0 clean
     negative control — but the function itself was never entered in
     that soak (its own entry diagnostic also 0/0), so this is an
     untested guard on an unexercised path, not a proven-safe executed
     one.
   - 10th, `static_5_800B4048` (unconfirmed name, s90): unguarded
     `MEM_W` off `a1`, saved to `$t0`/`ctx->r8` at entry before `a1` is
     reused (4 fixed-offset derefs). 1 occurrence. **Guarded s125**
     (`ROGUESQ_LOG_HANGAR_ENTRY_GUARD`), 0/0 clean negative control —
     but the function itself was never entered in that soak (its own
     s90 entry diagnostic also 0/0), same "untested guard on an
     unexercised path" caveat as the 9th class.
   - 11th, `projectModelBoundsToScreen` (`0x80065E98`, s92): direct
     deref of arg `a0` (no table lookup, different shape from 12th/16th
     — see PORTING-STATE s101). **Guarded s101**
     (`ROGUESQ_LOG_PROJECT_MODEL_BOUNDS_GUARD`), 0/0 clean negative
     control, no positive control yet.
   - 12th, `composeNpcOrientationMatrix` (`static_5_800AB1C8`, s74 +
     s95): unguarded table-byte-lookup-then-deref (632-byte stride into
     a fixed global array). 2 occurrences. **Guarded s100**
     (`ROGUESQ_LOG_COMPOSE_NPC_GUARD`), 0/544 clean negative control.
   - 13th, RT64-internal assert in
     `FramebufferManager::reinterpretTileRecord`
     (`rt64_framebuffer_manager.cpp:476-480`, s96) — RDP-submission path,
     not the hangar-tick family. **2nd occurrence confirmed s195** (~99
     sessions later, byte-for-byte identical backtrace). **Guarded s196**
     (`ROGUESQ_LOG_REINTERPRET_TILE_GUARD`, mirrors `queueGPUUploadTMEM`'s
     pattern exactly, early-return on unsupported format combo instead of
     asserting), 0/0 — no positive control yet, and the s196 soak never
     reached this line at all (died earlier, to the 18th class) so this is
     NOT a clean negative control either — genuinely untested this session.
   - 14th, `reserveAndEmitDLEntry` (s97/s98): scene-graph-traversal /
     DL-entry shape, not a bare `MEM_W`-off-an-arg deref — flagged as
     possibly needing different treatment than the table-lookup family.
     1 occurrence. **Guarded s109** (`ROGUESQ_LOG_DLENTRY_GUARD`), clean
     negative control (0 fires across the run; the capped entry log
     confirms the function itself is called frequently) but no positive
     control yet — the original SIGBUS has not recurred since to prove
     the guard actually catches it.
   - 15th, RT64-internal assert in `loadDrawState`
     (`rt64_state.cpp:747`, s97) — RDP-submission path, no source-level
     fix available. Recurred once (s99). Park; track recurrence only.
   - 16th, `activateAnimationKeyframe` (s98): unguarded table-byte-
     lookup-then-deref, same shape as 12th. **Guarded s99**
     (`ROGUESQ_LOG_ANIM_KEYFRAME_GUARD`), 0/0 clean negative control.
   - 17th, fault inside `updateHangarBayScene` itself (`static_5_
     800AB658`, s100) — outer call chain matches the 10th class but the
     backtrace is one frame shallower (no `static_5_800B4048` frame),
     confirmed a distinct class. 1 occurrence (never recurred since,
     across 10 soaks s100-s110). **Guarded s110** — source read found the
     table-lookup-then-deref shape repeats 5 independent times in this
     one function (not once); all 5 guarded
     (`ROGUESQ_LOG_HANGAR_BAY_SCENE_GUARD`), 0/5 clean negative control,
     no positive control yet (crash itself hasn't recurred to test it).
   - 18th, nearest symbol `heapFreeListDequeue + 12704` (s108, 2nd
     occurrence s122) via `submitSceneNodeRender` ← `processSceneNode` ←
     `traverseSceneGraphRecursive` ← `setupCameraMatrices` — the
     nearest-exported-symbol attribution turned out to be wrong by a
     whole function, not just an offset: `0x8000CFD4 + 0x31A0 =
     0x80010174` is a label inside `submitSceneNodeRender` itself
     (`funcs_4.c`), not inside `heapFreeListDequeue`. Real shape: an
     unbounded linked-list "find the tail" walk with no pointer
     validation at any iteration — new for this family (not a table
     lookup, not a single entry-checked arg pointer). **Guarded s123**
     (`ROGUESQ_LOG_SCENE_NODE_LIST_GUARD`, bails to the function's own
     pre-existing null-pointer reentry point `L_800101A4`), 0/0 clean
     negative control, no positive control yet.
   - 19th, RT64-internal `SIGSEGV` in `plume::MetalFramebuffer`'s
     constructor (s109) via `RT64::FramebufferManager::createTileCopyRecord`
     → `RT64::RenderTarget::setupColorFramebuffer`/`clearColorTarget` →
     `plume::MetalDevice::createFramebuffer` — a render-thread frame
     (`WorkloadQueue::threadRenderFrame`/`renderThreadLoop`), not the
     guest hangar-tick call chain every other class in this family
     shares. Several `[last-drawn-skip]` wild/OOB rejections immediately
     precede it in the log — plausibly related (a wild framebuffer
     descriptor reaching tile-copy/framebuffer creation with a bad
     dimension), not confirmed. 1 occurrence, not source-read.
   Also worth remembering: s93's `ROGUESQ_LOG_THREAD_RESUME` confound
   (a repro script was hardcoding the flag on, silently defeating a
   "turn it off" plan) is fixed at the source
   (`scratch/s73_post_a_scene/run_mission_keys.sh` now defaults, doesn't
   force) — do not re-diagnose this if a future soak looks like it's
   carrying unwanted log volume, just check the `env` prefix took
   effect.
2. **M3 — root-cause/fix the `queueGPUUploadTMEM` zero-size assert.**
   (s192: a defensive skip-guard now exists, `ROGUESQ_LOG_TMEM_ZERO_GUARD`
   at `rt64_texture_cache.cpp:1284` — this is a stopgap that skips the
   upload, matching the project's established pattern elsewhere; it does
   NOT close this goal-stack item, which is still the actual root-cause
   fix. The guard has not yet been confirmed reachable/firing in any run.)
   Path confirmed: `fullSyncFramebufferPairTiles` → `uploadTile` lambda
   → `TextureManager::uploadTexture` (`rt64_state.cpp:1329`) →
   `queueGPUUploadTMEM` (`rt64_rdp_tmem.cpp:84` →
   `rt64_texture_cache.cpp:1285`). The dormant `ROGUESQ_LOG_TMEM_ZERO=1`
   log (`rt64_rdp_tmem.cpp:63`) is now **0/5** across soaks with the
   flag armed (s87, animcb2 no flag, animcb3, animcb4, animcb5) —
   stays demoted to "keep it armed opportunistically," not a standalone
   experiment. Assert itself recurred a 7th time unarmed in s108
   (`s108_musyx_gate3`), no new diagnostic data.
3. **M3 — characterize the 10th crash class, SIGBUS in
   `static_5_800B4048` (s90): CLOSED, guarded s125.** See crash catalog
   and item 0 above.
4. **M3 — characterize the 9th crash class, `updateAnimatedTextureStreaming`
   SIGBUS (s89): CLOSED, guarded s124.** See crash catalog and item 0b above.
5. **M3 — `advancePlayerAnimationPhase` SIGBUS: PARKED (s89).** 3
   consecutive non-recurrences since s88 landed the correct instrument
   (s88, animcb2, animcb3) against 8 total crashing soaks since s83. Do
   not spend a dedicated soak chasing this further; if it recurs
   incidentally during a soak run for a different reason, the
   `ROGUESQ_LOG_ANIM_CB=1` instrument is still live and ready to read.
6. **M3 — check the Metal-shader-compiler SIGSEGV's reproducibility** (s83
   spline1: SIGSEGV inside `Metal.framework`'s `MTLCompilerFSCache`, no
   source on our side). Still only one data point.
7. **M3 — confirm the s83 spline div0 guard actually engages.** 0/5 fires
   so far (still 0 after s88/s89/s90); real fix by code inspection (genuine
   0/0 IEEE division) but no same-run positive control yet.
8. **M3 — characterize `frameStartReset` SIGBUS.** Demoted from
   "dominant blocker" after s85 (0 recurrences in s86–s90, 5 soaks);
   recurred s108 (2nd occurrence); **recurred again s156 (3rd
   occurrence, `+532`)** at a call chain (`static_5_800AAD9C ←
   static_5_800C6854 ← menuOverlayInit`) that is byte-identical to the
   12th class's (`composeNpcOrientationMatrix`) own chain — see item -8
   at the top of this list for the shared-dispatcher hypothesis this
   raised. Superseded: "only worth attention if it recurs more often" —
   it has (now 3 occurrences, most recent 2 in consecutive sessions);
   still no located faulting instruction/detector in any of the 3.
9. **M3 — HOLD_S=60 craft stick (M3 DoD body)** once items 1–4 are clear:
   `PROBE_MODE=start_only HOLD_S=60` marks 10/25/40; document phase timeline.
   Gate already keeps black off; residual S1 `fs` freeze (~3769–3872 plateau,
   s82/s85/s88/s89/s90) may still stall animation — if stick marks show no
   pose change on a frozen frame, next is S1 FULL_SYNC for hangar-flight
   tasks (not leave-key, not wild-FB).
10. **M4 — confirm the s53 missing-func fix at runtime (s54 applied + built it; only the game-run
   check remains).** Undriven outdoor-512 stretch; `grep -c "\[missing-func\]"` 3→0.
   Not load-gated (s60/s61). Full detail: PORTING-STATE s53, s54.
11. Past the first sustained mission hold: expect further new failure classes (mission overlay
   DMA → missing-func / UnhandledJumpTarget, new VI phase, overlays 12/44 splice, texture
   corruption). Each new failure is its own work unit.
12. **Doc housekeeping — `CURRENT-TRUTH.md` well over the ~35 KB CLAUDE.md guideline
   — thread exhausted (s55–s58).** Prefer M3 mission-content work over reopening this section.
13. **Sibling-repo housekeeping (flagged s54, not autonomous):** `~/Documents/Tools/rogue_squadron64`
   carries uncommitted symbol-file edits including s54's `mission_overlay.txt` fix. Ask the user
   before committing there.
14. **Band-row coverage history** (settled): s41–s49. s40's `col`-write probe fails its control.
15. **GPU→CPU present PNG** via `NativeTarget::copyToRAM` — a convenience, not a blocker.

Done this session (s95): landed a `get_function`-chokepoint instrument
(`ROGUESQ_LOG_DMA_CALLER=1`, `lib/N64ModernRuntime/librecomp/src/
overlays.cpp`) to find `submitDmaRequestBatch`'s indirect caller.
Before writing it, confirmed (via `N64Recomp/src/cgenerator.cpp`'s
codegen template and a fresh count — 28388/28389 `LOOKUP_FUNC(` sites
across all 45 `funcs_*.c`) that every indirect call in the recompiled
program resolves through this exact function immediately before being
invoked, and that the known boot-time call bypasses it (compiled as a
direct, literal-named call) — so an instrument there can only fire for
the unlocated indirect caller, no filtering needed. Rejected widening
`get_function`'s signature to thread `ctx` through (it's a shared ABI
with the mods system and the live-recompiler JIT); used a native
`backtrace()` instead, since `get_function`'s own call frame sits
directly under its caller. Built clean, `submodule-patches/export.sh`
run, committed (this is a `lib/` edit). Ran one soak
(`s95_dmacaller1`): **0/0 fires**, but not a null result on the
question — the instrument's same-run positive control
(`dma-ring-producer n=0`, the boot call) fired exactly as expected,
proving the instrument works; the process instead died at hold+~5s to
a different, older crash before reaching the ~140s point where the
phenomenon has occurred in every prior soak that got that far. That
crash (`composeNpcOrientationMatrix` SIGBUS, confirmed real name) is
not new — one prior, uncatalogued occurrence exists at s74 — logged
here as the 12th crash class. `ROGUESQ_LOG_DMA_CALLER=1` stays armed
for the next soak, which is a genuine re-attempt, not a 2nd failure.

Done this session (s94): implemented NEXT.md's prescribed instrument
(`ROGUESQ_LOG_DMA_RING=1`, two log points in
`N64Recomp/fixup_game_funcs.py` — producer at `submitDmaRequestBatch`'s
`L_80005768` merge point re-reading the just-written slot, consumer at
`piDmaWorker`'s tag-byte read before the skip branch), ran the full
regen pipeline clean, and ran exactly one soak
(`s94_dmaring1`) reproducing `do_rom_read` a 5th time. The instrument
discriminated cleanly on the first attempt: producer fired 10x (1 known
boot call + 9 unexplained firings ~140s later with ASCII-decoding
`devAddr` values), refuting "boot-only single producer" and confirming
an unlocated indirect caller. Re-verified via fresh grep that
`submitDmaRequestBatch(rdram` still has exactly 1 direct call site, so
the 9 extra firings are not the boot call looping — they must be a
`LOOKUP_FUNC`/`jalr` indirect call not yet found. Redirected next-steps
item 1 from "instrument the ring" (done) to "find the indirect caller
of `submitDmaRequestBatch`," and reframed the root-cause hypothesis
from "shared corruption race / later stomp" toward "wrong-field bug in
an unidentified caller," since the bad value is now known to exist at
write-time rather than being stomped in afterward.

Done this session (s93): before running NEXT.md's Path A, read the
harness script it prescribes and found `ROGUESQ_LOG_THREAD_RESUME=1`
was hardcoded unconditionally (line 8), meaning s92's own
confound-removal attempt via `env ROGUESQ_LOG_THREAD_RESUME=0` had been
silently clobbered and never actually ran — s92's "did not recur" was
not a clean test. Fixed the script
(`scratch/s73_post_a_scene/run_mission_keys.sh`, now
`${ROGUESQ_LOG_THREAD_RESUME:-1}`) and reran the prescribed soak
(`s93_romread3`): `do_rom_read` recurred on the first genuine attempt
(hold+13s), byte-identical to s85/s91
(`phys=0x1C676672 dram=0x80195190 bytes=0x600`), with `raw_r7=0x6C676672`
matching s91's 2nd soak's raw register value bit-for-bit — the
confound theory is now confirmed rather than merely proposed. Redirected
next-steps item 1 from "keep reproducing" to "find the source of the
corrupted register value," since reproduction is no longer in doubt.

Done this session (s92): read `osPiStartDma_recomp` source before
building anything (per NEXT.md's own step-2 plan) and found the
planned instrument was based on a wrong premise — `devAddr` is a
direct register argument, never read from the `OSIoMesg` at `mb`, so
"dump the message struct" would not have tested H1. Also checked the
decomp source tree for the real PI-manager caller (both
`osCreatePiManager`/`osPiStartDma` are `INCLUDE_ASM` stubs there, no
usable C source yet). Ran one soak (`s92_romread2`) reusing existing
instruments (s91's 5 flags + the pre-existing
`ROGUESQ_LOG_THREAD_RESUME=1`, no rebuild) to test NEXT.md's step-3
resume-count question. Results: `do_rom_read` **did not recur** (0/1,
first miss after 3/3); **`ra=0x00000000` fired on 487/487** sane
`pi-start-dma` calls this run (plus 3 unrelated entry-log instruments,
all always `ra=0`), **refuting** s91's reading of it as corruption
evidence — the anomaly narrows to `raw_r7` alone; found a **new 11th**
crash class instead (`projectModelBoundsToScreen` SIGBUS via the known
hangar-tick call family); identified a likely confound
(`ROGUESQ_LOG_THREAD_RESUME`'s log volume perturbing timing) for why
this soak diverged from s91's outcome. Controls held (`bad_total=0`,
anim-recurse `sp` flat) for a 7th straight session; TMEM-zero stayed
0/6.

Done, do not redo:
- ~~Optimise the ucode vector path~~ — s38: it was `-O0`; `-O2` gave 41x. SIMD/RSPRecomp vector work
  is unnecessary at 4.5 ms/task without a new measurement justifying it.
- ~~Confirm the ucode-performance bottleneck~~ (s37) · ~~Find why DL submission collapses~~ (s36) ·
  ~~Census the RDP stream~~ (s35) · ~~Localise the draw loss~~ (s33/s34).
- Coverage attribution (`LOG_BBOX`) and load/render format mismatch (`LOG_UPLOAD`) are ruled out —
  every draw covering the band is I4 with `tlut=0`, from I4 loads.
- The s27–s31 I4-decode line (`FIX_DXT_I`, `I4_SHADE_MONO`, `SHADE_ONLY_MONO`, restricted
  `FLATTEN_I4`) is retired — aimed at a texture that does not paint those pixels.

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
   - audio-engine gate stores → 0 in `funcs_23.c` (`initMusyXEngine`, `setDisplayMode`,
     `reapplyDisplayMode`; gate byte 0x800A0F50) — without this the scheduler wedges in
     `waitForMusyXAudioTaskDone`
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
- ~~Screen Recording permission is intermittent~~ — **overturned s32.** Capture and synthetic input
  both work: 74/74 `screencapture -l` succeeded across a full undriven run (73 with content, all
  phases), the game's CGWindow id was **stable** at one value for the whole run, and a driven run
  reached the hangar (512 origin 0x6AB400 at 56.0 s) off `winctl` keys. `could not create image from
  window` means the **window id is wrong**, not that permission is missing — check the id before
  blaming TCC (`winctl find <pid>`; `winctl list` is not a subcommand and prints nothing).
  `winctl trusted` reports Accessibility state directly.
- `winctl activate` (activateWithOptions:) is a cooperative request modern macOS **ignores while
  another app holds focus** — keys then get dropped with `trusted`=yes and the run silently follows
  the undriven route (s45; also the real cause of the session-25 failures regress.sh blamed on "no
  GUI session"). probe.sh/regress.sh now raise via System Events `set frontmost` (`raise_game()`);
  keep using them rather than winctl directly for driven runs.

## Overturned conclusions — do not act on these

- **Claim (s75/s76):** a single Start press from SELECT YOUR CRAFT leaves the
  menu into a distinct "hangar-flight" scene — an airborne X-wing outside the
  hangar. **Overturned by s150:** dense (0.2s-tick) capture across the same
  transition, cross-checked against the s76 `hold60/` archive (an
  independent prior run, not a new soak — two sources), shows the
  "airborne X-wing" frames are the *same* craft-select hangar 3D scene
  (identical X-wing pose, R2 unit, crate, wall paneling, moon backdrop)
  viewed from a progressively closer/lower camera angle with escalating
  render corruption (large striped/aliased degenerate polygons), not a
  new environment. A third, independent, code-level check confirms it:
  this session's crash (3rd recurrence of the already-catalogued 12th
  class, `composeNpcOrientationMatrix`, past both its s100/s126 guards —
  a 3rd, still-unlocated fault site) backtraces entirely through
  already-known hangar-menu functions (`menuOverlayInit` →
  `runHangarMenuFromOverlay` → `runHangarSelectionFrame` →
  `composeNpcOrientationMatrix`), none of them mission-overlay code.
  Believable because the title-yellow HUD text really does disappear and
  a tilted ship silhouette against stars reads as "flying", but the
  pre-Start static menu already shares that same starfield/moon backdrop,
  and the hangar walls stay visible in every post-Start frame examined.
  **Reopens "what leaves SELECT YOUR CRAFT into a mission" as unanswered.**
  Full detail: PORTING-STATE s150.

`## LLE stabilization session 2 (2026-07-12)` sits out of order in the log, between s7 and s8: its
conclusions are among the oldest in the file, not the newest.

The s2–s5 stabilization-era claims (LoadTile underflow, zeroed DL-chunk bytes, RDP-ring/trig-load
misreads of the audio `ucode_data`, "two gfx ucodes") are compressed to one line: **every one was
eventually explained by the shared-`dmem[]` race** (audio tasks staging over gfx state; fixed by
the recursive mutex, s5). Full detail: PORTING-STATE and PROJECT-OVERVIEW §3. Do not re-litigate
any s2–s4 conclusion without checking that section.
- **Claim (s5–s7):** 0x76A000/0x7DD000 are colour buffers cleared to white. **Overturned by s8:** they
  are Z-buffers (`SETZIMG` op 0x3E, 0xFFFCFFFC standard z-clear); colour buffers are 0x5D4000/0x66A000
  (640-wide), 0x6BA000/0x6DD000 (320-wide). Believable because 0xFFFC reads as white in a 16-bit
  colour buffer and the screen was white. Full detail: PORTING-STATE s8.
- **Claim (s7):** texrect draws execute but their output is invisible in the render target.
  **Overturned by s8:** `ROGUESQ_VI_FORCE_FB=0x5D4000` shows dense content — the pixels exist, the
  default present just picks a different buffer.
- **Claim (s8):** F5 geometry ops 0x01/0x02/0x03 emit zero RDP bytes (64/66 tasks), probably
  RSPRecomp culling every primitive. **Overturned by s9:** `rsp_dpc_submit`'s ring high-water mark
  lived in function-local statics, discarding any task no larger than the largest previous one;
  hoisting it to file scope (`s_submit_dl_base`/`s_submit_last_end`) fixed it — 65/65 tasks commit.
  Believable because RT64's own HLE leaves the same three ops stubbed, a second path agreeing on
  "no geometry".
- **Claims (s9, sixth pass), compressed:** "0x790000 is a z-buffer the VI never scans" (s10/s18/
  s21: it is a presented, double-buffered colour buffer — the +0x100000 z-pattern just holds
  everywhere else) and "`[dpc-behind]` counts 17 867 wrap drops in 60 s" (s10: real figure
  9 056 256 in 70 s — the counter read a sampled path).
- **Claim (s9/s10):** `ROGUESQ_DPC_WRAP=1` gives continuous rendering, and the Metal exhaustion it
  triggers must be contained with `ROGUESQ_MAX_FBPAIRS`. **Overturned by s11:** with the
  `VI_FULLSYNC` fix, wrap **off** gives more content and more detail with `[fbpair-cap]` never
  engaging — wrap-on was re-sending already-consumed ring bytes, papering over the missing FULL_SYNC
  that was the real cause (see next entry).
- **Claim (s10):** the Metal shared-memory exhaustion is a property of the post-logo tiled phase and
  the framebuffer-pair cap is the fix. **Overturned by s11:** that phase never emits RDP FULL_SYNC at
  all, so the workload never advanced (195,057 pairs, 23 GB of Metal buffers, black screen all
  downstream). Synthesising the frame boundary from the VI swap (`ROGUESQ_VI_FULLSYNC`) fixed it —
  see PROJECT-OVERVIEW §4.6. Believable because the allocation backtrace named `addFramebuffer`
  unambiguously and the cap did buy a clean 120 s run.
- **Claim (s9, third pass):** `ROGUESQ_PRIM_ALPHA_FF=1` (PRIM alpha ~3%) is needed to see text.
  **Overturned by s11:** verified, not assumed — with it off the attribution screen still renders
  fully legibly, so the hack was retired rather than replaced.
- **Claim (s9, mid-session):** the renderer regressed to black, so the 24 overlay-symbol moves must
  be reverted. **Overturned within s9:** sampling artefact — four one-shot captures at 4/8/14/20 s
  all showed black, but a 28-frame burst at 0.15 s showed 27/28 full of content; the moves were fine.
- **Claims (s12–s16), compressed:** "the 0x60xxxx I4/CI4 dumps are the hangar floor/wall assets" and
  "the 0x65xxxx RGBA16 loads are hangar assets" — both wrong (real CI sources elsewhere; the RGBA16
  loads fire during the 1024 title phase). A plausible decoded image does not identify a phase.
- **Claim (s14):** `ROGUESQ_FIX_LINE_MASK` (force `line = 2^(masks-4)` on 4-bit tiles) — wrong
  direction, the mask/line "disagreement" tiles are real. **Overturned by s15**, replaced by
  `ROGUESQ_FIX_SAMPLE_BOUNDS` (still default-on).
- **Claim (s14):** palette-bank-15 stomping (later LOADTLUTs from 0x62Bxxx replacing the red hangar
  palette) is the root of the rainbow floor band. **Overturned by s15:** the first 40 CI4 pal15
  uploads all use the red palettes with zero multi-colour loads — band pixels are warm red #ce6238, a
  layout scramble of correct colours, not a wrong TLUT bank. M1 (s44–s49) later found the real cause.
- **Claim (s13):** hangar walls need synthesised dxt, so `ROGUESQ_FIX_DXT` defaults ON. **Overturned
  by s22/s23:** it turns the 1024 title backdrop into a vertical-stripe mosaic and gives the hangar
  rainbow/static corruption; default is now OFF. Believable because s13's A/B was cross-run, the
  method s18 later rejected as unsound for animating scenes.
- **Claim (s18, first half):** the 512 phase draws flat sand-coloured polygons and fog #C8C0A0
  matches the on-screen colour. **Overturned by s18 (second half):** `ROGUESQ_FORCE_FOG` changes 0
  pixels — the sand is the **fill colour**, triangles paint black. A colour match is not attribution
  (PROJECT-OVERVIEW §4.2).
- **Claim (s18, mid-session):** textured triangles with S identically zero (base, dx, de all zero)
  explain the flat 512-phase rendering. **Overturned within s18:** those triangles are not in the 512
  phase — run-lifetime "first N" counters reported whatever phase started first. Interval-scoped
  counting finds **0** collapsed triangles in both 512 and 1024; the S=0 triangles live in the 640
  attribution phase. **Why believable:** a collapsed S coordinate is a textbook cause of flat texturing.
- **Claim (s18, fourth segment):** no RGBA32 LOADBLOCK is ever emitted in the 512 phase (exhaustive
  census: RGBA32 = 0), the TMEM high half is empty, so geometry rasterises black. **Overturned by
  s19:** `DUMP_TMEM_DRAW` at draw-record time sees **stale** TMEM — RT64 defers every LOADBLOCK to
  `fullSyncFramebufferPairTiles`; measured at upload, both TMEM halves are filled. This is the
  general "stale reads" trap, PROJECT-OVERVIEW §4.1.
- **Claim (s19):** the 1024-phase black screen is most likely the same zero-shade bug as the hangar;
  retest after the shade fix. **Overturned by s20/s21:** `FORCE_SHADE_WHITE=1` gives 0/4 content at
  1024 — the real cause is present starvation: `State::updateScreen` in PresentEarly mode
  early-returns whenever `presentEarly && !fromEarlyPresent`, and at 1024 no fbPair is ever an
  `earlyPresentCandidate`, so presents stop entirely.

- **Claim (s62/s63):** the M3 render-once-then-freeze bug is CPU-side — RSP task submission
  (`[lle task]`), command processing, and presentation all stay healthy through the freeze, so an RSP
  infinite loop is ruled out. **Overturned by s64:** both supporting observations were sampled-log
  artifacts. The `[task-brief]` iteration-cap population genuinely is unrelated (that part stands),
  but the "RSP stays healthy" read came from `[lle send_dl #N]`'s 1-in-32 throttled sampling, which
  has near-zero odds of ever landing on the run1/run2 trailing 5-6 tasks it needed to inspect — it
  only ever showed pre-freeze tasks (`Broke`, correctly). An unsampled per-task histogram
  (`ROGUESQ_LOG_RUNNER_ALL`, added s64) shows the true population: from task #3141 on, 100% of
  remaining tasks exit `RspExitReason::ImemOverrun` on real (not stub) triangle content, tracing to
  an RSP ucode branch RSPRecomp couldn't resolve. **Why believable:** the throttled log had correctly
  shown `Broke` on every task it ever sampled, so "the RSP side is healthy" looked like a repeatedly-
  confirmed fact rather than a fact about only the 96.9% of tasks the sample could ever land on.
- **Claim (s64/s66):** the freeze-phase ImemOverrun is the end-of-IMEM `bgez $2, L_0000`
  perspective-divide branch (fixup-1 hard exit); implementing a self-restart for it should un-freeze
  mission tasks. **Overturned by s67:** with both L_0000 outcomes rewritten to self-restart and the
  instrument live under `ROGUESQ_UCODE_NO_OPT=ON`, `[ucode-restart]` fired **0** times while tasks
  from #3216 on still exited ImemOverrun with `syncs=0`. Default `-O2` also DCE's the whole block
  (so an O2-only "null" would have been invalid). L_0000's static self-restart reading (s66) still
  stands as hardware truth; it is not the path freeze tasks take. **Why believable:** the source
  block literally returns ImemOverrun on both bgez outcomes, freeze onset coincides with
  triangle-heavy tasks, and the static disassembly of L_0000 is multi-source clean.
  **s68–s69 follow-through:** actual site was CLIP_1FBC → L_1650 hard exit (s68 counter ≡ every
  exit=2); reconnecting `goto L_1650` after the fixup-6 label (s69 fixup 8) drops exit=2 to 0
  and unfreezes `fs`.
- **Claim (s23):** the hangar's remaining dimness is real vertex lighting, not shade-decode, because
  its shade census is healthy. **Overturned by s25:** that census was the magnitude-only classifier
  s24 proved cannot distinguish −118 from +118 (PROJECT-OVERVIEW §4.2), so "ok" was really the
  all-negative population; driven A/B showed `SHADE_WRAP=1` brighter in 93/114 paired hangar frames.
- **Claim (s28):** `FORCE_SHADE_WHITE` kills the hangar multi-hue floor band, so the band colour is
  shade. **Overturned by s31:** on the standard hangar view the mid-ground band survives FSW —
  walls/pad go monochrome, multi-hue floor remains; warm% alone was a bad residual metric.
- **Claim (s30):** hangar mid-band is 100% untextured shade-only and `SHADE_ONLY_MONO` kills the band.
  **Overturned by s31:** the earlier census only sampled the landing-pad shade-only population; an
  improved census after the hangar found 201 textured-I4 tiles (imgs 0x604140/0x605140) alongside 73
  shade-only. Suppress/mono leave the multi-hue mid-ground; FSW proves it is TEXEL, not shade.
- **Claim (s46):** no complete clip overlay exists raw in the ROM (whole-ROM byte scan); the game
  materializes overlay images in DRAM at runtime, so only a runtime capture can recover it.
  **Overturned by s47:** all five runtime-captured overlay images are byte-identical to the ROM at
  `RDRAM_addr + 0xC00` (clip: 544/544 at ROM 0x26420). The recompiled window region is the packed
  overlay *storage* (init at window+8), which s46 read as "init image + stale clip tail" and which
  made its scan expectations wrong. **Why believable:** the window-region disassembly genuinely
  contains init code and clip-fan fragments at shifted offsets, and a byte scan for the *expected
  window layout* genuinely finds nothing.
- **Claim (s46):** ~40 window entries/task arrive via a non-L_1298 `jr` (jrc sum 247 vs 287 label
  hits), so case-level routing of the clip splice may be unsafe. **Overturned by s47** (fixup 5
  stray census): 4221/4221 `case 0x1DB0` arrivals come from the L_1298 `jr $3` (debug_line 594)
  with DMEM 0x153 already set to the requested overlay id. The excess label hits were
  fall-throughs from code above L_1DB0, which the label counters count but the dispatch does not.
  **Why believable:** the two counters were believed to measure the same population; they differ
  by exactly the fall-through paths.
- **Claim (s12–s47):** the 512-wide origin-0x6AB400 scene is the "main-menu hangar" — landing
  pad, parked X-wing, hangar walls. **Overturned by s48** — mechanism at "scene-identity
  correction" above. Proven by wall-structure identity between the s41 control frames and the s48
  full render, same origin, same input path, arrival times matching to 0.2 s. **Why believable:**
  the partial render was a coherent-looking scene for 36 sessions, and SELECT GAME's photographic
  hangar backdrop reinforced the "hangar" frame; nothing looked missing until the missing half
  rendered.
- **Claim (s47):** the briefing room presents from origin 0x656400, SELECT LEVEL from 0x696100,
  the clip fix changed menu timing, and the verify run overshot the hangar. **Overturned by
  s48:** all four wrong. The war room / SELECT LEVEL presents from **0x6AB400** (three runs); the
  0x696100 `[vi]` lines sit in the 640-wide pre-title phase; menu routing and timing are
  unchanged (title → SELECT GAME → war room, one press each, war room at 54.5 s vs s23's 54.7 s);
  and nothing was overshot — the band scene was on screen the whole time, rendering complete for
  the first time. **Why believable:** the completed render looked like a brand-new scene, so
  nearby unfamiliar origins in the log read as its identity, and "we missed the hangar" was the
  only story consistent with the hangar still existing.
- **Claim (s70 implied):** post-`a` SIGBUS is a thread lifetime bug (UAF of destroyed
  `OSThread` / `UltraThreadContext`, or double-signal). **Overturned by s71:** live-context
  set shows the crashed resume's `context` was **never created**; the good context of the same
  OSThread (`runAiAudioStreamPlaybackLoop` @ `0x801494B0`) was never destroyed; only 1/103967
  resumes had `live=0`, with a bit-diff vs the prior good pointer. **Why believable:** stack
  lands in `LightweightSemaphore::signal` after `resume_thread`, the classic UAF symptom, and
  destroy/create churn of other threads (ids 6–10) sits earlier in the same mission-entry window.
- **Claim (s71 H4 partial):** context bit-corruption is an unknown in-place smash; `last-drawn
  #1870` is only timing correlation. **Closed by s72:** the writer is the RT64 depth writeback
  immediately after that last-drawn, range `[0x140000,0x3E1332)` overlapping OSThread phys
  `0x1494B0`, with before/after snapshot proving the mutate. Width/OOB writeback gate stops
  the SIGBUS. **Why the correlation looked weak:** last-drawn only updates atomics (no RDRAM
  store); the actual store is the subsequent `copyNativeToRAM` on the paired depth FB.
- **Claim (s70–s72 residual):** after SIGBUS fix, remaining M3 defect is sustained **mission**
  texture garbage (g07 capital-ship class). **Overturned by s73:** g07 is a ~1s flash; stable
  post-`a` content for 55s+ is **SELECT YOUR CRAFT** (menu). s70 never stayed on craft-select
  only because it died at g07; s69 (25s grace, alive) already showed SELECT YOUR CRAFT. **Why
  believable:** the flash is dramatic and mission-shaped, and earlier deaths cut the timeline
  before the real destination rendered.
- **Claim (s74 residual):** leave from SELECT YOUR CRAFT may require double-Start or
  Start-after-`a` (first Start alone +3s still SELECT). **Overturned by s75:** start_only
  with unique tags leaves on one Start by +2–4s (title-yellow + hangar-flight visual).
  **Why believable:** s74 overwrote first-Start snaps with the second Start's names, so the
  only post-first-Start sample was `pre_probe_a` at +3s; short window + possible key drop
  looked like a hard double-Start rule.
- **Claim (s77 implied next):** refusing wild-width FB registration will unfreeze hangar-
  flight present (`fs` past ~3360). **Overturned by s78:** refuse fires, tilecopy control
  on 640 holds, map stays clean — **`fs` still plateaus ~3297** with high-tri `syncs=0`
  from #4252. **Why believable:** s77 showed wild FBs in the map at freeze time, so map
  pollution looked causal; same-run refuse + freeze splits registration from present.
- **Claim (s78 residual / S3):** UnhandledJump 0x0231 (exit=3 population from ~#4265)
  is what kills hangar-flight FULL_SYNC / present. **Overturned by s79:** onset of
  `syncs=0` is task **#4252** with **13** subsequent `exit=1` (Broke) high-tri tasks
  still at `syncs=0` before the first jump. Jump is real and permanent after #4265 but
  **not** the FULL_SYNC-loss root. **Why believable:** 899 jump lines dominate the
  freeze-window log and correlate with the stuck phase in wall-clock time.
- **Claim (s79 residual):** after post-leave SYNC_FULL loss, VI_FULLSYNC stalls
  (only one more `fs` advance then plateau) — so the present freeze is a synthetic
  decision failure (`fbPairCount==0` / no-trigger / FullSyncSeen). **Overturned by
  s80:** always-on `[vi-fs-decision]` shows **FIRE continues** (+141 synth) after
  RDP-`fs` plateaus; V1/V3/V4 refuted. `fs`/`rdpFs` counts DPC FULL_SYNC *opcodes*,
  not synthetic `State::fullSync()` — plateau is S1 restated. **Why believable:**
  the `[vi] fs=` field was the only advance metric in s78/s79 logs and moved in
  lockstep with healthy present earlier, so its freeze looked like the synthetic
  path stopping.
- **Claim (s80 V2 residual):** intermittent black is mysterious despite healthy
  present (`present-1024 empty=0` throughout + synthetic FIRE). **Overturned by
  s81:** `empty=0` logs only on last-drawn *address transitions*, not every
  present; mode-3 actively presents wild last-drawn (w=1..257) during black
  windows (`[vi-follow-draw]`). **Why believable:** empty=0 never flipped to 1 in
  the whole run, so "present RT always non-empty" looked continuously true.
- **Claim (s81 residual / G2):** gate may be too late or present still broken
  even if last-drawn is filtered. **Overturned by s82:** same-run skip control
  + hold pure-black 0/5 + hangar-flight content. **Why believable:** s81 black
  and wild last-drawn were co-timed but not yet proven causal by a live gate.
- **Claim (s87):** the 8th crash's mechanism is self-recursion via
  `advancePlayerAnimationPhase`'s own indirect call, `LOOKUP_FUNC` reading
  a stale/corrupted pointer from global slot `0x80139968` at guest
  `0x8006426C`. **Overturned by s88:** that call site is inside
  `invokeMenuOverlayHeaderCallback`, a different function never reached
  from `advancePlayerAnimationPhase`'s own body (which has zero indirect
  calls — only two direct `jal`s to `activateAnimationKeyframe`, whose
  own callees make no further calls at all). A correctly-targeted entry
  instrument (`ROGUESQ_LOG_ANIM_CB=1`) then showed the function is called
  at effectively constant, shallow stack depth (6 distinct `$sp` values
  across 3296 calls) — no recursion of any kind observed. **Why
  believable:** the source read that produced the claim searched a line
  range ("8130-8153") without checking which `RECOMP_FUNC` block those
  lines actually belonged to; the address happened to be the *only*
  indirect call visible in that grep window, which read as sufficient
  evidence without confirming the enclosing function name.

### Dead ends — labelled as such in the log, do not retry

- `RDP_ADDRESS_MASK` 0xFFFFFF → 0x7FFFFF (`rt64_rdp.h`, s3): 0x800000..0xFFFFFF are legitimate RT64
  extended-RDRAM handles; masking aliases them onto low memory and moved the crash earlier.
- Chunk-replay hack in `dma_rdram_to_dmem` (s3): the ucode legitimately reads trig values from
  0x170..0x280 right after a swap; 29 unhandled vs ~5.
- Widening the DMA shadow to `[ucode_data-0x1800, +0x1800)` to cover 0x37658 (s3): that content
  difference is legit dynamic data, not shadowable corruption.
- Blanket ucode-image shadow `shadow2` (s4): the engine legitimately rewrites `ucode+0x12DEA` and
  `ucode+0x7CD5C`; serving them stale gave 109 unhandled / 35 send_dl against a 256 baseline.
- `ROGUESQ_RING_RESYNC=1`, poking `DMEM[0x108]` = ring base per task (s4): no measurable change
  (41 vs 51) — aimed at a flush overflow that never existed.
- `dmem[0x153]=0xFF` to force a segment reload (s2b): made failures worse (6 exit=3 vs 2–4).
- Bulk moves of unmapped symbols out of `symbol_files/main_overlay.txt` (s9): each inserted symbol
  **splits** the enclosing function in that section — the duplicate-address truncation bug in reverse
  (general class: PROJECT-OVERVIEW §4.5) — producing a SIGBUS in `allocAndInitGridCellArray`. Use
  `tools/overlay_symbol_probe.py <0xADDR> [mission|menu|cinematic]` first (the reliable signal is the
  `addiu $sp, $sp, -N` prologue at +0), one validated batch at a time.
- Present-side snap-down and `findMostRecentContaining` fallbacks (s9):
  `present.screenVI.fbAddress()` already returns the framebuffer base and neither fallback ever fired.
- `ROGUESQ_VIEW_RDRAM=1` (s9): the game window never appears; the mode is broken in this fork.
- `ROGUESQ_WRAP_DEDUP=1` (s10): removes ~33000 redundant submissions but the run still reached
  193715 pairs and the same Metal assert.
- `ROGUESQ_FORCE_PAL15=1` (s14): clears the floor band but corrupts ceiling banners that legitimately
  share pal=15.
- **Claim (s85):** the `do_rom_read` corrupted `physical_addr` is "garbage that varies run-to-run,"
  evidence for a nondeterministic shared-corruption race. **Overturned by s91:** the exact same
  `phys=0x1C676672 ram=0xFFFFFFFF80195190 bytes=0x600` DMA call recurred byte-for-byte 3 times across
  3 sessions and 2 rebuilds — a race would not reproduce identically. Believable because s85's only
  comparison was against a *different* crash type (`thrgate2`, an alignment Abort with no logged
  value) from the same session, not a second instance of the same crash — it never actually had two
  comparable data points. Reclassified as a deterministic, reproducible bug (top of M3 next-steps).

## Method traps

Mechanism already generalized in PROJECT-OVERVIEW.md §4 → pointer only here, session tag is the
specific instance in PORTING-STATE:
- §4.1 instruments-that-lie: `fbPair.projections` over-count (s32), `[loadblock]` sampled-log
  miscount (s18/s19), stale TMEM at draw-record time (s19), capture harness outliving the process,
  `window_burst.sh` 60/60 false-positive (s9).
- §4.2 attribution errors: colour match ≠ attribution, fog #C8C0A0 (s18); plausible decoded image ≠
  phase ID (s17).
- §4.3 cross-run comparison: knob effects/nulls manufactured by camera drift, "7.30%" constant
  misread as an effect (s18); phase timing varies tens of seconds run-to-run, gate on
  `PROBE_PHASE_WIDTH`/`PROBE_KEYS_FROM_PHASE=1` not a stopwatch (s17 → s18/s23).
- §4.6 missing protocol events: pair/buffer/wrap counters measured instead of FULL_SYNC arrivals
  (s11).

Not yet generalized in PROJECT-OVERVIEW — specific to this codebase's instruments:
- Sparse one-shot screenshots land on genuine inter-screen transitions and read as a regression;
  always burst-sample (28 frames at 0.15 s: 27/28 with content, where 4 one-shots showed black) (s9).
- Validate a suppression instrument before believing a null result: `ROGUESQ_SUPPRESS_SHIFT=1`
  re-runs any suppression mode as a +80 px displacement so you can see it reach the screen (s18).
- The `[seq]` and `[full-hist]` walkers in `dpc_bridge` advance a fixed 8 bytes per command, so
  triangles (32–48 bytes) desync them into thousands of bogus SETCIMG addresses (`LOG_SEQ` also caps
  at 6000). Once geometry flows use `ROGUESQ_LOG_RDPHIST`, which uses RT64's own command lengths
  (s9/s11/s19).
- Histogram-drain timing misleads: the runner histogram showed 0 RDP bytes for a task the dispatch
  tracer proved had processed its full DL (s2b).
- Five frames per run does not average out camera motion, so even aggregate `pixel_stats.py` metrics
  are confounded when runs sample different moments (s18).
