# Rogue Squadron 64 Recomp — current truth

Compact operational handoff, maintained after Session 6511 (2026-10-27).
`PORTING-STATE.md` is the chronological ledger. Historical detail and the
retired CURRENT-TRUTH backlog are in `docs/PROJECT-OVERVIEW.md`.

## Headline

- The qualified route boots attribution, N64 logo, intro, Factor 5 logo, title,
  hangar, and mission origins; mission input reaches flight code.
- M5 audio de-stubbing, M3 idiom audits, generated-symbol renaming, and M6
  first-mission endurance are closed. G4 crash hunting is parked after clean
  coverage. G1 is mission coverage and visual quality, not autopilot work.
- Current owner frontier is G1c's span-grid legitimacy boundary, followed by
  G3c: terrain-edge fade, spike-line ground truth, and turning-camera shake.
  G3c(a) height-byte fade was null; G3c(b)'s VU
  arithmetic is internally consistent, the corrected FD57 replay passes, and
  the independent cxd4 scalar replay agrees with the target chain.

Session 6506 replaced the invalid cross-function cumulative join with an
invocation-local writer baseline and atomic key in the existing s650 fixup
path. The Debug build passed. The prescribed pinned dd1/dd4 run produced 14
dd1 and 8 dd4 `[postring]` rows, including nonempty and EMPTY controls; every
row had `key==seq`, positive writer activity, and nonnegative interval deltas.
The first dd1 interval was `144,144,0,0`; subsequent dd1 rows were `6..9,6..9,0,0`,
while dd4 rows were `49..53,49..53,0,0`. This removes the unsigned-underflow
join defect and shows the observed interval activity is at DB4/DC0, not EBC/EC4.
The result identifies the boundary/race artifact but does not yet prove which
writer changed the post-bin table; no game behavior or default changed.

Session 6508 added a regeneration-safe per-site byte mask and post-table diff
to that keyed probe. The Debug build passed. The pinned run held both dd1 and
dd4 for 151 s with zero VI stalls/crash markers; dd1 produced 14 keyed rows
and dd4 108, including nonempty and EMPTY controls. On the initial matching
controls, dd1 changed byte mask 0x80 with interval mask DC0=0x80, then 0x03
with DC0=0x03; dd4 changed 0x800000 then 0x18 with DC0 matching those masks.
DB4, EBC, and EC4 interval masks were zero in those controls. This selects
the concrete 0x80042DC0 writer for the observed post-bin change in two
independent arms. Later rows retain a nonzero diff with zero new interval
mask, so this does not claim every later mutation is DC0. No mitigation or
default changed.

Session 6509 classified the selected DC0 writer's live target/value in the same
keyed probe. The regeneration-safe instrument passed a Debug build. Clean
per-attempt evidence supplied dd1 with 14 keyed rows (6 EMPTY, 8 nonempty) and
dd4 with 31 keyed rows (23 EMPTY, 8 nonempty), with zero `[CRASH]` markers;
the positive controls therefore passed. Every sampled DC0 store wrote `0x7F`.
Both arms produced targets outside the 24-byte span table
`0x80130DB0..0x80130DC7`; dd4 labels these `span_mode=active_accept`, meaning
the existing draw-distance bound accepted addresses beyond the table, while
dd1 labels the bound `disabled`. This selects H-DC0-corrupt over
H-DC0-legitimate: the writer is `streamTerrainGridCellsByDistance` at
`0x80042DC0`, and its `ctx->r21` target path is the next upstream boundary to
audit. No guard or gameplay behavior changed.

Session 6510 reconstructed that target path in one paired pinned run. The
regeneration-safe probe logged 512 DC0 rows in each arm; dd1 had 15 keyed
postring rows and dd4 had 8, with the existing nonempty/EMPTY controls, zero
crash markers, and zero 30-second VI stalls. Every sampled row reconstructed
`addr` exactly as `r5 + r14`, where `r5 = r20 + (r30 << 6)` and `r14 =
0x80130DB0`; `r3` was always `0x7F`. The base is an offset into the 64-byte
row grid, not a host pointer, and the OUT addresses are the expected
row/inner positions beyond the first 24 bytes. This selects H-coherent-stream
over H-corrupt-input and overturns s6509's 24-byte-table interpretation: the
span table is the larger grid already admitted by the `0x2000` bound. No guard,
game behavior, or default changed.

Session 6511 completed the full-grid discriminator in one paired pinned run.
The regenerated probe passed its positive controls with 14 keyed dd1 rows and
8 keyed dd4 rows, no crash/abort markers, and no observed VI stall. Every row
reported a 64x64, 8192-byte span grid with non-127 contents. Full-range writer
activity was observed from DB4 and DC0 in both arms; dd1 addresses began near
`0x80130DB0` and dd4 addresses reached the outer grid, while EBC/EC4 had no
full-grid writes in the sampled rows. This refutes H-short-init (only the first
24 bytes initialized) and supports H-full-grid: the DC0 stream writes are
coherent accesses into a real 64x64 grid, not stale bytes outside a 24-byte
table. It does not yet prove whether the dd4 EMPTY result is a legitimate
span-table filter outcome or identify any initialization writer outside the
four instrumented sites. No guard, game behavior, or default changed.

Session 6500 extended the byte-store census with a 64-entry sequence-keyed
post-bin ring and bounded writer summary. The final pinned dd1/dd4 run reached
mission and held 151/151 s with zero VI stalls and crash markers. dd1 supplied
6 EMPTY and 8 nonempty controls; dd4 supplied 100 EMPTY and 8 nonempty
controls. Every joined row had `seq==ret==post`. dd4 EMPTY seq 269 had a
meaningful post table (`127,246,255,...`) while the stream sample was all 127,
so H-bin is refuted for the matching control and H-writer is selected. The
cumulative writer summary proves activity at 0x80042DB4 and 0x80042DC0, but
does not identify which site changed that row. No mitigation or default changed.

Session 6502 ran the prescribed per-return writer probe after fixing two join
defects. The first run passed controls but shared counters produced impossible
underflows; a thread-local retry showed that the bin and stream calls can cross
host threads, so thread-local state was not a valid key. The final single-global
snapshot added guest-thread IDs: both arms were clean (151/152 s, zero VI stalls
and crash markers), dd1 supplied 6 EMPTY/8 nonempty rows, and dd4 supplied 100
EMPTY/8 nonempty rows. The guest IDs matched, and 0x80042DB4 had positive count
deltas on the matching rows, but 0x80042EBC still had an impossible unsigned
count underflow. The writer attribution is therefore not yet valid; retain
H-writer over H-bin from s6500, but do not name an exact site. No runtime
default or gameplay behavior changed.

Session 6499 added a complete byte-store census and a post-bin return snapshot.
The corrected pinned dd1/dd4 run reached mission for 151 s; dd1 had 6 EMPTY and
8 nonempty controls, while dd4 had 25 EMPTY and 8 nonempty rows (dd4 also
reported 37 crash markers, so its hold is diagnostic only). Every joined row
had `seq==ret==post`. In dd1 EMPTY seq 2, the post-return table contained
non-127 values (`38,38,...`) with 28 meaningful stores, but the stream sample
was all sentinel/clear values with 40 stores. A later stream-path writer,
among `0x80042DB4`, `0x80042DC0`, `0x80042EBC`, and `0x80042EC4`, demonstrably
changes the table after rasterizer return; this selects H-writer for the dd1
EMPTY control. The dd4 EMPTY rows occur after the bounded post log, so H-bin
versus H-writer is not selected for dd4. No mitigation or default changed.

## Current frontier: G3c(b) spike-line discriminator

s6440: no retail/LLE reference exists locally (see docs/G3C-SPIKE-REFERENCE.md); H-retail unresolved, H-rt64 offline model (s6441, tools/g3c_spike_rdp_model.py): 16 of 79 logged wedges leave 4-850 px after the RDP scissor, so hardware would draw them too - H-rt64 not supported (single-source); CULL_SPIKE stays opt-in.

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

Session 6401: pose-matched contact sheet (scratch/agent/view/s6401/sheet.png) shows sky-coloured holes cut into terrain in dd2 (sawtooth), aspect (rectangle) and combined (wedge) but not retail; outer-column scalars are noise and the s6399 aspect lean is withdrawn. Edge is likely missing geometry, single frame per arm.

Session 6467: the first dd1-vs-dd8 capture used the shared attitude reference but
the existing pose lock excludes position; at sample n=300 the arms differed by
about 16 world units, and the contact sheet paired different route phases. The
fixed version added opt-in `ROGUESQ_POSE_PIN_POSITION=1` and rebuilt cleanly;
both arms then held 151 s with zero VI stalls/crash lines. Dump ordinal still is
not a phase key: the attempted sheet still paired title/hangar/craft-select
frames against flight frames. Terrain scores and that sheet are invalid for
selecting H-terrain or H-address-limit. Next discriminator must join dumps to
the logged flight VI/origin, not pair equal dump numbers.

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

Session 6503 was a checkpoint close-out only. Session 6504 completed the
handoff without rerunning the probe. Session 6505 completed the offline audit:
there is one counter declaration, no reset or duplicate assignment, and every
live 0x80042EBC store calls the writer helper. The apparent second 0x80042EC4
site is unreachable after an unconditional generated `goto`. The snapshot is
at the end of binPolygonIntoTerrainGrid while the writer is in the later
streamTerrainGridCellsByDistance, so the shared cumulative counter is an
invalid cross-function join even when guest IDs match. H-boundary is selected;
the exact per-invocation join fix remains to be built.

## Next steps — s6511 span-grid writer audit (top)
- **s6511 (top):** audit the upstream writer and dimensions of the full
  `0x80130DB0..0x80132DAF` span grid that the reconstructed DC0 path reads.
  In one Debug build and one pinned dd1/dd4 run, log the grid dimensions at
  initialization, every writer family that changes sampled rows, and a keyed
  empty-return snapshot. Competing outcomes: the grid is initialized and
  populated over the full 0x2000-byte extent (dd4 missing cells are a
  legitimate rasterizer/input result); only the first 24 bytes are initialized
  (the larger target is stale/uninitialized); or a writer changes the grid
  after rasterization with an unexpected source. Discriminator: positive
  initialization control plus keyed writer/source attribution for dd1 nonempty
  and dd4 EMPTY rows. Do not add a guard or change game behavior. ORIGIN:
  s6510 exactly reconstructed the supposedly out-of-table DC0 targets as
  row-grid addresses.
- **s6505 (folded):** the invocation-local key removed the shared cumulative
  underflow. H-boundary remains selected; the exact post-bin writer is open.
- **s6499 (folded):** the complete store census selected a later stream-path
  writer for the dd1 EMPTY control; the dd4 row was beyond its post budget.
- **s6498 (folded):** dd4 EMPTY rows have valid bounds and all-127 table
  samples, but the prior probe did not capture a post-return state or writer.
- **s6496 (top):** the `binPolygonIntoTerrainGrid` writer was instrumented and the
  pinned dd1/dd4 arms ran in one build. The positive control fired (dd1: 8 ok /
  6 empty logged returns; dd4: 8 ok / 25 empty). dd4 empty intervals contained
  repeated rasterizer calls (one interval had `nbin=262`) with changing,
  nonzero-area polygon extents and a stable divisor 12.8, while the span table
  remained all 127 and the window was `0,54/56,0,10`. This refutes
  H-footprint-degenerate at the polygon-input boundary. It does not split
  H-order (rasterizer refresh is late/stale) from H-scale (computed integer
  bins fall outside the table or are rejected). Next: log the rasterizer's
  computed min/max and first/last table-store indices, plus a sequence number
  shared with the stream return, in the same dd1/dd4 run.
- **s6491 (top):** buildGridCellMesh's only caller chain is buildVisibleTerrainGridAroundCamera -> buildGridCellMeshForFace; the cell list is nonempty on every call at dd1 and dd4 (list-empty gate refuted), but ForFace leaves an empty mesh chain on 41% of dd4 calls vs 5% of dd1 (sim also ~20% slower at dd4). Deficit is inside ForFace's per-cell loop before 0x8004349C (single run/arm). Next: per-cell exit census of ForFace (NEXT.md).
- **s6490 (second):** at dd4, 52% of low-ground flight frames have zero buildGridCellMesh entries over 9 VIs vs 1% of high-ground frames; dd1 builds every window (0/652 zero) -> terrain cell pass is not invoked in those frames (H-pass-skipped; single run/arm, slower-sim confound open). Passing cells are only 8-32 per run, so s6489 'per-VI pass-cell count' was ill-shaped. tools/g1c_lowframe_tris.py hardcodes fbs 0x80656000/0x806AB000 (flight fbs here are 0x80620000/0x80690000): its s6488/s6489 low/high split is suspect. Next: caller above 0x8004B930 and the gate that skips it at dd4 (NEXT.md).
- **s6489 (top):** summing tricnt over all tasks per VI (tools/g1c_lowframe_tris.py) confirms s6488 within the dd4 run (low 1239 vs high 1726 tris, -28%); also dd4 high frames submit ~half of dd1's tris (3338), cross-run lead only (iron rule 2). Next: per-VI pass-cell count + tris/cell logging build.
- **s6488 (top):** dd4 low-ground frames (39/185) submit ~28% fewer tris (med 415 vs 578) and ~15% shorter DLs than high-ground frames, with no shared ceiling (max 812 vs 809) -> H-data favoured, H-budget not indicated (single-source: tricnt = last task per VI). Next: per-VI tri sum + pass-cell count at the cell gate (NEXT.md). Tool: tools/g1c_lowframe_tris.py.
- **s6487 (top):** pool x4 (ROGUESQ_POOLMUL) does not restore dd4 ground; full per-frame series: dd1 8/452 low, dd4 135/261, dd4+pool 133/265 -> H-pool-exhaustion refuted, dd4 deficit is steady (~52% low frames), not intermittent (13-frame sample misled). Next: low vs high frames inside one dd4 run, passing cells vs draw count (NEXT.md).
- **s6486 (top):** H-fog REFUTED for dd4 missing ground. FORCE_FOG=FF00FF, pinned lvl1: dd1 positive control shows magenta (whole-frame med 0.33%, bottom band max 5.3%, a fogged distant rock); dd4 shows ~0 magenta (med 0.0000) while ground score stays 0.235 vs 0.875 (dd1). The sky-blue band where ground should be is NOT the fog colour (single run per arm; sheet scratch/agent/m6/s6486_sheet.png). With s6476/s6479 (cell material-link lookup fails, extra cells empty by data) the ground gap is H-data/H-budget, not haze. Next: who fills table 0x80136FCC link halfwords (NEXT.md).
- **s6485 (top):** 0x80137CE4 = difficulty index (readers all NPC/script code, none in funcs_8/9; s5793+s5818), NOT an LOD index; mesh-LOD levers DD_LOD/LODSCALE already measured no-gain (s6421). L-lod closed. Next: fog/haze params at dd1 vs dd4 pinned pose, then H-budget for ground-missing at dd>=4 (NEXT.md).
- **s6484 (top):** isPointXzWithinRangeOfRef = scale .25, thr 144 => 48 raw-unit NPC-vs-player AI range (s5819 values), NOT a terrain lever; with s6483/s6482 all cell-population distance gates are closed. Next: L-lod (0x80137CE4) / fog-haze scaling at dd>1 (NEXT.md).
- **s6483 (prev):** flood-fill floats 0x8003A80C/0x8003A810 = 0.8/0.5 vs constant a1=1.0 at all 4 call sites => dead gate, NOT a radius (static reading, single-source). Next: isPointXzWithinRangeOfRef 0x8003A7D4/7D8 values + [rng] in/out at dd1 vs dd3 (NEXT.md).
- **s6481 (top):** pool row+2 links are written continuously in flight (~83k stores/150 s dd1, 16 PCs; insert-like 0x800487F8, 0x8004B56C; unlink-like 0x80048EB8) via ROGUESQ_POOLWATCH (apply_s6481_poolwatch.py) -> far-cell empty link is runtime-population-bound, not load-time. Next: radius/distance arg of the dominant insert writer (NEXT.md).
- **s6480 (prev):** link table = pool of 12-byte rows at *0x80136FCC, size n from level data (load_level_hmp 0x80044554); gate = row[cell+0x1E]+2 != FFFF and row[that]+4 == 1. Pool census instrument (apply_s6480_poolcensus.py) was uninformative (free pattern gone, scan unbounded by n). Next: record n at 0x80041EF0 + write-watch sh to row+2 with PC (NEXT.md).
- **s6479 (top):** populated-cell census: pass cells/window dd1 75 vs dd3 36 while entries 2.5x; cell-pointer extent identical => extra cells added by widening are empty by link (H-data-limit; two arms, single run). Next: who fills table 0x80136FCC link halfwords and is it radius-bounded (NEXT.md).
- **s6476 (top):** buildGridCellMesh exit census: 99.5% (dd2)/99.95% (dd3) of entries exit at 0x8004BB3C (cell material-link lookup in table 0x80136FCC fails); dd3 passes 8x fewer cells despite 13% more entries. Control: exits sum to entries. Next = split BB18/BB34 and sample cell+0x1E (NEXT.md). Single run/arm, pinned.
**dd>=4 renders with the ground missing (s6468, single-source stills).** Sheets `scratch/agent/m6/s6469_flight_sheet.png`, `s6469_dd4_dd6_dd8_sheet.png`: dd1 solid ground; dd4/6/8 flat sky-blue where ground belongs, terrain chunks floating. The terrain-fraction scorer cannot see this (0.139 vs 0.133). Do not call dd>=4 "clean" on crash-free holds alone. Next: find dd2/dd3 break point with the same joiner (`tools/g1c_fbdump_join.py A B 0x80620000,0x80690000`) AND eyeball sheets; then name which budget drops ground tiles (cell pool / DL / vertex). Hangar at dd8 also shows scanline garbage (unresolved).

- s6470: pinned arms folded: median tri dd1 818/dd2 961/dd3 575/dd4 580/dd6 576/dd8 578 => break is at dd3 in the PINNED recipe (single-source); conflicts with s6419/s6422 (unpinned dd3+fix better). s6470_dd3_break_ab queued (pin vs NOFARCLIP vs repeat).
- s6469: existing dd2/dd3/dd4 dumps are unpinned (different poses) so the ground score tracked altitude; no break point yet. Pose-pinned dd2/3/4/6 arms queued (soak_queue/s6469_dd_break_sheet.sh -> scratch/agent/m6/g1_lvl1s6469p_*); fold, then use tools/g1c_ground_sheet.py (compare against pinned s6468p_d1 = control, s6468p_d8 = missing).

## Next steps (single monotonic backlog)

- s6467: dd8 lvl5 clean (301 s, 0 stalls/crashes); lvl10 was allattempts-failed with no crash marker. First dd1-vs-dd8 owner capture was phase-invalid because pose lock excluded position and dump ordinal is not a route key. Fixed opt-in position pin built and both fresh arms held 151 s clean, but equal dump numbers still paired different phases. Next: add an offline fbdump-to-`[vi]`/origin join and build a genuinely flight-matched dd1-vs-dd8 sheet; only then score terrain/HUD or revisit the 16 MB-limit SIGBUS hypothesis.
- s6466 (fold): dd8 lvl1 300 s hold clean on att2 (multiplier 8 confirmed in run.log, 0 alloc failures). CORRECTION: att1 was a real SIGBUS in factor5_ucode on the gfx thread (si_addr=0x109c08064, fail_att1.log:215850) at lvl1 start, not a route failure; I first mislabelled it from the soak summary alone. Hypothesis (unverified, 1 of 2 attempts): dd8 data past the 16 MB physical limit the gfx ucode can address. Queued s6467_dd8_lvl5/lvl10. If the SIGBUS recurs: map si_addr to a guest address, carve pools below 0x81000000. Then dd1-vs-dd8 owner contact sheet.
- s6464 (fold): lvl10 with FORCE_PLANET_UNLOCK=0xFF: dd4 retry (s6463) and dd1 control (s6464) both rc=0, hold 305/300 s, vi_stalls30s=0, crashlines=0 => dd4 qualified on lvl1/5/10; s6463 recipe-omission diagnosis CONFIRMED (two runs, was single-source). The s6461 audio-probe SIGBUS did not recur (unexplained, passive). Queued s6465_dd6_lvl10; then dd1-vs-dd6 owner contact sheet, then lift clamp to dd8 (apply_s6036_dd.py) and soak lvl1.
- s6463: lvl10 route failures (s6461 dd4, s6463 dd1 control) = recipes missing ROGUESQ_FORCE_PLANET_UNLOCK=0xFF, not dd (single-source until s6463_dd4/s6464_dd1 lvl10 pass). Both requeued with the export.
- s6462: dd6 lvl1 300 s hold CLEAN (0 stalls/crashes). dd4 lvl10 (s6461) = route failure (5 attempts bounced menus 6DD280/6BA280, never reached mission; hold untested) + 1 SIGBUS in diagnostic rs64_probe_audio_dma_write (att3, unreproduced, origin unproven). Queued s6463 dd4 lvl10 retry + dd1 control + s6462_dd6_lvl5; fold them, then dd8/next limit.
- (prior) s6461: G1c phase 2 — fold s6461_dd4_lvl10 and s6462_dd6_lvl1/lvl5 soak verdicts (dd clamp is 6 under ROGUESQ_DD_UNSAFE); find the next binding limit.
- **s6460**: dd4 FOLDED: lvl1+lvl5 300 s holds clean (multiplier 4 echoed, 0 crashes/stalls/alloc failures, VI mean 61.0, sd_wall 53/60 ms/s). Next: dd4 lvl10 hold, then lift clamp 4.0->6 (apply_s6036_dd.py:7, DD_UNSAFE only) and find the next limit; owner sheet dd1 vs dd4.
- **s6458**: s6457 spin vs NOSPIN FOLDED (tools/g3c_vi_dt.py): per-VI wall-dt distributions IDENTICAL (p50 6.0 vs 6.7 ms, sd<40ms 10.67 vs 10.58, 42%/41% of VIs stamped <2 ms after the previous). Oversleep is NOT the cause; s6456 spin stays opt-out-able but is unproven. New datum: [g3c] VI stamps arrive in bursts (3-4 VIs within 0.1 ms, then ~66 ms gap) with VI/s 60.9 and gfx tasks/s 18.6 on lvl1 => the stamp reflects task-completion batching, not VI timer jitter; the s6455 '2 ms sd' was a different regime. G3c(c) CLOSED as retail judder (4th line of evidence: arm-independent jerk s6455 + equal wall-dt spin/nospin). Next: fold s6459 dd4 holds (item 0 is resolved).
- s6455: G3c(c) camera-yaw jerk is arm-independent (VI-index alternation 0.19-0.21 in retail/fps60/wide/both); s6292 FPS60 selection was a wall-stamp artifact. Open: VI event wall dt sd ~2 ms in ALL arms (H-vi-timer vs retail judder).
- s6454: G3c(b) CLOSED as H-hw-draws: angrylion replay (tools/angrylion_replay/replay.c) lights the same 16/79 logged wedges (3909 px) as the s6441 model; control tri 4185 px. Wedges are retail-faithful; CULL_SPIKE stays opt-in, ask owner re default-on. NEXT = G3c(c) screen shake while turning (jerk of camera yaw vs craft yaw per presented frame; arms retail/FPS60/ASPECT/both).
- s6451: G1e s6450 per-VI dumps fold: md5 runs useless (2-VI field alternation, lag1 diff const 7.6 vs lag2 0.45); frame period still unmeasured; next read game-side frame counter per VI (tools/g1e_vi_period.py).
- s6449: s6448 edge soak FOLDED: tools/g3c_edge_stair.py stair_med retail 3.68 / ref(control2) 6.63 / dd2 6.19 / dd3 2.45 / fps60 3.54 / asp169 2.96 - control spread exceeds arm spread, so no opt-in shows more stair-stepping than retail (single-source). Sheet docs/owner_sheet_s6449_edge.png. G3c(a) parked pending owner judgement. Retail frame shows a spike line (G3b datum). Next: G1e real frame-rate measurement.
- s6448: G3c(a) far-edge arm table QUEUED (soak_queue/s6448_g3ca_edge.sh: retail/dd2/dd3/ASPECT16:9/FPS60 at pinned pose). Next: fold results, write edge-stair metric (terrain-vs-sky boundary x-run lengths; retail = control), owner sheet, then fix (scale haze with dd or fade outer cells). Then G3c(b) reference-RSP check, G3c(c) shake jerk measurement. No conclusions overturned this session.
- s6447: FOLDED real dd3 lvl5/lvl10 300 s holds: both clean ('multiplier 3' echoed, alive_at_end=1, vi_stalls30s=0, crashlines=0) => dd3 qualified on lvl1/5/10; owner to judge docs/owner_sheet_s6439.png; dd>3 still needs DD_UNSAFE. Next: G3c (owner visual report) per NEXT.md.
- s6446: CORRECTION: s6420 'dd3+fix lvl1/5/10 clean' holds were really dd2 (run.log: 'capped to 2'; no DD_UNSAFE in recipe). Real dd3 holds exist only for lvl1 (s6421 300 s, s6422 150 s). Guard raised to 3 (tools/apply_s6036_dd.py, built); soak_queue/s6446_dd3real_lvl5/lvl10 queued - fold; confirm run.log says 'multiplier 3'. Then record the dd knob bundle; default stays retail.
- s6442/s6443: M6 3x600 s retail holds lvl1/5/7 folded: 3/3 clean (0 crash, 0 VI stall; lvl7 mission_cycles=14 = fail/re-enter loop, not a fault). M6 goal met; do NOT repeat holds (G4 parked). Next: G1c phase 2 dd3 (see NEXT.md).
- s6439: owner contact sheet built (docs/owner_sheet_s6439.png, tools/owner_sheet_s6439.py); G3 livery (s6267) and G5 (s6268) were already closed. Ladder exhausted of non-owner items: ask owner to judge sheet; next engineering = M6 title->mission endurance (item 3b) or G3c(b) spike reference check.
- s6438: hangar 340/448-row claim NOT reproduced (tools/fb_rows_lit.py: wide hangar readbacks 436-448 lit rows of 448 in both arms) - H-viewport refuted, G1d hangar closed on rows. Next: owner contact sheet, G3 livery diff, G5.
- s6435: ASPECT!=4:3 now lifts ucode cap to 65536 (fixup, built). s6434 hangar soak folded clean (both wide arms alive, 0 stalls/crashes). s6437: s6436_aspect_cap folded - cap fires 0 in both arms (default and CAP=16384 control), hole scores similar (med .118 vs .110): ucode cap is NOT the 16:9 lvl1 hole source. Next: hangar 340/448 row check, owner contact sheet, G3 livery diff, G5.
- s6433: G1e CLOSED (s6254-s6262, s6290). Open: G1d hangar/menu 21:9 recheck (soak s6433_aspect_hangar219 queued), owner contact sheet, then G3 livery diff, G5. (s6432: wide-edge holes not reproduced.)

- s6427: 320-wide cams no longer vpw-scaled (logo shifted +78 at 16:9); soak s6427_aspect_menufix queued - fold, check fb_0000303 centred, then radar clip.
- G1d (s6430): s6428 verify soak FOLDED: logo centred at 16:9 (pixel diff vs 4:3 identical rows 0-320), 16:9 (796x448) and 21:9 (1024x448) flight fill frame with HUD at edges, radar unclipped; harness reports allattempts-failed for wide arms (4:3-keyed detector, not crashes). Remaining: hangar/menu 21:9 recheck, owner contact sheet, then G1e. OLD NOTE: s6428 cam-scale fix is built; soak_queue/s6428_aspect_verify.sh queued (a43ref/a43/a169/a219 pose-locked, lvl1). Fold it: logo centring, 16:9 radar clip, w640 late-dump noise (dump-stride mislabel vs real menu stride; re-read at w796, a43 = control). Earlier note (s6426) that menu garble is a wide-FB stride defect is now UNVERIFIED: s6427 showed the logo shift was camera scaling, and part of the garble may be dump-at-wrong-stride. Then contact sheet for owner, hangar 21:9, G1e.

0. [RESOLVED by s6418 farclip fix; see 0c/0f] G1c phase 2 (s6413): attitude pin works (d1b matches d1ref, control passes; dd2 matches). Position-matched (x~20.6) frames show dd3/dd4 DROP the near mountain (flat sky below craft) while dd1/dd2 draw it: terrain goes MISSING at dd>=3, not scorer defect (single-source, one frame/arm; view/s6413/sheet2.png). s6414: s6412 logs carry no pool/cap counters; soak_queue/s6414_dd_pool.sh (same pinned recipe + DLPOOLLOG=1) queued, fold its pool-length trajectory first. NEXT (original): log per-VI terrain tile/DL-chunk alloc failures and terrain draw counts at dd1/dd2/dd3 on the same pinned recipe (s6412_attpin.sh) to name the writer/limit (DL chunk supply, pool dims s6035); fix root cause or cap dd at 2 officially. s6411 dd2 lvl5 clean; lvl10 needs ROGUESQ_FORCE_PLANET_UNLOCK=0xFF. dd>2 REQUIRES ROGUESQ_DD_UNSAFE=1. | s6414 (fold): DL chunk pool is NOT the limiter - [dlpool] min=77 max=1925 empty_b=0 identically in d1b, d2 and u3 (H-chunk refuted, control d1 shows pool moving). Next: s6415_dd_grid ([gridlog] kept/req/cap per arm) splits H-pool/H-cap/H-cull. | s6416 (fold s6415_dd_grid, single-source): [gridlog] kept < cap in 166/166 rows across d1b/d2/u3 (max kept 1684 of cap 2048; 64x64 tier cap 600 never hit either); kept grows with dd (d1b ~330/756 req, d2 ~970/2024, u3 1354-1684/2021) and the gx/gz window is not clamped. H-pool and H-cap REFUTED; the cell list built upstream is bigger at dd3, yet terrain is missing => loss is DOWNSTREAM of streamTerrainGridCellsByDistance (per-node submit / far-clip / vertex-DL build). Next: s6416 per-node submit counters (cells entering vs DL emitted vs culled) on same pinned recipe.

0b. s6417: buildGridCellMeshForFace (0x8004317C) LOD-selects each cell by dist^2 vs fixed float table 0x8009DE94 and cuts the render chain at DEB4; nothing scales those with dd (lead H-farclip, offline read only). Instrument ROGUESQ_DD_MESHLOG built; soak_queue/s6417_dd_mesh.sh queued. Fold its [meshlog] chain vs list per arm first.
0d. s6419: farclip fix scored (g1c_fixed_score): tight terrain frac median dd1 0.044, dd2 0.074, dd3+fix 0.179, dd3 nofix control 0.077 (single-source, cross-run, pinned pose). s6420 fold: dd2+fix 300 s holds lvl1 and lvl10 clean (0 crash, 0 VI stall; lvl5 still queued). dd3+fix holds lvl1/5/10 queued (s6420_dd3fix_lvl*); next: fold them, then owner contact sheet; H-lod-coarse untested. posesheet by fbn is NOT view-matched - don't use it.
0f. s6422: dd3+fix 300 s holds lvl1/5/10 ALL clean (0 crash/0 stall). soak_queue/s6422_dd3_sheet.sh queued (pinned d1b/d3/d3lod sheet frames); s6421_dd3lod_lvl1 A/B still pending. Fold both, build owner sheet, decide LODSCALE bundling.
0e. s6421: dd3+fix lvl1 300 s hold clean (0 crash/0 stall). Built opt-in ROGUESQ_DD_LODSCALE=1 (LOD tiers DE94..A0 x dd^2, in apply_s6418_farclip.py); soak_queue/s6421_dd3lod_lvl1.sh queued as A/B vs s6420_dd3fix_lvl1. Fold lvl5/lvl10 dd3 holds + this A/B next, then owner contact sheet.
0c. s6418: H-farclip CONFIRMED (meshlog: chain == count(d2<DEB4) in dd1/2/3 while list grows 3x). Fix landed: tools/apply_s6418_farclip.py scales 0x8009DEB4 by dd^2 each build (game rewrites it, 143-220); ROGUESQ_DD_NOFARCLIP=1 = A/B. Fixed-score dd3 tight terrain 0.196 vs 0.121 without fix (cross-run, single-source). Next: position-matched owner sheet + 300 s holds lvl1/5/10 at dd2.

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

- s6409: dd3/dd4 (DD_UNSAFE) hold 420 s clean (0 crash/stall) on lvl1; the s6407 '~5% HUD-absent' was a scorer artifact (craft-select + post-mission menu frames); flight-only absent 1/1134, 2/824 (black transitions). No DL truncation at dd3/dd4. Next: pose-locked dd2/dd3/dd4 contact sheet to see whether the terrain gain is visible, then levels 5 and 10 holds (NEXT.md).

## Evidence index

Recent session findings are in `PORTING-STATE.md` sessions 6377–6385. Durable
background, closed threads, and the archived long backlog are in
`docs/PROJECT-OVERVIEW.md`. Queued-soak verdicts are in
`scratch/agent/SOAK-RESULTS.md`; do not treat a queued repeat soak as a work
unit.

- s6402: G3c(a) dd2 sawtooth/holes = frames with craft+HUD absent (likely truncated DL; single-source, see PORTING-STATE). Next: log UCODE_CAP/tri count per VI in dd2 pose-lock arm (scratch/agent/NEXT.md).
- s6403: ROOT CAUSE of dd2 craft/HUD-absent+sawtooth frames = F5 ucode iteration cap 16384 firing (cap 65536 -> 0 fires, craft+HUD intact; retail+CAP=1500 positive control reproduces missing craft/HUD). Default cap now 65536 when DRAW_DISTANCE>1 (fixup_factor5_ucode.py). s6404: dd2 default 0 fires, retail unchanged; craft/HUD visual confirmation in default arm still owed. Re-score G3c(a) holes with the cap fix, then G3c(c).

- s6405: dd2 terrain holes confirmed fixed by scaled ucode cap in dd2/aspect/combined (g3c_holes 0 frames>0.03, control fired). Next: G3c(c) turning-shake jerk (see NEXT.md).

- s6405: G3c closed out. (c) shake = retail 30 fps judder (s6302, equal HF residual all arms); (a) holes fixed by cap scaling and flight frames in retail/dd2/aspect show craft+HUD+terrain (view/s6406/sheet.png); (b) opt-in cull stays opt-in (no retail reference). Next: G1c phase 2, dd3 with scaled cap (NEXT.md).

- s6423 (fold s6422, single-source cross-run): dd1/dd3/dd3+LODSCALE 150 s lvl1 all clean. LODSCALE gives no terrain gain and +14% RSP ms over dd3 -> NOT in the DRAW_DISTANCE bundle. RSP cost dd3 ~2.2x dd1 (69->149 ms/s), VI still 63-65. Arms were not view-matched (POSE_LOCK pins position only); don't read the raw terrain-fraction drop. G1c phase 2 considered done at dd3; next rung G1d (ASPECT) state check.
- s6424: 21:9 arm crashed 3/3 (no OSMEM_MB=12 -> 8 MB heap exhaustion at load_level_hmp); s6425 makes ASPECT imply OSMEM 12 and re-queues the sheet (s6425_aspect_sheet2). Next: fold it, send sheet; hangar/menu 21:9; G1e.

- s6428: 16:9 logo +78px shift root-caused: 640-wide cams scaled x kv*0.8 into unwidened 640 fb; fix = scale keyed on live video-state width <=640 -> no scale (verified logo centred, flight intact). Still open G1d: 21:9/hangar recheck, radar clip repro, w640 late-dump noise (dump-stride mislabel?), then G1e.

- s6431: wide-aspect soaks must use MISSION_WIDTH=796|1024 (not MISSION_RE=ZZZ, which forced false nomission). Open G1d datum: terrain/sky holes at wide frame edges (single frame each at 16:9, 21:9) - see NEXT.md.

- s6436: s6435 cap soak void (MISSION_WIDTH=WW placeholder, no flight reached); requeued s6436_aspect_cap with 796.
- s6434: s6433 hangar soak 'notitle' = harness origin gates under wide FB (WIDE_ROUTE=1 added, s6434_aspect_hangar219 requeued). Dumps show hangar full-width but ~340/448 rows, and ASPECT flight black holes (single-source). Next: fold s6434; check hangar height via RT64 window capture / viewport; check holes with UCODE_CAP at ASPECT.
- s6452: G1e re-closed: retail ~30 fps vs FPS60 ~59 (0x8011A8F4, s6256-57) already measured; s6450-51 md5/per-VI approach redundant, abandoned. M6 hold soak s6452_m6_hold600 queued.

- s6465 (fold): dd6 lvl10 clean (301 s, 0 stalls/crashes) => dd6 qualified lvl1/5/10. Clamp under DD_UNSAFE lifted 6->8 (apply_s6036_dd.py + funcs_9.c); s6466_dd8_lvl1 queued. Then dd1 vs dd6 owner contact sheet.

- s6471: dd3 break A/B folded: d2ctl 905, d3nf/d3free/d3pin all ~575 median tri; farclip and pin ruled out, game submits shorter DL at dd3 (116k vs 205k). Next: read terrain cell-count/radius scaling in tools/apply_s6036_dd.py for dd^2 overflow at dd3.

- s6475: H-cutoff-small REFUTED (FARCLIP_MUL x4 at dd3: cutoff 1289->5157, chain 687->930, stripN 18.5->20.0). Next = buildGridCellMesh exit-path census (NEXT.md).
- s6474 (single-source, arms not phase-aligned): per-node strip-emit fraction is ~5% at dd2 and dd3 (no dd3 per-node bail); DEB4 cutoff 573 (dd2)/1289 (dd3) is below most list d2 (up to 6400 at dd3), chain=0 in late rows. Next = ROGUESQ_DD_FARCLIP_MUL A/B (NEXT.md). Instrument: ROGUESQ_DD_SUBLOG (tools/apply_s6474_subcount.py).
- s6473: H-GRID64 REFUTED offline (gridlog window is post-s6037-clamp, <=64; saturated in only 2/47 w, 6/47 d dd3 rows; kept<cap). Loss is downstream of the cell list: next = per-node submit/DL-emit counters dd2 vs dd3 (NEXT.md). | (superseded lead) s6472 (single-source, static): dd3 DL shrink likely from fixed 64x64 terrain-grid tables in binPolygonIntoTerrainGrid (0x8004286C; bbox width/depth at 0x80132DB4/BC predicted 58 at dd2, 87 at dd3). Unmeasured. Next: log width/depth at dd1/2/3 (see NEXT.md).

- s6477: buildGridCellMesh BB18 gate (table row link==0xFFFF) takes ~99% of exits at dd2/dd3; cell+0x1E indices are varied real rows (H-index unsupported). Next: dd1 control (NEXT.md).

- s6482: grid row+2 link writers (0x800487F8, 0x8004B56C) are generic list-node push/unlink, no distance gate (single-source). Next: radius in processGridCellByDistance/updateActiveGridCellState, else pivot L-lod/fog.

- **s6492 (supersedes s6491 'list never empty'):** g_s6491 listnz read stale r16 (head is v0). Real: streamTerrainGridCellsByDistance (0x8042B50) returns an empty list on 15.5% of dd4 calls (0.3% dd1); ForFace itself never skips cells before its jal; another 24% of dd4 ForFace calls get tiny lists with no cell < DEB4. Next: instrument the stream function's exits (NEXT.md).

- **s6493:** stream-function exit census (lvl1 pose-pinned, 150 s): dd4 empty=300/1504 (20%) vs dd1 7/2303; z-early-out, pool cap, spanbound skip, node==0 are all 0 at dd4, so the empties come from the per-cell span-table filters (0x80130DB0 signed-byte table). dd4 visits fewer cells/call than dd1 despite a 1.6x wider window. Next: dump window words + span table on empty calls (H-spanoverflow). Single-source.
- **s6495:** dumped window words + span table on stream-fn returns (lvl1 pose-pinned): dd4 empties = table all 127 (no-span sentinel) + window w=0,55/56,0,10 (word 2 = 0, vs 17 on ok calls); dd1 empties are normal rows beyond footprint. Table is not wrapped/out of range -> H-spanoverflow refuted; footprint rasterizer produced no rows (H-footprint). Single-source. Next: find the table/window writer and log its inputs.
