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
- **Owner listening report 2026-10-22 (G2):** after the s5668 compander fix and
  s5672 AI cadence fix, the fuzz is "way better than it used to be". Dialogue
  then confirmed by a live listen the same day: **dialogue is clean and there
  is no fuzz.** G2 audio fidelity is CLOSED by owner ear (independent of the
  s5669-s5674 PCM measurements, so two sources agree). Owner has watched missions
  1-~3 and the endgame-mission soak play; the window closing at the end of a
  soak hold is the harness SIGKILL, not a crash.

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
