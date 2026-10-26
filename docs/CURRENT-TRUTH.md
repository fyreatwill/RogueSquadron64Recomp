# Rogue Squadron 64 Recomp — current truth

Compact operational handoff, maintained as of Session 6237 (2026-10-25).
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

## Next steps (single monotonic backlog; per-session history archived in PROJECT-OVERVIEW.md, "Archived CURRENT-TRUTH backlog")

1. **G1d widescreen (active, `scratch/agent/NEXT.md`).** s6234: draw-time hash log (ROGUESQ_LOG_TEXHASH, control fired): noisy up_167 (h98bb35b7e7c80445) IS sampled 6x/frame throughout title, 0 cache misses -> H-up167 supported, H-cache disfavoured (rect-tile mapping not shown); next: log its LoadTile RDRAM source/dxt/tmem offset at upload and compare RDRAM bytes vs uploaded bytes. s6233 (single-source, NO positive control): `reinterpretTileRecord` logged 0 calls in a w900 title+select run (ROGUESQ_LOG_REINTERPRET / ROGUESQ_SKIP_REINTERPRET added in lib/rt64, patch exported) -> the s6232 framebuffer-reinterpret lead is DISFAVOURED (it was believable because the widened fb range overlaps photo tile sources); remaining leads H-up167 (rect = noisy 64x32 upload h98bb35b7e7c80445) and H-cache; next: per-texrect draw-time texture hash vs up_167 with a force-mark control. s6232: RT64 upload-time TMEM dump (ROGUESQ_DUMP_TMEM_DIR): 99/100 photo tiles upload CLEAN while the garbage rect still draws in the same run (single-source) -> not TMEM-upload content; lead = RT64 framebuffer->tile reinterpretation (`reinterpretTileRecord`) over the widened fb range; next log its hits in title phase. s6231: SETTILE/LOADBLOCK params identical for all photo tiles (game-side param ruled out); parse-time tile dump noisy even for good tiles (not the drawn texture) — next dump at RT64 upload time. s6230: RDRAM source bytes (first 64 B) of the garbage-rect photo tiles look like real photo (distinct 2-24, not noise ~55); H-src disfavoured (single-source), lead is RT64/TMEM tile-line/LOADBLOCK dxt mismatch; next dump full tile bytes + SETTILE/LOADBLOCK params. s6229: title/menu layer is a rigid +193 translation of the 512 layout (two passes + text; position questions CLOSED); garbage rect = noise texel content in photo columns, persists with DROP_EXTRA=0x25000 (pool alias not the cause); next: per-texrect texture source address and last writer. s6228: select screen centred at w796/w1024, but title photo backdrop still offset+cropped and garbage rect persists (not window/phase artifact); next name the photo draw's camera. s6227: defect A fixed (vpw 640-cam scale); next re-verify title/select frames at w796/w1024 and re-test defect B. s6222 (single-source): wide title art is the same 64x32 texrect grid as 4:3 but drawn at x 241..753 (not centred 142); stride refuted, x-origin of menu 2D layer is the lead; find the guest operand at texrect emitter PC 0x80007904 (NEXT.md). s6221 hangar alias test showed no effect; the notes below on alias are low priority. s6216: alias measured (ctl HUD TLUT 0xB24xxx outside memset/wb ranges ending 0xB00000; wide TLUT inside range ending at pool 0xAE6E00): the s6207 image drop is 0x25000 too short; next test drop += 0x25000 (NEXT.md). s6215 (lldb write-watch, positive control held): wide 0xAE5F20/0xAE6B20 "texels" are genuine guest HUD TLUT data (`packTlutEntriesRgba5551 <- loadTextureToMemory <- parseHmtMaterials <- buildHudAmmoReadout`), later zeroed by `rs_memset <- initVideoSubsystem` and rewritten by RT64 `copyNativeToRAM` writeback (wb range ends 0xAE6E00). Aliasing of texture memory with the enlarged framebuffer range. Next: compare wb/memset extents against texture allocations (NEXT.md). Keep the image drop; do not raise the 48-line cap, skip `copyNativeToRAM`, retarget `0x8096D600`, write `0x801163E8`, change n=3 `t0`, raise `osMemSize` or move `f0`.
2. **G1e higher frame rate (CLOSED as opt-in, s6261: FPS60 holds 301 s lvl1 and 303 s lvl10, 0 crash/0 VI stall; lvl5 hold also clean s6262; owner to judge feel; combo FPS60+dd2 CLEAN on lvl1+lvl5 (s6262 soaks, folded s6263: 302 s, alive_at_end=1, 0 stall, 0 crash lines); widescreen+FPS60 s6263 soaks were HARNESS-VOID (notitle: wide origins != 0x790400; game itself reached width=796/1024 flight, no crash), re-queued s6264 with origin-agnostic recipes, FOLDED s6265: 16:9 and 21:9 lvl1 ~205 s holds clean (alive_at_end=1, 0 stall, 0 crash lines; holds shorter than 300 s) - G1e/G1d combos closed; next G3 in-flight frame diffs; owner page docs/OWNER-OPT-INS.md).** s6255: byte 0x80128EAF 2->1 gives 60 gfx tasks/s in flight (RSP ~10 ms/frame, VI 60/s) and craft path/s is UNCHANGED (dt word 0x8011A904 halves; sim is delta-time) - opt-in `ROGUESQ_FPS60=1` shipped (default retail). Single-source, lvl1 only; still to check: mission timer, AI, particles/anim rate, audio sync, other levels, 300 s holds, hangar/title. Owner judges feel. s6256: whole-rdram rate diff (tools/g1e_rate_diff.py, ROGUESQ_G1E_DUMP) on lvl1+lvl5, 300 s holds clean: mission clocks time-based (ratio 1.00); only ~12 words frame-locked, incl. mission frame counter 0x8013889C (read by NPC curved-path/visibility/anim code) and advanceNpcOnCurvedPath's per-call countdown (static, single-source). s6257: NPC curved-path countdown (rec+0x1C) only gates a bounded re-probe cadence, motion is separate (static read) and no NPC float runs 2x (tools/g1e_float_rate_diff.py, lvl1+lvl5) -> H-negligible, caveat: no direct position control. s6258: lvl10 snap soak clean (303 s, 0 crash/stall); rate diff shows 0 frame-locked words (int arm has no positive control on this run, single-source), float diff only the known dt word 0x8011A8F4 (2.0x) with controls ~1. s6259: audio synth tick is per-VI (musyxSynthFrame), VI stays 60/s -> audio H-clean (static+rate-diff, no direct cue-timing control). s6259 hangar soak clean (mission_t 77 vs 81 s baseline, 0 stall) -> H-menu refuted. Remaining: FPS60 300 s holds lvl1/5/10 (queued s6260_g1e_fps60_l1/l5/l10), then ask owner to judge feel.
3. **G1 level 10/15 note:** both pass (a)+(b) only with `ROGUESQ_FORCE_PLANET_UNLOCK=0xFF` or a
   ~790 s planet-intro wait (SOAK_TIMEOUT >= 900). Forced-hit objective (d) is PARTIAL: counters move
   on lvl1-5,7,8 but no level end was shown driven by them (s5997).
4. **Parked, do not revive without new evidence:** G4 crash hunting (all 19 levels + hangar route
   clean, s5999-s6082); G3 hangar artifacts; M4 accumulator; title plume `si_addr=0x58`.
5. Optional: fresh MIPS source-to-ELF patch qualification; real-input lv0 human play.

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
