# Rogue Squadron 64 Recomp — current truth

Compact operational handoff, maintained as of Session 6188 (2026-10-25).
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

1. **G1d widescreen (active, `scratch/agent/NEXT.md`).** Aspect lever proven: `ROGUESQ_ASPECT_SCALE=k`
   (guPerspective aspect in setupCameraMatrices) scales rigid-object width ~1/k (s6108).
   Flight RDP census (s6110, `tools/rdpbin_scissor.py`): colour image 512 wide, scissor 512x448
   (+4-unit twin), secondary passes 640. A real widening must change colour-image width, scissor,
   viewport and VI width together under `ROGUESQ_ASPECT=16:9`. s6112: `ROGUESQ_VPW_SCALE=k` (+ASPECT_SCALE=k) widens the camera viewport (320x224 virtual rect -> 426) undistorted, but output is still a 512 image so the right side is cropped: remaining = scissor/colour-image/VI width + HUD x; scissor writer lead is
   setupCameraMatrices (0x80017xxx, halfword globals x float @0x800007A4); VI table
   `selectAndApplyViMode` (0x80128D50, 0x50-byte OSViMode entries), `osViSetMode_recomp`
   (upstream_compat.cpp:621). s6119-s6120: black 683 window was RT64 width allowlists (fixed, env-exact-match); window screenshots now show the undistorted 683 frame on L1. Remaining: bundle VPW/ASPECT_SCALE/FB_WIDTH behind `ROGUESQ_ASPECT=auto|4:3|16:9|21:9`, menus/hangar at 683, HUD x anchoring, 21:9.
   s6151: pc-range marks: digit text = 800c1000-1b60; ally icon + radar disc unmoved by ANY store range s6149-s6151 -> stop chasing stores, anchor at the consumer (reader of the 0x80340240 element table). s6149: marking only blocks 6/7 2nd stores moves the ring only (disc/counter/ally unmoved) - H-layout refuted for disc/counter; next label blocks 0x264-0x354 by pc range. s6147: flight HUD element table = 0x30-byte blocks, x at +0x24 (addr&0xF==4), y at +0x28; `ROGUESQ_HUD_MARKCLS=x|y` + MARKPC moves ally icon/ring in x, y-arm removes ring/ally/missile counter; radar disc and missile counter x not covered yet. s6148 (offline census of s6146b log): the 8 blocks (0x80340240+0x30n) are each stored twice in initHudStruct (4:3 value, then ~1.6x value that stays live), so the s6147 mark most likely hit the overwritten first store for the disc/counter (blocks 6/7; single-source). Next: mark the second store per x coordinate, confirm blocks 6/7 move, then ROGUESQ_HUD_ANCHOR; if not, census per-frame writers outside initHudStruct. s6150 (3-arm pc-range bisect, single-source, eyeballed fb frame): initHudStruct pcs 0b58-0d5c = counter SHIELD icon x (digit text is a separate writer; a hidden green circle reticle also appeared); 0738-083c and 098c-0ac4 move nothing visible. Ally icon + disc x still unlabelled: next bisect 0568-0738, 0ac4-0b58, 0d5c-1B60 (NEXT.md); fallback = anchor at the consumer of the 0x80340240 table. Superseded: s6149's expectation that the disc/counter x live in 0738-0d5c as one group - believable because the s6149 census put them in those blocks, but only 0b58-0d5c moved anything.
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

## G1d widescreen state (s6113)
Levers proven: ROGUESQ_VPW_SCALE (camera rect), ROGUESQ_ASPECT_SCALE (guPerspective aspect), ROGUESQ_FB_WIDTH (video-state a0 -> scissor + SETCOLORIMAGE width; plus osViSetMode width/xScale rewrite). Scissor does NOT follow the camera rect. Blocker: flight fbs at 0x80620000/0x80790000 overflow the 8 MB RDRAM top at width 683 (readback garbage). Next: relocate/verify buffers, then VI hstart/hend span + HUD x anchoring. Default behaviour unchanged (all opt-in).

## G1d update (s6114)
Widened-fb garbage = the two flight flip buffers (0x80620000/0x80690000) sit only 0x70000 apart (512x448x2), so 683-wide frames overlap each other. s6113's "0x80790000 overflow" was the hangar buffer. Fbs are carved top-down from osMemSize by the layout fn at 0x80000E00 (config struct 0x8010FCB0+0x2C..0x38 = region sizes); ROGUESQ_OSMEM_MB (4..8) shifts them; >8 MB aborts RT64 (8 MB rdram cap). Next: find/enlarge the fb size field under ROGUESQ_FB_WIDTH, then screenshot, VI hstart/hend, HUD x.

## G1d update (s6115)
fb size = partitionFramebufferMemory a2*a3*2; patched under ROGUESQ_FB_WIDTH (tools/apply_s6031_far.py applypfm). Flip buffers no longer overlap (spacing 0x95680) but 683 dumps remain garbage (control without width flag is valid). Next: compare SETCOLORIMAGE width vs RT64/VI width at present for a 683 frame; find any other hardcoded 512 stride. Window screenshots need the game window frontmost (not yet).

## G1d update (s6116)
Activated-window screenshots work (osascript frontmost + screencapture; ctl valid). w683 window is black; RDP draws 683-wide colour image at 0x8076A980 while VI shows pfm-moved buffers 0x8066A980/0x805D5300 and stalls. Next: find who sets colour-image addr 0x8076A980 (second fb pointer not covered by partitionFramebufferMemory patch).

## G1d update (s6117)
s6116's "second colour-image pointer" is REFUTED: 0x8076A980 is region 0x801163E4 (top-fbsize) = the intermediate render target; ctl has the identical role split (0x80790000 intermediate + two flips). Fixed: VI field-origin offset (mode +0x28/+0x3C, hardcoded 1024/2048) now scaled under ROGUESQ_FB_WIDTH -> VI fb alternates. Still black: flips receive no final image. Next: parse the w683 rdp.bin for the copy stage from 0x8076A980 into the flips (SETTEXTUREIMAGE/SETTILE line/TEXRECT with 512-based stride) and compare with ctl.


## G1d state (s6118)
Widened (ROGUESQ_FB_WIDTH=683) RDP stream is width-consistent with retail (scissors, tile lines, no copy stage; flips are drawn directly). Black window therefore lies downstream: RT64 VI/present path. Check VI_WIDTH_REG, xScale, hStart/vStart in the mode table (upstream_compat.cpp ~626: comRegs width/xScale at +0x04..; s6117 already scaled fldRegs origin).


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
