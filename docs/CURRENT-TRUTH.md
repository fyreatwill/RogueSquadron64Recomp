# Rogue Squadron 64 Recomp — current truth

Front matter for `PORTING-STATE.md`, which is chronological and contains superseded conclusions.
New here, or back after a break? Read **`docs/PROJECT-OVERVIEW.md`** first — what the project is, how
the four layers fit together, and the hurdle classes that have cost the most time.
Session tags: `s1` = 2026-07-09/10 build + overlay work, `s2`–`s9` = the `## LLE session N` headings,
`s10`–`s32` = the `## Session N` headings.

## USER DIRECTIVE (2026-08-04, human-set — overrides Next-steps ordering until satisfied)
Priority order for upcoming iterations, set after the 300-session review:
1. **Maintenance** (Step 0 of ITERATION.md triggers it at 60,000 bytes): compact per the Maintenance
   section of tools/agent/ITERATION.md; a >=200-net-line shrink counts as ADVANCED. Compaction history:
   s295/296 (562,666→59,811 bytes), s299 (61,293→47,105), s305 (this pass — collapsed this section's
   duplication of the Next-steps items -166..-161 narrative below into a pointer). 35 KB remains a
   stretch target, not a hard floor — the "Current truth" env-var/timeline prose and the Regeneration
   section's Standing warnings stay intact deliberately; both are used every iteration for phase-gating
   and build commands.
2. **M5 audio de-stubbing**: design doc DONE (s298, `docs/M5-AUDIO-PLAN.md`) — a 6-step incremental
   de-stubbing sequence, one validation soak per step. Steps 1-3 DONE and validated clean (s300/301).
   Step 4 (reversing each of the 3 audio-gate-byte force-zero sites, one per session) is IN PROGRESS:
   `initMusyXEngine`'s site reversed s302, but s306's reachability counter (2 soaks) found
   `initMusyXEngine` is never actually called — s302's validation is retroactively meaningless (see
   Overturned Conclusions), and gate=1 has still never been exercised by any soak. `setDisplayMode`'s
   site attempted s303 and again s307 (with s306's gate-consumer tags live): both reproduced an
   identical deterministic full-boot hang (39 RSP tasks, stuck at VI width 320), re-reverted both
   sessions. s307 localized the hang away from the 3 gate-consumer functions themselves (all 3 complete
   20 clean iterations) to a shared upstream resource that stops delivering work to both the audio-tick
   loop and RSP task dispatch after task #39/tick #19. Next work unit: trace what's supposed to produce
   RSP task #40 — the task-submission producer and/or scheduler wakeup logic, not the 3 gated functions.
   `reapplyDisplayMode`'s site remains untouched. Full narrative: Next-steps items -168..-161 below.
3. **M3 crash work only as systematic idiom-class audits** (the s282–s288 `-0x25A4` model), never
   reactive single-crash chases. Breadcrumbs are passive: enqueue soaks to scratch/agent/soak_queue/
   (the loop runs them between iterations), consume scratch/agent/SOAK-RESULTS.md.
Sanctioned tooling work unit, counts as ADVANCED whenever picked up: backport function-scoped
matching (the BREADCRUMB10+ slice idiom) to the ~100 file-scoped-only guard patches in
fixup_game_funcs.py, per the 2026-08-04 analysis in that file's header comment.


## Current truth (as of session 295; unchanged and reviewed through s304)

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

Menu state machine (s48, extended through s75; hold/crash triage s76-s114 — full session-by-session
chase in `PORTING-STATE`, not repeated here): title —start→ SELECT GAME —start→ war room / SELECT
LEVEL —start→ **AVAILABLE CRAFT** (war-room craft holograms; footer "PRESS [A] FOR LEVEL
DESCRIPTION"). From AVAILABLE CRAFT, `a` does **not** show a level description card (s61–s69). With
process alive 65s+ post-`a` (s72/s73): **black ~5s → ~1s mission-shaped capital-ship flash (texture
garbage) → stable SELECT YOUR CRAFT** (hangar pad + full X-wing, "PRESS [A] FOR CRAFT DESCRIPTION",
multi-hue floor garbage; camera orbits). From SELECT YOUR CRAFT: **`a` no-ops** (s74); **a single
Start leaves the menu** — **OVERTURNED s150 (see "Overturned conclusions"): same craft-select scene, a
corrupting camera move, not a new environment — "what leaves SELECT YOUR CRAFT into a mission" is
reopened as unanswered.** VI stays on the 0x6AB400/0x656400 pair — origin cannot name these scenes
(s48).

**Root causes found and fixed during the s76–s114 hold/crash-triage chase** (~20 distinct crash
classes total). Mechanisms and session tags: `docs/PROJECT-OVERVIEW.md` §3 ("Chasing M3 crashes").
Quick index: post-leave black screen FIXED s82 (sane-width gate); `evalCubicSplineAtTime` NaN abort
FIXED s83; OSThread UAF SIGBUS FIXED s84; `do_rom_read`/`piDmaWorker` DMA corruption FIXED s147/148;
TMEM-zero-dimension assert stopgap-guarded s192 (root cause still open); the ~20 "hangar-tick-family"
unguarded-pointer-chase classes closed s99-110 plus a s126-132 re-audit gap sweep, with the biggest
recurring sub-family (`-0x25A4` hangar-list-pointer) fully closed by the s282-288 audit lineage. Full
crash catalog with per-class status: "Next steps" list below (near the chronological bottom).

**s48 scene-identity correction:** there is no "main-menu hangar". The 512-wide origin-0x6AB400
scene is the round **level-select war room**; pre-clip-fix every clip-needing triangle dropped
(camera inside a curved room), so the tiered console rings/holotable were missing and read as a
"landing pad" + parked X-wing. Post-fix the room renders complete. VI origin **cannot** discriminate
menu scenes (the war room presents from the same 0x6AB400 as SELECT LEVEL); identify menu scenes
visually. 512-wide also covers a separate outdoor scene at origin 0x690400 — origin distinguishes
*phases*, not which menu scene is on screen.

Remaining visual defects:
- ~~s50/s51 AVAILABLE CRAFT → black → one mission frame → `fs` freeze / SIGBUS~~ — **FIXED**
  (ImemOverrun s69; depth-writeback SIGBUS s72 — mechanism in "Root causes found and fixed" above).
- ~~Hangar floor multi-hue band~~ — **FIXED and root-caused, s45–s48 (M1 closed).** Mechanism and
  fix recipe: `docs/PROJECT-OVERVIEW.md` §3. Parked anomaly (M4): 39 of 55 I4 uploads sample 64x128
  past `masks=6/6`. Overlays 12/44 still take the old broken dispatch path by design.
- ~~Hangar dimmer than the s11 peak~~ — **largely fixed, s25** by `SHADE_WRAP`.
- Outdoor 512 zero-shade is masked, not fixed: why LLE carries `baseFixed = −32768` is unknown
  (s19/s20).
- Triangles with S identically zero in the 640 attribution phase: real, uninvestigated (s18).
- `[dpc-behind]` ring-wrap drops remain genuine dropped content with `DPC_WRAP` off; not the cause of
  any known black screen (s11).

Stability: clean through s27 driven hangar soaks and s49's post-clip-fix regression sweep. 0
`UnhandledJumpTarget`, 0 `[defer-drop]`, 0 `[dmem-race]`, 0 asserts. `[missing-func]` clean in every
soaked phase to date except s49's undriven outdoor-512 stretch (3 addresses stubbed once each, 0
aborts — parked as an M4 curiosity). **s50–s72 mission-entry path:** ImemOverrun fixed s69, SIGBUS
from garbage depth writeback fixed s72; post-`a` process now soaks well past 65s without death.


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

**M3 — first gameplay: OPENED (s50), still open.** ImemOverrun FIXED (s69), OSThread SIGBUS FIXED
(s72), wild-FB black-screen gated (s82), `evalCubicSplineAtTime` NaN div0 guarded (s83). AVAILABLE
CRAFT and SELECT YOUR CRAFT are both reachable and stable. s50-s97 chased 15 sequentially-discovered
crash classes one at a time (each fix unmasking the next, from ImemOverrun down through TMEM-zero
asserts, `do_rom_read`/audio-array corruption, `advancePlayerAnimationPhase`, and
`composeNpcOrientationMatrix`) — full session-by-session chronicle: PORTING-STATE Sessions 68-97,
summarized in the crash-class catalog table at Next-steps item -15 below and the grouped era
entries in the Next-steps list. "Single Start leaves SELECT YOUR CRAFT into hangar-flight" (s75) was
**OVERTURNED s150** (see Overturned Conclusions) — it's the same craft-select scene under a
corrupting camera move, not a distinct scene; what a leave-key actually leads to is unresolved.
*Done when:* 60 seconds of in-mission rendering, craft visibly responds to synthetic input,
stability counters 0, and the phase timeline in this document covers the mission.

**M4 — parked correctness items**, one work unit each: outdoor `baseFixed = −32768` zero-shade root
cause (currently masked, not fixed); the S=0 triangles in the 640 attribution phase; the I4
`sample=64x128` anomaly if M1 didn't consume it; the 3 `[missing-func]` addresses stubbed in the
undriven outdoor-512 stretch (0x800C7120, 0x800FBD48, 0x800FB190, s49) — **identified s53**:
`getConfigFloatPair` / `clearMissionObjectiveFlagsAndEnterPhaseSix` / `requestMissionTransitionMode`,
all real mission-overlay functions misassigned to `symbol_files/main_overlay.txt` instead of
`mission_overlay.txt` (the `overlays.cpp:388` "symbol assigned to a non-overlay file" failure).
**s54: fix applied** (3 lines added to the sibling `~/Documents/Tools/rogue_squadron64` checkout's
`symbol_files/mission_overlay.txt` — not `lib/`, no `submodule-patches/export.sh` needed); full regen
pipeline ran clean. **Runtime confirmation still outstanding** (s54 skipped the game run rather than
risk a load-stalled false-negative under high system load; not yet re-attempted). That sibling repo
also carries pre-existing uncommitted changes to 3 other symbol files, unrelated to this fix —
flagged for the user, not committed autonomously (s54).

**M5 — audio de-stubbing (investigation first, not code).** The MusyX audio ucode already
recompiles (`factor5_ucode_b_recompiled.c` sits in the build as a never-called artifact). First
work unit: a design doc only — how audio tasks would run LLE alongside gfx (they share the `dmem[]`
serialization built in s5), what bridges RSP audio output to SDL, and what the audio-gate byte
reversal implies. **Gate M5 behind M2**: audio re-enters exactly the shared-state territory that
cost three sessions before the recursive mutex.


## Next steps, in order of expected value (s295)

Numbering convention (fixed s295, was previously three colliding sequences): items are
numbered highest-magnitude-negative (top, newest/highest priority) counting up to -1 (bottom,
oldest). Current top is -168 (s307); the next new item takes -169 and is inserted at the top.

-168. **(s307)** Re-reverses `setDisplayMode`'s gate-byte site (`0x8008EB40`) a 3rd time, this time
    with the s306-armed 3-function entry/exit tags live. **Soak reproduces s303's hang a 3rd time**
    (identical signature: `[phase]` stuck at 2 lines/width 320 the whole 600s window, exactly 39 RSP
    tasks, no crash, never reaches title). **Localizes the hang away from the 3 previously-suspected
    functions**: `update3DAudioFrame`, `tickAllActiveSongs`, and `tickAudioSequencerFrame` all fire 20
    clean entry/exit pairs (`n=0..19`, no dangling entries) before the freeze — none of them hangs
    internally. Cross-referencing the RSP task log: `[runner] task #N exit=1` climbs cleanly to `task
    #39` and then never produces `task #40` for the rest of the run; the audio-tick freeze (stuck at
    `n=19`) and the RSP-task freeze (stuck at task #39) land at the same point, both followed by pure
    scheduler churn (`[sched-queue]`/`[sched-check]`/`[sched-runnext]` with no new work) — the VI thread
    itself doesn't freeze (`update_screen #N` keeps climbing past #36000), it just perpetually skips
    presentation because `rdpFs` never advances past 39. **Revised hypothesis**: a shared upstream
    resource common to both the audio-tick loop and RSP task submission (likely a coop-scheduler
    dependency) stops delivering new work after a fixed small count — not a bug inside any of the 3
    gated functions. Reverted same session (one-site-per-session discipline): `fixup_game_funcs.py`'s
    regex restored to force-zero both `0x8008EB40` and `0x8008EC88` again, regenerated, rebuilt,
    verified in generated source. Single-source (one soak this session) but the "39 RSP tasks" number
    matches s303's independently-obtained soaks exactly — corroborating, not yet a same-session repeat
    of this specific localization. Next work unit (NEXT.md): trace what's supposed to produce RSP task
    #40 after task #39 exits — the task-submission producer and/or scheduler wakeup logic around that
    point, not the 3 gated functions (now cleared). Full detail: `PORTING-STATE` Session 307.

-167. **(s306)** Settles the s304-raised open question with a same-run-positive-controlled entry
    counter (`fixup_game_funcs.py`, env `ROGUESQ_LOG_INITMUSYX_REACH`): **`initMusyXEngine` is
    genuinely never called in the current recompiled game — reachability REFUTED, with 2 independent
    soaks confirming a clean, controlled null.** Soak 1 (`step5reach1`, died early to crash family #3's
    known `waitForAnyAudioSlot` pre-title SIGSEGV signature, unrelated to this change — zero
    `[audio-drain-enter]` lines, matching the exact s301-documented signature, not a new regression):
    `[reach-init-musyx]` 0 fires, `[reach-reset-musyx-CONTROL]` 2 fires. Soak 2 (`step5reach1b`, full
    boot → title → SELECT YOUR CRAFT → complete 240s hold with the full stick schedule, **0 crashes**,
    300s total): `[reach-init-musyx]` 0 fires across the entire run, `[reach-reset-musyx-CONTROL]` 7
    fires (`n=0..6`) — confirms the logging/`getenv` plumbing itself works throughout (positive control
    holds in both runs), so the null on `initMusyXEngine` is real, not a broken instrument. The 3
    gate-consumer tags batched in the same patch (`[reach-update3d-entry/exit]`,
    `[reach-allsongs-entry/exit]`, `[reach-audioseq-exit]`) also never fired in either soak — fully
    explained by the still-unchanged baseline (`setDisplayMode`/`reapplyDisplayMode` still force-zero
    the gate byte every call, per s303's revert), not new information on its own, but now armed and
    ready for the next site-reversal soak. **This retroactively invalidates s302's validation** (item
    -164 below, also flagged under Overturned Conclusions): s302 reversed `initMusyXEngine`'s gate-byte
    site and reported "0/2 family #1 recurrence" as evidence the reversal was safe, but since
    `initMusyXEngine` never executes, that reversed code path was never exercised in either of s302's
    soaks — the clean result reflects dead code, not a validated gate=1 state. **Net effect on the M5
    plan**: gate=1 has *still* never been exercised in any soak to date; s303's `setDisplayMode` hang
    remains the only time it was ever attempted, and remains the sole evidence about what happens when
    it is. Next work unit (NEXT.md): re-reverse `setDisplayMode`'s site (`0x8008EB40`) with the 3
    gate-consumer tags and `ROGUESQ_LOG_INITMUSYX_REACH` already armed, soak, and read which (if any) of
    `update3DAudioFrame`/`tickAllActiveSongs`/`tickAudioSequencerFrame` logs entry but never logs exit —
    localizes the hang instead of re-running s303's undifferentiated black-box reversal. Full detail:
    `PORTING-STATE` Session 306.

-166. **(s304)** Source-read (no build/soak): traces what `setDisplayMode`/`initMusyXEngine` compute
    into `$v0` before their gate-byte writes. **Refutes both of s303's anticipated hypotheses**: both
    sites write the identical simple constant `1` (no computed/branch-dependent value), and
    `setDisplayMode` has exactly one call site (`mainBootstrapWorker`, no retry/loop) — boot-once, same
    shape as `initMusyXEngine`. (`reapplyDisplayMode` genuinely is hot — called every video frame from
    `runVideoFrameTick` — but that's irrelevant to explaining s303's `setDisplayMode`-specific hang.)
    **New structural fact**: `setDisplayMode`/`reapplyDisplayMode` each contain their own entry-time
    zero-write to the gate byte, sandwiching the full MusyX-reset call sequence
    (`resetSongSubsystemCounter`→...→`reset3DAudioLists`, gated by `initAudioSubsystem`) between a
    disable and re-enable — a 0→1 toggle across the call. `initMusyXEngine`'s site has no such toggle;
    it's a plain unconditional "set to 1 once." **Leading revised hypothesis**: per s300 (item -162),
    the gate's only consumer (`musyxSynthFrame`) skips 3 ancillary functions (`update3DAudioFrame`,
    `tickAllActiveSongs`, `tickAudioSequencerFrame`) at gate=0 and calls them at gate=1 — never
    exercised in any validated soak to date. s303 assumed gate=1 was already safely exercised via
    s302's `initMusyXEngine` reversal, but an exhaustive text-grep of `RecompiledFuncs/*.c` found
    **zero references anywhere to `initMusyXEngine`** (`0x8008E940`) outside its own body — no `jal`,
    no absolute-pointer construction — i.e. no evidence it's ever called. (A raw ROM byte-scan for the
    address was also run but is invalidated by its own negative control — `jal` encodes a shifted
    26-bit field, not an absolute address, so the scan can't distinguish dead code from
    jal-only-reached code; discarded, not cited.) **Single-source** — doesn't rule out an ELF
    relocation/overlay mechanism outside `RecompiledFuncs/`. If `initMusyXEngine` is truly unreached,
    s302's validation never exercised gate=1 at all, and s303's hang would be the *first* real gate=1
    ever hit — promoting "first-ever execution of the 3 skipped functions" to the leading hang
    explanation. Next work unit (NEXT.md): a same-run-positive-controlled entry counter on
    `initMusyXEngine`, batched with entry/exit tags on the 3 gate-consumer functions. Full detail:
    `PORTING-STATE` Session 304.

-165. **(s303)** M5-AUDIO-PLAN.md step 4's 2nd slice: reverses `setDisplayMode`'s gate-byte force-zero
    site (`0x8008EB40`). 2 validation soaks: **2/2 identical deterministic full boot hangs** — VI width
    stuck at 320 the whole 600s window, exactly 39 RSP tasks both soaks, never reaching title. Not
    family #1's signature and not `waitForAnyAudioSlot`'s drain loop (never entered) — a different,
    unlocalized stall mechanism, but unambiguously caused by this site's reversal (this exact signature
    never appeared in s300-302's soaks). **Re-reverted same session**, restoring exactly s302's
    validated state (`initMusyXEngine` alone reversed) — confirmed via direct inspection, no re-soak
    needed. Confirms the plan's own risk flag that `setDisplayMode` is a hotter, non-interchangeable
    path vs. the boot-once `initMusyXEngine` site — **do not retry without a source-level read** of
    what `setDisplayMode` computes into `$v0` before the write (s304, item -166, answers this).
    `reapplyDisplayMode`'s site remains untouched and untested — treat as its own open question, not
    an inheritor of either sibling's risk profile. Full detail: `PORTING-STATE` Session 303.

-164. **(s302)** M5-AUDIO-PLAN.md step 4: reverses `initMusyXEngine`'s gate-byte force-zero site
    (`0x8008E9F8`) — splits the 3-way regex in `fixup_game_funcs.py` so only `setDisplayMode`/
    `reapplyDisplayMode` still force-zero; the guest's own real init-success write now takes effect.
    Confirmed via patch-count (`x2`, was `x3`) and direct inspection. 2 validation soaks: both reached
    SELECT YOUR CRAFT then died within the first hold-iter (~75s) to pre-existing, unrelated crash
    classes (RDRAM-host-base/`reserveAndEmitDLEntry`; `evalCubicSplineAtTime` NaN div0, s83) —
    **0/2 family #1 recurrence** (both deaths are outright crashes, not hangs, so can't be family #1
    by construction) and `WAITFORSLOT_GUARD` fired 0/2. `[audtask-dispatch]` confirms real ucode
    dispatch ran continuously to the crash point in both. Neither soak reached the 240s hold window —
    both crash classes predate this session and capped run length, same limitation s301 hit. Per the
    plan's one-site-per-session design, next work unit was `setDisplayMode`'s site (item -165 above).
    Full detail: `PORTING-STATE` Session 302.

-163. **(s301)** M5-AUDIO-PLAN.md step 3: lands the `waitForAnyAudioSlot` bounded-timeout guard
    (`fixup_game_funcs.py`) — once `g_audio_drain_iters` reaches 500,000 (overridable via
    `ROGUESQ_WAITFORSLOT_GUARD_CAP`), falls through instead of looping, fires logged via
    `ROGUESQ_LOG_WAITFORSLOT_GUARD`. Safe by construction — the next original instruction
    unconditionally reassigns the touched register on every path, so the guard only changes whether
    the loop takes one more lap. 3 validation soaks (`ROGUESQ_AUDIO_UCODE=1` armed): guard fire count
    **0/3** across 7 legitimate calls (each converged in 1 iteration); 2/3 soaks died to pre-existing,
    unrelated crash classes (crash family #3's own pre-title SIGSEGV signature once — confirmed not a
    legitimate call, zero entry-diagnostic lines despite the crash PC resolving inside the function;
    and the s300-control-soak RDRAM-host-base signature once, unrelated to audio). Confirms the guard
    is a correctly inert safety net — ready for step 4. Full detail: `PORTING-STATE` Session 301.

-162. **(s300)** M5-AUDIO-PLAN.md steps 1-2. Step 1 (source-read): traced `musyxSynthFrame`'s 5 reads
    of the audio-enable gate byte (`0x800A0F50`) and found the gate only skips 3 narrow ancillary
    functions (`update3DAudioFrame`, `tickAllActiveSongs`, `tickAudioSequencerFrame`) inside its
    per-VI-retrace tick — not task submission. Also resolved the s173 "gate byte appeared nonzero"
    contradiction: a full-tree grep found exactly one site that can ever write nonzero
    (`initMusyXEngine`, force-zeroed by `fixup_game_funcs.py`) — if s173's inference was accurate, the
    only explanation left is a wild/corrupting write, flagged for crash family #3
    (`waitForAnyAudioSlot`). Step 2: landed `factor5_ucode_b` behind a new `ROGUESQ_AUDIO_UCODE` env
    toggle (default off) plus an always-on `[audtask-dispatch]` counter giving **ground-truth
    confirmation** `M_AUDTASK` dispatches continuously from boot regardless of the gate or toggle (the
    `musyx-dma-call`/`voice-trigger-chain` instruments step 1 expected to use actually measure PI-DMA
    sample streaming, not task submission, and fired 0 times — would have been a false null without
    this counter). 2 soaks with the toggle on: 0 crashes, ~1,500+ real ucode dispatches, title→menu→
    hold. 1 control soak (toggle off) crashed to a pre-existing unrelated class — confirms baseline
    nonzero crash rate, not a regression. Full detail: `PORTING-STATE` Session 300.

-161. **(s298)** Writes `docs/M5-AUDIO-PLAN.md` (design doc, priority-2 per the USER DIRECTIVE),
    pivoting off `tickTextureMaterialExpiry-guard` per the loop's mandatory-pivot rule (3 straight
    iterations, no `BREADCRUMB12` recurrence to react to, no maintenance trigger). Survey (3 parallel
    read-only agents) found the audio stub is one dispatch-table entry (`musyx_stub` for `M_AUDTASK`,
    `src/main/main.cpp:594-595`), the `dmem[]`-sharing design question is already solved by the s5
    mutex, and the host SDL audio bridge is already fully functional — de-stubbing is narrower than
    the goal-stack framing implied. Also found the crash-family payoff case is weaker/mixed: 1 of 4
    documented audio-adjacent crash families confirmed stub-caused (and it argues for caution — the
    fix was disabling audio harder, not less), 2 of 4 plausible-unconfirmed, 1 of 4 confirmed
    unrelated. Landed a 6-step incremental de-stubbing sequence, each with its own validation soak;
    step 1 (free source-read, no code/soak) is the next work unit. Full detail: `PORTING-STATE`
    Session 298.

-160. **(s297)** Lands `MATEXPIRY_GUARD` (`ctx->r16` KSEG0-range check) in `tickTextureMaterialExpiry`
    at the site/bail-target item -159 specified (`fixup_game_funcs.py`, after `BREADCRUMB12` to match
    its POST-breadcrumb shape). Regen/build clean (`BREADCRUMB12` still x83, guard x1 new, 46-warning
    baseline unchanged). 2 validation soaks (`HOLD_S=275`): both clean, 0 crashes, 0 guard fires — a
    **weak null** (only 2 `BREADCRUMB12` recurrences across ~294 sessions, so 0/2 fits either
    outcome), not confirmation. Unconfirmed-but-not-refuted until a 3rd recurrence fires the guard
    (confirms) or crashes at the same PC anyway (refutes — re-read the bail path). `PORTING-STATE`
    Session 297.

-159..-132. **(s267-294) Breadcrumb whack-a-mole B2-B14 plus the `-0x25A4` hangar-list-pointer audit
    lineage — CLOSED.** Starting from a refuted a0-argument hypothesis for a guest-`0x80000000`-family
    fault inside `heapFreeListDequeue` (s267, confirmed via same-run positive control), single-function
    breadcrumbs `BREADCRUMB2`-`9` chased the "cached free-list-head" idiom across `beginFrameDLChunk`,
    `processSceneNode`, `submitSceneNodeRender`, `reserveAndEmitDLEntry`, `static_5_800AB658`,
    `emitAllocatedDLCommand`, and `tickWrappingTimerAccumulatorList` (s268-282) — most soaks caught the
    idiom recurring in a DIFFERENT already-known function rather than their own target (e.g. s269/270/271
    each landed on a fresh unguarded copy elsewhere), and a 3-session PRE-SCENE `waitForAnyAudioSlot`
    boot-crash streak on `BREADCRUMB9` (s277-280, tripping the rule-8 3-strikes threshold) turned out to
    be a transient 4-session window (s276-278, s280: 7/8 = 87.5%) already fully reverted by s281, CLOSED
    as a non-finding s289. s283-288 then ran a deliberate grep-based audit of every `-0x25A4($s1)`
    hangar-list-pointer site across `RecompiledFuncs/*.c` — far more sites than the incidental
    discoveries, landing 29 guards across 3 functions (s284) including a fix for a live crash the new
    guards exposed, finding a 3rd "second-hop" blind-spot instance in `static_5_800A9270` (s285),
    classifying all of `hangarInitialize`'s remaining chunks as dead/unreachable duplicate code
    (s286-287), and closing the whole lineage s288 (the apparent `playerSnowSpeederInit` overlap was
    REFUTED — genuinely live code that merely shares address space with 3 already-guarded functions, not
    a copy of any of them). Separately, s289-294 resumed the abandoned s249-251 project-wide
    unguarded-walk static sweep (`find_unguarded_walks.py`, 143 sites/43 functions), landing
    `BREADCRUMB10`-`14` on `inflate_fast`, `coalesceFreeHeapBlocks`, `tickTextureMaterialExpiry`,
    `tickSongSequence`, and `stopSongByHandle` — no unique translation bug in any of them (the
    `inflate_fast` s272 crash was the same long-tracked `MEM_B`/`MEM_BU` null→`0x80000003` signature
    guarded ~15 times elsewhere), but s293/294's soaks caught `tickTextureMaterialExpiry`'s
    (`BREADCRUMB12`) two independent recurrences at the identical guest PC (`0x80022094`,
    `funcs_6.c:12207`), crossing the confirmation bar s297 (item -160 above) used to land
    `MATEXPIRY_GUARD`. Full detail: `PORTING-STATE` Sessions 267-294.

-130..-131. **(s265-266)** Landed the "last-executed-guest-PC breadcrumb" instrument (`g_rs64_last_guest_pc`, s264's flagged investment), verified it works; the originally-targeted `submitSceneNodeRender+19268` crash didn't recur in 6 soaks (s265). A re-soak per the same plan then caught a genuine different-offset crash (+47120), localized via the new breadcrumb to a 2nd previously-unguarded occurrence of s197's "cached free-list head" idiom, landing `CACHE2_GUARD` (s266) — 2 post-fix soaks clean, but surfaced a different, higher-priority bug. Full detail: `PORTING-STATE` Sessions 265-266.

-129..-114. **(s249-264) `composeNpcOrientationMatrix` whack-a-mole CLOSED; genesis of the unguarded-walk static sweep.** The 9-guard whack-a-mole (open since s100) closed for good s261 (`COMPOSE_NPC_GUARD9`): first-ever live call into `renderUnlitMeshFaces`, survived to VI-update #8552/143.1s (prior best ~75s), converged on the recurring "KSEG0 pointer + rdram-base, no `MEM_W` subtraction" signature in `renderUnlitMeshFaces` (7th occurrence; see s216-219 under Overturned Conclusions). Also closed: `setLookupEntryField5ByKey` needed two guards not one (s260, a 2nd-level pointer inside the callee); `evalCubicSplineAtTime`'s unguarded pointer (s259); the last 2 `-0x25A4` hangar-bay-deref gaps (s258); `submitSceneNodeRender` finally got a complete source read (s263) after 66 sessions unaddressed. Separately, s249-251 opened the project-wide static sweep for this "RDRAM-base + un-subtracted wild pointer" family: a candidate-finder script (`scratch/agent/find_unguarded_walks.py`, 143 sites/43 functions) landed, 2 functions fully guarded from it -- then it sat abandoned 43 sessions until s294 resumed it (item -159 above). Full detail: PORTING-STATE Sessions 249-264.

-113..-85. **(s220-248) Three interleaved threads: Metal-crash fixes, the CALayer/campose SIGSEGV hunt, the freeze/scene-graph investigation.** (a) Two Metal-side crashes CLOSED with positive controls: the scissor-rect OOB SIGABRT (s246) and the `fbSize()==0` viewport-NaN SIGABRT via a VI-draw skip guard (s244). (b) The host QuartzCore/CALayer SIGSEGV hunt (`campose*`, s234-248) landed a wall-clock bridge and a validated instrument, but exhausted its rule-8 budget at s248 still inconclusive -- best remaining lead: a cross-thread `CAMetalLayer` property mutation (PORTING-STATE Session 239). (c) The post-SELECT-CRAFT freeze investigation (s220-226) proved the frozen picture (torn polygon -> flat fill, non-deterministic even on identical scripted input) sits downstream of a healthy scene-graph traversal and a still-climbing RDP full-sync counter -- not a stuck camera or frozen pointer. Also: the DL-payload-staleness probe (s230-233) stayed ambiguous, and a Bash-allowlist bug (`Bash(<dir>/:*)` rules silently not matching, s227-228) blocked 2 sessions before resolving s229. Full detail: PORTING-STATE Sessions 220-248.

-84..-26. **(s150-219) The long `heapWalker`/`renderUnlitMeshFaces`/`composeNpcOrientationMatrix`/`heapFreeListDequeue` whack-a-mole guard-gap chase.** ~70 sessions landing one unguarded-pointer-chase guard at a time, converging on 2 durable lessons: the literal `0x0000000300000000` at x0/x8 across 3 unrelated crash sites is this process's constant RDRAM host base pointer, not corrupted data (s219, see Overturned Conclusions); the real wild operand is the *other* register, with a KSEG0-tag signature recurring in `renderUnlitMeshFaces` specifically. Also settled: "single Start leaves SELECT YOUR CRAFT into hangar-flight" **OVERTURNED s150** (mission-entry unanswered again); the s162 post-leave cutscene stall is the s79/80 FULL_SYNC-loss class recurring, capable of at least one recovery (s153/154); a `[thr-resume]`-adjacent scheduler silent-drop mechanism (s180-187) got a defensive guard that produced the first fully crash-free full-length soak in that lineage (s187). Full detail: PORTING-STATE Sessions 150-219.

-25..-21. **(s133-149) Audio-array corruption (Thread B) — CLOSED, plus two side threads parked at
    exhausted rule-8 budget.** Real mechanism (non-atomic `voiceCount`-write-before-pointer-store race
    in `allocateSongChannelArray`) found s145, FIXED and verified s147/148: 3 independent verification
    soaks all clean — 0/13 corrupted `[voice-active-gate-nz]` reads post-fix (vs. 5 pre-fix), 0/3
    `do_rom_read` recurrences (vs. 9 prior) — first fully crash-free soaks for this shape since s83.
    **s149 bonus**: "what input leaves SELECT YOUR CRAFT" was never actually open — the leave
    transition fires correctly (invisible to VI-phase tracking); the real open question was always the
    post-leave scene and surviving its first ~2s, where the wider hangar-tick crash family kept
    landing. Path to the fix (s138-146): ruled out a static ROM string table (s138) and adjacent-heap
    aliasing (s139-141, via an `rs_malloc`/`rs_free` range-overlap measurement that also confirmed the
    voice array's per-slot stride is 136 bytes); named the real allocation as
    `allocateSongChannelArray`'s own 2nd alloc, one slot of a per-tick-toggled double-buffered pointer
    table (s141-143); found `musyxMixActiveVoices`'s unchecked-cursor write (s144, not proven the
    direct writer) before s145 found the real mechanism. Two side threads exhausted their rule-8
    budget without resolving, guards left in code regardless: `emitAllocatedDLCommand` soak hypothesis
    (s133-135: hit an environment-side Apple-Metal SIGSEGV, an 18th-class recurrence, then the
    separately-tracked `do_rom_read`/`piDmaWorker` corruption SIGSEGV — `emit-dl-guard2`/`3` never
    fired, 0/0 all 3 attempts); `submitSceneNodeRender`'s `MATLIST_GUARD1`/`GUARD2` (s136-137, parked
    at 2/3, both 0/0 on the new guards, both dying to the `do_rom_read` race). Full detail:
    `PORTING-STATE` Sessions 133-149.

-20. **Regen-pipeline reliability bug (s120, confirmed intermittent not deterministic).** Root cause:
    `N64Recomp` skips rewriting any `RecompiledFuncs/funcs_*.c` file that already exists on disk, so
    any patch whose regex anchor survives its own insertion stacks a duplicate on the next
    `fixup_game_funcs.py` run unless the file is deleted first. Deleting all `funcs_*.c` before every
    regen is mandatory but **not sufficient by itself** -- residual intermittency's root cause is
    still unknown. **Standing rule**: audit the patch report for anything other than the expected `xN`
    count after every `fixup_game_funcs.py` run. Full detail: `PORTING-STATE` Sessions 120, 121, 126.

-19..-17. **(s102-135) Thread A/B saga leading to the s145/147/148 fix above, plus the regen-pipeline
    root cause.** Thread A (s126-132): re-audited every already-guarded hangar-tick crash class for a
    2nd unguarded pointer-chase site — 6/8 had a genuine gap (all guarded); biggest hit
    `updateHangarBayScene`'s `-0x25A4` family (26 sites, s132), later fully closed by the s282-288
    audit lineage. Thread B (s116-145): chased the `voice+0x0`/`+0x34` corruption through several
    reframings; refuted along the way: stale `rs_malloc` memory, an OOB scan index, an RSP-ucode
    write, a computed-offset guest-C store, an adjacent-heap-allocation aliasing theory. Earlier
    (s102-113): traced the corrupted MusyX DMA-batch `devAddr` field backward through 5 functions
    across 6 sessions (`submitDmaRequestBatch`/`musyxSynthFrame` cleared → `acquireSampleStreamBlock`
    refuted, never entered → `fillSampleStreamRange` identified as writer, computing `devAddr` from
    `voice+0x34` → that field's allocator `initSampleStreamBlockCache` cleared, inputs already
    corrupted at entry → traced to `musyxRenderVoiceSamples` → `musyxInitVoiceFromSample` identified as
    the sole writer of that offset anywhere in the tree, s105/s111 exhaustive grep); the
    call-chain-ancestry angle (s105-110) was a 5-session dead end. **Methodology lesson**: comparing
    two instruments' log lines by *file order* across threads is not a valid proxy for real time
    order — cross-thread log correlation needs a shared sequence number. **Tooling** (s102,
    root-caused precisely by item -20 above): `fixup_game_funcs.py` is not idempotent — re-running it
    without a full ELF regen between runs inserts a second copy of every already-applied patch
    (harmless, but bloats generated files). Full detail: `PORTING-STATE` Sessions 102-135.

-16. **M3 hangar-tick-family guard program (s99-s110): 8 crash classes guarded** (16th/12th/11th/
    14th/17th/18th/9th/10th -- see the crash catalog below), all with clean negative controls, same
    `U32()`-truncated-bounds-check-then-`goto`-real-epilogue template used by every guard since. s101
    and s110 are two independent soaks that survived the entire family with zero crashes, reaching the
    ~140s DMA-corruption window alive. Full detail: `PORTING-STATE` Sessions 99-101, 109-110.

-15. **M3 -- find the indirect caller of `submitDmaRequestBatch`: CLOSED (s101).** The caller is
    `musyxSynthFrame` (`funcs_24.c:3095`, a per-VI-retrace audio tick) via `viRetraceHandlerThread` --
    not the mission/DL code path every earlier session assumed. Refuted dead ends, do not reopen:
    `ra=0x00000000` as a corruption signature, "dump the OSIoMesg at mb," consumer index desync, "the
    boot call loops more than once."

    **Crash catalog** (19 classes found chasing this window, s83-s110; "guarded" = landed with a clean
    negative control, treat as closed unless noted):

    | # | site | status |
    |---|---|---|
    | 9 | `updateAnimatedTextureStreaming` (funcs_11.c) | guarded s124, 2nd gap found+closed s127 |
    | 10 | `static_5_800B4048` | guarded s125, 2nd gap found+closed s127 |
    | 11 | `projectModelBoundsToScreen` | guarded s101, 2 more args found+guarded s128 |
    | 12 | `composeNpcOrientationMatrix` | guarded s100, 2nd independent loop found+guarded s126 |
    | 13 | RT64-internal, `reinterpretTileRecord` assert | guarded s196 after a 2nd occurrence (s195) |
    | 14 | `reserveAndEmitDLEntry` | guarded s109, confirmed clean s129 |
    | 15 | RT64-internal, `loadDrawState` zero-sample assert | root-caused RT64-internal (s159), guarded |
    | 16 | `activateAnimationKeyframe` | guarded s99, confirmed clean s130 |
    | 17 | fault inside `updateHangarBayScene` itself (5 sites) | guarded s110 |
    | 18 | `submitSceneNodeRender` free-list walk | guarded s123, 9 inlined copies found+reopened s131, root-caused as the `-0x25A4` family and closed via the s282-288 audit lineage |
    | 19 | RT64-internal SIGSEGV, `MetalFramebuffer` ctor via `createTileCopyRecord` | 1 occurrence, not source-read, not recurred |

    Thread A (s126-132, see item above) later found a *second* unguarded site in 6 of the 8 guarded
    functions -- already folded into the table above. Full detail: `PORTING-STATE` Sessions 93-110,
    124-132, 159, 195-196.

-14. **M3 — root-cause/fix the `queueGPUUploadTMEM` zero-size assert.** (Crash classes 9/10 —
    `updateAnimatedTextureStreaming`/`static_5_800B4048` SIGBUSes — CLOSED s124/s125, tracked only in
    the crash catalog table at item -15 above.)

-11. **M3 — `advancePlayerAnimationPhase` SIGBUS: PARKED (s89).** 3 consecutive non-recurrences since
    s88's correctly-targeted instrument, against 8 prior crashing soaks. Not worth a dedicated soak;
    if it recurs incidentally, `ROGUESQ_LOG_ANIM_CB=1` is still live and ready to read.

-10. **M3 — Metal-shader-compiler SIGSEGV reproducibility** (s83 spline1: SIGSEGV inside
    `Metal.framework`'s `MTLCompilerFSCache`, no source on our side). Still one data point.

-9. **M3 — confirm the s83 spline div0 guard actually engages.** 0/5 fires so far (still 0 after
    s88/s89/s90); real fix by code inspection (genuine 0/0 IEEE division) but no same-run positive
    control yet.

-8. **M3 — characterize `frameStartReset` SIGBUS.** 3 occurrences (s85, s108, s156 — the 3rd,
    `+532`, at a call chain byte-identical to `composeNpcOrientationMatrix`'s own, raising a
    shared-dispatcher hypothesis); no located faulting instruction in any of the 3.

-7. **M3 — HOLD_S=60 craft stick (M3 DoD body)** once earlier items clear: `PROBE_MODE=start_only
    HOLD_S=60` marks 10/25/40, document the phase timeline. Gate already keeps black off; residual S1
    `fs` freeze (~3769-3872 plateau) may still stall animation.

-6. **M4 — confirm the s53 missing-func fix at runtime** (s54 applied + built it; only the game-run
    check remains). Undriven outdoor-512 stretch; `grep -c "\[missing-func\]"` should go 3→0. Not
    load-gated (s60/s61). Full detail: PORTING-STATE s53, s54.

-5. Past the first sustained mission hold: expect further new failure classes (mission overlay DMA →
    missing-func/UnhandledJumpTarget, new VI phase, overlays 12/44 splice, texture corruption). Each
    new failure is its own work unit.

-3. **Sibling-repo housekeeping (flagged s54, not autonomous):** `~/Documents/Tools/rogue_squadron64`
    carries uncommitted symbol-file edits including s54's `mission_overlay.txt` fix. Ask the user
    before committing there.

-2. **Band-row coverage history** (settled, s41-49): s40's `col`-write probe fails its control.

-1. **GPU->CPU present PNG** via `NativeTarget::copyToRAM` -- a convenience, not a blocker.

**Done, do not redo:**
- Optimise the ucode vector path -- s38 found it was `-O0`; `-O2` gave 41x. SIMD/RSPRecomp vector work
  is unnecessary at 4.5ms/task without a new measurement justifying it.
- Confirm the ucode-performance bottleneck (s37) - find why DL submission collapses (s36) - census the
  RDP stream (s35) - localise the draw loss (s33/s34).
- Coverage attribution (`LOG_BBOX`) and load/render format mismatch (`LOG_UPLOAD`) -- every draw
  covering the band is I4 with `tlut=0`, from I4 loads.
- The s27-s31 I4-decode line (`FIX_DXT_I`, `I4_SHADE_MONO`, `SHADE_ONLY_MONO`, restricted
  `FLATTEN_I4`) -- aimed at a texture that does not paint those pixels.

(The s92-95 session-by-session DMA-caller narrative that used to live here is folded into the crash
catalog and DMA-caller finding above -- not duplicated.)

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

`## LLE stabilization session 2 (2026-07-12)` sits out of order in the log, between s7 and s8: its
conclusions are among the oldest in the file, not the newest.

- **(s222→s223)** "no soak reaches mesh-heavy content" — a 4-soak sample-size artifact; a re-run
  reached space-combat content before freezing. The freeze itself is real, still reproduces (now a
  flat fill, not a torn polygon). PORTING-STATE 223.
- **(s216-218→s219)** "shared corrupt literal `0x0000000300000000` at x0/x8, WRITTEN somewhere" — that
  register is the process's constant RDRAM host base pointer, present by construction in every
  `MEM_W` fault, not written corruption; the wild operand is the *other* register (byte-identical at 3
  sightings, all the same `renderUnlitMeshFaces` bug, vs. an unrelated 4th `heapWalker` bug).
  Believable: byte-identical across sessions months apart. PORTING-STATE 219.
- **(s75/76→s150)** "single Start from SELECT YOUR CRAFT leaves into a distinct hangar-flight scene" —
  dense capture + an independent prior run + a code-level check (crash backtraces stay entirely in
  hangar-menu code) show it's the same craft-select scene under a corrupting camera move. Believable:
  HUD disappears, tilted silhouette against stars reads as "flying." Reopens "what leaves SELECT YOUR
  CRAFT" as unanswered. PORTING-STATE 150.
- **(s2-31→various, ~15 claims, grouped)** Build/pixel-getting era, each overturned within 1-2
  sessions: Z-buffers misread as colour buffers; texrect output called invisible; RDP "emitting
  nothing" (real bug: a function-local ring high-water mark); `DPC_WRAP`/fbpair-cap misdiagnosed for
  missing FULL_SYNC (PROJECT-OVERVIEW §4.6); `PRIM_ALPHA_FF` called necessary for text; a
  sampling-artifact black-screen; misattributed texture dumps, floor-band line-mask/palette/dxt
  theories (M1's real cause: s44-49), fog-color attribution, S=0-triangle phase, stale-TMEM-at-draw
  (§4.1), and 1024-phase black screen (present-starvation, not zero-shade). PORTING-STATE 2-31.
- **(s62-69, grouped)** "RSP task submission stays healthy through the freeze" — a 1-in-32 throttled
  sample missed the crashing tail; an unsampled histogram showed 100% `ImemOverrun` exits.
  "Self-restarting the end-of-IMEM perspective-divide branch un-freezes tasks" — the instrument fired
  0 times; the real site was `CLIP_1FBC`→`L_1650` (reconnecting `goto L_1650` unfroze `fs`).
  PORTING-STATE 62-69.
- **(s12-48, grouped — real causes already stated in "Current truth" above)** "0x6AB400 is the
  main-menu hangar" (believable: the partial render looked coherent for 36 sessions); stray
  briefing-room/SELECT-LEVEL origin+timing claims; hangar dimness/floor-band misattributed to a
  magnitude-erasing shade census / a residual-metric artifact (real cause: M1 s44-49); "no complete
  clip overlay in ROM" / "routing may be unsafe" (a stray census conflated fall-through hits with real
  dispatch). All overturned s47/s48. PORTING-STATE 12-48.
- **(s70-82, ~9 claims, grouped)** The post-`a` SIGBUS/black-screen self-correction chain — UAF
  theories, what survives past it, Start-press counting, `fs`/present-stall theories — all resolved by
  the s84 UAF fix and s82 sane-width gate. PORTING-STATE 70-82.
- **(s87→s88)** "8th crash class is self-recursion in `advancePlayerAnimationPhase`" — that call site
  belongs to a different, unreached function; an instrument showed constant stack depth across 3296
  calls, no recursion. PORTING-STATE 88.
- **(s302→s306)** "reversing `initMusyXEngine`'s gate-byte force-zero site validated safely (0/2 family
  #1 recurrence over 2 soaks)" — a same-run-positive-controlled entry counter (2 soaks) found
  `initMusyXEngine` is never called at all; the reversed write never executed in either s302 soak, so
  their clean result reflects dead code, not a validated gate=1 state. Believable: the soaks genuinely
  were clean (0 crashes matching family #1, real ucode dispatch confirmed throughout) — nothing in
  their own signal suggested the reversed line hadn't run; only a dedicated reachability instrument
  could show that. Gate=1 has still never been exercised by any soak to date. PORTING-STATE 306.

### Dead ends — labelled as such in the log, do not retry

- **(s2b-s4, grouped)** `RDP_ADDRESS_MASK`→0x7FFFFF (aliased legitimate extended-RDRAM handles onto
  low memory); a chunk-replay hack in `dma_rdram_to_dmem` (legit trig reads right after a swap);
  widening the DMA shadow to 0x37658 (legit dynamic data); blanket ucode-image shadow `shadow2` (2
  addresses are legitimately rewritten); `ROGUESQ_RING_RESYNC=1` (no measurable change);
  `dmem[0x153]=0xFF` forced segment reload (made failures worse).
- Bulk moves of unmapped symbols out of `main_overlay.txt` (s9): splits the enclosing function
  (PROJECT-OVERVIEW §4.5), producing a SIGBUS. Use `tools/overlay_symbol_probe.py <0xADDR>` first, one
  validated batch at a time.
- Present-side snap-down / `findMostRecentContaining` fallbacks (s9): neither ever fired.
- `ROGUESQ_VIEW_RDRAM=1` (s9): the game window never appears; broken in this fork.
- `ROGUESQ_WRAP_DEDUP=1` (s10): removes ~33000 redundant submissions but the same Metal assert still
  hits.
- `ROGUESQ_FORCE_PAL15=1` (s14): clears the floor band but corrupts ceiling banners sharing pal=15.
- **(s85→s91)** "`do_rom_read` corrupted `physical_addr` is nondeterministic garbage" — the exact same
  DMA call recurred byte-for-byte 3 times across 3 sessions; reclassified deterministic, reproducible.

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
- A "crash-free, full hold survived" soak is not evidence the game did anything for that hold —
  MD5-checksum the `hold_NN.png` series before trusting a diagnostic null; s222's soak logged 991
  `[vi-fs-decision] FIRE` events and ran its full 350s hold with 0 crashes while the actual on-screen
  picture was byte-identical from `hold_04.png` onward, frozen the entire time.
- Launching a soak with `run_in_background=true` and then ending the turn before it finishes risks
  the harness reaping the whole process tree mid-run (s222 found exactly this: an orphaned soak,
  no crash logged, process gone, ~40 min stale). For soaks that fit the tool timeout, launch
  synchronously (foreground, no `&`) instead — it cannot be orphaned by a premature turn-end.
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
