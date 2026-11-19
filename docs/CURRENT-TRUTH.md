# Rogue Squadron 64 Recomp — current truth

Compact operational handoff, as of Session 7649 (2026-11-19).
`PORTING-STATE.md` is the chronological ledger; durable and migrated material lives in
`docs/PROJECT-OVERVIEW.md`. The full s7416 text of this file (every audit class AQ-BZ s7373-s7416 with all numbers,
controls and tool flags) is archived verbatim in PROJECT-OVERVIEW "Migrated from CURRENT-TRUTH (s7417 maintenance)"; item-1 classes DG-EO in "(s7491 migration)"; classes CC-DH s7420-s7451 in "(s7452 maintenance)";
s7315-s7369 classes in "(s7370 maintenance)"; the s7306 headline chronology in "(s7307 maintenance)"; older text in
"(s7187 maintenance)" and "(s6994 maintenance)"; s7533 Next-steps items 1,12,15-21 (classes FD-FZ) in "(s7534 maintenance)"; s7535-s7576 headline + items 17-21 + pre-s7300 superseded in "(s7581 maintenance)"; s7579-s7616 headline + items 19-46 in "(s7622 maintenance)". Grep there for any sNNNN.

## Headline

**Every engineering goal on the ladder is closed or awaiting the owner's look.** Nothing is broken at the
owner's recipe as far as any instrument can see; remaining items are owner judgements (list in Next steps).

- **NEW s7649: MK8 conclusion re-validation: 1 alias artefact, 0 standing conclusions reopened.** s6230/s6231 [g1d-tex]
  (w900 OSMEM 12) hashed/dumped `& 0x7FFFFF`-aliased low RAM for EVERY photo tile (true src >= 8 MB: s6235 1407/1407, s7649
  3017/3017); "parse-time bytes noisy" was the alias. The thread closed on the s6243 skip bisect, untouched. [g1d-tex] now
  keys 16 MB (+tex8= old key). s7391 BA safe by data (all stacks < 0x806F9BA0). Census misattributes some sites (s7650).
- **s7648: class MK8 (8 MB address keys/bounds at dd>1) CLOSED, H-mk8-diag-only, 0 fixes** (item 33,
  docs/MK8-KEY-ALIAS-CENSUS.md, `python3 tools/s7648_mk8_census.py --controls`). No default-on lookup aliases dd>1 data.
- **s7647: TS-4 CLOSED as an instrument artefact (H-alias8); H-slot-recycle withdrawn.** The s7645/s7646 key was `& 0x7FFFFF`
  but the RSP DMA mask is 25-bit (0x1FFFFF8) and the dd>1 bundle puts TriGen chunks above 8 MB (0x9950A0 aliased the MusyX stream
  buffer 0x195190). True-key L4 dd4: rd_after_pi 0, stale 0; same run alias8 4881 (= s7646's 4912); old-key arm 4876 (item 32).
- **NEW s7620: G6b F6 Controls panel LANDED (owner to try).** RT64's F1 inspector has no Metal backend, so the panel has
  its own ImGui context drawn through RT64's public post-VI hook (RT64::SetRenderHooks) with imgui_impl_metal; closed = hook
  returns, nothing encoded. Same run (PANEL_TEST): defaults 0 mismatches, scripted bind A=pad:b 112 (control), capture took
  key:E, Reset 0, panel open 0 (600 polls); json roundtrip ok; Save skipped under NO_SAVE_WRITE. Screenshot scratch/s7620/panel.png.
- **NEW s7617: G6a rumble LANDED, default ON (`ROGUESQ_RUMBLE=0` = old no-pak shape, `ROGUESQ_RUMBLE_SCALE` 0..2); owner to feel it.**
  src/main/main.cpp: port 0 reports a Rumble Pak; set_rumble records motor edges, poll_input (owner of `controller`) turns the
  100 ms on-fraction into s = (0.25 + 0.75*duty)*scale and sends SDL_GameControllerRumble(lo=s, hi=0.6s, 150 ms), refreshed
  every 50 ms, cancelled at duty 0. Proof (scratch/s7617, L4 dd1, same build): virtual test pad (ROGUESQ_RUMBLE_TEST=1, its
  Rumble callback = witness) got 14 calls from the game's own 4 osMotorStart at t=84.6 plus 20 from the 1 s injected train;
  RUMBLE=0+PAK_SHAPE_CTL=1 arm: same 4 Start/7 Stop, 0 pad calls. Saves: dev=1 (EEPROM) throughout. **s7638 closed both open
  items:** the virtual pad's rc=-1 was a test artefact (sdl2-compat reads the SDL2 Rumble callback's int 0 as SDL3 bool
  false; scratch/s7638/vpad_rc.c: cb 0 -> rc -1, cb 1 -> rc 0; cb now returns 1, gc arm sdl_fail 0/19); and a fallback chain
  SDL_GameControllerRumble -> SDL_JoystickRumble -> SDL_Haptic landed (advance on failure, 5 s re-probe after all fail,
  `ROGUESQ_RUMBLE_FORCE_PATH=joy|haptic` = control: joy 18/18 delivered, haptic on the non-haptic vpad -> path=none, 0 delivered).
  Game rumble is sparse (L12 130 s: none; L4: one burst at mission start).
- **s7579-s7616 host-side idiom-class audits: ALL CLOSED** (full text, numbers, controls, tool flags verbatim in
  PROJECT-OVERVIEW "(s7622 maintenance)"). TS-2 s7643 (TSan over host runtime, item 30): 1 hardening (s4211 PI ring), SEM blind spot now annotated. TS s7642 (TSan over all RT64+plume, item 29): H-clean, 0 fixes. CF s7641 (framework-callback threads, item 28): 1 fix (plume Metal drawable index race, TSan). AT s7640 (AppKit thread affinity, item 27): 1 fix (RT64 NFD_Init on Gfx Thread). ST s7639 (SDL thread affinity, item 26): 1 fix (F6 panel draw hook). H-clean, no fix: HB s7633 (bridge default-on diag, item 23; 1 getenv latched), HD s7632 (rt64 default-on diag work, item 22; 2 getenv latched), RP s7631 (lib/rt64 kept RDRAM pointers, item 21), RQ s7616, DQ s7615, HM s7614, HP s7613, RG s7612, SN s7611,
  OV s7610, MK s7609, HC s7606, RX s7603, TP s7602, TH s7592, OW-2 s7588, HR s7589, UI s7584, UBSan s7579-s7583 (every
  C-applicable check run; RS64_DIV32). Bounded/gated/masked: GR s7599, GX s7600, BS s7601 (5 diag composers fixed), AZ s7598
  (ROGUESQ_S7598_MASK=0 = old). Fixes landed, default on, =0 restores old: TK ROGUESQ_S7608_TK, UW s7607 (one fix), FR s7605 /
  RA ROGUESQ_S7604_ALLOC (dead-path), XC ROGUESQ_S7597_MODSCAN, FS ROGUESQ_S7596_RM, SV ROGUESQ_S7595_DIRS, SG ROGUESQ_S7594_SIG,
  EX ROGUESQ_S7593_MAINQUIT / _UQ_EXIT, MR ROGUESQ_S7591_HOSTPORT, HR-2 ROGUESQ_S7590_THRPORT, OW ROGUESQ_MTL_OWN, LK leaks
  ROGUESQ_MTL_WAITPOOL (s7585) + dispatch_data (s7586), LU s7580. **Hazard (s7616): never LAUNCH the game under lldb** (it tried
  to delete the ROM; EPERM saved it); attach to a normally started pid. New build dirs need a COPY of build/saves.
- **s7535-s7576 (classes GA-GR, regen health 19b, compensation chains 19c/19d, S6892, GUARD-6, do_break, float->int): ALL CLOSED.**
  Full text verbatim in PROJECT-OVERVIEW "(s7581 maintenance)". Landed defaults: RS64_DIV32/DIVU32 (s7575), RS64_TRUNC_W_S/D (s7576),
  tools/rs64_anchor.py regen fix (s7558), regen_replay "ok" (s7560). Opt-in fixes: ROGUESQ_SP_LATE=1 (GA s7535-s7537),
  ROGUESQ_RDP_NODRAIN=3 (GB s7540; OWNER-OPT-INS row). Owner decisions from them: M5_B40_VALUE (s7558/s7564), SP_LATE. Censuses
  docs/COMPENSATION-CHAINS.md (122 rows, 0 UNKNOWN) and docs/DEFAULT-ON-LEVERS.md (s7557). No default flipped.
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
- **s7645/s7646 "gfx tasks read display-list bytes that PI DMAs refill mid-task at dd>1 (L4 4912/120 s); H-slot-recycle" (superseded
  s7647).** Believable: controls fired, dd1 arm read 0, and the issuer/ROM offsets were coherent. But both sides were keyed `& 0x7FFFFF`
  while the RSP addresses 32 MB and dd>1 data lives above 8 MB: true-key overlap 0, alias-only overlap 4881 in the same run.
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
- Pre-s7300 superseded entries (s6445-s7288, 27 lines) moved verbatim to PROJECT-OVERVIEW "(s7581 maintenance)"; grep there.
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
- Public forks (owner, 2026-11-18): loop.sh runs `tools/agent/publish_forks.sh` between iterations; it pushes `autonomy` to
  fyreatwill/RogueSquadron64Recomp (fast-forward only) and mirrors N64Recomp tool source + decomp tracked files to their `rs64`
  forks. Never commit ROM-derived data (*.z64, ucode/RDRAM dumps, RecompiledFuncs) or files > 50 MB, and never rewrite history,
  or publishing stops (`scratch/agent/PUBLISH-BLOCKED.md`). `tools/build-from-scratch.sh` is the public build; keep it working.
- Read `docs/F5-UCODE-REFERENCE.md` before interpreting Factor 5 streams. Positive control for every null; two
  independent lines before a conclusion enters this file.

## Next steps (single monotonic backlog)

- **Ladder item 4 REVISIT has no open target (s7638):** the rename sweep is CLOSED (item 19), the M4 accumulator boundary is
  CLOSED (s5354: cxd4 LLE retail shows the same transient 0x8000 lanes in every hangar task, docs/REVISIT-S5354-M4-RETAIL-PCS.md)
  and the external retail-entry boundary is CLOSED route-absent (s4845). Do not schedule a revisit; take an owner item or G-rung.

Spec: ITERATION.md item 3c. No backlog-exhausted block. Renumbered s7534 into one sequence 1-18, s7622 folded 19-46 into 19 (1-21 now) (the s7533 numbering 1-22 is archived
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
    after a regen run tools/s7610_ov_census.py --controls + tools/scan_selfbranch.py + the s7407-s7419 emission tools with --controls (rc 0); after a ucode regen tools/ucode_regen.sh verify
    + tools/s7507_rsp_ctrl_flow.py + s7508_rsp_scalar_gaps.py + s7509_rsp_vec_operands.py; after a save/files.cpp edit tools/s7595_sv_census.py --controls + --harness; after a librecomp/ultramodern
    replacement change tools/s7527_host_replace_audit.py --controls; after any new host writer into guest RAM tools/s7542_gc_census.py; after a src/main static/hook change tools/s7548_gh_census.py; after a threads.cpp/recomp.cpp thread-entry edit tools/s7606_hc_census.py --controls; after a new host queue / std::thread / pending-list tools/s7615_dq_census.py --controls; after a fixup/apply script edit tools/s7549_gi_census.py --controls; after an RT64 fullSync/framebuffer-manager edit tools/s7550_gj_census.py --controls; after a librecomp/ultramodern getter or a new os*_recomp import tools/s7555_go_census.py --controls; after a scheduler/replacement or injected-yield change tools/s7543_gd_census.py --controls and tools/s7546_gf_census.py --controls; after a new host-retained guest pointer (osSetEventMesg-style registration) tools/s7547_gg_census.py --controls; after a class-touched function change, its class scorer.
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
17. **Classes GA-GR + 19b/19c/19d + S6892/GUARD-6 + do_break/float->int (s7535-s7576): ALL CLOSED** (verbatim in
    PROJECT-OVERVIEW "(s7581 maintenance)"). SP_LATE AC repeat DONE s7637: L12 dd4 ABBA x2 on AC holds 60.0 gen/s in both settings
    (8/8 alive, scratch/s7637_splate_ac), so it costs nothing on AC; the battery-only CPU-bound case stays unresolved and does not matter to the owner. Regen trees: tools/regen_front.sh D/pristine; cp -R D/pristine D/replay;
    tools/regen_replay.sh D/replay; tools/regen_verify.sh D/replay D/verify.
18. **After-regen UB gates (all CLOSED, rc 0 expected):** tools/s7575_ir_calls.sh + `tools/s7575_break_census.py --controls --ir D`
    (BLIND=0); `python3 tools/s7576_trunc_census.py --controls` (FOLDED=0); after a ucode regen or rsp*.hpp edit
    `tools/s7577_ubsan_sites.py <tu> --check` per ucode TU (UNCLASSIFIED 0) + `tools/s7577_ucode_ub_census.py scratch/s7577`;
    tools/s7580_lui_identity.py (0 object diffs). UBSan builds: `env SAN=<checks> B=<dir> zsh tools/build_ubsanc.sh`, scorer
    tools/s7579_bounds_report.py, plants ROGUESQ_S7578_PLANT=1-6,u (SANREC for non-recoverable checks). s7578 null/wrapv, s7579 bounds, s7580 shift/align, s7582
    pointer-overflow, s7583 div0/fcast/bool/builtin/vla/nonnull/unreachable CLOSED: every C-applicable UBSan check has run.
19. **Rerun-after-change censuses s7579-s7616 (all CLOSED; per-class trigger text verbatim in PROJECT-OVERVIEW
    "(s7622 maintenance)").** Each `python3 tools/s76NN_<cls>_census.py --controls` must exit 0 after an edit in its scope:
    RQ/DQ s7616/s7615 (lib/rt64 RDRAM reads, new threads; a worker-thread RDRAM reader needs a command-time copy or a gate),
    HM/HP s7614/s7613 (--ast; statics), RG/SN/MK s7612/s7611/s7609 (--witness; regen, statics), OV s7610 (regen, overlays.cpp),
    TK s7608, UW s7607 (throw/catch, blocking calls), HC s7606 (threads.cpp/recomp.cpp), FR/RA/RX s7605/s7604/s7603 (host code
    touching guest regs/FPRs), TP s7602 (TO_PTR views), BS s7601, GX s7600, GR s7599, AZ s7598 (allocations, createTexture),
    XC s7597 (throw/json parse), FS/SV/SG s7596/s7595/s7594, EX/TH s7593/s7592, MR s7591 (lib/ edits). OW/OW-2/LK/HR
    s7585-s7589 tools as named in the archive. Renaming sweep closed (s6868). ROGUESQ_MTL_WAITPOOL default on.
20. **G6 (owner 2026-11-18, ahead of everything else): G6a rumble LANDED s7617; G6b controls LANDED s7618-s7620 (table
    src/main/rs64_bindings.h == old map, ROGUESQ_BIND_OLD=1; controls.json beside the exe, rs64_bindings_json.h; F6 panel
    src/main/rs64_controls_panel.cpp + rs64_imgui_metal.mm, ROGUESQ_CONTROLS_PANEL=0 removes it). Both close on the owner's
    hands. Rerun `ROGUESQ_BIND_PANEL_TEST=1` (scratch/s7620/run.zsh) + tools/test_bindings.cpp after any input-path edit.
    G6c stand-ins: design docs/G6C-STANDINS-PLAN.md (s7621): H-portable (game-side visibility bucket only, no HLE state),
    all 17 upstream code addresses identical in our syms. Step 2 LANDED s7623: src/main/rs64_standins.cpp +
    tools/apply_s7623_standins.py (RS64_REPLAY), ROGUESQ_STANDINS=1|tog (+_LOG=1), dd>1 only; region 0x81700000..0x81800000
    (spill capped 7 MB; matrices reach the DL pool via a stack copy, so CPU-only). L1: 47 objects, submits > 0 at dd2/dd4,
    0 at dd1, 3/3 arms alive 0 stall (single run, on battery). **Step 3 (s7624): H-culled.** The game's own view test
    (transformVec3ToNpcLocalWithScale 0x8001DC34, inside addNpcToVisibilityBucket, which returns 1 only when linked; the bucket is
    a linked list with no cap, so H-budget-at-bucket is refuted by code read) accepts 0.2% of stand-in submits (L1 93/40018,
    L4 361/151825); only 2/9 (L1) and 10/59 (L4) later spawns were ever accepted before spawning (0.5-4.2 s early). Per-frame
    toggle fb dumps: flicker per triplet toggling <= forced-off control (L1 3879 vs 4351, L4 1807 vs 2207), synthetic control
    PASS. The s7621 "no far_check port needed" was wrong: upstream widens that test's far ($f0 *= dd, 0x8001E078) and its
    +-125 camera box (0x8001DCEC/0x8001DD38, constants 0x8000093C/940) and relies on RT64 HLE far matrices for translations past
    convertMat3x4ToN64Mtx's reach; we have neither. **Step 3b (s7625): H-far selected, fixed at the bucket; the draw path culls next.**
    Exit tally (tools/apply_s7625_viewtest_reason.py; exits sum to calls): in-front stand-ins die at the far exit 0x8001DDA8
    (view+0x28 = 30.8 L1 / 27.8 L4 at dd4 = the retail object far; stand-ins sit at d 40-110), then side; box +-125 rejects
    ~3%. Fix tools/apply_s7625_standins_far.py: far *= ROGUESQ_STANDINS_FAR (default dd; =1 retail, =tog) for OUR call only;
    the box test runs first so no matrix overflow is possible. Same-run tog: pass rate L1 0.41% -> 29.6%, L4 0.47% -> 24.2%,
    far rejects 9021 -> 0 / 27996 -> 27, 4/4 arms alive 0 stall. But fb flicker with far on still shows nothing (L1 4068 vs
    4206 off, L4 1813 vs 2129, control PASS, 294/255 accepted in window 1). **Step 3c (s7626) supersedes "accepted stand-ins
    are not drawn": that window had no stimulus.** Stand-ins never use selectMeshLodAndSubmitForRender (probe droids only), so
    upstream's 0x80058264/0x80058304 hooks do not apply. tools/apply_s7626_sg_probe.py (ROGUESQ_STANDINS_LOG=1, other nodes as
    control): traverseSceneGraphRecursive visits/converts them (L1 81591 in 130 s, cam z 42-121, packed t < 2^31); their meshes
    are prebuilt-DL (flags 0x00100018, same as most real objects) and queue mesh+0x34 at 0x80116400; beginFrameDLChunk reads
    100% of those entries (65390/65390). The dump windows (40-46 s after first submit) held ~0 stand-in draws (L1 0, L4 ~60/s
    for 2 s); they draw at 9-19 s. **Step 3d (s7627): stand-ins DRAW RDP pixels.** L1 dd4 STANDINS=frame, dumps 10/16 s,
    flicker px/triplet window1 vs forced-off window2: P (PULL=3) 1071 vs 107.5, N (true depth) 547 vs 108, real-object control
    C (ROGUESQ_STANDINS_CTL=1, real nodes collapsed on off calls, ours never added) 180891 vs 107.5; synthetic control PASS all
    arms, 3/3 alive 0 stall. **Step 3 proof by eye (s7628): stand-ins are visible early, true depth, on 2 levels.** Same-run
    adjacent-frame pairs (tools/s7628_standins_sheet.py, docs/owner_sheet_s7628_standins_on_off.jpg): L1 dd2 a far bunker in the
    haze; L4 dd4 a row of far city towers (1949 px) the game has not spawned yet. L4 dd2 shows none (flicker 143 vs 155 forced-off
    = inside the game's own spawn radius, expected). Flicker scorer alone is NOT proof: the s7627 N excess (547) and the s7628
    L1 dd4 top pairs are cliff-texture shimmer + laser bolts, not stand-ins (eye check); keep the eye check. Dumps show each call
    one swap late (stand-ins appear in label-0 frames). Spawns preceded by a stand-in: L1 10-11 (2-62 s early), L4 19 (0.2-5 s).
    4/4 arms alive, 0 fatal, 0 VI stall. **Step 4 (s7629): 300 s holds STANDINS=1 dd4 owner recipe, L0-L5 6/6 clean** (alive, 0
    crash, 0 VI stall, gap <=148 ms, stand-ins active per spawn lines); **s7630: L6-L18 also clean -> 19/19** (gap <=162 ms,
    spawns 13-360 per level). Owner row in OWNER-OPT-INS + sheet docs/owner_sheet_s7630_standins_on_off.jpg (cluster crops). **G6c now
    closes on the owner's look; default stays off.** Scorer
    now ranks by clustered diff px (`--cluster 16`, 8x8 blocks): bunker 153 / towers 1298 / shimmer 0 / none 0 median, control PASS;
    a window-2 shimmer map was tried and rejected (does not predict window 1). Then the owner sheet decides.
21. **Class RP (RDRAM-derived pointers kept in lib/rt64 across calls): CLOSED s7631, H-clean, no fix.** Regex
    (tools/s7631_rp_scan.py) + clang AST (tools/s7631_rp_ast.py) joined by tools/s7631_rp_census.py: 36 rows both, 3 ast-only
    explained, 0 OPEN (fresh 26, offset 6, gated 4 HLE-only, base 2, copy 1, host 1); planted OPEN / fresh / drop-row controls
    PASS. HLE-only = static defaults + 0 `[hle send_dl` vs 566 `[lle send_dl` in a s7628 300 s hold.
22. **Class HD (default-on diagnostic work in lib/rt64 per-list/per-command paths; NEXT said "DD", but s7447 owns DD): CLOSED
    s7632.** tools/s7632_dd_scan.py (regex) + tools/s7632_dd_ast.py (AST) + tools/s7632_dd_census.py (gate spread through calls, join,
    hand classes): 377 joint rows, 0 OPEN, controls PASS. Only copy rows: the s4281/s4282 list snapshot. Same-run timer
    (ROGUESQ_S7632_STATS=1): 0.82 / 1.03 ms/s at L1 / L4 dd4 = 0.37-0.43% of processRDPLists (which uses about 23% of a core at dd4,
    single-source), so **kept**. ROGUESQ_S7632_SNAP=0 skips it. Fixed: 2 per-call getenv in uploadTexture (UPSPAN, TMEM_ZERO) are
    now static latches.
23. **Class HB (default-on diagnostic work in src/rsp/dpc_bridge.cpp + rt64_render_context.cpp): CLOSED s7633, H-clean.**
    tools/s7633_hb_census.py (s7632 scan+AST with `--hot`, bridge hand classes): 0 OPEN, 0 copy rows, controls PASS. Same run
    (L1 dd4 16:9 FPS60, GLUE_TIME timer + `sample`, agree ~25-27 ms/s): all per-submit walker cost is functional (G1D_DEBRIEF pillar
    12.5, CULL_SPIKE 8.2, wide-aspect radar region shift ~6 ms/s, armed by main.cpp:14403 setenv). Diag leftovers each <1 ms/s.
    Fixed: per-commit getenv(ROGUESQ_TRACE_DISPATCH) latched.
24. **Walker fusion: LANDED + CLOSED s7635 (ROGUESQ_S7634_FUSE default 1; =0 old two walks, =tog same-run A/B, =chk/=inj check).**
    Spike + region bodies run per command in one walk (dpc_bridge.cpp rs64_region_scan fused -> rs64_spike_scan rb callback).
    Equivalence, same run (L1 dd4 16:9 FPS60, DD_SKYZ=1, 703M commands): shadow late-write check 0 live, 3 inert (op 2E DD_SKYZ
    late puts, predicted), injected 21/21 seen. Saving only ~0.75-0.8 ms/s (L1, L12 GLUE_TIME tog A/B), not the s7634 ~6:
    a standalone decode walk overstates what fusing removes. Further walker fusion (pillar) is not worth it.
25. **Spike body per-tri cost: CLOSED s7636, H-mem.** ROGUESQ_S7636_FASTSPIKE (default 0; =1 on, =tog, =chk) is an exact
    integer guard test (vertex coords are int64/2^18). chk L1 dd4: 0 disagreements / 90.2M tris, injected 22016/22016. tog A/B:
    saves 377 (L1) / 86 (L12) us per parity, ~0.2-0.75 ms/s, at A/A noise (pillar delta 63/-157): cost is the command loads, not
    the double maths. Walker per-tri cost thread closed; scratch/s7636/RESULT.txt.
26. **Class ST (SDL thread affinity vs SDL3 `\threadsafety` docs): CLOSED s7639, 1 fix.** `python3 tools/s7639_st_census.py
    --controls` (exit 0; rerun after any SDL call edit or new thread): 231 sites, preprocessor-aware, roots MAIN/GAME/PRESENT/GFX/
    WORKER, controls a/b/c/e PASS; 34 hand rows dead on macOS (ImGui SDL backend + setup paths; runtime sdlWindow=0x0). Live
    violation was the s7620 F6 panel hook_draw (present thread) calling SDL_GetWindowFromID/GetWindowSize; now update_gfx
    publishes the size (ROGUESQ_S7639_ST=0 old, =chk 0/215 mismatches, =chkp control 243/243). RT64 window checks use plume
    CocoaWindow (main-queue dispatch): safe.
27. **Class AT (AppKit calls off the main thread): CLOSED s7640, 1 fix.** Runtime witness = Apple's Main Thread Checker
    (`zsh scratch/s7640/run.zsh <tag> [ENV=..]`, DYLD_INSERT_LIBRARIES libMainThreadChecker, boot to F6 panel draw): before, 1
    report per boot, -[NSApplication activationPolicy] in NFD_Init <- RT64::Application ctor on the Gfx Thread. Fix (lib/rt64
    rt64_file_dialog.cpp, default on, ROGUESQ_S7640_AT=0 old): NFD_Init on the main queue (2 s bounded wait), NFD_Quit posted.
    Arms (same build): old+plant 2 reports (Gfx + plant), fix+plant 1 (plant only), fix 0. Static half
    `python3 tools/s7640_at_census.py --controls` (exit 0): 50 sites in 4 ObjC TUs + CAMetalLayer calls, controls a-d PASS; plume
    CocoaWindow all guarded, NFD dialogs dead (developerMode=0), rs64_display_mac main-only. Plant: ROGUESQ_S7640_AT_PLANT=1.

28. **Class CF (framework-callback threads: Metal handlers, SDL watch/vpad, dispatch, exit hooks): CLOSED s7641, 1 fix.**
    Witness = Thread Sanitizer on plume_metal.cpp only (`zsh tools/s7641_tsan_build.sh`, then `zsh tools/s7641_tsan_run.zsh <tag>
    RogueSquadron64Recomp_tsan [ENV=..]`): plume present()'s completion handler did a plain RMW of currentAvailableDrawableIndex on
    Metal threads (two threads seen) vs acquireTexture's read; now atomic CAS (lib/rt64 plume_metal, ROGUESQ_S7641_CF=0 old).
    Arms: old 18 reports (2 on the index), fix 16 (0); the 16 are metal-cpp __block std::function copies TSan cannot order
    (Metal handoff not intercepted), same in both. `python3 tools/s7641_cf_census.py --controls` (exit 0): 22 sites, controls a-d
    PASS. MTC regression with fix: 0, plant 1.
29. **Class TS (Thread Sanitizer over ALL of RT64 + plume): CLOSED s7642, H-clean, 0 fixes.** `zsh tools/s7642_tsan_rt64_build.sh`
    (99 of 101 rt64/plume TUs instrumented; optimus/shader_compiler compile empty on macOS) -> build/RogueSquadron64Recomp_tsan2;
    `zsh tools/s7642_tsan_run.zsh <tag> RogueSquadron64Recomp_tsan2 [ENV=..]` (boot, DUR=45), flight via g1e_owner_quiet_arms
    (GAME=./RogueSquadron64Recomp_tsan2, TSAN_OPTIONS exported); bucket with `python3 tools/s7642_tsan_bucket.py <tsan files>`.
    Boot: 28 reports / 3 sites (the s7641 blind spots); ctl S7641_CF=0: 30 / 5 (index pair back). L1 dd2 120 s flight
    (level_ok=1, vi_stalls30s=0): 52 / 6 sites, all Metal-handoff blind spots (registration/pre-commit writes vs handler reads);
    3 new sites are the PRESENT_RING Rs64SStamp init/`c` stamp vs its handlers. Scheduled->completed handler order held 3304/3304
    S rows (no use-after-free of the stamp). No report has an RT64 worker/state/texture race pair.
30. **Class TS-2 (TSan over the HOST runtime: ultramodern 15, librecomp 27, all 29 RogueSquadron64Recomp.dir src TUs, plus the
    s7642 rt64/plume objects): CLOSED s7643, H-clean for host-defects, 1 hardening.** NOTE prior art: s7354 class AE already ran a
    host TSan (tools/build_tsan.sh, tools/s7354_tsan_report.py HAND table); this pass re-derived it independently and agrees.
    `zsh tools/s7643_tsan_host_build.sh` (needs the s7642 archives) -> build/RogueSquadron64Recomp_tsan3; runner
    `zsh tools/s7643_tsan_run.zsh <tag> RogueSquadron64Recomp_tsan3 [ENV=..]`; bucket `python3 tools/s7643_tsan_pairs.py <files>`
    (function pair + creating-thread role + location). Control ROGUESQ_S7643_PLANT=1 (main.cpp plain counter bumped from update_gfx
    on main and get_n64_input on the game thread): reported 2/2 runs. NEW: lib/N64ModernRuntime thirdparty lightweightsemaphore.h
    annotates signal()=__tsan_release / successful wait()=__tsan_acquire under `__has_feature(thread_sanitizer)` ONLY (shipped
    binary unchanged): boot reports 1173 (32 pairs, ~1140 guest<->guest RDRAM thread/mesg queue = s7354 "SEM") -> 26 (6 pairs, all
    the s7641 Metal-handoff class). Every future host TSan run is now clean signal. Hardening: rs64_s4211_pi_n/ring (guest PI DMA
    writer vs RSP-thread reader, default-on diag, s7354 BENIGN) now publishes with release/acquire, scan stays 256 clear;
    ROGUESQ_S7643_PI=0 = old plain counter. L1 dd2 120 s flight: fix 59 reports/6 pairs (0 on s4211), old 62/8 (counter pair back +
    2 do_rom_read<->rsp::run_task RDRAM bytes). Both flights level_ok=1, alive, vi_stalls30s=0. Remaining non-Metal pair:
    rs64_g1d_title_vi (s7354 BENIGN, single writer). Not covered: guest RDRAM concurrency (RSP task reading bytes a guest PI DMA
    writes, do_rom_read<->run_task): guest code is uninstrumented, see NEXT.md class TS-3.
31. **Class TS-3 (RSP audio task vs guest PI DMA on the same RDRAM bytes): CLOSED s7644, H-retail/H-margin, 0 fixes.** The s7643
    do_rom_read<->run_task pair is the audio task's ucode_data -> DMEM byte copy (rsp.cpp dma_rdram_to_dmem, atos run_task+7108
    on tsan3), not the s4211 hash (no s4211 dp range covers 0x800A5134). The game's OSTask declares ucode_data=0x800A4E00
    (aspMainDataStart) size 0x800, but real data ends ~0x800A5120: then the game's vars speechSampleOffsetsLoaded/speechFileLoaded
    and from 0x800A5130 the overlay VA region, which the game fills in 0x4000-byte PI chunks. Instrument (default off, src/rsp/
    s7644_rspdma.cpp + hooks in librecomp rsp.cpp/pi.cpp): `ROGUESQ_S7644_RSPDMA=1` classifies every PI DMA overlapping the last
    audio task's ucode_data or command list by task state (copy/run/idle) and bytes changed, plus an image FNV per task;
    `ROGUESQ_S7644_RSPDMA_CTL=1` = synthetic overlap line (fired 1/1 per arm). L1 + L4 dd2 FPS60 16:9 120 s (scratch/s7644/run):
    ~8.8k audio tasks, 4+4 ud overlaps all 0x800A5130+0x4D0 (overlay ROM 0x137580/0x10C2D0/0xA5D30, chg 1054-1121 bytes),
    state copy 0, torn 0, command-list (dp) overlaps 0; every image change is either one of those DMAs or a CPU write ~8 tasks
    later with no PI DMA. Hardware rspboot copies the same declared 0x800 at task start, so the tail bytes are retail-identical.

32. **Class TS-4 (LLE gfx task vs guest PI DMA on RDRAM the task DMA-reads): CLOSED s7647, H-alias8 (instrument artefact), 0 fixes.**
    s7645/s7646 keyed both sides `& 0x7FFFFF`; the RSP reads with rs64_s7327_mask 0x1FFFFF8, and at dd>1 (OSMEM 12 heap / DLPOOLX /
    spill) gfx data lives above 8 MB. The 0x110-B reads at DMEM 0x170 are the ucode's TriGen chunk fetch (L_11B0, chunk word 0 =
    next, 0x108 stride) at 0x9950A0+, which aliased the MusyX 256-B sample-stream PIs (musyxSynthFrame -> submitDmaRequestBatch ->
    piDmaWorker, buffer 0x80195190+, 0x600 per voice). s7647 (src/rsp/s7644_rspdma.cpp pm(): key 0x1FFFFFF, `ROGUESQ_S7647_MASK8=1` =
    old key; new same-run counters hi_reads + alias8): L4 dd4 FPS60 16:9 120 s, true key rd_after_pi 0/0 B, stale 0, refetch 0,
    ctl_rd 5, hi_reads 11.7M; alias8 4881/647 KB in the SAME run; old-key arm m4 rd_after_pi 4876, stale 117, ctl_refetch 1. Both
    alive, 0 crash, vi_stalls30s 0. The dd1 zero of s7646 was real only because dd1 has nothing above 8 MB. scratch/s7647/run.
    The other 8 MB keys were audited as class MK8 (item 33): all diagnostic.

33. **Class MK8 (8 MB phys masks `& 0x7FFFFF`, phys end checks `0x800000`, 0x807Fxxxx near-bounds): CLOSED s7648,
    H-mk8-diag-only, 0 behaviour fixes.** `python3 tools/s7648_mk8_census.py` (exit 1 on an unclassified site; `--controls`
    plants an ungated host key + generated bound, s7648 2/2 flagged PASS). Host src+lib 229 sites (D 177 env-gated, D* 52
    hand-read), generated 25 (D 17 opt-in/diag patch blocks, F 8 float masks), ucode 0. Fills the "class M, open" gap of
    s7337_bound_census.py, whose generated pattern missed 13 `0x807Fxxxx` bounds (all opt-in/diag). Single-source by
    construction (static read); D is a regex on the enclosing function, D* list in docs/MK8-KEY-ALIAS-CENSUS.md.
    s7649 re-validation (table in the doc): only s6230/s6231 [g1d-tex] was an alias artefact (intermediate, superseded by
    s6243); instrument re-keyed. 34. **Open (s7650): census function attribution** — the FN regex can pin a site to the
    previous definition (rt64_render_context.cpp:2088-2147 -> rs64_s7541_span), so those sites' D labels are unproven.

## Evidence index

- Maintenance archives (whole CURRENT-TRUTH verbatim): PROJECT-OVERVIEW s7417, s7370, s7307, s7187, s6994; trims s7262,
  s7134, s7121, s7104, s6982, s6962; s6900, s6847, s6759; [Maintenance s6667 retained evidence](PROJECT-OVERVIEW.md#maintenance-s6667-retained-evidence).
- Objective contracts [G1-OBJECTIVE-RESPONSE](G1-OBJECTIVE-RESPONSE.md); images [G1-FRAMEBUFFER-COVERAGE](G1-FRAMEBUFFER-COVERAGE.md).
- Owner commands docs/OWNER-OPT-INS.md; owner sheets docs/owner_sheet_s7*.png/jpg.
- Queued-soak verdicts `scratch/agent/SOAK-RESULTS.md`; loop.sh edits take effect before the next soak phase
  (s7235 re-exec); idle-gated recipes polled up to SOAK_IDLE_WAIT=1800 s (s7254).
- Recent chronology: PORTING-STATE sessions 7579-7622; search bounded windows only.
