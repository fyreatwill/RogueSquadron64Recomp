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
   s295/296 (562,666→59,811 bytes), s299 (61,293→47,105), s305 (62,103→54,550), s308 (this pass —
   60,540→45,772 bytes, 692→458 lines, 234 net: condensed the s297-307 Next-steps items -168..-160 into
   one dense summary, migrated the s83-s110 crash catalog table to `docs/PROJECT-OVERVIEW.md` §7, and
   tightened the older -159..-132/-25..-21/-19..-17 grouped items and the small M3/M4 tail items -16..-1).
   35 KB remains a stretch target, not a hard floor — the "Current truth" env-var/timeline prose and the
   Regeneration section's Standing warnings stay intact deliberately; both are used every iteration for
   phase-gating and build commands.
2. **M5 audio de-stubbing**: design doc DONE (s298, `docs/M5-AUDIO-PLAN.md`) — a 6-step incremental
   de-stubbing sequence, one validation soak per step. Steps 1-3 DONE and validated clean (s300/301).
   Step 4 (reversing each of the 3 audio-gate-byte force-zero sites, one per session) is IN PROGRESS:
   `initMusyXEngine`'s site reversed s302, but s306's reachability counter (2 soaks) found
   `initMusyXEngine` is never actually called — s302's validation is retroactively meaningless (see
   Overturned Conclusions), and gate=1 has still never been exercised by any soak. `setDisplayMode`'s
   site attempted s303, s307, s310, and s311 (each with the prior session's diagnostics live): all 4
   reproduced an identical deterministic full-boot hang (~39 RSP tasks/`rdpFs`, stuck at VI width 320),
   re-reverted every session. s310's batched 4-site diagnostic (`ROGUESQ_LOG_AUDIOTICK_TRACE`) found
   `viRetraceHandlerThread`'s own loop, the VI-retrace 4-slot callback table, and `musyxSynthFrame`'s own
   entry all keep firing well past the tick-19/20 point where 3 gate-consumer functions
   (`update3DAudioFrame`/`tickAllActiveSongs`/`tickAudioSequencerFrame`) and RSP `M_AUDTASK` submission
   stop — refuting H1 (driving thread stops being woken) and H4 (full unreaped queue, source-confirmed
   no such queue exists). s311 ran the same reversal a 5th time with a full 10-minute capture and matched
   sample caps across every diagnostic, and found **two distinct, sequential freeze boundaries**, not
   one: a SOFT stop at call #19/20 (only the 3 gate-consumer functions + `M_AUDTASK` submission stop;
   `musyxSynthFrame`'s own entry and its `[musyx-gate1]` countdown/period read — confirmed constant,
   ruling out that gate's raw inputs as the cause — keep executing normally for ~20 more calls), then a
   HARD stop at call #39/40 (everything, including `viRetraceHandlerThread`'s own loop, stops
   simultaneously with the RSP task-runner's last dispatch, task #39 — the same event s307/s309 called
   "the later full-scheduler wedge," now dated against the audio-tick diagnostics too). Next work unit:
   instrument the branch/compare immediately after `[musyx-gate1]`'s read point (or the 2 other
   near-identical gate copies s107 found but s311 didn't touch) to find what diverges at call #19.
   Full narrative: Next-steps item -171 below. `reapplyDisplayMode`'s site remains untouched.
3. **M3 crash work only as systematic idiom-class audits** (the s282–s288 `-0x25A4` model), never
   reactive single-crash chases. Breadcrumbs are passive: enqueue soaks to scratch/agent/soak_queue/
   (the loop runs them between iterations), consume scratch/agent/SOAK-RESULTS.md.
Sanctioned tooling work unit, counts as ADVANCED whenever picked up: backport function-scoped
matching (the BREADCRUMB10+ slice idiom) to the ~100 file-scoped-only guard patches in
fixup_game_funcs.py, per the 2026-08-04 analysis in that file's header comment.


## Current truth (as of session 295; unchanged and reviewed through s307)

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
oldest). Current top is -171 (s311); the next new item takes -172 and is inserted at the top.

-171. **(s311) M5 audio de-stubbing: NEXT.md Option A executed — rules out `[musyx-gate1]`'s raw
    countdown/period inputs as the tick-19 divergence, and an unplanned full-length capture finds a
    2ND, later freeze boundary at call #39/40.** Widened `[musyx-gate1]`'s sample cap from a flat
    `n<20` (capped exactly at the freeze point) to `n<40||(n%128)==0`, matching s310's own diagnostics'
    convention, and reversed `setDisplayMode`'s gate site a 5th time to exercise it. Result: the gate's
    countdown/period values stay constant (`0`/`16777216`) across all 40 samples — **rules out Option
    A's hypothesis** (this specific read point does not change at tick 20). But because this soak ran
    the FULL 600s phase-timeout with every diagnostic's cap wide enough to show continued activity via
    its own modulo resample, the previously-ambiguous silence past each cap is now decisive: the 3
    gate-consumer functions (`update3DAudioFrame`/`tickAllActiveSongs`/`tickAudioSequencerFrame`) and
    RSP `M_AUDTASK` submission stop together at call #19/20 (a SOFT stop — `musyxSynthFrame`'s own
    entry and gate1 read keep running normally for ~20 more calls), then EVERYTHING — including
    `viRetraceHandlerThread`'s own loop-top and the VI-retrace callback-table slot read — stops
    simultaneously at call #39/40, in lockstep with the RSP task-runner's last dispatch (task #39,
    matching s307/s309's independently-dated "later full-scheduler wedge," now tied to the same event
    on the audio-tick side too). Narrows the next work unit to the branch/compare immediately after
    `[musyx-gate1]`'s read point (not the raw inputs, now ruled out), or the 2 other near-identical
    gate copies s107 found but this session didn't instrument. `setDisplayMode`'s site re-reverted to
    force-zero same session (baseline restored, verified rebuilt); the widened `[musyx-gate1]` cap kept,
    armed-but-inert by default. Full detail: `PORTING-STATE` Session 311.

-170. **(s310) M5 audio de-stubbing: batched diagnostic REFUTES H1 and H4, localizes the tick-19 stall
    to inside `musyxSynthFrame`/a callee.** Source-read found the real invocation mechanism a literal-text
    grep missed: `viRetraceHandlerThread` (`funcs_4.c:29441`) drives `musyxSynthFrame` via an INDIRECT
    call — a 4-slot VI-retrace callback table walk (`funcs_4.c:29975-30007`, base `0x8011A8A4`), not a
    direct textual call; `musyxSynthFrame` separately self-registers into that table via a one-time call
    through a DMEM-mixer callback pointer at `0x801499D4` (installed by `initN64RspMixer`). Landed a
    4-site diagnostic (`ROGUESQ_LOG_AUDIOTICK_TRACE`: `[vi-cb-loop]`, `[vi-cb-slot]`, `[synth-entry]`,
    `[synth-rearm-ptr]`) plus a 4th reversal of `setDisplayMode`'s gate site to reproduce the freeze in
    one soak. Result: the freeze reproduced identically (VI stuck at 320, `rdpFs` pinned at 39) but all
    4 new diagnostics show `viRetraceHandlerThread`'s loop, the callback-table slot holding
    `musyxSynthFrame`'s address, and `musyxSynthFrame`'s own entry ALL keep firing 40+ times, well past
    the tick-19/20 point where the audio-tick counters stop — **refuting H1** (the driving thread/chain
    stops being invoked) at the outer level. Combined with an independent source-read finding no
    `M_AUDTASK`-specific bounded queue exists anywhere in the runtime, **H4 is also refuted**. The freeze
    is narrowed to something inside `musyxSynthFrame` (or a callee it reaches on the "run" branch) that
    changes starting at tick ~20 — H2/H3 territory; the existing `[musyx-gate1]` countdown/period print
    was uninformative (constant across its own 20-sample cap, which can't show a change at tick 20).
    `setDisplayMode`'s site re-reverted to force-zero same session (baseline restored, verified rebuilt);
    the 4 new diagnostics kept, armed-but-inert by default. Full detail: `PORTING-STATE` Session 310.

-169. **(s309) M5 audio de-stubbing: source-read overturns s307's "lockstep" claim — see Overturned
    Conclusions.** `main.cpp` source-confirms the `[runner]` (RSP-task) and `[audtask-dispatch]`
    (audio-tick) counters are separate code paths (`factor5_gfx_runner` for `M_GFXTASK` only; a distinct
    branch for `M_AUDTASK`), and re-reading s307's own log shows they stop at different points, not
    together — audio ticks stop at tick #19 while 18 more RSP tasks dispatch cleanly with the scheduler
    provably still healthy (1550 sched-log lines, same 7 threads cycling), before a separate, later
    full-scheduler wedge hits at RSP task #39. No soak run this session (pure source-read of an existing
    log, per the work unit's own instruction). Next work unit: a thread-identity diagnostic to find which
    of the 7 scheduler-visible threads drives the audio tick, and whether it's scheduled-but-silent after
    tick #19 (points at a gate/branch inside `viRetraceHandlerThread`/`musyxSynthFrame`) or stops being
    queued outright (points at whatever wakes that thread). Full detail: `PORTING-STATE` Session 309.

-168..-160. **(s297-307) M5 audio de-stubbing step 4: gate-byte reversal investigation — IN PROGRESS**
    (active thread, `HYPOTHESIS-ID: m5-audio-destub-step4-setdisplaymode-hang`). Condensed narrative
    also at USER DIRECTIVE item 2 above; full session detail: `PORTING-STATE` Sessions 297-307.
    - s297: lands `MATEXPIRY_GUARD` on `tickTextureMaterialExpiry`; 2 soaks clean, 0/2 fires (weak
      null, unconfirmed-not-refuted).
    - s298: writes `docs/M5-AUDIO-PLAN.md` — 6-step incremental audio de-stub sequence, one validation
      soak per step.
    - s300: source-reads the gate byte (`0x800A0F50`) — its only consumer, `musyxSynthFrame`, skips 3
      ancillary functions (`update3DAudioFrame`/`tickAllActiveSongs`/`tickAudioSequencerFrame`) at
      gate=0; lands an always-on `[audtask-dispatch]` counter proving real ucode task submission runs
      continuously regardless of the gate.
    - s301: lands a bounded-timeout guard on `waitForAnyAudioSlot`, 0/3 fires across 3 soaks — inert
      safety net, ready for the reversal.
    - s302: reverses `initMusyXEngine`'s gate site (`0x8008E9F8`); 2 soaks, 0/2 family #1 recurrence —
      **later OVERTURNED s306**: the function is dead code, never called, so this validated nothing
      (see Overturned Conclusions).
    - s303: reverses `setDisplayMode`'s gate site (`0x8008EB40`); **2/2 soaks hang identically** — VI
      stuck at width 320, exactly 39 RSP tasks, never reaches title, no crash. Re-reverted same
      session.
    - s304: source-read refutes both anticipated hypotheses (wrong value; call-frequency) — both sites
      write the same simple constant, both are boot-once. Surfaces the toggle-structure difference
      (setDisplayMode zeros-then-resets the gate around its own call) and flags `initMusyXEngine`
      reachability as single-source-unconfirmed (0 grep hits anywhere outside its own body).
    - s306: same-run-positive-controlled reachability counter (2 soaks, one a clean 300s full hold)
      **confirms `initMusyXEngine` is never called** — retroactively invalidates s302's validation;
      arms 3 gate-consumer entry/exit tags for the next reversal attempt.
    - s307: re-reverses `setDisplayMode`'s site a 3rd time with s306's tags live — **reproduces the
      hang a 3rd time but localizes it**: all 3 previously-suspected functions complete 20 clean
      entry/exit pairs before the freeze, clearing them as the hang site. Cross-referencing the RSP
      task-runner log: task #39 is the last ever dispatched, in lockstep with the audio-tick freeze
      (stuck at n=19) — both followed by pure scheduler churn with no new work. Points to a shared
      upstream resource (likely the coop-scheduler wakeup chain), not the 3 gated functions. Reverted
      same session.
    - **Current state**: `initMusyXEngine`'s site alone reversed (validated as a dead-code no-op, not
      a real gate=1 test); `setDisplayMode`/`reapplyDisplayMode` still force-zero every call. Gate=1
      has never been exercised by any soak to date. Next work unit (NEXT.md): trace why RSP task #40
      never arrives after task #39's clean exit — the task-submission producer and/or scheduler
      wakeup logic, not the 3 gated functions (now cleared).

-159..-132. **(s267-294) Breadcrumb whack-a-mole B2-B14 plus the `-0x25A4` hangar-list-pointer audit lineage — CLOSED.** From a refuted a0-argument hypothesis for a guest-`0x80000000`-family fault inside `heapFreeListDequeue` (s267), single-function breadcrumbs `BREADCRUMB2`-`9` chased the "cached free-list-head" idiom across 7 functions (s268-282; most soaks caught it recurring in a different already-known function than their own target); a 3-session `BREADCRUMB9` PRE-SCENE `waitForAnyAudioSlot` boot-crash streak (s277-280) turned out to be a transient window, CLOSED as a non-finding s289. s283-288 then ran a deliberate grep-based audit of every `-0x25A4($s1)` hangar-list-pointer site, landing 29 guards across 3 functions (s284), a 3rd "second-hop" instance (s285), classifying `hangarInitialize`'s remaining chunks as dead code (s286-287), and closing the lineage s288 (a suspected `playerSnowSpeederInit` overlap was REFUTED — live code merely sharing address space, not a copy). Separately s289-294 resumed the abandoned s249-251 project-wide unguarded-walk sweep (`find_unguarded_walks.py`, 143 sites/43 functions), landing `BREADCRUMB10`-`14` on 5 functions — no unique bug in most, but s293/294 caught `tickTextureMaterialExpiry`'s (`BREADCRUMB12`) two recurrences at the identical guest PC, crossing the confirmation bar s297 used to land `MATEXPIRY_GUARD`. Full detail: `PORTING-STATE` Sessions 267-294.

-130..-131. **(s265-266)** Landed the "last-executed-guest-PC breadcrumb" instrument (`g_rs64_last_guest_pc`, s264's flagged investment), verified it works; the originally-targeted `submitSceneNodeRender+19268` crash didn't recur in 6 soaks (s265). A re-soak per the same plan then caught a genuine different-offset crash (+47120), localized via the new breadcrumb to a 2nd previously-unguarded occurrence of s197's "cached free-list head" idiom, landing `CACHE2_GUARD` (s266) — 2 post-fix soaks clean, but surfaced a different, higher-priority bug. Full detail: `PORTING-STATE` Sessions 265-266.

-129..-114. **(s249-264) `composeNpcOrientationMatrix` whack-a-mole CLOSED; genesis of the unguarded-walk static sweep.** The 9-guard whack-a-mole (open since s100) closed for good s261 (`COMPOSE_NPC_GUARD9`): first-ever live call into `renderUnlitMeshFaces`, survived to VI-update #8552/143.1s (prior best ~75s), converged on the recurring "KSEG0 pointer + rdram-base, no `MEM_W` subtraction" signature in `renderUnlitMeshFaces` (7th occurrence; see s216-219 under Overturned Conclusions). Also closed: `setLookupEntryField5ByKey` needed two guards not one (s260, a 2nd-level pointer inside the callee); `evalCubicSplineAtTime`'s unguarded pointer (s259); the last 2 `-0x25A4` hangar-bay-deref gaps (s258); `submitSceneNodeRender` finally got a complete source read (s263) after 66 sessions unaddressed. Separately, s249-251 opened the project-wide static sweep for this "RDRAM-base + un-subtracted wild pointer" family: a candidate-finder script (`scratch/agent/find_unguarded_walks.py`, 143 sites/43 functions) landed, 2 functions fully guarded from it -- then it sat abandoned 43 sessions until s294 resumed it (item -159 above). Full detail: PORTING-STATE Sessions 249-264.

-113..-85. **(s220-248) Three interleaved threads: Metal-crash fixes, the CALayer/campose SIGSEGV hunt, the freeze/scene-graph investigation.** (a) Two Metal-side crashes CLOSED with positive controls: the scissor-rect OOB SIGABRT (s246) and the `fbSize()==0` viewport-NaN SIGABRT via a VI-draw skip guard (s244). (b) The host QuartzCore/CALayer SIGSEGV hunt (`campose*`, s234-248) landed a wall-clock bridge and a validated instrument, but exhausted its rule-8 budget at s248 still inconclusive -- best remaining lead: a cross-thread `CAMetalLayer` property mutation (PORTING-STATE Session 239). (c) The post-SELECT-CRAFT freeze investigation (s220-226) proved the frozen picture (torn polygon -> flat fill, non-deterministic even on identical scripted input) sits downstream of a healthy scene-graph traversal and a still-climbing RDP full-sync counter -- not a stuck camera or frozen pointer. Also: the DL-payload-staleness probe (s230-233) stayed ambiguous, and a Bash-allowlist bug (`Bash(<dir>/:*)` rules silently not matching, s227-228) blocked 2 sessions before resolving s229. Full detail: PORTING-STATE Sessions 220-248.

-84..-26. **(s150-219) The long `heapWalker`/`renderUnlitMeshFaces`/`composeNpcOrientationMatrix`/`heapFreeListDequeue` whack-a-mole guard-gap chase.** ~70 sessions landing one unguarded-pointer-chase guard at a time, converging on 2 durable lessons: the literal `0x0000000300000000` at x0/x8 across 3 unrelated crash sites is this process's constant RDRAM host base pointer, not corrupted data (s219, see Overturned Conclusions); the real wild operand is the *other* register, with a KSEG0-tag signature recurring in `renderUnlitMeshFaces` specifically. Also settled: "single Start leaves SELECT YOUR CRAFT into hangar-flight" **OVERTURNED s150** (mission-entry unanswered again); the s162 post-leave cutscene stall is the s79/80 FULL_SYNC-loss class recurring, capable of at least one recovery (s153/154); a `[thr-resume]`-adjacent scheduler silent-drop mechanism (s180-187) got a defensive guard that produced the first fully crash-free full-length soak in that lineage (s187). Full detail: PORTING-STATE Sessions 150-219.

-25..-21. **(s133-149) Audio-array corruption (Thread B) — CLOSED, plus two side threads parked at exhausted rule-8 budget.** Real mechanism (non-atomic `voiceCount`-write-before-pointer-store race in `allocateSongChannelArray`) found s145, FIXED and verified s147/148: 3 independent verification soaks all clean — 0/13 corrupted `[voice-active-gate-nz]` reads post-fix (vs. 5 pre-fix), 0/3 `do_rom_read` recurrences (vs. 9 prior), first fully crash-free soaks for this shape since s83. **s149 bonus**: "what input leaves SELECT YOUR CRAFT" was never actually open — the leave transition fires correctly (invisible to VI-phase tracking); the real open question was always surviving the post-leave scene's first ~2s. Path to the fix (s138-146): ruled out a static ROM string table and adjacent-heap aliasing (confirmed voice-array stride is 136 bytes); traced to `allocateSongChannelArray`'s own 2nd alloc, a per-tick-toggled double-buffered pointer table (s141-143), via `musyxMixActiveVoices`'s unchecked-cursor write (s144) before s145 found the race. Two side threads exhausted rule-8 budget without resolving (guards left in code): `emitAllocatedDLCommand` (s133-135, `emit-dl-guard2`/`3` 0/0 all 3 attempts, both deaths unrelated pre-existing classes); `submitSceneNodeRender`'s `MATLIST_GUARD1`/`GUARD2` (s136-137, parked at 2/3, both 0/0, both dying to the `do_rom_read` race). Full detail: `PORTING-STATE` Sessions 133-149.

-20. **Regen-pipeline reliability bug (s120, confirmed intermittent not deterministic).** Root cause:
    `N64Recomp` skips rewriting any `RecompiledFuncs/funcs_*.c` file that already exists on disk, so
    any patch whose regex anchor survives its own insertion stacks a duplicate on the next
    `fixup_game_funcs.py` run unless the file is deleted first. Deleting all `funcs_*.c` before every
    regen is mandatory but **not sufficient by itself** -- residual intermittency's root cause is
    still unknown. **Standing rule**: audit the patch report for anything other than the expected `xN`
    count after every `fixup_game_funcs.py` run. Full detail: `PORTING-STATE` Sessions 120, 121, 126.

-19..-17. **(s102-135) Thread A/B saga leading to the s145/147/148 fix above, plus the regen-pipeline root cause.** Thread A (s126-132): re-audited every already-guarded hangar-tick crash class for a 2nd unguarded pointer-chase site — 6/8 had a genuine gap; biggest hit `updateHangarBayScene`'s `-0x25A4` family (26 sites, s132), later fully closed by the s282-288 audit lineage. Thread B (s116-145): chased the `voice+0x0`/`+0x34` corruption through several reframings (refuted: stale `rs_malloc` memory, an OOB scan index, an RSP-ucode write, a computed-offset guest-C store, adjacent-heap aliasing). Earlier (s102-113): traced the corrupted MusyX DMA-batch `devAddr` field backward across 6 sessions/5 functions to `musyxInitVoiceFromSample`, the sole writer of that offset anywhere in the tree (s105/s111 exhaustive grep); the call-chain-ancestry angle (s105-110) was a 5-session dead end. **Methodology lesson**: comparing instruments' log lines by *file order* across threads is not a valid proxy for real time order — cross-thread correlation needs a shared sequence number. **Tooling** (s102, root-caused precisely by item -20 above): `fixup_game_funcs.py` is not idempotent — re-running it without a full ELF regen inserts a second copy of every already-applied patch. Full detail: `PORTING-STATE` Sessions 102-135.

-16. **M3 hangar-tick-family guard program (s99-s110): 8 crash classes guarded** (16th/12th/11th/14th/17th/18th/9th/10th — see crash catalog, `docs/PROJECT-OVERVIEW.md` §7), all with clean negative controls, same `U32()`-truncated-bounds-check-then-`goto`-real-epilogue template used by every guard since. s101 and s110 survived the entire family with zero crashes, reaching the ~140s DMA-corruption window alive. Full detail: `PORTING-STATE` Sessions 99-101, 109-110.

-15. **M3 -- find the indirect caller of `submitDmaRequestBatch`: CLOSED (s101).** The caller is `musyxSynthFrame` (`funcs_24.c:3095`, a per-VI-retrace audio tick) via `viRetraceHandlerThread` — not the mission/DL code path every earlier session assumed. Refuted dead ends, do not reopen: `ra=0x00000000` as a corruption signature, "dump the OSIoMesg at mb," consumer index desync, "the boot call loops more than once." Crash catalog (19 classes, s83-s110): `docs/PROJECT-OVERVIEW.md` §7 — all guarded/closed except #19 (1 occurrence, never recurred). Full detail: `PORTING-STATE` Sessions 93-110, 124-132, 159, 195-196.

-14. **M3 — `queueGPUUploadTMEM` zero-size assert.** Crash classes 9/10 (`updateAnimatedTextureStreaming`/`static_5_800B4048` SIGBUSes) CLOSED s124/s125, tracked in the crash catalog only.

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
- **(s307→s309)** "the RSP-task freeze and the audio-tick freeze land at the same point (task #39/tick
  #19), pointing to one shared upstream resource that stops feeding both" — a source-read of
  `main.cpp` found the two counters live on entirely separate code paths (`[runner]` inside
  `factor5_gfx_runner`, `M_GFXTASK`-only; `[audtask-dispatch]` a distinct `M_AUDTASK` branch, never
  routed through the former), and re-reading s307's own log by line number (not just by tick/task count)
  shows audio ticks stop at line 3013 while RSP tasks keep dispatching cleanly for 18 more tasks through
  line 4943, with 1550 scheduler log lines proving the cooperative scheduler stays healthy throughout
  that gap — only *after* task #39 does scheduling activity stop entirely. Two sequential, distinct
  stalls, not one shared cause. Believable: both counters hit round, similarly-small numbers (39 and 19)
  in the same log and both are followed by "scheduler churn with no new work," which reads as
  simultaneous unless the actual line numbers and thread-identity sets are diffed. PORTING-STATE 309.

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
