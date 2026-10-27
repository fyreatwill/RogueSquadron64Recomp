# Rogue Squadron 64 Recomp — current truth

Compact operational handoff, maintained as of Session 6348 (2026-10-26).
`PORTING-STATE.md` is the chronological ledger. Durable background and closed
detail are in `docs/PROJECT-OVERVIEW.md`; exact run verdicts are in
`scratch/agent/SOAK-RESULTS.md` and the named audit documents.

## Headline

- s6348: the target-range phase-5 census passed the ordinary-store, VTX,
  bulk, and forced-red controls and captured 44 target-store/post pairs. The
  only writers overlapping `0x735560..0x7355D0` were the pointer/list-shaped
  `0x8000D114` stores plus one zero store at `0x80010FCC`; none of their
  post-values equaled the independent red VTX boundary. The boundary remained
  red across five phase-6 tasks, with zero phase-5 DMA overlap. H-later-store
  is refuted for the instrumented guest-store class; the transition remains
  open to a host write or earlier/uninstrumented copy. The DD3 level-1 hold
  reached mission in 8 seconds and held 130 seconds with `alive_at_end=1`,
  zero VI stalls, and zero crash lines. No mitigation was added.

- s6347: the exact-address D114 witness passed all controls and captured 43
  phase-5 rows in the target `0x735560..0x7355D0` lanes. The generated
  `0x8000D114` effective addresses were the target addresses and the post-store
  helper used the live RDRAM base, but source/pre/post values were
  pointer/list-shaped and did not equal the later red VTX-boundary bytes.
  H-real-store, H-wrong-address, and H-wrong-buffer are refuted for these
  sampled rows; a later phase-5 guest writer remains unnamed. The DD3 level-1
  hold reached mission in 7 seconds and held 130 seconds with zero VI stalls or
  crash lines. No mitigation was added.

- s6337: the post-store shadow passed ordinary-store, VTX, bulk, source-red, and post-store controls. Of 2,308 bounded phase-6 VTX join rows, 2,303 had valid post-store readback; the only exact post-store/current-VTX matches were 15 zero-valued rows, while red-valued VTX lanes had no matching phase-5 guest-store post-value. The DD3 level-1 hold reached mission in 8 seconds and stayed alive 130 seconds with zero VI stalls/crash lines. This rules out the observed phase-5 guest-store last-writer path as the source of the red bytes; exact-lane host-write ordering remains open. No mitigation was added.
- s6339: the exact-lane host-order witness passed all prior controls and recorded 128 bounded rows, all `rsp_dmem_to_rdram`. On sampled red-valued phase-6 VTX lanes, pre-write bytes were already red and post-write bytes changed; these host DMAs are later overwrites, not the transition that creates the red source. The DD3 level-1 hold reached mission and stayed alive 130 seconds with zero VI stalls/crash lines. H-host-write-order is not selected for the sampled lanes; the source-transition boundary remains open between earlier/unlogged bulk population and VTX-side source/read ordering. No mitigation was added.
- s6341: the source-transition witness passed the VTX, ordinary-store, and bulk positive controls and recorded 64 phase-6 rows. For red range `0x735560..0x7355D0`, registration bytes already equaled VTX-read bytes and were already red; no overlapping DMA occurred after registration (`dma_events=0`). The run reached mission in 8 seconds, but the harness did not emit its hold summary before the game was SIGKILLed, so no endurance claim is made. This selects an earlier/unlogged population path over VTX-side copy and the sampled host-order path; the writer remains unnamed. No mitigation was added.
- s6342: extended the witness with capped phase-5 host-DMA retention and a phase-5 store-event history. The fixed arm reached mission in 7 seconds and held 130 seconds with zero VI stalls/crash lines; VTX/store/bulk/forced-red controls fired. The sampled red VTX ranges had zero phase-5 DMA overlaps. The retained last-writer join still points to phase-5 PC `0x8000D114`, but its values are pointer/list-shaped rather than red payload; the bounded store-event table saturated before matching rows and cannot select a writer. The phase-5 transition remains open; no mitigation was added.
- s6345: replaced the saturated phase-5 store prefix with a 65,536-entry ring plus a per-word phase-boundary fallback. The fixed ring still wrapped, but the fallback found 28 phase-5 snapshot lanes for `0x735560..0x7355D0`, 23 with red boundary bytes, and zero phase-5 DMA overlaps. All four controls fired; DD3 level 1 reached mission in 8 seconds and held 130 seconds with zero VI stalls/crash lines. Every matching row was attributed to `0x8000D114` with pointer/list-shaped source values, and the post-store readback repeated those values instead of the actual red VTX bytes. This proves the bytes are already red at the retained phase-5 boundary but does not identify a legitimate colour writer; the `0x8000D114` attribution/readback witness is invalid for this payload and needs an exact-address/base audit. No mitigation was added.

- s6328: the batched F5 DMA-source instrument passed its positive control (about 1.9M sampled reads; flight reached phase 6/7), but `ROGUESQ_EDGE_FORCE_RED=1` at 0x8004B910 still produced no terrain red (red fraction 0 in the late flight dump; radar-only red remains); the sampled reads are mostly broad 0x0170/0x0280 display-list/terrain records and do not name a colour writer. The epilogue is ruled out; next instrument the actual F5 `VTX` load and its vertex-buffer byte range, then identify the last guest store into that range.
- s6329 checkpoint close-out: no rerun; the s6328 conclusion and VTX/store discriminator remain current.
- s6330: the regeneration-preserved F5 `0x04` VTX probe passed in phases 3–7 (320 records; phase 6 sources include `0x735560..0x73E3B0`) and the red arm still produced no terrain red. The existing p6 page-fault witness also fired in phase 6 at `0x733378`, but its `guest_pc=0x8000D3D0` is a stack-local `sw v0,0x14(sp)`, so it is not a named vertex-buffer writer; the page-fault annotation is not sufficient guest-store attribution. Next: add an exact-range guest-store shadow with an ordinary-store positive control.
- s6331: the exact-range post-VTX shadow passed both controls: the ordinary store at `0x801E8710` fired in phase 4 and the F5 VTX control fired in phase 6. The red/DD3 level-1 hold reached mission in 14 s and stayed alive 130 s with zero VI stalls/crash lines. No parity-instrumented guest store overlapped a phase-6 VTX range; 96 overlaps were phase-7 buffer writes, all zero-valued. This does not yet prove H-ucode-light: stores before the VTX task and bulk/uninstrumented copies are not in the post-VTX shadow.
- s6333: the pre-VTX last-writer join passed the ordinary-store, VTX, and bulk controls on the successful retry. Phase-6 VTX ranges joined to prior hooked guest stores, predominantly PC `0x8000D114` in phase 5 (`heapFreeListDequeue`), and many source words already contained red bytes. `rsp_dmem_to_rdram` also overlapped a phase-6 VTX range, proving a bulk/DMA population path. The existing parity hook still passes literal zero for `value`, so the writer value field is not evidence; the source-byte dump is. This selects a pre-copy/bulk population path over a no-writer null, but does not yet identify which writer supplies the rendered colour.
- s6334: the regeneration-preserved value witness at `0x8000D114` passed the ordinary-store, VTX, and bulk controls. Its actual values are pointer/list-shaped (`0x800DB7D8`, `0x800DB79C`, etc.), not red colour bytes, while the joined phase-6 VTX ranges still contain red source bytes and `rsp_dmem_to_rdram` overlaps them. The named `heapFreeListDequeue` store is therefore a list writer, not the colour writer; H-bulk/pre-copy remains selected but the exact DMA source/value is open. The 130-second DD3 level-1 hold reached mission with zero crash lines and zero VI stalls.
- s6335: the new exact-lane `rsp_dmem_to_rdram` payload witness passed with 64 bounded phase-6 overlaps; ordinary-store, VTX, and bulk controls fired, and the DD3 level-1 hold reached mission in 8 seconds and stayed alive 130 seconds with zero VI stalls/crash lines. The DMA payload bytes in the joined lanes do not match the red bytes later read by the same F5 VTX ranges (for example `0x735560..0x7355D0`: DMA payload begins `D317...`, VTX reads `FFA4...`; `0x72D898` also differs). This rules out H-bulk-colour for these writes. The source-red path is still pre-VTX, but its actual writer or ordering remains open.

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
and 300-second hold coverage (a)+(b) (s5938). Levels 10 and 15 PASS (a)+(b) only after the ~790 s planet-intro
viewer auto-advance (s5943) or with `ROGUESQ_FORCE_PLANET_UNLOCK=0xFF`; short waits end `nomission`
(`curOvl=1 cineState=F7B80040`, origins 0x644D00/0x6A2900) - a retail planet-intro timer, not a crash.
Levels 15b..18b held clean in the G4 sweep (s5999-s6082). A valid coverage run requires `[lvsel]` with
`a1 == 1<<level`, flight handoff, >=300 s alive, zero crash lines, and no 30 s VI stall; missing controls
are failures of evaluation. Shared runner lives at `scratch/agent/g1_level_coverage_common.zsh` (outside the queue glob).

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
- C patches (s6269): PatchesLib was shadowed on macOS (ld64 pulls archive members lazily). Now: `tools/weaken_patched_funcs.py ../N64Recomp/RecompiledFuncs` (after fixup_game_funcs, before cmake) weakens names in its PATCH_WEAKEN list, CMake `-force_load`s PatchesLib on Apple, and `fixup_patches_host.py` renames the stale allocateDisplayListBuffer override out of the way (the hand-fixed funcs_3 version stays live; heap guards remain fixup-inlined). Live: `isCinematicActive` (probe) and `setRngSeed` (s6277: arg passing + guest store, two-arm shadow check with ROGUESQ_RAND_CTL control, 0 mismatches / control fires; hand m5/probe hooks on that store are bypassed). Limitation (s6277): libc-reserved names (`rand` -> `rand_recomp`) cannot be patched, N64Recomp strict mode rejects the renamed symbol. To patch another function: add it to PATCH_WEAKEN, ensure the game version has no hand fixups, qualify two-arm.
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

## Next steps (single monotonic backlog; per-session history archived in PROJECT-OVERVIEW.md, "Archived CURRENT-TRUTH backlog")

- **s6355 (G3c a):** s6354 soak folded: radius-fade position pair is col=sp+0x74 -> cam.x/2 axis, row=sp+0x44 -> cam.z/2 axis (arm `pcr`, `ROGUESQ_EDGE_FADE_R2=r0,r1,116,68,...`). Two sources: hand-recomputed logged d (11.96) and row tracking cam.z/2 across frames; swapped pairing gives d 28-49. This supersedes the s6353 'both pairs invalid' reading (it dumped the wrong words). Rendered effect still UNPROVEN: edge-score medians identical to no-fade (cross-run, sky-heavy frames). Queued s6355_g3c_r2_redctl (red-haze ctl 0..1 + mid 18..26); see NEXT.md.
- **s6352 (G3c a):** s6326 'fade uninformative' was a wrong-site null (hook at 0x8004B910 never reaches drawn terrain, s6327/6328); the proven site is L_8004AA74 in 0x8004A6C0 (s6314). Built ROGUESQ_EDGE_FADE_R2 there (xoff/zoff stack-float offsets to calibrate from ROGUESQ_EDGE_FADE_R2_LOG); soak s6352_g3c_r2 queued, result pending. apply10f-i now wired in fixup. Single-source until the control fires.
- **s6350 (G3c a):** red-VTX thread CLOSED (two sources: s6349 host-write census + s6350 decode of all logged ranges as pos-only int16 x,y,z,0 records; 0xFF = sign bytes). Do not chase a colour writer. Next: return to G3c(a) far-terrain edge measurement (retail-vs-dd arm frames, edge fade) and G3c(b)/(c) arms.
- **s6349 (G3c a) RESOLVED for 0x735560: "red" = int16 sign bytes of x,y,z,pad position shorts (F5 spec: vertex and colour arrays are separate; decoded quads like (-92,-273,-92,0)).** Fixed-range host-write census: zero host writes overlap `0x735560..0x7355D0` before phase 7 (all 96 rows are phase-7 `rsp_dmem_to_rdram` RDP-command writebacks; controls fired). Host-write and ordering hypotheses are dead. The logged "red" bytes are `FFA4 FEEF FFAA FF09...` = negative int16 position shorts (0xFF sign byte, 0000 pad), so the red detector (any 0xFF lane) is plausibly a false positive on sign bytes (single-source, unconfirmed). Next: check the detector against the F5 VTX field layout and re-score by field (pos vs colour); if red is only sign bytes, retire the s6330-s6348 red-writer thread and return to the real jagged-edge measurement.
- **s6348 (G3c a):** the target-range census captured every instrumented phase-5 guest store overlapping `0x735560..0x7355D0`; only `0x8000D114` pointer/list stores and one zero store at `0x80010FCC` appeared, and no post-value matched the independent red VTX boundary. Next: instrument host RDRAM writes overlapping this exact target range across the phase-5→phase-6 boundary, retaining API, sequence, pre-bytes, payload/post-bytes, and phase; retain the ordinary-store, VTX, bulk, and forced-red controls. The discriminator is a host write whose post-bytes first become the red boundary; absence with controls firing selects an earlier/uninstrumented copy or ordering gap. No fade/cull mitigation.
- **s6323 (G3c a):** builder grid coord at 0x80130C10 = camera*0.5 (origin 0). AA94 cell ids do NOT linearly track it (resid 12-15 cells). Next: fade by lit-vertex world radius ([edgepos]) from camera, skip cell mapping. See scratch/agent/NEXT.md.
- s6321 (G3c a): CAMERA POSITION FOUND: struct ptr at 0x80138D1C; +0x28 = 3x3 rotation (9 floats), +0x4C..0x54 = world pos x,y,z (smooth in flight; positive control orthonormal rows). Log: ROGUESQ_G3C_CAMLOG=1 (tools/apply_s6321_camlog.py). Cell scale 12.8 UNVERIFIED. Next: regress AA94 cell stash vs pos/12.8, then edge fade centred on camera. Single-source (one lvl1 run).
- s6320 (G3c a): RAM-snapshot scan (40 snaps, tools/g3c_ramscan.py) REFUTED a plain float position triple in 8 MB RDRAM (single-source); only triple = timeline ramp 0x8011A8F4. Next: log terrain-pass view matrix translation row (H-matrix) vs H-none.
- s6318 (G3c a): s6317 cal2 folded. Cell stash works (col/row span 0..63, wrapping = ring-buffer slot indices, not world coords). Floats at 0x80138D20 and 0x80137DBC are CONSTANT garbage across the run: not position records (H-cam/H-pl dead there). Next: fade centre = per-frame circular mean of visited cells mod 64, fade by circular distance; add a frame-boundary marker to the log first.
- (superseded by s6318) s6317 (G3c a): s6316 `cell=` junk explained: log fires in A6C0 epilogue where r19 != AA94's s3. AA94 now stashes cell (col,row)=(a0+0x18,+0x1A) into rs64_ef_col/row; [edgefade5] logs cell + 32 camera floats + 12 player floats. Soak s6317_g3c_cal2 queued; next regress cell mean vs floats for fade centre/cell size.
- s6316 (G3c a): s6315 REFUTED the fade centre: A6C0 a1 is a unit normal (no position) and 0x80137DBC is a slot not a float record (pl=1e10 garbage, f=1 everywhere). Position source = caller 0x8004AA94 a0 cell idx (+0x18/+0x1A halfwords). [edgefade4] calibration soak s6316_g3c_cal queued; next: find player cell/pos, move fade hook to AA94 level (or compute f per cell and pass via global).
- (superseded by s6316) s6315 (G3c a): ROGUESQ_EDGE_FADE=start,end[,r,g,b] built (apply10c, A6C0 epilogue; centre=player rec 0x80137DBC [1],[3]*GRIDSCALE 0.5 UNVERIFIED); soak s6315_g3c_edgefade3 queued, no result yet.
- s6314 (G3c a): CONFIRMED by run: 0x8004A6C0 (via 0x8004AA94) is the terrain lit-RGB writer; ROGUESQ_EDGE_FADE_TEST2=0.2 turns terrain near-black (scratch/agent/m6/s6314_g3c/{base,t2}_f1200.png), sky/HUD/craft unchanged. 0x8004B644 is NOT the terrain path (s6313 negative explained). Next: distance-based fade in A6C0 epilogue = ROGUESQ_EDGE_FADE.
- s6313 (G3c a): s6311 soak folded: RGB x0.2 hook at 0x8004B644 epilogue did NOT darken terrain (mean 109.9 vs 106.3) => positive control negative; a0 steps 0x10 with low nibble 0xC (Vtx colour) yet overwritten/cached elsewhere. Next: find later colour store/copy in buildGridCellMesh 0x8004BCA0..0x8004BFF4.
- s6311 (G3c a): 0x8004B644 a0 = 0x10-stride lit-colour scratch array (via 0x80137A50), not proven to be the Vtx; epilogue hook ROGUESQ_EDGE_FADE_TEST (RGB scale, positive control) + ROGUESQ_G3C_POSLOG built (tools/apply_s6311_edgefade.py); soak recipe s6311_g3c_edgefade actually queued in s6312 (s6311 never wrote it). Single-source static.
- s6309 (G3c a): buildGridCellMeshForFace has no colour/alpha store (link bytes only); fade hook must be in the 0x80046214..0x8004B644 callees (NEXT.md). Single-source static.
- s6306 (G3c a): built opt-in ROGUESQ_EDGE_DROP_D2 (tools/apply_s6303_celltest.py) and queued 3-arm dd3 soak s6306_g3c_edgedrop; RESULT s6307: hook fires (celltest pass flips to 0 for d2 above threshold; drop30 d2=127 pass=0 where r2=222) but dd3_none/drop100/drop30 are indistinguishable: terrain_med 0.038/0.043/0.043, edge_excess_med -0.004/-0.005/-0.005, hole_med 0.108/0.108/0.113 (control=PASS, ~1500 fb each). The 0x800434E4 r2 test does NOT gate the drawn footprint (single-source); the jagged edge is set elsewhere (footprint frustum 0x80043918 / mesh builder).
- s6305 (G3c a): forced fog at dd3 is flat across depth (far/mid/near magenta 0.25/0.27/0.27; nofog ~0, retail 0.01/0.02/0.03) -> no distance haze ramp; H-fade refuted, far edge = footprint trapezoid (s6303). Next: opt-in edge-ring fade in a fixup script (NEXT.md). Single-source.

- **s6289 corrects s6288 5j:** the dd3 `+128 chunks at 80E00000` alloc is NOT from the finder-grow (zero `[finder-grow]`/`[s6289-real]` lines in 10 failing logs; finder C-patch not live, it is in PATCH_WEAKEN). Culprit is another grow site (begin/b030/topup); `ra` in `[dlpoolx]` is always 0 so tag sites by constant. Parked behind G3c.
- **s6293 G3c terrain-edge arm table:** five concurrent level-1 arms all passed
  dump/terrain controls and held ~205 s clean. Edge-excess medians (outer 12.5%
  terrain minus center 50%) were retail 0.0212, DD2 -0.0000, DD3 -0.0043,
  aspect 0.0354, DD3+aspect 0.0344. Late-frame contact sheets visibly show the
  blocky boundary in opt-in arms. This is a qualified H-aspect lead, not a root
  cause: retail p90 was 0.2502 and the scorer/contact sheets share one runtime
  framebuffer source; H-fade/H-radius and the writer remain unresolved. No
  mitigation is allowed until the writer/value is named. Next: static-enumerate
  terrain/fog/radius writers, then one phase-gated writer/value discriminator.
- **s6308 G3c(a):** footprint-clamp run dropped as redundant: ROGUESQ_DRAW_DISTANCE already scales the 0x80043918 input (s6303 extent 29.4->78.3 cells; s6307 r2 test null) => H-frustum; next is an opt-in outer-ring fade in buildGridCellMeshForFace (see NEXT.md).
- **s6304:** fog-ramp soak + tools/g3c_fogramp.py queued (result pending; see NEXT.md).
- **s6303 G3c(a) cell-test result (single-source):** the r^2 test at 0x800434E4 is a NEAR ring (r2 153.8-220, identical in retail/dd3/aspect; pass = d2<r2). Traversed far extent: retail 29.4 cells, dd3 78.3, dd3+21:9 79.5 -> dd scales the footprint (0x80043918) ~2.7x, aspect does not. Not the far-edge writer. Next: in-flight fog/shade ramp vs distance (ROGUESQ_FORCE_FOG). Tools: tools/apply_s6303_celltest.py, tools/g3c_celltest.py.
- **s6296 G3c static enumeration (single-source):** terrain radius 0x8009DEAC feeds only the footprint frustum (0x80043918), a scroll offset (computeGridLayerScrollOffset) and the r^2 per-cell test (buildGridCellMeshForFace 0x800434E0); no guest fog/haze start/end derives from radius/FOV/aspect, so H-fade has no writer to scale. Remaining lead: per-vertex shade/alpha ramp by distance (measure in one phase-gated run) vs the footprint trapezoid far side itself.
- **s6295 G3c radius result:** 21:9 flight rows at 0x80043918 are raw 19.68-23.94, eff=1, identical to the retail band, so H-radius is ruled out for ASPECT (single-source). Remaining H-aspect/H-fade: static-enumerate the projection/fog writer next. Run key-driven arms one at a time (concurrent windows stall pre-flight).
- **s6294 G3c radius-writer probe:** the new fixup-backed probe at guest PC
  `0x80043918` (raw terrain-radius source `0x8009DEAC`) fired in the retail
  mission control (`raw` rose 16 -> ~24, `valid=1`) and in the 21:9 arm. The
  21:9 launch reached the widened 1024 VI origin `0x00B20400`, but the common
  harness was first keyed to the retail title origin and the corrected retry
  reached no mission; therefore this is instrument qualification, not a flight
  discriminator. Its pre-flight aspect samples were unchanged (`raw=16,2`,
  `eff=1`) and cannot select H-radius. Next: rerun with the known
  origin-agnostic recipe (`TITLE_ORIGIN='0x[0-9A-F]*' MISSION_RE='[0-9A-F]+'`),
  then proceed to the projection/fog writer if flight radius remains unchanged.
- **s6292 G3c turn-shake result:** the phase-gated camera/craft instrument passed
  its positive control in all four arms. Sign-alternation was retail 0.395,
  FPS60 0.625, wide-only 0.384, and FPS60+wide 0.632, with thousands of records
  per arm and zero crash markers. This selects H-fps60 (camera cadence/pacing),
  while H-aspect is not supported. **SUPERSEDED s6302:** alternation fraction is amplitude-blind (FPS60 accel rms is lower); tools/g3c_hf.py HF residual (control fired) = retail 11.8, FPS60 12.2, wide 11.2, both 12.2 mrad -> no arm adds shake; (c) is H-retail/30fps judder, closed pending owner.
- **Owner visual report 2026-10-26 (G3c, next):**
  (a) jagged/blocky terrain edge where fog normally hides it, (b) knife spikes still
  visible (G3b "retail-identical" was never checked against a reference: reopened),
  (c) slight screen shake while turning. Spec: ITERATION.md item 3c G3c.
  **s6293 (c/a) status:** shake discriminator selects FPS60; the terrain-edge
  arm table gives an aspect lead but does not name the cause. Next is the writer
  audit, then (b) spikes reference check.

0. **G3 CLOSED (s6267):** craft shade matches retail (dark-pixel median 74.9 vs 76.0, radar-ring control matches; docs/G3-INFLIGHT-DIFF.md). Next: owner playtest judgement of opt-ins (docs/OWNER-OPT-INS.md); G5 renaming sweep COMPLETE (s6268: 5 placeholders left in syms toml are code/data fragments of named functions, not functions); next rung: optional MIPS source-to-ELF patch qualification (item 5).
1. **G1d widescreen (closed as opt-in, was active, `scratch/agent/NEXT.md`).** **s6275: ROGUESQ_SKIP_TOGGLE=<N> added (lib/rt64 rt64_rdp.cpp, within-run on/off every N VI; 268 transitions logged = instrument works) but fb dumps stayed at 500-frame cadence (ROGUESQ_FB_DUMP_EVERY not forwarded by g1_level_coverage_common.zsh), so no adjacent on/off pair: residual draw-vs-stale-fb question still OPEN, thread parked/owner-optional; NEXT.md = wait for owner feedback or forward the dump env and rerun s6275_run.sh. No conclusion overturned.** **s6276: rerun done (cadence bug was m6_god_common.sh COMMON overriding XENV, fixed): 49 w900 dumps bit-identical across skip on/off, run stalled at phase=7, no blanking control -> VOID, residual stays OPEN/owner-optional; revive only with a native-target dump or writeback-gating toggle.** **s6274 correction: the s6234 'H-up167 supported' lead and its 'compare up_167 RDRAM vs upload' next step are SUPERSEDED by s6239/s6240 (up_167 is not sampled by texrects; its triangles are edge slivers) - it was believable because the draw-time hash log showed up_167 sampled 6x/frame, but the sampled rows were all valid. Open item is only the ~0.13 ph4 lower-band residual (s6253); NEXT.md holds a within-run skip-toggle design, owner-optional, park after one iteration.** s6234: draw-time hash log (ROGUESQ_LOG_TEXHASH, control fired): noisy up_167 (h98bb35b7e7c80445) IS sampled 6x/frame throughout title, 0 cache misses -> H-up167 supported, H-cache disfavoured (rect-tile mapping not shown); next: log its LoadTile RDRAM source/dxt/tmem offset at upload and compare RDRAM bytes vs uploaded bytes. s6233 (single-source, NO positive control): `reinterpretTileRecord` logged 0 calls in a w900 title+select run (ROGUESQ_LOG_REINTERPRET / ROGUESQ_SKIP_REINTERPRET added in lib/rt64, patch exported) -> the s6232 framebuffer-reinterpret lead is DISFAVOURED (it was believable because the widened fb range overlaps photo tile sources); remaining leads H-up167 (rect = noisy 64x32 upload h98bb35b7e7c80445) and H-cache; next: per-texrect draw-time texture hash vs up_167 with a force-mark control. s6232: RT64 upload-time TMEM dump (ROGUESQ_DUMP_TMEM_DIR): 99/100 photo tiles upload CLEAN while the garbage rect still draws in the same run (single-source) -> not TMEM-upload content; lead = RT64 framebuffer->tile reinterpretation (`reinterpretTileRecord`) over the widened fb range; next log its hits in title phase. s6231: SETTILE/LOADBLOCK params identical for all photo tiles (game-side param ruled out); parse-time tile dump noisy even for good tiles (not the drawn texture) — next dump at RT64 upload time. s6230: RDRAM source bytes (first 64 B) of the garbage-rect photo tiles look like real photo (distinct 2-24, not noise ~55); H-src disfavoured (single-source), lead is RT64/TMEM tile-line/LOADBLOCK dxt mismatch; next dump full tile bytes + SETTILE/LOADBLOCK params. s6229: title/menu layer is a rigid +193 translation of the 512 layout (two passes + text; position questions CLOSED); garbage rect = noise texel content in photo columns, persists with DROP_EXTRA=0x25000 (pool alias not the cause); next: per-texrect texture source address and last writer. s6228: select screen centred at w796/w1024, but title photo backdrop still offset+cropped and garbage rect persists (not window/phase artifact); next name the photo draw's camera. s6227: defect A fixed (vpw 640-cam scale); next re-verify title/select frames at w796/w1024 and re-test defect B. s6222 (single-source): wide title art is the same 64x32 texrect grid as 4:3 but drawn at x 241..753 (not centred 142); stride refuted, x-origin of menu 2D layer is the lead; find the guest operand at texrect emitter PC 0x80007904 (NEXT.md). s6221 hangar alias test showed no effect; the notes below on alias are low priority. s6216: alias measured (ctl HUD TLUT 0xB24xxx outside memset/wb ranges ending 0xB00000; wide TLUT inside range ending at pool 0xAE6E00): the s6207 image drop is 0x25000 too short; next test drop += 0x25000 (NEXT.md). s6215 (lldb write-watch, positive control held): wide 0xAE5F20/0xAE6B20 "texels" are genuine guest HUD TLUT data (`packTlutEntriesRgba5551 <- loadTextureToMemory <- parseHmtMaterials <- buildHudAmmoReadout`), later zeroed by `rs_memset <- initVideoSubsystem` and rewritten by RT64 `copyNativeToRAM` writeback (wb range ends 0xAE6E00). Aliasing of texture memory with the enlarged framebuffer range. Next: compare wb/memset extents against texture allocations (NEXT.md). Keep the image drop; do not raise the 48-line cap, skip `copyNativeToRAM`, retarget `0x8096D600`, write `0x801163E8`, change n=3 `t0`, raise `osMemSize` or move `f0`.
2. **G1e higher frame rate (CLOSED as opt-in, s6261: FPS60 holds 301 s lvl1 and 303 s lvl10, 0 crash/0 VI stall; lvl5 hold also clean s6262; owner to judge feel; combo FPS60+dd2 CLEAN on lvl1+lvl5 (s6262 soaks, folded s6263: 302 s, alive_at_end=1, 0 stall, 0 crash lines); widescreen+FPS60 s6263 soaks were HARNESS-VOID (notitle: wide origins != 0x790400; game itself reached width=796/1024 flight, no crash), re-queued s6264 with origin-agnostic recipes, FOLDED s6265: 16:9 and 21:9 lvl1 ~205 s holds clean (alive_at_end=1, 0 stall, 0 crash lines; holds shorter than 300 s) - G1e/G1d combos closed; next G3 in-flight frame diffs; owner page docs/OWNER-OPT-INS.md).** s6255: byte 0x80128EAF 2->1 gives 60 gfx tasks/s in flight (RSP ~10 ms/frame, VI 60/s) and craft path/s is UNCHANGED (dt word 0x8011A904 halves; sim is delta-time) - opt-in `ROGUESQ_FPS60=1` shipped (default retail). Single-source, lvl1 only; still to check: mission timer, AI, particles/anim rate, audio sync, other levels, 300 s holds, hangar/title. Owner judges feel. s6256: whole-rdram rate diff (tools/g1e_rate_diff.py, ROGUESQ_G1E_DUMP) on lvl1+lvl5, 300 s holds clean: mission clocks time-based (ratio 1.00); only ~12 words frame-locked, incl. mission frame counter 0x8013889C (read by NPC curved-path/visibility/anim code) and advanceNpcOnCurvedPath's per-call countdown (static, single-source). s6257: NPC curved-path countdown (rec+0x1C) only gates a bounded re-probe cadence, motion is separate (static read) and no NPC float runs 2x (tools/g1e_float_rate_diff.py, lvl1+lvl5) -> H-negligible, caveat: no direct position control. s6258: lvl10 snap soak clean (303 s, 0 crash/stall); rate diff shows 0 frame-locked words (int arm has no positive control on this run, single-source), float diff only the known dt word 0x8011A8F4 (2.0x) with controls ~1. s6259: audio synth tick is per-VI (musyxSynthFrame), VI stays 60/s -> audio H-clean (static+rate-diff, no direct cue-timing control). s6259 hangar soak clean (mission_t 77 vs 81 s baseline, 0 stall) -> H-menu refuted. Remaining: FPS60 300 s holds lvl1/5/10 (queued s6260_g1e_fps60_l1/l5/l10), then ask owner to judge feel.
3. **G1 level 10/15 note:** both pass (a)+(b) only with `ROGUESQ_FORCE_PLANET_UNLOCK=0xFF` or a
   ~790 s planet-intro wait (SOAK_TIMEOUT >= 900). Forced-hit objective (d) is PARTIAL: counters move
   on lvl1-5,7,8 but no level end was shown driven by them (s5997).
4. **Parked, do not revive without new evidence:** G4 crash hunting (all 19 levels + hangar route
   clean, s5999-s6082); G3 hangar artifacts; M4 accumulator; title plume `si_addr=0x58`.
5. **C-patch pipeline qualified (s6269, arg/store case s6277: setRngSeed live, rand unpatchable); s6270 300 s holds with the patched binary: lvl11 and lvl14 CLEAN (s6271 fold), lvl18 CLEAN (s6270 soak rc=0); s6271_plume_title16_patched was a BROKEN RECIPE (bash vs zsh, no game ran, NO DATA — superseded: its 'clean' expectation was never earned); refixed as s6272_plume_attach16_patched, FOLDED s6273: control=PASS, titles 16/16, bad=0 (plume did not recur; parked)** (side-effect check only, not a G4 sweep). Fold the SOAK-RESULTS verdicts first; crash -> backtrace + root cause. Any new patch needs its target in tools/weaken_patched_funcs.py PATCH_WEAKEN and a two-arm qualification.
5d. **s6282:** dd1 control (lvl1, same recipe, 120 s): ZERO findAndUnlinkSmallestEntry calls, 0 crashes, 0 VI stalls (setRngSeed/isCinematicActive lines = positive control for patch logging). dd3: used list already 374 at the fallback's first call, first NULL at call ~51 (used 424-430, 82-83 size-0 free entries) in two runs. SELECTS H-pool-small (demand outruns exact-fit buckets) over H-no-return; REFUTES 'POOLX scales this pool' (POOLX sizes the terrain stream pool, apply_s6058_poolx.py). NEXT: find the initialiser of the bucket pool (array ptr 0x80128F00, 2048 buckets, ~139 entries) and scale it with ROGUESQ_DRAW_DISTANCE, addresses < 0x81000000. Superseded: s6281's 'H-pool-small vs H-no-return split' is now resolved to pool-small (single recipe).
5j. **s6288:** the s6286 'step at 43' / menu death with DLPOOLX was our own ungated begin-time GROW hook (fired at len 254<256 in the menu); now gated to after begin#AT. Gated dd3 (MB=2) reaches begin ~4000 (cache 1356->635, leak ~0.2/begin) then the FIRST finder-grow chain (pc 0x80015544) -> SIGBUS guest addr 1 in drawSubtitleText 5/5: synthesized chain shape wrong for that caller. Next: read the 0x80015544 caller + drawSubtitleText chunk use to fix the chain convention (+0/+4/size fields), then residual leak measurement.
5i. **s6287 (corrects s6286 'step at 43'):** that step was a DLPOOLX-grow artifact; unmodified dd3 decays 1035@begin6000 -> 51@~6590 (5/5) -> 0@6656 then crashes in beginFrameDLChunk; dd1 floor 77. ROGUESQ_PPLOG=1 (tools/apply_s6287_ppcount.py): pushes==pops/2 every frame in both arms (no missing return); heavy frame demand ~330 chunks at dd3 vs ~76 at dd1 (renderFlatMeshFaceGroup 0x80011470, emitMaterialTexturedDL 0x8000E180). SELECTS H-burst + small unattributed leak. Next: residual (len delta vs counted net) per begin (NEXT.md).
5h. **s6286 (corrects s6285 'dd3 drains slowly'):** DL-chunk cache length is identical dd1/dd3 for begins 1-42, then at dd3 drops 254 -> 0 at begin 43-44 and stays empty (every +128 grow consumed in-frame); dd1 recovers though reclaimDisplayListChunk is never called (returns come from the `sw 0x63B0` sites). Also: s6285's per-site top-ups/b030/finder-grow BREAK BOOT whenever DLPOOLX=1 (grow an uninitialised cache) — the 'notitle 5/5' in those arms was that, not dd3; now gated by `rs64_s6285_en()` (armed after begin#ROGUESQ_DLPOOLX_AT, off when ROGUESQ_DLPOOLX_PRE set). Pre-grow at begin#1 also kills level start (finder NULL call 1). Next: per-frame 0x63B0 push/pop attribution begins 41-45.
5g. **s6285:** finder callers = 110 sites/29 funcs; finder-grow removes the NULL at call 58 but dd3 still dies at unguarded inline cache pops (~447 sites `lw rK,0x63B0` without empty test); blanket top-up breaks rs_free in the menu. Consumers outrun the cache; next = chunk in-use high-water per frame dd1 vs dd3 and the reclaim sink, then a single one-shot pre-grow at beginFrameDLChunk. DLPOOLX stays env-gated.
5f. **s6284:** DL-chunk arena capacity refuted: DLPOOLX arena 1 MB vs 4 MB give identical dd3 failure (15 grows = 1920 chunks, arena never exhausted, finder NULL at call 58/59, SIGBUS). The grow hook only runs at beginFrameDLChunk; the finder is reached from another empty-cache allocation site. Next: static-enumerate finder callers on that path and grow there.
5e. **s6283 (supersedes the s6282 NEXT premise 'scale the bucket pool carve'):** the LUT bucket table (`initTextureLUTAndAllocBuffers` 0x8001E230, count a0=a1=2048 from caller) is NOT the limiting pool. dd3 with ROGUESQ_LUTSCALE=4 (buckets=8192, control line printed) fails identically to LUTSCALE=1: used_len 374 at call 1, 424 at call 52, NULL at call 59 (DD_UNSAFE=1 required, else s6102 caps dd to 2). It was believable because the finder walks that bucket array and ~139 entries sit in it, but entry supply is set elsewhere. Next: request-size histogram dd1 vs dd3 + who feeds/returns used-list entries (NEXT.md).
5c. **s6281:** at the dd3 NULL return the pool holds 83 bucket entries, ALL size 0 (finder skips them), and 429 entries on the used list (init had ~139): usable chunks are exhausted, not corrupted. Single-source; needs a dd1 control with the same dump.
5b. **s6280 CORRECTION of s6278/s6279: the dd3 'wild pointer 0xd4400005' crash was the s6278 diagnostic wrapper's own bug** (tools/fixup_patches_host.py read the used-list head/bucket array with base 0x80000000 instead of 0x80120000, i.e. code at 0x80008EF8 as a pointer; lldb frame #0 was the wrapper at patches.c:1407, head=0x54400001 = a MIPS `bnel`). With the base fixed the finder IS called (calls=1..32+, bad=0) and the dd3 run dies later at the REAL dd>=3 signature: `[find-null] call=59 buckets=2048 usedhead=0x801605C0` (first 64 buckets empty) then SIGBUS si_addr=0x380000004 last-guest-pc 0x8000ade8 = the caller dereferencing the NULL return. So dd3 is DL-chunk POOL EXHAUSTION (59 allocations then empty), not corruption; no mystery writer. Next: where the pool is sized/filled (see NEXT.md). The s6278/s6279 'finder uncalled' and 'patch exonerated by identical crash' conclusions are VOID (both arms crashed in the wrapper).
6. Optional: real-input lv0 human play.

### Settled results worth keeping (from the archived backlog)

- **G1b CLOSED (s6017):** slow seconds were our O(n^2) scan in rsp_dpc_submit (dpc_bridge.cpp); fixed
  with a hash index: 17.6% -> 0% slow seconds. `ROGUESQ_G1B=1` is the frame-time instrument.
- **G3b CLOSED as opt-in (s6085):** spike lines = ucode clip-plane wedges (Y pinned -170.25) plus
  off-screen tris; `ROGUESQ_CULL_SPIKE=1` opt-in cull, `ROGUESQ_LOG_SPIKE` instrument.
- **G1c phase 2 CLOSED (s6102):** `ROGUESQ_DRAW_DISTANCE` capped at 2 (auto-far; tri x2.3, terrain
  fraction 0.030->0.074, VI 60/s, 300 s clean on L1/L5/L10) unless `ROGUESQ_DD_UNSAFE=1`. dd>=3
  dies in 150-290 s: display-list chunk pool (*(0x801163B0)) / finder `findAndUnlinkSmallestEntry`
  (0x8002221C) returns NULL, deref at 0x8000A97C; not heap, arena, LUT size or pool size (s6086-s6101).
  Writer of the exhaustion unnamed. rc=0 is not a pass: read `alive_at_end`. Levers: UCODE_CAP
  (`ROGUESQ_UCODE_CAP`, default 16384 retail), DD_FAR, POOLX (px2 safe, px3+ exhausts the 8 MB heap),
  BIGARENA, DLPOOLX. Owner guide: docs/DRAW-DISTANCE.md. Never trust the s6088/s6094 bucket readers.
- **G3 pillar stubs:** were our FIX_ZERO_SHADE (default now OFF, s5971). Render fidelity otherwise
  closed at eyeball level (retail oracle: docs/G3-RETAIL-PIXEL-ORACLE.md).
- Harness lessons: macOS has no `timeout` (use perl alarm); lldb host RDRAM base is per-run; guest
  globals read from C++ need `rdram+(int32)addr`; recipes need `# SOAK_TIMEOUT=` headers; always diff
  tele vs ctl recipes.

## Evidence index

Use `PORTING-STATE.md` only through bounded grep/sed windows. Use
`docs/PROJECT-OVERVIEW.md` for migrated history, `docs/M5-AUDIO-PLAN.md` for
audio inventory, `docs/F5-UCODE-REFERENCE.md` for the microcode contract,
`docs/M6-OBJECTIVE-COUNTER-WRITERS.md` and `docs/M6-PHASE-MACHINE.md` for
mission logic, and `scratch/agent/SOAK-RESULTS.md` for queued verdicts.

## G1d widescreen (distilled s6113-s6222; full log in PROJECT-OVERVIEW.md "Archived CURRENT-TRUTH G1d log")
Default stays retail 4:3. Opt-in levers: `ROGUESQ_ASPECT=<w>:<h>` (derives FB_WIDTH + scales in main.cpp `rs64_g1d_apply_aspect_policy`), `ROGUESQ_FB_WIDTH`, `ROGUESQ_VPW_SCALE`, `ROGUESQ_ASPECT_SCALE`, `ROGUESQ_FP_XSCALE` (terrain footprint), `ROGUESQ_HUD_ANCHOR=A,R` + `ROGUESQ_SHIFT_REGION` (HUD/radar), `ROGUESQ_OSMEM_MB` (<=16), `ROGUESQ_G1D_DROP_EXTRA`. Width clamps to 1024 (1032+ fails, root constant unnamed).
- **Memory (settled).** Wide framebuffers eat the 8 MB heap (partitionFramebufferMemory 0x80000DD4: each fb w*448*2) -> NULL rs_malloc(0x1000) -> crash at mission start. Fix: `ROGUESQ_OSMEM_MB=12`. Required: all ~1011 hard-coded `0x80800000` guards became runtime `RS64_RAM_TOP` (tools/fixup_ramtop.py, tools/apply_s6132_ramtop_cpp.py); RT64/librecomp 8 MB caps widened to 16 MB (state.cpp, workload_queue.cpp, f3dfactor5.cpp, rsp.hpp DMA read AND write, sp.cpp, dpc_bridge.cpp; lib patches exported). 12 MB harness origins = 8 MB origins +0x400000 (use TITLE_ORIGIN/MISSION_RE; wide origins differ per width).
- **Working at wide (single-source each):** 16:9 (w796) and 21:9 (w1024) level-1 flight frames correct; terrain fills width (FP_XSCALE); flight HUD sprites emitted by 0x800159B4 (x in 4x units, [0x800006F8]=4.0) anchored by HUD_ANCHOR, radar disc is RDP tris shifted via SHIFT_REGION, reticle exempt (world-projected); menu/hangar video state and fb allocation widened via the `buildAndRegisterDefaultMaterial` / partition hooks (512x448 and 512x340 rewrites), mission reached and held ~182 s clean at 12 MB wide.
- **Defect A (2D menus) FIXED s6227:** cause was our s6112 vpw camera scale applying W/512 to 640-wide menu cameras (cx 320->562; origin = cx-320+64). Now 640-wide cams scale by W/640: title texrect origin 193 at w900 (centred), level-select screenshot centred/full width. Still to check: title-phase capture (fix_01) shows garbage block left + off-centre art (maybe defect B), select-craft cropping, other widths (w796/w1024).
- **Open defect B (phase-4 central corruption, intermittent, s6172-s6212):** wide phase-4 title frame shows a corrupt central rectangle. Chain of evidence: route/CI/scissor identical modulo width (no hidden CI pass); RT64 readback is the immediate writer but source hashes match (not RT64 layout); wide RDP stream has ~2x central TEXRECTs from the same guest PC; the extra texture reads come from a pool-chunk field whose pointer (0xAE5F20..0xAE6B20) lies in the phase-3 640x340 image writeback span ending 0xB00000 — the widened n=3 carve (t0 0xAE200 vs 0x70000) makes the DL-chunk pool (`0xAE6E00`) overlap the phase-2/3 images; texels are rewritten after the phase-3 writeback by an unnamed writer (s6214 H-fresh). Do NOT drop the writeback; do NOT raise osMemSize (overlap is top-invariant). `ROGUESQ_G1D_DROP_EXTRA=0x25000` relocates the pool off the HUD TLUT gap: s6219/s6221 show identical sane HUD and no corruption difference, H-alias unsupported. Defect B may be moot if defect A's layout fix covers it; re-test only after A.
- **Superseded in this arc:** s6120 "widened frame works end to end" (pre-flight screenshot only); s6130 "pool not built at 12 MB" (instrument's 8 MB walk bound); s6145-s6153 HUD x/y offsets (+0x24/+0x28 are scale); s6195 "root first 0x100 bytes zero" (23-bit-masked witness); ring-producer / heap-fragmentation hypotheses (s6125/s6127); s6219 ammo-readout premise (menu-only overlay).

- s6236 (offline, single-source): noisy up_167 TMEM = a 672-byte f4/s2 LoadBlock at tmem 0 (srcfnv 16aef4cc85ca1200, from 0x803780/0x9712B0/0x93AD50/0x94FE70) + ~3.4 KB stale TMEM from earlier 2048/4096-B loads; hash churns because the stale tail churns. Next: log SETTILE/SETTILESIZE (line, size, fmt) of the draw using up_167 to see whether the 64x32 span is the game's or RT64-derived (NEXT.md).
- s6235: per-load log (ROGUESQ_LOG_LOADS) shows no single LoadBlock>=1KB builds the noisy up_167 TMEM (matcher control OK, single-source); H-load disfavoured, next = stamp upload with load seq and diff the preceding loads (see NEXT.md).

- s6237 (G1d): the noisy up_167 title texture is a game-defined 64x21 4bpp tile (lrt=80, maskt=5); identical descriptor at 4:3 and wide, so RT64 does not widen it. Rows 21-31 are stale TMEM by design. Open: does a draw sample them (NEXT.md). Logger: `ROGUESQ_LOG_UPSPAN=1`.

- s6238 (G1d): `ROGUESQ_LOG_TEXRECT_T=1` texrect t-range logger: 120 family draws sample only valid rows (16-row tile t<=15.75; 80-row tile), maskt=0; the maskt=5 up_167 render tile never appeared in the capped sample. H-sample-stale unproven (NEXT.md: filter on maskt==5).
- s6239: maskt==5 texrect draws = 0 (ctl 20); up_167 not sampled by texrects.
- s6240 (G1d, single-source): `ROGUESQ_LOG_TRI_T=1` triangle tile logger: 102 up_167-descriptor triangles are <=3x2 px edge slivers, t<=20.01 (<21 valid rows) -> H-sample-stale refuted on texrect AND triangle paths; up_167 is not the garbage-rect source. Next: key the garbage region by screen bbox (NEXT.md).
- s6242 (G1d): ROGUESQ_SKIP_DRAW (tri/texrect/fill, ph3 or ph2) does not remove the wide-title garbage rect; ph3 control did not blank frame (retained?). Next: all-phase skip + fb readback log (NEXT.md).
- s6241 (G1d, single-source): `ROGUESQ_LOG_BBOX=1` region logger (control fired): photo CI4 wedge triangles with x<0 bboxes occur at both 4:3 and wide, so they are not the wide-only painter; logging cannot name the painter. Next: skip-bisect by draw class in ph3 (NEXT.md).
- s6243 (G1d): SKIPPH=-1 all-draw skip blanks the wide title (control OK); ph4-only skip leaves noise below y~255 -> garbage rect is aliased undrawn fb RAM, not a draw. Next: intersect RT64 writeback ranges with the w900 fb (NEXT.md).
- s6244 (G1d): ROGUESQ_WBLOG: ph4 title colour writeback addr=0xB3B200 ww=900 rows 0-447 covers the whole 512x444 scan-out (origin 0xB3AE00); noise = native-target undrawn rows written back. [SUPERSEDED by s6245/s6246: believable because the writeback range covered the whole fb, but clamping it did not remove the noise.]


## s6245/s6246 update (G1d wide-title noise)
- s6245: clamping the w900 writeback to 256 rows made the lower band MORE non-black (0.998 vs 0.819 control) -> undrawn-row writeback is not the sole source (single run each).
- s6246: ROGUESQ_WB_CLEAR=1 (zero fb span before writeback) -> lower band 0.545 (control 0.819): stale RAM is ~0.27 of it. Remainder is real drawn content (hangar bg tiled across 900 width, seams x~65/130/195/705/770) plus white native-target blocks at lower corners (x<65, x>770, y>255) that survive pre-zeroing. Single run per arm.
- Next: find which draw class paints the tiled bg strips and the white corners (s6244 skip arms), widen/clamp the bg S range, clear native target to black at wide alloc (NEXT.md).
- s6247: phase-4 skip arms with WB_CLEAR (single run each, lower-band non-black): none 0.639, tri-all 0.699, fill 0.809, texrect-all 0.174 (upper 0.0). Texrects paint the tiled bg/strips; residual 0.174 is neither texrect nor tri -> fill or native white corners. Next: clear native target to black at wide alloc, re-measure residual.

- s6248: H-native-white REFUTED by source (RT64 clearColorTarget clears to opaque black, rt64_render_target.cpp:353 / plume RenderColor default a=1). Residual 0.174 comes from RDRAM read-in or fill ops, not an uncleared target. Next: log/zero the RDRAM span at read-in time (rt64_state.cpp ~2412 read path) + texrect S ranges (LOG_TEXRECT_T).

- s6249: G1d wide-title: RI_CLEAR (pre-read-in memset) cuts texrect-skip residual only 0.174->0.132; H-readin minor. Open: H-bg-wrap, fill-rect residual. See NEXT.md.
- s6250: bboxR ph4 garbage-region texrects are 8-22 px glyph-like rects, no >512 S span (single-source, 600-line cap) -> H-bg-wrap unsupported. Open: fill-rect residual (NEXT.md).
- s6251: wide-title ph4 lower-band residual: texrect-all 0.132 -> fill+texrect-all 0.050, so fill ops paint ~0.08 (single-source). skip-all arm reads 1.0 (invalid control). Open: remaining 0.05 (try fill+texrect+tri-all csv, log fill rects with colour).
- s6252: fill+texrect+tri-all csv arm reads lower=1.0 (same invalid-control artefact as skip-all), so skipping tris cannot attribute the last 0.05; H-tri-rest untested. Next: log fill rect and tri extents/colours in ph4 and correlate with non-black columns (positive control: a logged primitive covering the band must map to non-black pixels). Skip-class arms are exhausted. No earlier conclusion overturned.
- s6253: ph4 issues zero fill rects (ROGUESQ_LOG_FILLALL positive control 830 lines in ph2/3/5), so s6251's "fill paints 0.08" is refuted; texrect-all lower reads 0.131-0.173 across runs, fb dump at frame 500 reads 1.0 in all skip arms (invalid). Residual unattributed; next: within-run toggle, not cross-run.

- s6279 (VOID, see 5b): the identical-crash 'exoneration' compared two arms that both crashed inside the buggy wrapper.

- s6297: s6293 aspect/dd3_aspect edge scores are VOID (dump decoded 1024-wide VI as 512, fixed via ROGUESQ_FB_WIDTH=1024). Corrected aspect edge_excess_med=-0.0026 vs retail 0.0212: H-aspect unsupported. dd3_aspect not yet rescored.

- s6299 G3c(a): tools/g3c_horizon_score.py; jump_med retail .281 / dd3 .317 / aspect .394 / dd3_aspect .400 (matched-frame aspect-retail +.111, dd3-retail +.023); hole metric void (water=sky colour). Single-source, aspect-confounded. Next: G3c(b) spikes (NEXT.md).
- s6300 G3c(b): RSP divide unit (VRCP/VRSQ + tables) matches ares/hardware ROM values (rcp[0..3]=FFFF,FF00,FE01,FD04); wedges not explained by it. VCH/VCL/VCR/VMULF/VMACF and a vertex replay of swap 1867 still open; CULL_SPIKE stays opt-in. Single-source.
- s6301 G3c(b): tools/rsp_vu_diff: 496/496 VU op/element hashes identical SIMD vs SISD (31 ops x 16 e), mutation control fires on VCL. Emulation of clip/multiply ops has no SIMD defect; still ares-lineage (not hardware). Spike thread: ask owner re CULL_SPIKE default; else move on.

- s6322: visited-cell regression vs cam/s at baseline for s=12.8 (refuted); next fit emitting cells. 
- s6319: footprint-derived fade centre (circular mean of AA94 cells) REFUTED offline (single-source, s6317 log): AA94 visits the whole 64-ring as a streaming sweep, centre jumps, R~0.5. G3c(a) fade needs a true player/camera position source (RAM-diff scan of smoothly changing floats in flight).

- s6324 (G3c a): terrain lit-vertex pos (hook 0x8004B910, 0x48/0x50($sp)) is in the cam*0.5 grid frame; radius from cam*0.5 bounded: dd1 max 19.5 / p99 17.7, dd3 max 26.1 / p99 25.2 (single-source, forward-biased sample). AA94 cell-id mapping is unnecessary: fade by that radius directly (next: implement fade + frame compare).

- s6327 (g3c-a): force-red at the 0x8004B910 epilogue (ROGUESQ_EDGE_FORCE_RED) leaves in-flight terrain unchanged (single-source, viewed fb 4002 + red-fraction vs ctl) -> that epilogue is NOT the terrain colour sink; the s6325/6326 radfade hook is misplaced. Next: locate the real vertex-colour writer (see NEXT.md).
- s6351 G3c(b): replay unrunnable (logs gone, no independent RSP ref, no clip constants in F5 ref); stays opt-in, owner call. Next: (a) writer audit.

- s6353: G3c(a) radfade2 at AA74 positive control PASSED (s6352 ctl flat sky-blue terrain vs dark in log arm). Position stack pair unresolved: only sp+0x44 varies (x-like); s6353 soak tests 0x44/0x48 and 0x44/0x4C. Single-source.
- s6354: s6353 pairs invalid (w4=0 always). Decoded from code: at AA74 hook sp+0x44=row, sp+0x74=col, sp+0x40=height. Soak s6354_g3c_r2_colrow queued (xoff=116,zoff=68 and swapped). Single-source until logged d varies and is bounded.
