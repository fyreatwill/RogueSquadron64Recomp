# Rogue Squadron 64 Recomp — current truth

Compact operational handoff, maintained as of Session 5937 (2026-10-22).
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
and 300-second hold coverage (a)+(b) (11a/b, 12a/b, 13a/b, 14a: rc=0, vi_stalls30s=0, crashlines=0, hold 303-305 s; s5938). Levels 10 and 15 PASS (a)+(b) with a long wait for the planet-intro viewer auto-advance (~790 s): lvl10long mission_t=207s hold 303s, lvl15long mission_t=251s hold 305s, 0 crash, 0 stall (s5943). The older 10/15a short-wait runs failed identically (nomission, `curOvl=1 cineState=F7B80040`, origin 0x644D00/0x6A2900 alternating, letterboxed planet cinematic; s5939); 14b passes; 15b..18b are queued. Paired forced-level recipes for levels 10..18
were queued, but the first queue pass failed before launch because the shared
runner was itself a consumable `.sh` recipe and was moved to `soak_queue/done/`:

```text
20261022-135630 | g1_level_coverage_common | rc=1   | 0s
20261022-135630 | g1_lvl10a              | rc=127 | 0s
```

These are unevaluable and must not be counted as coverage. The repaired level-10
pair passed `[lvsel]` (`cursor=10`, `res=0xA`) in all five attempts per arm,
but both arms exhausted at `nomission`; their observed origins were only
`0x006A2900` and `0x00644D00`. A follow-up arm shifted the post-selection
`a/sl/sr` schedule from 95 s to 64 s; all five attempts still ended
`nomission` after reaching `0x006A2900` at about 60.4–60.9 s. The early-input
H1 explanation is rejected for this recipe; the level-10 transition remains
unresolved. This is not level coverage or crash/stall data.
Existing logs now locate the first repeatable divergence: after the selector and
section-4 DMA, level 10 retains stale cinematic state (`curOvl=1`,
`cineState=F7B80040`, `STAR`) and does not immediately enter `cineBody`, while
the level-11 control logs `cineBody a0=0xB`, resets to `curOvl=2`/zero cinematic
state, and then reaches `0x00696100` followed by `0x00690400`. This is a
transition-dispatch boundary, not yet a named writer or proof that
`0x006A2900` is invalid for level 10.
Session 5933 moved
the shared runner to `scratch/agent/g1_level_coverage_common.zsh`, outside the
queue glob, and restored level-10 `a/b` plus level-11 `a` wrappers. The wrappers
pass syntax/path-only checks. A valid
coverage run requires `[lvsel]` with `a1 == 1<<level`, flight
handoff, at least 300 seconds alive, zero crash lines, and no 30-second VI
stall. Missing controls are failures of evaluation, not passes.

G1 verification, once route+hold works for every level, additionally requires
a framebuffer showing terrain, craft, and HUD, plus a forced-hit objective
counter/end-gate response. Mission-to-mission progression and making the
autopilot win are owner playtest scope.

## Durable state and constraints

- Audio default route is active; `ROGUESQ_AUDIO_UCODE=0` is the silent control.
- `ROGUESQ_AUDIO_DEVICE` and `build/audio_device.txt` are owner routing state;
  do not alter them or treat `[audio-route]` as M5 evidence.
- The hangar route remains flaky at roughly 1/3 to 3/5 launches. Native hangar
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

## Next steps (single monotonic backlog)
- **s6000 G4:** lvl0 hold r1+r2 clean (662 s, 0 stall, 0 crash); r3 pending in the queue.
- **s6001 G4:** lvl0 3/3 clean 660 s holds (closed). The pillar-stub Next items below (s5964/s5970/s5999) are STALE - s5971 fixed them (FIX_ZERO_SHADE off). Queued m6_lvl{11-14,16-18}_hold660; fold, then G1(c) framebuffer check lvl10-18. s6008: hangar route 3/3 clean (att=1); d/e/f queued.
- **s6007:** hangar-route soaks a/b folded: both att=1, 600 s hold, 0 crash/0 VI stall (n=2, not enough to revise the ~1/3-3/5 flake rate). Run c still queued.
- **s6006 G4 CLOSED 0-18:** lvl18 662 s hold clean (0 stall/0 crash); all levels 0-18 held. Queued s6006_hangar_route_{a,b,c}; fold from SOAK-RESULTS.md (any abort => lldb/ASan backtrace + writer), then G5/parked hangar items.
- **s6005 G4/G1(c):** lvl16 (662 s) and lvl17 (662 s) holds: 0 stall, 0 crash, but both end in MISSION FAILED/GAME OVER (blind autopilot dies) and the harness cycles fail->results->select->relaunch (3x and 9x), all clean. lvl17/18 frames show terrain+craft+HUD (docs/g1_lvl16_18_contact.png; single-source). Next: fold lvl18 hold, then G3.
- **s6004 G4/G1(c):** lvl10 (665 s) and lvl15 (661 s) holds clean (0 stall/0 crash). G1(c) eyeball check lvl10-15 passes (docs/g1_lvl10_15_contact.png: terrain, craft, HUD; single-source). Next: fold lvl16/17/18 holds, then G1(c) contact sheet for 16-18; G4 closes for 0-18 if clean.
- **s6003 G4:** lvl13 (662 s) and lvl14 (663 s) holds clean (0 stall, 0 crash). Queued m6_lvl10/15_hold660 (PLANET_UNLOCK lever); lvl16/17/18 still queued. Next: fold those 5, then G3 hangar artifacts.
- **s6002 G4:** lvl11 (662 s) and lvl12 (665 s) holds clean (0 stall, 0 crash, alive_at_end=1). G1(c) for them was already covered by s5945 (18/18), so the "framebuffer check lvl10-18" in the s6001 line is moot. Pending: lvl13/14/16/17/18 queued; then lvl10/15 (SOAK_TIMEOUT~2100). No conclusions overturned.
- **s5999 G4 (queued; r1/r2 folded s6000):** m6_lvl0_hold660_r1-3 enqueued (lvl0 was the only level without a 660 s hold). Fold verdicts from SOAK-RESULTS.md: 3x clean (rc=0, 0 crash/0 VI stall) closes lvl0 G4, then take G3 hangar white pillar stubs (s5964) or the plume si_addr=0x58 lldb loop; any abort => lldb/ASan backtrace + writer. No conclusions overturned this session.
- **s5998 G3 (single-source, visual):** lvl0 same-level pair (docs/g3_port_lvl0_oracle_pair_f5000.png vs retail lvl1 oracle) shows no port-only in-flight defect; G3 in-flight closed coarse. Next: G4 soaks of any level not yet held >=660 s with a keyed run, else G3 hangar white pillar stubs (s5964).
- **G1(d) s5997 CLOSED (PARTIAL-final):** a0=2/3 success requests come from per-level checkComplexObjectives gated on a level-specific BOOL set (lvl8: 5,A,E,15-18 via lv8_checkComplexObjectives+4560; bools set by trigger descriptors, identical in ctl/tele arms); counters 1/2/10 gate only lvl0. Forced hits move counters but cannot complete lvl8. lvl7 end = 3 deaths. Next: G4 crash/stall soaks across levels, then G3 render fidelity.
- **G1(d) s5996 (two-line, offline):** lvl7 ctl+tele end = THIRD a0=1 (death) requestMissionTransitionMode call -> lives exhausted -> game over, not a counter gate (supersedes s5995's threshold reading); lvl8 ctl+tele both end via a0=2 mask=4 ph=7 success requests with no TELE dependence. (d) = PARTIAL: forced hits move counters (lvl1-5,7,8) but no level end has been shown driven by them. Next: ask whether any level's objective counter reaching its target changes B14/phase (static: read objective-complete callers of requestMissionTransitionMode a0=2/3), else mark (d) closed-as-moves-counters and take G4/G3.
- (superseded by s5996) **G1(d) s5995:** lvl7 id=2 peak=3 matches s5474's counter[2]>=3 end threshold, but endMissionCleanup fires once in BOTH ctl and tele arms (lvl7, lvl8), ~2600 VIs after the reset - so counters move under TELE but counter->end link is undemonstrated. Next: find what triggers the ctl-arm end (requestMissionTransitionMode callers / timer), via one lldb bp on clearMissionObjectiveFlagsAndEnterPhaseSix in a ctl run.
- **s5989:** lvl1 colour question answered offline via RS64_RDP_BIN_PORT: soak s5989_lvl1_rdpbin queued; analyze with `python3 -I tools/rdpbin_tri_colors.py scratch/agent/s5989/lvl1_rdp.bin [ord]`.
- **s5988:** lvl1 ground zoom = structured tiling (not format garble); dark-tint vs legit open; per-tri colour dump queued (NEXT.md).
- **s5987:** plume attach g/h 20/20 clean (control PASS) -> plume loop closed as non-recurring. New G3 datum: port lvl1 frames 4000/4500 show flat dark mesh ground (eyeball, undecided; NEXT.md).

- **s5986:** s5982 lldb-launch plume soaks were a tooling null (getcwd EPERM, titles=0/3); attach recipes s5986_plume_attach_g/h queued (control + 10 boots each).
- **s5980 G4:** m6_lvl1_hold660_r1/r2 clean (664-665 s hold, 0 VI stall, 0 crash lines; single-source harness verdict). r3 + m6_lvl3_hold660 + m6_lvl6_hold660 queued. Fold verdicts; crash/stall => lldb backtrace + writer. If all clean: queue lvl2,4,5,7,8,9 holds, then loop title boots under lldb for the si_addr=0x58 plume SIGSEGV.
- **s5985 G1/G3:** all levels 0-9 hold >=300 s (lvl1-9 660 s) with 0 crash/0 VI stall; port lvl0 flight frame (docs/g3_port_lvl0_flight.png) shows terrain/craft/HUD, no eyeball defect vs retail lvl1 oracle (single-source). G3 in-flight closed at coarse level. Next: G1 (c)/(d) objective-counter forced hits per level, and title boots under lldb for plume si_addr=0x58.
- **s5978 G3 in-flight (single-source, visual):** unpaused retail lvl1 flight frame obtained (scratch/agent/s5978_retail_flight.sh: stop presses at 76 s, flight starts 77.4 s, fb-dump DELAY counts from FIRST 512-wide VI ~38 s not run start; frame docs/g3_retail_lvl1_flight_oracle.png, X-wing/reticle/radar/HUD/terrain/sky all render). Port flight frames (docs/g1_flight_contact_sheet.png) show the same element classes; no port-only defect visible at eyeball level. Not pixel-diffed (different camera/scene state). Next: same-camera comparison needs a port frame at lvl1 start; else G3 in-flight closed at coarse level, move to G4 soaks.
- **s5977 G3 in-flight oracle:** retail oracle reaches Tatooine mission 1 with alternating start/A presses (scratch/agent/s5977_retail_flight.sh; frame docs/g3_retail_lvl1_paused_oracle.png, paused). Supersedes 'oracle reaches boot/attract only'. Next: unpaused retail frame, then diff vs port lvl1 flight frame (NEXT.md). G2 stale PCM-compare NEXT discarded (closed by owner ear).

- **s5970 G3 (single-source):** Available Craft white pillar stubs are TEXTURED tris (cap DLs 0x3007936f0.. L=0x552038), not untextured shade-only (TINT_OM mode 3 negative; mode 4 rect control turned both pillars green). Next: log/force texture identity for cap tris (NEXT.md).
- **s5969 G3 (single-source):** ROGUESQ_TINT_OM (control passed): port-only othermode 0x504240/0x550231/0xf0a4001 tris on Select Craft are the floor-glow decal, platform and planet = legitimate, NOT the white-pillar stubs (those are on Available Craft, not reached). Next: same probe on Available Craft page, tint untextured white-shade tris.
- **s5968 G3 (single-source):** address-free descriptor pairing (s5968_descpair.py; ctl retN/N-1 tri-overlap 0.95, portN/N-1 0.80) retail-vs-port tri-weighted overlap 0.05 (keyJ 0.07). Retail loads uniform LOADBLOCK 1023-texel chunks (I16-ish fmt4/size2) with othermode 0x552230/0x552078; port loads variable 191-767 texel blocks, 0x552038/0x552230. Producers differ (cxd4 RSP vs rt64 HLE), so RDP command streams cannot pair by texture; texel bytes are not in either dump. Next: port-side per-draw texture hash + paint port-only stub tris a flat colour in rt64 to identify which DL/texture they come from (NEXT.md).
- **s5967 G3:** image_read_en (0x40) is NEVER consumed by rt64 (IM_RD only #defined; no OtherMode accessor/shader use) => the 0x552078 vs 0x552038 delta is not the stub cause; H-rdp-imgread refuted statically. Next: texel-content hash pairing of port-only tris (NEXT.md).
- **s5966 G3:** address-keyed retail/port frame pairing impossible (SETTIMG addr overlap 0.00, self-ctl 1.0; fmt-only 0.80). Next: texel-content hash pairing or in-run image_read_en toggle (NEXT.md).
- **s5965 G3 (single-source):** last-stable-frame census (s5965_last.py/s5965_bbox.py): retail 1115 tris vs port 425; retail 0x552078 tris cover y172-298, port 0x552038 tris y78-224, port-only states 0x504240/0x550231/0xf0a4001 exist (~40 tris). Frames are likely different scene states, so 0x40 delta is NOT yet a defect. Next: match by DL/texture content or camera, not 'last frame'.
- **s5964 G3 (top item, single-source):** same-page retail frame (scratch/agent/s5964/r12.png, Available Craft) vs port s4642: white pillar stubs are port-only (supersedes s5963's different-page caveat). RDP census (s5964_oth.py): retail othermode-lo 0x552078 vs port 0x552038 (image_read_en 0x40), frames not page-aligned. Next: page-align the retail rdp frame and port frame, list differing tri states, toggle image_read_en in rt64 in-run. See scratch/agent/NEXT.md.

- **s5962 lvl6 (d):** heartbeat control passed (hb ticks=1 both arms, 600 in tele), objsnap shows no change in either arm => lvl6 forced hits move no counter in the snapshotted table (H-B, single-source). H-C refuted. Next: G3 render fidelity (hangar artifacts list).

- s5956: lvl4 ctl5 (no TELE) also prints objsnap id=15 (8) + id=5 (4): id=15 cycling is baseline, lvl4 (d) NOT shown (supersedes s5949 / s5955 reading). lvl6 ctl has 0 objsnap; lvl6 tele + lvl7 pair queued.
- **G1(d) lvl1 (s5946, single-source):** TELE fires (0 vs 10) and objective-writer calls rise (BooleanCount 13->22), but [objcount] id=13 max stays 4 in both arms. Use `tools/g1_d_compare.sh N` for lvl2-5.
- **G1(d) lvl2/3 (s5948, single-source):** both pairs complete. TELE fires 0 vs 10 in each (control passes). lvl2: BooleanCount writes 4->17 (tele), but applyDatObjectiveTriggerEffect falls 114->42; lvl3: BooleanCount 0->8, applyDat 44->20. [objcount] val= line never printed in either arm (objcount_max empty). Reading: forced hits do reach the objective-count writer on lvl1/2/3 (H1 partial), but no end-gate/counter id is identified, so (d) is NOT yet PASS. Applied-effect count dropping under TELE is unexplained (tele ends runs earlier? or kills triggers) - needs per-run duration/phase gating. lvl5 pair still queued (soak_queue g1_lvl{4,5}_{ctl,tele}).
- **G1(d) lvl4 (s5949, single-source):** TELE 0 vs 10; objcount val max 2->3, applyDat 2->8, BooleanCount 7->10, no crash. First level where the objective counter moves under forced hits; applyDat rises here (opposite of lvl2/3).
- **G1(d) lvl5 ctl3 (s5954, single-source):** ctl 0 objsnap lines vs tele `id=2 0->1` only (TELE control fired). Forced hits move just fail counter id=2 on lvl5; (d) not PASS. g1_lvl4_tele5 queued for the lvl4 id; then lvl6 ctl+tele pair.
- **G1(d) lvl5 tele3 (s5953, single-source):** TELE 10 vs 0, applyDat 2->6, BooleanCount 4->5, objcount_max 0 both. New [objsnap] full-array diff (tools/apply_s5953_objsnap.py) built; g1_lvl5_tele4 queued to fold it, then lvl6 ctl+tele pair.
- **G1(d) lvl5 (s5952: ctl2/tele2 both reached mission clean, but tele2 recipe lacked ROGUESQ_TELE_BOLT so compare is void; tele3 queued; always diff tele vs ctl recipe)** (s5951, supersedes s5950's flag hypothesis; single-source):** NO_SAVE_WRITE is NOT the cause of the s5950 void pair. Believable then because the void arms carried the flag and s5715_lvl5a did not; but g1_lvl5_nsw (flag on) reached mission at 79 s and held 303 s clean, while g1_lvl5_nonsw (flag off) hit the 0x62BD00 viewer stall on att1 and passed on att2 (107 s). The viewer hang is intermittent, writer unknown. Re-queued g1_lvl5_ctl2/tele2; fold, then run g1_d_compare.sh 5. If the stall recurs, take an lldb backtrace (no guard patches). Recipes need their own `# SOAK_TIMEOUT=` header.
- **Owner listening report 2026-10-22 (G2):** after the s5668 compander fix and
  s5672 AI cadence fix, the fuzz is "way better than it used to be". Dialogue
  then confirmed by a live listen the same day: **dialogue is clean and there
  is no fuzz.** G2 audio fidelity is CLOSED by owner ear (independent of the
  s5669-s5674 PCM measurements, so two sources agree). Owner has watched missions
  1-~3 and the endgame-mission soak play; the window closing at the end of a
  soak hold is the harness SIGKILL, not a crash.

0ac. (s5994) G1(d) lvl7 id=2 0>2>3>0 and lvl8 id=6 0>1>2>3>4>0 move under TELE only (ctl absent); reset to 0, no end gate seen, target unknown => PARTIAL, single-source. Tool: tools/objsnap_summary.py.
0ab. (s5958) (d) status: lvl7 tele (10 hits, 0 crash) moves objsnap id=2 0->2->3->0, absent in ctl (single-source, one arm each); same counter as lvl5. lvl6 tele (tele=9) shows NO objsnap movement (not shown; widen snapshot via level-table objective slot). lvl8 ctl+tele queued (soak_queue/g1_lvl8_*), then lvl9.
0aa. (s5945) 10/15 unlock lever CONFIRMED (flight 104/135 s, 300 s hold clean) => (a)+(b) done for all levels 1-18; (c) done for 18/18 from existing fbd dumps (docs/g1_flight_contact_sheet.png, in-port only, no retail oracle). Now (d): fold g1_lvl{1..5}_tele vs g1_lvl{1,3}_ctl ([sph] TELE lines = positive control; compare [objcount]/[objwr]); extend to 6-18 if TELE fires.
0a. (s5944) Landed ROGUESQ_FORCE_PLANET_UNLOCK (byte 0x8013A663). Fold g1_lvl10_pu / g1_lvl15_pu: flight in ~400 s confirms the unlock-bit gate (then 10/15 route is instant); still viewer-stuck refutes it.
0. (s5942) Levels 10/15 viewer likely NOT stuck: lvl10 arms the G2 auto-advance at ~790 s (lvl5 exits via G1 button at once); soaks capped at 880 s killed it mid-exit. g1_lvl10long/15long (2100 s cap) queued; fold their verdicts. If they reach flight, mark 10/15 (a) and note the 13-min delay is retail-timer or a missing planet unlock bit (FORCE_UNLOCK writes only 0x8013B2F; G1 needs byte 0x8013A663 bit asset+1) -- forcing that bit would make it exit instantly.
0b. (s5941) Viewer is the retail planet-intro: getPlanetAssetForLevel maps level 0->0, 5->1, 10->2, 15->3, else 0xFF (skip); level 5 exits it, 10/15 do not. Next: find the runModelViewerLoop exit condition that differs for asset 2/3 (per-asset model/anim load or table), log it in one run for levels 5/10/15. Earlier note: Levels 10 and 15 (a+b) fail alike; 16a passes. s5940 REVISION: cineState=F7B80040 is NOT stale (level 11 shows it too). Main thread sits in menuOverlayInit -> runModelViewerLoop (frame-pumping, no deadlock; single-source, 2 samples). Next: read the menuOverlayInit branch (funcs_34.c ~7250, jal 0x800C9BF0 / 0x800C6900) for selection 10/15 vs 11 to decide whether the viewer is legit retail behaviour for those entries; then continue 16b..18b.
1. Re-run the corrected level-10 `a/b` coverage pair after the s5818
   diagnostic guard build; the guard audit does not change mission state or
   count as level coverage. Require `[lvsel]`, flight, and the 300-second hold.
2. Identify the writer/caller responsible for level-10’s missing immediate
   `cineBody` transition after section-4 DMA. Compare `ROGUESQ_LOG_LEVEL` and
   phase state around level 10’s `0x006A2900` edge against level 11’s
   `0x00696100` edge; do not try another timing-only arm. Do not count level 10
   until a level-appropriate flight origin is identified and held for 300 s.
3. Rerun level 10 `a/b` with the corrected transition control, then consume
   levels 11..18 from the repaired queue.
4. Sweep remaining levels for route+hold, then add framebuffer and forced-hit
   objective checks to every level.
5. Fold the human lv0 play when available; a loss, softlock, or broken render is
   a new root-cause datum, while a win establishes a tooling limitation.
6. After G1 coverage, pursue G3 render fidelity and any distinct G4 crash/stall
   datum. G2 owner listening remains the audio-fidelity follow-up.
7. Optional: qualify a fresh MIPS source-to-ELF patch after higher-priority G1.

## Evidence index

Use `PORTING-STATE.md` only through bounded grep/sed windows. Use
`docs/PROJECT-OVERVIEW.md` for migrated history, `docs/M5-AUDIO-PLAN.md` for
audio inventory, `docs/F5-UCODE-REFERENCE.md` for the microcode contract,
`docs/M6-OBJECTIVE-COUNTER-WRITERS.md` and `docs/M6-PHASE-MACHINE.md` for
mission logic, and `scratch/agent/SOAK-RESULTS.md` for queued verdicts.

- s5959: lvl8 (d) shown — tele forced hits step objsnap id=6 0->4->0, ctl silent. lvl9 pair queued.
- s5960: lvl9 (d) ambiguous (baseline cycle both arms). Objsnap now also diffs per frame in tickMissionObjectives (`[objsnap-t]`); g1_lvl6t ctl+tele queued to settle lvl6 (d).
- s5961: g1_lvl6t pair (0 crash/0 stall) printed ZERO `[objsnap-t]` lines in both arms, but no hook-ran control existed, so it is NOT evidence that lvl6 (d) is dead. Hook now prints `[objsnap-t] hb ticks=N` heartbeat; g1_lvl6u ctl+tele queued. Superseded: the s5960 plan that lvl6t "settles" lvl6 (d) - it was believable because the hook was in the binary, but presence of the string never proved the function is called per frame on lvl6. Next step #1 is to fold g1_lvl6u (heartbeat first).

- **s5963 G3 retail pixel oracle:** angrylion software RDP as m64p plugin gives real retail framebuffers (docs/G3-RETAIL-PIXEL-ORACLE.md, recipe scratch/agent/s5963_angry_fb.sh). Port hangar white pillar stubs are absent in retail (single-source). Next: same-page port/retail frame pair + DL/RDP-state diff for the stub draws.
- s5973: lvl1+lvl2 _zs soaks fold clean (sky and terrain textured, 0% black; single-source visual). lvl3,4,5,7,8,9 _zs still queued — fold them next (see NEXT.md); if any shows black sky, re-enable the fix narrowly for that DL. No conclusion overturned.
- s5971: FIX_ZERO_SHADE was the writer of white hangar pillar caps/shadows; default flipped OFF (verified hangar + lvl6; s5973-s5974 lvl1-4 sky/terrain fine; lvl5+lvl7 fine at s5975; lvl8+lvl9 fine at s5976 — all 9 levels verified, flip CLOSED; two lines: frame review + hangar/lvl6 earlier).

- (s5981) M6 660s holds: lvl1 3/3 and lvl3 1/1 clean (0 crash, 0 VI stall). lvl2,4,5,6,7,8,9 hold660 recipes queued; fold verdicts next, then title-boot plume SIGSEGV (si_addr=0x58) loop under lldb.
- (s5983) M6 660s holds lvl1-6 clean (single-source harness verdicts); lvl7-9 holds and two lldb plume title soaks still queued.

- (s5984) M6 660s holds lvl7/lvl8 clean (single-source). lvl9 hold + plume lldb soaks queued. G3: post-fix port lvl1 frames in docs/g3_port_lvl1_flight_postfix.png are a different level from the retail oracle frame (Tatooine=lvl0); g1_lvl0_oracle_pair queued for the same-level comparison.

- s5990 (single-source): lvl1 raw RDP capture shows ground/flight tris have BRIGHT vertex shade (mean 140-240, constant prim 4fd926b9) — H2' dark-shade ruled out; remaining H3' (TLUT/texel) / H1 / renderer-side. Tools: tools/rdpbin_tri_colors.py, tools/rdpbin_top_groups.py.

- s5991: lvl1 CI ground timgs use TLUT src 0x563980/0x563260; RDRAM-paired capture queued (s5991_lvl1_rdpbin_rdram) to decode palette vs observed colour. Next: tools/rdram_decode_tlut.py.
- s5993 (single-source, visual): lvl1 RDRAM fb (tools/fb_from_rdram.py, 512x358) shows textured grass/rock hills; the 'dark ground' is a cliff face with legit streaky texture. H4 not supported; g3-lvl1-mesh-ground CLOSED. G1(d) lvl7 (tele objsnap 33 vs 2) and lvl8 (objcount 0->4) show counter movement; lvl9 none. Next: G1(d) end-gate identification for lvl7/lvl8 via tools/apply_s5953_objsnap.py.
- s5992 (single-source): lvl1 ground TLUT 0x563980 / CI8 timgs decode to mid-bright red-brown (mean ~(125,25,20)); H3' (bad palette/texels) ruled out. With bright vertex shade (s5990) the darkening, if real, is renderer-side (H4) or legit (H1). Tool: tools/rdram_decode_tlut.py. Next: framebuffer-pixel vs predicted-colour check for one ord-7 CI group.
