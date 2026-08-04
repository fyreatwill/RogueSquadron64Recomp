# Rogue Squadron 64 Recomp — current truth

Front matter for `PORTING-STATE.md`, which is chronological and contains superseded conclusions.
New here, or back after a break? Read **`docs/PROJECT-OVERVIEW.md`** first — what the project is, how the four layers fit together, and the hurdle classes that have cost the most time.
Session tags: `s1` = 2026-07-09/10 build + overlay work, `s2`–`s9` = the `## LLE session N` headings, `s10`–`s32` = the `## Session N` headings.

## USER DIRECTIVE (2026-08-04, human-set — overrides Next-steps ordering until satisfied)
Priority order for upcoming iterations, set after the 300-session review:
1. **Maintenance** (Step 0 of ITERATION.md triggers it at 60,000 bytes): compact per the Maintenance
   section of tools/agent/ITERATION.md; a >=200-net-line shrink counts as ADVANCED. Compaction history:
   s295/296 (562,666→59,811 bytes), s299 (61,293→47,105), s305 (62,103→54,550), s308 (60,540→45,772
   bytes, 692→458 lines, 234 net), s314 (60,051→34,745 bytes, 605→397 lines, 207 net — condensed the
   s309-312 Next-steps items -172..-169 into one summary; migrated the s99-294 closed investigation
   lineages and the instrument-specific Method Traps to `docs/PROJECT-OVERVIEW.md` §8/§9; tightened
   the Goal-stack M3/M4 descriptions, the menu-state-machine/defects/stability prose, and the last 3
   Overturned Conclusions entries). 35 KB remains a stretch target, not a hard floor — the "Current
   truth" env-var/timeline prose and the Regeneration section's Standing warnings stay intact
   deliberately; both are used every iteration for phase-gating and build commands.
2. **M5 audio de-stubbing**: design doc DONE (s298), steps 1-3 DONE (s300/301). Step 4 (reversing the 3 audio-gate-byte force-zero sites) IN PROGRESS, `HYPOTHESIS-ID: m5-audio-destub-step4-setdisplaymode-hang`. `setDisplayMode`'s site reversed/re-reverted 9 times (s303-316), each reproducing an identical deterministic full-boot hang and narrowing it further. Current state (s316, direct measurement): the 3-gate-copy model for what actually fires the tick-producer functions is now contradicted by direct instrumentation — full detail Next-steps item -175.
3. **M3 crash work only as systematic idiom-class audits** (the s282–s288 `-0x25A4` model), never
   reactive single-crash chases. Breadcrumbs are passive: enqueue soaks to scratch/agent/soak_queue/
   (the loop runs them between iterations), consume scratch/agent/SOAK-RESULTS.md.
Sanctioned tooling work unit, counts as ADVANCED whenever picked up: backport function-scoped matching (the BREADCRUMB10+ slice idiom) to the ~100 file-scoped-only guard patches in fixup_game_funcs.py, per the 2026-08-04 analysis in that file's header comment.

## Current truth (as of session 295; unchanged and reviewed through s313)

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
move; what a leave-key actually leads to is unresolved. *Done when:* 60 seconds of in-mission
rendering, craft visibly responds to synthetic input, stability counters 0, and the phase timeline
in this document covers the mission.

**M4 — parked correctness items**, one work unit each: outdoor `baseFixed = −32768` zero-shade root
cause; S=0 triangles in the 640 attribution phase; the I4 `sample=64x128` anomaly if M1 didn't
consume it; the 3 `[missing-func]` addresses in the undriven outdoor-512 stretch — root-caused and
fixed s53/54 (3 mission-overlay symbols misassigned to `main_overlay.txt`; see Next-steps item -6),
**runtime confirmation still outstanding**.

**M5 — audio de-stubbing (investigation first, not code).** The MusyX audio ucode already
recompiles (`factor5_ucode_b_recompiled.c` sits in the build as a never-called artifact). First
work unit: a design doc only — how audio tasks would run LLE alongside gfx (they share the `dmem[]`
serialization built in s5), what bridges RSP audio output to SDL, and what the audio-gate byte
reversal implies. **Gate M5 behind M2**: audio re-enters exactly the shared-state territory that
cost three sessions before the recursive mutex.


## Next steps, in order of expected value (s295)

Numbering convention (fixed s295, was previously three colliding sequences): items are
numbered highest-magnitude-negative (top, newest/highest priority) counting up to -1 (bottom,
oldest). Current top is -175 (s316); the next new item takes -176 and is inserted at the top.

-175. **(s316) M5 audio de-stubbing: the 3-gate-copy model for what fires the tick-producer functions
    is unconfirmed — direct instrumentation of gate2/gate3 contradicts it.** Item -174 asked why
    `tickAllActiveSongs`/`tickAudioSequencerFrame`/`tickAllAudioChannels` stop 3 calls before everything
    else (37 vs 40). Step 1 sanity check (grepped `fixup_game_funcs.py`'s patch definitions) confirmed
    these ARE 3 genuinely distinct functions, not a double-counted call site — no labeling artifact.
    Step 2 (source-read + interleaved log analysis) found the 3 near-identical countdown gates inside
    `musyxSynthFrame` (`funcs_24.c`, reads at ~0x80091474/0x80091534/0x800915E8, all sharing ONE
    countdown at `G_BASE-0x68EC`) are the only static call sites to `tickAudioSequencerFrame`/
    `tickAllActiveSongs` anywhere in `RecompiledFuncs/*.c` (grep-confirmed exhaustive). Only gate1 had
    ever been instrumented (s108, cap widened s311, taken-outcome added s312) — 4 sessions measured its
    raw countdown/period inputs but never checked whether it ever actually took the "call" branch.
    Added the identical diagnostic to gate2 and gate3 (`[musyx-gate2]`/`[musyx-gate3]`), one soak
    (`setDisplayMode`'s site reversed a 9th time to match s315's run conditions, re-reverted same
    session). **Result: none of the 3 gates ever takes the "call" branch.** gate1: 40/40 samples,
    `taken_skip=1` every time. gate2: only 4 of its containing loop's iterations are ever reached at all
    (n=0..3, then the loop stops being entered) — all 4 `taken_skip=1`. gate3: **0 samples, its
    containing code path is never reached once** in the whole 600s run. Yet `tickAllActiveSongs`'s own
    independent entry counter confirms 37 real calls happened in the same run/log. Direct contradiction:
    the only known call sites, sampled exhaustively, account for zero of the 37 observed calls. Two
    explanations survive: (a) an unlocated indirect/function-pointer call site (a textual grep would
    miss this — s310 found exactly this pattern one level up, for `musyxSynthFrame`'s own invocation via
    a VI-retrace callback table), or (b) a subtle addressing/polarity error in the gate model despite it
    matching the disassembly pattern exactly. `setDisplayMode`'s site reverted, baseline restored and
    rebuilt. Full detail: `PORTING-STATE` Session 316.

-174. **(s315) M5 audio de-stubbing: `[audtask-dispatch]` REFUTES its own "M_AUDTASK submission stops
    at call 20/20" conclusion — see Overturned Conclusions.** Before source-reading
    `tickAudioSequencerFrame`/`tickAllAudioChannels` to hunt the gate item -173 asked for, checked the
    instrument first: `get_rsp_microcode()`'s `M_AUDTASK` case in `src/main/main.cpp` (native runtime
    code, not `fixup_game_funcs.py`) had the exact same unwidened flat-cap bug (`n<20 ||
    n%256==0`) s312/s313 found and fixed in 4 *other* M5 audio diagnostics — a log stopping at exactly
    20 lines was indistinguishable from "really stopped" vs. "kept incrementing silently until n=256,"
    and the ~40-call hard-stop boundary this investigation keeps finding never reaches 256. Widened to
    the established `n<40||(n%128)==0` convention, reversed `setDisplayMode`'s site an 8th time, ran
    one soak. **Direct measurement**: `[audtask-dispatch]` fires **40/40** (n=0..39), matching
    `update3DAudioFrame` (`[reach-update3d-*]`, also 40/40) and the RSP task-runner's own last dispatch
    (task #39) — not 20/20. `tickAllActiveSongs`/`tickAudioSequencerFrame`/`tickAllAudioChannels`
    unchanged at **37/37**. **Result: 2 distinct stop points, not 3** — a 37/37 stop (the 3
    tick-producer functions) and a 40/40 hard stop (`update3DAudioFrame`, `M_AUDTASK` submission, and
    the RSP task-runner together). `M_AUDTASK` submission was never diverging from its own upstream
    callers; that was the same print-cap illusion. Open question narrowed, not answered: why do the 3
    tick-producer functions stop 3 calls before everything else (37 vs 40)? `setDisplayMode`'s site
    reverted, baseline restored and rebuilt. Full detail: `PORTING-STATE` Session 315.

-173. **(s313) M5 audio de-stubbing: widened-cap soak REFUTES the "3 gate-consumer functions stop at
    call 19/20" conclusion — see Overturned Conclusions. Superseded by item -174 (s315): the
    `[audtask-dispatch]` count in this item's own table was itself unwidened and wrong (20/20, actually
    40/40) — kept for the update3DAudioFrame/tick-producer numbers, which s315 confirmed unchanged.**
    Widened the flat `n<20` print caps on
    `[reach-update3d-entry/exit]`/`[reach-allsongs-entry/exit]`/`[reach-audioseq-exit]`/
    `[tick-audio-seq]`/`[tick-all-audio-channels]` to the resampled `n<40||(n%128)==0` convention,
    reversed `setDisplayMode`'s gate site a 7th time, ran one soak, re-reverted same session. **Direct
    measurement**: `[reach-update3d-entry/exit]` (`update3DAudioFrame`) fires all **40/40** times,
    matching the hard-stop boundary (RSP task-runner's last dispatch, task #39) — not 19/20.
    `tickAllActiveSongs`/`tickAudioSequencerFrame`/`tickAllAudioChannels` stop 3 calls earlier, at
    **37/37** — a real, smaller, previously-unmeasured stop point, also not 19/20. Only
    `[audtask-dispatch]` (RSP `M_AUDTASK` submission, already resampled since s310/s311) genuinely
    stops at **20/20**. Three distinct stop points, not one shared soft stop — the old framing was an
    artifact of the unwidened flat cap, as s312 suspected. New open question: why `M_AUDTASK`
    submission (call 20) diverges from its own 2 upstream tickers (call 37) and from
    `update3DAudioFrame` (call 40). `setDisplayMode`'s site re-reverted, baseline restored; the widened
    caps kept, armed-but-inert by default. Full detail: `PORTING-STATE` Session 313.

-172..-169. **(s309-312) M5 audio de-stubbing step 4: incremental instrumentation narrowing the
    tick-19 stall, each step's conclusion superseded by s313's direct measurement (item -173 above).**
    s309: source-read of `main.cpp` overturned s307's "lockstep" claim (see Overturned Conclusions) —
    `[runner]` (RSP-task) and `[audtask-dispatch]` (audio-tick) are separate code paths, stopping at
    different points (tick #19 vs. task #39), not together. s310: found the real `musyxSynthFrame`
    invocation mechanism (an indirect call through a 4-slot VI-retrace callback table, not a direct
    textual call — a literal-text grep had missed it) and landed a 4-site diagnostic
    (`ROGUESQ_LOG_AUDIOTICK_TRACE`) showing `viRetraceHandlerThread`'s loop, the callback slot, and
    `musyxSynthFrame`'s own entry all keep firing 40+ times — refuting H1 (driving thread stops) and
    H4 (unreaped queue; source-confirmed no such queue exists), narrowing the stall to inside
    `musyxSynthFrame`/a callee. s311: widened `[musyx-gate1]`'s sample cap and ran a full 10-minute
    capture, ruling out that gate's raw countdown/period inputs (constant across all 40 samples) and
    finding **two apparently-distinct freeze boundaries** — a SOFT stop at call #19/20 (3
    gate-consumer functions + `M_AUDTASK` submission) and a HARD stop at call #39/40 (everything,
    matching the RSP task-runner's last dispatch, task #39). s312: source-read of `musyxSynthFrame`
    found `[musyx-gate1]`'s branch is provably always "skip" in this window (not gating anything), and
    that `update3DAudioFrame` has its own independent single-byte gate (`0x800A0F50`) which a new
    `[audio-gate-raw]` diagnostic measured constant-nonzero across 40/40 samples — in direct tension
    with the "stops at 19/20" framing, traced to an unwidened flat `n<20` print cap (no modulo resample)
    in the diagnostic that produced that framing. **s313 then widened those caps and directly measured
    the true call counts, settling the question** (item -173): not one shared soft stop, but three
    distinct stop points. `setDisplayMode`'s gate site was reversed and re-reverted every session
    (baseline restored each time); all diagnostics from this run kept, armed-but-inert by default. Full
    detail: `PORTING-STATE` Sessions 309-312.

-168..-160. **(s297-307) M5 audio de-stubbing step 4: gate-byte reversal investigation — lead-up to
    item -173's current state, superseded by direct measurement.** `HYPOTHESIS-ID:
    m5-audio-destub-step4-setdisplaymode-hang`. s297-301 built the instrumentation runway:
    `MATEXPIRY_GUARD` (0/2, weak null), `docs/M5-AUDIO-PLAN.md` (s298), a source-read of the gate byte
    `0x800A0F50` confirming `musyxSynthFrame` is its only consumer and an always-on
    `[audtask-dispatch]` counter (s300), a bounded-timeout guard on `waitForAnyAudioSlot` (s301, 0/3).
    s302 reversed `initMusyXEngine`'s gate site — later OVERTURNED s306 (dead code, never called, see
    Overturned Conclusions). s303/s307 reversed `setDisplayMode`'s gate site twice more, both
    reproducing the identical hang (VI stuck at 320, 39 RSP tasks); s304's source-read found both
    gate sites write the same boot-once constant; s306's reachability counter confirmed
    `initMusyXEngine` dead code and armed 3 gate-consumer entry/exit tags; s307 used those tags to
    localize the hang to a shared upstream resource rather than the 3 gated functions themselves
    (later refined by s309-312, item -172..-169, then settled by s313's direct measurement, item
    -173). Full session detail: `PORTING-STATE` Sessions 297-307.

-159..-14 (excluding -20, kept below). **Nine closed investigation lineages, s99-s294 — all CLOSED,
    no outstanding action.** Whack-a-mole guard-gap chases (`composeNpcOrientationMatrix`,
    `renderUnlitMeshFaces`, `heapWalker`, `heapFreeListDequeue`, the `-0x25A4` hangar-list-pointer
    family, breadcrumbs B2-B14), the audio-array-corruption race fix (s145/147/148), the
    `submitDmaRequestBatch` indirect-caller find (s101), the CALayer/campose SIGSEGV hunt, and the
    regen-pipeline-idempotency root cause. Full one-paragraph-per-lineage summaries migrated to
    `docs/PROJECT-OVERVIEW.md` §9 (this session's maintenance pass); full raw detail remains in
    `PORTING-STATE` Sessions 99-294.

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
- **(s302→s306)** "reversing `initMusyXEngine`'s gate-byte site validated safely (0/2 family #1
  recurrence)" — a positive-controlled entry counter found `initMusyXEngine` is never called at all,
  so the reversed write never executed; the clean result reflects dead code, not a validated gate=1
  state. Believable: the soaks genuinely were clean with real ucode dispatch confirmed throughout —
  only a dedicated reachability instrument could show the line hadn't run. Gate=1 still never
  exercised by any soak. PORTING-STATE 306.
- **(s307→s309)** "the RSP-task freeze and audio-tick freeze land at the same point (task #39/tick
  #19), one shared upstream resource stopping both" — `main.cpp` source-read found the two counters
  are separate code paths; re-reading s307's own log by line number (not tick/task count) shows audio
  ticks stop 18 tasks and 1930 log lines before the RSP-task freeze, with the scheduler provably
  healthy throughout that gap. Two sequential stalls, not one. Believable: both counters hit similarly
  small round numbers followed by "scheduler churn with no new work," which reads as simultaneous
  unless line numbers are actually diffed. PORTING-STATE 309.
- **(s307/s310/s311→s313)** "the 3 gate-consumer functions and RSP `M_AUDTASK` submission all stop
  together at call #19/20 (a SOFT stop)" — a widened, resampled print-cap soak (s313) found
  `update3DAudioFrame` actually fires 40/40 (the hard-stop boundary); its 2 sibling tickers stop 3
  calls earlier at 37/37; only `M_AUDTASK` submission genuinely stops at 20/20 — three stop points, not
  one. Believable: the flat `n<20` cap predates the modulo-resample convention (s310/s311) and nobody
  retrofitted it; a log truncated at exactly 20 lines is indistinguishable from a real stop without a
  resample. PORTING-STATE 313.
- **(s313→s315)** "`M_AUDTASK` submission genuinely stops at call 20/20" — `[audtask-dispatch]`
  (`src/main/main.cpp`, the RSP-scheduler dispatch point, not a `fixup_game_funcs.py` patch) had the
  identical unwidened `n<20||n%256==0` flat cap s313 had just finished fixing in 4 *other* diagnostics,
  missed because it lives in native runtime code rather than the recompiled-game-code patch file where
  the others live. A widened-cap soak (s315) found it actually fires 40/40, matching
  `update3DAudioFrame` and the RSP task-runner's own last dispatch — not diverging from its callers at
  all. Believable: s313 had just fixed the exact same bug pattern elsewhere in the same investigation
  and had every reason to believe the remaining tag was already resampled (`docs/CURRENT-TRUTH.md`
  s313's own item -173 explicitly called it "already resampled since s310/s311" without re-checking the
  source). 2 stop points (37/37 and 40/40), not 3. PORTING-STATE 315.
- **(s107/s108→s316)** "the 3 near-identical countdown/period gate copies inside `musyxSynthFrame` are
  the mechanism that fires `tickAllActiveSongs`/`tickAudioSequencerFrame`" — never validated with a
  positive control across 4 sessions (s108/s311/s312 all measured gate1's raw countdown/period inputs
  without ever observing it take the "call" branch). s316 instrumented the other 2 copies the same way:
  gate1 40/40 samples `taken_skip=1`, gate2 only 4/40 iterations ever reached (all `taken_skip=1`), gate3
  0 samples (never reached). None of the 3 known gates ever fires the call in this run, yet
  `tickAllActiveSongs` independently logs 37 real calls. The true call site is still unidentified.
  Believable: the disassembly pattern (decrement, reload-on-zero, conditional call) matched exactly, and
  raw-input constancy looked like sufficient evidence without checking the branch outcome itself.
  PORTING-STATE 316.

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
