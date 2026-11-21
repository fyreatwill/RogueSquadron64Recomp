# Rogue Squadron 64 Recomp — current truth

Compact operational handoff, as of Session 7736 (2026-11-20).
`PORTING-STATE.md` is the chronological ledger; durable and migrated material lives in
`docs/PROJECT-OVERVIEW.md`. The full s7416 text of this file (every audit class AQ-BZ s7373-s7416 with all numbers,
controls and tool flags) is archived verbatim in PROJECT-OVERVIEW "Migrated from CURRENT-TRUTH (s7417 maintenance)"; item-1 classes DG-EO in "(s7491 migration)"; classes CC-DH s7420-s7451 in "(s7452 maintenance)";
s7315-s7369 classes in "(s7370 maintenance)"; the s7306 headline chronology in "(s7307 maintenance)"; older text in
"(s7187 maintenance)" and "(s6994 maintenance)"; s7533 Next-steps items 1,12,15-21 (classes FD-FZ) in "(s7534 maintenance)"; s7535-s7576 headline + items 17-21 + pre-s7300 superseded in "(s7581 maintenance)"; s7579-s7616 headline + items 19-46 in "(s7622 maintenance)"; s7647-s7659 headline + items 21-35 in "(s7662 maintenance)"; s7617-s7702 headline + item 20 (G6) in "(s7703 maintenance)". Grep there for any sNNNN.

## Headline

**Every engineering goal on the ladder is closed or awaiting the owner's look.** Nothing is broken at the
owner's recipe as far as any instrument can see; remaining items are owner judgements (list in Next steps).

- **s7737 DIAG consumer census (H-none after review; now in the s7719 gate).** tools/s7737_diag_consumers.py takes every reverse
  DIAG/ORDER-DIAG/REGEN-FUNC-DIAG row (live-only lines no fixup reproduces), pulls the env names those lines read (direct getenv +
  brace-matched bodies of the helpers they call, src/ and live preludes) and their `[tag]` log prefixes, and greps live consumers
  (tools/ scripts, pending soak recipes, OWNER-OPT-INS; census/audit/gate/fixup/apply files excluded). Current tree: 73 rows, 0
  CONSUMED, 2 ACCEPTED (s6826 TICK_TRACE hooks at 6 menu PCs in funcs_32: stale in live, g3_float_quanta_audit.scan marks them
  unreachable on BOTH trees, the fixup only adds; tools/s7737_diag_consumer_accept.tsv), 71 ORPHAN. Controls: synthetic
  LOG_G1D_TASK -> CONSUMED / nobody -> ORPHAN, and the real one: the pre-fix s7735 replay -> beginFrameDLChunk [g1d-alloc] CONSUMED,
  gate VERDICT H-drift (diag-consumers 1). s7736 replay: gate H-mirrored. Also seen: live funcs_10 transformWorldPosToGridSpace has
  the s6314 EDGE_FADE_TEST2 block TWICE (opt-in scale applied twice; the replay has it once = correct; accepted ORDER-BEHAVIOUR).
- **s7736 live-only reader split: 1 needed probe restored to the regen, the rest dead/accepted.** Of the 18 live-only getenv
  occurrences (live vs replay), ROGUESQ_LOG_G1D_TASK's s6201 [g1d-alloc] block (beginFrameDLChunk, funcs_3) was silently lost by a
  regen: its inline fixer call ran before the S5798 store form, and its 0x8000A934 anchor broke once s6285/s6287 text landed. Fixed:
  apply_s6201_alloc anchors on 0x8000A938 + keeps s6336 order, and tools/apply_s7736_g1d_alloc.py runs it from RS64_REPLAY after
  s6287. New replay: beginFrameDLChunk byte-identical to live, reverse DIAG 67->66, gate H-mirrored, controls PASS. The other 13 are
  accepted dead text: funcs_50.c (5, orphan prelude-only chunk from a 51-chunk regen, 0 RECOMP_FUNC), funcs_9 CLAMPP + FORFACE_LOG x4
  (closed s6496-s6526 chain; the 4 DRAW_DISTANCE reads sit inside FORFACE_LOG-gated fprintf, not owner behaviour), funcs_10 EDGE_FADE_TEST2.
- **s7735 regen replay reproduces the s7734 readings (H-replays selected, H-drift refuted).** tools/s7719_regen_gate.py (in the
  gate sweep) now also runs `s7734_compiled_reader_census.py --tree <fresh replay>`: replay 378 readings, 0 unreviewed HIDDEN/NOREF,
  B40 new form present (2 sites); planted control (replay funcs_23 B40 put back to the pre-s7734 text) -> HIDDEN rc 1 PASS. The
  one live-only reading is ROGUESQ_CLAMPP (s6522 funcs_9 probe, not in RS64_REPLAY, a known DIAG line). Sweep --only s7719|s7734: 2 GREEN.
- **s7734 compiled-tree reader census (H-hidden selected, 3 names, fixed).** tools/s7734_compiled_reader_census.py models every
  `getenv("ROGUESQ_*")` in RecompiledFuncs + factor5_ucode (379 distinct readings: COVERED 346, NOREF 14 numeric/sentinel (hand-read, NOREF_OK), UNMOD 19)
  against the live script/host signatures. HIDDEN were: LOG_ALL in the s4159 preclear census (presence: =0 and "" turned it ON),
  DD_CAPX_TOG s6548 log cadence (presence vs `atoi`), M5_B40_VALUE guest store ("" passed r2 while the host labels "" control).
  All three script texts + compiled tree fixed; 0 HIDDEN. Controls: planted presence line -> HIDDEN, S4562 default strip 1 -> 0.
  Rerun after any regen: `python3 tools/s7734_compiled_reader_census.py` (rc 0).
- **s7733 truth census DEAD filter (H-dead selected).** 76 apply/fixup reader texts over 34 names are not in the compiled
  tree (replace anchors, steps whose anchor matches nothing); s7714 and s7716 now drop them before modelling (`--dead` lists them,
  planted/live/B40/unfiltered controls PASS). 3 REVIEWED splits were dead-text votes only (OVL2C_DROP, M5_B40_VALUE, S4562_PAUSE).
  fixup_factor5_ucode.py `_old_cap` replace removed (byte-identical on all 12 ucode files, planted control). Open: the census
  never models the compiled tree itself; S4562_PAUSE's live reader (funcs_24.c, s4786 `if (!e) e = "4"`) arms when unset.
- **s7732 "=0 reads ON": ROGUESQ_ASPECT was the one owner-facing trap (H-trap for it, H-mode for 17 others).** main.cpp took any
  ASPECT value as opt-in, so `=0`/`=off`/`=orig`/a typo opened the high-DPI fitted window with a retail 4:3 picture (same-binary
  KEEP control: drawable 1280x960 vs 640x480). Launch now unsets any value that is not auto/expand/W:H (`[s7732] ...`, re-exec;
  shell and settings file); `ROGUESQ_S7732_KEEP_ASPECT=1` = old. Census gate zero_on_check: 18 owner-documented presence names,
  all reviewed (values, model over-reads, NO_SAVE_WRITE save-safe), planted control PASS.
- **s7731 on/off words now read as their digit (H-agree on readers, H-against-intent selected).** Truth census VALUES +=
  off/on/true/" 1"/"1 ": 0 unreviewed SPLIT, but every switch reads digits only, so `=off`/`=false`/`=no` read ON at 216
  names (FPS60, ASPECT, CULL_SPIKE...) and `=on`/`=yes` OFF at 39 (`*e == '1'` QOS family); `=true` picked the 't' tog mode.
  rs64_settings_apply now maps whole-value words (any case) to "0"/"1" in the shell env and settings-file values
  (`[s7731] NAME=on read as 1`, re-exec), except kKeepWords names whose reader gives the letter its own meaning
  (DD_OFFMAPCULL_H 'o' = gate off; HUD_MARKCLS 'y'). `ROGUESQ_S7731_KEEP_WORDS=1` = old. Live same binary: QOS_ALL=on arms
  QoS (KEEP control: not), settings-file `yes` arms it (KEEP: not), `=1` control arms, unset does not. Census gates: words
  unmapped-against 0 (control: no normaliser -> all 6), letter scan unkept 0 (control: empty keep -> both names).
- **s7730 empty env values are unset for every reader (H-split selected).** Pre-fix live, same binary: `ROGUESQ_ASPECT=`
  opened the high-DPI opt-in window (drawable 1280x960 vs unset 640x480) and `ROGUESQ_OSMEM_MB=` at dd2 blocked the bundle's
  12 MB / 0x81000000 spill layout (no `[ddbundle] osmem=12` line; the owner LEVEL=15 fix layout). rs64_settings_apply now
  unsets every empty `ROGUESQ_*` at launch (`[s7730] NAME= is empty: treated as unset`) and re-execs so pre-main statics agree;
  `ROGUESQ_S7730_KEEP_EMPTY=1` = old (control reproduces the loss). The truth census VALUES include "" (0 unreviewed SPLIT,
  planted control PASS). s7729 (81 unmodelled sites classed; settings-file `NAME=` left unset) and s7728 stand.
- **s7727 NSZombie census on the owner hangar route: H-clean.** s7469 abort/re-entry schedule (4 mission loads, 3 SELECT YOUR
  CRAFT re-entries, ship scrolls) at 16:9 dd4 FPS60 STANDINS=1 FULLSCREEN, 570 s/arm: default 0 zombies in all 8 segments (270k
  MISSING POOLS lines); same-run MTL_OWN=0 control 364 TextureDescriptor zombies, >=12 in every segment. Both arms 0 fatal.
  Scorer gained `--mark`/`--segments` (tools/s7726_zombie_census.py). Over-release thread closed on both owner routes.
- **s7726 NSZombie census past boot: H-clean.** L4 owner recipe 150 s, NSZombieEnabled + OBJC_DEBUG_MISSING_POOLS: default arm
  0 zombies boot+flight (68k MISSING POOLS lines, all live objects); same-run ROGUESQ_MTL_OWN=0 control 163 TextureDescriptor zombies
  (113 boot + 50 flight). Scorer tools/s7726_zombie_census.py (rc 3 on a blind control). s7725 soak folded: L4 300 s clean.
- **s7725 RT64 Present SIGTRAP (.ips 2026-11-18-014353) root-caused and fixed:** plume MetalBufferFormattedView released a +0
  `textureBufferDescriptor` (NSZombie boot: 103 `_NSZombie_MTLTextureDescriptorInternal` -> 0 with the fix; ROGUESQ_MTL_OWN=0 control
  103 in the same binary). The pool push flushes the freed pending object (TLS slot 0x160); OBJC_DEBUG_MISSING_POOLS only made the
  reporter read its isa (PAC brk 0xc472). Latent in normal play (dangling pointer in a never-drained pool). Census widened to all
  class factories (OLD 7 OVERRELEASE, NEW 0). Witness tools/s7725_pool_trap_repro.sh. Soak s7725_texdesc_L4 queued.
- **s7724 deferred scorers CLOSED (item 32): 7 more gates over retained captures** (S7724_RETAINED: s7433/s7435-s7438 profiler
  scorers on scratch/s7435 sample_*.txt.zst, s7467 ASan arms on scratch/s7467r, s7624 flicker L1); planted RED mutants 18/18 PASS
  (control frames renamed -> CONTROL FAIL rc 3; unreviewed UBSan group -> rc 1; window-1 rows dropped -> regex unmatched).
  H-no-control s7367/s7369/s7434/s7589 (s7589's own control FAILs on both retained hr.tsv), H-gone s7247. Scorer work ends here.
  stop_gate churn guard no longer counts `from rs64_zopen import zopen` lines (s7723 tripped on 12; recount 1). Sweep 215: 212 GREEN 3 REPORT 0 RED 0 HOLLOW.
- **s7723 NEEDS-INPUT scorers: 11 become gates over their retained scratch/ captures** (S7723_RETAINED in the sweep; logs read
  as .zst via tools/rs64_zopen.py; tools/s7723_retained_controls.py plants one RED row per gate, 11/11 PASS and is itself swept).
  s7393/s7399 exit 0 with their control removed, so the CONTROL PASS regex is load-bearing. Rest: H-gone 10, H-dead 2 (s7421/s7423
  -> s7719 gate), H-stale-coupled s7389, H-no-control s7391, deferred-retainable 9 (CURRENT-TRUTH item 32). Sweep 0 RED 0 HOLLOW.
- **s7722 REPORT tools CLOSED: s7082 jal + s7083 lowering censuses are gates now** (`--check`, s7082 `--plant`; ARGS over the
  retained scratch/s7082 front-end pass; RED controls extra-jal-line / mutated case label rc 1). s7031/s7210/s7441 stay REPORT
  (H-report, pure tables). Sweep 196 {GREEN 193, REPORT 3} 0 RED 0 HOLLOW. Next: the 39 s7718 NEEDS-INPUT scorers (one iteration).
- **s7721 HOLLOW_KEYS vocabulary audit CLOSED (H-gap, no real open item):** 649 count keys enumerated over all 196 captured
  outputs; 19 open-class words added (MISSING/STALE/RACE/UNGUARDED/DISAGREE/LEAK/FOLDED/...), 5 flagged gates reviewed HOLLOW_OK
  (s7085, s7359, s7632, s7633 already classified). Sweep 196 {GREEN 191, REPORT 5}, new control hol_s7721 PASS. Next: REPORT tools.
- **s7720 sweep-scoring audit CLOSED (H-more): rc-0 gates now score HOLLOW on a nonzero open count or an unpassed
  --check/--strict/--gate (controls hol_open/hol_zero/hol_flag PASS).** 16 tools now run with their flag; 7 had failed their own
  --check while GREEN, all 7 reviewed GREEN: s7384 static-state 114/114 MULTI reviewed, 0 RACE (pi.cpp rom INITORDER,
  g_rdram_for_submit BENIGN same-value, env_cache trace LOCKED by pthread mutex, rest DIAG/LOCKED/ARTEFACT); s7557 every
  default-on lever has a docs row (PROJECT-OVERVIEW "Default-on internal guards and fixes"). allowed_red list empty again.
- **s7719 regen-replay drift CLOSED H-mirrored, both directions; now a live sweep gate.** Fresh front == s7558 pristine; replay vs
  live 2620/141/18, s7421 new-vs-s7558 {} (control PASS), s7423 forward H-diag and new `--reverse` (live-only statements in every
  function) 29 rows all hand-accepted (tools/s7719_live_only_accept.tsv). tools/s7719_regen_gate.py (front + RS64_REPLAY_TREE_ONLY
  replay + both scans, 2.6 min, wiring controls 2/2 RED) is in the sweep. Also: s7363/s7364/s7366 printed OPEN 19/22/6 yet scored
  GREEN (no --check); ARGS fixed, 35 rows hand-reviewed bounded/locked, 0 defects. regen_verify.sh now RV_JOBS (default 2).
- **s7717 setenv-after-static-init idiom CLOSED (H-clean, static + runtime).** Every reader that latches a ROGUESQ_* var in a
  file-scope initializer before main()'s auto-default setenvs is re-armed after the policy or reviewed. s7427_env_policy_order.py
  had drifted RED unseen (not named *_census.py; the s7713 OSMEM sanitiser read, reviewed benign). Its scan missed
  `struct T {T(){..}} x;` globals (S7246Init); fixed, 316 roots, control 5/5 incl. dropped re-arms. Runtime trace (scratch/s7717/run.zsh)
  = the same 5 handled pre-policy reads, plant control PASS. The sweep now also runs EXTRA_GATES s7427/s7424/s7425. s7426 checks B-D are
  SUPERSEDED by s7714/s7716 (its RED rows are helper/polarity false positives). Sweep 143: 138 GREEN 5 REPORT 0 RED.
- **s7716 default-on label census (gate): idiom "flipped default, stale label" CLOSED.** tools/s7716_default_label_census.py
  (controls 5/5, in the gate sweep) models every reader of 198 default-on names incl. getenvs inside printf args, polarity-free:
  0 LABEL-WRONG, 5 reviewed splits, 40 hand-read deferred/unmodelled. Its debug-doc check fixed 2 rows of
  docs/debug-trace-env-vars.md (LOG_M4_Y8000 is opt-in since s6712; SPIN_YIELD is default on since s4199). Docs only.
- **s7714/s7715 truth census (gate): 0 owner-setting on/off splits.** tools/s7714_truth_census.py (controls 6/6, in the gate sweep) parses
  every multi-site reader's C, isolates the expression on that variable and evaluates unset/0/1/2/t/yes: 646 sites modelled, 14
  REVIEWED mode letters / dead / diag. Fixed: the vendored m5 label (unset AUDIO_UCODE now prints audio_on, as the real ucode runs;
  mirrored into funcs_34.c), SPIKE_DMEM and STANDINS_LOG/CTL/PULL presence readers (=0 armed them). Witness scratch/s7714/run.zsh 4/4.
  s7715: Python-embedded C now tokenised file-wide (controls 8/8): 708 modelled, 81 unmodelled (pass-ons/foreign/no-decision
  residue, class CLOSED). New split fixed: ROGUESQ_M5_C88_VALUE labels said c88=0 for unset while the store passes the guest
  value ([s7715-c88], S7715_C88LBL=0 old; witness 3/3). B40 (replay-flipped, owner item) and S4562_PAUSE REVIEWED.
- **s7713 multi-reader clamp census + OSMEM_MB fix.** tools/s7713_multireader_census.py (controls 5/5, in the gate sweep): of 289
  ROGUESQ_* names read at >=2 sites, 3 pair a clamping reader with a raw-threshold reader. DRAW_DISTANCE MASKED (s7712), FB_WIDTH AGREE,
  OSMEM_MB was split: recomp.cpp maps values outside 4..16 to 8, but the dd bundle armed the 12 MB spill/ramtop layout for raw >8 (e.g.
  20). Fixed in rs64_s7358_sanitize_env (`[s7713-osmem]`, ROGUESQ_S7713_OSMEMCAP=0 = old); runtime arms 4/4 (old arm reproduces it).
  Owner lines use 8 or 12, so the owner path is unchanged.
- **s7718 gate-sweep coverage: 52 more offline gates swept; 4 closed classes had gone RED or hollow unseen (H-drift).** The sweep
  discovered only s7*_census.py; 100 other tools with a VERDICT or a planted control were classified (scratch/s7718/classification.tsv):
  19 GATE-LIVE + 33 GATE-CONTROL-ONLY now in tools/s7651_gate_sweep.py (S7718_LIVE / S7718_CONTROL_ONLY), 39 NEEDS-INPUT (scorers of
  one capture), 4 COVERED (s7631/s7632 sources), 2 DEAD (s7426 B-D, s7324 refuted by s7327), 1 RUNTIME, 1 TOOL, 1 REPORT. Found:
  s7412 CONTROL FAIL (s7580's `0X803Fu` lui literals read impure: 24,262 lui sites silently unchecked), s7413 link error + 52k
  loads hollowed by s7484's RS64_S7484_LD observer prefix (lb 9.8k forms -> 40), s7428 two FIXED rows (a comment false positive,
  the s7430 rotate size probe), s7430 the s7702 log unreviewed (opt-in). All four tools fixed, harvests restored (s7413 101,169 pure
  sites = its closure count), real code 0 MISM; s7412/s7413 rows now pin harvest size. Wiring control 4/4 RED reverted -> 4/4 GREEN.
  Sweep 195 gates: 190 GREEN 5 REPORT 0 RED. No game code changed.
- **s7702/s7704-s7706 21:9 fb read-back: HARMLESS (CLOSED).** s7705/s7706: L1 and L4 intro cutscene + flight read no skipped buffer (join tool). The game LOADBLOCKs its previous 768-wide frame in the Hoth canyon
  flyover (t 12-16.7 s), and RT64 skips that write-back (SKIP_WILD_W). RT64 never serves those loads from its GPU copy (LOG_FBOVL 0 at 21:9).
  But write-back on vs off gives pixel-identical presented frames, and filling the skipped buffers with magenta (opt-in lib/rt64
  ROGUESQ_S7704_POISON=768) puts 0 magenta pixels on screen. The copy never reaches the picture, so no allowlist change.
  Tools: tools/s7704_wide_fbcopy_arms.zsh + s7704_fbcopy_score.py.
- **G5h cutscene pool floor (s6908) re-held post-G6c (s7696-s7701):** mission intros L1/L4/L5 and the AT THE MOVIES playlist (outro
  proxy) at 16:9 dd2/dd4 and 21:9 dd2 (kept nodes floor vs old cap e.g. 16:9 dd2 1350/831, 21:9 dd2 1605/858); visible where the old
  cap leaves flat ground holes (sheets docs/owner_sheet_s7700_movies_dd2.jpg, s7701_movies_219_dd2.jpg, scratch/s7699/L5d2_sheet.png).
  Stand-ins never run inside intro cutscenes (H-absent, 3/3 levels). At 21:9 FB_DUMP needs ROGUESQ_ALLOW_WILD_W=1 (tools arm it).
- **Post-G6c re-holds (s7692-s7695): clean.** 300 s STANDINS=1 dd4 owner recipe L1/L4/L5/L10/L12/L15 6/6; G5c 900 s freeze gate L4/L12
  (0 gaps >= 250 ms after t=95 s, SIGSTOP control caught); G2b crawl audio fix 2 vs ctl 1037; G5d logo share unchanged.
- **G6c stand-ins (ROGUESQ_STANDINS=1, opt-in, dd>1 only): DONE, owner's look.** Design docs/G6C-STANDINS-PLAN.md; code
  src/main/rs64_standins.cpp + tools/apply_s7623_standins.py and follow-ups (RS64_REPLAY). Visible early at true depth on 2 levels,
  19/19 levels 300 s clean (s7629/s7630), sheet docs/owner_sheet_s7691_standins_on_off.jpg. Default-on sub-fixes inside STANDINS (=0 old):
  S7625 far (STANDINS_FAR=dd), S7672_HOLD (no blink at spawn), S7677_GEN, S7679_NEAR=15, S7681_SHIELD, S7684_RSKEY, S7685-S7687_POSSUB,
  S7690_PARITY (frame mode). Ghost thread closed as H-gate (s7676); level changes safe (s7678). Rerun tools/g6c_sub_handler_map.py after
  a stand-in table edit and scratch/s7672/run.zsh after a stand-in code edit.
- **G6a rumble (s7617/s7638/s7671, default ON, ROGUESQ_RUMBLE=0 old, _SCALE 0..2) and G6b controls (s7618-s7620, s7666-s7670; table
  src/main/rs64_bindings.h == old map, controls.json, F6 panel): LANDED, owner's hands.** Rumble abort cannot stick (the game stops the
  motor at PAUSE entry). F6 panel survives mission load, fullscreen toggle and live resize (S7668_ASPECT). After an input-path edit
  rerun `ROGUESQ_BIND_PANEL_TEST=1` scratch/s7620/run.zsh + tools/test_bindings.cpp.
- **Owner launch settings s7663 (`--preset tv|ultrawide|window`, build/settings.txt; env > file > preset; s7667 relative
  ROGUESQ_CONTROLS resolves beside the file): owner to try.** Crash reports gate s7664 (tools/crash_reports.py; NEW outranks all work).
- **s7660/s7661:** title plume si_addr=0x58 CLOSED (0/76 boots); lldb attach works in loop sessions (preflight tools/lldb_attach_check.sh;
  never LAUNCH the game under lldb, s7616).
- **s7647-s7659 (census-gate sweep + classes TS-4/MK8): ALL CLOSED, 0 behaviour defects** (archive "(s7662 maintenance)"). Standing
  check: `python3 tools/s7651_gate_sweep.py` (--jobs 2; cold ~455-530 s, warm ~15 s) -> 135 GREEN (s7716 adds its census), 5 REPORT, 0 RED; stop_gate blocks RED.
  Key reviews by text anchor, never line number. NEEDS-INPUT gates use retained inputs under scratch/s7215, s7316/ram, s7573/retained.
  All s7617-s7702 bullets verbatim in PROJECT-OVERVIEW "(s7703 maintenance)".
- **s7579-s7616 host-side idiom-class audits: ALL CLOSED** (full text, numbers, controls, tool flags verbatim in
  PROJECT-OVERVIEW "(s7622 maintenance)"). TS-2 s7643 (TSan over host runtime, item 21; archived s7662): 1 hardening (s4211 PI ring), SEM blind spot now annotated. TS s7642 (TSan over all RT64+plume, item 21; archived s7662): H-clean, 0 fixes. CF s7641 (framework-callback threads, item 28): 1 fix (plume Metal drawable index race, TSan). AT s7640 (AppKit thread affinity, item 27): 1 fix (RT64 NFD_Init on Gfx Thread). ST s7639 (SDL thread affinity, item 26): 1 fix (F6 panel draw hook). H-clean, no fix: HB s7633 (bridge default-on diag, item 23; 1 getenv latched), HD s7632 (rt64 default-on diag work, item 22; 2 getenv latched), RP s7631 (lib/rt64 kept RDRAM pointers, item 21), RQ s7616, DQ s7615, HM s7614, HP s7613, RG s7612, SN s7611,
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
- **G5c freezes CLOSED (s7272-s7285; re-held s7694 on the post-G6c binary, STANDINS=1 L4/L12 900 s):** 0 flight image holds >= 250 ms on quiet host, windowed, fullscreen, 900 s
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
- s7587 "the 2026-11-18-014353 RT64 Present SIGTRAP is an OBJC_DEBUG_MISSING_POOLS instrument artifact": believable because only
  the debug arm crashed; superseded by s7725 (the env alone never traps; the push flushes a freed +0 texture descriptor that plume
  over-released; fixed).
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
- Title plume si_addr=0x58 CLOSED s7660 (0/76 boots); reopen only if `[plume-null-color-attachment]` prints.
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
   s7005/s7006), G5g hangar lens (s6907), G5h cutscene background (s6908-s6919; re-held post-G6c s7698-s7700 incl. movies playlist): owner flight / look.**
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
18. **After-regen UB gates (all CLOSED, rc 0 expected; rerun s7693 on the post-G6c tree: all rc 0, BLIND=0, FOLDED=0):** tools/s7575_ir_calls.sh + `tools/s7575_break_census.py --controls --ir D`
    (BLIND=0); `python3 tools/s7576_trunc_census.py --controls` (FOLDED=0); after a ucode regen or rsp*.hpp edit
    `tools/s7577_ubsan_sites.py <tu> --check` per ucode TU (UNCLASSIFIED 0) + `tools/s7577_ucode_ub_census.py scratch/s7577`;
    tools/s7580_lui_identity.py (0 object diffs). UBSan builds: `env SAN=<checks> B=<dir> zsh tools/build_ubsanc.sh`, scorer
    tools/s7579_bounds_report.py, plants ROGUESQ_S7578_PLANT=1-6,u (SANREC for non-recoverable checks). s7578 null/wrapv, s7579 bounds, s7580 shift/align, s7582
    pointer-overflow, s7583 div0/fcast/bool/builtin/vla/nonnull/unreachable CLOSED: every C-applicable UBSan check has run.
19. **Rerun-after-change censuses s7579-s7616 (all CLOSED, 26/26 rc 0 s7693; RG --witness takes >=2 of s7103/s7108/s7110 logs; per-class trigger text verbatim in PROJECT-OVERVIEW
    "(s7622 maintenance)").** Each `python3 tools/s76NN_<cls>_census.py --controls` must exit 0 after an edit in its scope:
    RQ/DQ s7616/s7615 (lib/rt64 RDRAM reads, new threads; a worker-thread RDRAM reader needs a command-time copy or a gate),
    HM/HP s7614/s7613 (--ast; statics), RG/SN/MK s7612/s7611/s7609 (--witness; regen, statics), OV s7610 (regen, overlays.cpp),
    TK s7608, UW s7607 (throw/catch, blocking calls), HC s7606 (threads.cpp/recomp.cpp), FR/RA/RX s7605/s7604/s7603 (host code
    touching guest regs/FPRs), TP s7602 (TO_PTR views), BS s7601, GX s7600, GR s7599, AZ s7598 (allocations, createTexture),
    XC s7597 (throw/json parse), FS/SV/SG s7596/s7595/s7594, EX/TH s7593/s7592, MR s7591 (lib/ edits). OW/OW-2/LK/HR
    s7585-s7589 tools as named in the archive. Renaming sweep closed (s6868). ROGUESQ_MTL_WAITPOOL default on.
20. **G6 (owner 2026-11-18): G6a rumble, G6b controls, G6c stand-ins: all LANDED, close on the owner's hands/look** (headline).
    Full step history s7617-s7691 (stand-in steps 2-4, H-culled/H-far, draw proof, handoff polish) verbatim in PROJECT-OVERVIEW
    "(s7703 maintenance)".
21. **Classes RP, HD, HB, ST, AT, CF, TS, TS-2, TS-3, TS-4, MK8 + walker fusion + spike cost + closed-gate drift (s7631-s7659):
    ALL CLOSED** (full text, numbers, controls, tools verbatim in PROJECT-OVERVIEW "(s7662 maintenance)"). Defaults that stay
    (=0 / old restores): ROGUESQ_S7634_FUSE=1 (walker fusion), S7639_ST, S7640_AT, S7641_CF, S7643_PI (release/acquire s4211 ring),
    S7632_SNAP; opt-ins/diag: S7636_FASTSPIKE (default 0), S7632_STATS, S7644_RSPDMA(_CTL), S7647_MASK8. Rerun triggers:
    tools/s7639_st_census.py after any SDL call edit or new thread; tools/s7640_at_census.py / s7641_cf_census.py after AppKit or
    framework-callback edits; TSan builds tools/s7642_tsan_rt64_build.sh, s7643_tsan_host_build.sh (lightweightsemaphore tsan
    annotations are TSan-only); the gate sweep after any src/ or lib/ change. A new G above 0x80180000 reads unclassified (RED): re-dump.
22. **s7663 launch settings/presets: owner to try.** After any edit to rs64_settings.cpp rerun tools/test_settings.cpp and
    scratch/s7663/run.zsh (5 arms; C must print `[gfx-qos] mode=1` from the file). New owner recipes go in its presets() table.
23. **s7614_hm census: CLOSED s7673.** rs64_settings.cpp `p.vars` = host (static const preset table of string literals; row
    proof-checked, broken-proof control -> DRIFT). Census exits 0, controls 8/8. Add a row for any new static with pointer members. s7673 also re-greened s7611/s7599/s7352/s7535 (rows for s7663/s7671/s7672 code): run the gate sweep after every src/ commit.
24. **Crash-report gate (s7664):** `python3 tools/crash_reports.py` (rc 1 = NEW). Deliberate crash arms: quote the .ips basename
    in the session entry. Test tools/agent/test_crash_reports_gate.sh. DIAG datum RogueSquadron64Recomp-2026-11-17-053804
    (s7523 SLOWRDP consume() SIGSEGV) CLOSED s7665 as H-devbuild: crash 05:38, file first committed 05:59; both committed versions
    pass an ASan/UBSan fuzz (tools/test_s7523_model.sh, 2 controls) and the post-commit arms ran alive. Rerun that test after any
    s7523_slow_rdp.cpp edit.

25. **G1d 21:9 fb read-back of skipped wild-width buffers: CLOSED s7704-s7706 (H-invisible + H-none, 2 levels).** Boot cinematic read never
    reaches the picture (s7704). L1 (s7705) and L4 (s7706) at 21:9: 0 post-boot reads inside any skipped extent, any age
    (tools/s7705_join.py `in_after_boot=0`; boot ctl IN 3/3 per run; only post-boot hit = RSP DMA past the end of the 340-row 0xB80800
    buffer). 16:9 skips nothing (skipw=0). Rerun tools/s7705_fbread_flight.zsh + tools/test_s7705_join.sh after any SKIP_WILD_W change.
26. **21:9 post-G6c holds: CLEAN s7707 (3/3).** ROGUESQ_ASPECT=21:9 dd2 STANDINS=1 FPS60 fullscreen 300 s: L1/L15 (loop) + L4
    (in-session): alive 3/3, vi_stalls30s=0, max_gap 148 ms, level_ok=1, aspect 21:9 line 1/1, stand-ins on 1/1, spawns 38/39/164.
27. **Gate sweep was RED 13 for s7702-s7706, fixed s7707 (rules only, 0 behaviour defects).** New s7702 census
    (src/rsp/s7702_fbread.cpp, ROGUESQ_S7702_FBREAD), s7704 poison (lib/rt64 rt64_state.cpp fullSync, ROGUESQ_S7704_POISON) and the
    standins s_cut_prev edge static were unclassified in 13 gates. stop_gate --verify DID block s7702-s7706, but loop.sh moves on after
    MAX_CONTRACT_RETRIES=2 and nobody re-ran the sweep. Rows: census_rules.py (2), s7533/s7542/s7550/s7600/s7601/s7611/s7613 tables.
    Now 130 GREEN / 5 REPORT / 0 RED. Rule: ANY new src/ or lib/ instrument file -> run the sweep before committing.
    FIXED s7708: loop.sh now writes scratch/agent/CONTRACT-CARRY.md whenever the contract is still unmet after the retries
    and prepends it ("Unmet contract from the previous iteration (fix FIRST)") to the next prompt; deleted once --verify passes.
    Retry prompts for a census-RED verdict now say a checkpoint close-out does not clear it. Test tools/agent/test_contract_carry.sh
    (8/8; mutation controls: no prepend -> 2 FAIL, no write -> FAIL). If CONTRACT-CARRY.md heads your prompt, fix it before NEXT.md.
28. **Agent tool tests gated s7709.** tools/agent/run_tests.sh runs every tools/agent/test_*.sh (8, ~60 s, PASS/FAIL line each,
    rc 1 on any FAIL). stop_gate --verify runs it when the iteration's commits touch tools/agent/*.sh|*.py and blocks "agent tool
    tests FAIL: <names>" (RS64_AGENT_TESTS=0 skips). Test tools/agent/test_agent_tests_gate.sh 3/3 (red/green/untouched) + 2 mutation
    controls (trigger disabled, runner ignores rc -> red FAILs). All 7 pre-existing tests were already green (H-green).

29. **Owner-setting census s7710: CLEAN (H-clean, controls 5/5).** Every ROGUESQ_* name in OWNER-OPT-INS.md + README (112) and the
    --preset table (4) is read by code (quoted in src/, lib/rt64/src, lib/N64ModernRuntime or a fixup/apply script; CMake option()
    for SRC_OPT/FUNCS_OPT); ROGUESQ_NAME is the allow-listed syntax placeholder. build/settings.txt is checked too when present.
    `python3 tools/s7710_optins_census.py --controls` is in the gate sweep (now 136 gates, 131 GREEN): a doc row for a setting the
    code no longer reads goes RED. Limit: "read" = quoted string, so a name kept only in a log format would pass.
30. **Owner-setting VALUE census s7711: CLEAN (H-clean, controls 5/5).** All 127 documented `ROGUESQ_X=V` pairs (docs, README,
    presets) reach a parser that reads V: no fraction under atoi, no `16:9`/list under a numeric-only parse, no "=0" lever that only
    tests the pointer, every dd>4 doc command carries DD_UNSAFE=1. `tools/s7711_optval_census.py --controls` is in the gate sweep
    (137 gates, 132 GREEN; s7713: 138, 133 GREEN). Static and single-source: range clamps hand-checked only for RUMBLE_SCALE, OSMEM_MB, STICK_GATE, dd.
31. **Multi-reader clamp census s7713: CLEAN after the OSMEM_MB fix (H-many: one more split than s7712's DD; controls 5/5).**
    `tools/s7713_multireader_census.py --controls` gates clamp-vs-raw-threshold splits across all multi-reader names (sanitizer
    modelled first). Runtime witness scratch/s7713/run.zsh. s7728: the m5 audio_stub label was fixed in s7714; rs64_env_int
    names are all single-reader (nothing to model). s7714 truth census now probes =false/=no and runs a host LOG_ALL pass
    (`python3 tools/s7714_truth_census.py --controls`, rc 0): rerun after adding any ROGUESQ_LOG_* reader in src/ or lib/.
    s7729: every unmodelled site is in UNMODELLED_T (class + line fragment); a new reader it cannot model exits 1 until classed.
    s7730: VALUES include ""; empty ROGUESQ_* values are stripped at launch (rs64_settings.cpp), so "" never reaches a reader.

32. **Gate-sweep coverage s7718/s7723: offline gates all swept (208).** s7421/s7423 superseded by s7719_regen_gate. Of the 39
    s7718 NEEDS-INPUT scorers 11 are gated over retained captures (s7723), 7 more in s7724 (s7433/s7435-s7438/s7467/s7624).
    CLOSED: s7367/s7369/s7434/s7589 H-no-control, s7247 H-gone. No further scorer work.
    Lesson (s7412/s7413): a harvest-based gate can exit 0 while a later fixup idiom hides its sites; pin the harvest size.
    Lesson (s7723): a scorer whose "control absent" path exits 0 (s7393, s7399) is only a gate with a CONTROL PASS regex.

## Evidence index

- Maintenance archives (whole CURRENT-TRUTH verbatim): PROJECT-OVERVIEW s7417, s7370, s7307, s7187, s6994; trims s7262,
  s7134, s7121, s7104, s6982, s6962; s6900, s6847, s6759; [Maintenance s6667 retained evidence](PROJECT-OVERVIEW.md#maintenance-s6667-retained-evidence).
- Objective contracts [G1-OBJECTIVE-RESPONSE](G1-OBJECTIVE-RESPONSE.md); images [G1-FRAMEBUFFER-COVERAGE](G1-FRAMEBUFFER-COVERAGE.md).
- Owner commands docs/OWNER-OPT-INS.md; owner sheets docs/owner_sheet_s7*.png/jpg.
- Queued-soak verdicts `scratch/agent/SOAK-RESULTS.md`; loop.sh edits take effect before the next soak phase
  (s7235 re-exec); idle-gated recipes polled up to SOAK_IDLE_WAIT=1800 s (s7254).
- Recent chronology: PORTING-STATE sessions 7617-7704; search bounded windows only.
