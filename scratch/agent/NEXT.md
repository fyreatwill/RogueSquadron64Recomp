# NEXT work unit — guard the fbSize()==0 NaN-viewport crash, then re-soak

## Where the investigation stands

This is a NEW finding (s243), separate from the s238-242 host-CALayer
SIGSEGV investigation at the SELECT-CRAFT->mission transition (`n=12420`,
`t≈131s`). Do NOT conflate the two.

s243 ran `mtldebug1` (`MTL_DEBUG_LAYER=1`, Apple's Metal API validation
layer) per s242's plan. It found a **different, much earlier** crash: a
fatal Metal viewport-validation `SIGABRT` at guest decision `n=4421`:

```
-[MTLDebugRenderCommandEncoder setViewports:count:]:3961: failed assertion `Viewport Validation
viewport.originX must not be infinite or NaN.
viewport.originY must not be infinite or NaN.
viewport.width must not be infinite or NaN.
viewport.height must not be infinite or NaN.
```

Stack: `RT64::VIRenderer::render` -> `MetalCommandList::drawInstanced`
-> `MetalCommandList::checkForUpdatesInGraphicsState` ->
`-[MTLDebugRenderCommandEncoder setViewports:count:]`.

`run.log`'s frame immediately before the crash: `[pe gate #3183] ...
viDiff=1 ... viW=0` — the VI framebuffer width read as **0**, one line
after an `osViSetMode #12` mode-change log line (`width=512`).

**Root cause (static read, `lib/rt64/src/render/rt64_vi_renderer.cpp`)**:
- `getViewportAndScissor()` (~line 103): `sdSize = vi.fbSize()` (when
  `removeBlackBorders` is true, which it is in this build).
- `computeHDSize()` (line 17-19): `hdSize = sdSize * resolutionScale /
  downsamplingScale` — if `sdSize.x` (or `.y`) is 0, the corresponding
  `hdSize` component is also 0 (0 times anything is 0).
- `fromSDtoHD()` (line 21-24): `relativeScale = hdSize / sdSize` — with
  both 0, this is **0/0 = NaN**, which then multiplies into every
  viewport coordinate downstream (`topLeftViewport`/`bottomRightViewport`
  in `getViewportAndScissor`, line 112-115), producing exactly the NaN
  viewport Metal's validator caught.

This is presumably silently tolerated (garbage draw or invisible frame)
by Metal with validation OFF — plausible explanation for why it's never
shown up as a `[CRASH]` in any prior non-`MTL_DEBUG_LAYER` soak despite
`vi.fbSize()` apparently hitting zero at least once here.

**Open question, NOT yet answered**: is this `fbSize()==0` transient a
rare one-off (e.g. specific to the VI mode-switch this schedule
triggers), or does it happen routinely and Metal just eats it silently
every other soak? This session is a single data point for frequency.

## Hypotheses for this iteration

1. **H1 — guarding the zero-size case in `fromSDtoHD`/`computeHDSize`
   eliminates the assertion.** Adding an early-out (skip the draw, or
   clamp `sdSize`/`hdSize` components away from 0) when `vi.fbSize()` is
   degenerate stops the `Viewport Validation` abort in a re-soak with
   the same schedule.
2. **H2 — the guard changes symptom but not root cause.** The abort
   stops, but something else visibly breaks (e.g. a one-frame visual
   glitch, or a different downstream NaN reappears elsewhere consuming
   `hdSize`) — the fix is incomplete or needs to move earlier (e.g.
   guard `vi.fbSize()` itself, not just this one consumer).
3. **H3 — this is unrelated noise.** `fbSize()==0` was itself a fluke of
   this exact schedule/instrumentation combination and won't recur;
   guarding it is harmless but low-value. (Low prior — the mechanism is
   fully explained by a real code path, not a coincidence, so this
   should only be entertained if the guard has zero effect on repeat
   soaks AND `fbSize()==0` never recurs in logging.)

**Discriminating measurement**: instrument `vi.fbSize()` (or the
`sdSize`/`hdSize` computation directly) to log when either component is
0, guard against it (see fix sketch below), rebuild, and re-run the
`mtldebug1`-style soak (same schedule) with `MTL_DEBUG_LAYER=1` still
armed. If the `Viewport Validation` assertion is gone AND the zero-size
log line still fires (proving the condition still occurs but is now
handled), that's H1 confirmed with a positive control. If the assertion
is gone but the zero-size log line never fires either, the guard's
positive control failed — the "fix" can't be trusted yet.

## Do this iteration

1. Read `lib/rt64/src/render/rt64_vi_renderer.cpp` lines 1-125 (already
   read once this session, contents fresh in PORTING-STATE Session 243).
2. Add a guard: when `sdSize.x <= 0 || sdSize.y <= 0` (or `hdSize.x <= 0
   || hdSize.y <= 0` after `computeHDSize`), skip calling
   `commandList->setViewports(viewport)` for that frame (return early
   from `draw()`/`render()` before it), OR clamp `sdSize`/`hdSize` to a
   minimum of e.g. `{1.0f, 1.0f}` before the division in `fromSDtoHD`.
   Prefer skip-the-draw if a one-frame skip is visually harmless (VI
   width 0 for one frame during a mode switch is presumably a blank/
   transitional frame anyway) — simpler and avoids picking an arbitrary
   clamp value. Add a one-line log (reuse the `ROGUESQ_LOG_*` env-gated
   pattern already used elsewhere in this codebase, or a plain
   `fprintf(stderr, ...)` gated by a new `RT64_LOG_VI_ZERO_SIZE` env var)
   so the re-soak can confirm the guard actually fired (positive
   control — iron rule 1).
3. This touches `lib/rt64` — **run `./submodule-patches/export.sh` and
   commit the refreshed patch in this SAME iteration** (CLAUDE.md hard
   rule, iron rule 9). Rebuild:
   `DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build build`
   (check the actual build command/target used in prior sessions if this
   invocation fails — grep PORTING-STATE.md for the last successful
   `cmake --build` line if unsure).
4. Verify the fresh binary carries the new log string: `strings
   build/RogueSquadron64Recomp | grep RT64_LOG_VI_ZERO_SIZE` (or
   whatever string you chose) before soaking.
5. Copy `run_mtldebug1.sh` to `run_mtldebug2.sh` in
   `scratch/s73_post_a_scene/`, same schedule/env, add the new guard's
   log env var to `GAME_EXTRA_ENV` alongside `MTL_DEBUG_LAYER=1`. Tag:
   `mtldebug2`. Run with `run_in_background: true`, block-wait via
   `TaskOutput` if the Stop hook fires mid-run (confirmed pattern,
   s242/s243) rather than re-launching.
6. Check `run.log` for: (a) the zero-size guard log line firing at all
   (positive control the condition still occurs), (b) absence of the
   `Viewport Validation` assertion, (c) whether the SELECT-CRAFT->
   mission transition and beyond is reached crash-free or hits the
   ORIGINAL `n=12420` SIGSEGV family instead (that would be a genuinely
   interesting result — it would mean this NaN-viewport bug was masking
   or unrelated to the CALayer crash, resolved either way).

## Do NOT do this iteration

- Do NOT touch `lib/N64ModernRuntime` — this fix is entirely within
  `lib/rt64`.
- Do NOT re-run `malloclog1`/`malloclog2`/`metalresize1`/`campose15`/
  `mtldebug1` (all superseded/results stand).
- Do NOT assume this guard fixes the s238-242 host-CALayer SIGSEGV
  family — they are DIFFERENT crashes (different signal, different
  stack, different trigger point). Report the `mtldebug2` re-soak result
  on its own terms; only note a connection if the CALayer crash actually
  stops recurring across multiple soaks after this fix (it won't be
  provable in one soak either way — see CLAUDE.md "no cross-run A/B on
  animating scenes").
- Do NOT skip `submodule-patches/export.sh` — this WILL touch `lib/rt64`.

## Environment notes (carried forward, still current as of s243)

- **Permission gate CONFIRMED CLEARED through s243.**
- **`GAME_EXTRA_ENV`** (`run_mission_keys.sh`, s241): space-separated
  `VAR=val VAR2=val2` string, scopes extra env vars to ONLY the game
  process. Reused successfully for `MTL_DEBUG_LAYER=1` in `mtldebug1`
  (positive control: `run.log` line 1 = `Metal API Validation Enabled`).
- **Block-wait pattern confirmed again (s243)**: `TaskOutput` with
  `block: true` and a generous timeout (180000-480000ms) against the
  background task ID returns the final result cleanly when the Stop
  hook fires mid-soak — no need to re-launch.
- **`MTL_DEBUG_LAYER=1` is a strong instrument** — it caught a real bug
  on the very first soak, unlike the silent `MallocStackLogging`
  attempt. Worth keeping armed in future soaks of this render path even
  after this specific NaN-viewport bug is fixed, in case it surfaces
  more.
- `/tmp` is not writable this session — write scratch/report files
  inside `RogueSquadron64Recomp`/`N64Recomp`/`rogue_squadron64` only.
- Compound `cd ... && ...` commands and `git -C <path> <cmd>` get
  blocked/require extra approval — issue `cd` as its own Bash call
  first, then the next command separately.
- **Headless permission matching is a PREFIX match** — write
  `env PROBE_MODE=1 zsh run.sh`, not `PROBE_MODE=1 zsh run.sh`.
- **`campose*` armed env-var set** (unchanged since `campose11`):
  `ROGUESQ_LOG_CAMPOSE`, `ROGUESQ_LOG_MAT3INV`,
  `ROGUESQ_LOG_UNLIT_MESH_TRACER`, `ROGUESQ_LOG_RENDERUNLIT_GUARD`,
  `ROGUESQ_LOG_HEAPWALKER_GUARD`/`GUARD3`/`GUARD4`,
  `ROGUESQ_LOG_MESGQUEUE_GUARD`, `ROGUESQ_LOG_HEAPLISTDEQ_GUARD`,
  `ROGUESQ_LOG_EMIT_DL_GUARD2`/`GUARD3`, `ROGUESQ_LOG_DL_PAYLOAD_STALE=1`
  — keep these armed in any new soak.
- **This exact schedule (`schedulepush2`/`campose*` family) crash rate at
  the SELECT-CRAFT->mission transition is 5/10 soaks crashed vs 5/10
  survived** (as of `malloclog2`, s242) for the ORIGINAL CALayer SIGSEGV
  family — `mtldebug1`'s new SIGABRT does NOT count against this tally,
  it's a different crash that fires before the transition is even
  reached.
- **`rs64_elapsed_seconds()`** (`src/main/rt64_render_context.cpp`,
  `extern "C"`) is the canonical shared wall-clock — declare
  `extern "C" double rs64_elapsed_seconds(void);` at NAMESPACE scope
  (not inside a function body) in any new PATCH block that needs it.
- **Verify "crash-free" visually**: MD5-checksum a spread of `hold_NN.png`
  (Python script, not shell loops) — `scratch/agent/
  checksum_campose11.py` (s235) is mtime-aware, reuse this pattern.
- **`rm -f <glob>`/`find <dir> -delete` are blocked** — use
  `python3 -c "import glob, os; [os.remove(f) for f in glob.glob('<pattern>')]"`.
- Re-running the same soak script/tag OVERWRITES the previous run's
  `run.log` in place — copy the driver script to a new tag name per soak.
- The driver's own `CRASH: N` summary line counts occurrences of the
  LITERAL STRING `[CRASH]` (many per single crash event) — grep
  specifically for `[CRASH] caught signal` to count actual crash events.
- `scratch/agent/STATUS`/`OUTCOME` get reset at the START of each
  iteration by the harness — finding them reset at session start is
  normal.
- **`/scratch/` is wholesale gitignored** — only `STATUS`, `OUTCOME`,
  `NEXT.md`, and `run_mission_keys.sh` are tracked exceptions.
- Verify a fresh binary before trusting a null result: `strings
  build/RogueSquadron64Recomp | grep '<your-new-tag>'` confirms the log
  string actually compiled in, and `ls -la build/RogueSquadron64Recomp`
  vs. the soak's start time confirms it's not a stale binary — both
  cheap, do them before trusting any zero-count result.

## Housekeeping still flagged, still not done

`docs/CURRENT-TRUTH.md` is past both the ~35 KB CLAUDE.md budget and the
Read tool's 256 KB single-read limit (confirmed s195, still true s243 —
read it with `grep`/offset-limited `Read`, never a plain whole-file
`Read`) — flagged for 34+ sessions without action. Migrate durable
mechanism/architecture material to `PROJECT-OVERVIEW.md` and prune
superseded detail.

`fixup_game_funcs.py`'s untracked, single-copy state in the `N64Recomp`
sibling checkout has been flagged since s83, still not fixed (not this
repo's commit scope) — worth surfacing to the user directly.

`/Users/williambuckley/Documents/Tools/N64Recomp` and
`~/Documents/Tools/rogue_squadron64` are separate git checkouts with
long-standing uncommitted changes, unrelated to this repo's commit scope.
Still flagged for the user, not committed autonomously.

The pre-existing NaN/`NAN_CHECK` and unguarded-deref crash families still
have a proposed but unshipped fix (CURRENT-TRUTH -55/-56, PORTING-STATE
Session 215) — this is a GUEST-side recompiled-C-code assert family
(`sinfApprox`, `funcs_5.c`), confirmed DIFFERENT from s243's HOST-side
Metal-viewport-NaN bug (different mechanism, different code, different
crash signature) — do not conflate the two. Still worth picking up on
its own merits eventually but is NOT the next work unit.
