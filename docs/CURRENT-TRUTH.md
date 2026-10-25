# Rogue Squadron 64 Recomp — current truth

Compact operational handoff, maintained as of Session 6215 (2026-10-25).
`PORTING-STATE.md` is the chronological ledger. Durable background and closed
detail are in `docs/PROJECT-OVERVIEW.md`; exact run verdicts are in
`scratch/agent/SOAK-RESULTS.md` and the named audit documents.

## Headline

- The qualified route boots attribution, N64 logo, intro, Factor 5 logo, title,
  hangar, and mission origins. Mission input reaches flight code.
- M6 first-mission route endurance is closed: 31 keyed title-to-mission holds
  (251 minutes), including 10/10 long holds with the hangar route, had zero
  crash and zero VI stall. Idle autopilot eventually reaches a legitimate
  mission-failed path; this is not proof that every mission is correct.
- M5 audio de-stubbing is closed for the qualified route. Audio fidelity fixes
  were reverified at s5926 (underrun 1/15360, rails 3/368 loud rows); owner
  listening follow-up is recorded in `docs/G2-AUDIO-FIDELITY-CLOSURE.md`.
- M3 idiom audits, generated-symbol renaming, and regeneration determinism are
  closed. M4 accumulator and native hangar artifacts remain parked.
- G1 is now mission coverage, not autopilot development. The owner directive
  on 2026-10-22 closes the s5841-s5930 aim/steer/bolt thread as harness work.

## Current frontier: G1 mission coverage

The companion decomp census gives `NUM_LEVELS=0x13`: playable levels 0..18;
`LOGO_LEVEL=0x13` and `ATST_LEVEL=0x14` are sentinels. Levels 1..9 and 11..14a have route
and 300-second hold coverage (a)+(b) (s5938). Levels 10 and 15 PASS (a)+(b) only after the ~790 s planet-intro
viewer auto-advance (s5943) or with `ROGUESQ_FORCE_PLANET_UNLOCK=0xFF`; short waits end `nomission`
(`curOvl=1 cineState=F7B80040`, origins 0x644D00/0x6A2900) - a retail planet-intro timer, not a crash.
Levels 15b..18b held clean in the G4 sweep (s5999-s6082). A valid coverage run requires `[lvsel]` with
`a1 == 1<<level`, flight handoff, >=300 s alive, zero crash lines, and no 30 s VI stall; missing controls
are failures of evaluation. Shared runner lives at `scratch/agent/g1_level_coverage_common.zsh` (outside the queue glob).

G1 verification, once route+hold works for every level, additionally requires
a framebuffer showing terrain, craft, and HUD, plus a forced-hit objective
counter/end-gate response. Mission-to-mission progression and making the
autopilot win are owner playtest scope.

## Durable state and constraints

- Audio default route is active; `ROGUESQ_AUDIO_UCODE=0` is the silent control.
- `ROGUESQ_AUDIO_DEVICE` and `build/audio_device.txt` are owner routing state;
  do not alter them or treat `[audio-route]` as M5 evidence.
- Hangar route (s6006-s6011, post FIX_ZERO_SHADE-off): 9 soaks a-i, 8 first-attempt (att=1) and 1 att=2 (run h; log holds only the summary line, no crash/stall recorded), all 600 s holds with 0 crash / 0 VI stall. The old ~1/3-3/5 flake rate is NOT reproduced (single-source harness). G4 hangar route closed. Native hangar
  artifacts (rim band, holo spikes, stale edge, overlay splice, accumulator
  origin, `0x1F0D74`, odd PI DMA) are parked. No mitigation is acceptable
  without naming the writer and establishing value legitimacy.
- PatchesLib is shadowed on macOS; the live heap guards are fixup-inlined.
  `-force_load` is an unperformed behavior-changing A/B.
- A real MIPS cross-toolchain is installed at `/opt/homebrew/bin`; fresh
  source-to-ELF patch qualification is optional because the existing ELF path
  is qualified.
- The title plume `si_addr=0x58` is probably dissolved by the s5597
  `poke_be32` overflow fix (28 clean boots); wait for passive recurrence.
- The open human dependency is the real-input lv0 play:
  `scratch/agent/g1_human_play.sh human1`, then read its summary. This does not
  block offline coverage work.

## Operational rules that remain live

- Read `docs/F5-UCODE-REFERENCE.md` before interpreting Factor 5 display lists.
  Retail oracle evidence needs whole-RDRAM, VI, and phase positive controls.
- Batch instrumentation and all A/B arms in one build/run. Gate animated
  comparisons on VI transitions, not wall-clock time. Scope budgets to phase.
- A null requires a positive control in the same run; two independent lines of
  evidence are required before changing current truth.
- Ground truth precedes new instrumentation. A mitigation is not an
  explanation: identify the writer and establish whether its value is legal.
- Generated changes belong in fixup tooling. Regen order is
  `make_elf.py -> N64Recomp -> fixup_game_funcs.py -> cmake`.
- Run from `build/`, capture output to a file, and SIGKILL test process groups.
  Never reset, clean, checkout, or update a submodule. After editing `lib/`,
  run `./submodule-patches/export.sh` and commit refreshed patches.
- Static `jal` does not maintain r31 in generated code; host backtraces identify
  callers. VI origin is a framebuffer address and is content-blind.

## Closed or parked threads

- Overlay dispatch/DMA fix and the qualified render route are complete.
- M5 de-stubbing and G2 root-cause fixes are complete pending owner listening.
- M3 crash classes, M4 accumulator comparison, generated-symbol sweep,
  title-plume clean-boot loops, and mission-aim harness work are closed or
  parked. Do not revive them without genuinely new evidence.
- The old mission outcome/voice/death diaries and the s5841-s5930 aim ledger
  were migrated to `docs/PROJECT-OVERVIEW.md` during prior maintenance. Their
  historical hypotheses are not current work items.

## Next steps (single monotonic backlog; per-session history archived in PROJECT-OVERVIEW.md, "Archived CURRENT-TRUTH backlog")

1. **G1d widescreen (active, `scratch/agent/NEXT.md`).** s6216: alias measured (ctl HUD TLUT 0xB24xxx outside memset/wb ranges ending 0xB00000; wide TLUT inside range ending at pool 0xAE6E00): the s6207 image drop is 0x25000 too short; next test drop += 0x25000 (NEXT.md). s6215 (lldb write-watch, positive control held): wide 0xAE5F20/0xAE6B20 "texels" are genuine guest HUD TLUT data (`packTlutEntriesRgba5551 <- loadTextureToMemory <- parseHmtMaterials <- buildHudAmmoReadout`), later zeroed by `rs_memset <- initVideoSubsystem` and rewritten by RT64 `copyNativeToRAM` writeback (wb range ends 0xAE6E00). Aliasing of texture memory with the enlarged framebuffer range. Next: compare wb/memset extents against texture allocations (NEXT.md). Keep the image drop; do not raise the 48-line cap, skip `copyNativeToRAM`, retarget `0x8096D600`, write `0x801163E8`, change n=3 `t0`, raise `osMemSize` or move `f0`.
2. **G1e higher frame rate** after G1d (spec: ITERATION.md 3c).
3. **G1 level 10/15 note:** both pass (a)+(b) only with `ROGUESQ_FORCE_PLANET_UNLOCK=0xFF` or a
   ~790 s planet-intro wait (SOAK_TIMEOUT >= 900). Forced-hit objective (d) is PARTIAL: counters move
   on lvl1-5,7,8 but no level end was shown driven by them (s5997).
4. **Parked, do not revive without new evidence:** G4 crash hunting (all 19 levels + hangar route
   clean, s5999-s6082); G3 hangar artifacts; M4 accumulator; title plume `si_addr=0x58`.
5. Optional: fresh MIPS source-to-ELF patch qualification; real-input lv0 human play.

### Settled results worth keeping (from the archived backlog)

- **G1b CLOSED (s6017):** slow seconds were our O(n^2) scan in rsp_dpc_submit (dpc_bridge.cpp); fixed
  with a hash index: 17.6% -> 0% slow seconds. `ROGUESQ_G1B=1` is the frame-time instrument.
- **G3b CLOSED as opt-in (s6085):** spike lines = ucode clip-plane wedges (Y pinned -170.25) plus
  off-screen tris; `ROGUESQ_CULL_SPIKE=1` opt-in cull, `ROGUESQ_LOG_SPIKE` instrument.
- **G1c phase 2 CLOSED (s6102):** `ROGUESQ_DRAW_DISTANCE` capped at 2 (auto-far; tri x2.3, terrain
  fraction 0.030->0.074, VI 60/s, 300 s clean on L1/L5/L10) unless `ROGUESQ_DD_UNSAFE=1`. dd>=3
  dies in 150-290 s: display-list chunk pool (*(0x801163B0)) / finder `findAndUnlinkSmallestEntry`
  (0x8002221C) returns NULL, deref at 0x8000A97C; not heap, arena, LUT size or pool size (s6086-s6101).
  Writer of the exhaustion unnamed. rc=0 is not a pass: read `alive_at_end`. Levers: UCODE_CAP
  (`ROGUESQ_UCODE_CAP`, default 16384 retail), DD_FAR, POOLX (px2 safe, px3+ exhausts the 8 MB heap),
  BIGARENA, DLPOOLX. Owner guide: docs/DRAW-DISTANCE.md. Never trust the s6088/s6094 bucket readers.
- **G3 pillar stubs:** were our FIX_ZERO_SHADE (default now OFF, s5971). Render fidelity otherwise
  closed at eyeball level (retail oracle: docs/G3-RETAIL-PIXEL-ORACLE.md).
- Harness lessons: macOS has no `timeout` (use perl alarm); lldb host RDRAM base is per-run; guest
  globals read from C++ need `rdram+(int32)addr`; recipes need `# SOAK_TIMEOUT=` headers; always diff
  tele vs ctl recipes.

## Evidence index

Use `PORTING-STATE.md` only through bounded grep/sed windows. Use
`docs/PROJECT-OVERVIEW.md` for migrated history, `docs/M5-AUDIO-PLAN.md` for
audio inventory, `docs/F5-UCODE-REFERENCE.md` for the microcode contract,
`docs/M6-OBJECTIVE-COUNTER-WRITERS.md` and `docs/M6-PHASE-MACHINE.md` for
mission logic, and `scratch/agent/SOAK-RESULTS.md` for queued verdicts.

## G1d levers (s6113-s6118)
`ROGUESQ_VPW_SCALE`, `ROGUESQ_ASPECT_SCALE`, and `ROGUESQ_FB_WIDTH` are the levers. Scissor does not follow the camera rect. 683-wide flip buffers overlap unless `partitionFramebufferMemory` sizes them `a2*a3*2`. s6116's second colour-image pointer was the intermediate target at `0x801163E4`, not a missed flip. VI field origins (mode +0x28/+0x3C) scale with the width. The widened RDP stream itself was width-consistent; the black window was the RT64 width allowlist, fixed at s6119. Default stays retail.

## G1d status (s6119)
ROGUESQ_FB_WIDTH=683 now renders (s6119): RT64 width allowlists (last-drawn store, mode-3 saneW, writeback allowW) accept width==FB_WIDTH; VI regs verified consistent (w683 xScale 0x444, origin field offset 1366). Fbdump flip shows a correct frame; on-screen window not yet verified. Next: window screenshot with game frontmost, then wire ROGUESQ_ASPECT=16:9/21:9 (FOV/HUD x), menus/hangar check.

- s6126: NULL-dest DMA writer = rs_malloc(0x1000) returning NULL (consumed unchecked by processAssetLoadStep s0+0x48 -> submitDmaSlot); heaplog shows live only 0x3FF568 of the 8 MB heap at that moment, so it is allocator capacity/fragmentation, not volume. [heaplog-null1000]+[pi-null-dest] diagnostics landed (ROGUESQ_HEAPLOG, ROGUESQ_LOG_DMA). NEXT: dump freelist (largest free block, heap bounds) at the NULL, vs ctl at same ordinal.
- s6125: ring-producer soaks (wide+ctl) show the NULL-dest 0x1000 DMA (devAddr 0xB01A5E20, mb 0x80110828) is NOT enqueued by submitDmaRequestBatch in either arm (9018 other rows fire = control), so the ring-clobber/ring-producer-NULL hypotheses are closed (they were believable because the ring was the only instrumented producer). Open: H-heap (NULL rs_malloc at wide FB), H-ptr (NULL global), other producer. NEXT: env-gated fixup diagnostic logging rs_malloc==0 + caller and dest==0 queue callers.
- s6124: 4:3 ctl has 0 NULL DMAs; at 21:9 the same stream scratch buffer yields dest 0 one request after valid chunks (H-heap vs H-clobber open); ring-producer soaks s6124_g1d_ring_wide/ctl queued.
- s6123: wide-mission crash = NULL-dest PI DMA (failed alloc), H-heap leading, ctl43 DMA-log soak queued.
- s6121: ROGUESQ_ASPECT=<w>:<h> (>4:3) now derives FB_WIDTH+scales in main.cpp; 16:9/21:9 soaks queued, results pending.

- **G1d s6122 (supersedes s6120 'widened frame works end to end'):** ROGUESQ_FB_WIDTH/ASPECT 683/797/1045 all crash 5/5 at mission start (do_rom_read, 64-bit DMA dest 0x380000003, ~150 lines after initMission n=1); 4:3 ctl is fine. s6120's screenshot was pre-flight only. The `initMission+1000` frame in logs is the lvinit-bt diagnostic, not the crash. H-heap (wider pfm fbs starve the 8 MB heap -> NULL alloc) vs H-stride untested; s6122 soak (ROGUESQ_LOG_DMA) queued to name the caller. s6121 screenshots are invalid (game not frontmost; use s6120_run.sh's osascript activate).

## s6127 update (G1d 21:9 crash)
The 21:9 NULL-dest DMA is rs_malloc(0x1000,flags=9) failing from true MAIN-heap exhaustion (0x80154690..0x8071B670, free 0xCB0, used 0x5C5E50) with the secondary heap slot (0x8010FF00) = 0; the 4:3 control has the main heap to 0x80795BF0 with ~2.6 MB free. Not fragmentation. Open: which allocations add ~2 MB in wide, and why heap end / secondary slot differ. See PORTING-STATE Session 6127.

## s6128 update (G1d 21:9 heap)
Allocation stream (every rs_malloc>=0x4000) is identical wide vs 4:3 for ~370 rows; extra consumption is ONE heap block: 0x3E4B00 (wide) vs 0x2DB000 (ctl), created by a path the heaplog misses (no logged rs_malloc has either size), plus heap end lower in wide (0x8071B670 vs 0x80795BF0 later in ctl). `[heapwalk-top]` instrument landed. Next: find that block's creator and the ctl heap-end growth.

## s6129 update (G1d 21:9 heap root cause)
The 21:9 heap deficit is the widened framebuffer carve: partitionFramebufferMemory (0x80000DD4) places fbs at the top of the 8 MB (globals 0x801163D8/DC/E4/F8), each w*448*2 (512: 0x70000; 1045: 0xE4980), so 21:9 moves heap end -0x74980, fb base and the top-down pool -0xE9300 and costs ~1.9 MB of the 2.6 MB 4:3 free space (-> NULL rs_malloc(0x1000), s6127). The 0x2DB000/0x3E4B00 "block" is that pool region. 16:9 (796) has no heap NULL but stalls in initMission -> initializeObjectiveTracking -> lv1_initializeObjectTracking (new, uncharacterized). Fix routes: lift RT64's 8 MB rdram cap (osMemSize up to 16 MB; ROGUESQ_OSMEM_MB clamps to 8 in recomp.cpp:565) or shrink the carve. NEXT: find where RT64 caps rdram, and charcterize the 16:9 stall.

## G1d update (s6130)
RT64's 8 MB rdram bounds (state.cpp:3395 etc.) widened to 16 MB; ROGUESQ_OSMEM_MB now allows <=16. 12 MB then dies at boot (4:3 too): DL-chunk pool *(0x801163B0) is len=0 at first beginFrameDLChunk (8 MB: 1356). The game's pool build depends on osMemSize. NEXT: find the pool builder (store watch on 0x801163B0 during boot, 8 vs 12) and see which osMemSize test skips it; alternative route is shrinking the fb carve at 8 MB instead.

## G1d update (s6131) — supersedes s6130 'pool not built at 12 MB'
The pool IS built at 12 MB (head 0x80B20000, builder 0x80017B88 via initVideoBootWrapper). The crash is our ~1011 hard-coded `0x80800000` pointer-range guards in generated funcs (+107 in src/main, 28 tools scripts) rejecting any pointer above 8 MB; s6130's len=0 was the instrument's own 8 MB walk bound. NEXT: replace the literal with a runtime RS64_RAM_TOP in the fixup script, rebuild, retest OSMEM=12 (then 21:9/16:9).

## G1d update (s6132)
8 MB pointer guards are now RS64_RAM_TOP (runtime, = 0x80000000+OSMEM_MB): funcs_*.c via tools/fixup_ramtop.py (last fixup stage), C++ via tools/apply_s6132_ramtop_cpp.py (already applied; lib edits exported). ROGUESQ_OSMEM_MB=12 now boots, reaches initMission lvl1, then hangs after lv1_initializeObjectTracking (no crash; same spot as the 16:9 8 MB stall). Next: sample/lldb that stall, compare args/pool vs 8 MB. Then 21:9 at 12 MB.

(s6133) OSMEM=12 "hang" REFUTED as a deadlock: waitForPostSwapAck cycles ~30/s and the post-swap flags advance; the scanned-out frame (origin 0xA90400) is frozen stripe garbage; m6_god_common.sh:30 hardcodes origin 0x00790400 so 12 MB runs read "notitle". Single-arm (8 MB control not run). NEXT: compare RDP color-image address vs VI origin vs what RT64 reads at 12 MB; parameterise the harness origin.

(s6134) Two more RT64 8 MB caps fixed (workload_queue.cpp:500 colour-image drop, f3dfactor5.cpp:193 matrix load; 16 MB now). OSMEM=12 still shows non-flight garbage frames and "nomission"; 8 MB control not yet run. Harness accepts TITLE_ORIGIN. NEXT: 8 MB-vs-12 MB same-recipe control with per-frame SetColorImage address / VI origin / rdram hash at origin.

(s6135) OSMEM=12 'nomission' was a harness constant (12 MB origins = 8 MB origins +0x400000; use TITLE_ORIGIN=0x00B90400 MISSION_RE=A90400). Real defect: RSP DMA (rsp.hpp:239), sp.cpp range check and dpc_bridge.cpp:2850/3934 dropped everything >8 MB -> widened to 16 MB; RT64 now draws at 12 MB (rt64drawn 13k lines). Unverified: flight frame correctness at 12 MB and a ~4x lower swap count per hold. NEXT: dump the VI-origin frame (ROGUESQ_FB_DUMP_VI=1) in flight at 12 MB, find why swap n stalls ~1500, then 16:9/21:9 at 12 MB.

(s6136) OSMEM=12 swap-rate collapse: gfx task 236 ms CPU vs 9 ms at 8 MB (G1B + sample). RT64 makeFramebufferTile row loop (stale 1x1 fb @0xFF0000) fixed closed-form; remaining cost is loadTLUT/loadToTMEMCommon with oversized params => the RDP stream at 12 MB is corrupt (garbage frame). NEXT: log bad LoadTLUT/LoadTile params 8 vs 12 MB, trace the producing ucode word (masks 0x7FFFFF in ucode/main.cpp walker, DMA >8 MB).
(s6137) OSMEM=12: RT64 first TLUT already junk with NO preceding SetTImg (8 MB control sane); no 8 MB mask left in RT64/ucode data paths. So the RDP list window (DPC start/end) or the RSP DMA-out to it is wrong at >8 MB. NEXT: log DPC start/end + first words per submit, 8 vs 12 MB.
(s6138) OSMEM=12 corrupt RDP stream ROOT CAUSE: librecomp rsp.hpp dma_dmem_to_rdram dropped writes >= 8 MB (s6135 fixed only the read side); widened to 16 MB, lib patch exported. 12 MB now matches 8 MB RDP bytes, task cost 9-10 ms, 0 crash. (s6139) 12 MB flight frame verified correct (terrain/craft/HUD; 60 s clean). NEXT: ROGUESQ_ASPECT=21:9 and 16:9 with ROGUESQ_OSMEM_MB=12 (heap deficit s6129 should now be gone).
(s6141) 21:9 fails identically at OSMEM 12 and 16 (memory refuted); 18:9 w896 renders correct flight => failing width in (896,1045], suspect 1024 cap. NEXT: bisect FB_WIDTH 960/1024/1032.
(s6140) OSMEM=12: 16:9 renders correct widescreen L1 flight (w796 dump, 0 crash; harness origin regex invalid for wide arms - judge by dump). 21:9 (w1045) still never reaches a wide frame (w320 stripe garbage, guest stall). NEXT: bisect 21:9 by width (e.g. ROGUESQ_FBW between 796 and 1045) at 12 MB to find the first failing width; then HUD edge anchoring.

(s6142) G1d: FB width bisect at OSMEM 12: 960 and 1024 render wide flight, 1032 and 1045 fail (stripe garbage). Cap in (1024,1032]. Aspect policy now clamps width to 1024 (unbuilt/unverified). Root constant unnamed.
(s6143) 21:9 clamp to w1024 verified: 13 w1024 flight frames, 0 crash; left terrain void + HUD anchoring remain.
(s6144) Terrain left void FIXED: footprint frustum x-extent (0x800438C4) now scaled by ROGUESQ_FP_XSCALE (default=ASPECT_SCALE); terrain fills w1024 in flight. Remaining: HUD edge anchoring, menus/hangar at wide.
(s6145) HUD anchoring: flight HUD (radar, brackets, crosshair) is mesh+matrix built in initHudStruct (0x800C0084), NOT linkHudNodeAndComputeScreenPos (that is subtitle overlay; ROGUESQ_HUD_DX lever only affects it, never fired in flight). Next: find the HUD ortho/node transform consumer (watch writes to D_8010CA30+0x18/+0x1C or the HUD matrix) and shift there.
(s6146) CORRECTS s6145: D_8010CA30 is NOT a HUD struct array (mixed globals). Flight HUD element x/y are floats (320x240 virtual px) at 0x80340240..0x80340430 written by initHudStruct (pcs 0x800C0180..0x800C1320); mark-control +160 on all of them made radar/ally marker/missile counter vanish (positive control OK). Next: bisect per element block by pc range (ROGUESQ_HUD_MARKPC=<px>:<lo>-<hi>) to map x vs y, then anchor x<160 left / x>=160 right by (virtW-320)/2, check for a per-frame rewriter.

(s6152, single-source offline) HUD element block at node+0x3C: x/y floats are +0x18/+0x1C; +0x24/+0x28 are scale (sx,sy). initHudStruct is a message-switch handler, not an init. s6147-s6151 'x at +0x24' premise is superseded (believable: marking those offsets visibly moved/removed icons because scale changes). Next: find the list-walk consumer (buildHudAmmoReadout 0x800B8380, updateMenuPerFrame 0x800BB8B4, readers of *(s4)+8), then anchor +0x18.
(s6153, offline) No function loads float x+y (0x18/0x1C) off one base as a HUD draw (10 matches, none HUD); buildHudAmmoReadout only copies them. Consumer likely copies as words or goes via a generic node transform; next: runtime read-watch on an element x address (needs a load hook) or trace callers of initHudStruct's list head.
(s6154, single-source static) Draw-time HUD x/y consumer candidate: 0x800159B4 (funcs_4.c:22628), x=(elem+0x18+vp+0x18)*[0x800006F8], y likewise; driven by setupCameraMatrices lists vp+0xC/vp+0x8. Supersedes the s6153 line. Unverified at runtime.

(s6155, runtime, 2 arms single screenshot pair) 0x800159B4 verified as the flight HUD sprite emitter (also emits world sprites); [0x800006F8]=4.0, x in 4x units. ROGUESQ_HUD_CPOS=<px> lever moves ally counter + radar ring; centre threshold (160*scale) is wrong for wide view so all moved left. Next: restrict to vp=0x800cf090 list, use real centre, wire into ROGUESQ_ASPECT. Supersedes s6154 'unverified'.

(s6156) ROGUESQ_HUD_ANCHOR=A,R (w796: 142,334) puts counter+ally icon at left edge and radar ring at right edge in a fbdump; radar disc + crescent unmoved (other emitter). Wide-view HUD lists uniformly offset +142 px (vp cdc80/cd670/138d20). Next: disc emitter, derive A/R from width, wire into ROGUESQ_ASPECT.
(s6157, 2 arms, eyeballed fbdump) disc unmoved when anchor also covers vp cf090 or 165ec8 (env ROGUESQ_HUD_ANCHOR_VP): the radar disc is not a 0x800159B4 sprite; likely a mesh with a matrix translate. Next: locate the radar mesh's matrix (or screen-space shift), then derive A/R from width and wire into ROGUESQ_ASPECT.
(s6158) Radar disc = RDP tris/rects (not mesh matrix, not 0x800159B4): ROGUESQ_LOG_REGION/ROGUESQ_SHIFT_REGION (dpc_bridge.cpp rs64_region_scan, size-capped) shifts it in screen space; with ROGUESQ_HUD_ANCHOR=142,334 + SHIFT_REGION=192 at w796 ring and disc align at the right edge (single frame, eyeballed). Open: crescent, reticle displaced by anchor, derive A/R/region from width and wire into ROGUESQ_ASPECT.

- s6159 (G1d): ROGUESQ_ASPECT>4:3 now auto-sets HUD anchor + radar-disc region shift (main.cpp rs64_g1d_apply_aspect_policy). Good at w796; at w1024 RA law (0.434*ex+68.7, 2-pt fit) leaves ring missing; reticle off-centre. See NEXT.md.
- s6160 (G1d): RA law now 192+0.294*(ex-284); w1024 ring+disc aligned (auto run; ring vanishes at R>=547). Open: reticle centring, w683.
- s6161 (G1d): reticle exempted from HUD anchor (vp 138d20 elems <0x80300000 are world-projected); w796 reticle now ~+60px ahead of craft, ring/disc/counter aligned. 3:2 (w672) HUD law extrapolation bad (ring clipped, disc off) - not a target aspect. Open: owner-eyeball 16:9/21:9 contact sheet; crescent; menus/hangar under ASPECT.
- s6162 (G1d): 21:9 w1024 lvl1 full-frame check passes (reticle, radar, counter, no spikes; single-source). Next: menus/hangar under ASPECT=16:9, then owner contact sheet.
- s6163 (G1d): matched 4:3 and 16:9 route logs reached title, hangar, craft-select, and mission with zero crash markers. 16:9 title/hangar captures are visibly horizontal garbage while 4:3 captures are valid; the 16:9 route gate was invalid because it required the 4:3 title origin. Wide origins are 0x00752200/0x006AB638/0x00652438 at w796. This is a render/presentation defect, not a route failure. s6164 parameterized title, hangar, and mission origin gates in g1_fly.sh. The fresh control passed the new gate; the fresh wide arms did not reproduce the qualified route (8 MB never reached the wide title; 12 MB stalled in phase 6), so they are not new rendering evidence. Existing s6163b paired captures remain the evidence: VI width/origin transitions are correct while the first wide hangar dump is garbage. H-stride/VI mismatch vs H-menu policy remain open because the paired RDP colour-image relation was not recorded.
- s6165 (G1d): the RDP/VI join trace fired in valid 4:3 and 16:9/12 MB arms. At hangar phase 5, control emits CI width 512 and scissor 512-style coordinates with VI width 512; wide emits the same CI/scissor values while VI width is 796. Wide title/flight use width-aware CI values, so the defect is scoped to the menu/hangar video-state/display-list policy, not the route or a one-frame transition. The wide arm reached relocated title 0x00B52200, hangar 0x00AAB638, and mission 0x00A52438 with no crash markers; control reached 0x00790400, 0x006AB400, and 0x00690400. Positive control: 5,785 control and 2,460 wide RDP-route rows. Single-source runtime evidence selects H-menu-policy over H-transition-only; the exact writer remains open.
- s6166: the existing writer attribution plus the RDP route probe identified the writer. `buildAndRegisterDefaultMaterial` (guest PC 0x80017C14, global width source 0x8011A838) runs with menu/hangar dimensions `(0x200,0x154)` and `(0x280,0x154)`, while the existing s6113 hook only rewrites `(0x200,0x1C0)` (512x448 flight). In the wide arm, phase 5 therefore remains `ci_w=512`, scissor `2048x1360`, VI width 796 (640 phase-5 route rows); the writer is not a display-list decoder or RT64 present defect. The 4:3 companion reached only phases 2-4 in this attempt, so its missing phase-5 rows are a route miss, not a null result. Static store census and runtime attribution independently name the game-side writer. Next: widen only the menu/hangar 512-pixel calls behind the opt-in aspect setting, then rebuild and compare phase-5 RDP/VI joins and framebuffer dumps.
- s6167: the regeneration-safe hook now also rewrites the identified 512x340 menu/hangar call. In a paired run, control held 304 s after mission onset with 0 crash / 0 VI stall; wide phase 5 changed to `ci_w=796` and scissor `3184x1360` with VI 796 (640 route rows), proving H-menu-video-state and refuting a later display-list writer. Wide then crashed 5/5 in `renderLitTexturedMeshFaces+7948` before mission; only pre-change 512-wide dumps exist, so menu framebuffer allocation, guest render input, and RT64 downstream explanations remain open. No mitigation landed.
- s6168: `ROGUESQ_LOG_FB_ALLOC` at `partitionFramebufferMemory` plus the existing RDP/VI join was run in fixed concurrent control/wide arms. Both arms positively fired the allocation trace. The wide arm still calls the partition writer with legitimate `512x340` menu/hangar dimensions, while the opt-in video-state writer emits `ci_w=796`, scissor `3184x1360`, VI 796; framebuffer bases shift by the expected 0x400000 for 12 MB. The wide arm again fails in `renderLitTexturedMeshFaces+7948`. Independent allocation and RDP/VI evidence selects H-menu-fb-allocation: widen the matching 512x340 allocation under the opt-in aspect setting. H-menu-render-input and H-wide-RT64 are not selected. The trace is regeneration-safe in `tools/apply_s6031_far.py`; default retail behavior is unchanged.
- s6170: the allocation hook now rewrites both 512x448 and 512x340 when the opt-in width is active. In a valid paired run using actual mission origins, control and wide both reached mission and held 182/183 s clean; wide produced 320 phase-5 rows at `ci_w=796`, scissor `3184x1360`, VI 796, and the `[fbw] pfm` positive control showed `512x340 wv=796`. The prior crash disappeared. H-menu-fb-fixed is selected for that failure.
- s6171: the existing paired dumps show coherent control title/menu pixels but horizontal scanline garbage in the wide arm's early 512-wide title/menu frames; later 796-wide select-level/flight frames are coherent. Route, allocation, and phase-5 joins are sane. H-menu-layout is selected; the remaining writer is an earlier-phase menu/title width policy. Next: attribute and widen that earlier phase under the opt-in aspect setting, then rerun the same paired capture.
- s6172: a fresh same-build paired run positively fired the writer, framebuffer-allocation, RDP-route, and dump instruments. The control's first 512-wide title dump is coherent; the wide arm's matching 512-wide dump is horizontal scanline corruption. The writer census saw the same early dimensions in both arms (320x224, 640x340, 640x480, 512x340, 512x448); the opt-in arm rewrote the two 512 dimensions, and later phase-4 routes were `ci_w=796` with matching wide scissors. Thus the remaining defect is not the already-fixed 512x340 allocator or a missing logged 512 title allocation call, and it is not an RT64-only present artifact because the guest dump is already corrupt. The concurrent harness retries failed the title gate, so this is single-source route evidence, not a clean endurance result. H-unsupported-asset/earlier-phase producer remains open; no mitigation landed.

- s6173: the new phase-scoped `[g1d-join]` probe compiled and positively fired in both 12 MB arms (196 control joins, 842 wide joins; the wide route also emitted 5,743 RDP rows). At title phase 4/frame 500, control joined `VI width=1024`, title origin `0xB90400`, `CI width=512`, while wide joined `VI width=1024`, title origin `0xB52200`, `CI width=796`; both had the expected RDP list ranges and nonzero CI counts. The matching wide frame-500 guest dump was coherent in this attempt by row-uniqueness inspection, so s6172's scanline corruption did not reproduce. This validates the join instrument and narrows the defect to intermittent or frame-specific producer/layout behavior; it does not select H-early-producer or H-unrewritten-secondary. The diagnostic processes were SIGKILLed before endurance completion, so this is not a route/hold result. No mitigation landed.

- s6174 retry checkpoint: no new run was performed. The s6173 positive control and non-reproduction remain the only new evidence; the next discriminator is unchanged: capture every phase-4 title frame and join each guest dump to its CI/VI/RDP-route records.

- s6176: the every-frame capture reached 72 phase-4 wide joins (frames 417-488).
  The first attempt exposed a diagnostic defect: with VI width 1024, the dump
  helper used a 512-pixel paired-row stride even when `ROGUESQ_ASPECT=16:9` had
  selected a 796-pixel framebuffer. The helper was corrected and rebuilt; the
  fixed run logged `stride=796`, VI origin `0xB52200`, CI width 796, and matching
  wide scissors. The decoded guest frames have a coherent title around a
  horizontally corrupted central rectangle, so the defect is before
  presentation and the old dump-stride explanation is closed. Because the
  join records only the last CI, H-unrewritten-secondary (a hidden 320/512/640
  pass) and H-early-producer remain open; H-early-RT64 is weakened but not
  formally closed without a complete per-frame CI census. The diagnostic change
  is in `src/main/upstream_compat.cpp`.

- s6180: the complete-build retry matched the first 2,000 phase-4 RDP opcodes
  between control and wide arms; only expected scissor and SETCOLORIMAGE width
  and address fields differed. The wide guest framebuffer remained corrupt.
  This weakens hidden-command and RT64-only explanations but does not identify
  the late writer/readback event. Next is a complete frame-scoped RDP-range and
  raw-framebuffer-hash census.

- s6177: the new per-swap CI census positively fired in both paired arms (842
  joins each; 160 phase-4 frames each). Every phase-4 control submission was
  `512@0xB90000`; every wide submission was `796@0xB51E00`, with three repeated
  submissions of the same RDP range per swap and no hidden 320/512/640 or
  alternate-address CI. This closes H-unrewritten-secondary for phase 4. The
  wide frame-408 guest dump was also structurally non-corrupt (448 unique rows,
  all 796 columns varying; control had the expected black columns), so
  H-producer was not selected in this capture and s6172's intermittent
  corruption did not reproduce. The instrument is in
  `src/main/rt64_render_context.cpp`; no rendering mitigation landed.

- s6178: the corrected paired census ran with 842 joins and thousands of dumps
  in each arm. Phases 2-3 were identical in control and wide: phase 2 used
  only 320-wide CIs at `0xABA000`/`0xADD000`, and phase 3 used only 640-wide
  CIs at `0x9D4000`/`0xA6A000`. No aspect-specific early producer or alternate
  CI was observed. Phase 4 remained width-consistent (512 control, 796 wide);
  the intermittent central corruption did not recur. This weakens
  H-early-phase and leaves H-intermittent-layout / an in-list producer open.
  The first wrapper attempt was invalid because this checkout uses `build/`,
  not `build/Debug`; the fixed wrapper passes `BUILD=$PWD/build`.

- s6179: the corrected paired census reproduced the wide title corruption. The
  control and wide arms each had 160 phase-4 joins; every control frame was
  `512@0xB90000` and every wide frame was only `796@0xB51E00`. A wide guest
  framebuffer dump at frame 500 has the same horizontal-corruption rectangle,
  while the paired control dump is coherent. The complete CI census plus the
  pre-presentation guest-frame defect selects H-in-list-producer for this
  occurrence and rules out an early hidden or secondary CI. The writer inside
  the valid phase-4 list remains unnamed; no mitigation landed.

- s6180: a phase-4 complete RDP-word census ran in concurrent control/wide arms.
  Both arms fired the word and VI/CI positive controls. The first 2,000 command
  opcodes matched; the first word differences were the expected width-dependent
  scissor and SETCOLORIMAGE fields (`512/0xB90000` versus `796/0xB51E00`). The
  wide guest framebuffer still showed the central corruption. This weakens
  H-in-list-command as an unexpected-command explanation and leaves
  H-guest-layout versus H-intermittent-layout open. The oracle cannot reach this
  phase, so it supplied no independent phase-4 ground truth; no mitigation landed.

- s6182: the corrected 12 MB-origin paired run supplied the missing positive
  control. Both arms reached phase 4 with 160 joined frames and 1,440 route
  records. Every control record was the expected 512-wide CI/scissor stream;
  every wide record was the expected 796-wide stream, with no late alternate CI
  or hidden 320/512/640 pass. The wide guest framebuffer hashes still differ
  from control, and the run intentionally stopped at the title census
  (`MISSION_RE=ZZZ`), so no mission/hold verdict applies. H-hidden-width-pass
  is closed for the observed phase-4 route; H-guest-layout is now leading over
  H-intermittent-layout, but the framebuffer writer/stride is still unnamed.
  The wrapper also fixed stale 8 MB title origins and the missing LEVEL export;
  no rendering value or mitigation changed.

- s6183: the rebuilt paired 12 MB run again reached phase 4 in both arms with
  160 joined frames and 1,440 route records each. Every control frame used only
  `512@0xB90000`; every wide frame used only `796@0xB51E00`, with expected
  scissors and no hidden alternate CI. This is a positive complete route census
  and closes the hidden-late-CI branch for this run, but it is not the missing
  guest-write/readback discriminator: the existing word hook sees submitted RDP
  bytes, not framebuffer writers, and the dump hook does not log first host
  readback bytes. H-guest-layout, H-intermittent-layout, and H-renderer-readback
  therefore remain open. `MISSION_RE=ZZZ` means no mission/hold verdict.

- s6184: the new phase-4 `copyToRAM` trace fired 400 times in each paired arm,
  with the route positive controls still at 160 joins and 1,440 records. The
  control copied `512x448` to `0xB90000` (457,728 bytes); wide copied `796x448`
  to `0xB51E00` (711,624 bytes). All 399 consecutive `before` hashes after the
  first exactly equaled the preceding `host` hash in both arms (`mismatch=0`).
  This names the RT64 readback-copy boundary as the immediate writer of the
  changing bytes and rules out an intervening guest write between copies. It
  does not yet name the RT64 source-region/layout defect producing the wide
  central rectangle. No mitigation landed.

- s6185: the source-side extension fired 400 times in each paired arm, with
  160 phase-4 joins and 1,440 route rows each. Control read back from target
  `0xB90000` (`512x447`); wide read back from target `0xB51E00` (`796x447`).
  Center and outer source hashes were copied unchanged into the guest: all 399
  consecutive transitions matched the preceding host hash in both regions and
  both arms. This rules out an intervening guest write and source-hash
  alternation for this capture, selecting the RT64 render-target/readback
  layout boundary over H-guest-layout and H-intermittent-readback. The target
  allocation/resolve writer is still unnamed; no mitigation landed.

- s6188: the first 240-second paired run was invalid: both arms positively
  fired the join probe but stopped in phase 3. Extending the same runner to 600
  seconds produced a valid paired run with 160 phase-4 joins, 400 copy traces,
  and 80,000 bounded RDP-word records per arm, with no crash/abort markers.
  Control used target `0xB90000` at `512x447`; wide used `0xB51E00` at
  `796x447`. Both copied rows 0-447 with the matching width. This rules out a
  wrong target identity or copy extent for this capture and weakens
  H-copy-layout. The dynamic opcode census is near-identical, so it does not
  yet name H-rdp-producer versus H-resolve-layout; no mitigation landed.

- s6189: the corrected 600-second paired run enabled both new probes and
  positively fired 682/570 joins, 400 copy traces, 12,000 command records, and
  target/native logs in control/wide. After normalizing reversed TEXRECT
  endpoints in the captured raw records, phase 4 had 1,868 central-overlapping
  TEXRECTs in control versus 2,165 wide (3,775/3,787 total); control source
  target was 512x447 at 0xB90000 and wide was 796x447 at 0xB51E00. The target
  logs showed no resolve-texture use and no dimension mismatch at the source
  boundary. This selects H-rdp-producer over H-resolve-layout for this capture:
  the wide-only central draw population is already present in submitted RDP
  commands. The exact game-side producer/writer is still unnamed. The live
  central flag had a reversed-endpoint diagnostic bug, fixed and compile-tested
  after the run; the result above is an offline normalization of the captured
  raw rectangles. No mitigation landed.

- s6190: added task serial, root display-list, guest PC, DPC window, and submit
  serial to each phase-4 command row. The paired 12 MB route positively fired
  425/522 joins, 535/477 copy rows, and 8,000 command rows per arm before the
  diagnostic hold was SIGKILLed. Central TEXRECTs came from the same guest PC
  `0x8000834C` and the same alternating two-root-DL pattern after relocation;
  each arm used one coherent DPC submission window. Wide tasks emitted about
  123-127 central TEXRECTs versus 61-65 in control. This rules out a hidden
  secondary CI/scissor pass and a distinct menu-writer/source-PC path for this
  capture, selecting the same-source RSP/width-dependent geometry path. The
  exact RSP input field remains unnamed; no mitigation landed.

- s6191: `[g1d-task]` at `rs64_run_lle_gfx` positively captured the phase-4 RSP
  task identity in both arms (control 912 rows, wide 591; each also had 160
  phase-4 joins and 400 copy rows). Both arms use type-1 tasks with identical
  `data_size=0`, `ucode=0x80024A10`, `ucode_data=0x80038D00`, and
  `ucode_data_size=0x800`; the two dominant root-DL addresses relocate by a
  constant `-0x3E200` in wide. Existing command attribution independently names
  guest PC `0x8000834C` in both arms. This selects H-width-input / same task
  identity and rules out a distinct wide task-builder identity for this capture;
  the exact width-bearing RSP input (root-DL bytes versus bootstrap/DMEM input)
  remains open. The oracle cannot reach this 1024-wide phase, so this is
  single-source runtime evidence with positive controls, not retail-grounded
  proof. The trace is env-gated by `ROGUESQ_LOG_G1D_TASK`.

- s6192: the paired input probe fired with the required controls (656/615
  phase-4 joins and 400 copy rows in control/wide). Post-DMA `ucode_data` was
  identical in both arms (`0xD91538FA`, 794 nonzero bytes). The
  callback-selected root-DL probe captured 26/29 unique roots; every sampled
  first 0x100-byte window was zero (`hash=0xE6A1D1C5`, `nz=0`) in both arms,
  while normalized root sequences included the known `-0x3E200` relocation.
  The initial task-wrapper sample was independently zero-filled, so it was
  rejected as a root witness and corrected in the same iteration. This closes
  root-DL bytes and ucode-data as the observed source of the extra central
  TEXRECT population and selects H-other-RDRAM: the width-bearing value is
  read from another RSP-visible RDRAM table. The oracle cannot reach this
  phase; no render mitigation landed.

- s6195: the complete main-ucode DMA-read witness fired in one paired build
  (12,288 control rows, 12,286 wide rows; 32/28 root rows and 400/400 copy
  rows). The first read, the common `mem=0x1DB0` bootstrap source, matched
  exactly. The first differing candidate is the `mem=0x170`, `len=0x10F`
  command-source DMA at root-relative offset zero: control hash `0x8D4703B3`
  versus wide `0x12499740`, with the same guest PC `0x80007904` and transfer
  shape. The previously matched root witness covered only its first 0x100
  bytes, so this selects the root-DL tail / dynamic command-source table as
  the first width-bearing RDRAM input (H-table), while leaving open whether
  those differing tail words are legitimate relocations or width-dependent
  command data. The new regeneration-safe `ROGUESQ_LOG_G1D_READS` witness
  records address, width, hash, nonzero count, task/root, guest PC, and DPC
  window. No rendering mitigation landed.

- s6196: that open question is closed for the node body. Paired controls were
  160 phase-4 joins and 400 copies per arm. Pointer words, including the
  RDP list at +0x108 (`E7/B9/B7/B6/BE/FA`), match after `0x3E200`. From +0x28
  wide is `0x00010001` (one `0x0001FFFF` at +0xDC) where control is zero,
  and +0x78..0xB4 replaces control's `05200002` block. `0x00010001` is not a
  pointer (its low address is identical static code). This selects H-command
  for the node body and refutes H-relocation / H-other for those words.
  Superseded: s6195's "first 0x100 bytes are zero". Believable because both
  arms' `[g1d-root]` samples hashed `0xE6A1D1C5` with `nz=0`, but that witness
  masks the root to 23 bits (`0x32D820`) and does not read the DMA at
  `0xB2D820` (`head_nz=69` vs `136`). Writer of `0x00010001` still unnamed.
  No rendering mitigation.

- s6197: 0x200-byte dump of the first two root nodes (`scratch/agent/soak_results/s6197/`). Control node 0 has `05200002` once at 0x78 (positive control). Wide node 0 (`0x80AEF620`) has zero hits at any byte offset and 81 words of `00010001` (runs `0x28..0xD8`, `0xE0..0x104`, `0x198..0x1FC`; `0001FFFF` at `0xDC`). 32 words match, 9 relocate by `0x3E200`, 6 other diffs sit in the preserved RDP list (`0x178` = width-1). This refutes H-shift in that window and selects H-fill. Control node 1's 0x78 block is different data, not `05200002`. Writer still unnamed. Superseded: "the fixed-point block might sit past the 0x10F DMA" — believable because that is the RSP transfer length and s6196 stopped there.

- s6198: scalar B/H/W/D stores do not create the command-node words. Paired 12 MB run `scratch/agent/soak_results/s6198e/` (160 phase-4 joins and root `0x003BD0` both arms; copies 400/320). Control node `0xB2D820` still has `05200002` at +0x78; wide node `0xAEF620` still has 81 `00010001` words from +0x28. An unevictable above-8 MB log was still open at the node dump (cap line after the dump) and recorded 0 changed words inside either 0x200 window. Uncapped `05200002` exact rows: 259, none in the node; the same hook did log a create at `0xA3DE48`. Dead end: s6198d credited `rs_memset` (`0x800078EC`) for 128 wide-node words because the byte store was scored on the word it left unchanged. Superseded: "the fill PC is a scalar store the parity hook can name" — believable because the bytes sit in RDRAM and SB/SH/SW/SD are the usual writers; s6198e is the before/after check those hooks needed. Next witness is a DMA destination or `do_swl`/`do_swr`, not another scalar hook. No rendering change.

- s6199: that block witness selects H-swl for the control word and H-host for the wide fill. `scratch/agent/soak_results/s6199/` and `s6199b/` each had 160 phase-4 joins and root `0x003BD0` in both arms. Control cover of node+0x78 is one `swl` at PC `0x8000D5A8` (phase 3, `00000000`->`05200002`, dest `0xB2D898`). Wide cover of node+0x28 is zero rows across PI, RSP, `zmemcpy`, and signature unaligned stores, including s6199b's short signature scan (521 rows, 0 on the node). The wide process's `0x8000D5A8` still writes `0xB2D898`, not the relocated node. No rendering change.

- s6200: the host writer is `Framebuffer::copyNativeToRAM`. Wide node+0x28 has 193 `rt64wb` covers and no other block kind. The last span is the shared 640x340 image at `0xA95C00` (`len=0x6A400`, end `0xB00000`); phase-2 `0xADD000` and phase-3 `0xA6A000` also cover it and are present in the 4:3 arm, whose node at `0xB2D820` is outside them. `wrap`/`unwrap` did not run. Node delta `0x3E200` equals one widened 448-line buffer. Do not drop the writeback.

- s6201: H-base selected. Paired 12 MB run `scratch/agent/soak_results/s6201/witness.txt` (screen unlocked; ctl pid 53957 ready 41 s, wide pid 54067 ready 40 s, both SIGKILL). Phase-4 `[g1d-task] data_ptr` equals `[g1d-alloc]` at PC `0x8000A9CC` in the same arm (ctl `0x80B2D820`, wide `0x80AEF620`); stride `0x108` and pool n=3 bytes `0x4AF58` / arg `0x4B000` match. Carve n=3 is the only difference: `t0` `0x70000` vs `0xAE200` (`(796-512)*448*2`), `d8 = top-t0`, pool = `d8-0x6B000`. Carves n=0..2 identical, still ending at `0xB00000`. Wide pool `[0xAE6E00,0xB31D58)` crosses that end; f0/f4 stay above it. Superseded: "the allocator returned a block `0x3E200` larger." Believable because the node moved by exactly the framebuffer growth. The chunk index inside the pool is unchanged (132 and 190). Do not raise `osMemSize` (the `a3!=0` images subtract a hardcoded `0x100000`, so the overlap is top-invariant) and do not skip the writeback.

- s6202: the opt-in `0x80001010` retarget refused to write. Paired 12 MB run, screen unlocked, ctl pid 54975 ready 41 s, wide pid 55078 ready 40 s, both SIGKILL, 0 crash. Control skipped (`outw=512`), kept `e8=0x80B25000`, `data_ptr=0x80B2D820`, task-time `w78=05200002`. Wide candidate `base=0x8096D600` `span_end=0x809B8600` (`ec-t2`; the prior `0x8096D800` figure is 0x200 high) lost to main-heap end `0x80B95BF0` head `0x80154690`, so `e8` stayed `0x80AE6E00` and task-time `w28=w78=00010001`. Superseded: "the span under `ec` is a free hole." Believable because it ends at `ec` and below the images that end at `0xB00000`. The same heap end is also above the working control pool `0x80B25000`, so this does not yet prove the candidate bytes are a live allocation. `r3` was not changed; `t0`/`d8`/`dc`/`f0`/`f4`/`f8`/`ec` match s6201. Next: classify the heap block covering each address. Do not pick a second address until that split is known.

- s6203: both addresses are one non-free block. Paired 12 MB run, screen unlocked, ctl pid 55929 ready 41 s, wide pid 56047 ready 40 s, both SIGKILL, 0 crash. `[g1d-hblk]` at the `0x80001010` store (no new store): head `0x80154690`, nblk=109, same=1, block `0x808B77F0` flags `0x0006` tag `0` size `0x2DB000` covers `0x80B25000` and `0x8096D600` in both arms. Span ends `0x80B92800`. Free bit is clear, so this is not the free hole. Control `w78=05200002` at `0x80B2D820`; wide `e8` stayed `0x80AE6E00`, `w28=w78=00010001`. Carve and pool n=3 match s6202. Selects H-early; refutes H-free and H-live. The walk stopped once both hits were in hand, so `last` is this block, not the s6202 heap end.
- s6204: that block does not survive to pool init. Same recipe, screen unlocked, ctl pid 57020 ready 40 s, wide pid 57122 ready 40 s, both SIGKILL, 0 crash. Carve-time `[g1d-hblk]` still matches s6203 (positive control). `[g1d-hblk-pool]` at `0x80018030` n=3: both arms `nblk=21 same=0`, `0x80B25000` hit=0, `0x8096D600` covered by `0x80195180` flags `0x0001` size `0x861660` (ctl) / `0x823460` (wide). Span end equals `ec-0x10` (`0x809F67F0` / `0x809B85F0`); size and `ec` both drop by `0x3E200` in the wide arm. Live pools `0x80B25000` and `0x80AE6E00` are above that stop. Refutes H-same and stated H-grow. Do not retarget `0x8096D600`: it is inside the free block, and the retail pool is above the terminator. Superseded: "a free flag on `ec-t2` would make that span the right pool base." Believable because s6202 rejected it only for lying under the carve-time heap end. The pool-time free flag is real and the placement is still wrong. Next: `ROGUESQ_LOG_RS_FREE` and `ROGUESQ_LOG_COALESCE_HEAP_ENTRY` between the two heap lines. No store.
- s6205: that replacement is `coalesceFreeHeapBlocks`, not `rs_free`. Paired 12 MB run, screen-lock key absent, ctl pid 57833 ready 40 s, wide pid 57943 ready 40 s, both SIGKILL, 0 crash. Positive controls match s6204 (`w78=05200002` at `0x80B2D820`; wide `e8=0x80AE6E00`, `w28=w78=00010001`). `[rs-free]` fired 6983/6899 times and 0 times in the window (caller_ra is 0, the known entry value). `[coalesce-entry]` fired 3 times (cap 256 not hit). The in-window row is `a0=0 a1=0 a2=0x80154690 a3=ec`. `a3` sits inside the old block. Size identity: `(0x809F6800-0x80195180-0x20)=0x861660` and `(0x809B8600-0x80195180-0x20)=0x823460`. The only caller is `runVideoFrameTick` `0x80001430`. Selects H-coalesce; refutes H-free. Superseded: "a0/a1 would be the covering pointers." Believable because the hypothesis named those two args, but on the return-0 path they are the mode and `a2`/`a3` are the heap bounds. Carve n=0/1/2 are identical across arms; their `d8` images end at `0xB00000`. The wide n=3 pool is what crosses them. No store.
- s6206: phase 4 reads that span as a texture, not as a color image. Paired 12 MB run, screen unlocked, ctl pid 58818 ready 41 s, wide pid 58929 ready 40 s, both SIGKILL, 0 crash. Witness `scratch/agent/soak_results/s6206/witness.txt` (raw logs deleted). Layout controls match s6205: ctl `data_ptr=0x80B2D820` `w78=05200002` `e8=0x80B25000`; wide `e8=0x80AE6E00` `data_ptr=0x80AEF620` `w28=w78=00010001`. `[g1d-img]` fired in both arms (`ci` 336/288). `ci_hit=0`. `last_ci` is `0xB90000` / `0xB51E00`. `ti_hit` is exactly 83 per submission (ctl, 9296 at subs=112) and 32 per submission (wide, 3072 at subs=96). `[g1d-wb]` n=1024 n4=0 in both; the printed rows are phase 2 and 3, including `0xADD000` len `0x23000` ending at `0xB00000`. The first 48 TI hits (the log cap) stay below the wide pool: ctl stride `0x1000` from `0xA6AA10` to `0xA99A10`, wide max `0xAE6B20`. Guest PC on those hits is `0x80007904`, and later summaries also show `0x8000834C`. Selects H-read. Refutes H-clobber and H-blind. Superseded: "phase 4 does not read the early images, so the overlap is only a stale copy." Believable because `ci_hit` is 0 and the phase-4 color target is the real framebuffer. The texture count is not 0. Do not drop the writeback.
- s6207: opt-in drop of the top-0x100000 images by 0x19200 (wide only; `apply_s6207_drop`) moved d8/dc and the phase-2/3 writebacks so they end at e8=0xAE6E00. The 16 logged wide w78 rows went from 00010001 to 00000000; none became 05200002. SetTextureImage prefix stayed 0xAE6120 (the s6206 prefix); ti_hit stayed 32/submission. ci_hit=0, last_ci=0xB51E00, n=3 e8 unchanged, 4:3 w78 stayed 05200002, 0 crash. Phase-4 dump fb_0001438_w796.ppm still has the white rectangle; the 4:3 dump does not. Selects H-still (the pointer is not d8 or dc). Refutes H-clear and H-broke. Superseded: "moving those images moves the texture pointer and clears the rectangle" — believable because phase 4 samples that image and its writeback filled the node. Side effect, title only: n=0/n=2 f8 and n=2 ec also shifted 0x19200. Do not skip the writeback.
- s6208: texture address is a 0x108 pool-chunk field, not `0x801163E8`/`F0`/`F4` and not root `data_ptr` (index 132). Paired 12 MB run, screen unlocked, ctl pid 61210 / wide pid 61319, ready 41/40 s, SIGKILL, 0 crash. Controls: ctl `w78=05200002` at `0x80B2D820` drop=0; wide `e8=0x80AE6E00` drop=0x19200 `w78=0`. `0x80A6AA10` at `0x80B29954` (index 71 +0x1C). `0x80AE6120` at `0x80AF08C4` (index 150 +0x14); other wide prefixes also +0x14. `ti_hit` 83 vs 32. `in_node` is blind (23-bit `root_dl`). Selects H-recompute. Refutes H-f0, H-node, H-miss. Superseded: "the pointer is `f0`/`f4`/`e8`" — believable because those globals stayed put when `d8`/`dc` moved; the RSP never DMAs that page for this word. Do not patch. s6209 dumped that window and selected H-two.

- s6209: one `[g1d-win]` per arm, 8 big-endian words before the first phase-4 prefix and 8 after. Screen unlocked. ctl pid 62100 ready 41 s, wide pid 62276 ready 40 s, both SIGKILL, 0 crash. Controls held: ctl `drop=0` `w78=05200002` `data_ptr=0x80B2D820` pool `0x80B25000`; wide `drop=0x19200` `e8=0x80AE6E00` `w78=0`. `ti_hit` still 83 and 32 per submission, `ci_hit=0`. Not H-moved. ctl `word_at=0x80B29954` `idx=71` `chunk_off=28` (0x1C), before `04C304C3,00000000,00000000,E6000000,00000000,F5100000,07080200,FD100000`, after `F3000000,077FF000,F5102000,00000000,F2000000,000FC07C,BA000E02,00000000`. wide `word_at=0x80AF08C4` `idx=150` `chunk_off=20` (0x14), before `80AF0DD8,B5000000,00000000,00000000,00000000,E6000000,00000000,FD100000`, after `E8000000,00000000,F5000100,07000000,F0000000,073FC000,BA000E02,00008000`. `chunk_off` in the log is decimal. Pool word at `0x801163E8` matched `[g1d-pool]` n=3. Chunk bytes `[0x00,0x10)` match; control then has `F5100000/07080200` (opcode 0xF5, G_SETTILE) and wide does not, so the shared `FD100000` G_SETTIMG opcode sits 8 bytes later in control. Immediate neighbors other than that opcode disagree (`07080200` vs `00000000`, `F3000000` vs `E8000000`). A later `BA000E02` matches at pointer+0x1C and does not make the windows the same. Selects H-two. Refutes H-shift and H-moved. Do not patch either slot. Superseded: "an 8-byte slide would reveal one shifted field." Believable because the offsets differ by 8. The bytes on either side of the pointer are not the same values.

- s6210: two `[g1d-win]` lines per arm, same 12 MB sequential recipe. Screen unlocked. ctl pid 63148 ready 40 s, wide pid 63297 ready 40 s, both SIGKILL, 0 crash. Controls held: ctl `drop=0` `w78=05200002` `data_ptr=0x80B2D820` `e8=0x80B25000`; wide `drop=0x19200` `e8=0x80AE6E00` `w78=0`. `ti_hit` 83 and 32 per submission, `ci_hit=0`. First windows unchanged (ctl idx 71 +0x1C `0x80B29954`=`0x80A6AA10`; wide idx 150 +0x14 `0x80AF08C4`=`0x80AE6120`). Second ctl window is the predicted sibling: `0x80B29A5C`=`0x80A6BA10` idx 72 chunk_off 28 (0x1C). Before/after match the first ctl window except the word at -0x20 (`04C304C3` vs `00000000`). Second wide window is `0x80AF0FFC`=`0x80AE5520` idx 157 chunk_off 20 (0x14), not idx 151 +0x14 (`0x80AF09CC`). The word matches; the chunk does not. Zero `[g1d-ptr]` word_at values fall in chunks 151..156 (that probe only records `[0xA6A000, 0xB00000)`). Selects H-other. Refutes H-template. Do not compare wide neighbors. Do not patch. Superseded: "the second wide texture word sits in the next chunk, index 151." Believable because control's second word is the next chunk and the next logged wide word is `0x80AE5520`. Its pool index is 157.

- s6211: phase 4 DMA-reads wide chunk 151. Paired 12 MB run, screen unlocked, ctl pid 64109 ready 36 s, wide pid 64248 ready 40 s, both SIGKILL, 0 crash. Witness `scratch/agent/soak_results/s6211/witness.txt`. Controls held: ctl `drop=0` `w78=05200002` at `data_ptr=0x80B2D820` `e8=0x80B25000`; wide `drop=0x19200` `e8=0x80AE6E00` `w78=0`. `ti_hit` 83 per submission (18592/224) and 32 per submission (5120/160). `ci_hit=0`. `[g1d-ch]` ctl idx 72 `dram=0x80B29A40` `ov=0x108` guest PC `0x80007904`, words end `FD100000,80A6BA10` at +0x1C (the s6210 sibling; positive control). Wide idx 151 `dram=0x80AF09B8` `ov=0x108` same PC, words `00000000,00000000,E6000000,00000000,FD100000,80AE5F20,E8000000,00000000`. `0x80AE5F20` is at +0x14. It is not on the s6208 exact list and not on the `0x1000` stride from `0xA6AA10`. `[g1d-img-hit] kind=ti addr=0xAE5F20 w0=0xFD100000` (also `0xAE5D20`). Selects H-read-tex. Refutes H-unread. The idx 156 line is only `ov=0x8` (a tail); do not treat its first 8 words as DMA-read. The idx 152 line is the 7-byte tail of the chunk-151 DMA; the cap of 4 stopped a full chunk-152 line. Logged TI hits (cap 48, 23 distinct) run `0xAE4920`..`0xAE6B20` by `0x200` and none sit at or above pool `0xAE6E00`. Superseded: "chunks 151..156 may be unread because no `[g1d-ptr]` word_at falls there." Believable because that probe keeps only the exact prefixes plus a `0x1000` stride, and `0xAE5F20` fails both while still lying in `[0xA6A000, 0xB00000)`. Do not patch.

- s6214 (single-source, one paired run): wide pointers 0xAE5F20/0xAE6B20 stay at the `00010001` fill through every wb (last covering wb phase 3 n=41) and hold real texels (`00010845 008300C5 ...`) by TI hit 1, unchanged at hit 2; ctl 0xA6AA10 is a flat fill at hit 1. So the texels are written after phase-3 wb and before phase-4 TI hit 1, by a writer not yet named (H-fresh). Next: name that writer via a guest-PC-attributed write watch / lldb hw watchpoint on 0xAE5F20.

- s6212: the uncapped phase-4 TI set does not cross the pool. Wide `[g1d-ti] n=23 min=0xA6A010 max=0xAE6B20 above=0 ov=0 abcap=0 pool=0x80AE6E00 saw=0xAE5F20` (6144 hits, 32/submission). `0xAE6B20` is `0x2E0` below `0xAE6E00`; `0xAE6D20` and `0xAE6F20` are absent. The same 23 addresses are the entire 48-line hit log: 18-address `0x200` ladder `0xAE4920`..`0xAE6B20` (`FD100000`) plus `0xA6A010` (`FD500000`) and four `FD180000` addresses `0xA6A810`..`0xA6D810`. Control `[g1d-ti] n=75 min=0xA6AA10 max=0xAABA10 above=0 pool=0x80B25000 saw=0xA6AA10`, `w78=05200002` at `0x80B2D820`, chunk 72 `ov=0x108`. Its first 48 hits are a `0x1000` stride `0xA6AA10`..`0xA99A10`; the other 27 are not in that prefix. Logged phase-3 writeback `0xA50E00`..`0xAE6E00` covers all 23 wide starts (sampled log, not a full writeback census). Selects H-stop. Superseded: "the 48-line cap hides a ladder step inside the pool" — believable because s6211 stopped at 48 lines while `ti_hit` was 5120. Do not patch. Next is the byte dump at those pointers.

- s6217: `ROGUESQ_G1D_DROP_EXTRA=0x25000` (wide arm) moves wb/memset end from 0xAE6E00 to 0xAC1E00, off the HUD TLUT gap; no crash. HUD render correctness unverified. Next: capture framebuffer in both arms; if HUD correct make the extra (t0-0x70000 total) the default for wide.
- s6218: HUD screenshots of both arms occluded at bottom-right (inconclusive); recapture with window-id screencapture (NEXT.md).
- s6219: window-id capture works (`scratch/agent/winid.js`). Wide ctl and DROP_EXTRA=0x25000 arms show identical sane HUD (lives, wingman, radar; radar clipped at right edge = HUD not edge-anchored yet), but neither shows the ammo readout, so the alias verdict is untested on its only consumer. s6220 (offline, single-source): buildHudAmmoReadout is a MENU-overlay function called unconditionally from a menu-screen setup (ROM caller 0x11BC64); flight cannot show it, so the s6219 premise is superseded (believable: name says HUD/ammo). The alias test must capture the hangar/ship-select screen in both wide arms (NEXT.md).
