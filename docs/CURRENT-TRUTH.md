# Rogue Squadron 64 Recomp — current truth

Compact operational handoff, as of Session 7003 (2026-11-08).
`PORTING-STATE.md` is the chronological ledger; durable and migrated material lives in
`docs/PROJECT-OVERVIEW.md`. The full pre-compaction text of this file (s6893-s6993 headline
bullets with every number, superseded list, G1e chronology) is archived verbatim in
PROJECT-OVERVIEW "Migrated from CURRENT-TRUTH (s6994 maintenance)" — grep there for any sNNNN.

## Headline

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

Open or awaiting the owner (each one line; detail in the s6994 archive under the session):
- **s6992 FIXED, default on: L15 21:9 dd4 crash.** ORIGIN ours: the game's pointer test
  `(p & 0xFF000000) == 0x80000000` (7 sites) rejected the 0x81000000 spill arena, a TLUT pointer
  became slot id 0x1058 and overwrote the material pool. tools/apply_s6993_ptrmask.py,
  ROGUESQ_PTRMASK=0 = retail mask. Same-binary control crash / fixed 200 s at 21:9 and 16:9.
- **G1e game fps per level (dd4 FPS60 VI_LOCK QOS_ALL, flown level checked): 60 in flight on all levels.**
  s6996: in-flight seconds (tools/g1e_level_fps.py fl_shown) L16 59.7, L17/L7 59.9, rest 59.8-60.0; C30 control 30.0.
  The s6993 L7/L16/L17 56.3-58.5 was menu/restart screen time inside the window (backdrop menu 16x, wl=0 presents).
- **G1e latency/present chain s6962-s6989, all closed:** defaults on ROGUESQ_VI_RT (s6967, VI
  thread time-constraint policy), STDERR_ASYNC (s6979), G1E_CELLIDX at dd>1 (s6963); opt-ins
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
Recent only; older entries: PROJECT-OVERVIEW "(s6994 maintenance)", "(s6900 maintenance)", "(s6870)", "(s6759 maintenance)".
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

Spec: ITERATION.md item 3c. No backlog-exhausted block. Owner order: G5i (fixed, owner look), then the rest; active unit: G5f dd2 on L7 (NEXT.md).

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
6. **G5e fog: done s6904; owner look.**
7. **G5f knife lines: fixed s6906; owner flight.** Lines < 60 px at dd4 L4: real geometry, W_SHEET_PX=200 confirmed (s7002). dd1 closed s7003 (clamp halves transients, removes knife lines). Open: dd2 / a second level (NEXT.md).
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
