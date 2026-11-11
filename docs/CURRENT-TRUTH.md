# Rogue Squadron 64 Recomp — current truth

Compact operational handoff, as of Session 7147 (2026-11-11).
`PORTING-STATE.md` is the chronological ledger; durable and migrated material lives in
`docs/PROJECT-OVERVIEW.md`. The full pre-compaction text of this file (s6893-s6993 headline
bullets with every number, superseded list, G1e chronology) is archived verbatim in
PROJECT-OVERVIEW "Migrated from CURRENT-TRUTH (s6994 maintenance)" — grep there for any sNNNN.

## Headline

**s7125 G3 owner-recipe fidelity (L6 dd4 16:9 FPS60): RT64 == angrylion to the retail floor (H-equal).** Once the G5B_FRAME recorder runs after the radar-disc shift walker (rs64_region_scan, s6158), the score is frac>40 median 0.010, mean|d| 1.85, 7/713 frames over 0.02, against 0.010 / 1.62 at retail settings. The recorder fix is in src/rsp/dpc_bridge.cpp (ROGUESQ_G5B_FRAME_EARLY=1 restores the old point). Before it, every wide capture showed a ~1000 px HUD diff, and s7098's 'HUD anchor applied in RT64' was this. The remaining large diffs are guard-band sky sheets: the hardware paints them as flat beige wedges, and the deliberate ROGUESQ_W_SHEET_PX cull drops them, so RT64 shows sky. A same-run W_SHEET_ALT=0 toggle confirms it: with the cull off, RT64 draws them as dark bands. Sheets: docs/owner_sheet_s7125_*.png; tools/s7125_arm.zsh, capture rect 0,9,369,216 for the 1360x796 window.
- In plain words: at the owner's settings the renderer draws the same picture as an accurate N64 model. The only big differences are bogus sky sheets the port removes on purpose.
- **s7127-s7130 W_SHEET escape: CLOSED.** Escaper = all-W-positive hairline wedge from a guard-band corner ((-199,-112), (-398,-224), (994.8,-112), (1193.8,-224) at 16:9). Default-on ROGUESQ_W_SHEET_POS (rt64_gbi_rdp.cpp; =0 restores, =t drops in odd 24 MHz seconds only) drops long, all-W>0, W-ratio < 1/64 tris with a corner vertex and a <= 8 px base. ROGUESQ_G5B_FRAME_TRIG=<pre>,<post> (dpc_bridge.cpp) writes a swap ring only around a detection.
- Pixel check: kept arm t1 5 fires invisible on RT64 and angrylion (|d| 0.3-1.3 = control; painted-line control 6-11); dropped arm p3 5 fires, line-minus-control |d| median -0.1 (H-fixed, RT64 == hardware where dropped); p1/p2/p4 0 fires (corner-free control fired 6/2/10). Rate ~0-5 per 300 s. Owner sheet docs/owner_sheet_s7129_wsheet_cull.png (tools/s7129_sheet.py).

**s7142 G3 hangar 21:9/16:9: RT64 drew 2D texrects 1.33x wide, FIXED (default on, ROGUESQ_RECT_ASPECT=0 restores).** RT64 scales Rectangle/fill draws by source/target when the scissor matches the VI fb ratio (hangar fb 1024x336 vs target 1024:448; 796x336 vs 16:9). LLE triangles never get it, so menu text came out wider than the stream. Same-build arms: 21:9 centre frac>40 0.074->0.051, text boxes 0.334->0.213; 16:9 0.082->0.056, 0.335->0.206, frames >0.05 497->135. Sheet docs/owner_sheet_s7142_rect_aspect.png.
- In plain words: hangar and menu titles at 16:9 and 21:9 are now drawn the width the game asks for. They had been stretched about a third wider than the ships around them.

**s7132-s7136 21:9/16:9 owner recipe L6: hole classes all closed.** s7133 split x (ROGUESQ_HORIZON_XFIX), s7135 60 deg pitch gate (ROGUESQ_HORIZON_GATEFIX), s7136 sky corner (ROGUESQ_HORIZON_SKYFILL; all default on, no-op at 4:3, =0 retail). s7136: in banked dives the wide corner looks above the opaque sky band's top (~+17 deg; the 4:3 corner stays inside), where the art expects the clear colour (band top fades to A89880 = the ACE1 fill). The clear now covers the whole viewport under ASPECT: hole swaps 21:9 11 -> 0, 16:9 9 -> 0, RT64 window agrees. Sheets docs/owner_sheet_s7136_sky_fill*.png. The corner shows flat haze beige; that is retail on L6 (s7138: the top-fade skirt height is level config +0x2C, 0 on L6 only, so the skirt is zero-area and emits nothing; L1 skirt draws). Item 29.

**s7120-s7123:** NEARLIFT k1.6 replicated vs retail camera same run (steady wall losses 42/2 over 4 runs, z -6.0; H-smooth; s7121: the 2-16 u camera steps were a 3-camera log join, flight cam 80138458 has 0 steps; use `s7119_hop.py --cam 80138458`). s7122: L1 flight RT64 == angrylion (572 frames, mean|d| 7.8, edges + speckle; tools/s7122_fidelity.py, s7122_sheet.py); CULL_SPIKE costs nothing. s7123: the 4:3 pillarbox is centred (SCK pads the right; tools/s7123_present_rect.py); its narrowness = owner-closed VI_SHAPE.


**s7098 G5b: the big in-flight terrain drops RT64 presents are already in the RDP stream (H-stream, two lines); they are a near-wall flicker that follows FPS60, not draw distance (single-run arms).** One L6 dd4 16:9 owner-recipe run captured the forwarded stream (ROGUESQ_G5B_FRAME, RAM every 20 swaps) and the presented window (g5b_capture) together. angrylion needs a 16 MB core for dd>1 (stock RDRAM_MAX_SIZE 8 MB overflows rdram_hidden[] on cimg 0x98AA00; tools/angrylion_replay/build16.sh). (1) 316 own-RAM flight swaps, angrylion vs presented (tools/s7098_rt64_vs_al.py, lag 15 ms): floor 0.043, 1/316 over threshold, KILL_AREA=3000 control 16/16 flagged. (2) All 70 g5b_drops transients, candidate swaps within 100 ms replayed (tools/s7098_transients.py): 53 are matched by a swap's hardware render. The 10 large ones (T 0.12-0.71) the scorer called RT64-only look identical to their angrylion render by eye (scratch/s7098/rt64_a.png, rt64_b.png; the gap is a HUD-position offset only). Every large event is the near canyon wall missing for 1-3 frames while the camera hugs or enters it, sky showing through. Arms on L6 (tools/s7098_wall_flicker.py, episodes per run): dd4 FPS60 6 and 4; CULL_SPIKE=tog splits 1 on / 3 off episodes (cull refuted); dd4 FPS60=0 gives 0 in 130 s of wall-hug; dd1 FPS60 gives 2 (same picture: the camera alternates inside and outside the wall).
- In plain words: the renderer draws exactly what it is given. The missing-wall flashes come from the game side, and they only appear with the 60 fps mode on, at any draw distance.
- Caveat: the owner said dd1 was clean, so this FPS60 near-wall class may not be the owner's dd-dependent drop. Nothing here explains a dd-only drop.
- Next: FPS60 camera vs terrain collision on render-only frames (NEXT.md, slug fps60-wall-camera).

**s7096 DPC bridge forwarding coverage CLOSED: RT64 receives exactly the hardware-consumed RDP byte stream (H-fwd-exact, two lines).** src/rsp/s7096_fwd_cover.cpp (ROGUESQ_S7096_FWD=1|ctl; hooks in RSP_DPC_START/END, rs64_rt_submit site ids, every deliberate drop path, rs64_dpc_record_submit pre-compare). L6 flight, 3 runs: dd1 4:3 2.82 GB, dd4 16:9 15.07 / 16.60 GB, HW == FWD with 0 missing / dup / out-of-order / foreign, 0 drop paths fired; self-test 8/8, ctl mutant flagged 64/64 tasks. Content: dd1 0; dd4 ~18 B/task differ at the handoff, but 0 differ just before record_submit (pre_bytes == fwd), so every change is one of our own edit walkers (0x2D = g1d title_clear scissor clamp; bulk = triangle words, attribution single-source). No late writer, so the bridge is not a G5b terrain-drop source.
- In plain words: every drawing command the graphics microcode produces reaches the renderer exactly once and in order. The only bytes that change on the way are our own deliberate fixes.
- Next: name each edit walker's byte changes (NEXT.md, slug bridge-edit-census).

**s7082-s7087 N64Recomp lowering censuses CLOSED** (every mnemonic maps to a census tool; table docs/N64RECOMP-WARNING-CENSUS.md; full text in PROJECT-OVERVIEW "Migrated from CURRENT-TRUTH (s7134)"). Rerun the census tools after any regen.


**s7081 N64Recomp self-branch miscompile FIXED (tools/fixup_selfbranch.py, default on, `ROGUESQ_SELFBRANCH_FIX=0` = old path): the 16 backward out-of-function branches in the 4 voice resampler helpers now store the caller-tail target and return; the caller dispatches to a label at that target (retail: finished one-shot sample -> store last word, zero-fill, caller epilogue).** Differential test tools/s7081_selfbranch_test/run_test.py runs the generated C against an independent MIPS interpreter executing the retail ELF bytes: fix arm 2400/2400 exit+loop cases match (all 16 targets hit), old arm crashes on every case whose exit fires (it rereads samples from address 0), loop-path controls match in both arms. Live funcs_24.c byte-equal to the tested file; preempt 6; L6 boot to flight 309 s clean, 0 exits fired (block dead in play, s6878). The 2 data_gap_* out-of-function gotos are decoded data, left alone.

**s7072 menu "Debris" cell-mesh family renamed: it is the menu JPEG (JFIF) decoder, not a glyph mesh.** Evidence from the bodies: callers are parseJfifDHTMarker / resetJfifDecodeState / loadJfifAsset; a bit reader with 0xFF stuffing and 0xFFD9 EOI detection; a Huffman size table from 16 counts capped at 256; libjpeg's 0x580-byte range-limit table plus a >>3 (5-bit) copy; four 256-entry YCbCr->RGB tables using 1.402/1.772/0.71414/0.34414 (all in the ELF); a float IDCT. 11 renames (scratch/s7072/renames.tsv) applied to the live tree, menu_overlay.txt, syms toml and fixup_preempt_point.py. Control: the preempt fixup reports 6 functions / 9 tag lines before and after. Rebuild plus an L6 boot to flight: renamed symbols in 3/113 host samples, 0 crash. The format-message callers (rasterizeFormatMessageGlyphs, tickFormatMessageWorker) drive this decoder, so their names are suspect too (NEXT.md).

**s7070 gfx-hash-audit CLOSED (no build, tools/s7070_parents.py over the s7069 on/off dumps, two sets agree): Gfx-thread XXH3_hashLong (7.3%) and memmove (8.1%) are RT64 framebuffer RAM tracking/writeback (checkRAM, hashTracking, storeRAM, copyNativeToRAM, updateScreen: ~77% of hash, ~60% of memmove), texture hashing ~11%, no rs64 caller.** ~0.22 ms/frame total, 60 fps held: not a lever.

**s7069 host-selftime-audit CLOSED: the 2033 generated rs64_m5_lowfield_store / rs64_s4307_synth_read call sites test a flag inline (tools/apply_s7069_callsite_gate.py, same-name macro after the decl, call lines untouched; `ROGUESQ_DIAG_CALLSITE=0` = old path).** Same build, L6 dd1 4:3 FPS60 268 s each, 0 crash/stall: [Game] 0 hook samples 0/0 vs 71/60 control; the bigger win was skipped argument evaluation (two s5228 lowfield sites call getenv per store): getenv 597 -> 15, [Game] 0 on-CPU self 4625 -> 3591. Single run per arm.

**s7068 diag call-site gates (`ROGUESQ_DIAG_GATE=0` = old path): per-RDP-command e9 boundary/provenance calls (rt64_interpreter.cpp), the per-gfx-task 4 KB ucode FNV (rs64_e9prov_task_begin) and the many-gate store/load hooks (rs64_m5_lowfield_store, rs64_s4307_synth_read) now early-out unless their logs are on.** Same build, L6 dd1 4:3 FPS60, 268 s flights each, 0 crash/stall: Gfx diag self 665 vs 1066 samples (BoundaryCommand 0/115, authoritative_span 0/74, task_begin 3/55), [Game] 0 diag 285 vs 450 (synth_read 70/127, lowfield 42/127; residual = generated call entry). ~0.3% of a core; no fps claim. dpc_record_submit_impl/spike_scan are functional, left.

**s7067 host self-time audit (tools/s7067_selftime.py, s7066 dumps): our diagnostics are 6-10% of MAIN / Gfx / [Game] 0 on-CPU self time but only ~0.7% of one core (game threads are ~2% busy, Gfx ~8%).** Top single leftover was a per-call dladdr in osViSetMode_recomp's log line (8.6% of [Game] 0 self). Now cached per return address (`ROGUESQ_DLADDR_CACHE=0` = old path): same build, 268 s L6 flights, 0 crash/stall: 3.7 vs 67 us per call, dladdr samples 1 vs 312. Positive control: __findenv_locked 447 -> 0 across the s7066 arms in the same tool. No fps claim.

**s7066 hot-getenv class CLOSED: one cached getenv for the whole image (src/main/rs64_env_cache.cpp, default on, `ROGUESQ_ENV_CACHE=0` = libSystem path).** Census (tools/s7066_getenv_census.py): 2265 generated getenv sites (110 per-call) + 1031 host sites (529 per-call by heuristic) + lib/ ultramodern/RT64, too many to patch singly, so the executable now defines getenv/setenv/unsetenv/putenv: ROGUESQ_* names are served from a lock-free per-name table (no environ lock), any setenv through the image invalidates it, other names pass through; dylibs (SDL) keep libSystem's. Two runs, s7065 recipe L6 dd1 4:3 FPS60, host-sampled (tools/s7066_getenv_samples.py): on = 0 libSystem getenv samples (99 cheap cached lookups) vs off (positive control) 776 (MAIN 456), s7065 baseline 583; both 365 s flight, 0 crash, 0 VI stall, fps 58.9 / 59.0 (cross-run; the cost was ~0.25% of MAIN, so no fps gain is claimed). Policy setenv values still seen ([s7037] lines / auto bundle unaffected: setenv invalidates).

**s7065 transition stalls CLOSED as retail feel (H-vispin, audio-time form).** Host blocked-stack samples (tools/s7065_sample_loop.zsh + tools/s7065_sample_yields.py, no build; L6 dd1 4:3 FPS60, 366 s, 0 crash): in all 7 sampled gaps the game thread's OS-silent stretch is `runVideoFrameTick -> musyxNoopStub -> waitForMusyXAudioTaskDone` yielding 113-138 ms (normal seconds: 99% osRecvMesg waits). Code: its countdown 0x8014998A = 16 mix chunks of 192 samples = 3072 samples at 22047 Hz = 139 ms = 8.37 VI, matching s7064's 8/9-VI quantization. Gap = 139 ms fixed wait + 25-66 ms slot drain + occasional ~70 ms shutdownMusyXVoices. H-compute, H-tokenwait refuted. Retail timing inferred from code (oracle cannot reach these scenes).

**s7063 21:9 dd6 auto survey CLOSED: all 19 levels hold ~60 fps in flight with 0 crashes (H-ok).** Last two holds on the s7062 build (queued soaks s7062_219auto_L10/_L15, 363-364 s flight each, alive, 0 crash lines, 0 VI stalls): L10 60.00 fps, L15 59.99 excl. gaps, P(>=2VI) 0.00, no RSP-bound slow frames (tools/s7060_survey_table.py --suf g). Per level, fps excl. gaps (s7058-s7062 rings): L0 59.61, L2 59.58, L3 59.60, L6 59.80, L7 59.92, L8 59.98, L9 60.00 (with auto 9:8192, s7062), L10 60.00, L11 59.93, L14 59.92, L15 59.99, L16 59.48 (transition stalls = loads, 59.68 excl. >40 ms), L17 59.70, L18 60.00; L1-L5/L12/L13 measured s7050-s7058 (L12/L13 need auto K=0.5). Older headline bullets s7006-s7045 moved to PROJECT-OVERVIEW "Migrated from CURRENT-TRUTH (s7063)".

**s7062 21:9 dd6 auto bundle now caps L9 at 8192 cells (`ROGUESQ_DD_WIDEWIN_CAPLEVEL=9:8192` auto when FB_WIDTH>796 and no explicit _CAP; explicit _CAPLEVEL wins, `=-` off).** Frozen poses L9 21:9 (6 poses, 2 runs for c8192): c8192 vs c10240 0.00 at every pose, control c6144 1.18/0.99/0.25 at k0-k2 (same run). Confirm hold on the new build: 368 s, 0 crash, [s7037] caplevel=9:8192 (auto), L9 60.00 fps, P(>=2VI) 0.00, 5 slow frames (s7058 auto at 10240: 58.50, 469 slow frames; cross-run, supporting only). L10/L15 21:9 dd6 holds queued (s7062_219auto_*), the last levels without a survey row.

**s7061 L9 21:9 dense-burst dip: WIDEWIN cap 8192 holds ~60 fps where 10240 dips (H-8192-holds, 2 runs); new opt-in `ROGUESQ_DD_WIDEWIN_CAPLEVEL=<lvl>:<cells>[,...]` (+`_CAPLEVEL_TOG=1` same-run on/off/on), NOT auto yet (edge unqualified).** Run 1 explicit tog3 CAP 8192/10240/8192, 505 s, 0 crash: control rsp p1-p0 +0.56 (A/A -0.00); burst 270-370 s 59.8/58.3/59.5 fps, P(>=2VI) 0/0.03/0.01; 450-545 s 59.9/59.0/59.5. Run 2 via the new knob (CAP 10240 + CAPLEVEL=9:8192 TOG), 505 s, 0 crash: rsp p1-p0 +0.52 (knob = explicit cap), burst 270-390 s 60.0/58.2/60.0 (333 ms shift 60.0/59.2/59.2). Survey L17 59.70 / L18 60.00 excl. gaps: OK. Next: frozen poses c10240/c8192/c6144 on L9, then fold `9:8192` into the 21:9 auto bundle if invisible.

**s7060 21:9 dd6 auto survey L8/L9/L14/L16 (H-laggard on L9, but NOT a K lever; no game build).** New tools/s7060_survey_table.py scores every scratch/s7058 ring in one table (reproduces s7059 L0 59.61 / L6 59.80) and flags RSP-bound >=2-VI frames, not just mean rsp. L8 59.98 / L14 59.92 fps excl. gaps: OK. L16 59.48 excl. (59.68 excl. >40 ms): the same paired transition stalls as L6/L7 (25 gaps, rsp 0, inits 8), slow-frame rsp 11.4: not K. L9 58.45, 0 transition gaps, 469 slow frames with rsp 16.9 in a 40 s burst (55.4 fps there). Same-run K tog 0.5/0.6/0.5 on L9 (KLEVEL=9:0.5, 505 s): rsp -0.6 ms (shifted A/A 0.4), fps 59.1 in all phases and 52.1/53.0/49.9 inside the burst: K refuted. Same-run cell-cap tog 4096/10240/4096: rsp +2.15 / run +1.12 ms at 10240 (A/A -0.15), and in the 270-370 s burst window 60.0 / 58.7 / 60.0 fps, P(>=2VI) 0/0.02/0: L9's dip is the dd6 window's extra cells in its densest stretch (H-dd-window). Single run with a mild burst (bursts vary with combat; godrefills 17-20). Next: same-run cap 8192/10240/8192 on L9, then a level-scoped cap. L17/L18 still queued.

**s7059:** L0/L6/L7/L11 ~60 fps in flight; the 200-320 ms gaps on L6/L7/L16/L17 are scene-transition stalls (menuOverlayInit/endMissionCleanup/cinematicLoopBody, mostly anyAudioSlotActive polling, xctrace single-source), identical at dd1 4:3: loads, outside G5c's bar.

**s7058 21:9 L2/L3 need no level K (H-done, no build).** Same-run tog K0.5/0.6/0.5, 21:9 dd6 bundle, 507 s each, 0 crash/stall: L2 59.5/59.6/59.7 fps, rsp 10.40/10.93/10.42; L3 59.6/59.5/59.7, rsp 9.79/10.61/9.80 (A/A rsp 0.02). K0.5 saves 0.5-0.8 ms rsp but both levels already sit at the 60 fps ceiling, so auto KLEVEL stays `12:0.5,13:0.5`. 21:9 measured: L1-L5, L12, L13; the other 10 levels (not L10 cloud, L15 owner-gated) are queued as auto-path soaks (s7058_219auto_L*).

**s7057 dd6 21:9 bundle uses K=0.5 on L12 and L13 (ROGUESQ_DD_OFFMAPCULL_KLEVEL, auto `12:0.5,13:0.5` when FB_WIDTH>796 and no explicit _K; level from gCurrentLevel 0x80130B70).** L13 same-run tog 0.5/0.6/0.5 at 21:9, 509 s, 0 crash: 59.4/58.5/59.4 fps, rsp 11.83/13.06/11.75, P(>=2VI) 0.01/0.03/0.01 (A/A p2-p0 0.0 fps). L13 frozen poses (k0-k3): K0.5 0 px with dLum>8 vs K0.6, K0.3 control 3/9/64 px (0.07/0.18/0.29) fires; single-source (one run, dark level). L12 (s7056): 59.6/59.0/59.5. L4 keeps 0.6 (s7051 band). `KLEVEL=-` disables.

**s7055 21:9 L12 WIDEWIN cap 12288 is a small cost, not a cliff (no build, no default change).** Same-run tog3 holds, 2x506 s, 0 crash/stall: 12288 vs 10240 rsp +0.11..+0.18, guest run +0.45..+0.48 ms (all 4 comparisons), fps +0.2/-0.3 (A) -0.9/-0.5 (B), P(>=2VI) +0..0.02; control ring_sum/f +30%. L12 21:9 bundle sits at 54-55 fps (P 0.09-0.11) whatever the cap: next lever is a level-scoped K=0.5 (s7050: L12 +0.8 fps, poses 0.00) that leaves L4 at 0.6 (s7051).

**s7054 21:9 L4 WIDEWIN cap 12288 (POOLX_MAX=6) is ~free (H-free, no build, no default change).** Same-run tog3 holds, 2x508 s flight, alive, 0 crash/stall, xor8 ~22.6k frames: run A 10240/12288/10240 58.7/59.5/59.5 fps, rsp 9.83/10.08/10.07; run B 12288/10240/12288 59.4/59.3/58.7, rsp 11.39/11.16/11.43. 12288 vs 10240 rsp +0.25/+0.23 (A) +0.23/+0.27 (B), fps inside the A/A spread (0.7-0.8), P(>=2VI) <=0.02. Positive control: [s7031] ring_sum/f 5700-5850 vs 4120-4370 (+35% cells walked), +1350-1400 ocull/f, so the off-map cull eats most of the extra cells. OWNER-OPT-INS 12288 line now carries the cost. 21:9 cap thread closed: 12288 offered as opt-in, default 10240 unchanged (owner-gated).

**s7053 21:9 L4: the default WIDEWIN cap 10240 still binds a little (H-more-small, no build, no default change).** Frozen poses, arms c10240 / c12288 (POOLX_MAX=6) / c9216 ctl, 3 runs 0 crash: c12288 0.08-0.17 (0.1-0.2% px) in the same far-left shoreline band, ctl c9216 0.26-0.39 (replicates s7052); column scan: far water top rises 2-5 rows at 12288, falls 8-12 at 9216. Sheet docs/owner_sheet_s7053_l4_219_cap12288.jpg, OWNER-OPT-INS line added. Open: 12288 cost on L4 21:9 (NEXT.md).

**s7052 21:9 L12 cost thread CLOSED (H-visible, no build, no default change): WIDEWIN cap 9216 is visible on L4 at 21:9.** Frozen poses 21:9 FPS60 dd6 bundle (K0.6 KEDGE auto), arms c10240 / c9216 / c8192 ctl, 6 runs 0 crash, [s7037] k=0.6 in all, same positions per level. tools/s7032_pose_cull_score.py --base c10240: **L4 c9216 0.39/0.37/0.38/0.36/0.32/0.28/0.26 (0.4% px), ctl c8192 0.74-1.15 (1.0% px), A/A 0.00**; band rows ~716-800 x 1-1007 of 2720x1252 = the far shoreline on the left, lowered and jagged by eye (docs/owner_sheet_s7052_l4_219_cap9216.jpg). L1: c9216 and c8192 both <=0.02 (cap does not bind on L1: no power). 21:9 L12 stays ~59 fps at the bundle (s7048-s7050); both cheap levers (K0.5 s7051, cap 9216 s7052) shave the L4 horizon. OWNER-OPT-INS corrected. Next: does cap 10240 itself shave L4 21:9 (POOLX_MAX=6 12288 arm, NEXT.md).

**s7051 the s7050 21:9 K=0.5 default is REVERTED (H-visible-elsewhere): K=0.6 at every aspect again (src/main/main.cpp s7037 block).** Frozen poses 21:9 dd6 bundle, arms k05 (auto) / k06 (explicit 0.6) / foldk0 (KEDGE=0 control), same positions per level, 9 runs 0 crash: L1 k05 <=0.05 (ctl 0.56/0.53 at k5/k6); **L4 k05 0.06 -> 0.33 rising with k, 0.7% px in one far-horizon band (rows 717-803); by eye K0.5 shaves the curved far ground band to a flatter, lower edge (docs/owner_sheet_s7051_l4_219_k05_band.png); foldk0 = k05 pixel-identical, so KEDGE does not cover it**; L13 no power (ctl <=0.03, dark). K=0.5 stays an explicit opt-in (OWNER-OPT-INS). Boot check: 21:9 logs k=0.6, explicit 0.5 -> 0.5. Next: NEXT.md (cap 9216 qualification at 21:9 or close the thread).

**s7050 21:9 L12 fog-depth K lever: H-K selected, dd6 bundle now uses K=0.5 when wider than 16:9 (src/main/main.cpp s7037 block, FB_WIDTH>796; explicit ROGUESQ_DD_OFFMAPCULL_K wins; 16:9 keeps 0.6).** Same-run holds L12 21:9 dd6 WIDEWIN cap 10240 KEDGE 0.8,12, tog3 K, order rotated, 2x507 s, 0 crash/stall, xor8 ~22.6k frames: run A K0.6/0.5/0.45 58.6/59.5/59.7 fps, rsp 13.61/12.33/11.68; run B K0.5/0.45/0.6 59.5/59.4/58.8, rsp 12.16/11.56/13.44 -> K0.5 vs 0.6 +0.9/+0.7 fps (rsp -1.27/-1.29), K0.45 +1.1/+0.6 (rsp -1.93/-1.88); ocull/f ph +23% (0.5) / +34% (0.45), so H-noop refuted. Frozen poses (4 arms, one path, pos 156.5,-8.5,19.8): k05 and k045 0.00/0.000 vs k06 at in-flight k4-k6 although they cull ~2x more cells there (432/536 vs 207 ocull/f); positive control foldk0 (KEDGE=0) 0.60/0.59/0.66 -> H-K-visible refuted at these poses (single run of image evidence, 3 in-flight poses, L12 only). 0.5 chosen over 0.45 for margin (fps gain within run spread of each other). Boot check: 21:9 logs [s7037] k=0.5, 16:9 k=0.6. Next: qualify K0.5 at 21:9 on L1/L4/L13 poses + a hold (NEXT.md).

**s7049 21:9 L12 cap lever (no build): 8192 is cheaper but VISIBLE, 9216 invisible but tiny (H-cap-visible).** Same-run holds (tog3 WIDEWIN_CAP, order rotated, 2x507 s, 0 crash/stall): 8192 vs 10240 +0.7/+2.0 fps (rsp -0.60/-0.63), 9216 +0.5/+0.5 (rsp -0.13/-0.16); absolute 10240 59.0 in one run, 56.3 in the other (host/path spread ~3 fps, so s7048's 56 was partly the run). Frozen poses vs cap10240: cap9216 0.00, foldk0 ctl 0.60-0.66, **cap8192 13.4 at k4/k5 (9.5% px: drops a distant ice ground band; cap10240 = s7048 fold/dd6off cross-run)**. No default change; OWNER-OPT-INS states the trade; sheet docs/owner_sheet_s7049_l12_219_cap.jpg. Next: cheaper fog-depth K at 21:9 (NEXT.md).

**s7048 21:9 L12 check of the folded dd6 bundle (no build): KEDGE stays invisible, but L12 at 21:9 runs only ~56 fps with the bundle, gate or no gate.** Frozen poses 21:9 FPS60 L12 NOREF, arms dd6off / fold (auto, KEDGE 0.8,12) / foldk0 (KEDGE=0, positive control), 3/3 0 crashes, same posefreeze path: k4-k6 fold 0.06/0.05/0.06 0.0% px vs foldk0 0.66/0.65/0.71 1.5% px; by eye fold = dd6off soft band, foldk0 the flat cut (docs/owner_sheet_s7048_l12_219_kedge.jpg, rows dd6off/fold/foldk0, bottom 45%, k4|k6). Same-run hold L12 21:9 (tog3 KEDGE "0.8,12;0;0.8,12", 507 s flight, alive, 0 stalls, 0 crash), xor8 21.2k frames: p0 ke12 55.8 fps rsp 13.75 / p1 K0.6 56.5 rsp 13.48 / p2 ke12 55.6 rsp 13.74, P(>=2VI) 0.07/0.06/0.08; A/A p0-p2 0.2 fps, gate cost -0.7..-0.9 fps (+0.27 ms rsp), k2cells/f 1895/0/1957. So H-same refuted on cost, H-wide-visible refuted, H-wide-cost only partly: the shortfall is the 21:9 L12 bundle itself (rsp ~13.5 vs ~12 at 16:9), not the gate. KEDGE stays the default. Next: a cheaper lever for 21:9 L12 (cap tog3, NEXT.md).

**s7047 KEDGE=0.8,12 FOLDED into the dd6 auto bundle (src/main/main.cpp s7037 block, setenv overwrite=0; `ROGUESQ_DD_OFFMAPCULL_KEDGE=0` restores the hard cut).** Variants on L12 16:9 frozen poses vs dd6off: ke12 0.07/0.0% px (replicates s7046), ke10 0.39/0.8% (visible step at the N boundary), k07e12 0.27/0.5%, dd6b ctl 0.81/1.8%: only N=12,k2=0.8 is invisible. New per-phase syntax `KEDGE=a,Na;b,Nb;c,Nc` (upstream_compat.cpp) -> same-run hold ke12/K0.6/ke12: L12 59.6/59.8/59.9 fps (ke12 rsp +0.39/+0.33 ms vs K0.6; ke12 A/A 0.06), L13 60.0/60.0/60.0 (rsp +0.45), 0 crash/stall. Fold check: auto bundle 0.07 vs KEDGE=0 0.81 at the same poses, [s7037] kedge=0.8,12 logged. s7046's 58.0 fps (other autopilot path, k2cells/f 1836 vs 1140) is the low end; the >=58.5 bar is met in 2/3 ke12 phases over two runs. Owner look still decides; 21:9 L12 not yet checked (NEXT.md).

Open or awaiting the owner (each one line; detail in the s6994 archive under the session):
- **s6992 FIXED, default on: L15 21:9 dd4 crash.** ORIGIN ours: the game's pointer test
  `(p & 0xFF000000) == 0x80000000` (7 sites) rejected the 0x81000000 spill arena, a TLUT pointer
  became slot id 0x1058 and overwrote the material pool. tools/apply_s6993_ptrmask.py,
  ROGUESQ_PTRMASK=0 = retail mask. Same-binary control crash / fixed 200 s at 21:9 and 16:9.
- **G1e game fps per level (dd4 FPS60 VI_LOCK QOS_ALL, flown level checked): 60 in flight on all levels.**
  s6996: in-flight seconds (tools/g1e_level_fps.py fl_shown) L16 59.7, L17/L7 59.9, rest 59.8-60.0; C30 control 30.0.
  The s6993 L7/L16/L17 56.3-58.5 was menu/restart screen time inside the window (backdrop menu 16x, wl=0 presents).
- **G1e latency/present chain s6962-s6989, all closed:** defaults on ROGUESQ_VI_RT (s6967, VI
  thread time-constraint policy), STDERR_ASYNC (s6979), G1E_CELLIDX at dd>1 (s6963; mode 3 bounded flat since s7024); opt-ins
  VI_LOCK=1 (implies PRESENT_DRAIN_ACQ=8, target 10), QOS_ALL=1 (= GFX/GUEST/PRESENT/WL/UPLOAD
  QoS; quiet host neutral, burst lates 178 -> 6, s6989). Owner decides QoS default.
- **Boot freeze (1 in ~65, passive):** s6993 first live [stall-dump]: retrace thread 8011CD28
  blocked on a FULL send to 0x80128CF0, game thread waiting elsewhere. [stall-dump] self-samples
  host stacks (ROGUESQ_STALL_SAMPLE_DIR, tools/sample_game_threads.py). Wait for recurrence.
- **G5 owner items, fixed and awaiting the owner's flight/look** (G5a s6893 tile-pool overrun,
  G5b s6896-s6901 TriGen wrap + far loss, G5c s6902 shade-ordinal rehash stalls, G5d s6903 cine
  gate, G5e s6904 dd fog, G5f s6906 W_CLAMP, G5g s6907 hangar aim, G5h s6908-s6919 cutscene
  ground/floor/varclamp/cut-live): see Next steps 2-9. Final-mission dd>1 heap crash fixed by
  OSMEM_MB=12 at dd>1 (2026-11-05). DL chunk arena reclaim s6909 (dd>1 10-min crash).
- **Wide/aspect, 2026-11 fixes default on (=0 old):** G1D_SHOWROOM (s6926), G1D_340PERSP hangar
  width (s6927), G1D_INTROSHAPE / W640 / SCISSOR_TOL (s6929), notch safe area + exact VPW_SCALE
  (s6930), WIDE_LOGQUIET (s6932), WIDE_UNDRAWN cut-noise blank (s6924).
- **Opt-ins awaiting the owner's choice (default off):** VI_SHAPE (true 1.25 dot pixel, s6928;
  owner 2026-11-08: shape fine as is, stays opt-in, no further work), DD_MELT (s6916, sea slab),
  DD_SKYZ (s6917, SEL2 rule s6947-s6949), DD_CUT_LIVE (s6920), HANGAR_FOV, G5G_LENS.
  Owner ran MELT, SKYZ, VI_LOCK, QOS_ALL and reported nothing wrong (2026-11-08).
- **Closed, not ours:** s6923 lava-shot "wedge" is the game's own translucent mesh.
- Save guard: runner.sh exports ROGUESQ_NO_SAVE_WRITE=1 and snapshots build/saves to
  ~/Documents/RS64-save-backups/auto. Never touch the owner's save (profile "ASS").

## Closed work, summarised

Detail: PROJECT-OVERVIEW "Migrated from CURRENT-TRUTH (s6900 maintenance)" and "(s6994 maintenance)".
- **G3 retail match** (angrylion oracle, same-run controls): boot, attract, hangar, crawl, intro,
  missions 1-19 sim+render with dt pinned, front-end at RDP level, AT THE MOVIES 81/81. CLOSED s6784-s6792.
- **Default-on fixes from that sweep:** UCODE_CAP 65536 (dd>1 1048576), MENU_WORKER_FIFO,
  EXACT_EDGES, exact-ns VI deadline, LLE_FORCE/UNGATED/SOLO, audio_device_mutex.
- **G1e rate:** s6696 per-vector getenv removed (~17 fps since s6372), -O2, RSP work s6713-s6775,
  FPS60 rate classes closed s6828-s6831 (docs/FPS60-FIXES.md).
- **G1, G1c, G1d, G1f, G3c, M5, M3, M6, G2, renaming (s6868): closed.** G1(d) objectives and G4
  crash hunting parked by owner. dd4 is the ceiling that adds terrain (docs/DRAW-DISTANCE.md).
- **Wide + dd span class (s6879-s6885)** and 21:9/16:9 width class (s6848-s6861, docs/G1D-WIDTH-CENSUS.md).
- **Spill arena (s6858)** + heap address audit H-clean (s6862, docs/HEAP-ADDR-AUDIT.md); s6992
  found the 7-site pointer-mask class this audit missed (it looked for heap bounds, not mask tests).
- **Regen (s6863-s6881):** replay from pristine compiles/links/boots; live tree NOT regenerated
  (docs/REGEN-VERIFY.md). N64Recomp self-branch miscompile FIXED s7081 (tools/fixup_selfbranch.py).
- **Present thread (s6884-s6891, s6931):** SCREEN_JOB, PRESENT_INFLIGHT, PRESENT_DRAIN opt-in/off;
  true-60 Hz latency levels are sticky in whole vsyncs.

## Superseded conclusions — do not act on these
- s7122 "RT64 shows the 4:3 picture off-centre (21/66 px margins)". Believable: rect search on the capture fit well. s7123: SCK pads the right of the capture; in window points the margins are 43/45 (centred).
- s7120 "the flight camera sometimes jumps 2-16 u in one frame (open flight, both arms)" and "the lift arm has more >1.0 u jerks". Believable: t/t+1 pairs of equal size, far from any lift, in all runs. s7121: the join in s7119_hop mixed cam objects 458/A28/930; per-cam the flight cam has 0 such steps and the cut cams' stray tick is never presented.
- s7113 "H-raymiss CONFIRMED: the collision tests a surface up to ~0.2 u off the drawn mesh; H-gap refuted". Believable: two-pose static control agreed to 0.002-0.004 u and lattice snap fitted. But a common-mode error (fitted P00/P11, corner-frame basis) passes a two-pose test; s7114 exact surfaces from the shared bytes show the rebuild biased +0.07..+0.18 p50 (p90 to +0.52) where drawn == collision exactly.
- s7113 "the drawn mesh is displaced from the collision grid (0.042 off lattice)". Believable: same rebuild. s7114: TriGen and the sampler read the identical 25 bytes on the same lattice; the only real divergence is LOD decimation (flags in mesh+0x14), and removing it does not change the loss rate.
- s7098 "the near-wall flashes only appear with the 60 fps mode on". Believable: presented-episode counts leaned FPS60. At stream level the eye-cell near clip occurs at the 30 fps rate (s7108) and at full retail settings at the same rate (s7109, 17.4 vs 15.9 per hug-min).
- s7102 "the near-wall zig-zag is the corner push and the y clamp fighting (H-fight)". Believable: the one episode caught flipped push/all-miss/push at 105/1000 ticks. Over 5 more episodes (s7102 r1/r2) 2 had 0 flips, and in s7103 a fix that re-pushes after the clamp left the episode rate unchanged (5/2714 off vs 5/3738 on).
- s7100 "FPS60 near-wall episodes are 4.1x more frequent per tick (p=0.033)". Believable: 4 same-run splits agreed in direction. Two more runs (s7101 A, C) bring it to 1.6x, p=0.185; the excess is unproven. Also s7100's "push-out tuned for dt 1/30": the s7101 push-out has no dt.
- s7059 "transition stalls are mostly the game thread polling isAudioSlotActive/anyAudioSlotActive". Believable: 209/298 game-thread xctrace
  samples in stalls were audio polling. s7064's slot ring timed the waits directly: 25-66 ms per 200-335 ms gap (~14%); the sampler saw only
  ~30 samples per stall, so the off-sample remainder (game thread OS-silent 133-150 ms) was never attributed.
- s7032 "at poses 0-4 the craft flies below the plateau top, the wall face occludes it". Believable: by eye the dark wall stays in view and R=2
  only trims its top sliver there. s7033 read the clamped edge cells' heights in the game's own units: the eye is above them on ~99% of culled cells,
  so height occlusion does not explain the invisibility at poses 0-4.
Recent only; older entries: PROJECT-OVERVIEW "(s6994 maintenance)", "(s6900 maintenance)", "(s6870)", "(s6759 maintenance)".
- s7009-s7013 "WIDEWIN costs ~10-25 fps / VI cliff at 6144 / owner fps trade" (s7014): every arm ran the harness's LOG_PHASE
  probe path (main ucode TU, FAST off). Believable because the toggle split was same-run and self-consistent; the absolute level
  was the debug path's. Owner path: 59-60 fps at 8192. Any harness timing number since s6713 without G1E_FAST=1 PROBES=0 is suspect.
- s6895 "clamp on raises small transients at dd1, 306 vs 157" (s7003): old area-drop rule; under the current rule on is half of off.
- s6901 "ring 7 empties near diagonals" (s7001): dips are on axis headings, edge stepping at 56 cells; the guess was never measured.
- s6993 "H-level-cost: dense levels 7/16/17 run 56-58.5 fps" (s6996): whole-window shown/s counted menu/restart screens; in flight they hold 59.7-60.
- s6990 "60.0 fps on all 19 levels at 16:9" and s6962 "LEVEL=4 58.5, LEVEL=10 60.0" (s6991):
  FORCE_UNLOCK=1 clamps the cursor to level 1, every arm flew level 1. Check `cur` / cursorMask.
- s6991 "21:9 selects a 2000-slot texture table" (s6992): read after the corruption; it is 2048.
- s6984/s6986 VI-phase framing of lates (s6987): the chain picked the next frame's kick; R->W is the late term.
- s6968 "VI_LOCK alone cuts latency" (s6969): the gain is LOCK + ACQ8.
- "Port 4:3 presentation has retail shape" (s6928): retail spans 640 dots for 512 columns.
- s6918 "cutoff inputs match retail" (s6919): sampled after the game's write, before our overwrite. Sample at the reader.
- s6894 "no gap over 250 ms" via capture gaps (s6902): use tools/g5c_frozen_runs.py or [g1b] sd_wall max.
- s6901/s6810 "dd4 ~59 fps" applied to 16:9 (s6902): that was 4:3.
- s6788-s6791 "G3e drops CLOSED" (owner 2026-11-04, reopened as G5b): detector missed the owner's drops.
- s6895 "dd1 has no knife lines" (s6906): dd1 has the thickest, 29 vs 1 same run.
- s6791 "camera slides while yaw lags" (s6907): those floats are view translation, not position.
- PORTING-STATE line 1862 "Fog contributes nothing" (s6904): true only of the early pre-flight scene.
- g3_aspect_crop scores s6879-s6881 scored pillarbox bars; "pinned pose" s6445-s6583 is attitude-only;
  "300 s hold" FPS60/dd>1 s6774-s6862 counted from boot (use inits= and flight_s=).

## Run recipes and hard config

- Run from `build/` with the ROM beside it; SIGKILL to stop; one game run at a time.
- Disk is ~20 GB free: a 960x540 g5b_capture is ~9 GB/min (s7002 filled the disk at 125 s). Keep captures <= 90 s, delete raws after scoring.
- Pinned dd4 lvl1 run: `zsh scratch/agent/s6549_run.sh <dd> <poolx>`. G5 arm template
  `scratch/s6899/arm.zsh`; scenes `scratch/s6908/arm.zsh` (EARLY_N=13, FL_START past the scene).
  Hangar camera arms: `scratch/s6907/arm.zsh`, log ROGUESQ_G5G_CAM=<file>, score tools/g5g_pan_score.py.
  Per-level owner-recipe fps: tools/g1e_owner_quiet_arms.zsh (sets FORCE_UNLOCK to the level; check `cur`).
- dd4 needs no DD_UNSAFE (s6582); higher uses DD_UNSAFE (clamp 8). Confirm run.log echoes `multiplier N`.
- lvl10/15 need `ROGUESQ_FORCE_PLANET_UNLOCK=0xFF`. L10 flight is cloud with no terrain grid (s7000). Wide soaks need `MISSION_WIDTH=796|1024` +
  `WIDE_ROUTE=1`; ASPECT implies `OSMEM_MB=12`.
- Pose control: `ROGUESQ_POSE_LOCK=1` + `ROGUESQ_POSE_FREEZE=<x,...>:<ms>` (needs RAND_TRACE +
  DEBUG_WRITE; tools/g3_optin_pose_arms.sh, PIN=1 pins dt). Port dt pin:
  `ROGUESQ_XTRACE_POKE=800FA730:29:30:3d088889` (oracle RS64_XTRACE_POKE).
- Timing: any ROGUESQ_LOG_* turns FAST off and PROBES on: set `ROGUESQ_G1E_FAST=1 ROGUESQ_G1E_PROBES=0`.
  Per-frame meter `[g1b]` (sd_wall, tasks/s).
- Present rings (ROGUESQ_PRESENT_RING): check tools/g1e_present_cadence.py first; at=0 throughout
  is not a measurement; the window must be partly visible (ROGUESQ_WINDOW_POS). Late-present
  positive control: load generator scratch/s6982/burst.
- Freezes: stalls = [g1b] sd_wall max; image freezes = tools/g5c_frozen_runs.py on a g5b_capture
  .raw; `sample <pid> <s> <ms>` costs no build.
- AT THE MOVIES shots by run time (dd1 16:9): 76 887-912, 77 912-924, 78 924-942, 79 942-952 s.
- Frame comparison: window captures are Display-P3, convert to sRGB; port RDRAM fb dumps lack
  RT64 3D frames; score menus by RDP (tools/g3_rdp_frame_match.py, tools/g3_menu_pair.sh).
- Oracle missions: tools/g3_eep_patch.py sets +0x31; use --save-dir, never swap a save over the
  user .eep. Do not re-run mission-3 flight.
- Soak verdicts: `scratch/agent/SOAK-RESULTS.md`; read `alive_at_end` / `crashlines`, never rc.
- Knob tables: PROJECT-OVERVIEW "G1c draw-distance knob and recipe reference";
  docs/DRAW-DISTANCE.md; owner commands docs/OWNER-OPT-INS.md.

## G1 mission coverage

Playable levels 0..18 (`NUM_LEVELS=0x13`); 19/20 are sentinels. All have route, 300 s holds and
framebuffer presence; level 1 has a retail flight match; objective response (d) parked by owner.
See docs/G1-FRAMEBUFFER-COVERAGE.md and docs/G1-OBJECTIVE-RESPONSE.md. Never send hull damage on
level 8 (counter3==1 fails the mission).

## Durable constraints
- Never end a turn to wait on a run: foreground (timeout <= 600 s) or queue a soak (s6865/s6866).
- Retail defaults stay unless the owner chooses; never make an opt-in default from a single source.
- Crash-free holds do not mean "renders correctly" (s6468). No mitigation without naming the
  writer; dd>1 fixes live in `tools/apply_s6*.py` (registered in RS64_REPLAY only, docs/REGEN-VERIFY.md).
- Any guest pointer the game range-tests must sit where its test accepts it: 0x81000000+ fails
  `(p & 0xFF000000) == 0x80000000` unless ROGUESQ_PTRMASK (s6992). Re-check this for any new arena.
- Never reset, clean, checkout or update submodules; after editing `lib/` run
  `./submodule-patches/export.sh` and commit.
- Controls: get_n64_input is the pre-6ed036b97 mapping; no changes without an owner request.
- Title plume parked; reopen only on new evidence.
- Read `docs/F5-UCODE-REFERENCE.md` before interpreting Factor 5 streams. Positive control for
  every null; two independent lines before a conclusion enters this file.

## Next steps (single monotonic backlog)

Spec: ITERATION.md item 3c. No backlog-exhausted block. Owner order: G5i (fixed, owner look), then the rest; tog split de-biased s7017 (xor8); gfx-glue closed s7018 (walks 0.2-0.45 ms/frame); dd6/dd8 measured s7019 (55.8/53.3 fps, cells capped px5); s7020 dd6 cost = cells (H-cells, multiplier ~0); s7022 stream walk linear 171 ns/cell; s7025 clamp drift = our create hook double-updating the std index, fixed (create 6.5 us -> 218 ns); s7026 DPC submit = RT64 per-byte + ~21 ns/bump bridge, wait flat; s7027 per-bump checks only ~3.6 of ~24 ns (H-checks refuted); s7028/s7029 bridge split closed (H-call, shadow refuted); s7030 fogged-cell cull: H-fogwaste refuted, 0.5 x fog-end depth cull = rsp -4.9 ms invisible on L1 (H-offmap lead); s7031 off-map census: 82%/62% of dd6 cells off-map, R=2 cull rsp -9.75/-3.71 ms (L1/L4), image unqualified; s7032 frozen poses: R=2/R=8 VISIBLE once the eye climbs above the off-map plateau (H-plateau); s7033 height gate image-neutral but saves 0 ms (H-costgone, eye above edge tops almost always); s7034 off-map past 0.6 x fog end: ~invisible at 7 poses, rsp -3.04 ms -> 60 fps on L1 (H-fogdepth); s7035 L4 repeat: <=0.10 at 8 poses, rsp -1.52 ms (H-general, opt-in offered); s7036 holds clean (opt-in qualified); s7037 cull bundled into DD knob for dd>=6+WIDEWIN, 12288 cells buy nothing visible at +0.6 ms; s7038-s7040 bundle qualified (21:9 poses, cutscenes, 16:9); s7041-s7043 bundle holds all levels 0-18 at 16:9 clean (L12 42.8->59.7, L13 48.3->59.9 need the cull); s7044 L12 bundle VISIBLE (horizon band cut, 0.8-0.9 / 1.8% px, A/A 0), L13 clean; s7045 H-trade: K=0.8 invisible but 54.1 fps on L12, retail has no ground there (defect = hard cut edge); s7046-s7051 KEDGE folded, 21:9 L12 levers (cap 8192/9216, K0.5) all shave a horizon somewhere; s7052 closed the 21:9 L12 cost thread at ~59 fps; s7053/s7054 cap 12288 on L4 21:9: +2-5 shoreline rows at rsp +0.25 ms, fps unchanged (opt-in offered); s7056-s7060 21:9 level K (12:0.5,13:0.5 auto), survey 17 levels; s7061 L9 burst = cells, cap 8192 holds 60 (CAPLEVEL knob); s7062 9:8192 folded into 21:9 auto (poses invisible, hold 60.00); s7064 transition stalls: audio drain = 25-66 ms of 200-335 ms gaps, game thread OS-silent 133-150 ms; s7065 that stretch = waitForMusyXAudioTaskDone 3072-sample countdown (139 ms, retail-designed), thread closed; active unit: NEXT.md.

1. **G5i: fixed s6995, closes on the owner's look** (abort -> hangar -> scroll across several craft or
   double-press). Route scratch/s6995/arm.zsh + route_long.txt; metric tools/g5i_pan_metric.py. Fullscreen dd2/dd4 verified s6997; 21:9 and L14 abort verified s6999. Nothing left to run.
2. **G5a mission crash: fixed s6893, awaiting owner re-flight** of Gerrard V (LEVEL=4) past half
   way, repeated. s6998 closed the copyNativeToRAM question: every writeback lands in the image's own
   heap block or above the heap (0 stale / foreign / header hits, dd4 16:9 and dd1 4:3, ROGUESQ_G5A_WBLIVE=1).
3. **G5b terrain drops: awaiting owner flight.** s6901 far-loss fix (FWDWIN) holds on L4, L1, L5 (s6902) and L7 (s7000, dd4: dips 36 -> 0,
   ring 5/6 dips 61/77 -> 0/3, worst heading p10 1474 -> 3131; score with tools/g5b_fwdwin_seamless.py, which drops the flip seam).
   LEVEL=10 has no terrain grid in flight (cloud level): never use it for terrain measures. Ring-7 dips closed s7001 (axis-heading edge stepping, not diagonals, not a loss).
4. **G5c freezes: fixed s6902, soak clean; closes on owner flight.**
5. **G5d Factor 5 logo: fixed s6903; owner boot at dd2/dd4.**
6. **G5e fog: done s6904; owner look.** 21:9 dd4 far slab (s7007): fully fogged terrain, fog colour (152,107,98) vs sky band (~205,152,110); DD_FOG barely moves it,
   dd1 has none, opt-in DD_MELT takes it to the dd1 floor same run (hard80 40->26% centre; tools/g5e_edge_score.py; sheet docs/owner_sheet_s7007_melt_219.png).
   Residual side/corner edge = the 64x64 terrain window's SIDE (s7008, two lines: same-run FWDWIN=tog changes side-third hard80 23->18 / 27->12; trace
   site 13 shows the frustum footprint 140-290 cells wide vs the 64-cell box). K is not a lever: the box is pinned to the near footprint edge, so
   K 0..30 moves the centre exit only 64->68 cells while 21:9 side rays leave through a side face at 18-22 cells on 98% of calls (tools/g5e_window_geom.py;
   MAPWIN_K=8 tog run: no consistent change). Fix = widen the window past 64 columns (slot array 0x80132DC0 row<<8 stride, span tables
   0x80130DB0/0x80131DB0; 9 base sites in binPolygonIntoTerrainGrid/streamTerrainGridCellsByDistance/buildGridCellMeshForFace).
   **s7009 built: ROGUESQ_DD_WIDEWIN=1|tog (opt-in), tools/apply_s7009_widewin.py**: tables moved to 0x83000000 at 128 stride (9 base + 11 shift sites,
   s6049/s6882/s6883 bounds follow g_rs64_ww), window up to N=128 per axis, pool cap spent on forward axis first. Same-run tog, two runs, 21:9 dd4 L4:
   side-third hard80 N128 18.4->14.6 / 16.1->8.3, N96 21.2->12.7 / 17.7->5.8, centre flat; trace 128x64 or 64x128 on 89% of on calls, pool 8192 never
   exhausted (site 18 = 0); 0 crashes. COST: captured fps 59.6->50.7 (N128) and 61.9->49.4 (N96, window 96x85): cost follows cell count (area 8192 vs 4096),
   not shape. Owner sheet docs/owner_sheet_s7009_widewin_219.png. Holds L1/L15 300 s clean (crash=0, wide on), L4 still queued. **s7010 cost = H-rsp** (G1E_TL same-run tog split, tools/g5e_cost_by_parity.py,
   0.5 s-shifted control collapses to T -0.16): per frame guest run 1.83->2.56 ms (+0.74), gfx task start->RSP exit 13.26->16.90 (+3.64, p90
   16.3->23.2), so P(frame >= 2 VI) 0.07->0.61 and fps 56->37; single run.
   **s7011: two cost levers refuted.** (i) Frustum cull: code-read, the stream (0x80042D50..DA8) already skips every cell whose span from the game's 3D
   view pyramid (eye 0x80130C10 + 4 far corners, 0x800439C0..A14, x-extent widened by FP_XSCALE) is empty or misses the cell's height range, so the
   extra wide-window cells are inside the view; agrees with s7008 geometry (side rays leave the 64 box at 18-22 cells). A 2D wedge cull would remove
   nothing. (ii) LOD tiers 0x8009DE94..A0 = 256/49/30.25/16 dist^2 in node units, i.e. they only grade the ring within 4-16 nodes of the eye; new opt-in
   ROGUESQ_DD_LODMUL=<f> (_TOG=1, tools/apply_s7011_lodmul.py) at 0.25 and 4: rsp on-off +1.03 / +1.09 ms vs null arm (mul 1) +0.08 and 0.5 s-shifted
   controls +0.45/-1.40/+0.74, so no effect above the ~1 ms parity noise in either direction. Confound found: arm scripts' default
   ROGUESQ_CULL_SPIKE=tog shares the 1 s parity; the null arm shows it does not bias rsp (s7010's +3.6 stands), use CULL=1 in future tog arms.
   **s7012 area cap (ROGUESQ_DD_WIDEWIN_CAP=a[,b,c], WIDEWIN=tog3 cycles them per mach second, tools/apply_s7012_widewin_cap.py):** one same-run
   3-phase run each, 21:9 dd4 L4 CULL=1. Cost (g5e_cost_by_parity.py --phases 3): rsp 13.62 / 15.64 / 16.94 ms at 4096 / 6144 / 8192 (8192-4096 +3.32
   reproduces s7010's +3.64; 1/3-period shifted splits smear as they must), but fps 57.3 / 37.5 / 34.9 and P(>=2VI) 0.04 / 0.60 / 0.72: the VI cliff
   (rsp + guest run past ~16.7 ms) is crossed already at 6144. Edge (g5e_edge_score.py phases=3): side-third hard80 left 22.5 / 17.2 / 17.6, right
   18.2 / 13.5 / 14.4: all the side-edge gain arrives by 6144 (edge knee), the fps cost is nearly all-or-nothing (cliff). Sheet
   docs/owner_sheet_s7012_widewin_cap.png (rows 2-3 flight; row 1 caught a debrief). Next: caps below 6144 (4608/5120/5632) to find the largest
   cap that stays under the VI cliff and how much side-edge gain it keeps (NEXT.md).
   **s7013: no room below the cliff.** Same-run caps 4096/5120/5632: fps 54.2/45.7/43.3, P(>=2VI) 0.11/0.31/0.38, rsp 13.06/14.13/14.41 (~0.9 ms per
   1000 cells). H-room refuted: WIDEWIN is an owner trade (wider 21:9 sides for ~35-45 fps) and stays opt-in. Both at once needs a cheaper gfx RSP task
   (13 ms at the retail window is the binding term). Next: profile the gfx RSP thread at 21:9 dd4 to name the hot ucode path (NEXT.md).
   **s7014 SUPERSEDES the s7009-s7013 cost lines above** (harness probe path): owner path 59-60 fps at caps 4096-8192, rsp 8.8-11.9 ms,
   two runs. WIDEWIN is free at 21:9 dd4 L4; still opt-in until the owner says. s7015: L15 21:9 and L4 16:9 free, L1 21:9 58.1 fps (P 0.03);
   offered in OWNER-OPT-INS, owner look. Glue walks measured s7018: 0.2-0.45 ms/frame, closed.
   s7019 dd>4 at 21:9 WIDEWIN L1: dd6 55.8 / dd8 53.3 fps vs dd4 59.5; POOLX clamp 5 means dd>=5 = 10240 cells, dd8 = dd6 window.
   s7020: same-run cap split at dd6: 8192 cells = dd4 cost, +2048 cells = rsp +1.7 / run +0.7 ms (52 fps); dd8's extra was cross-run. Headroom needs a cheaper per-cell path.
   s7021: per-frame split names it (gfx +1.72 = ucode self 0.70 over 7 blocks + submit 0.68 + 0.26; game +0.91, streamTerrainGridCellsByDistance
   +0.31 largest); e9prov route counters gated (rsp -0.14 same run). Next: streamTerrainGridCellsByDistance per-frame walk (NEXT.md).
   s7022: that walk is linear, 171 ns/cell inclusive, 1 call/frame, 1.38 ms at 8192 cells. Next: split ns/cell into self vs callees + skip fraction (NEXT.md).
   s7025: create-hook double index update fixed. s7026 (two runs, spin control passes): post-fix dd6 cap 10240 = 53-54 fps vs 59 at 8192, +1.3 ms/task;
   DPC share = RT64 handoff per byte (~3 ns/B flat; only 7-8 handoffs/task, nothing to batch) + bridge ~21 ns per DPC_END bump (85k bumps/task = ~1.9 ms
   fixed, all caps); lock wait flat ~1.4 ms/task (RT64 fbwait, single-source name), not per-cell. Next: bump fast path in rsp_dpc_submit_impl (NEXT.md).
   s7027: bump fast path (ROGUESQ_G1E_BUMPFAST, opt-in, exact: 408M checked, bad 0, ctl 4) skips all per-bump checks on 54% of bumps but cuts
   bridge self only 8% (24.4 -> 22.4 ns/bump): H-checks refuted; the cost is the push/counters/atomics (or AQ=3 timing offset). Next: split those (NEXT.md).
   s7028/s7029: bridge closed (H-call). s7030: ROGUESQ_DD_FOGCULL (opt-in): 2% of cells past fog end (0 ms); 0.5 x fog end culls 51%, rsp -4.9 ms, invisible on L1
   (cells behind the off-map horizon wall?). Next: classify on-map/off-map cells and cull off-map rings, L1 + L4 (NEXT.md).
   s7031-s7036: off-map cull past 0.6 x fog end qualified (see headline). s7037: folded into the DD knob for dd>=6+WIDEWIN; 12288 cells (POOLX_MAX=6) cost
   +0.6 ms rsp with no edge-score gain at dd8: dd6+bundle is the max useful step. s7038: close-out sheet done, bundle invisible (<=0.23 vs A/A 0.00), dd6 > dd4 > dd1; CLOSED on the owner's look. s7039: bundle invisible in the cutscene playlist (tog3 rank, R0 control fires). s7040: clean at 16:9 too (poses <=0.28, L1 58.6 -> 59.9 fps). s7041/s7042: 16:9 holds clean on L0, L2, L3, L6-L9, L11, L12 (L12 needs the cull: 42.8 -> 59.7 fps). s7043: L13-L18 clean too (L13 48.3 -> 59.9 needs the cull); sweep CLOSED. s7044: L12 bundle shows a hard horizon cut (L13 clean); s7045: retail dd1 has no ground there, K=0.8 invisible but 54 fps; s7046: KEDGE=0.8,12 invisible at 58.0 fps (L1 no cost). s7047: N=10 / k2=0.7 visible (0.39 / 0.27); ke12 folded into the bundle (L12 59.6-59.9, L13 60.0 same run). s7048: 21:9 L12 gate still invisible (0.06 vs ctl 0.66) but the bundle holds only ~56 fps there (K0.6 56.5, ke12 55.7; gate -0.8 fps). s7049: cap 8192 visible, 9216 tiny. s7050: K=0.5 at >16:9 folded into the bundle (L12 21:9 +0.9/+0.7 fps, poses 0.00). s7051: K0.5 shaves the L4 21:9 far horizon (0.33, by eye) -> reverted, opt-in only. s7052-s7055: caps 9216 visible, 12288 small cost. s7056: K=0.5 level-scoped to L12 at >16:9 (KLEVEL, +0.6/+0.5 fps same run, L4 stays 0.6). s7057: L13 added (+0.9 fps, poses clean vs K0.3 control). s7058-s7063: 21:9 survey of all 19 levels CLOSED (~60 fps in flight, 0 crashes; L9 auto cap 9:8192). Owner look.
7. **G5f knife lines: fixed s6906; owner flight.** Lines < 60 px at dd4 L4: real geometry, W_SHEET_PX=200 confirmed (s7002). dd1 closed s7003 (clamp halves transients, removes knife lines). dd2 L7 s7004: long lines fewer, drops leave 0 holes (DROPLOG). Owner sheet s7005 docs/owner_sheet_s7005_g5f.png (dd4 L4: 0 clamp-on knife lines in 24 viewed). 21:9 dd4 s7006: 0 clamp-on knife lines in 29 viewed, sheet docs/owner_sheet_s7006_g5f_219.png. Nothing left to run; owner look.
8. **G5g hangar stretch: done s6907** — superseded in priority by item 1 (re-entry failure).
   Owner decides on flight and cutscene lens (report sheet docs/owner_sheet_s6907_lens_elsewhere.png).
9. **G5h cutscene background: closes on the owner's look.** Intros s6908, playlist s6909, scene
   s6910, floating triangles s6911, far band s6919; DD_MELT, DD_SKYZ, DD_CUT_LIVE opt-in, owner chooses.
10. **L15 21:9: owner re-flight after s6992 PTRMASK.**
11. **G1e residual: CLOSED s6996** (in flight 59.7-60 on all levels; the shortfall was non-flight time).
    Use fl_shown/fl_miss, not shown/s, for per-level fps. Open, owner scope: why L7/L16/L17 autopilot holds cycle the backdrop menu.
12. **G1d close-out awaiting owner judgement** (scratch/s6731/sheet_menus_owner.png).
13. **Scene-transition stalls: CLOSED s7065** (retail-designed 3072-sample audio wait, ~139 ms, plus slot drain). Reopen only on an owner report of a transition hitch longer than ~350 ms.
13b. **Hot getenv: CLOSED s7066. Hot dladdr: CLOSED s7067. Diag call-site gates: CLOSED s7068 (ROGUESQ_DIAG_GATE) + s7069 (generated sites, ROGUESQ_DIAG_CALLSITE).** Gfx-thread hash/memmove audit CLOSED s7070 (RT64 framebuffer tracking, ~0.22 ms/frame, no rs64 caller).
14. **Owner judgement / parked:** FPS60 feel, G3c sheets, QoS default, native hangar geometry,
    rare dd4/dd8 gfx SIGBUS (single-source). Reopen on an owner report or side-effect failure.
15. **(PARKED by owner) G1(d) objective qualification.** PORTING-STATE s6640-s6687 first.
16. **Misnomer rename: CLOSED s7080** (menu overlay s7072-s7077, text-slot family s7078/s7080, controller input s7079). Tools: tools/apply_symbol_renames.py + tools/s7075_fnsum.py. Reopen only on an owner report.
17. **N64Recomp self-branch miscompile: FIXED s7081** (tools/fixup_selfbranch.py in the vendored fixup chain, differential test vs retail bytes). Any new `branching outside` warning after a regen: rerun tools/scan_selfbranch.py + the test.
18. **N64Recomp lowering censuses: series CLOSED s7087** (s7082 warnings, s7083 control flow, s7084 FPU, s7085 integer + ddivu /0 fix, s7086 memory/immediates/branches, s7087 residual opcodes + 120/120 mnemonic coverage + osGetCount sign-extension fix; tools/s708[2-7]_*). Rerun all after any regen.
19. **Host-shim census: CLOSED s7088 (ABI) + s7089 (results vs ROM; s3531 duplicate-call fixup bug fixed).**
20. **Fixup-layer statement census: CLOSED s7090** (0 untagged dup/drop; tools/s7090_fixup_statement_census.py, exit 1 = a defect; rerun after any fixup edit).
21. **RSP ucode fixup census: CLOSED s7091** (0 unexplained; regen via tools/ucode_regen.sh, rerun `verify` after any RSPRecomp/fixup change).
22. **RSP VU fast paths + divide: CLOSED s7092** (tools/s7092_vu_mem_test, 0/8.59 G; rerun after any rsp_vu*.hpp / rsp.hpp DMEM edit).
23. **RSPRecomp scalar lowering: CLOSED s7093** (tools/s7093_su_census.py --controls; sltiu $zero/neg-imm template fixed in RSPRecomp; rerun after any RSPRecomp change).
24. **RSP runtime DMA + cop0: CLOSED s7094** (audio ucode_data off-by-one fixed; tools/s7094_dma_test + tools/s7094_dma_census.py, rerun after any rsp.hpp/rsp.cpp DMA edit).
25. **DPC registers CLOSED s7095; bridge forwarding coverage CLOSED s7096** (ROGUESQ_S7095_DPC / ROGUESQ_S7096_FWD=ctl, rerun after any dpc_bridge.cpp submit/defer/wrap edit; MISSING_UNEXPLAINED/dup/order must stay 0). Edit-walker census CLOSED s7097 (ROGUESQ_S7097_EDIT=ctl; unattributed must stay 0). RT64 vs angrylion on the same dd4 stream CLOSED s7098 (H-stream: big drops are in the stream; replay with tools/angrylion_replay/build16.sh).
26. **Near-wall flicker (s7098-s7115): eye-cell near-plane loss, RETAIL behaviour (s7109). Refuted: corner width, near 15, margin re-push, post-move, ucode drop, LOD decimation (s7108-s7114), H-gap (s7115). s7115 H-probe CONFIRMED s7116 (opt-in ROGUESQ_S7115_NEARLIFT=1: pooled 4 runs losses 83/31, pierce class removed). s7117: swap = previous tick's camera; residual at terrain 1.0-1.5 near. s7118: NEARK=1.6 removes it (steady 13/1, 5 runs). s7119: no hop at k1.6 (H-smooth, same-run jerk vs off). s7120: off vs k1.6 replicated, 42/2 over 4 runs (z -6.0). s7121: no flight-cam steps (s7120 steps were a cam-mix join). DONE: closes on the owner's look.** Drop is in the RDP stream (s7098).
27. **G3 flight fidelity at retail settings: CLOSED s7124** (L1 s7122 + L6 s7124, RT64 == angrylion; replay snapshot bug fixed in frame_replay.c). Owner recipe L6 CLOSED s7125 (H-equal). W_SHEET escape CLOSED s7130 (ROGUESQ_W_SHEET_POS default on; both arms pixel-checked; owner sheet s7129).
28. **G3 owner-recipe fidelity L1/L4: CLOSED s7131 (H-equal).** tools/s7131_arm.zsh; L1 frac>40 0.028 (retail floor 0.024), L4 0.017. Sheet docs/owner_sheet_s7131_L1_L4_fidelity.png.
29. **G3 21:9 holes: CLOSED s7132-s7140, owner look.** HORIZON_XFIX (s7133), GATEFIX (s7135), SKYFILL (s7136; insert before L_8005BC8C); L6 top-fade skirt fadeH=0 is RETAIL (s7138, table 0x800A05D0+0x30*lvl+0x2C). Holes 0 on L1/L4/L15/L6 vs SKYFILL=0 77-107. Sheets docs/owner_sheet_s713[69]_*, s7140. Detail: PORTING-STATE s7132-s7140.
30. **G3 owner-recipe fidelity at 21:9: CLOSED s7141 (H-equal).** L15 med 0.019, L6 0.012; side excess = HUD rings. tools/s7141_{arm,post}.zsh. Sheet docs/owner_sheet_s7141_219_fidelity.png.
31. **G3 hangar 21:9 + 16:9: RECT_ASPECT fixed s7142; residual = registration (s7143). CLOSED, owner look.**
32. **G3 level select + available craft 21:9: CLOSED s7144 (H-equal).** Sheet docs/owner_sheet_s7144_menus_219.png.
33. **G3 STAR WARS logo recede 21:9: CLOSED s7145 (H-equal).** Sheet docs/owner_sheet_s7145_logo_219.png.
34. **G3 text crawl 21:9: CLOSED s7146 (H-equal).** Route = s7146_arm.zsh with AP ending 64:a (crawl swaps 5200+). Crawl = 640x300 fb (cimg w640, 0 texrects): RECT_ASPECT=0 arm identical. One fit (x +0.25, y 0, yscale 0.992) + x-scale 1.0025: frac 0.082 -> 0.004-0.008. Sheet docs/owner_sheet_s7146_crawl_219.png.
35. **640-fb crawl x-scale 1.0025: CLOSED s7147 (noise).** VI scans exactly 640 cols (xScale 0x400, hStart 108..748) and RT64 boxes 640 in the 1024 fb's window span; a fine-grid fit (tools/s7147_joint_fit.py) gives 1.000 on two new runs, 1.0025 only on s7146 T1. Side: RT64 fbSize() shows 2 rows more than the VI (296 vs 294, 336 vs 334); opt-in ROGUESQ_VI_EXACT_ROWS=1, register-correct, pixel-unqualified.
36. **(next, NEXT.md) G3 mission intro cutscenes at the owner recipe 16:9** vs angrylion (not covered by 27-34).

## Evidence index

- s6994 maintenance archive (whole s6993 CURRENT-TRUTH verbatim): PROJECT-OVERVIEW.
- s6982 (s6964/s6965 present level), s6962 (G1e thread s6935-s6961), s6926, s6924, s6918, s6917,
  s6915, s6914, s6912, s6909 trims: PROJECT-OVERVIEW "Migrated from CURRENT-TRUTH (sNNNN)".
- s6900, s6847, s6759 maintenance archives; [Maintenance s6667 retained evidence](PROJECT-OVERVIEW.md#maintenance-s6667-retained-evidence).
- Objective contracts [G1-OBJECTIVE-RESPONSE](G1-OBJECTIVE-RESPONSE.md); images [G1-FRAMEBUFFER-COVERAGE](G1-FRAMEBUFFER-COVERAGE.md).
- Queued-soak verdicts: `scratch/agent/SOAK-RESULTS.md`; latest s6980_219_async_noqos_r1/r2 (folded s6981).
- Recent chronology: PORTING-STATE sessions 6893-6994; search bounded windows only.
