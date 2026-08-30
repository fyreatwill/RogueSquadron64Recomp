# Rogue Squadron 64 Recomp — current truth

Operational state for [`PORTING-STATE.md`](../PORTING-STATE.md). Durable
background is in [`PROJECT-OVERVIEW.md`](PROJECT-OVERVIEW.md); exact run
recipes and evidence remain in the ledger and `scratch/agent/`.

Current maintenance marker: Session 3309 (2026-08-30). Compacted from
61,424 bytes / 1,094 lines; durable s3201–s3302 archive is
PROJECT-OVERVIEW section 54.

## Live investigation (s3303–s3308)

Session 3308 port-censused `cinematicStageAdvancer` (`0x800AF550`)
in one build and one 120 s retry. The first launch crashed at VI
320 in `spTaskSchedulerThread` (`last-guest-pc=0x8000834c`) before
marks; the same-binary retry is the live scope. Controls: 6/6
stage-adv marks, 7/7 cine-loop marks, 24/24 s3305 marks,
completion-wins 61, request-reset 61, SP-complete 64, VI
`640 @ 0x0066A500`, viewer return, cinematic entry, loop-head, and
exit-gate. Ptr-check `0x800AF55C` ran n=138 all `$v1=0` `taken=1`.
Silent: fp-compare `0x800AF590`, stage-lt7 `0x800AF5B4`, ret-one
`0x800AF5BC`. ret-zero `0x800AF604` `$v0=0`. Entry `$a2` is 1/60
then 1/30. Same-run `[phase] cineState` is 0 after boot (83 rows)
via `rdram_be32_at(0xB0934)`. This selects `H-PtrZeroSkip` and
refutes `H-DtBelowThreshold`, `H-StageNeverHits7`, and retry
`H-CoverageInvalid`. The 6074 gate stays 0 because the skip
returns 0. Named guest writer is `cinematicInitializer` `sw` at
`0x800AF4B8`; named clearer is `cinematicDeactivator` `sw $zero`
at `0x800AF640`. No M5 Step 3. Evidence:
`scratch/agent/s3308_stage_advancer.md`.

The queued 600 s soak (`s3307_cine_loop_600s`) was SIGKILL at
600 s with no crash, no title 1024, and exit-gate `v0_nz=0`
(printed n=100). The scheduler was still matching recv at width
640 origin `0x696100`. That extends `H-PortLoopNoExit` and is
consistent with `H-PtrZeroSkip`.

Session 3307 port-censused the Session 3306 cinematic loop/exit
edges. Same first-launch crash at VI 320; the same-binary 121 s
retry is the live scope. Controls: 7/7 cine-loop marks, 24/24
s3305 marks, completion-wins 69, request-reset 69, SP-complete
64, VI `640 @ 0x0066A500`, viewer return, and cinematic entry
`$a0=0x13`. Early-exit `0x800A5DD8` `$v0=1` not taken. Loop-head /
exit-gate / backedge ran through printed n=150 (VI `#640`) with
gate `$v0=0` (`v0_nz=0`). Silent: `0x800A64BC`, `0x800A65E4`,
`0x800A6618`, second menu, title 1024. This selects
`H-PortLoopNoExit` and refutes `H-PortPrologueStall`,
`H-PortExitNoReturn`, and retry `H-CoverageInvalid`. Combined with
retail Session 3306, the port-only stop was
`cinematicStageAdvancer` never returning 1. Evidence:
`scratch/agent/s3307_cinematic_loop.md`.

Session 3306 asked the independent retail oracle for
`cinematicLoopBody`'s loop/exit path. The 90 s Rice run is the live
scope. Controls: 10000-write, `[gpr-ctl]`, VI `640 @ 0x0066A500` at
2.1 s, entry at 6.5 s, caller `0x8003E114` at 48.9 s. Early-exit
`0x800A5DD8` `$v0=1` not taken. Loop-head `0x800A6024` began at
10.4 s then 1002× `0x800A64B4`. Exit-gate `0x800A6074` was `$v0=0`
for 1002 first-cinematic iters, then `$v0=1` at 48.8 s into
`0x800A64BC`, epilogue, return `0x800A6618`, caller `0x8003E114`,
and second menu `0x8003E13C`. Title `1024 @ 0x00790400` at 49.2 s.
This selects `H-RetailFiniteLoop`. Evidence:
`scratch/agent/s3306_retail_cinematic_exit.md`.

Session 3305 censused the post-viewer continuation. All 24 mark IDs and
the arm/reset/SP/VI/viewer controls passed. The live path reached
`cinematicLoopBody` entry `0x800A5D80` and never reached `0x800A6618`
or title 1024. Session 3307 refined that missing return to
`H-PortLoopNoExit`. Evidence:
`scratch/agent/s3305_postviewer_continuation.md`.

Session 3304 promoted completion-wins/not-yielded status to the default and
added one request-reset helper to both weak and linked strong task-start
paths; request-only remains available as
`ROGUESQ_SP_YIELDED_REQUEST_ONLY=1`. The same-build pair passed arm,
pre=1/post=0 reset, SP-completion, viewer-entry, and 640-phase controls.
Default emitted 44 `requested=1 returned=0` / E60 rows, matched SENT/SRET
through n=100, and returned from the viewer. Rollback still died at SENT
n=3. Default never published title 1024 in 120 s (`H-ViewerOnly`). ORIGIN:
the request bit is legitimate, but it is not a legitimate yielded-task
result on a host with no interrupt/resume path. Evidence:
`scratch/agent/s3304_yield_lifecycle_default.md`.

Session 3303 ran the same-build port A/B for request-only
`osSpTaskYielded` versus diagnostic completion-wins. Both arms passed
`640 @ 0x0066A500`, viewer-entry, arm-row, and SP-completion controls.
Baseline reported `requested=1 returned=1`, took 19E70/19E80F 12 times,
and stopped at SENT n=3 / SRET n=2 / 2D50 n=3. Completion-wins reported
`requested=1 returned=0`, took 19E60, restored 19ED0/19F1C/19FE4,
returned SRET n=3, and advanced through matched SENT/SRET and 2D50 n=10.
This selects `H-FalseYieldStatus` and refutes `H-StatusOnly`,
`H-YieldStatusNotCausal`, and valid-pair coverage failure. Combined with
retail s3296/s3298/s3301, the causal conclusion is two-source. ORIGIN: the
request bit is legitimately written by `osSpTaskYield`, but is not a
legitimate yielded-task result because the host never interrupts/resumes a
task. Evidence: `scratch/agent/s3303_yield_status_ab.md`.

## Current state

The native port builds and boots through attribution, the N64 logo, intro
cinematic, star flare, Factor 5 logo, title VI 1024 (`0x00790400`), and hangar
VI 512 (`0x006AB400`) on the validated spin-yield/F5-LLE route. Hangar visuals
still have geometry/color artifacts. Audio is not production-complete: the
Factor 5 image task is the qualified real-audio arm and `musyx_stub`/Broke is
the silent control.

The current default after Session 3304 returns from the attract viewer
and enters `cinematicLoopBody` (`0x800A5D80`), then stays at VI
`640 @ 0x0066A500` because `cinematicStageAdvancer` always skips on a
null `0x800B0934`. Retail Session 3306 exits that loop at 48.8 s and
reaches title `1024 @ 0x00790400` at 49.2 s. Boot attract on both
sides is menu `$a1=9` → `runMenuModelViewerScreen` → cinematic →
second menu `$a1=2` (`0x8003E13C`), not the architecture sketch of
menu `$a1=9`, menu `(s3, 2, 0xB)`, then cinematic.

`H-PortTargetPublicationAbsent` still holds: the live post-640
publisher is `applyPendingViChanges` (`viRetraceHandlerThread` at
`0x80019914`); it requested width 640 at slot `0x80128DF0`. Retail
title 1024 rewrites all four OSViMode slot +8 words to `0x00000400`
via `initVideoSubsystem` (`0x8001B6B0`) from `advanceVideoFrame`
`0x80018378`. Port Session 3278 never published a 1024 template.

The latest same-build M5 image-versus-silent qualification passed
dispatch controls in both arms but reached only pre-title VI 640.
Independent retail controls reached title and hangar. Target-phase
audio/task/DMA/service/slot/voice/MORT/PCM nulls are unevaluable; no
audio, route, VI, gate, wait, voice, destination, or output change is
authorized without a named legitimate writer and ordering edge. Do
not remove the status-03 wait hatch.

Retail target-phase `osViSwapBuffer` (`0x80035500`) is caller
`0x8001BE24`, `$a0=0x80790000` (physical `0x00790000`), origins
`0x00790400/0x00790800`. The port has a target-row logger but never
emits the row (`H-PortRowMissing`). Session 3274's target-span writer
`0x800078EC` is `rs_memset`, not a VI publisher.

`PatchesLib` cannot be built on this Unix checkout: no target, cache
points at `E:/mips-toolchain`, no local `mips64-elf-*`, no generated
`RecompiledPatches/patches.c`. That is `H-GuardHostMissing`, not
guard evidence. Do not retry the local missing-target build. M5 Step
3 remains gated.

## Next steps

Priority is maintenance, M5 de-stubbing, systematic M3, then generated-symbol
renaming. M5 design is complete in `docs/M5-AUDIO-PLAN.md`. Session 3304's
completion-aware SP-yield lifecycle returns the viewer; Session 3308 shows
the cinematic exit-gate stays `$v0=0` because `cinematicStageAdvancer`
skips on `$v1==0` at `0x800AF55C` (`0x800B0934` null) while retail
Session 3306 returns at 48.9 s via `0x800A6074` `$v0=1` → `0x800A64BC`.
Session 3276's `H-PortTargetPublicationAbsent` still holds. No M5 Step 3
audio change is authorized until a like-for-like target row exists.

1. Independent retail write-watch of physical `0x000B0934` (guest
   `0x800B0934`) during first attract, plus exec of
   `cinematicInitializer` store `0x800AF4B8` and
   `cinematicDeactivator` clear `0x800AF640`. Whole-RDRAM 10000-write
   control, VI `640 @ 0x0066A500`, cinematic entry. Distinguish
   retail-live KSEG0 pointer, retail-also-zero, named-PC writer, and
   invalid coverage. Do not add audio/output changes. Keep the s3308
   table.
2. Session 3285 moved the 3270 alignment + cycle-cap class onto the
   generated host walks that link here. Remaining: validate
   `patches/heap_guards.c` on the configured Windows/MIPS host
   (`PatchesLib`). Do not repeat the local missing-target build. The
   guard is not evidence that the VI-640 route or audio is corrupt.
3. After the pre-VI-640 scheduler crash is repaired or explained, capture
   consumed-message identity at `0x80019CD0` with `ROGUESQ_RECV_TRACE`
   positive controls. Session 3269 selected `H-RecvWatchUnavailable`. Require
   caller, message pointer, type byte, and `89F/28D44` in the same phase.
4. Execute M5 plan Step 3 only after a valid target-phase Step 1/2 row names
   one missing image task/output contract edge. Keep the change to exactly one
   proven writer/consumer relation.
5. Closed static M3 classes, retain existing traps/guards as safety only:
   A8 key-on divisor, A12 `0x8014974C`, A9 voice-array base, A10 3D voice-list
   head, 43-site `SONGTEMPO_TABLE_GUARD`. `-0x68A8`/`-0x68B0` is
   `H-NotPatchable`. Status-03 is a named `stopVoiceSlotSynced` /
   `serviceVoicePoolFrame` contract.
6. Generated-symbol sweep remains closed (Sessions 3210/3212/3217).
7. M4 restage destination is hangar `gspTask` (`0x800377C8`) with physical
   `output_buff` `0x0075C000` / `0x00781800`. Keep the external retail-entry
   boundary, hangar `0x8000` Y / accumulator arithmetic, and M5 SP-yield/MORT
   publication threads parked pending a new target-phase discriminator. The
   corrected MORT descriptor edge is `+0x190` to `dmaVoiceSampleAndSignal`.

## Durable boundaries and operating rules

Factor 5 uses [`F5-UCODE-REFERENCE.md`](F5-UCODE-REFERENCE.md), not standard
F3DEX assumptions. The qualified graphics path is LLE-only. Interpreter
limits, null-GBI guards, and similar defenses are safety mechanisms, not
explanations. Overlay dispatch is fixed enough for the validated route.

Ask the independent retail oracle for ground truth before adding port
instrumentation. Every instrument needs a same-run positive control,
phase-scoped budgets, and two independent lines of evidence before promotion.
Phase-gate animated comparisons on VI transitions and build every A/B arm
together. A null without a positive control is worthless.

Regeneration order is `make_elf.py` → N64Recomp → `fixup_game_funcs.py` → CMake.
Never hand-edit generated functions for behavior changes. If `lib/` changes,
export submodule patches in the same iteration. Never run `git submodule update`,
`git checkout -- lib/...`, `git clean`, or `git reset --hard`. Kill runs with
SIGKILL and run from `build/`. A mitigation-shaped change requires an `ORIGIN:`
line naming the writer and stating whether the value is legitimate.

CMake's `RECOMP_FUNCS_DIR` is `../N64Recomp/RecompiledFuncs`. The recomp
direct C call to `submitGfxFrame` does not write guest `$ra` `0x800C2D98`
into `0x40($sp)`; a saved-ra viewer gate on that word is dead. Static
boundary-only symbol classifications remain non-renames when companion
symbols, source/m2c, callers, and local semantics do not provide a
defensible name. Stable companion duplicate-prefix and preamble mappings
belong in `tools/rename/build_redefs.py`.

`--pc-phase-log-width` defers `--watch-pc` until the first listed VI
bucket (`g_defer_exec_watches`). Arm at first VI when a 320-phase
event matters. Mupen can omit a nullifiable delay-slot PC (Session
3285 vs 3287 at `0x800C2B88`).

The strong `osSpTaskStartGo_recomp` override omits the weak
implementation's request clear, while `osSpTaskYielded` reports
request state even though the runtime never interrupts a task.
Session 3304's completion-aware default is the live contract;
`ROGUESQ_SP_YIELDED_REQUEST_ONLY=1` restores the old stall.

## Superseded conclusions

The original overlay/menu-only explanation, intrinsic VI-640 flakiness,
missing-input and wait-return explanations, global-zero image-DMA theory,
route-wide PCM-gap theory, and force-zero default policy are superseded at
their measured scopes. They were believable before qualified routes,
same-build controls, or independent retail attribution existed. Full failed
experiments remain in the ledger and archived overview.

Sessions 3262–3264 selected `H-SourceUnavailable` /
`H-PortPublicationSourceUnavailable` because `RecompiledFuncs/` is
absent from this repository root. Believable as a local-tree probe;
CMake's `RECOMP_FUNCS_DIR` is `../N64Recomp/RecompiledFuncs`. Session
3276 used that tree to complete the caller table.

The `swapBufferWithViMode` delay-slot width-2 request looked like a
VI-mode publisher bug that might block title 1024. Session 3277
restored hardware `$a0` order; the copied mode is width 320 and the
1024 request is still absent. Believable because the illegitimate
width-2 pointer was a real generated-code defect on the only
swap-time `osViSetMode` path.

Sessions 3288–3302 described the port's viewer stall through
`H-PortFadeOutNeverEntered`, `H-SubmitRecvBlocked`,
`H-PortSchedSendMissing`, `H-Ed0CompareSkip`, and the type-2
yield/busy-byte chain. Those findings were accurate under the
then-default request-only `osSpTaskYielded` contract and remain
reproducible with `ROGUESQ_SP_YIELDED_REQUEST_ONLY=1`, but they no
longer describe the default runtime after Session 3304. They were
believable because the runtime itself reported a requested task as
yielded; Session 3304's completion-aware default reaches E60, keeps
SENT/SRET matched, and returns from the viewer. The downstream
missing title publication is not superseded. Per-session retail
parity for that stall (s3291–s3302) is archived in PROJECT-OVERVIEW
section 54.

Session 3305 selected `H-CinematicEntryStalls` because `0x800A6618`
was silent after entry. Believable as a hang at the first
instruction; Session 3307 measured a live loop with a stuck
exit-gate, so the missing return is `H-PortLoopNoExit` not an
entry stall.

Session 3307 left the stuck 6074 `$v0` as a skip/stage/dt
predicate or a too-slow loop. Believable because retail needed
~1003 iters / 48.8 s. Session 3308 measured `$v1=0` at
`0x800AF55C` on every call, so the stage/dt path never runs.

The prescribed Session 3306 30 s undriven Rice recipe does not
reach the cinematic return: first attract still has exit-gate
`$v0=0` at 30 s. Believable because Session 3283 with Start
returned at 17.0 s. Without Start the finite loop runs ~1003
iterations and returns at 48.9 s.

Session 3274's target-span writer `0x800078EC` was treated as a
candidate VI/output publisher. It is `rs_memset` (`0x800078E0`).
The span is being filled; that PC does not publish a VI mode.

Session 3278 left retail's four-slot table unevaluated at title.
Session 3279 measured every slot +8 word as 1024 while title
`1024 @ 0x00790400` was live. Session 3280 named the 1024-edge
jal as `advanceVideoFrame` `0x80018378`, already the port's 640
publisher, so a title-only overlay caller is refuted.

`--pc-phase-log-width` deferred 320-phase ticks in Session 3281.
Session 3282 armed at first VI and recovered the 2.0 s first
`menuOverlayInit` (`$a1=9`). The 17 s jal is the second
activation (`$a1=2` from `mainGameLoop` `0x8003E13C`), not a wait
inside the first call and not unused site `0x8003E0CC`. Session
3283 measured the 2.0–17 s gap as viewer return at 6.9 s then
`cinematicLoopBody` until the 17 s jal. Session 3284 measured
retail `runMenuModelViewerScreen` entry at 2.5 s and return at
6.7 s, so the port is stuck inside a screen retail also uses —
then Session 3304 unstuck the viewer and moved the stop into
the cinematic.

Session 3285's `H-RetailNoFadeStore` (zero `0x800C2B88` hits) is
superseded by Session 3287: `0x800C2B84` was live at 6.1–6.6 s
and the taken beq followed the last 2B84, so Mupen omitted the
nullifiable delay-slot PC.

Session 2791 described stale request clearing in the weak
`librecomp` `osSpTaskStartGo_recomp` as the active lifecycle.
Believable from `sp.cpp`; the linked strong override in
`src/main/upstream_compat.cpp` shadows it and does not clear
the request. Session 3303 shows clearing alone is not the
decisive contract: reporting the request as a yielded completion
causes E70/E80F, while not-yielded status restores the viewer
scheduler and submit loop.

## Evidence index

Live-thread evidence:
`scratch/agent/s3308_stage_advancer.md`,
`scratch/agent/s3307_cinematic_loop.md`,
`scratch/agent/s3306_retail_cinematic_exit.md`,
`scratch/agent/s3305_postviewer_continuation.md`,
`scratch/agent/s3304_yield_lifecycle_default.md`,
`scratch/agent/s3303_yield_status_ab.md`.
VI/publication: `s3276_m5_target_vi_publication_audit.md`,
`s3278_osvimode_table_census.md`,
`s3279_retail_osvimode_slots.md`.
M5 route: `s3272_m5_step1_pair.md`,
`s3246_m5_port_vi_boundary_audit.md`.
M3: `s3285_freelist_live_guard.md`,
`s3249_m3_status03_audit.md`.
Use `grep -n` plus a bounded `sed` window for `PORTING-STATE.md`; never
read that multi-megabyte ledger wholesale. The soak queue is consumed
by automation; fold only new tail lines into the next audit. Session
3210 closes the generated-symbol sweep.
