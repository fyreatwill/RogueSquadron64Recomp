# Rogue Squadron 64 Recomp — current truth

Front matter for `PORTING-STATE.md`, which is chronological and contains superseded conclusions.
New here, or back after a break? Read **`docs/PROJECT-OVERVIEW.md`** first — what the project is, how
the four layers fit together, and the hurdle classes that have cost the most time.
Session tags: `s1` = 2026-07-09/10 build + overlay work, `s2`–`s9` = the `## LLE session N` headings,
`s10`–`s32` = the `## Session N` headings.

## Current truth (as of session 83)

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
  (width>1280 or past 8MB — same family as s72 writeback; does **not** unfreeze present).
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
| ~93 s | 640 | transition — **process dies here** (undriven-era observation) |

Menu state machine (s48, three driven runs; extended s50; post-`a` path s73; Start path s74/s75;
hold attempt s76):
title —start→ SELECT GAME —start→ war room / SELECT LEVEL —start→ **AVAILABLE CRAFT**
(war-room craft holograms; footer "PRESS [A] FOR LEVEL DESCRIPTION"). From AVAILABLE CRAFT,
`a` does **not** show a level description card (s61–s69). With process alive 65s post-`a`
(s72/s73): **black ~5s → ~1s mission-shaped capital-ship flash (texture garbage) → stable
SELECT YOUR CRAFT** (hangar pad + full X-wing, "PRESS [A] FOR CRAFT DESCRIPTION", multi-hue
floor garbage; camera orbits). From SELECT YOUR CRAFT: **`a` no-ops** (s74); **single Start
is enough** to leave into hangar-flight (s75/s76: title-yellow ~13k → 0 by +2–4s; airborne
X-wing). VI stays on the 0x6AB400/0x656400 pair — origin cannot name these scenes (s48).
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
framing (s91).**
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

## Next steps, in order of expected value (s91)

1. **M3 — root-cause the deterministic `do_rom_read` corruption (was
   item 4, now the top-priority lead — s91 turned it from "unproven
   race hypothesis" into a 3x-reproducible bug).** The crash is a fixed
   DMA call: `mb≈0x80111270 dram=0x80195190 size=0x600 pri=1 dir=0` on
   thread id=1 (the PI DMA worker), always right after a `[thr-resume]
   tag=swap` onto that thread, with `ctx->r7` (devAddr) **and**
   `ctx->r31` (return address) both reading as unpopulated/garbage
   together. Next probe: log the OSMesgQueue send side for this specific
   `mq`/`mb` (find the `osSendMesg`/`osJamMesg` call feeding the PI
   manager's message queue — `librecomp`'s PI manager thread, search
   `piDmaWorker`/`osPiMgrGetHandle` context in `lib/N64ModernRuntime/
   librecomp/src/pi.cpp`) to see whether the *enqueued* `OSIoMesg` at
   `mb=0x80111270` is itself already garbage (an uninitialized/reused
   guest struct — points to a guest-side or overlay-load bug) or valid
   right up until `piDmaWorker` dequeues and reads it (points to a
   host-side context-restore bug specific to this thread). Also worth a
   cheap positive check first: dump guest RDRAM at `mb=0x80111270` for
   the full `OSIoMesg` struct (`hdr`, `devAddr`, `dramAddr`, `size`) at
   the moment of the bad call — if `devAddr` in RDRAM itself already
   holds `0x6C676672`-shaped garbage, the bug is upstream of
   `osPiStartDma_recomp` entirely (whoever built this `OSIoMesg`), not
   in the register-read path this session instrumented.
   `ROGUESQ_LOG_DMA=1` already logs `[pi-start-dma]` with `mb`/`ra`/
   `raw_r7` — reuse the same soak command from s91 (`animcb5`/`animcb6`
   commands, PORTING-STATE s91) since the bug reproduces on demand at
   ~hold+11-13s; no new build needed unless adding the OSMesgQueue-side
   log.
2. **M3 — root-cause/fix the `queueGPUUploadTMEM` zero-size assert.**
   Path confirmed: `fullSyncFramebufferPairTiles` → `uploadTile` lambda
   → `TextureManager::uploadTexture` (`rt64_state.cpp:1329`) →
   `queueGPUUploadTMEM` (`rt64_rdp_tmem.cpp:84` →
   `rt64_texture_cache.cpp:1285`). The dormant `ROGUESQ_LOG_TMEM_ZERO=1`
   log (`rt64_rdp_tmem.cpp:63`) is now **0/5** across soaks with the
   flag armed or not (s87, animcb2 no flag, animcb3, animcb4, animcb5) —
   stays demoted to "keep it armed opportunistically," not a standalone
   experiment.
3. **M3 — characterize the 10th crash class, SIGBUS in
   `static_5_800B4048` (s90).** Did not recur in s91's two soaks.
   Instrument (`ROGUESQ_LOG_HANGAR_ENTRY=1`) stays armed and ready; no
   dedicated soak needed, fold into whatever soak runs next.
4. **M3 — characterize the 9th crash class, `updateAnimatedTextureStreaming`
   SIGBUS (s89).** Also did not recur in s91. Instrument
   (`ROGUESQ_LOG_ANIM_TEX_STREAM=1`) stays armed.
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
8. **M3 — characterize `frameStartReset` SIGBUS if it recurs.** Demoted
   from "dominant blocker" after s85: 0 recurrences in s86–s90 (5 soaks).
   Only worth dedicated attention again if it reappears; do not gate it
   speculatively without a faulting instruction (no existing detector,
   unlike thr-resume).
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

Done this session (s91): ran the batched-instrument soak NEXT.md
prescribed (`animcb5`) with all 5 flags armed including the
correctly-named `ROGUESQ_LOG_DMA=1` — crashed on `do_rom_read`
(`phys=0x1C676672 ram=0xFFFFFFFF80195190 bytes=0x600`), **byte-for-byte
identical** to s85's `romread1` run from 6 sessions earlier. Read
`osPiStartDma_recomp` source to confirm the exact mechanism
(`devAddr = ctx->r7 | rom_base`, a live register read), added
`[pi-start-dma]` logging (return address + raw r7 + DMA args) at that
call site (`lib/N64ModernRuntime`, exported + committed), rebuilt, and
ran a 2nd soak (`animcb6`) — **crashed a 3rd time with the identical
DMA call**, additionally showing `ra=0x00000000` and a `raw_r7` with a
completely different bit shape from every real call's kseg1 pattern.
Three independent byte-identical occurrences **refutes** s85/s86's
"random race, varies run-to-run" framing and **establishes** a
deterministic, reproducible bug — reclassified as the new top-priority
lead (next-steps item 1) instead of "shared corruption race." 9th/10th
crash classes did not recur; `[anim-recurse]`/`thr-resume bad=1`
controls held for a 6th straight session. TMEM-zero stayed 0/5.

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
