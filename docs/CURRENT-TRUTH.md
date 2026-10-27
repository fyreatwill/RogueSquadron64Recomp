# Rogue Squadron 64 Recomp — current truth

Compact operational handoff, maintained after Session 6386 (2026-10-26).
`PORTING-STATE.md` is the chronological ledger. Historical detail and the
retired CURRENT-TRUTH backlog are in `docs/PROJECT-OVERVIEW.md`.

## Headline

- The qualified route boots attribution, N64 logo, intro, Factor 5 logo, title,
  hangar, and mission origins; mission input reaches flight code.
- M5 audio de-stubbing, M3 idiom audits, generated-symbol renaming, and M6
  first-mission endurance are closed. G4 crash hunting is parked after clean
  coverage. G1 is mission coverage and visual quality, not autopilot work.
- Current owner frontier is G3c: terrain-edge fade, spike-line ground truth,
  and turning-camera shake. G3c(a) height-byte fade was null; G3c(b)'s VU
  arithmetic is internally consistent and the corrected FD57 replay passes,
  but independent/reference-RSP ground truth is still open.

## Current frontier: G3c(b) spike-line discriminator

Session 6378 produced the known FD57 wedge route: a 128-op VU ring showed a
legitimate near-zero-w clip ratio chain. Session 6379 replayed 90 accumulator
links with 0 mismatches. The s6380 route audit corrected the prior zero-FD57
interpretation: s6380 had a `nomission-att1` retry, then `att=2 mission`, while
s6380long matched the reference `att=1 mission` route. s6380long recorded 185
`[spike-st]` rows and 23,680 `[spike-vu8]` rows, including 155 and 546 FD57
rows respectively. The target positive control therefore passes in both
witness streams. Session 6385 replayed the corrected FD57 post-`vd` ring:
2 rows, 8/8 accumulator matches, and 8/8 result matches, with no saturation.
This rules out a replay arithmetic error in that ring, but does not establish
retail/reference-RSP equivalence or explain the visible wedge. Session 6386
found the independent cxd4 RSP sources and built their scalar VU objects, but
the offline comparator segfaulted reproducibly around parsed row 95 after
consuming 88 rows; it never reached a valid FD57 comparison. The Ares-derived
header path is the runtime implementation and is not independent ground truth.

The independent comparison is currently capability-blocked; the route audit
still passes its positive control. The next gate is the owner's
`ROGUESQ_CULL_SPIKE` decision, not another game run.

## G1 mission coverage

Playable levels are 0..18 (`NUM_LEVELS=0x13`; 19 and 20 are sentinels). Levels
1–9 and 11–18 have route/hold coverage; levels 10 and 15 need the planet
unlock or its long retail intro. Verification still needs framebuffer evidence
of terrain, craft, and HUD plus a forced-hit objective response. Mission wins,
autopilot aim, and mission-to-mission progression are owner playtest scope.

## Durable constraints

- Retail defaults remain unchanged. Opt-ins include draw distance, aspect,
  FPS60, spike culling, and audio control. Do not make an opt-in default from
  a single-source result.
- `ROGUESQ_DRAW_DISTANCE` is clean through 2x. Higher settings exhaust the
  display-list chunk supply; no mitigation is acceptable without naming the
  writer and establishing value legitimacy.
- Wide rendering uses runtime RAM-top handling and a larger reported memory
  arm; default remains 4:3/retail. Native hangar artifacts remain parked.
- The title plume is parked after clean boots. Reopen only on new evidence.
- Read `docs/F5-UCODE-REFERENCE.md` before interpreting Factor 5 streams.
  Ground truth must precede new instrumentation; every null needs a positive
  control and two independent lines of evidence before changing this file.
- Generated diagnostics must survive regeneration through fixup tooling.
  Never reset, clean, checkout, or update submodules. If editing `lib/`, run
  `./submodule-patches/export.sh` and commit the refreshed patches.

## Next steps (single monotonic backlog)

1. Finish G3c(b) with the owner's decision on `ROGUESQ_CULL_SPIKE`; the
   independent cxd4 comparison is capability-blocked after a reproducible
   offline comparator crash, so do not infer clamp behavior from the internally
   consistent but single-source s6380long replay.
2. Finish G3c(a) only with a phase-gated edge measurement and owner-viewable
   frames; the height-byte fade arm is closed as ineffective.
3. Measure the owner-reported turning shake with the retail/FPS60/aspect arms
   if it remains actionable; current residual evidence is consistent with
   retail 30-Hz judder.
4. Then resume G1c draw-distance phase 2, G1d aspect, G1e frame rate, and
   G5 only in the stated ladder order. G4 and aim/steer work stay parked.

## Evidence index

Recent session findings are in `PORTING-STATE.md` sessions 6377–6385. Durable
background, closed threads, and the archived long backlog are in
`docs/PROJECT-OVERVIEW.md`. Queued-soak verdicts are in
`scratch/agent/SOAK-RESULTS.md`; do not treat a queued repeat soak as a work
unit.
