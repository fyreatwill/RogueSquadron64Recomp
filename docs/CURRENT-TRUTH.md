# Rogue Squadron 64 Recomp — current truth

Compact operational handoff, as of Session 6556 (2026-10-27).
`PORTING-STATE.md` is the chronological ledger. Historical detail, the
retired backlog, and the verbatim s6378-s6551 body of this file are in
`docs/PROJECT-OVERVIEW.md` ("Migrated from CURRENT-TRUTH (s6552 maintenance)"
and "Archive: CURRENT-TRUTH body s6378-s6551").

## Headline

- The qualified route boots attribution, N64 logo, intro, Factor 5 logo, title,
  hangar, and mission origins; mission input reaches flight code.
- M5 audio de-stubbing, M3 idiom audits, generated-symbol renaming (G5), M6
  first-mission endurance (3x600 s lvl1/5/7, s6442), and G2 audio are closed.
  G4 crash hunting is parked after clean coverage. G1 is mission coverage and
  visual quality, not autopilot work.
- **Active thread: G1c draw-distance phase 2 (HYPOTHESIS-ID g1c-dd-phase2).**
  - s6549-s6551: `ROGUESQ_DD_POOLX` > 1 at dd4 lvl1 lifts the 0x80130C4C
    2048-cell cap (2400 observed) but SIGSEGVs in `renderFlatMeshFaceGroup`
    (si_addr=0x380000004). px2/px3/px4 (cap 800/1200/1600) ALL fault at the
    same store, 0x80011524 `sw v0,4(a0)` with a0=0x80000000 (a NULL list
    node); px1 clean. Deterministic (5/5); BIGARENA pool divert does not change
    it (2/2), so not a heap-alloc failure and not a cap threshold (H-table
    refuted). `docs/DRAW-DISTANCE.md`'s "POOLX 1..2.5 fit" is therefore stale.
    Open hypotheses (NEXT.md): H-uninit (extra pool entries never linked),
    H-fixedarr (retail-sized parallel array read past its end), H-clamp
    (ddclamp window feeds an entry the game never built).
  - s6548: `[ddclamp]` lvl1 terrain is 64x64 with a 2048-cell cap; dd4
    (~88x137) and dd6 (~101x174) footprints both clamp to the terrain, so dd6
    draws no more than dd4 on lvl1 (s6547: dd6 cheaper, 56 vs 109 ms/s).
  - Span-reject bypass is default-on for dd>1 (s6529). The dd>=4 missing
    ground was the per-cell span filter rejecting saturated (-128) cells
    (s6515-s6528; same-run SPANFORCE terrain 0.047 -> 0.209). The saturation
    writer is unnamed; the bypass is a workaround.
  - Bypass cap (`ROGUESQ_BYPASS_MAXCELLS`, default 120 for dd>1, s6540):
    cap120 buys no terrain over cap0 in either rotation order (two-source,
    s6543 + same-pose sheet s6546); only unlimited accept buys terrain (~3x
    tight) at ~1.7x wall. Owner recommendation pending: inf for dd>1 (cap0
    visibly drops ground).
  - Rare dd4-family gfx-thread SIGBUS (factor5_ucode, si_addr ~17 MB above
    rdram base; s6461 lvl10, s6466 dd8 lvl1 att1, s6529 lvl5): 0 crashes in
    the last 8 lvl5 dd4 runs, rate <=~1/9, not bypass-specific (s6534).
  - s6556: DL-chunk census (s6287) shows pushes == real pops per frame at px1 and px2 (counted pops = pops+pushes because push sites also load head). Yet px2 len falls ~600 chunks/frame (1553->0 in 24 begins ~5932-5956) with ~20 pops/frame: chunks leave the free list off-census (chain cut / unmatched consumer). Leak and bad-free refuted. Next: log the list cut point (NEXT.md). s6558: instrument ROGUESQ_CHUNKCUT built; run e3 partial (begin 41 cut only, uncontrolled); read g1_lvl1s6553_dd4_px2_e3/run.log past begin 5900, then run the _st selftest arm.
- **G3c (owner visual report): engineering closed, owner judgement pending.**
  (a) far-edge stair: no opt-in rougher than retail (s6449, s6544);
  (b) spike wedges: H-hw-draws, angrylion lights the same 16/79 wedges
  (s6454), `ROGUESQ_CULL_SPIKE` stays opt-in; (c) turning shake: retail 30 fps
  judder (s6455, s6458).
- **G1d (aspect): closed on engineering** (s6430 flight fill/HUD/logo, s6438
  hangar rows); owner contact sheet outstanding; native hangar artifacts parked.
- **G1e (frame rate): closed** (retail ~30 fps vs FPS60 ~59, s6452).

## Superseded conclusions — do not act on these

One line each: claim (superseded by; why it was believable).

- s6555/s6554 "chunks consumed by a runaway consumer / free path leaks" (s6556: pops==pushes per frame; chunks vanish without a pop).
- s6554 "runaway consumer in traverseSceneGraphRecursive" (s6555: sibling loop visits 8-17 nodes/frame, 0 revisits at the fault frames; the fault stack merely passes through it).

- s6553 "dd>1 NULL node = DL-chunk supply shortfall" (s6554: a 12x larger arena is consumed in ~24 frames; chunk-empty is the symptom of a runaway scene-graph walk).
- s6550 "split POOLX=3 vs 4 for a threshold" (s6551: px2-4 all fault; the cap scaled with POOLX).
- s6545 "cap0 vs inf undecided" / s6544 "pinned pose" sheet (s6546; s6544 pinned only the stair-metric window, not the camera).
- s6539 cap ordering 0<40<120<inf for terrain (s6541 retracted as run-to-run scatter; 4-10 frames/arm looked monotonic).
- s6542 cap0 dearer than cap120 (s6543: post-inf hysteresis; rotation order confounded it).
- s6540 "default path differs from explicit cap120" (s6541 H-noise; single runs differed).
- s6537 "a cell cap keeps most of the gain cheaply" (s6543: gain is all-or-nothing; cap arms were cross-run).
- s6525 dd4-rejected cells have sentinel recs -2 (s6526 raw dump: normal recs; the joined log read unpopulated bytes).
- s6520 span bytes 0x80 "never written" (s6521: clamp/clear values; 0x80 resembled an init fill).
- s6516 dd4 EMPTY reads another table (s6517: sampling-phase confound; dump rows covered different key ranges).
- s6509 DC0 writes outside a 24-byte span table (s6510/s6511: it is a 64x64 grid; only 24 bytes were dumped).
- s6502 thread-local / s6500-s6505 cumulative writer joins (s6505/s6506: cross-function shared counter; guest IDs matched).
- s6495 all-127 table = rasterizer produced no rows (s6514; snapshot is taken after the filter's own 0x7F stamp).
- s6491 cell list never empty (s6492: read stale r16; head is v0).
- s6488/s6489 low-vs-high-ground tri split (suspect: tool hardcodes non-flight fbs).
- s6472 fixed 64x64 grid tables limit dd3 (s6473 offline: window is post-clamp, kept<cap).
- s6470/s6471 "game submits shorter DL at dd3" break point (explained by the span-filter chain; pinned vs unpinned recipes disagreed).
- s6466 dd8 att1 "route failure" (real SIGBUS; soak summary alone mislabelled it).
- s6446: s6420 "dd3+fix lvl1/5/10 clean" holds were dd2 (run.log said `capped to 2`).
- s6414 durable constraint "dd>2 exhausts the DL chunk supply" ([dlpool] identical across arms; H-chunk refuted).
- s6407 ~5% HUD-absent at dd3/dd4 (s6409: scorer counted menu frames).
- s6399 aspect side-edge lean (s6401 withdrawn: outer-column scalars are noise).
- s6393/s6391 fixed wide-flight origin gate (origin is allocator-dependent).
- s6380 zero-FD57 interpretation (s6380long route audit: retry arm took a different route).
- s6292 FPS60 owns the turning shake (s6455: VI wall-stamp artifact).
- s6426 menu garble = wide-FB stride defect (s6427: 640-wide cam scaling).
- s6434 hangar only ~340/448 rows (s6438: 436-448 lit; dumps misread).

## Run recipes and hard config

- Run from `build/` with the ROM beside it; SIGKILL to stop; one game run at a time.
- Current pinned dd4 lvl1 run: `zsh scratch/agent/s6549_run.sh <dd> <poolx>`.
- dd>2 needs `ROGUESQ_DD_UNSAFE=1` (clamp 8); confirm run.log echoes `multiplier N`.
- lvl10/15 need `ROGUESQ_FORCE_PLANET_UNLOCK=0xFF`. Wide soaks need
  `MISSION_WIDTH=796|1024` + `WIDE_ROUTE=1`; ASPECT implies `OSMEM_MB=12`.
- Pose control: `ROGUESQ_POSE_LOCK=1` + `ROGUESQ_POSE_PIN_POSITION=1`; dump
  ordinal is not a phase key, join dumps to `[vi]`/origin
  (`tools/g1c_fbdump_join.py`).
- Soak verdicts: `scratch/agent/SOAK-RESULTS.md`; read `alive_at_end` /
  `crashlines`, never rc. A queued repeat soak is not a work unit.
- Per-frame cost meter: `[g1b]` lines in run.log (sd_wall, tasks/s).
- Full dd knob/instrument table: PROJECT-OVERVIEW "G1c draw-distance knob and
  recipe reference"; owner guide `docs/DRAW-DISTANCE.md`.

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
- `ROGUESQ_DRAW_DISTANCE`: dd2 qualified lvl1/5/10; dd3/dd4/dd6 300 s holds
  clean lvl1/5/10 under DD_UNSAFE; dd8 lvl1/5 clean. Crash-free holds do not
  mean "renders correctly" (s6468: dd>=4 ground missing before the bypass).
  No mitigation is acceptable without naming the writer and establishing value
  legitimacy; dd>1 fixes live in `tools/apply_s6*.py` and fixup scripts.
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

1. **Census DL-chunk pops/pushes per swap by caller (ra), px1 vs px2** (g1c-dd-phase2, top; NEXT.md). s6555 REFUTED traverseSceneGraphRecursive as the runaway (8-17 nodes/frame, 0 cycles at the px2 crash frames; selftest positive control fired). Chunk drain is inside per-node submit work or a failed chunk return (reclaim=0 everywhere; px1 len rises, px2 leaks ~5/frame then collapses).
2. **Lift the 0x80130C4C 2048-cell cap with its pool** once item 1 is fixed;
   qualify on lvl1, then on a level with terrain larger than 64x64 (s6548).
3. **Owner decision: dd>1 bypass cap.** cap120 is pointless; choose cap0
   (cheap, drops ground) or inf (terrain, ~1.7x wall). Sheets
   `docs/owner_sheet_s6546.png` (same-pose), `docs/owner_sheet_s6540_cap.png`
   (not pose-matched).
4. **Name the span-grid saturation writer** (edge loop at 0x80042820/0x800426D8
   `sb trunc(clamp(f0,f12,f10))`, s6521) and fix at the writer to retire the
   bypass workaround; two-arm qualify.
5. **dd4/dd8 gfx-thread SIGBUS (rare).** On recurrence: backtrace, map si_addr
   to a guest address, test H-16MB (keep gfx-read data below 0x81000000).
6. **dd8 hangar scanline garbage** (s6468, unresolved, single-source).
7. **G3c owner judgement**: edge sheet `docs/owner_sheet_s6449_edge.png`,
   `docs/owner_sheet_s6439.png`; ask whether `ROGUESQ_CULL_SPIKE` should be
   default-on.
8. **G1d owner contact sheet** (16:9/21:9 flight and hangar).
9. **G1 coverage (c)+(d)**: framebuffer terrain/craft/HUD evidence and a
   forced-hit objective response for every level 0..18.
10. **Ladder (ITERATION.md 3c)**: after the above, G3 render fidelity
    (hangar artifacts, in-flight diffs vs retail frames). G4 and aim/steer stay
    parked; G2, G5 closed.

## Evidence index

Recent session findings are in `PORTING-STATE.md` sessions 6378–6551. Durable
background, closed threads, and the archived backlogs are in
`docs/PROJECT-OVERVIEW.md`. Queued-soak verdicts are in
`scratch/agent/SOAK-RESULTS.md`.
