# Rogue Squadron 64 Recomp — current truth

Compact operational handoff, maintained as of Session 6113 (2026-10-24).
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
