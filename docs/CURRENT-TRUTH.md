# Rogue Squadron 64 Recomp — current truth

Compact operational handoff, maintained after Session 6392 (2026-10-26).
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

Session 6392 completed a bounded M3 audit of host-facing RSP callback inputs.
`rs64_run_lle_gfx` now rejects null RDRAM, null shared DMEM, or null task before
locking or staging the task, and the optional audio-object reader rejects null
RDRAM before its first diagnostic read. The writer is the host callback
context, not guest game data; null is invalid. The Debug target rebuilt
successfully with only pre-existing warnings. No production null hit was
observed, so this is a safety invariant rather than evidence of a live crash.

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

1. Diagnose the aspect-only route mismatch: run that arm alone with the same
   recipe and record every phase/origin transition. Determine whether
   `0x0058B038` is a legitimate aspect route, a stale gate, or a concurrency
   artifact before repeating the four-arm edge table. The height-byte fade arm
   is closed as ineffective.
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
