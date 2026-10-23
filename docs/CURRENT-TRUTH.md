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

## Next steps (single monotonic backlog)
- **s6044 G1c:** retail dd1w tblwatch: tbl 0x80136DC4 never zero (3 nonzero swaps); death churn (lives=12736) also in retail => not dd-specific. Pending: s6043_dd2w tblwatch (queued) decides H2 (dd-specific zeroing: name writer) vs symptom (lldb bt of dd2s SIGBUS). Single-source.
- **s6045 G1c:** dd2w: tblwatch (call-entry sampler) never sees tbl==0 (3 nonzero swaps) yet SIGBUS regs show base=0x80000000 (tbl==0) mid-call. s6045_dd2lw FAILED as a harness (macOS has no timeout cmd; lldb never attached, 0 stops, no positive control = not a null); requeued as s6046_dd2lw (perl alarm). Pending: lldb hw write-watch 0x80136DC4 names the zeroing writer. Single-source.
- **s6046 G1c:** s6046_dd2lw also void: lldb watched a guessed host address 0x380136DC4 (RDRAM base is an mmap; address unreadable), watch never fired, no positive control. Overturned belief: "host addr = 0x38000000 + vaddr" (believable because SIGBUS fault addresses looked like 0x37e..., but the base is per-run). Requeued as s6047_dd2lw: breakpoint on streamTerrainGridCellsByDistance, watch x0+0x136DC4 (lldb_tblwatch2.cmds). Next step #1 unchanged: fold s6047 (control = stops at table swaps; zero-word stop bt names writer).
- **s6037 G1c:** dd2 (2x) crashed 5/5 in getGridCellValueAt: footprint window unclamped, spills past terrain (x0=3 w=33 on 32). Window DID scale (w 16->32). apply_s6037_ddclamp.py clamps to terrain dims when knob!=1; arms s6037_dd15c/dd2c/dd3c queued - fold: crash gone? w scaling at lvl1 64x64 stage, distant-terrain fb fraction, frame time. Then levels 5 and 10 holds.
- **s6038 G1c:** ddclamp works (window <= terrain) but did NOT fix dd2: 5/5 SIGSEGV moved to streamTerrainGridCellsByDistance 0x80042D88 (`lb 3(v1)`, v1=*(0x80130004)+(cell&0x1FFF)*30 == 0), and dd15c (1.5x) aborted on a NaN assert in vec3Cross at 88 s. Writer of the NULL not yet named. apply_s6038_cellprobe.py logs [cellprobe]; soaks s6038_dd2p/dd15p queued. dd3c parked in /tmp.
- **s6035 G1c (code-read, single-source):** footprint polygon has NO clamp; scale knob is float 0x8009DEAC (14.5; DEB0 recomputed each call). Hard limits: terrain w/h and 64-wide window bitmaps (0x80132DB0/0x80133DB0). Unresolved: why earlier x2/x3 arms gave only +4%/+7%. Next: ROGUESQ_DRAW_DISTANCE scaling DEAC + read queued [gridlog] arms.
- **s6034 G1c (RESULT):** retail lvl1: requested cells 504-1148 < pool cap 2048, window ~35x29 of 64x64 terrain => cap and terrain-end NOT binding; limit is the footprint window written by binPolygonIntoTerrainGrid (single run, single-source). Next: log its input polygon + clamp.
- **s6034 G1c:** stream pool (0x18 nodes, cap lhu 0x80130C4C) + window 0x80132DB0..BC + terrain w/h 0x80136DF8/FA bound the visible set (single-source, code read). `[gridlog]` instrument (ROGUESQ_DD_GRIDLOG=1) built; arms s6034_g1c_ret/posab/cell2 queued, fold kept-vs-cap next.
- **s6033 G1c:** far-plane arms folded: far025 -45% tri/task (control OK), far2 flat (+0.3%), far4 partial -11%. ALL scalar levers (footprint, FOV, LOD, cell, igrid, fog, far) are shrink-only/flat => retail cap is not a tunable scalar. Next: H-data (is lvl1 terrain extent baked: dump grid cell dims/world extent from allocAndInitGridCellArray and compare to camera far distance) then L-budget (0x80137A68 buffer, rs_malloc 200*(n/10)). near4 arm still queued.
- **s6031 G1c:** far-plane knob ROGUESQ_DD_FAR/DD_NEAR (tools/apply_s6031_far.py, guPerspective args in setupCameraMatrices 0x80016D10) built; arms s6031_g1c_farret/far025/far2/far4/near4 were staged but NOT queued until s6032 (copied from scratch/agent/s6031_arms/ to soak_queue/); fold results next. Then L-budget.
- **s6023 G1c:** FOV 0x130C50 and LOD-table arms (fov15/fov025/lod2/lod025) queued; fold results next.
- **s6027 G1c:** ROGUESQ_DD_CELLMUL (pre-alloc cell count at allocAndInitGridCellArray entry, tools/apply_s6027_cellmul.py) built; arms s6027_g1c_cell025 / cell2 queued, results pending in SOAK-RESULTS.md. Then fog arm.
- **s6030 G1c:** fog arms folded: FORCE_FOG magenta 750-2900 px/frame (0.4-1.6%) as a thin sliver vs 0 in control => fog does not tint terrain; L-fade closed (single-source). Next: far-plane / L-radius, then L-budget.
- **s6028 G1c:** s6027 cell-count arms folded: x0.25 532.7 / retail 578.7 / x2 629.2 tri/task (-8% / +8.7%, cross-run, noise ~5-7%) => cell count is a weak monotonic lever, not the extend lever (single-source). Next: ROGUESQ_FORCE_FOG in-flight arm (H-fade), then far-plane.
- **s6025 G1c:** LOD-table arms (0x9ECB0 x2/x0.25) +6.2%/+4.9% tri/task, x0.25 control failed => table inert for lvl1 flight (not extend lever, not refuted by a valid control either). igrid2/igrid025 still queued, fold next.
- **s6024 G1c:** FOV 0x130C50 arms: x0.25 control -24.6% tri/task, x1.5 -10.3% (and a self-inflicted vec3Cross NaN abort at 183 s) => FOV is shrink-only too. Int-mode knob (ROGUESQ_DD_IADDRS/IMUL) built; igrid2/igrid025 arms queued on 0x137A58/0x137A60. LOD arms (s6023) pending.
- **s6022 G1c:** r2A/r3A (0x9DEAC x2/x3): per-task tri +4%/+7%, total tri -5%/-16% => footprint scalar is shrink-only (posAB x0.25 = -31%); not the extend lever. Cap lives elsewhere: grid buffer size (0x80137A68, rs_malloc 200*(n/10)) or FOV 0x80130C50; LOD 0x9ECB0 and fog arms unrun.
- **s6021 G1c:** 0x8009DEAC (14.5) is the live footprint scalar: posAB (A+B at 0.25x) tri 641->443 (-31%) vs own retail arm, B alone (0x9DEB0) 581->621 inert. r2A/r3A queued; rise = L-radius. Single-source (tri counts).
- **s6020 G1c:** rodata floats 0x3A4FC..0x3A50C are pooled constants (0.5/512/1), pos2 control failed; real footprint scalars are RAM floats 0x8009DEAC/0x8009DEB0 (buildVisibleTerrainGridAroundCamera). Arms s6020_g1c_posB/posAB/r2B queued; read `[g1c] state=` bins with tri>=50 filter.
- **s6019 G1c:** pos control FAILED (0x8003A538 is a 0.5 grid-snap, not radius; s6018 arms void). Lever retargeted to rodata floats 0x3A4FC..0x3A50C (read by streamTerrainGridCellsByDistance 0x80042B50), ROGUESQ_DD_ADDRS overrides. Arms s6019_g1c_pos2 + s6018_g1c_r2 queued. LOD (0x8009ECB0) control still unrun. Fog (L-fade) untouched.
- **Owner request 2026-10-23 (queued as G1c, after G1b):** extend draw distance so
  more landscape renders than retail did. Find the limiting lever (distance fade,
  terrain radius, LOD index 0x80137CE4, buffer caps) and expose it as opt-in
  ROGUESQ_DRAW_DISTANCE, default retail. Full spec: ITERATION.md item 3c G1c.
- **Owner report 2026-10-23 (queued as G1b, after the G1 level sweep):** ~70% of
  missions play flawlessly; the rest intermittently slow down game-wide
  ("buffering"), on busy scenes and on bare landscape alike. Never measured
  (no wall-clock in logs). Hypotheses and the single discriminating instrument
  are in `tools/agent/ITERATION.md` 3c G1b.
- **s6014 (G1b measured):** 217/748 s of lvl1 and ~26% of hangar/menu seconds have gfx send_dl at 130-210 ms/task (vs ~9) with cpu~wall, so the game runs ~5 gfx tasks/s while VI stays 60. Host load/QoS/log volume do NOT co-vary. Open: RT64/RSP work vs harness instrumentation (8 s cadence = FB dump). Quiet-vs-loud arms queued (s6014_g1b_*); then `sample` the game during a slow second.
- **s6015 (arm fold):** the s6014 "quiet" arm FAILED its positive control (151 vs 171 KB/s; volume is ungated [m4-y8000]/[s3290-stall]/[s3294-stall]/[s3295-disp], not the FBH/TRI/DRAWN/OBJBOOL/HUDBIT knobs). So "log volume does not co-vary" in the line above is only "those five knobs do not matter" (slow fraction loud 17.6% vs quiet 23.2%, single-source); H-log remains untested but a-priori weak (~150 KB/s vs 130-210 ms stalls). Next: soak s6015_g1b_sample (`sample` of the game on slow seconds) - read scratch/agent/g1b_samples/s6015/.
- **s6013:** ftz0/ftz1 clean (opt-in stays off). G1b instrument ROGUESQ_G1B built; soaks s6013_g1b_lvl1/lvl10 queued (NEXT.md).
- **s6012:** FP div census closed (no guard); opt-in ROGUESQ_FTZ added, soaks s6012_ftz1/0 queued (NEXT.md).
- **s6000 G4:** lvl0 hold r1+r2 clean (662 s, 0 stall, 0 crash); r3 pending in the queue.
- **s6001 G4:** lvl0 3/3 clean 660 s holds (closed). The pillar-stub Next items below (s5964/s5970/s5999) are STALE - s5971 fixed them (FIX_ZERO_SHADE off). Queued m6_lvl{11-14,16-18}_hold660; fold, then G1(c) framebuffer check lvl10-18. s6008: hangar route 3/3 clean (att=1); d/e/f queued.
- **s6007:** hangar-route soaks a/b folded: both att=1, 600 s hold, 0 crash/0 VI stall (n=2, not enough to revise the ~1/3-3/5 flake rate). Run c still queued.
- **s6006 G4 CLOSED 0-18:** lvl18 662 s hold clean (0 stall/0 crash); all levels 0-18 held. Queued s6006_hangar_route_{a,b,c}; fold from SOAK-RESULTS.md (any abort => lldb/ASan backtrace + writer), then G5/parked hangar items.
- **s6005 G4/G1(c):** lvl16 (662 s) and lvl17 (662 s) holds: 0 stall, 0 crash, but both end in MISSION FAILED/GAME OVER (blind autopilot dies) and the harness cycles fail->results->select->relaunch (3x and 9x), all clean. lvl17/18 frames show terrain+craft+HUD (docs/g1_lvl16_18_contact.png; single-source). Next: fold lvl18 hold, then G3.
- **s6004 G4/G1(c):** lvl10 (665 s) and lvl15 (661 s) holds clean (0 stall/0 crash). G1(c) eyeball check lvl10-15 passes (docs/g1_lvl10_15_contact.png: terrain, craft, HUD; single-source). Next: fold lvl16/17/18 holds, then G1(c) contact sheet for 16-18; G4 closes for 0-18 if clean.
- **s6009 G4 hangar route:** 7/7 first-attempt launches clean (a-g: att=1, 600 s hold, 0 stall, 0 crash), single-source harness; h,i queued. If 9/9, downgrade the ~1/3-3/5 flake note (line ~69) to 'not reproduced post FIX_ZERO_SHADE-off'.
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


## G1b update (s6016)
Gfx thread hot spot found by `sample` (s6015): ~80% of gfx samples in O(n^2) g_s4272_sh scan at dpc_bridge.cpp:2748 + s4285 diag loop; fixed s6016 (hash index, ROGUESQ_S4285 gate). Verify with soak s6016_g1b_scanfix vs s6014 loud baseline (17.6% slow seconds). H-host/H-shader/H-log not supported.

- **s6017 (G1b CLOSED):** s6016 hash-index fix: lvl1 slow seconds 132/748 (17.6%) -> 0/748, mean sd_wall 31.4 -> 10.3 ms, tasks/s 25.5 -> 30.2, 0 crash/stall. Cause was our own O(n^2) scan in rsp_dpc_submit. Reuse the `[g1b]` instrument (ROGUESQ_G1B=1) as the frame-time baseline for G1c. Next: G1c.

- s6036 G1c: ROGUESQ_DRAW_DISTANCE knob landed (scales DEAC read at 0x80043918; DEAC has runtime writers). Soaks s6036_dd1/2/3 queued; fold window w (must stay <=64) and distant-terrain fraction. Gridlog output lives in scratch/agent/m6/*/run.log.

- s6039: cellprobe address bug fixed (table ptr is t0+4, t0=0x80136DC0, not 0x80130004); dd2 crash = NULL cell descriptor table at that struct, corrected probe queued (s6039_dd2q).

- **s6040 G1c:** cellprobe: crash struct is static 0x80136DC0 (tbl=*(+4)==0), not *(0x80130004). ddclamp treated window counts as maxima; rewritten (clamp start+count to terrain, w*d<=pool cap). Seen req=420>cap=400 once. Arms s6040_dd2r/dd3r queued; if tbl==0 persists, watch 0x80136DC4 writer.
- **s6043 G1c:** gate worked (dd15s/dd2s reach mission) but both then die in-mission ~t=98s with tbl 0x80136DC4==0 and window x0=0x7F7F0017 (poison high half; dd2s SIGBUS deterministic). Writer unnamed. tblwatch probe + s6043_dd1w/dd2w arms queued (retail control); fold: does retail also zero tbl mid-mission?
- **s6042 G1c:** dd2 failures (4 of 5 arms) are `nomission` = crash BEFORE mission start with terrain table 0x80136DC4==0 (not a corrupt writer); knob+clamp now gated on table != 0; arms s6042_dd15s/dd2s/dd3s queued - fold: dd2 reaches mission? remaining in-mission deaths (dd2r died_in_verify) need a backtrace.
- **s6041 G1c:** dd2r failures show poison-like window x0~0x7F7F7F97 that the clamp cannot produce => clamp is not the root cause; dd3r crashes at +9960 wild ptr. See NEXT.md.

- **s6048 G1c (lldb, single-source until soaks):** the dd2/dd3 crashes' zeroed terrain table (0x80136DC4) is overwritten by scanConvertTriangleToSpanTable's byte stores (0x7f clamps) at row ~384; span table holds 80 rows x 64 cols, row range unclamped. Guard tools/apply_s6048_spanbound.py (dd!=1 only). Fold s6048_dd1b/2b/3b: 2x/3x should hold 300 s with [spanbound] skips; then measure distant-terrain fraction per step and clamp the footprint properly instead of skipping if skips are large.
