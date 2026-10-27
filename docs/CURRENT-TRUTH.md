# Rogue Squadron 64 Recomp — current truth

Compact operational handoff, maintained after Session 6397 (2026-10-27).
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
  arithmetic is internally consistent, the corrected FD57 replay passes, and
  the independent cxd4 scalar replay agrees with the target chain.

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

Session 6388 built a fresh scalar cxd4 replay from the already-present
independent source and fed it the bounded FD57 witness window. It consumed
four records, matched all 24 consecutive accumulator lanes, and independently
produced FD57 on the VMADH lane-1 result. The prior comparator block was an
integration/parser defect caused by interleaved diagnostics in the full log,
not a missing reference capability. This refutes the RSP-emulation/clamp
disagreement hypothesis. It does not prove retail visual fidelity, so
`ROGUESQ_CULL_SPIKE` remains opt-in and the retail default is unchanged.

Session 6389 ran the G3c(a) arm table in one fresh Debug build. Retail and
draw-distance=2 reached mission origin and held 184/183 seconds with zero VI
stalls and crash markers. Their mission-phase edge scores were
`edge_excess_med=0.0286` and `0.0029`; both terrain controls passed. The
aspect-only and combined arms initially missed the retail title origin because
widescreen changes it from `0x00790400` to `0x00639238`. Session 6390 corrected
the route gate: the widescreen arm reached stable flight-equivalent
`width=796 origin=0x00639238` and held 131 seconds; the retail control reached
`0x00690400` and held 130 seconds. Both had zero VI stalls and crash markers,
alive-at-end, and positive framebuffer-hash controls. This validates the
widescreen mission gate but does not select H-edge-fog, H-edge-grid, or
H-edge-aspect; no runtime or default changed.

Session 6391 reran the four-arm edge table concurrently. Retail and dd2 reached
`0x00690400`; combined reached `width=796 origin=0x00639238`. The aspect-only
arm instead settled at `width=796 origin=0x0058B038`, so its route gate failed
despite alive-at-end, zero VI stalls, zero crash markers, and a positive
framebuffer control. The four edge scores are not a valid discriminator and
remain provisional; no visual hypothesis was selected.

Session 6393 reran the aspect-only arm in isolation with the same level-1
recipe. It held 184 seconds alive with zero VI stalls and zero crash markers;
the phase-5 DMA witness and framebuffer-hash positive controls fired. The
ordered VI transitions were `320@0x280`, `640@0xA1F500`, `1024@0xB20400`,
`640@0xA4B100`, then stable flight `1024@0x9D5800`. Thus the prior
`0x0058B038` expectation is not a stable route identity: the isolated run
reached valid wide flight with a different, allocator-dependent origin. This
rules out H-route-failure and makes the fixed-origin gate stale; the edge-arm
scores still need a rerun using phase/flight controls instead of an origin
allowlist.

Session 6394 ran the four-arm table with framebuffer dumps and the phase-5
writer witness. The first launch exposed a basic-grep regex defect in the
temporary route helper. After fixing it, aspect-only and combined reached
796-wide flight and fired 28 phase-5 target-store rows each with no crash
markers. Retail and dd2 did not pass the mission gate in the concurrent run;
their raw edge scores (`-0.0876` and `-0.0238`) are invalid alongside the
valid-but-not-comparable aspect (`-0.0259`) and combined (`-0.0001`) scores.
The positive terrain controls fired in all dump sets. This confirms the gate
still needs per-arm flight-width criteria; no visual hypothesis is selected.

Session 6392 completed a bounded M3 audit of host-facing RSP callback inputs.
`rs64_run_lle_gfx` now rejects null RDRAM, null shared DMEM, or null task before
locking or staging the task, and the optional audio-object reader rejects null
RDRAM before its first diagnostic read. The writer is the host callback
context, not guest game data; null is invalid. The Debug target rebuilt
successfully with only pre-existing warnings. No production null hit was
observed, so this is a safety invariant rather than evidence of a live crash.

Session 6395 reran the four edge arms with the per-arm width predicate. The
helper classified all four arms as `allattempts-failed` at its title gate, so
no arm was eligible for scoring. This gate result is stale: the final aspect
and combined logs each contain 28 phase-5 target-store rows, sustained
796-wide VI rows, framebuffer dumps, and zero crash markers; retail and dd2
contain sustained 640-wide rows and the same positive framebuffer controls,
but no phase-5 rows. The title predicate blocks valid wide-arm mission
evidence and cannot distinguish the edge hypotheses.

Session 6396 fixed the gate in `m6_god_common.sh`: optional-title arms now
wait for the literal autopilot marker, and wide-flight matching accepts the
emitted `width=796 ... origin=...` order. The clean concurrent rerun reached
mission on attempt 1 in all arms (retail/dd2 at 91s; aspect/combined at 33/34s),
passed 130s verification, and recorded zero crash lines and zero 30s VI stalls.
Framebuffer controls passed. Provisional post-flight edge scores were retail
`-0.0038`, dd2 `-0.0014`, aspect `0.0518`, combined `0.0158`; dump windows
were not phase-aligned across arms, so no edge hypothesis is selected.

Session 6397 scored the s6394 dumps filtered by flight width: all controls pass but
terrain_med spans 0.44 (retail) to 0.035 (dd2), so width does not align scene content
and the colour-fraction edge score is not a discriminator. No edge hypothesis selected;
next needs a phase-gated fixed-camera capture or a horizon-profile metric.

Session 6398: the phase-aligned horizon profile (tools/g3c_phase_horizon.py) is also not a discriminator: autopilot camera pose diverges between arms within ~1000 VIs of flight start (viewed frames in scratch/agent/view/s6398/), and retail already scores jump~0.33. Only a pose-locked capture (pinned camera matrix / no-input hover arm, or offline pose-matched frame pairs) can compare arms.

Session 6399: ROGUESQ_POSE_LOCK=1 (no-input hover, main.cpp) works in all 4 arms (s6400_posel.sh); arms share pose within ~0.15 at poselock n=60 and ~5 units at n=570, then drift with sim rate. Score only the early window (dumps from flight start to ~n=600) with tools/g3c_horizon_score.py. Matched-window scoring: jump_med retail .283 dd2 .217 aspect .314 combined .260 (single-source, weak) - dd-grid not supported, aspect side-edge weak lean.

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

1. Re-score the completed four-arm G3c(a) run using phase-aligned flight dump
   windows (640 retail/dd2, 796 aspect/combined), positive framebuffer hashes,
   and zero crash/stall markers. The title gate and width-order defects are
   fixed; do not use a fixed VI origin. Select fog/grid/aspect only when all
   four scores are from comparable flight phases. The height-byte fade arm is
   closed as ineffective.
2. Measure the owner-reported turning shake with the retail/FPS60/aspect arms
   if it remains actionable; current residual evidence is consistent with
   retail 30-Hz judder.
3. Then resume G1c draw-distance phase 2, G1d aspect, G1e frame rate, and
   G5 only in the stated ladder order. G4 and aim/steer work stay parked.

## Evidence index

Recent session findings are in `PORTING-STATE.md` sessions 6377–6385. Durable
background, closed threads, and the archived long backlog are in
`docs/PROJECT-OVERVIEW.md`. Queued-soak verdicts are in
`scratch/agent/SOAK-RESULTS.md`; do not treat a queued repeat soak as a work
unit.
