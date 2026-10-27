# Rogue Squadron 64 Recomp — current truth

Compact operational handoff, maintained after Session 6383 (2026-10-26).
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
  arithmetic is internally consistent but its clamp discriminator lacks the
  FD57 positive control in the latest runs.

## Current frontier: G3c(b) spike-line discriminator

Session 6378 produced the known FD57 wedge route: a 128-op VU ring showed a
legitimate near-zero-w clip ratio chain. Session 6379 replayed 90 accumulator
links with 0 mismatches. Session 6380 added all-lane post-`vd` capture and the
clamp replay, but two runs produced 3,328 and 3,072 rows, 10 generic saturated
matches, and zero FD57 rows. Sessions 6381–6382 were checkpoint retries only.
No clamp conclusion or mitigation is qualified.

The immediate work unit is the bounded offline comparison in
`scratch/agent/NEXT.md`: compare s6380 and s6380long against the known s6378
route, phase, origin, task, key, and control markers. Only a route mismatch
justifies one corrected capture. Matching route with no FD57 selects timing;
FD57 in `[spike-st]` but not `[spike-vu8]` selects instrumentation.

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

1. Complete the s6383 FD57 route audit from `scratch/agent/NEXT.md`; capture
   once only if the audit identifies a smallest route/input correction.
2. Finish G3c(b) with an independent/reference-RSP comparison or owner’s
   decision on `ROGUESQ_CULL_SPIKE`; do not infer clamp behavior from the
   unqualified s6380 run.
3. Finish G3c(a) only with a phase-gated edge measurement and owner-viewable
   frames; the height-byte fade arm is closed as ineffective.
4. Measure the owner-reported turning shake with the retail/FPS60/aspect arms
   if it remains actionable; current residual evidence is consistent with
   retail 30-Hz judder.
5. Then resume G1c draw-distance phase 2, G1d aspect, G1e frame rate, and
   G5 only in the stated ladder order. G4 and aim/steer work stay parked.

## Evidence index

Recent session findings are in `PORTING-STATE.md` sessions 6377–6382. Durable
background, closed threads, and the archived long backlog are in
`docs/PROJECT-OVERVIEW.md`. Queued-soak verdicts are in
`scratch/agent/SOAK-RESULTS.md`; do not treat a queued repeat soak as a work
unit.
