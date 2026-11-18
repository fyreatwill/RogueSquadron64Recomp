# Rogue Squadron 64 Recomp — current truth

Compact operational handoff, as of Session 7563 (2026-11-17).
`PORTING-STATE.md` is the chronological ledger; durable and migrated material lives in
`docs/PROJECT-OVERVIEW.md`. The full s7416 text of this file (every audit class AQ-BZ s7373-s7416 with all numbers,
controls and tool flags) is archived verbatim in PROJECT-OVERVIEW "Migrated from CURRENT-TRUTH (s7417 maintenance)"; item-1 classes DG-EO in "(s7491 migration)"; classes CC-DH s7420-s7451 in "(s7452 maintenance)";
s7315-s7369 classes in "(s7370 maintenance)"; the s7306 headline chronology in "(s7307 maintenance)"; older text in
"(s7187 maintenance)" and "(s6994 maintenance)"; s7533 Next-steps items 1,12,15-21 (classes FD-FZ) in "(s7534 maintenance)". Grep there for any sNNNN.

## Headline

**Every engineering goal on the ladder is closed or awaiting the owner's look.** Nothing is broken at the
owner's recipe as far as any instrument can see; remaining items are owner judgements (list in Next steps).

- **NEW s7565 (19c CLOSED): compensation-chain audit, H-chains selected.** tools/s7565_comp_chain.py -> docs/COMPENSATION-CHAINS.md
  (122 rows, hand verdicts, controls 8/8): CHAIN 34 (12 on the retail route, 22 inside dd>1/ASPECT features), FEATURE 34,
  RETAIL-GAP 41, GUARD 6, DIAG 5, OWNER 1, UNKNOWN 1 (S6892). Retail-route chains beyond s4889/s7476: WRAP_RESTORE+S4272
  (WRAP_FLUSH), DPC_KEEP_PIPE (our PIPESYNC drop), CUT_LIVE (s6418 at dd1), SHADE_ORD_RESET (our diag map), S7376/S7383/S7384
  (follow-draw mode 3), S7478 (canary), G1D_EDGE_CONTENT. B40 children: only s4889/s7476 (of 196 tags in the s7558 A/B logs, the
  only gate-0-exclusive ones). GQ census fix: `e[0] == 48` idiom was invisible, S4889/S7476 now in DEFAULT-ON-LEVERS (117 ON).
- **s7564 (19b(c) CLOSED, 19b CLOSED): B40 A/B, H-gate0-safe selected; owner decision pending.** s7558_b40_ab rerun
  in-session (ALLOW_SLOW, battery clk 1.52, 16:9 FPS60, L4 dd2 / L1 dd4 / L12 dd4, 240 s each): default gate-0 and B40=1 arms
  6/6 alive, 0 crashlines, vi_stalls30s=0, gen/s per pair 59.5/59.2, 37.1/37.0, 31.0/30.8 (tools/s7537_ring_cost.py, from 60 s).
  Same-run witness: `[s4889] first-gate-zero-dereg` (reads MEM_BU 0x800A0F50==0) and `[s7476] dereg a1 17->1 fix=1` fire in every
  default arm and in NO B40=1 arm. So gate-0 is safe today only because two compensating patches (s4889 dereg, s7476 $a1 fix) run;
  the retail store (B40=1) needs neither. s4700's 2/4 gate-0 crash predates both. Owner question (item 4): restore the retail
  store as default? Not flipped. The `[cineBody] B40=` field reads 0x80130B40, NOT the gate - never use it as a witness.
- **s7563 (19b s7420 CLOSED): s7420 parser census OPEN 1 -> 0, H-blind selected (false row).** fixup_patches_host.py's
  anchored `^RECOMP_FUNC` regex edits RecompiledPatches/patches.c (CMake step 2), which weaken_patched_funcs.py never touches:
  patches.c has 0 weak headers, its 3 override headers are strong, libPatchesLib.a defines them `T`, libRecompiledFuncs.a
  has them `weak external` (nm -m), binary carries all 3 `[patch-live]` probes, 39 s7490 hooks present. Census gained a
  PATCHES-TREE phase (tools from CMakeLists given RECOMPILED_PATCHES_DIR) -> IMMUNE-TREE only while patches.c has 0 weak
  headers; control (4) plants one and must reopen it (PASS, controls 4/4). `s7420 --controls` is now a regen_replay gate.
- **s7562 (19b(e) CLOSED): s7375 NOLOCK thread census OPEN 8 -> 0, H-confined selected, no race.** The 8 s7472-s7521
  diag containers: 7 CALLER-LOCKED (s7500/s7503 helpers under g_s7500_mu/g_s7503_mu; s7475/s7480/s7488 under s_s7475_mu, the
  gfx/lambda callers arrive via rs64_s7491_hst -> rs64_s7475_store after that lock; s7521 seen_off under its file mutex m), 1
  GUEST-SERIAL (s_s7472_seen: only the rs_malloc/rs_free fixup hooks). `s7375 --selftest && --check` is now a regen_replay.sh
  gate; negative controls: planted std::thread-touched container -> REVIEW/OPEN 1, dropped verdict row -> OPEN 1; fresh
  regen_replay (scratch/s7562/replay) "ok" 8m26s.
- **s7561 (19b(d) CLOSED): census analysers tightened, H-collateral refuted.** s7366 lockset: scope-aware declared() +
  param/local shadow test -> 71 false MIXED rows gone (68 local/param, 3 explained), 1 access the OLD analyser had hidden
  surfaced (g_audio_route_pref@audio_route_resolve, reviewed H-safe-thread); gap kept and documented: static locals and locals
  captured by thread lambdas are never lockset-checked. s7363: clamp ternary with any constant arm (`p < 16 ? p : 15`) is CLAMP,
  3 keys reclassified. Selftests extended with negative controls (HEAD fails them), plant still OPEN, fresh regen_replay "ok".
- **s7560 (19b(b) CLOSED): `tools/regen_replay.sh` runs to "ok"** (first time since s7484; and since s7467 the s7364 OOB
  ASan plant could never be cleared). 180 census rows reviewed (s7363 24 keys BOUNDED; s7364 29 BOUNDED/11 FIXED/1 TRUST/1 PLANT, OOB
  now clears only with a `PLANT ` verdict; s7366 48 caller-locked/26 same-name locals/1 thread_local). Real defects fixed, all in
  env-gated diagnostic code: 1 lock race (s_s7518_ln / s_s7519_dt vs host-thread rs64_s7491_hst writers, STALEWATCH only; L4 hold
  with it armed alive, ctl fired) + 5 latent over-reads (s7551/s7552/s7491_hst bitmap/s7523/s7535). regen_verify unchanged 2607/141.
- **s7558 (class GR CLOSED, tools/s7558_gr_census.py --check rc 0, --controls 16/16): one hidden default.** The MusyX gate store
  setDisplayMode 0x8008EB40 -> 0x800A0F50 **defaults to 0** (retail v0 only with ROGUESQ_M5_B40_VALUE=1), contradicting s4701's
  documented pass-through default (B40=0: 2 crashes/4; pass-through 0/15, s4700-s4703). The fixer writes the s4701 form; s5544's
  fixup_live_replay "B40 ternary polarity" rule flips it back to what live had (default-0 already at the N64Recomp repo's first
  funcs_23 commit, s5484). Owner decides; A/B soak queued (scratch/agent/soak_queue/s7558_b40_ab.sh). All other 109,737 fixup hunks
  are gated, inert, wild-pointer guards (826), recompiler-correctness or host plumbing. Also: **the regen chain aborted at
  fixup_menu_worker since s7484** (s7484 load wraps broke bare-load anchors in 6 fixups) -> fixed with tools/rs64_anchor.py; regen
  now stops at the s7363 host-array gate (27 + s7364 71 + s7366 82 unreviewed rows from s7480-s7535), and replay vs live is
  2607 same / 141 differ. **s7559: the drift is H-layout, 0 open LOST** (vs the s7421 baseline 114: 35 new rows are SLOTPERM, the
  s7487 lwl/lwr counter slots numbered in another order, same 410 pcs, reports pc-keyed; 1 CODEGEN static-note inlining; PATCH tags
  equal to the s7421 census minus its fixed double-applies) -> Next steps 19b(b).
- **NEW s7535 (class GA, OPEN H-latent-fix): early gfx sp_complete races the F5 LLE's inputs in flight.** ultramodern sends
  sp_complete before send_dl, so the game starts the next frame while the LLE still fetches. Same-run A/B (ROGUESQ_S7535_GA_CHK=1
  ROGUESQ_S7535_LATE=alt, controls 106/106, 3 runs): flight diff bytes/task early 635 vs hardware-order 164 (L4), 472 vs 53 (L15 dd8
  21:9); the excess is all in the 0x720000-0x75FFFF gfx pool (1.19 MB vs 6.7 kB), next-frame vertex shade bytes. DL chunk-link
  streaming (0x110 chunks, link at +0x10C) is SP-done-independent = hardware concurrency. Fix candidate ROGUESQ_S7535_LATE=1
  is now standalone ROGUESQ_SP_LATE=0|1|alt (s7536). **s7536: no geometry consequence** (spikes / big hulls per task equal in both
  states, 5 same-run alt arms L4 dd2/dd4 16:9 + L1 dd8 21:9, 2 reseeded; ctl 32285/32292) -> H-colour-only, not a G5b/G5f source.
  **s7537: FPS60 cost nil where the game holds 60** (L1/L4/L12 dd1/dd4 16:9 fullscreen, 60.0 vs 60.0 /s; L12 dd4 on a 1.53x
  battery clock CPU-bound 3v3 ABBA early 52.9-54.6 vs late 51.4-52.9, unresolved) -> SP_LATE=1 listed in OWNER-OPT-INS, census
  rows H-latent-FIXED(opt-in), census exits 0. Default unchanged (owner).
- **Class GB (s7538-s7540): CLOSED, fix opt-in (ROGUESQ_RDP_NODRAIN=3).** tools/s7538_gb_census.py enumerates every
  completion signal the runtime posts to the guest (29 sites, 31 mode rows, 0 unclassified, --controls 7/7). Default config: every
  device finishes or copies its guest-RAM access before the signal (PI rom/sram synchronous, AI PCM byte-swapped into a host vector
  at osAiSetNextBuffer, SI polled before, audio RSP synchronous, DP after send_dl, VI = hardware scan-out) except GA (opt-in fixed).
  OPEN: ROGUESQ_RDP_ASYNC=1 ROGUESQ_RDP_NODRAIN=1 (an OWNER-OPT-INS row) posts dp_complete while the RT64 worker still holds the
  task's tail job(s) (s6709 pend_jobs 2.0, ~3.3 ms fullSync), which read textures from RDRAM and write fb copies to RDRAM after
  the guest was told the RDP is done. **s7539 measured: TORN** (tools/s7539_gb_score.py, ROGUESQ_S7539_GB_CHK=1): L1/L4/L12 167/297/354
  of ~8-13M post-signal loads read bytes the guest rewrote after dp_complete, all one 2 KB 64x64 4-bit texture re-decoded every
  frame by swizzleTextureRowsToTmem (0x800249B4/E4, via parseImageFile; store watch). Controls: planted == caught, older-snapshot
  diffs fire, witness ~0.5-0.7 MB/window. Legitimate guest writes; on-screen effect unmeasured. **s7540 fix: ROGUESQ_RDP_NODRAIN=3** (reads-wait: task exit waits for
  rs64_s7540_reads_done(), called by RT64 fullSync after its last fullSyncFramebufferPairTiles). Same-run NODRAIN=4 cycle
  (drain/nodrain/reads-wait per task) L1/L4/L12: reads-wait 0 post-signal loads, nodrain 43/50/196 torn (controls caught);
  Gfx wait per task 1.2-1.6 ms vs 3.3-4.3 drained, 0 nodrain. OWNER-OPT-INS recommends =3; census exits 0. **s7541: the rest of fullSync after reads_done is clean too** (rs64_s7541_span, tools/s7541_gb_score.py, NODRAIN=4 + ROGUESQ_S7541_HOLD=1, L4/L12/L1): fb read-ins, writeback targets and hashTracking spans 0 guest changes after the post, controls planted==caught, same-run nodrain loads torn. Residual H-late-write: ~84% of writebacks land after dp_complete; no guest reader known (s6938, s7391; NODRAIN=3 WBW rerun queued). Item 18.
- **Class GC (s7542): CLOSED.** tools/s7542_gc_census.py (rules tools/s7542_gc_rules.py) enumerates every host-side write into guest
  RDRAM (10 idioms, 158 sites, 176 rows, 0 unclassified, 0 open, --controls 8/8): default config = before its signal (PI, SRAM, audio
  RSP, sync RT64), on the guest thread (58 rows: libultra replacements, OSMesgQueue stores only in dequeue_external_messages), init,
  env diag/lever, or dead. Late rows: GA (F5 DMA writes, opt-in fix SP_LATE=1) and GB writebacks under NODRAIN (s7541_wbw_rwait: flight
  readers only RT64 updateScreen XXH3 / copyRAMToNativeAndChanges, ctl fired). Timer thread re-arms OSTimer after posting = hardware
  order, OSTimer libultra-private (H-os-private, single-source).
- **Class GD (s7543): CLOSED.** tools/s7543_gd_census.py (exit 0, --controls 9/9): no port yield splits two dependent guest-struct
  stores. Guest threads hold one run token and lose it only at an explicit yield; __osDisableInt/__osRestoreInt are no-ops. (A) 49
  runtime replacements, stores vs yields in body order with one level of callee followed: 36 atomic (no yield or tail yield only), 6
  yield-safe with a named invariant (do_send/do_recv block in a while(full/empty) re-check before any queue store; s7195 park never
  returns; osStopThread(NULL), osStartThread, _thread_func and the osSendMesg dup-drop branch-split), 7 hand-off primitives where nothing
  touches guest RAM between running.signal() and the caller's running.wait(). (B) generated-code critical sections: one DisableInt
  region (musyxSynthFrame_s4562_impl, no call inside); all 13 cop0 Status writes resolve to the FR-bit FPU toggle, not IE. (C) 51
  injected yields in 31 guest functions all sit outside every region, so hardware could switch threads there via an interrupt too.
- **Class GE (s7544): CLOSED statically.** tools/s7544_ge_census.py (exit 0, --controls 13/13). Boring check: the port's OSThreadState
  enum is STOPPED=0 QUEUED=1 RUNNING=2 BLOCKED=3 (libultra 1/2/4/8) and RUNNING/BLOCKED are never stored, so every running or
  mesg-blocked thread reads QUEUED. (A) 18 transition rows in 11 replacements, each H-equal or H-benign vs libultra (osStartThread on a
  mesg-blocked STOPPED thread: port makes it runnable, the do_recv/do_send while-loop re-blocks it). (B) 0 guest loads/stores into the
  11 static OSThread structs (constant-address propagation) or worker+0x20..0x4F in the service-worker fns: nothing reads the
  divergent values. (C) 40 thread-API call sites: the 3 osStopThread sites all stop ANOTHER thread (mainBootstrapWorker -> 0x8010D3D0;
  waitForSerialIdle -> siServiceThread, unreachable from it by direct calls) or are dead (stopServiceWorker); no osStopThread(NULL)
  caller, so the s7543 seed row is dead code. Every osStartThread targets a fresh or stopped thread (port re-inserts a RUNNABLE one,
  libultra ignores it): direct create in the same fn, startServiceWorker after registerServiceWorker, releaseSerialLock paired W/R
  with waitForSerialIdle, restartServiceWorker dead. Limits (single-source, static): heap-carried thread pointers are not followed;
  reachability is direct calls only. **s7545 runtime witness: CLOSED.** ROGUESQ_S7545_THRWATCH=1 (+STORE_DIAG=1) marks every created
  OSThread [t, t+0x1B0) (osCreateThread/osDestroyThread via the RS64_S7491 hook) in the s7484 load / s5798 store bitmaps; L1 dd1, L4/L12
  dd4, 220 s each (tools/s7545_thrwatch_recipe.zsh, score 0): 20 threads created, 8 destroyed, 0 guest loads/stores into any LIVE
  thread; controls watch-ctl L+S and plant L+S (siServiceThread+0x10 at 150 s) fired in all 3. v1 without destroy tracking saw ~20k
  stores/20 s: MusyX voice render + heap code reusing the structs of 4 destroyed threads (saveServiceWorker x2 etc.) = legitimate.
- **G3 render fidelity: H-equal everywhere scored (s7122-s7217).** RT64 == angrylion to the retail floor at
  4:3, 16:9, 21:9, fullscreen 16:9 and ASPECT=auto fullscreen, flight L0-L18, menus, cutscenes, front end,
  LEVEL DESCRIPTION. Only large residuals: the deliberate W_SHEET_PX / W_SHEET_POS guard-band sky-sheet culls.
  Default-on fixes from it (=0 old): FBW_ALIGN (s7188), RECT_ASPECT (s7142), HORIZON_XFIX / GATEFIX / SKYFILL
  (s7133-s7136) + SKYFILL_BOT (s7166), W_SHEET_POS (s7130).
- **Draw distance (G1c) at the owner screens.** dd4 is the 4:3 ceiling (docs/DRAW-DISTANCE.md). Wide:
  dd6 auto bundle (off-map cull past 0.6 x fog end, KEDGE 0.8,12, WIDEWIN cap 10240, auto KLEVEL `12:0.5,13:0.5`,
  CAPLEVEL `9:8192` when FB_WIDTH>796) holds ~60 fps on all 19 levels at 21:9 and 16:9. WIDEWIN auto stack
  (R=88 + 2x2 merge 0.4 + E16, main.cpp [s7258], STACK=0 off) at any dd>1 with ROGUESQ_DD_WIDEWIN=1; merge+E16
  carry the cost cut, R=48 only ate the side gain (s7265-s7266). L12 auto RLEVEL `12:48` at dd>=6 (s7287).
  **dd8 auto px8 + R128 (main.cpp [s7293], ROGUESQ_DD_PX8_AUTO=0 off) QUALIFIED at 16:9 (s7295) and 21:9 (s7299):**
  300 s, 0 crash, 60/s on L1/L5/L9/L10/L12; total emitted cells/call L4 16:9 ref 6902 -> 11406. Far plane capped at
  32767 (ROGUESQ_DD_FARMAX, s7310): above it the sky-dome edge clip pins to x=0 (21:9 left sliver).
- **G5e fog (opt-in ROGUESQ_DD_FOG_ALT=1,3,1, s7302-s7307): QUALIFIED at both owner screens.** ke3 at dd8 =
  dd4's fog end; melts the far horizon into haze, near detail kept (16:9 L1 1.3/2.4/2.7%, L4 1.5/6.5/4.0% texture
  removed far/near/side); weaker at 21:9 (L1 null in all bands, lever ctl 8/27/17% PASS, s7306); untouched on
  L10 (cloud). Holds: 16:9 L1/L5/L10 300 s (s7304) and **21:9 L1/L5 300 s (s7307 fold: 0 crash, 60/s, beyond-route
  3/1 s, ctl flat-30 176 s PASS)**. Cheaper per frame in both: same-soak L1 heaviest20 12.57 -> 9.69 ms (16:9),
  13.53 -> 9.40 ms (21:9). Default unchanged; owner judges the look (docs/OWNER-OPT-INS.md, sheets s7303/s7305/s7306, same-pose dd6/dd8/fog s7308).
- **G5c freezes CLOSED (s7272-s7285):** 0 flight image holds >= 250 ms on quiet host, windowed, fullscreen, 900 s
  L4/L12; every hold is a black death/restart or cutscene transition; off-window gaps are fb-relocation scene
  changes (s7284). Background CPU load IS a real freeze source and ROGUESQ_QOS_ALL=1 removes it (s7277-s7281;
  minimal set GUEST_QOS+PRESENT_QOS); GPU contention slows evenly, no freezes, CPU QoS cannot help (s7282-s7283).
  Transition stalls = retail 3072-sample MusyX wait ~139 ms (s7065, s7285). **Owner: QOS_ALL default?**
- **Retina (s7203-s7224): opt-in ROGUESQ_RETINA=1 CLOSED in every scenario** (flight, front end, windowed 21:9,
  live resize, hot-plug): H-free (GPU +0.05-0.4 ms, 0 gaps), H-sharp (HUD crops 0.42-0.57 -> 0.73-0.82).
  **Owner: RETINA default?** Sheets docs/owner_sheet_s7205_retina.png, s7220, s7223, s7224.
- **Host hazards fixed, default on (=0 old):** guard-refused mq drop (s7194) and park (s7195); PI DMA to unknown
  region posts completion (s7196); AI drain post when SDL stops pulling (s7197, AI_STALL_POST_MS); AI backlog
  trim 150 ms (s7198, AI_BACKLOG_MS); audio output hot-plug (s7199, AUDIO_HOTPLUG; default-route needs nothing
  s7200); pad hot-plug (s7201, PAD_HOTPLUG); display hot-plug (s7202, DISPLAY_HOTPLUG; own-display gate s7222,
  HOTPLUG_ANY=1 old). Censuses CLOSED: docs/COOP-SCHED-POLL-CENSUS.md, docs/HOST-COMPLETION-CENSUS.md.
- **Presentation fixes, default on (lib/rt64):** interlaced still address VI_ILACE_ADDR / PE_STALEFIX (s7206),
  4:3 double present PE_DEDUPE (s7208), present box shape PRESENT_SHAPEFIX (s7213). Elite Rogues field screen
  presents progressive (RT64 ignores the scissor field bit; design difference, s7209/s7210).
- **Window/aspect (G1f) CLOSED:** auto follows the display at boot, live resize gives bars (FB_WIDTH lives in
  statics, s7225); ROGUESQ_WIN_DISPLAY=<n>|mouse drives auto/notch/fit/placement on a secondary (s7226);
  F11 and target-display removal OK (s7227/s7228). In-flight flat-30 in harness runs is the diag ucode path
  (LOG_PHASE -> G1E_PROBES); the coverage harness defaults OWNER_TIMING=1 (s7229).
- **Boot freeze (1 in ~65, s6993) stays PASSIVE:** [stall-dump] prints [stall-wait] + [stall-cf0]; H-cycle refuted
  (s7193); 0 in 100+ owner-env boots since. Hunter `env HUNT_OWNER=1 HUNT_CONTROL=1 zsh tools/boot_freeze_hunt.sh <out> N 34 12`.
- **dd8 21:9 hangar-route mission-load crash FIXED (s7326, default on):** spill blocks never saw the retail scene-change bulk free
  (coalesceFreeHeapBlocks frees every non-0x80 persistent block), so loadLevelAssets' 0x2DFF00 outlived the reset, the 4 MB spill
  arena filled, rs_malloc NULL, SIGBUS in grid-cell terrain code. rs64_s7326_spill_reset releases a1&0x84==0 spill blocks at the reset
  (ROGUESQ_SPILL_RESET=0 old) + 8 MB arena 0x81000000-0x81800000, RAMTOP 24 (ROGUESQ_SPILL_MB=4 old). Same-build arms: release-only
  and arena-only both crash, both together 650 s / 2 mission cycles clean; heap_np_kept=0 at every sync (retail semantics).
- **Spill reads by the RSP FIXED (s7327, default on):** the RSP DMA masked DRAM_ADDR to 24 bits, so gfx ucode reads of terrain grid
  data in a spill block (dd>=6 hangar route) fetched the 0x80xxxxxx alias. 25-bit mask in rsp.hpp, ROGUESQ_RSP_DMA25=0 old (item 17).
  **Visible (s7328):** with the grid buffer forced into spill (new lever ROGUESQ_SPILL_FORCE=min:0x200000) on posed L1 dd8 16:9, the
  old mask draws near terrain as rainbow garbage polygons (37.8% of pixels at one freeze); the fix is pixel-identical to the no-spill
  layout. Sheet docs/owner_sheet_s7328_dma25.jpg.
- **L15 21:9 dd4 crash FIXED (s6992):** 7-site `(p & 0xFF000000) == 0x80000000` test vs the 0x81000000 spill arena;
  tools/apply_s6993_ptrmask.py, ROGUESQ_PTRMASK=0 retail.
- **G1e:** 60 fps in flight on all levels (s6996; use fl_shown). Defaults VI_RT, STDERR_ASYNC, G1E_CELLIDX;
  opt-ins VI_LOCK=1, QOS_ALL=1.
- **Wide/aspect fixes default on:** G1D_SHOWROOM, G1D_340PERSP, G1D_INTROSHAPE / W640 / SCISSOR_TOL, notch safe
  area + VPW_SCALE, WIDE_LOGQUIET, WIDE_UNDRAWN (s6924-s6932).
- **Opt-ins, owner's choice (default off):** VI_SHAPE (owner: stays opt-in), DD_MELT, DD_SKYZ, DD_CUT_LIVE,
  HANGAR_FOV, G5G_LENS, NEARLIFT (near-wall flicker is retail, s7109; k1.6 removes it), WIDEWIN cap 12288,
  RETINA, QOS_ALL, DD_FOG_ALT. Owner ran MELT, SKYZ, VI_LOCK, QOS_ALL and reported nothing wrong (2026-11-08).
- Save guard: runner.sh exports ROGUESQ_NO_SAVE_WRITE=1 and snapshots build/saves to
  ~/Documents/RS64-save-backups/auto. Never touch the owner's save (profile "ASS").

## Closed work, summarised

Detail: PROJECT-OVERVIEW "Migrated from CURRENT-TRUTH (s6900 / s6994 / s7187 / s7262 / s7307)".
- **G3 retail match** (angrylion oracle): boot, attract, hangar, crawl, intro, missions 1-19, front end at RDP
  level, AT THE MOVIES 81/81 (s6784-s6792); presented-frame matrix s7122-s7217.
- **Default-on fixes from that sweep:** UCODE_CAP 65536 (dd>1 1048576), MENU_WORKER_FIFO, EXACT_EDGES, exact-ns
  VI deadline, LLE_FORCE/UNGATED/SOLO, audio_device_mutex.
- **G1e rate:** s6696 getenv, -O2, RSP work s6713-s6775, FPS60 classes s6828-s6831 (docs/FPS60-FIXES.md).
- **G1, G1c, G1d, G1f, G3c, M5, M3, M6, G2, renaming (s6868, misnomers s7072-s7080): closed.** G1(d) objectives
  and G4 crash hunting parked by owner.
- **Engineering s7066-s7098:** cached getenv (ENV_CACHE), dladdr cache, diag call-site gates, N64Recomp
  self-branch miscompile (tools/fixup_selfbranch.py), lowering / host-shim / fixup / RSP censuses, DPC bridge
  forwards exactly the hardware RDP stream (s7096), big G5b drops are already in the RDP stream (s7098).
- **WIDEWIN thread s7231-s7271 CLOSED:** cost (H-tiny far side cells), auto stack, side-edge gain at 21:9 kept at
  R=88, 16:9 side gain below run noise (H-noise s7269), stack invisible in cutscenes at both aspects (s7270/s7271).
- **Wide + dd span class (s6879-s6885)**, width class (docs/G1D-WIDTH-CENSUS.md), spill arena (s6858) + heap audit
  (docs/HEAP-ADDR-AUDIT.md; missed the s6992 mask class).
- **Regen (s6863-s6881):** replay from pristine compiles/links/boots; live tree NOT regenerated (docs/REGEN-VERIFY.md).
- **Present thread (s6884-s6891, s6931):** SCREEN_JOB, PRESENT_INFLIGHT, PRESENT_DRAIN opt-in/off.

## Superseded conclusions — do not act on these
- **s7552 "pre-mission out-of-rect colour change is real content (a darkening fade)" (superseded s7553).** Believable: samples
  0x294B->0x2109 failed RT64's requant test F(pre,d). But F only models upward dither from pre; the source is the retained float.
  s7553 shadow: pre == RT64's own last writeback for 100% of those px, post within ±1, dark/bright balanced, outside every draw.
- **s4711 "retail never runs reapplyAudioConfig/reapplyDisplayMode at boot/attract" (superseded s7476).** Believable because the oracle
  ran 120 s with 0 hits; but it ran with dummy video, which never leaves the 320 boot phase. With Rice + Start presses retail calls
  reapplyDisplayMode on every scene (t=2.1/6.7/17.3/38.4 s). The count=1 re-init was the port's s4889 patch clobbering $a1.
Recent only; older entries in the PROJECT-OVERVIEW maintenance archives (s7307, s6994, s6900, s6870, s6759).
- s7418 "32 live cache ops". Believable: RecompiledFuncs census with a passing liveness control. s7419: its liveness keyed on objdump
  names, so 147 renamed functions were `nofn`; one live CDE (clearMemory16ByteBlocks 0x8000041C, boot) was skipped -> 33, still safe.
- "0 live cache ops" (s7405 class BO). Believable because the census ran with a control that passed (Status/Count/Compare rows),
  but that control never exercised `cache`: mips64-elf-objdump prints cache as .word, so the row could not fire. s7418 on
  RecompiledFuncs: 32 live (CDE 0x0D + HWB-D 0x19 only), no-op-safe. Class BO's FR/RM/FS conclusions stand.
- "FCSR.FS vs host FZ: known and left, ROGUESQ_FTZ stays opt-in" (s6013/s7087). Believable because the s6012 lvl1 holds
  were clean in both arms; but no instrument ever asked whether denormals occur. s7405 FPSR witness: they do (game thread, in
  flight), so FTZ is now default on (=0 old).
- s7376 "the present thread already takes workloadMutex at line ~676 in the same frame" (used in its deadlock/coverage reasoning).
  Believable: upstream locks it there. s7377 counter: that lock sits on the `!interpolationEnabled` branch, taken on 27/10800 presents;
  the other 99.7% ran lock-free (fixed by ROGUESQ_S7377_EARLYLOCK).
- s7372 "17 AQ rows exercised in mission incl. dpc defer_begin and rs64_s6094_tick; 73 never executed". Believable: coverage
  counts are exact. s7373: the s7366 rows' line numbers predated s7368/s7371 edits (20/97 lines no longer named the container);
  re-cut rows give 19 mission rows (defer_begin and s6094_tick out, both env-gated; get, s6702_release_locked, heapsync in), 71 unexecuted.
- s7193 "boot-freeze second wait unknown, not reproducible by forcing" -> s7367: it is MAIN IN 0x8011A818 (scheduler chain), reached when MAIN (not retrace) is starved; s7193 forced retrace holds, which let MAIN return to CF0.
- s7325 "46 audio reads land in song-channel arrays freed by waitForMusyXAudioTaskDone (via musyxNoopStub) or the scene sync". Believable:
  allocator frames said allocateSongChannelArray. s7330: the blocks are the synth's command-list buffers, and the boot hits come from
  tasks built AFTER the scene bulk free (no wait involved); only 1 in-flight case belongs to the wait path.
- s7324 "class G CLOSED, H-cpu-only: the RCP is never handed a spill address". Believable: 462M DMAs at dd8 21:9 L4, 0 direct, ctl
  198/198. It ran the forced-level route, where loadLevelAssets' 0x2DFF00 sits in the main heap; on the hangar route (s7327, dd8 16:9)
  the reset/reload puts it in spill and the gfx ucode DMAs its grid-layer data at 0x81xxxxxx (fixed: 25-bit DMA mask).
- s7324 "40k audio RSP reads hit heap GAPS / freed blocks (no live rs_malloc block)". Believable: the s7317 map recorded every hooked
  malloc/free. s7325: the retail scene reset frees in bulk without rs_free, the map kept 531 stale entries shadowing live blocks;
  the guest heap walk puts every address inside an allocated block, dd1 identical. Re-synced map: 46 residual reads.
- s7316 "spill live in the dd2 16:9 L1 run; 80-87 heap words held spill pointers". Believable: the words were aligned 0x81xxxxxx in
  heap. s7317 allocation map: all 833 spill blocks are freed in the load window; those words are halfword data and dead stack slots.
- s7312 "the presented window can lag the RDP stream for seconds (first run after a rebuild)". Believable: same pose, same stream,
  two captures 0.7 s apart both wrong. s7313: a voided batch-1 L5 game was still alive and the pose script captured the oldest game
  (`pgrep|head -1`); the repro arm with a one-game guard matched 6/6 (diff 0.01 vs 92.8 control).
- s7286/s7288 "the terrain window binds from dd4; dd4->dd6 adds 1.8% cells". Believable: [s7233] in= sat at ~3550
  dd4..dd8. s7291: in= counts only the retail-equivalent 64x64 window (constant by construction); total cells grow +24%.
- s7283 "off-window gaps >=250 ms are the GPU saturator draining after SIGKILL". Believable: they followed lit holds
  near +381 s. s7284: that hold is the SIGSTOP control; the gaps are black fb-relocation transitions.
- s7247/s7259/s7262 "the WIDEWIN auto stack removes no visible ground". Believable: holes/seams scorers clean. They never
  scored the side edge; s7264 showed R=48 erased the side gain (fixed by R=88, s7266).
- s7230 "dd6 at 21:9 adds ~6.6 ms per task (H-dd)" and s7014-s7017 "WIDEWIN costs little at 21:9 dd4". Believable: the arms
  seemed to differ only in radius; s7231 2x2: WIDEWIN +4.5 ms, radius +0.7 ms. s7230 also ran on battery (x1.4, s7251).
- s7054/s7063 "L4 21:9 dd6 58.7-59.5 fps". Believable: whole-flight averages; s7230 heavy window flat 30 (battery);
  AC s7257: 60.0/s at 14.06 ms.
- s7227/s7228 "in-flight flat-30 under FPS60 is the game's own rate". Believable: rigid 33.3 ms swaps, free present path.
  s7229: the harness ran the diagnostic ucode path; owner path holds 60/s.
- s7180 "swaps 4700-5028 are LEVEL DESCRIPTION" / s7181 "Elite Rogues 0.047". s7183: it is Elite Rogues; residual =
  weave-reference combing while it scrolls.
- s7122 "4:3 picture off-centre". s7123: SCK pads the capture; in window points it is centred.
- s7120 "flight camera jumps 2-16 u". s7121: the join mixed cam objects; per-cam 0 such steps.
- s7113 "H-raymiss: collision surface ~0.2 u off the drawn mesh". s7114: common-mode rebuild bias; drawn == collision exactly.
- s7098 "near-wall flashes only with FPS60". s7108/s7109: same rate at 30 fps and full retail.
- s7102 "near-wall zig-zag is push vs clamp (H-fight)"; s7100 "FPS60 episodes 4.1x" (s7101: 1.6x, p=0.185).
- s7059 "transition stalls are audio-slot polling". s7064: waits are ~14% of the gap; remainder OS-silent.
- s7032 "the wall face occludes the craft at poses 0-4". s7033: eye above ~99% of culled cells.
- s7009-s7013 "WIDEWIN costs ~10-25 fps": harness LOG_PHASE probe path. Any harness timing since s6713 without
  G1E_FAST=1 PROBES=0 is suspect.
- s6990 "60.0 fps on all 19 levels at 16:9": FORCE_UNLOCK=1 clamps the cursor to level 1. Check `cur` / cursorMask.
- s6788-s6791 "G3e drops CLOSED" (reopened as G5b); s6895 "dd1 has no knife lines" (s6906: dd1 has the thickest).
- PORTING-STATE line 1862 "Fog contributes nothing" (s6904): true only of the early pre-flight scene.
- g3_aspect_crop scores s6879-s6881 scored pillarbox bars; "pinned pose" s6445-s6583 is attitude-only;
  "300 s hold" FPS60/dd>1 s6774-s6862 counted from boot (use inits= and flight_s=).

## Run recipes and hard config

- Run from `build/` with the ROM beside it; SIGKILL to stop; one game run at a time.
- Disk ~20 GB free: a 960x540 g5b_capture is ~9 GB/min. Keep captures <= 90 s, delete raws after scoring.
- Arms: tools/g1e_owner_quiet_arms.zsh (per-level owner fps; sets FORCE_UNLOCK, check `cur`); G5 template
  `scratch/s6899/arm.zsh`; scenes `scratch/s6908/arm.zsh`; hangar `scratch/s6907/arm.zsh` + tools/g5g_pan_score.py;
  fog/edge sheets tools/s7306_fog_219.zsh, tools/s7263_widewin_edge_arms.zsh (SHEET=1), tools/s7268_edge_delta.py;
  image holds tools/s7272_g5c_hold_arm.zsh + s7272_image_hold.py; toggle load tools/s7277_toggle_load_arm.zsh.
- dd4 needs no DD_UNSAFE; higher uses DD_UNSAFE (clamp 8). Confirm run.log echoes `multiplier N`.
- lvl10/15 need `ROGUESQ_FORCE_PLANET_UNLOCK=0xFF`. L10 is cloud with no terrain grid: never use it for terrain
  measures. Wide soaks need `MISSION_WIDTH=796|1024` + `WIDE_ROUTE=1`; ASPECT implies `OSMEM_MB=12`. 16:9 autopilot
  gates wait on VI width 1592, not 1024 (s7271).
- Pose control (s7308: PIN=1 repeat arms are pixel-identical at a freeze, so cross-run arm diffs are exact there; score with
  tools/s7308_pose_horizon.py): `ROGUESQ_POSE_LOCK=1` + `ROGUESQ_POSE_FREEZE=<x,...>:<ms>` (needs RAND_TRACE + DEBUG_WRITE;
  tools/g3_optin_pose_arms.sh). Port dt pin `ROGUESQ_XTRACE_POKE=800FA730:29:30:3d088889`.
- Timing: any ROGUESQ_LOG_* turns FAST off and PROBES on: set `ROGUESQ_G1E_FAST=1 ROGUESQ_G1E_PROBES=0`, or
  OWNER_TIMING=1 in the harness. Per-frame meter `[g1b]` (sd_wall, tasks/s). Measure on AC power (battery x1.4).
- Present rings (ROGUESQ_PRESENT_RING): tools/g1e_present_cadence.py first; at=0 throughout is not a measurement.
- g5b_capture is sRGB since s7151; raws before s7151 are Display-P3 (FID_P3=1).
- Freezes: stalls = [g1b] sd_wall max; image freezes = tools/g5c_frozen_runs.py / s7272_image_hold.py;
  `sample <pid> <s> <ms>` costs no build.
- AT THE MOVIES shots by run time (dd1 16:9): 76 887-912, 77 912-924, 78 924-942, 79 942-952 s.
- Frame comparison: score menus by RDP (tools/g3_rdp_frame_match.py, tools/g3_menu_pair.sh). G3 kit: arms
  tools/s7125_arm.zsh, s7131_arm.zsh, s7141_{arm,post}.zsh, s7146_arm.zsh, post s7152_post.zsh; scorers
  tools/s7122_fidelity.py (FID_ALROWS=444/336: RT64 shows rows 0-443 / 0-335), s7183_native_edge.py,
  s7210_regfit.py (run first at 16:9); replay tools/angrylion_replay/build16.sh. L17 autopilot dies ~126 s.
- Oracle missions: tools/g3_eep_patch.py sets +0x31; use --save-dir, never swap a save over the user .eep.
- Slow builds (TSan/ASan): `ROGUESQ_AUTOPILOT_CLOCK=frames ROGUESQ_AUTOPILOT_FPS=58` (FPS60) keys autopilot to fullsyncs,
  but front-end screens are VI-timed, so the route still diverges at TSan speed; gate with `<s>:w<width>` events (s7371).
- Soak verdicts: `scratch/agent/SOAK-RESULTS.md`; read `alive_at_end` / `crashlines`, never rc (since s7456 the loop's line carries `arms= alive=a/k crash_arms= stall_arms= fatal=`; arms=0 = recipe printed no summary). Recipes that
  drive the window carry `# SOAK_NEEDS_IDLE=<secs>`; zsh recipes run under their shebang shell (s7287).
- Knob tables: PROJECT-OVERVIEW "G1c draw-distance knob and recipe reference"; docs/DRAW-DISTANCE.md;
  owner commands docs/OWNER-OPT-INS.md.

## G1 mission coverage

Playable levels 0..18 (`NUM_LEVELS=0x13`); 19/20 are sentinels. All have route, 300 s holds and framebuffer
presence; level 1 has a retail flight match; objective response (d) parked by owner. See
docs/G1-FRAMEBUFFER-COVERAGE.md and docs/G1-OBJECTIVE-RESPONSE.md. Never send hull damage on level 8.

## Durable constraints
- Never end a turn to wait on a run: foreground (timeout <= 600 s) or queue a soak.
- Retail defaults stay unless the owner chooses; never make an opt-in default from a single source.
- Crash-free holds do not mean "renders correctly" (s6468). No mitigation without naming the writer; dd>1 fixes
  live in `tools/apply_s6*.py` (registered in RS64_REPLAY only, docs/REGEN-VERIFY.md).
- The RSP DMA keeps bit 24 (s7327, phys < 32 MB); RDP image addresses and the game's own 24-bit rebuilds (class D) still drop it, so
  textures / colour images / DL-pool refs must stay below 0x81000000.
- Any guest pointer the game range-tests must sit where its test accepts it: 0x81000000+ fails
  `(p & 0xFF000000) == 0x80000000` unless ROGUESQ_PTRMASK (s6992). Re-check for any new arena.
- Never reset, clean, checkout or update submodules; after editing `lib/` run `./submodule-patches/export.sh` and commit.
- Controls: get_n64_input is the pre-6ed036b97 mapping; no changes without an owner request.
- Title plume parked; reopen only on new evidence.
- Read `docs/F5-UCODE-REFERENCE.md` before interpreting Factor 5 streams. Positive control for every null; two
  independent lines before a conclusion enters this file.

## Next steps (single monotonic backlog)

Spec: ITERATION.md item 3c. No backlog-exhausted block. Renumbered s7534 into one sequence 1-18 (the s7533 numbering 1-22 is archived
verbatim in PROJECT-OVERVIEW "(s7534 maintenance)").

1. **Audit classes CC-FZ s7420-s7533: ALL CLOSED** (full text, numbers, controls, tool flags: PROJECT-OVERVIEW
   "(s7452 maintenance)" for CC-DH, "(s7488)/(s7491 migration)" for DG-EO, "(s7534 maintenance)" for the rest incl.
   FD-FZ). Last fold: s7533_fz_levels score 0 (L1 dd8 21:9, L7/L10/L12 dd4, 4/4 alive) -> FZ CLOSED 6 levels.
2. **G5e fog: owner look.** ROGUESQ_DD_FOG_ALT=1,3,1 qualified at 16:9 and 21:9 (headline). Only if the owner asks for
   more haze at 21:9: sweep ke 2 / 2.5 with `tools/s7306_fog_219.zsh l1k2:1:1,2,1`.
3. **21:9 dd>1 left-edge sliver FIXED (s7310, ROGUESQ_DD_FARMAX default 32767, 0 = old), qualified s7312: owner look.**
   Far above ~36-40k units makes the F5 clip pin sky-dome edge panels to fb x=0 (two lines: RDP W decode + presented
   left-column count, 12 same-pose arms; mechanism single-source). Sheets docs/owner_sheet_s7310_farmax.jpg,
   s7312_farmax_l5_l12.jpg. POSE_FREEZE "<x" = falling crossing (L12 needs it).
4. **Owner decisions on defaults:** M5_B40_VALUE (s7558/s7564: default 0 is alive only via the s4889+s7476 compensations; =1 is retail and equally clean 6/6), RETINA=1, QOS_ALL=1, S7524_V2P=1 (s7526), SP_LATE=1 (s7537), DD_FOG_ALT, dd8 bundle, RENDER_TO_RAM=0 (s7385). Never flip without the owner.
   QOS_ALL evidence: s7277-s7281 (load freezes removed) + s7382 (the threads it raises are exactly the hot ones, DEFAULT otherwise).
5. **G5i hangar re-entry (s6995), G5a Gerrard V crash (s6893; s6998 writeback audit clean), G5b terrain drops
   (FWDWIN far-loss fix, tools/g5b_fwdwin_seamless.py), G5d logo (s6903), G5f knife lines (s6906; sheets
   s7005/s7006), G5g hangar lens (s6907), G5h cutscene background (s6908-s6919): owner flight / look.**
6. **L15 21:9: owner re-flight after s6992 PTRMASK.**
7. **G1d close-out: owner judgement** (scratch/s6731/sheet_menus_owner.png); owner scope: why L7/L16/L17
   autopilot holds cycle the backdrop menu.
8. **Near-wall NEARLIFT, G3 21:9 holes (s7132-s7140), L4 cutscene SKYFILL_BOT (s7166): owner look.**
9. **Owner judgement / parked:** FPS60 feel, G3c sheets, native hangar geometry, rare dd4/dd8 gfx SIGBUS
   (single-source). Reopen on an owner report or side-effect failure.
10. **(PARKED by owner) G1(d) objective qualification.** PORTING-STATE s6640-s6687 first.
11. **RENDER_TO_RAM=0 CLOSED s7389: ready for the owner (OWNER-OPT-INS), default stays on.** Saves ~2.5 ms/gfx task in
    mission (s7385); abort-cut stale-upload stripe fixed (s7387, ROGUESQ_R2R_CPUUP=1 old); soaks L1/L4/L12 300 s pass (s7389);
    fb-cpu-reader census CLOSED s7391 (0 guest loads from a live colour image on 6 levels; build_fbld, ROGUESQ_S7389_FBLD=1).
    Not covered: RSP/RDP DMA reads (RT64 fb-as-texture owns those).
12. **Rerun-after-change censuses (all CLOSED, 0 defects; tool list verbatim in PROJECT-OVERVIEW "(s7534 maintenance)"):**
    after a regen run tools/scan_selfbranch.py + the s7407-s7419 emission tools with --controls (rc 0); after a ucode regen tools/ucode_regen.sh verify
    + tools/s7507_rsp_ctrl_flow.py + s7508_rsp_scalar_gaps.py + s7509_rsp_vec_operands.py; after a librecomp/ultramodern
    replacement change tools/s7527_host_replace_audit.py --controls; after any new host writer into guest RAM tools/s7542_gc_census.py; after a src/main static/hook change tools/s7548_gh_census.py; after a fixup/apply script edit tools/s7549_gi_census.py --controls; after an RT64 fullSync/framebuffer-manager edit tools/s7550_gj_census.py --controls; after a librecomp/ultramodern getter or a new os*_recomp import tools/s7555_go_census.py --controls; after a scheduler/replacement or injected-yield change tools/s7543_gd_census.py --controls and tools/s7546_gf_census.py --controls; after a new host-retained guest pointer (osSetEventMesg-style registration) tools/s7547_gg_census.py --controls; after a class-touched function change, its class scorer.
13. **Closed, reopen only on an owner report:** transition stalls (s7065/s7285), host self-time (s7066-s7070),
    misnomer rename (s7080; tools/apply_symbol_renames.py), G1e residual (s6996), G5c freezes (s7285), GPU
    contention (s7283), WIDEWIN thread (s7271), Retina (s7224), window/aspect G1f (s7228).
14. **Harness discipline (CLOSED s7313-s7314, s7332):** iteration tools take the pid from tools/rs64_game_pid.zsh;
    loop.sh SIGKILLs any game alive around each soak recipe and names it in SOAK-RESULTS (a kill line = that run's
    frame times are contaminated). Soak recipes take the analyser's own rc (`${pipestatus[1]}`), never a grep's.
15. **Idiom-class audits s7315-s7416 (AQ-BZ) and their runtime soak folds: ALL CLOSED/PASSED** (archives: s7370, s7417,
    s7534 maintenance). No class soak is outstanding.
16. **Default-on fixes from the audits (=0 / old value restores the previous behaviour):** full list verbatim in
    PROJECT-OVERVIEW "(s7534 maintenance)" (SPILL_RESET, RSP_DMA25, S7334-S7364, CF0_DUPDROP, DLPOOLX_ARM_REBUILD, S7376-S7405
    locks/fixes, FTZ, STICK_GATE s7513, S7528_EVICT, the s7533 FPS60 clamp byte CAS).
17. **Class GA (s7535) CLOSED as owner opt-in (s7537).** tools/s7535_ga_census.py (565 sites, 0 open H-latent-fix, exits 0,
    --controls 10/10); knob ROGUESQ_SP_LATE=0|1|alt (+SEED); (b) H-colour-only (s7536); (c) cost scored from the present ring by
    tools/s7537_ring_cost.py (quiet harness has no [g1b]; score from --from 72, the mission load is 62-67 s), runs
    scratch/s7537_splate_cost_batt. Open only: the queued AC repeat scratch/agent/soak_queue/s7536_splate_cost.sh (runs when on AC;
    fold with `python3 tools/s7537_ring_cost.py scratch/s7536_splate_cost <arms> --from 72`); if AC L12 dd4 late < early - 0.5 in a
    3v3 ABBA, try delivering SP done at the LLE's last input fetch. Owner decides the default.
18. **Class GB follow-ups (s7540-s7541).** (a) CLOSED s7545: NODRAIN=3 vs =1 vs 0 (ASYNC=1, owner recipe, L5/L12 dd4, ABCCBA,
    battery clk 1.44-1.53 ALLOW_SLOW, scratch/s7540_rwait_cost, tools/s7537_ring_cost.py --from 72): gen/s L5 59.4-59.5, L12 59.8-60.0 in
    every arm, 12/12 alive, 0 stall -> no game-rate cost where the game holds 60 (single-source; CPU-bound case not exercised). (b) CLOSED s7541: post-
    reads_done read-ins / writeback clobbers / hashTracking 0 on L4/L12/L1. (c) CLOSED s7542: s7541_wbw_rwait
    (NODRAIN=3, L4/L12 dd4, L1 dd8 21:9) live readers only RT64 updateScreen XXH3, ctl fired. (d) CLOSED s7542: class GC census (headline).
19. **Class GE CLOSED (static s7544 + runtime s7545, headline).** Reopen only if a guest code path reads OSThread fields.
    **Class GF CLOSED s7546** (tools/s7546_gf_census.py, rc 0, --controls 5/5): 122 host OSThread-field reads; the 7 reachable after
    osDestroyThread(other) (wait_for_resumed:289, _thread_func:621/625/635/636) are equality compares of ->context against the
    thread's own captured context, or on the true side of one, so any reused value self-terminates (H-safe); the rest are live/diag.
    Guest: service-worker keys are monotonic (0x801128D4) and unregister unlinks before rs_free, so no OS call names a freed struct.
    Runtime (s7545 logs): 8/8 destroys per level followed by the woken thread's self-destroy re-call, 0 dead-ctx, 0 resume-skip,
    0x801937F0 reused as a new thread 0.2 s later.
    **Class GG CLOSED s7547** (tools/s7547_gg_census.py, rc 0, --controls 6/6): every guest pointer ultramodern/librecomp retain
    past the call (event/VI mq, VI mode + fb, timer, PI retQueue) resolves to a static object < heap base 0x80154690 (derived from
    initMainHeap) or the top-of-RAM fb carve (fb slot table 0x80128E98 writers verified = initVideoSubsystem only); 0 heap objects
    retained. Event queues match the s7395 runtime list one for one.
    **Class GH CLOSED s7548** (tools/s7548_gh_census.py, rc 0, --controls 10/10; static, single-source): 272 src/main statics
    (247 int/atomic, 7 pointer, 18 container) capture a guest-derived value; 249 are never dereferenced and never escape (H-diag);
    the 23 that are: 2 H-inflight (s_pending_task_data_ptr / s_pending_audio_task, re-set per task in get_rsp_microcode), 6 H-gated
    (default-off env, verified per deref site), 2 H-base (rdram itself), 3 H-host (calloc shadows), 2 H-refresh (s7031 terrain dims
    re-read per frame), 8 H-value escapes (PCs, s6919 cutoff float bits, s6893 clamp). 0 OPEN. Control 1 first FAILED (MEM_* macros
    were not deref sites) and was fixed before the verdict.
    **Class GI CLOSED s7549** (tools/s7549_gi_census.py, rc 0, --controls 9/9, 7.5 s; static, single-source): 5174 static
    declarators injected into RecompiledFuncs/funcs_*.c (block-scoped; file-scope incl. every comma declarator); 101 (name, PATCH tag)
    rows capture a guest value; 93 never reach a guest deref / ctx reg / guest store (H-diag; host callees of the 4 call-escaping
    rows take values only). The 8 that do: 3 H-inflight (s7482 reserve base, consumed in the same partitionFramebufferMemory call,
    pend cleared each pass; s7108_s2 read by s7108_x later in the same function, no label between; rs5839_obj read by the
    default-off rs5835 probe right after entry), 1 H-refresh (s6496_a0, re-read from a0 before each deref), 4 H-value (org6418 /
    org6421 / org7011 float bits of static 0x8009DEB4 / 0x8009DE94 constants, og6112 viewport ints, VPW_SCALE-gated). 0 OPEN.
    **Class GJ CLOSED s7550** (tools/s7550_gj_census.py, rc 0, --controls 8/8; static, single-source): RT64's 4 default-on RDRAM
    writes (fullSync colour/depth copyNativeToRAM; renderToRAM defaults on) take address = current pair SETCIMG/SETZIMG, width =
    colorImg.width, rows = drawColorRect/drawDepthRect, the retained fb.height only as a min() clamp; the registry walks (storeRAM,
    checkRAM, uploadRAM, hashTracking) take const RDRAM; present reads the current VI origin; 0 open. Host side of the s7545
    heap-reuse family (GF-GJ) closed.
    **Class GK CLOSED s7551** (ROGUESQ_S7551_GK=1 + _PLANT=1, tools/s7551_gk_score.py --controls 4/4; runtime, sync RDP only):
    snapshot every written-back span at checkRDRAM, diff snapshot/pre/post per byte at each writeback, L1 dd1 / L4 dd4 / L12 dd4
    16:9 FPS60: 0 bytes changed between DL start and writeback in ~45 GB compared (H-clean), planted control 99.5-100% seen and
    clobbered (depth-kind 376/376 pre-mission; mission depth span is first written back as a colour Z-clear pass at the same
    address, which consumes its plant). The full-row writeback never reverts a guest/host write. Not covered: RDP_ASYNC=1.
    **Class GL CLOSED s7552 (H-dither, benign; tools/s7552_gl_score.py --controls 5/5; two lines: per-pixel numbers + FbWriteColorCS):**
    mission colour rtOut is RT64 re-dithering undrawn columns from the retained render target on each writeback when the fb's
    bestDitherPattern is NOISE (L12 dd4: 436,631 px, all ±1, up/down balanced, 97% col 795 = outside the scissor, rest a rect 28-774
    frame); MAGICSQ fbs (L1, L4) give 0. No guest reader, present uses the render target: no fix.
    **Class GM CLOSED s7553 (tools/s7553_gm_score.py --controls 5/5; ROGUESQ_S7551_GK=1 + rs64RawRect pre-scissor draw union + 16 MB
    shadow of RT64's last writeback):** every out-of-rect writeback change in every phase (L12 5.4M colour / 10.9M depth px, L1) has
    pre == RT64's own previous writeback (1.00000); colour post within ±1 of it, dark/bright balanced (re-dither); depth keeps z
    (post>>2 == pre>>2) and only rewrites dz (game Z-clear fill 0xFFFE -> depth target 0xFFFC). The s7552 pre-mission "fade" cols
    41-56 are outside every draw and ±1 like the rest (s7552 F test accepted only upward moves). **Class GN CLOSED s7554 (H-clean, async):** GK+GM rerun under
    ROGUESQ_RDP_ASYNC=1 NODRAIN=3 (L12/L4 dd4, L1 dd1, 16:9 FPS60, 120 s; scratch/s7554_gn): gwb=gch=clob=0 colour and depth, all
    phases, ~18 GB compared; plant control 1130/1136, 1208/1212, 1478/1484; GM verdicts identical to sync (C H-dither, Z H-depth-req,
    preIsLast 0.99994-1.0). Async witness same run (scratch/s7554_gn_ctl, L4 + ROGUESQ_G1B=1): [s7540-rw] sig=9427 idle=0, GK H-clean,
    ctl 890/892. The guest never touches a pending writeback span, so the worker's late full-row writeback reverts nothing. All 4
    GJ write sites carry the hook. OWNER-OPT-INS row now gives NODRAIN=3.
    **Class GO CLOSED s7555** (tools/s7555_go_census.py, rc 0, --controls 7/7; static, single-source except osViGetCurrentField =
    retail oracle s2199/s2211): every value-returning replacement (74 defs) and every device-status getter. Of 29 the game imports
    (168 guest call sites, $v0 read/kill per site): 0 device-status getters other than osSpTaskYielded and osViGetCurrentField.
    osAiGetLength/GetStatus, osDpGetStatus, osPiGetStatus, osViGetCurrent/NextFramebuffer, osGetCount and every __os*DeviceBusy are
    not imported (nm), and the generated code forms no 0x04xx/0xA4xx/0x1FC0 register base, so nothing polls DP/AI/PI busy and
    NODRAIN/ASYNC cannot hand out a stale status. osSpTaskYielded (spTaskSchedulerThread 0x80019E14, sets resume flag 0x8011A89F)
    returns 0 = completed, right because the LLE never yields a running task, whatever the mode. osAiSetNextBuffer always returns 0
    (retail -1 when the FIFO is full), but both runAiAudioStreamPlaybackLoop sites kill $v0 (H-ret-unused). The rest are synchronous
    (PI, EEPROM, SI), no-pak, queue results, or not status values. Instrument bug fixed before the verdict: ctx->r29 matched
    ctx->r2.
    **Class GP CLOSED s7556 (H-unit-ok; tools/s7556_gp_census.py rc 0, --controls 9/9; static + s7402/s6256 runtime):** all 14 osGetTime
    sites consume only the low word $v1 (GO's $v0-only scan read 'kill' there); none reads the 64-bit value. Every time divisor reads
    osClockRate (3 fns; no hardcoded 46.875/62.5 MHz in game code); host 46875 ticks/ms, osClockRate fix default-on. Sim dt
    (timeSnapshotFiller +0x20) = dstamp/clock + getViModePeriod()*0.001*N (N = VIs per frame if >=2, else 1; ROM K=K'=0.001,
    period 16.667/20 ms): linear in VI count, so FPS60 single-VI frames get exactly one VI (s7402 runtime histogram: 1-VI frames
    exist and sum tracks wall). Durations reach only the gated profiler or write-only globals.
    **Class GQ CLOSED s7557 (H-unlisted, fixed by listing; tools/s7557_gq_census.py rc 0, --controls 11/11; static):** code->docs
    direction of s7426 (which checked docs->code). 3934 built sources incl. generated RecompiledFuncs, 3877 getenv sites + defaulting
    helpers: 215 default-active names = 115 behaviour levers ON when unset, 23 diag-only, 77 feature parameters (value defaults,
    inert unless their feature is on). Every ON lever has =0 by construction (the parse idiom is the switch) -> H-no-switch cannot
    arise for an env read. 97 listed; 17 had NO row in OWNER-OPT-INS/CURRENT-TRUTH/FPS60-FIXES/PROJECT-OVERVIEW (AUDIO_PRIVATE_DMEM,
    AUDIO_WAIT_NOPUMP, COPY_GUARD, DD_OFFMAPCULL_EYE, DPC_KEEP_PIPE, DPC_WRAP_FLUSH, FL_HDR_HARD_SKIP, G1D_OVL_WRAP, HLE_PATCH_ALPHA,
    PIO_GUARD, PI_DMA_GUARD, PI_UNK_COMPLETE, PREEMPT_POINT, S4272, S6892, SPAI_GUARD, WRAP_RESTORE), 1 no session (G1D_FPDEPTH).
    Fix: generated docs/DEFAULT-ON-LEVERS.md (every ON lever, sessions, source comment; `--write` regenerates), linked from
    OWNER-OPT-INS. Not covered: unconditional fixups with no env at all -> class GR (NEXT.md).
    **Class GR CLOSED s7558** (headline): fixup hunks with no env switch; 1 BEHAV (B40 gate, owner decision, item 4).
19b. **Regen health (s7558) CLOSED s7564**: (a) s7559, (b) s7560, (d) s7561, (e) s7562, s7420 census s7563, (c) B40 A/B s7564
    (headline). Rebuild the trees: tools/regen_front.sh D/pristine; cp -R D/pristine D/replay; tools/regen_replay.sh D/replay;
    tools/regen_verify.sh D/replay D/verify.
19c. **Compensation-chain audit CLOSED s7565** (headline; docs/COMPENSATION-CHAINS.md, `tools/s7565_comp_chain.py --write --check`).
19d. **Retail-route chain simplification (s7565, OPEN, next; NEXT.md).** For each of the 12 retail-route chains, decide offline
    whether the parent can be confined so the child becomes dead code with identical default behaviour (start: dpc_bridge trio
    DPC_KEEP_PIPE / S4272 / WRAP_RESTORE; then CUT_LIVE vs s6418, SHADE_ORD_RESET vs its diag map). Never flip a default.
20. **When 1-19 offer nothing an agent can do:** take the next open ITERATION.md 3c rung (G5 renaming sweep,
    item 4) or a new idiom-class audit; do not write a backlog-exhausted block.

## Evidence index

- Maintenance archives (whole CURRENT-TRUTH verbatim): PROJECT-OVERVIEW s7417, s7370, s7307, s7187, s6994; trims s7262,
  s7134, s7121, s7104, s6982, s6962; s6900, s6847, s6759; [Maintenance s6667 retained evidence](PROJECT-OVERVIEW.md#maintenance-s6667-retained-evidence).
- Objective contracts [G1-OBJECTIVE-RESPONSE](G1-OBJECTIVE-RESPONSE.md); images [G1-FRAMEBUFFER-COVERAGE](G1-FRAMEBUFFER-COVERAGE.md).
- Owner commands docs/OWNER-OPT-INS.md; owner sheets docs/owner_sheet_s7*.png/jpg.
- Queued-soak verdicts `scratch/agent/SOAK-RESULTS.md`; loop.sh edits take effect before the next soak phase
  (s7235 re-exec); idle-gated recipes polled up to SOAK_IDLE_WAIT=1800 s (s7254).
- Recent chronology: PORTING-STATE sessions 7417-7452; search bounded windows only.
