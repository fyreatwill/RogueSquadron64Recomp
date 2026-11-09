# Rogue Squadron 64 Recomp — current truth

Compact operational handoff, as of Session 7034 (2026-11-09).
`PORTING-STATE.md` is the chronological ledger; durable and migrated material lives in
`docs/PROJECT-OVERVIEW.md`. The full pre-compaction text of this file (s6893-s6993 headline
bullets with every number, superseded list, G1e chronology) is archived verbatim in
PROJECT-OVERVIEW "Migrated from CURRENT-TRUTH (s6994 maintenance)" — grep there for any sNNNN.

## Headline

**s7034 off-map cull past k x fog end: H-fogdepth on L1 (21:9 dd6 WIDEWIN cap 10240 MELT FPS60, 6 runs, 0 crashes).** New ROGUESQ_DD_OFFMAPCULL_K=<k>|a,b,c
(default 0): an off-map cell past R is culled only if its depth > k x fog end. Frozen poses, _H=off: K=0.6 0.01-0.04 at poses 0-4 and 0.18/0.17 at the void poses 5/6
(ungated R=2 10.6/39.0, FOGCULL 0.3 control 3.6/4.0; by eye = offA, diff a horizon sliver); K=0.8 <=0.05. Same-run cost: K=0.6 rsp -3.04 ms, 54.8 -> 60.0 fps,
P(>=2VI) 0.10 -> 0.00; K=0.8 only -0.56. Sheet docs/owner_sheet_s7034_fogdepth.jpg. Single level: L4 repeat next (NEXT.md), then owner opt-in
`ROGUESQ_DD_OFFMAPCULL=2 ROGUESQ_DD_OFFMAPCULL_H=off ROGUESQ_DD_OFFMAPCULL_K=0.6`.
**s7033 off-map height gate: image-neutral but costs nothing (H-costgone; L1 21:9 dd6 WIDEWIN cap 10240 MELT FPS60, 5 runs, 0 crashes).** New default-on
ROGUESQ_DD_OFFMAPCULL_H=<margin> (=off fixed R, =tog gate in tog3 phase 1 only) culls an off-map cell past R only while the eye is below its clamped edge cell's
top, read from the game's own record bytes (rec+3/+4, units y*C/H as in scanConvertTriangleToSpanTable; up self-calibrated from the eye cell, y down-negative).
Frozen poses: R=2+gate = offA to 0.00 at all 7 poses; R=2 ungated reproduces s7032 exactly (0.20..39.0), k03 control 0.5-4.0 (sheet docs/owner_sheet_s7033_heightgate.jpg).
Same-run cost (tog3 R=-1 / 2+gate / 2): rsp 14.19 / 14.20 / 6.23 ms, fps 53.3 / 55.2 / 59.8; the gate leaves 42 of 5444 culled cells/frame: the eye is above the
edge tops on nearly the whole flight. So s7032's "poses 0-4 are below the plateau top" is wrong (by-eye reading): the cull is invisible there for another reason
(fog / on-map occlusion). Height lever closed. Next: off-map AND past k x fog end (NEXT.md).
**s7032 off-map cull is VISIBLE at frozen poses (H-plateau; L1 21:9 dd6, separate deterministic same-pose runs, tools/s7032_pose_cull_score.py, 9 runs 0 crashes):**
A/A 0.01, FOGCULL=0.3 control 0.5-4.0. Below the plateau top, R=2 trims only a wall-top sliver (0.13-0.51). Once the craft climbs above the off-map plateau near the edge,
R=2 leaves a sky void (39.0) and R=8 a wedge (15.5) (docs/owner_sheet_s7032_offmap_pose.jpg). The eye stays on the map (new eye-cell latch, tools/apply_s7032_eyegate.py;
its EYE gate never fired), so the gate must be height-based: cull only while the eye is below the clamped edge height. OFFMAPCULL is not an opt-in candidate yet.
Fixed: a plain ROGUESQ_DD_FOGCULL=<k> starting with '0' (e.g. 0.3) never armed the hook; only tog3 worked before.
**s7031 off-map cells (tools/apply_s7031_offmap.py, opt-in ROGUESQ_DD_OFFMAPCULL=<R>|tog3, default off; dd6 21:9 WIDEWIN cap 10240, L1 + L4, 0 crashes): H-offmap selected
on census + cost.** 82% (L1, map 64x64) / 62% (L4, 94x94) of streamed cells are off the map (clamp branch), 95% / 82% of the 0.5-1.0 fog-end band, mostly 17+ rings
outside the edge. Culling off-map cells beyond 2 rings: L1 rsp 15.21 -> 5.46 ms (49.6 -> 60 fps), L4 12.27 -> 8.56 (55.4 -> 60). Image NOT qualified: the mean-image
A/A floor exceeded the k=0.3 control in both runs (autopilot banking); by eye the L1 wall face stays (sheets docs/owner_sheet_s7031_offmap_l1.jpg / _l4.jpg). Next:
frozen-pose check done s7032 (visible).
**s7030 fogged-cell cull (ROGUESQ_DD_FOGCULL=<k>|tog3, opt-in default off, tools/apply_s7030_fogcull.py; L1 dd6 21:9 WIDEWIN cap 10240, 3 runs, 0 crashes):**
H-fogwaste refuted: only 2.1% of the ~7040 streamed cells/frame lie past the fog end (fe ~86 grid, frustum far 108); culling them (k=1) saves 0 ms.
But a forward-depth cull at 0.5 x fog end removes 51% of cells: rsp -4.9 ms/frame, 48.6-53.8 -> 59.7-60 fps (two runs; 1/3-period shifted control smears),
and on L1 the image does not change (mean-image |d| 2.4-3.1 vs k=0.3 positive control 8.2; sheet docs/owner_sheet_s7030_fogcull.jpg): those cells sit
behind the dark horizon "wall", which looks like clamped off-map cells (s7024: 97-98% of getGridCellValueAt time is the off-map clamp branch).
New lead H-offmap (single level, single-source). k=0.5 is NOT a default candidate until an open level is checked. Next: NEXT.md (off-map cells).
**s7029 bridge trimming CLOSED (H-call; L1 dd6 21:9 WIDEWIN cap 10240, 0 crashes x2):** the s7028 BUMPFAST=2 bad2=1 was the CHECKER: its
`ref.exchange(0) == x && ...` short-circuited on the 4 planted flushes, so ref_cmds was never reset and flush 5 always miscompared. Fixed;
BUMPFAST=2 CHECK now exact (bad2 0 of 13499, ctl2 4/4, state guard 475M bad 0). Shadow split, same run (new ROGUESQ_G1E_BUMPFAST_SH=tog3,
tools/s7029_shadow_split.py): net ns/bump as-is 9.66, reserve 14.68, no-shadow 13.65 -> neither the S4272 shadow copy nor vector growth carries
the remainder (both arms read slower: per-arm noise ~5 ns/bump); the rest is call overhead + range push. Single-source. Bridge micro-trimming
stops here (whole bridge <0.3 ms/task left to win); BUMPFAST/BUMPFAST=2 stay opt-in. Next: NEXT.md (fogged-cell cull at dd>4).
**s7028 bump cost split (BUMPFAST=tog3 same-run 3-way + new AQ_NULL offset column, tools/s7028_bump_push_split.py, L1 dd6 21:9 WIDEWIN cap 10240, 0 crashes):**
H-offset: 9.0 of the 24.7 ns/bump "bridge self" is the AQ=3 clock pair (flat across arms). Real cost is 15.7 ns/bump (~1.37 ms/task): checks 1.7 (11%),
counter atomics 3.3 (21%, below the 40% H-atomics bar), push/shadow/call 10.7 (68%, the largest term). New opt-in BUMPFAST=2 (plain per-task counters)
is NOT exact yet: CHECK bad2=1 of 11702 task flushes (ctl2 4/4, state guard 395M bad 0). s7026/s7027 per-bump absolutes include the offset; their deltas stand.
**s7025 clamp drift named and fixed (tools/apply_s7025_clampsplit.py, same switch ROGUESQ_S7022_ST=1, L1 dd6 21:9 WIDEWIN cap 10240, 4 runs, 0 crashes):**
the ~40 -> 130 ns climb per clampGridCellLookup call was the create path (~40-80 creates/frame, 88 ns -> 6.5 us each), and inside it neither game
call (processGridCellByDistance 22 ns, nested alloc gv 45 ns, both flat) but our own host hook rs64_s6963_create, which also updated the unbounded
std index while mode 3 was active. Fix, default: update only the index in use (ROGUESQ_G1E_CREATE_BOTH=1 old, =tog 8 s A/B). Same run: create 218 ns
flat vs 1.0 -> 4.9 us, clamp call 92 vs 122 ns (~0.2-0.3 ms/frame at dd6). Exact: CHECK=2 45.0M compares 0 bad, flip 45110/45110. Residual: index
get+validate rise ~25 ns once the 10240-record pool fills (record reads spread, r_step ~3400): minor, left. Thread closed; next NEXT.md.
**s7024 getGridCellValueAt split (tools/apply_s7024_gvbranch.py, ROGUESQ_S7022_ST=1, L1 dd6 21:9 WIDEWIN, 4 runs, 0 crashes): H-clamp.** The off-map
clampGridCellLookup branch is 97-98% of gv time (4500-6300 calls/frame, 113-155 ns); direct table hits 10 ns; node walk ~0. New default at dd>1
ROGUESQ_G1E_CELLIDX=3: the s6963 index as a bounded flat table (record -> key reverse array; =2 old std index, tog3 = same-run A/B). Same speed
as std (113.7 vs 112.9 ns, same run), exact (CHECK 42.1M compares 0 bad, flip control 42253/42253). The std index never drops re-used records'
keys (7.5k -> 338k in 3 min); the flat one peaks at 10.2k. Per-call cost climbs ~40 -> 130 ns over a hold in both modes, so it is not the container.
Next: what that drift is (NEXT.md).
**s7023 stream loop split (tools/apply_s7023_calleetime.py, same switch ROGUESQ_S7022_ST=1, same recipe, 0 crashes; path counts sum exactly to cells):**
callees 55-60% / self 40-45%: getGridCellValueAt 96-120 ns/call = 41-48% of the loop (largest term), processGridCellByDistance 31 ns/call 12-14%,
call-path inline 74-81 ns/cell, skip cells 33-38 ns. 75-78% of cells take the call path (H-skipmix refuted), 0 rejects. Ceiling of a fix here ~0.7 ms/frame. Next: NEXT.md.
**s7022 stream walk is linear (ROGUESQ_S7022_ST=1 per-call timer, tools/apply_s7022_streamtime.py, same-run tog3 8192/10240, L1 dd6 21:9 WIDEWIN, 0 crashes):**
streamTerrainGridCellsByDistance runs once per frame, setup 0.5 us, loop 1.38 ms at 8192 cells / 1.69 ms at 10240 (inclusive of its two callees),
171 ns/cell flat at both caps: H-superlinear refuted, every window cell is walked every frame. xctrace put 62% of the function's samples on
0.5 us of setup code: per-line xctrace splits inside big recompiled functions are attribution artifacts, do not act on them. Next: NEXT.md.
**s7021 G1c per-cell cost named (per-frame xctrace split of the s7020 dd6 cap toggle, tools/xctrace_phase_split.py, 50 paired triples, 0 crashes):**
+2048 cells = gfx thread +1.72 +-0.22 ms/frame (= TL rsp +1.72; A/A +0.05): ucode self +0.70 spread over L_1F98/pre/L_1090/L_162C/L_16B8/L_1298/L_1740,
DPC submit +0.68 (bridge self 0.24, RT64 submit_rdp_range 0.23, record_submit 0.16); game thread +0.91 (= TL run +0.93): streamTerrainGridCellsByDistance
+0.31 (largest single term), renderFlatMeshFaceGroup +0.15. A per-SECOND split reads ~0 by construction (cells cut fps in the same ratio): split per frame.
Change, default on: the e9prov route counters (ovl_route & 4 more) are gated out of the owner ucode (ROGUESQ_E9PROV_FORCE=1|tog restores); same-run
tog A/B at dd6 cap 10240: rsp -0.14, T -0.42 ms/frame (51.0 vs 49.9 fps; shift control rsp -0.01), ovl_route samples 0 vs +0.22 ms/frame. Next: NEXT.md.
**s7020 G1c dd6 cell-cap split (same run, tog3 caps 8192/10240/10240, L1 21:9 WIDEWIN owner path, 0 crashes): H-cells.** cap 8192 59.2 fps rsp 12.42 run 3.10
(= dd4), cap 10240 52.1/52.6 fps, rsp +1.73/+1.60, run +0.74/+0.66; A/A null p2-p1 rsp -0.14; 1 s shift relabels, 0.5 s smears. The dd multiplier
itself costs ~0 at fixed cells. Binding limit above dd4 = per-cell cost (~0.85 ms rsp + 0.35 ms run per 1000 cells). Next: profile split by cap phase (NEXT.md).
**s7019 G1c dd>4 headroom (L1 21:9 WIDEWIN owner path, separate runs, 0 crashes x3):** dd4 59.5 fps (rsp 12.6), dd6 55.8 (rsp 13.9, P(>=2VI) 0.07),
dd8 53.3 (rsp 14.0, P 0.13). Above dd5 the cell pool is clamped (main.cpp rs64_g1c_apply_dd_policy POOLX<=5 = 10240 cells): dd6 and dd8 place the same
128x80 window (trace 17), pool never exhausted (site 18 = 0), so dd8 adds ~2.5 fps of cost and no terrain cells (cost source unnamed: dd-multiplier-scaled).
dd4 stays the top 60 fps owner setting. Next: same-run cap split at dd6 (NEXT.md).
**s7018 gfx-host-glue closed:** on the xor8 split the live record_submit walks (pillar+fused rect_wrap+tail) cost rsp 0.45 ms/frame
(G2 GLUE_TOG=1; walk timer 0.23 ms/frame), the s7016 fusion saves 0.26 ms (F2; timer 0.15), A/A null +0.08 (N3, reproduces N2), all in rsp, rdp/dpc 0;
L1 21:9 dd4 WIDEWIN owner path 59.3-59.9 fps, 0 crashes x3. Glue is 2-4% of a ~12.6 ms gfx task: trimming is done. Next: G1c dd>4 headroom (NEXT.md).
**s7017 tog split de-biased:** the s7010 odd-second bias is the harness autopilot's 2 s press cycle (a, sl, a, sr = 8 s cycle; 4 s rsp
component 0.4-0.9 ms in 8/8 rings), not the tool or the game. New split xor8 = (sec ^ sec>>3)&1 (rs64_tog_odd, default; ROGUESQ_TOG_SPLIT=parity
old) cancels any 8 s-periodic load. Same build: A/A null rsp +0.08 ms (parity on the same frames +0.73); positive control WIDEWIN=tog L1 21:9 dd4
rsp +3.50 ms, fps 60.0/59.6 (s7015 parity said +4.21, 58.1), 0 crashes. g5e_cost_by_parity.py reads split= from the anchor. Older parity deltas
under ~1 ms remain unreadable; re-measure with the new split.
**s7015 WIDEWIN owner-path cost on other levels/aspect (same-run tog, FAST=1 PROBES=0, dd4 MELT CULL=1, 0 crashes, 0 VI stalls, 320 s holds):**
L15 21:9 fps 60.0/60.0 (rsp +1.95), L4 16:9 59.7/59.6 (rsp +2.34), L1 21:9 60.0/58.1, P(>=2VI) 0.00/0.03 (rsp 9.27->13.48, +4.21: the densest arm);
0.5 s-shifted controls collapse (|rsp| <= 0.5). WIDEWIN is offered in OWNER-OPT-INS; default stays the owner's call. Next: trim the gfx-thread host glue (NEXT.md).
**s7014 WIDEWIN costs no fps on the owner's path; s7010-s7013's VI cliff was the harness.** m6_god_common.sh sets ROGUESQ_LOG_PHASE,
which turns G1E_FAST off and G1E_PROBES on (main ucode TU, slow DMA). Same-run tog3 caps 4096/6144/8192 with FAST=1 PROBES=0
(21:9 dd4 L4, MELT, CULL=1): fps 58.9/59.9/60.0, P(>=2VI) 0.00, rsp 8.8/10.4/11.1 ms (vs 13.6/15.6/16.9, 57/37.5/35 fps probes-on);
second run WIDEWIN=1 cap 8192 fixed: ~58.5 fps, P 0.01-0.04, rsp 11.4-11.9, 0 crashes. New harness switch OWNER_TIMING=1 (use for every
timing arm). Gfx-thread profile at 21:9 dd4 (xctrace + new tools/xctrace_ucode_blocks.py / xctrace_fn_lines.py): ucode self 41%,
DPC_END at L_1198 -> rsp_dpc_submit_impl 34% (RT64 RDP decode 16%, our bridge self 8% + rs64_dpc_record_submit ~12 full-stream scans 7%).
**G5i fixed s6995, awaiting the owner's look:** the hangar fish-eye after an abort was our s6907 aim
releasing onto the retail view on a fixed 3.85 s clock; scrolls over more distance or chained presses (4.8-6.7 s, likely
after re-entry because the cursor starts on another craft) were handed back mid pan (craft 23-31 deg off axis). Release
is now keyed on the raw view reaching the craft (ROGUESQ_G5G_RELMODE=time = old). Same-build A/B <=4.5 vs 22.8/31.1 deg.
Stale statics / re-entry RAM refuted (re-entry identical to first entry on equal scrolls). Sheet docs/owner_sheet_s6995_g5i_reentry.png.
s6997: holds at the owner's FULLSCREEN dd2 and dd4 (all scrolls <=4.5 deg; same-build RELMODE=time control 22.8/31.1);
sheet docs/owner_sheet_s6997_g5i_fullscreen.png. s6999: holds at 21:9 dd2 and after an abort from level 14 (all <=4.5 deg,
incl. 6.9 s scrolls; RELMODE=time control 22.8/31.1 at 21:9); sheet docs/owner_sheet_s6999_g5i_219.png. Nothing left to run.
**s7000 G5b:** FWDWIN far-loss fix also holds on L7 at dd4 (armed dips 36 -> 0, ring 5/6 dips 61/77 -> 0/3, near unchanged,
site-15 control 5868/5976 odd vs 100/5998 even); L10 has no terrain in flight. Next steps 3.
**s7001 G5b ring 7 closed:** the armed outer-ring dips sit on AXIS headings (0 near diagonals, 5 arms), the 64-cell window edge
stepping across the ring-7 boundary (56 cells); extra terrain the old clamp never drew, not a loss (tools/g5b_ring7_discrim.py).
**s7002 G5f short lines:** W_SHEET_PX 200 -> 40 same run (ROGUESQ_W_SHEET_ALT) ADDS lines under 60 px (20-39 px 605 -> 1096, 9/10 windows,
~= the 627 extra drops): kept clamped 40-200 px tris are real slivers; 200 stays. 18 viewed 20 px+ lines at dd4 L4 are all real motion (tools/g5f_short_buckets.py).
**s7003 G5f dd1 closed:** same-run W_CLAMP=tog at dd1 L4: clamp ON has fewer short lines (20-39 px 649 off -> 305 on, 100+ 47 -> 7, on below off in 5/5 windows,
control 87%); viewed clamp-off long lines are knife lines. s6895's 306-vs-157 belonged to the old area rule. Default on at dd1 stands.
**s7004 G5f dd2 L7:** two same-run W_CLAMP=tog captures (flight frames only; the autopilot crashes ~75 s in, later frames are menus): 100+ px lines
22 -> 9 and 8 -> 3 off -> on; short-line counts follow scene content (run 1 on lower, run 2 on higher = HUD reticle in odd seconds), not the clamp.
New ROGUESQ_W_SHEET_DROPLOG=<path> (rt64): 23 in-flight drops matched to frames, 0 visible holes. L7 clamp-off long lines are mostly bolts (knife lines rare here).
**s7005 G5f owner sheet (dd4 L4 16:9):** docs/owner_sheet_s7005_g5f.png (tools/g5f_owner_sheet.py). 100+ px lines off -> on 145 -> 26 (T40), 252 -> 34 (T20, catches the
faint dotted lines); 0 of 24 viewed clamp-on candidates are knife lines; solid and dotted knife lines seen only in clamp-off seconds. Toggle-edge frames
(VI phase < 0.05) were rendered in the previous second: never count them for W_CLAMP=tog arms.
**s7006 G5f 21:9 dd4 L4:** 100+ px 170 -> 57 (T40), 243 -> 59 (T20), controls 91%/76%; 0 of 29 viewed clamp-on events are knife lines (far-terrain edge,
bolts, buildings), the 6 longest clamp-off are knife lines. Sheet docs/owner_sheet_s7006_g5f_219.png. G5f now closes on the owner's look at 16:9 and 21:9.

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
  (docs/REGEN-VERIFY.md). N64Recomp self-branch miscompile not fixed, H-dead on missions 1-2 (s6878).
- **Present thread (s6884-s6891, s6931):** SCREEN_JOB, PRESENT_INFLIGHT, PRESENT_DRAIN opt-in/off;
  true-60 Hz latency levels are sticky in whole vsyncs.

## Superseded conclusions — do not act on these
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

Spec: ITERATION.md item 3c. No backlog-exhausted block. Owner order: G5i (fixed, owner look), then the rest; tog split de-biased s7017 (xor8); gfx-glue closed s7018 (walks 0.2-0.45 ms/frame); dd6/dd8 measured s7019 (55.8/53.3 fps, cells capped px5); s7020 dd6 cost = cells (H-cells, multiplier ~0); s7022 stream walk linear 171 ns/cell; s7025 clamp drift = our create hook double-updating the std index, fixed (create 6.5 us -> 218 ns); s7026 DPC submit = RT64 per-byte + ~21 ns/bump bridge, wait flat; s7027 per-bump checks only ~3.6 of ~24 ns (H-checks refuted); s7028/s7029 bridge split closed (H-call, shadow refuted); s7030 fogged-cell cull: H-fogwaste refuted, 0.5 x fog-end depth cull = rsp -4.9 ms invisible on L1 (H-offmap lead); s7031 off-map census: 82%/62% of dd6 cells off-map, R=2 cull rsp -9.75/-3.71 ms (L1/L4), image unqualified; s7032 frozen poses: R=2/R=8 VISIBLE once the eye climbs above the off-map plateau (H-plateau); s7033 height gate image-neutral but saves 0 ms (H-costgone, eye above edge tops almost always); s7034 off-map past 0.6 x fog end: ~invisible at 7 poses, rsp -3.04 ms -> 60 fps on L1 (H-fogdepth); active unit: NEXT.md (L4 repeat).

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
7. **G5f knife lines: fixed s6906; owner flight.** Lines < 60 px at dd4 L4: real geometry, W_SHEET_PX=200 confirmed (s7002). dd1 closed s7003 (clamp halves transients, removes knife lines). dd2 L7 s7004: long lines fewer, drops leave 0 holes (DROPLOG). Owner sheet s7005 docs/owner_sheet_s7005_g5f.png (dd4 L4: 0 clamp-on knife lines in 24 viewed). 21:9 dd4 s7006: 0 clamp-on knife lines in 29 viewed, sheet docs/owner_sheet_s7006_g5f_219.png. Nothing left to run; owner look.
8. **G5g hangar stretch: done s6907** — superseded in priority by item 1 (re-entry failure).
   Owner decides on flight and cutscene lens (report sheet docs/owner_sheet_s6907_lens_elsewhere.png).
9. **G5h cutscene background: closes on the owner's look.** Intros s6908, playlist s6909, scene
   s6910, floating triangles s6911, far band s6919; DD_MELT, DD_SKYZ, DD_CUT_LIVE opt-in, owner chooses.
10. **L15 21:9: owner re-flight after s6992 PTRMASK.**
11. **G1e residual: CLOSED s6996** (in flight 59.7-60 on all levels; the shortfall was non-flight time).
    Use fl_shown/fl_miss, not shown/s, for per-level fps. Open, owner scope: why L7/L16/L17 autopilot holds cycle the backdrop menu.
12. **G1d close-out awaiting owner judgement** (scratch/s6731/sheet_menus_owner.png).
13. **Owner judgement / parked:** FPS60 feel, G3c sheets, QoS default, native hangar geometry,
    rare dd4/dd8 gfx SIGBUS (single-source). Reopen on an owner report or side-effect failure.
14. **(PARKED by owner) G1(d) objective qualification.** PORTING-STATE s6640-s6687 first.

## Evidence index

- s6994 maintenance archive (whole s6993 CURRENT-TRUTH verbatim): PROJECT-OVERVIEW.
- s6982 (s6964/s6965 present level), s6962 (G1e thread s6935-s6961), s6926, s6924, s6918, s6917,
  s6915, s6914, s6912, s6909 trims: PROJECT-OVERVIEW "Migrated from CURRENT-TRUTH (sNNNN)".
- s6900, s6847, s6759 maintenance archives; [Maintenance s6667 retained evidence](PROJECT-OVERVIEW.md#maintenance-s6667-retained-evidence).
- Objective contracts [G1-OBJECTIVE-RESPONSE](G1-OBJECTIVE-RESPONSE.md); images [G1-FRAMEBUFFER-COVERAGE](G1-FRAMEBUFFER-COVERAGE.md).
- Queued-soak verdicts: `scratch/agent/SOAK-RESULTS.md`; latest s6980_219_async_noqos_r1/r2 (folded s6981).
- Recent chronology: PORTING-STATE sessions 6893-6994; search bounded windows only.
