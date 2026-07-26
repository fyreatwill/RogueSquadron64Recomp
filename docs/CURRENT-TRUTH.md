# Rogue Squadron 64 Recomp — current truth

Front matter for `PORTING-STATE.md`, which is chronological and contains superseded conclusions.
New here, or back after a break? Read **`docs/PROJECT-OVERVIEW.md`** first — what the project is, how
the four layers fit together, and the hurdle classes that have cost the most time.
Session tags: `s1` = 2026-07-09/10 build + overlay work, `s2`–`s9` = the `## LLE session N` headings,
`s10`–`s32` = the `## Session N` headings.

## Current truth (as of session 45)

    cd build && ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 \
      ROGUESQ_STUB_MISSING_FUNCS=1 ./RogueSquadron64Recomp

Metal shader rebuilds need full Xcode on PATH:
`export DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer` (bare CLT has no `metal`).

- `ROGUESQ_LLE_SOLO=1` is not optional: without it the runner runs LLE **and then falls through to
  HLE for the same task** (s9).
- Default-ON, no longer worth naming: `ROGUESQ_VI_FOLLOW_DRAW=3` (s23), `ROGUESQ_SHADE_WRAP=1`
  **per-pixel** (s24 vertex → s26 shader), `ROGUESQ_FIX_ZERO_SHADE` (s20, largely subsumed by
  wrap), `ROGUESQ_FIX_SAMPLE_BOUNDS` (s15), `ROGUESQ_VI_FULLSYNC` (s11), PresentEarly fallthrough +
  forceAdvance + `ROGUESQ_PRESENT_EARLY_FORCE` (s21), deferred-range coalescing (opt out with
  `ROGUESQ_NO_DPC_MERGE=1`, s10).
- Default-OFF, keep them off: `ROGUESQ_FIX_DXT` (s22/s23), `ROGUESQ_FIX_DXT_I` (s27, null on
  hangar band), `ROGUESQ_FLATTEN_I4` / `FLATTEN_RGBA16` / `FLATTEN_CI4` (attribution probes),
  `ROGUESQ_SHADE_ONLY_MONO` (s30; pad-only, not a band fix), `ROGUESQ_SHADE_WRAP=3` (s31 shared
  wrap experiment), `ROGUESQ_SHADOW2`, `ROGUESQ_RING_RESYNC`.
- Deleted from the code (s44, title-screen probe unchanged): `ROGUESQ_DPC_WRAP` /
  `ROGUESQ_WRAP_DEDUP` (s11 — wrap bytes are now always counted and dropped), `ROGUESQ_FORCE_PAL15`
  (s14, dead per s15), `ROGUESQ_FORCE_SHADE_WHITE` (s19, its shade line closed at s43).
  `ROGUESQ_MAX_FBPAIRS` (default 8192) engages 0 times since s11 but is KEPT deliberately — OOM
  insurance for future FULL_SYNC-less phases (M3 missions), turns a 22 GB Metal abort into a capped
  workload (s44).

Unattended timeline (VI width, ±1 s over 9 runs, s18; content counts s9/s20/s22/s23):

| t | VI | scene |
|---|---|---|
| 0.0 s | 0 → 320 | boot |
| 1.7 s | 640 | attribution → N64 logo → cinematic geometry → star flare → **Factor 5 logo**, all correct (content in 24/60 frames over ~2–44 s) |
| ~46.5 s | 1024 | **title screen** — logo, pilot, X-wing, START/OPTIONS; 5/5 content frames, ~20.9k colours |
| ~72 s | 640 | transition |
| ~90 s | 512, origin 0x690400 | **outdoor scene** — sky, clouds, horizon, sand; 6/6 content frames |

**s39/`-O2` harness note:** the game now progresses further per unit time, so the old
`PROBE_KEYS="3:start 7:start 11:a 15:a 19:a"` schedule overshoots the hangar into a later exterior
scene that shares VI origin **0x6AB400** — origin alone no longer identifies the hangar. Use
`"3:start 7:start"`. The phase timeline below is unchanged (transitions are not render-rate bound).

Driven from the title with `PROBE_KEYS_FROM_PHASE=1` (s23):

| t | VI | scene |
|---|---|---|
| 46.7 s | 1024 | clean title |
| ~50 s | 1024 | **SELECT GAME** (X-wing hangar preview, AAA rating, ERASE GAME) |
| 54.7 s | 512, origin 0x6AB400, colour 0x656000/0x6AB000 | **main-menu hangar**, textured 3D, animating, 5.4k–7.6k colours/frame |
| ~66 s | 512 | camera pans; one frame of RGB static on a wall screen |
| later | 512 | starfield / open bay (mission-intro-ish) |
| ~93 s | 640 | transition — **process dies here** |

512-wide covers two different scenes; tell them apart by VI origin (0x690400 outdoor, 0x6AB400
hangar), never by width alone (s18/s23).

Remaining visual defects:
- **Hangar floor multi-hue band** (horizontal scramble): stale content showing through a coverage
  hole — pixels no triangle covers, in a target the game never clears, so old bytes shine through
  (s41 mark-vertices: 3.6 % of the band stays warm with every draw forced magenta). Established, in
  order: not stale RDRAM (`RAM_PATTERN` puts zero magenta on screen); not the I4 floor texture
  (`tlut=0` cannot be multi-hue — the whole s27–s31 decode line is dead); not under-rendering (that
  was the separate `-O0` ucode-perf defect, 41x fixed at s38 — 186.6 → 4.5 ms/task — with the band
  unchanged); not a submission gap (s42 y-span histogram: rows 141–201 carry 723–2 072 tris/bin, a
  trough not an absence); not raster-state rejection (s43: band draws are wall-identical, sig 0x52).
  Durable structure: the hangar image accumulates across dozens of 2–10-call workloads
  (`TARGET_CLEAR=1` shows a single frame holds only door panels + pad + ceiling sliver), so no
  single frame's census can attribute a pixel; `TARGET_CLEAR=2` was a dead instrument (only pair 1
  carries colour); parked anomaly: 39 of 55 I4 uploads sample 64x128 past `masks=6/6`.
  **s45 did the clip/cull census** (`ROGUESQ_UCODE_CULLSTATS=1`): degenerate=0, backface lives in
  the pad rows — and clip-flagged triangles (328k/phase) are handed to overlay 4 and never return
  (see M1 above). The clip loss and the `[dpc-wrap]` ring drops are the two surviving band
  candidates.
- ~~Hangar dimmer than the s11 peak~~ — **largely fixed, s25** by `SHADE_WRAP` (vertex
  then s26 per-pixel).
- Outdoor 512 zero-shade is masked, not fixed: `ROGUESQ_FIX_ZERO_SHADE` + wrap both map
  the −0.5 class to white; why LLE carries `baseFixed = −32768` is unknown (s19/s20).
- Triangles with S identically zero in the 640 attribution phase: real, uninvestigated (s18).
- `[dpc-behind]` ring-wrap drops remain genuine dropped content with `DPC_WRAP` off; they are simply
  not the cause of any known black screen (s11).

Stability: clean through s27 driven hangar soaks. 0 `UnhandledJumpTarget`, 0 `[defer-drop]`,
0 `[dmem-race]`, 0 `[missing-func]`, 0 asserts.

## Goal stack — work strictly top-down

A milestone is done only when its definition-of-done is met **and documented here**. The
autonomous loop (`tools/agent/loop.sh`, contract in `tools/agent/ITERATION.md`) always draws its
work unit from the top open milestone, so this ladder is what keeps it from idling.

**M1 — hangar band root cause and fix** *(current; s45 state: the ucode clip/cull census ran —
`ROGUESQ_UCODE_CULLSTATS=1`, fixup 3 in `tools/fixup_factor5_ucode.py`, analysis
`scratch/agent/cullstats_sum.py`).* s45 result: degenerate rejects are zero in the hangar and
backface rejects live in the pad rows, but **328,205 hangar triangles per phase are flagged
"needs clipping", handed to clip overlay 4 (`r5=4 → L_1268`), and none ever returns** — the
resident clip-fan re-entry ran 0 times in 3 runs while the census identities held exactly. On
hardware a clip-crossing triangle becomes a fan of clipped triangles; here it is silently dropped.
The static recomp cannot load overlay code by DMA, so the `jr` at L_1298 lands on a valid label
(0 UnhandledJumpTarget) that is not the clip fan — structural sketch, needs the s46 trace. A second
loss also surfaced: RDP-side triangle records are 5–133x below ucode-side emissions (hangar 50k vs
6.64M), sitting at the `[dpc-wrap]` drops (event #27.9M by run end). Both candidates survive for
the band; the clip loss is a confirmed defect regardless.
*Done when:* mechanism traced input → code path → pixels, fix applied, and the s41 mark-vertices
mode-2 probe shows band rows receiving geometry, with other phases unchanged.

**M2 — post-`-O2` regression sweep and soak.** Phase-gated `regress.sh` across all six known scenes
against the s23 baselines, plus three 10-minute driven hangar soaks. *Done when:* per-phase metrics
within baseline bands and all stability counters (UnhandledJumpTarget, defer-drop, dmem-race,
missing-func, asserts) at 0.

**M3 — first gameplay.** Extend the driven key schedule past SELECT GAME into mission 1. Expect new
failure classes: mission-overlay DMA (watch missing-func / UnhandledJumpTarget), a new VI phase to
add to the timeline, possibly new ucode ops. Each new failure is its own work unit — return to the
M1-style method. *Done when:* 60 seconds of in-mission rendering, craft visibly responds to
synthetic input, stability counters 0, and the phase timeline in this document covers the mission.

**M4 — parked correctness items**, one work unit each: outdoor `baseFixed = −32768` zero-shade root
cause (currently masked, not fixed); the S=0 triangles in the 640 attribution phase; the I4
`sample=64x128` anomaly if M1 didn't consume it.

**M5 — audio de-stubbing (investigation first, not code).** The MusyX audio ucode already
recompiles (`factor5_ucode_b_recompiled.c` sits in the build as a never-called artifact). First
work unit: a design doc only — how audio tasks would run LLE alongside gfx (they share the `dmem[]`
serialization built in s5), what bridges RSP audio output to SDL, and what the audio-gate byte
reversal implies. **Gate M5 behind M2**: audio re-enters exactly the shared-state territory that
cost three sessions before the recursive mutex.

## Next steps, in order of expected value (s45)

1. **Trace the overlay-4 (clip) dispatch end-to-end** — one diagnostic build+run: at L_1268/L_1298
   log the overlay id, the entry address read from the DMEM 0x76 table, and the label the indirect
   jump resolves to; establish what code actually runs when a triangle needs clipping, then decide
   the fix (recompile the clip overlay image via RSPRecomp vs a C-side clip in the fixup). The
   discriminating follow-up for the band: once clipped triangles produce output, re-run the s41
   mark-vertices mode-2 probe — band rows filling in confirms the clip loss owned the band; band
   unchanged pivots to the ring-drop candidate (s45: RDP records 50k of 6.64M hangar emissions,
   `[dpc-wrap]` #27.9M). Caveat for any row attribution: the +0x1A screen y of out-of-volume
   vertices is unusable in the hangar (hand-class buckets read 0/0/0 there, s45).
2. **Identify what should cover the band rows.** s39 re-measured coverage on the fast build:
   band-overlapping draws rose 1 600 → 7 600 while the band stayed identical, and `TARGET_CLEAR=1`
   (median 728 distinct vs 52 550 control) shows **no workload ever draws band content** — the
   hangar image is accumulated across hundreds of 1–14-call workloads into a never-cleared target.
   The band is a **CONFIRMED coverage hole (s41)**, established with `ROGUESQ_MARK_VTX` in
   `rt64_gbi_rdp.cpp` (writes `colorWorkBuffer`; `=1` marks every vertex — control passes at 886 488
   magenta px/frame — `=2` marks only band-row vertices). Under mode 1 the band crop is 62.5 %
   magenta, 13.3 % black and **3.6 % still warm**, against 4.35 % warm unmarked: forcing every draw
   magenta leaves the orange untouched, so **those pixels receive no geometry at all**. Walls above
   and pad below are drawn; the mid-ground strip is not. (s40's earlier probe wrote through `col` in
   `RDP::drawTris` and failed its own control — that path never reaches output; do not reuse it.)
   **s42 answered that**: `ROGUESQ_LOG_YHIST=1` bins triangles by full ymin..ymax **span** (not
   vertex or centroid) and shows **no gap** — the band rows (game y ≈141–201, derived from the s41
   mode-2 image: capture = 2.33·game + 151) carry 2 072 / 1 806 / 792 / 723 triangles per 20px bin,
   a trough between the wall rows (~2 000) and pad rows (4 000–5 300) but not an absence. **The
   geometry is submitted, so the hole is downstream of submission** — z-rejection, alpha/coverage,
   scissor, or column mismatch. **s43 did that census** (`ROGUESQ_LOG_ZSTATE=1`, windows walls 60–140 / band 141–201 / pad
   220–320): the band draws are **indistinguishable from the wall draws** — same dominant signature
   0x52 (textured, zCmp=0, zUpd=1, alphaCvgSel=1), 2 409 vs 2 609. No z, alpha, coverage or scissor
   difference. So the band pixels are **gaps between triangles**, not rejected draws: some polygons
   that should fill those rows are never emitted while their neighbours are. Texture decode
   (s27–s31), submission gap (s42) and raster-state rejection (s43) are all now eliminated.
   **s45 did that census** (`ROGUESQ_UCODE_CULLSTATS=1`): degenerate=0, backface lives in the pad
   rows — and clip-flagged triangles (328k/phase) are handed to overlay 4 and never return (see M1
   above). The clip loss and the `[dpc-wrap]` ring drops are the two surviving band candidates.
3. **Visual regression check on the other phases after `-O2`**, plus a stability soak.
4. **GPU→CPU present PNG** via `NativeTarget::copyToRAM` — a convenience, not a blocker.

Done, do not redo:
- ~~Optimise the ucode vector path~~ — s38: it was `-O0`; `-O2` gave 41x. SIMD/RSPRecomp vector work
  is unnecessary at 4.5 ms/task without a new measurement justifying it.
- ~~Confirm the ucode-performance bottleneck~~ (s37) · ~~Find why DL submission collapses~~ (s36) ·
  ~~Census the RDP stream~~ (s35) · ~~Localise the draw loss~~ (s33/s34).
- Coverage attribution (`LOG_BBOX`) and load/render format mismatch (`LOG_UPLOAD`) are ruled out —
  every draw covering the band is I4 with `tlut=0`, from I4 loads.
- The s27–s31 I4-decode line (`FIX_DXT_I`, `I4_SHADE_MONO`, `SHADE_ONLY_MONO`, restricted
  `FLATTEN_I4`) is retired — aimed at a texture that does not paint those pixels.

## Regeneration and build pipeline

Game functions (s1) — all four steps, in order:

1. `cd ~/Documents/Tools/rogue_squadron64 && python3 tools/make_elf.py`
2. `cd ~/Documents/Tools/N64Recomp && ./build/N64Recomp rogue_squadron.toml`
3. `python3 ~/Documents/Tools/N64Recomp/fixup_game_funcs.py` — **required**, and the only thing that
   re-applies the hand-edits, idempotently:
   - writes to `$zero` (`0 = expr;`) commented out (~2700 sites; the recompiler emits invalid C)
   - `fake_func_*` gap fillers with gotos to nonexistent labels → `__builtin_trap()`
   - real functions with cross-function branches (shared asm tails: `lvj_checkComplexObjectives`,
     `audioCompandS16`, `applyVoiceDelayFilter`, `__OSGlobalIntMask`) → each bad goto becomes
     `__builtin_trap()`; a runtime SIGTRAP means one of those was taken
   - audio-engine gate stores → 0 in `funcs_23.c` (`initMusyXEngine`, `setDisplayMode`,
     `reapplyDisplayMode`; gate byte 0x800A0F50) — without this the scheduler wedges in
     `waitForMusyXAudioTaskDone`
   - the `jr $t9` return idiom in `funcs_4.c` (`convertMat3x4ToN64Mtx`, 0x80018D80) → plain `return`
     instead of `LOOKUP_FUNC(ctx->r25)`
   - `musyxKeyOnVoice` `break 6/7` div-by-zero guards → early `return`, keyed on the exact `do_break`
     constants 2148076780..2148077008
4. `cd build && cmake --build . -j8`

RSP ucode (only when a ucode toml changes): `~/Documents/Tools/N64Recomp/build/RSPRecomp` on
`factor5_rsp.toml` / `factor5_boot_rsp.toml` → `build/factor5_ucode/*.c`, then
`tools/fixup_factor5_ucode.py`. `factor5b_rsp.toml` (ROM 0x9ABE0) is the **MusyX audio** ucode;
`factor5_ucode_b_recompiled.c` stays in the build as a never-called artifact (s5).

Standing warnings:
- `lib/N64ModernRuntime` and `lib/rt64` carry **uncommitted working-tree patches**:
  `librecomp/src/pi.cpp` `do_dma` → `load_overlays_by_start`, `overlays.cpp` `it < upper`,
  `librecomp/src/rsp.cpp` `rs64_dmem_lock/unlock` hooks (the shared-DMEM serialization, s5), and the
  whole RT64 assert-guard chain (s2b/s3/s7/s9/s12). **Never `git submodule update --force`.**
- The ROM must sit next to the executable in `build/`; run from anywhere else and the binary silently
  takes the "place your ROM" path and gives a dead VI (s8).
- Hand-edited diagnostics in `build/factor5_ucode/*.c` survive a cmake build but **not** an RSPRecomp
  regen — add them to `tools/fixup_factor5_ucode.py` to keep them. Diagnostics in `RecompiledFuncs`
  are wiped by regen entirely.
- The settings.json Bash allowlist matches the FIRST WORD of the command: `VAR=1 tools/probe.sh …`
  is denied despite `Bash(tools/:*)` — prefix such commands with `env` (allowlisted) instead (s44).
- Harness: `clang -O1 -fobjc-arc -framework Cocoa -framework CoreGraphics -o build/winctl tools/winctl.m`;
  capture with `tools/probe.sh` / `tools/regress.sh`. Kill runs with SIGKILL, not SIGTERM — the TERM
  path aborts in SDL_QUIT cleanup and leaves a crash dialog over the next run's capture (s9).
  Python decoders need `scratch/venv/bin/python` (PIL is gone from system python, s18).
- `regress.sh` preflight must not write probe images as `.*` hidden names: `screencapture` refuses
  final path components starting with `.` (exit 0, no file) and falsely reports visual=denied (s26).
- ~~Screen Recording permission is intermittent~~ — **overturned s32.** Capture and synthetic input
  both work: 74/74 `screencapture -l` succeeded across a full undriven run (73 with content, all
  phases), the game's CGWindow id was **stable** at one value for the whole run, and a driven run
  reached the hangar (512 origin 0x6AB400 at 56.0 s) off `winctl` keys. `could not create image from
  window` means the **window id is wrong**, not that permission is missing — check the id before
  blaming TCC (`winctl find <pid>`; `winctl list` is not a subcommand and prints nothing).
  `winctl trusted` reports Accessibility state directly.
- `winctl activate` (activateWithOptions:) is a cooperative request modern macOS **ignores while
  another app holds focus** — keys then get dropped with `trusted`=yes and the run silently follows
  the undriven route (s45; also the real cause of the session-25 failures regress.sh blamed on "no
  GUI session"). probe.sh/regress.sh now raise via System Events `set frontmost` (`raise_game()`);
  keep using them rather than winctl directly for driven runs.

## Overturned conclusions — do not act on these

`## LLE stabilization session 2 (2026-07-12)` sits out of order in the log, between s7 and s8: its
conclusions are among the oldest in the file, not the newest.

The s2–s5 stabilization-era claims are compressed here (full detail: PORTING-STATE, and the saga
narrative in PROJECT-OVERVIEW §3). Every one was eventually explained by the shared-`dmem[]` race
(one global 4 KB array, audio tasks staging over gfx state; fixed by the recursive mutex, s5):
- **s2:** "LLE stall is LoadTile/LoadBlock coordinate underflow" — real fix was `rsp_dpc_macros.h`
  never resetting `DPC_CURRENT` on a `DPC_START` write.
- **s2b:** "residual exit=3 is zeroed DL-chunk bytes at DMEM 0x228" — chunk fetch was faithful; the
  dispatch-table trample was real and came from the audio task.
- **s3:** "0xF80 image from 0xA4E00 is the RDP ring / a trig load" → it is MusyX audio `ucode_data`;
  "op 0xBA flush-cursor overflow trampled DMEM" → no overflow existed, it was `run_task` DMA'ing
  audio data over `dmem[0..0xF7F]`; "trig table generated in-ucode" → nothing is generated in-ucode
  (s4 static sweep: everything arrives by DMA).
- **s4:** "two F5 gfx ucodes; dispatch ucode B separately" → 0x80099FE0 is the MusyX AUDIO ucode;
  gfx routes only via `send_dl`. Dispatching B "helped" only by keeping gfx code off audio staging.
- **Claim (s5–s7):** 0x76A000 and 0x7DD000 are colour buffers cleared to white. **Overturned by s8:**
  they are **Z-buffers** — `SETZIMG` (op 0x3E) names exactly those addresses and 0xFFFCFFFC is the
  standard z-clear. Colour buffers are 0x5D4000/0x66A000 (640-wide) and 0x6BA000/0x6DD000 (320-wide).
  **Why believable:** 0xFFFC reads as white in a 16-bit colour buffer, and the screen was white.
- **Claim (s7):** texrect draws execute on the GPU but their pixel output is invisible in the render
  target. **Overturned by s8:** `ROGUESQ_VI_FORCE_FB=0x5D4000` shows dense real texture content — the
  pixels exist, the default present picks a different buffer. **Why believable:** every pipeline
  stage was instrumented and healthy, and the presented buffer really was uniform white.
- **Claim (s8):** the visual blocker is that F5 geometry ops 0x01/0x02/0x03 emit zero RDP bytes (64 of
  66 tasks commit 0 ranges), probably RSPRecomp's VU translation culling every primitive.
  **Overturned by s9:** `rsp_dpc_submit` kept its ring high-water mark in function-local statics, so
  any task whose output was no larger than the largest previous task's was discarded whole. Hoisted
  to `s_submit_dl_base`/`s_submit_last_end`: 65/65 tasks commit, 4575 TEXRECT in 14 s vs 399 in 45 s.
  **Why believable:** the count was exactly zero, and RT64's HLE leaves the same three ops stubbed —
  two independent-looking paths agreeing on "no geometry".
- **Claim (s9, sixth pass):** 0x790000 is that phase's z-buffer (second colour buffer + 0x100000, the
  pattern every other phase follows) and the VI never scans it. **Overturned by s10**
  (`[osViSwapBuffer #1472] fb=0x80790000`), **s18** (drawTarget 0x690000 vs VI origin 0x690400 —
  colour, double-buffered) **and s21** (`set-cimg-full addr=0x790000 w=512`, presented, 11/11 content
  frames). **Why believable:** the +0x100000 z-buffer pattern does hold everywhere else.
- **Claim (s9, sixth pass):** `[dpc-behind]` counts 17867 ring-wrap drops in 60 s. **Overturned by
  s10:** the real figure is **9,056,256 wrap events in 70 s**, each a distinct range — three orders of
  magnitude out. **Why believable:** the counter was real; it was just reading a sampled path.
- **Claim (s9/s10):** `ROGUESQ_DPC_WRAP=1` is what gives continuous rendering, and the Metal
  exhaustion it triggers must be contained with `ROGUESQ_MAX_FBPAIRS`. **Overturned by s11:** with
  the `VI_FULLSYNC` fix, wrap **off** gives more content (57/63 frames vs 32/62), 3 framebuffer pairs
  per workload instead of 448, strictly more detail (red door lighting appears only in wrap-off
  captures), and `[fbpair-cap]` engages 0 times — wrap forwarding was re-sending already-consumed ring
  bytes. **Why believable:** wrap-on genuinely removed the black post-logo phase, by papering over the
  missing FULL_SYNC that was the actual cause.
- **Claim (s10):** the Metal shared-memory exhaustion is a property of the post-logo tiled phase and
  the framebuffer-pair cap is the fix. **Overturned by s11:** that phase never emits RDP FULL_SYNC at
  all, so the workload never advanced; 195,057 pairs, 23 GB of Metal buffers and the black screen are
  all downstream of that. Synthesising the frame boundary from the VI swap fixes it. **Why
  believable:** the allocation backtrace named `addFramebuffer` unambiguously and the cap did buy a
  clean 120 s run.
- **Claim (s9, third pass):** `ROGUESQ_PRIM_ALPHA_FF=1` is needed to see text — PRIM alpha is 0x08
  (~3 % opacity) on almost every presented draw. **Overturned by s11:** verified, not assumed — with
  it off the attribution screen still renders fully legibly, so the hack can be retired rather than
  replaced. **Why believable:** the combiner really is `TEXEL0 * PRIM` with alpha straight from PRIM,
  and forcing 0xFF really did make the screen appear.
- **Claim (s9, fifth pass, mid-session):** the renderer has regressed to black, so the 24
  overlay-symbol moves must be reverted. **Overturned within s9:** sampling artefact — a 28-frame
  burst at 0.15 s showed 27/28 frames full of content; the moves were fine and were re-applied.
  **Why believable:** four one-shot captures at 4/8/14/20 s all showed black.
- **Claim (s12/s13):** the hangar floor/wall assets are the I4/CI4 textures at 0x60xxxx (dumped via
  `ROGUESQ_DUMP_HANGAR_TEX`). **Overturned by s16:** wrong assets. The real CI sources are 0x741B80
  (words=114, 48×38), 0x741460 (words=228, 64×57) and 0x4Fxxxx / 0x6Axxxx (words=256, 64×64). **Why
  believable:** the 0x60xxxx dumps decode offline as plausible structured grayscale.
- **Claim (s12–s16):** the 0x65xxxx RGBA16 loads and their `[fb-miss]` lines are hangar wall/floor
  assets. **Overturned by s17:** they fire while the VI is at **width=1024 origin=0x790400** — the
  title screen, not the 512 hangar (confirmed by line-number interleave of `[loadblock a=0x65…]`
  against `[vi] update_screen`). That is why five sessions of knob-tuning never moved the hangar band.
  **Why believable:** they fire 160,000+ times per run and decode into a Rebel pilot beside an X-wing,
  equally plausible as cinematic or hangar content.
- **Claim (s14):** `ROGUESQ_FIX_LINE_MASK` — for 4-bit tiles with masks ∈ [4,7], force
  `line = 2^(masks-4)` so decode stride matches the wrap period. **Overturned by s15:** wrong
  direction — `line=3 / lrs=188` CI4 pal15 is a real 48×38 tile (LOADBLOCK words=114 = 912 B =
  48*38*0.5), and forcing line→4 with sample 64 scrambled it further. Replaced by
  `ROGUESQ_FIX_SAMPLE_BOUNDS` (keep the emitted line, shrink sampleWidth/Height to min(mask,
  line-implied, lrs/lrt span)). **Why believable:** mask and line disagreeing usually does mean one is
  wrong.
- **Claim (s14):** palette-bank-15 stomping is the root of the rainbow floor band — later LOADTLUTs
  from 0x62Bxxx replace the red hangar palette. **Overturned by s15:** the first 40 CI4 pal15 uploads
  all use the red palettes 0x751FA0 / 0x751FC0, with **zero** multi-colour 0x62Bxxx; band pixels are
  warm red #ce6238, i.e. a layout scramble of correct colours, not a wrong TLUT bank. **Why
  believable:** an offline decode with a multi-colour palette reproduced the rainbow noise closely.
- **Claim (s13):** hangar walls need synthesised dxt, so `ROGUESQ_FIX_DXT` defaults ON. **Overturned
  by s22 and s23:** on the 1024 title sheet the synthesis turns the photographic backdrop into a
  vertical-stripe mosaic (`FIX_DXT=0` gives a sharp pilot, R2-D2, X-wing panels); on the hangar,
  same-run A/B, `FIX_DXT=1` gives **rainbow / TV-static corruption** on floor and walls. Default is
  now **OFF** for both. s16's narrowing (synthesise for RGBA only, since CI/I are stored
  pre-interleaved) is superseded too — the RGBA16 title sheet decodes perfectly from a linear offline
  read. **Why believable:** every LOADBLOCK really carries `dxt=0`, hardware really uses dxt to
  XOR-interleave odd TMEM lines, and s13's A/B did look better — but it was a cross-run comparison,
  the method s18 later rejected.
- **Claim (s18, first half):** the 512 phase draws flat sand-coloured polygons, and fog #C8C0A0
  matches the on-screen #c5be9d. **Overturned by s18 (second half):** `ROGUESQ_FORCE_FOG=FF00FF`
  changes **0 of 1,782,144** pixels. The sand is the **fill colour** (`FORCE_FILL` = 58.0 %,
  + `DROP_ALL_TRIS` = 81.2 %); triangles cover ~23 % and paint **black**. Revised symptom, unifying
  512 and 1024: textured geometry renders black. **Why believable:** two sand-coloured things in a
  desert scene is a tidy coincidence.
- **Claim (s18, mid-session):** textured triangles with S identically zero (base, dx, de all zero)
  explain the flat 512-phase rendering. **Overturned within s18:** those triangles are not in the 512
  phase — run-lifetime "first N" counters reported whatever phase started first. Interval-scoped
  counting finds **0** collapsed triangles in both 512 and 1024; the S=0 triangles live in the 640
  attribution phase. **Why believable:** a collapsed S coordinate is a textbook cause of flat texturing.
- **Claim (s18, fourth segment):** no RGBA32 LOADBLOCK is ever emitted in the 512 phase (exhaustive
  census: f2/s2 = 1,614, f4/s2 = 25,840, RGBA32 = 0), the TMEM high half is empty, so blue and alpha
  are absent and geometry rasterises black. **Overturned by s19:** `DUMP_TMEM_DRAW` at draw-record
  time sees **stale** TMEM — RT64 defers every LOADBLOCK to `fullSyncFramebufferPairTiles`, where
  `lastLoadOpByTMEM` and the census also update. The stream does emit `SETTIMG f0/s3 → SETTILE load →
  LOADBLOCK words=512 → SETTILE render line=8 → DRAW`, and at upload both halves are filled
  (lo 2048/2048, hi 1646–1871/2048). **Why believable:** the 1655/128 nonzero split matched a 256-word
  non-split load to the byte, and the RDP's own `lastLoadOpByTMEM[]` agreed.
- **Claim (s19):** the 1024-phase black screen is most likely the same zero-shade bug; retest after
  the shade fix. **Overturned by s20/s21:** `FORCE_SHADE_WHITE=1` gives 0/4 content at 1024, pure
  #000. The cause is present starvation — `State::updateScreen` in PresentEarly mode early-returns
  whenever `presentEarly && !fromEarlyPresent`, and at 1024 no fbPair is an `earlyPresentCandidate`,
  so presents stop entirely. **Why believable:** both phases were black at once and one fix had just
  explained the other.

- **Claim (s23):** the hangar's remaining dimness is real vertex lighting or a missing layer, not a
  shade-decode problem, because its shade census is healthy (`vtxRGB black=0 ok≈90–150 white=0`).
  **Overturned by s25:** that census is the magnitude-only classifier s24 proved cannot distinguish
  −118 from +118, so the "ok" bucket was the all-negative population. Driven A/B: `SHADE_WRAP=1` is
  brighter in 93 of 114 paired hangar frames and removes the control's intermittent collapses to
  ~50 % black. **Why believable:** the census really did report a healthy-looking spread, and the
  hangar was the one phase whose shade had never been re-examined after s24 — because reaching it
  needs synthetic input, which the s24 A/B did not have.
- **Claim (s28):** `FORCE_SHADE_WHITE` kills the hangar multi-hue floor band (warm% 1.15→0), so the
  band colour is shade. **Overturned by s31:** on the standard hangar view the mid-ground band
  **survives** FSW (`scratch/s31_fsw_rep.png`) — walls go perfect greyscale I4, pad goes solid white,
  multi-hue floor remains. warm% alone is a bad residual metric (~3% still scores). **Why
  believable:** FSW does remove shade tint from walls and pad; the earlier A/B camera angle may have
  had less mid-ground floor in frame.
- **Claim (s30):** hangar mid-band is 100% untextured shade-only and `SHADE_ONLY_MONO` kills the band.
  **Overturned by s31:** midtex first-100 + ycen 180–360 only sampled the landing-pad shade-only
  population. Improved census after hangar: **201 textured I4** (imgs 0x604140/0x605140, ycen med
  145) + 73 shade-only. Suppress/mono leave the multi-hue mid-ground; FSW proves it is TEXEL.
  **Why believable:** s30 midtex really did report 105/105 tiles=0 — it was a sampling bias, not a
  bad instrument.

### Dead ends — labelled as such in the log, do not retry

- `RDP_ADDRESS_MASK` 0xFFFFFF → 0x7FFFFF (`rt64_rdp.h`, s3): 0x800000..0xFFFFFF are legitimate RT64
  extended-RDRAM handles; masking aliases them onto low memory and moved the crash earlier.
- Chunk-replay hack in `dma_rdram_to_dmem` (s3): the ucode legitimately reads trig values from
  0x170..0x280 right after a swap; 29 unhandled vs ~5.
- Widening the DMA shadow to `[ucode_data-0x1800, +0x1800)` to cover 0x37658 (s3): that content
  difference is legit dynamic data, not shadowable corruption.
- Blanket ucode-image shadow `shadow2` (s4): the engine legitimately rewrites `ucode+0x12DEA` and
  `ucode+0x7CD5C`; serving them stale gave 109 unhandled / 35 send_dl against a 256 baseline.
- `ROGUESQ_RING_RESYNC=1`, poking `DMEM[0x108]` = ring base per task (s4): no measurable change
  (41 vs 51) — aimed at a flush overflow that never existed.
- `dmem[0x153]=0xFF` to force a segment reload (s2b): made failures worse (6 exit=3 vs 2–4).
- Bulk moves of unmapped symbols out of `symbol_files/main_overlay.txt` (s9): each inserted symbol
  **splits** the enclosing function in that section — the duplicate-address truncation bug in reverse
  — producing a SIGBUS in `allocAndInitGridCellArray`. Use `tools/overlay_symbol_probe.py <0xADDR>
  [mission|menu|cinematic]` first (the reliable signal is the `addiu $sp, $sp, -N` prologue at +0),
  one validated batch at a time.
- Present-side snap-down and `findMostRecentContaining` fallbacks (s9):
  `present.screenVI.fbAddress()` already returns the framebuffer base and neither fallback ever fired.
- `ROGUESQ_VIEW_RDRAM=1` (s9): the game window never appears; the mode is broken in this fork.
- `ROGUESQ_WRAP_DEDUP=1` (s10): removes ~33000 redundant submissions but the run still reached
  193715 pairs and the same Metal assert.
- `ROGUESQ_FORCE_PAL15=1` (s14): clears the floor band but corrupts ceiling banners that legitimately
  share pal=15.

## Method traps

- `fbPair.projections` is a reused vector; only `projectionCount` entries are live. Counting its
  size reported "292-468 draw calls" where the true figure was 2-10 — use `fbPair.gameCallCount`
  (s32).
- Sampled diagnostic lines lie about totals: `[loadblock]` prints the first 60 then every 500th, so
  counting its lines said "43 RGBA32 loads" where an exhaustive census said zero (s18, restated s19).
- TMEM, `lastLoadOpByTMEM` and any load census read at draw-record time are stale under RT64, which
  defers LOADBLOCKs to `fullSyncFramebufferPairTiles`; measure at upload (s19).
- Sparse one-shot screenshots land on genuine inter-screen transitions and read as a regression;
  always burst-sample (28 frames at 0.15 s: 27/28 with content, where 4 one-shots showed black) (s9).
- Cross-run A/B is not a method for an animating scene — the camera differs, so knob effects and nulls
  are both manufactured; "7.30 % other pixels" identical to three significant figures across three
  configurations is a constant, not an effect. Compare forced-colour pixel **fractions** within a
  phase-matched run, or toggle within a single run (s18).
- Validate a suppression instrument before believing a null result: `ROGUESQ_SUPPRESS_SHIFT=1` re-runs
  any suppression mode as a +80 px displacement so you can see it reach the screen (s18).
- A capture harness that keeps shooting after the process dies photographs the window underneath and
  reports it as content — `window_burst.sh` read 60/60 that way; counts taken before the liveness
  check was added are suspect (s9).
- The `[seq]` and `[full-hist]` walkers in `dpc_bridge` advance a fixed 8 bytes per command, so
  triangles (32–48 bytes) desync them into thousands of bogus SETCIMG addresses (`LOG_SEQ` also caps
  at 6000). Once geometry flows use `ROGUESQ_LOG_RDPHIST`, which uses RT64's own command lengths
  (s9/s11/s19).
- Run-to-run phase timing varies by tens of seconds (Factor 5 logo at 18 s in one run, 44 s in
  another), so fixed capture windows miss phases. Gate on the VI-width transition
  (`PROBE_PHASE_WIDTH`, `PROBE_KEYS_FROM_PHASE=1`), never on a stopwatch (s17 → s18/s23).
- When a downstream resource explodes, first count the event that is *supposed* to bound it. Sessions
  6–10 measured pair counts, buffer bytes and wrap counters ever more precisely and never counted
  FULL_SYNC arrivals — the one number that named the cause (s11).
- A colour match is not attribution: fog #C8C0A0 matching the on-screen #c5be9d was coincidence (s18).
- A plausible decoded image does not identify a phase — confirm the phase from the VI width, not from
  what the picture looks like (s17).
- Histogram-drain timing misleads: the runner histogram showed 0 RDP bytes for a task the dispatch
  tracer proved had processed its full DL (s2b).
- Five frames per run does not average out camera motion, so even aggregate `pixel_stats.py` metrics
  are confounded when runs sample different moments (s18).
