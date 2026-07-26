# Rogue Squadron 64 Recomp — current truth

Front matter for `PORTING-STATE.md`, which is chronological and contains superseded conclusions.
New here, or back after a break? Read **`docs/PROJECT-OVERVIEW.md`** first — what the project is, how
the four layers fit together, and the hurdle classes that have cost the most time.
Session tags: `s1` = 2026-07-09/10 build + overlay work, `s2`–`s9` = the `## LLE session N` headings,
`s10`–`s32` = the `## Session N` headings.

## Current truth (as of session 52)

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
  wrap experiment), `ROGUESQ_SHADOW2`, `ROGUESQ_RING_RESYNC`. Diagnostics: `ROGUESQ_DUMP_IMEM_DMA=1`
  (s47, lib-side) dumps every skipped IMEM DMA to `build/imem_dma_dump.bin`
  (`scratch/s47_parse_imemdump.py` decodes).
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

Driven from the title with `PROBE_KEYS_FROM_PHASE=1` (s23, scene names corrected s48):

| t | VI | scene |
|---|---|---|
| 46.7 s | 1024 | clean title |
| ~50 s | 1024 | **SELECT GAME** (photographic hangar backdrop, AAA save, ERASE GAME) — waits for input indefinitely |
| +1 press | 512, origin 0x6AB400, colour 0x656000/0x6AB000 | **level-select war room → SELECT LEVEL — "AMBUSH AT MOS EISLEY"** with X-wing hologram (the scene s12–s47 called the "main-menu hangar"; see s48 below) |
| ~93 s | 640 | transition — **process dies here** (undriven-era observation) |

Menu state machine (s48, three driven runs; extended s50): title —start→ SELECT GAME —start→ war
room / SELECT LEVEL —start→ **AVAILABLE CRAFT** (craft-select screen: X-wing hologram, "PRIMARY
WEAPON: BLASTERS" / "DEFENSE: SHIELD", two alternate-craft thumbnails; footer keeps "AMBUSH AT MOS
EISLEY / PRESS [A] FOR LEVEL DESCRIPTION"). Renders correctly, stable for 20s observed (s50). The
LEVEL DESCRIPTION prompt (`a` from AVAILABLE CRAFT) does **not** show a description card — see the
black-screen/crash entry below; mission launch itself is still untested.

**s48 scene-identity correction:** there is no "main-menu hangar". The 512-wide origin-0x6AB400
scene is the round **level-select war room**. Pre-clip-fix it rendered with every clip-needing
triangle dropped (camera inside a curved room), so the tiered console rings and holotable were
missing: the central platform read as a "landing pad", the Mos Eisley preview hologram as a parked
X-wing, and the stale-RDRAM band filled the rows the rings should cover. Post-fix the room renders
complete. VI origin **cannot** discriminate menu scenes (the war room presents from the same
0x6AB400); identify menu scenes visually from captures.

512-wide covers two different scenes; tell them apart by VI origin (0x690400 outdoor, 0x6AB400
war room) — but see s48: origin distinguishes *phases*, not which menu scene is on screen.

Remaining visual defects:
- **Confirmed on 2 independent runs (s50, s51): AVAILABLE CRAFT → LEVEL DESCRIPTION black screen +
  silent process death.** Pressing `a` on the AVAILABLE CRAFT screen (footer: "PRESS [A] FOR LEVEL
  DESCRIPTION") goes solid black within 2.4s and the process is gone (`kill -0` fails) ~9-10s after
  the press, with **zero** `missing-func`/`UnhandledJumpTarget`/`dmem-race`/`assert` lines anywhere
  in the log. s51 established event ordering: the RDP `fs` (full-sync) counter freezes **before**
  the correlated `fmt=7` copy-mode-draw warning appears (line 16730 vs 16764 in that run's log),
  which weakens the theory that the native-copy no-op (`NativeTarget::copyFromRAM`/`copyToNative`,
  `lib/rt64/src/render/rt64_native_target.cpp:65,84,264`) causes the freeze — it is more likely a
  downstream symptom. A static read of that guard (s51) found it pre-existing, deliberately
  designed for exactly this input (any `siz==4b` copy, not specifically `fmt=7`), and its `nullptr`
  result is null-checked by every caller found — no obvious crash risk on that exact path. The `fs`
  freeze itself (not yet traced to which DL task fails to reach FULL_SYNC) is now the leading
  hypothesis. **s51 also found a generalizable environment confound**: driven runs on this box can
  silently stall in phase-advance (`fs` frozen, `[fbpair-cap]` hit) under concurrent system load —
  check `uptime`/concurrent-`claude`-process-count before trusting a `PROBE_PHASE_TIMEOUT` expiry
  as a game-code finding. 3 backtrace attempts (2× lldb, 1× `sample`) this session were consumed by
  that confound rather than yielding a trace; budget rule says stop and pick a different method
  next (an in-process crash handler needing no external attach, once load is controlled for). Full
  detail: PORTING-STATE s50, s51.
- ~~Hangar floor multi-hue band~~ — **FIXED and root-caused, s45–s48 (M1 closed).** The band was
  stale RDRAM showing through the hole left by the war room's clip-flagged geometry: all clip
  dispatches to overlay 4 ran the wrong code (window-swap IMEM DMA skipped), so the tiered
  console rings / holotable never drew. s47 spliced the real clip overlay in; s48 verified in the
  scene itself: mode-2 mark-vertices shows band rows rasterizing geometry (band-crop magenta
  15–22 % vs ~11 % pre-fix edge-only), a clean run shows zero streak band with the rings rendered,
  fanjal 5.6–5.8k per 512-phase with census identities exact, and `[dpc-wrap]` reproducibly
  halved (17.06M → 9.91M). Parked anomaly still open (M4): 39 of 55 I4 uploads sample 64x128 past
  `masks=6/6`. Overlays 12/44 still take the old broken dispatch path by design — same splice
  recipe applies if a phase ever needs them.
- ~~Hangar dimmer than the s11 peak~~ — **largely fixed, s25** by `SHADE_WRAP` (vertex
  then s26 per-pixel).
- Outdoor 512 zero-shade is masked, not fixed: `ROGUESQ_FIX_ZERO_SHADE` + wrap both map
  the −0.5 class to white; why LLE carries `baseFixed = −32768` is unknown (s19/s20).
- Triangles with S identically zero in the 640 attribution phase: real, uninvestigated (s18).
- `[dpc-behind]` ring-wrap drops remain genuine dropped content with `DPC_WRAP` off; they are simply
  not the cause of any known black screen (s11).

Stability: clean through s27 driven hangar soaks and s49's post-clip-fix regression sweep
(undriven full timeline + driven war room). 0 `UnhandledJumpTarget`, 0 `[defer-drop]`,
0 `[dmem-race]`, 0 asserts. `[missing-func]` clean in every soaked phase to date, **except**: s49's
undriven outdoor-512 stretch stubbed 3 distinct addresses once each (0x800C7120, 0x800FBD48,
0x800FB190) with 0 aborts — never itemized before because prior soaks targeted hangar/war-room, not
outdoor. Parked as an M4 curiosity, not a blocker. **s50, new menu territory only:** AVAILABLE
CRAFT's LEVEL DESCRIPTION prompt kills the process with **none** of these four counters firing —
see "Remaining visual defects" above. Single-run, not yet reproduced; does not touch the s27–s49
stability record for hangar/war-room/outdoor, which stands unchanged.

## Goal stack — work strictly top-down

A milestone is done only when its definition-of-done is met **and documented here**. The
autonomous loop (`tools/agent/loop.sh`, contract in `tools/agent/ITERATION.md`) always draws its
work unit from the top open milestone, so this ladder is what keeps it from idling.

**M1 — hangar band root cause and fix: DONE (s48).** Mechanism (s45/s46): all overlay dispatches
share entry **0x1DB0** and the window-swap IMEM DMA is skipped, so clip dispatches ran the packed
overlay-image *storage* instead of clip code — every clip-flagged triangle vanished. s47 spliced
the real clip overlay (raw in ROM at `RDRAM_addr + 0xC00`; `tools/make_clip_composite.py` +
`factor5_rsp_ovl4.toml` + fixup 6, routed by `DMEM 0x153 == 4`). s48 closed the definition-of-done
in the scene itself: band rows rasterize geometry (mode-2 marker), clean captures show the war
room complete with zero streak band, census identities exact across 672+696 tasks, all stability
counters 0. Full detail: PORTING-STATE s45–s48. Overlays 12/44 still take the old broken path by
design — same splice recipe applies if they ever matter.

**M2 — post-clip-fix regression sweep: DONE (s49).** Undriven full-timeline run + driven war-room
run, both cullstats-instrumented. Non-512 phases matched the documented timeline within normal
variance, 0 cull-census-identity violations anywhere. War room rendered complete on two frames 32s
apart — new baseline: 1138 tasks, fanjal=9448, 0 violations (scales with capture window vs s48's
5.6–5.8k, not a fixed constant). Stability 0 except 3 gracefully-stubbed `[missing-func]` addresses
in the undriven outdoor stretch, never soaked before — parked as M4. Full detail: PORTING-STATE s49.

**M3 — first gameplay: OPENED (s50), LEVEL DESCRIPTION death confirmed + partially traced (s51).**
AVAILABLE CRAFT (craft-select) confirmed reachable and renders correctly, one press past SELECT
LEVEL. LEVEL DESCRIPTION (the `a` prompt from AVAILABLE CRAFT) black-screens and silently kills the
process — now confirmed on 2 independent runs (s50, s51); s51 narrowed the mechanism to the `fs`
(full-sync) freeze as the leading cause rather than the correlated `fmt=7` copy-mode no-op (event
ordering + static-code read both point away from the no-op) — see "Remaining visual defects" above
and PORTING-STATE s50/s51. Backtrace attempts are blocked by a shared-machine load confound, not
solved — corroborated a 3rd time in s52, still with no successful repro under load; an in-process
crash handler (`src/main/main.cpp`, s52) is now in place and needs no external attach, but has not
yet been exercised because the repro has not reached the death screen since it was added. Next
sub-unit is retrying the repro when load is genuinely low, then tracing what DL task fails to reach
FULL_SYNC if the handler doesn't fire. Expect
further new failure classes as this progresses (mission-overlay DMA, a new VI phase, possibly new
ucode ops) — each is its own work unit. *Done when:* 60 seconds of in-mission rendering, craft
visibly responds to synthetic input, stability counters 0, and the phase timeline in this document
covers the mission.

**M4 — parked correctness items**, one work unit each: outdoor `baseFixed = −32768` zero-shade root
cause (currently masked, not fixed); the S=0 triangles in the 640 attribution phase; the I4
`sample=64x128` anomaly if M1 didn't consume it; the 3 `[missing-func]` addresses stubbed in the
undriven outdoor-512 stretch (0x800C7120, 0x800FBD48, 0x800FB190, s49) — identify what they are and
whether the stub is behaviorally silent or masking something.

**M5 — audio de-stubbing (investigation first, not code).** The MusyX audio ucode already
recompiles (`factor5_ucode_b_recompiled.c` sits in the build as a never-called artifact). First
work unit: a design doc only — how audio tasks would run LLE alongside gfx (they share the `dmem[]`
serialization built in s5), what bridges RSP audio output to SDL, and what the audio-gate byte
reversal implies. **Gate M5 behind M2**: audio re-enters exactly the shared-state territory that
cost three sessions before the recursive mutex.

## Next steps, in order of expected value (s52)

1. **M3 — LEVEL DESCRIPTION black-screen/crash: trace the `fs` freeze. In-process crash handler is
   now in place (s52); retry the repro ONLY when system load is genuinely low.** Confirmed on 2
   independent runs (s50, s51). s51 ruled the `fmt=7` native-copy no-op down to "probably downstream
   symptom, not cause" (event ordering: `fs` freezes before the `fmt=7` warning; static read: the
   guard is pre-existing and its null result is checked by every caller). The leading hypothesis is
   still the `fs` freeze itself — some DL task around the AVAILABLE CRAFT → LEVEL DESCRIPTION
   transition never reaches FULL_SYNC. `src/main/main.cpp` now installs a POSIX `sigaction` handler
   for SIGSEGV/SIGBUS/SIGABRT (mirrors the existing Windows-only one) that backtraces to stderr with
   no external attach needed — use this instead of lldb/`sample` for the next H3 attempt. **s52
   tried to exercise it and could not**: `uptime`/`ps aux | grep -c claude` showed load 2.4–3.7
   with 33 concurrent Claude processes (at/above the s51 confound threshold), and the run stalled
   permanently in the 640-wide phase (`[fbpair-cap]` hit at 8192, `fs=0` stuck) before ever reaching
   phase 1024 — the *third* independent occurrence of this exact stall signature under load (s51 had
   two, with different attach methods each time; s52 had none at all). **Do not attempt this repro
   again until `uptime` load average is comfortably under ~1.5 AND few/no other `claude` processes
   are running** — three same-signature stalls across two sessions is strong enough now that a 4th
   attempt under similar load should not be attempted; wait or ask the user instead of burning
   another cycle. Do not attempt a fix until the mechanism is clear. Full detail: PORTING-STATE s50,
   s51, s52.
2. Once the black screen is understood/fixed, continue past AVAILABLE CRAFT toward mission 1
   launch. Expect further new failure classes (mission overlay DMA → missing-func /
   UnhandledJumpTarget, new VI phase, possibly overlays 12/44 needing the s47 splice recipe). Each
   new failure is its own work unit.
3. **M4 parked items**, cheapest first: identify the 3 `[missing-func]` addresses stubbed in the
   s49 undriven outdoor-512 run (0x800C7120, 0x800FBD48, 0x800FB190) — symbol lookup, then decide
   if the stub is silent or needs real implementation. Then outdoor zero-shade root cause, the S=0
   640-phase triangles, and the I4 sample=64x128 anomaly.
4. **Band-row coverage history** (settled chain, for reference): s41 `MARK_VTX` proved a coverage
   hole; s42 `LOG_YHIST` proved submission through band rows; s43 `LOG_ZSTATE` proved raster-clean
   draws; s27–s31 eliminated texture decode; s45–s47 pinned and fixed the clip-dispatch loss; s48
   proved the fix fills the band (and renamed the scene); s49 closed the regression sweep. s40's
   `col`-write probe fails its own control — do not reuse.
5. **GPU→CPU present PNG** via `NativeTarget::copyToRAM` — a convenience, not a blocker.

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
`tools/fixup_factor5_ucode.py`. **s47: before the fixup, also run
`python3 tools/make_clip_composite.py` + RSPRecomp on `factor5_rsp_ovl4.toml`** — fixup 6 splices
the clip-overlay translation from `factor5_ucode_ovl4_recompiled.c` and hard-fails without it
(build/ is gitignored, so a fresh checkout must regenerate it). `factor5b_rsp.toml` (ROM 0x9ABE0)
is the **MusyX audio** ucode; `factor5_ucode_b_recompiled.c` stays in the build as a never-called
artifact (s5).

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

The s2–s5 stabilization-era claims (LoadTile underflow, zeroed DL-chunk bytes, RDP-ring/trig-load
misreads of the audio `ucode_data`, "two gfx ucodes") are compressed to one line: **every one was
eventually explained by the shared-`dmem[]` race** (audio tasks staging over gfx state; fixed by
the recursive mutex, s5). Full detail: PORTING-STATE and PROJECT-OVERVIEW §3. Do not re-litigate
any s2–s4 conclusion without checking that section.
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
- **Claims (s9, sixth pass), compressed:** "0x790000 is a z-buffer the VI never scans" (s10/s18/
  s21: it is a presented, double-buffered colour buffer — the +0x100000 z-pattern just holds
  everywhere else) and "`[dpc-behind]` counts 17 867 wrap drops in 60 s" (s10: real figure
  9 056 256 in 70 s — the counter read a sampled path).
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
- **Claims (s12–s16), compressed:** "the 0x60xxxx I4/CI4 dumps are the hangar floor/wall assets"
  (s16: wrong assets — real CI sources 0x741B80/0x741460/0x4Fxxxx/0x6Axxxx) and "the 0x65xxxx
  RGBA16 loads are hangar assets" (s17: they fire during the 1024 title phase — why five sessions
  of knob-tuning never moved the band). **Why believable:** both decode into plausible imagery;
  a plausible decoded image does not identify a phase.
- **Claim (s14):** `ROGUESQ_FIX_LINE_MASK` (force `line = 2^(masks-4)` on 4-bit tiles).
  **Overturned by s15:** wrong direction — the mask/line "disagreement" tiles are real; replaced
  by `ROGUESQ_FIX_SAMPLE_BOUNDS`. **Why believable:** mask and line disagreeing usually does mean
  one is wrong.
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
- **Claim (s46):** no complete clip overlay exists raw in the ROM (whole-ROM byte scan); the game
  materializes overlay images in DRAM at runtime, so only a runtime capture can recover it.
  **Overturned by s47:** all five runtime-captured overlay images are byte-identical to the ROM at
  `RDRAM_addr + 0xC00` (clip: 544/544 at ROM 0x26420). The recompiled window region is the packed
  overlay *storage* (init at window+8), which s46 read as "init image + stale clip tail" and which
  made its scan expectations wrong. **Why believable:** the window-region disassembly genuinely
  contains init code and clip-fan fragments at shifted offsets, and a byte scan for the *expected
  window layout* genuinely finds nothing.
- **Claim (s46):** ~40 window entries/task arrive via a non-L_1298 `jr` (jrc sum 247 vs 287 label
  hits), so case-level routing of the clip splice may be unsafe. **Overturned by s47** (fixup 5
  stray census): 4221/4221 `case 0x1DB0` arrivals come from the L_1298 `jr $3` (debug_line 594)
  with DMEM 0x153 already set to the requested overlay id. The excess label hits were
  fall-throughs from code above L_1DB0, which the label counters count but the dispatch does not.
  **Why believable:** the two counters were believed to measure the same population; they differ
  by exactly the fall-through paths.
- **Claim (s12–s47):** the 512-wide origin-0x6AB400 scene is the "main-menu hangar" — landing
  pad, parked X-wing, hangar walls. **Overturned by s48:** it is the **level-select war room**,
  rendered pre-fix without every clip-flagged triangle (tiered console rings, holotable), which
  made the central platform read as a pad and the Mos Eisley preview hologram as a parked X-wing.
  Proven by wall-structure identity between the s41 control frames and the s48 full render, same
  origin, same input path, arrival times matching to 0.2 s. **Why believable:** the partial
  render was a coherent-looking scene for 36 sessions, and SELECT GAME's photographic hangar
  backdrop reinforced the "hangar" frame; nothing looked missing until the missing half rendered.
- **Claim (s47):** the briefing room presents from origin 0x656400, SELECT LEVEL from 0x696100,
  the clip fix changed menu timing, and the verify run overshot the hangar. **Overturned by
  s48:** all four wrong. The war room / SELECT LEVEL presents from **0x6AB400** (three runs); the
  0x696100 `[vi]` lines sit in the 640-wide pre-title phase; menu routing and timing are
  unchanged (title → SELECT GAME → war room, one press each, war room at 54.5 s vs s23's 54.7 s);
  and nothing was overshot — the band scene was on screen the whole time, rendering complete for
  the first time. **Why believable:** the completed render looked like a brand-new scene, so
  nearby unfamiliar origins in the log read as its identity, and "we missed the hangar" was the
  only story consistent with the hangar still existing.

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
