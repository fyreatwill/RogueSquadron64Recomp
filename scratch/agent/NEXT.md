# NEXT work unit — static trace the new scissor-rect Metal SIGABRT

## Where the investigation stands

s244 landed and confirmed a fix for s243's `fbSize()==0` NaN-viewport
crash (`lib/rt64/src/render/rt64_vi_renderer.cpp`, `VIRenderer::
render()` now skips the draw for that frame when `vi.fbSize()` reports a
zero component). The `mtldebug2` re-soak confirmed with a same-run
positive control: the exact `osViSetMode #12`/`viW=0` trigger point now
logs `[vi zero-size guard] skipping VI draw, fbSize=(0,0)` twice instead
of crashing, and zero `Viewport Validation` assertions appear anywhere
in the run. **This specific fix is DONE — do not re-open it.**

The same `mtldebug2` soak still crashed, but on a **NEW, unrelated**
Metal SIGABRT:

```
-[MTLDebugRenderCommandEncoder setScissorRects:count:]:4189: failed assertion `Set Scissor Rects Validation
(rect.x(77) + rect.width(0))(77) must be <= render pass width(6)
'
```

Stack: `RT64::FramebufferRenderer::submitRasterScene` (a lambda over
`InstanceDrawCall`) -> `MetalCommandList::drawInstanced` ->
`checkForUpdatesInGraphicsState` -> `-[MTLDebugRenderCommandEncoder
setScissorRects:count:]`. **This is a completely different code path
from `VIRenderer`** — raster-scene framebuffer submission, not VI
presentation — so s244's guard is unrelated to it and cannot have
caused or masked it.

Timing note (NOT yet causal evidence): this crash fired at wall-clock
t≈131.7s, the same approximate window as the s238-242 host-CALayer
`n=12420`/`t≈131s` SIGSEGV family — but different signal (SIGABRT vs
SIGSEGV), different stack, different validation message. **Do not
conflate the two.** Full detail and log excerpts: PORTING-STATE Session
244.

## Hypotheses for this iteration

1. **H1 — `render pass width(6)` is a genuinely tiny, valid render
   target** (e.g. a 1D lookup texture, a shadow map tile, a
   cubemap/icon face) and the scissor rect (`rect.x=77`) is being
   computed against the WRONG target's dimensions — a scale/space
   mismatch bug (something computing a scissor in one framebuffer's
   coordinate space but applying it to a different, smaller one).
2. **H2 — `render pass width(6)` is itself a degenerate/uninitialized
   value** (should be some real width like 320/512/1024 but reads as 6
   due to a stale pointer, uninitialized struct field, or an
   arithmetic bug elsewhere) — same *class* of bug as s243/s244's
   `fbSize()==0` (a numeric field going degenerate transiently), just
   in a different subsystem (raster scene submission vs VI
   presentation).
3. **H3 — this is a pre-existing bug unrelated to anything from s238
   onward**, and it was simply never reached before because the
   VI-NaN crash (s243) or the CALayer SIGSEGV (s238-242) always fired
   first in every prior soak — s244's guard just cleared the path for
   the game to run long enough to reach it. (This has a reasonably
   high prior — it's the simplest explanation for "why has nobody seen
   this before" and doesn't require inventing a new interaction.)

**Discriminating measurement for THIS iteration**: static read only
(no `lib/` edit yet — per "no speculative fix" rule, confirm the
mechanism before touching code). Read
`lib/rt64/src/render/rt64_framebuffer_renderer.cpp`'s
`submitRasterScene()` and whatever function computes the scissor rect
for an `InstanceDrawCall` (grep for `setScissors`/`RenderRect` calls in
that file, similar to how s243 traced `getViewportAndScissor()`). Find:
(a) what render target width=6 corresponds to (grep for where that
framebuffer's dimensions get set — is 6 ever a legitimate designed
size, or clearly a fallback/uninitialized default?), (b) where
`rect.x=77` comes from and whether it's computed against a DIFFERENT
framebuffer's size than the one actually being rendered to (H1) or
whether the width itself is corrupt (H2).

## Do this iteration

1. Read `lib/rt64/src/render/rt64_framebuffer_renderer.cpp` — find
   `submitRasterScene()` and trace how `RenderRect`/scissor values are
   built for `InstanceDrawCall`s (mirror s243's method: find the
   producing function(s), read the actual arithmetic, don't guess).
2. Grep for where the render pass's own width/height (the `render pass
   width(6)` in the assertion) is set — likely a `Framebuffer`/
   `RenderFramebufferStorage` field passed into
   `FramebufferRenderer::recordFramebuffer()` (the caller one frame up
   the crash stack, in the same file). Trace it back to its origin.
3. Determine H1 vs H2 vs H3 from the static read alone if possible. If
   the code doesn't discriminate cleanly, the next step (still this
   iteration if budget allows, else next iteration) is a **targeted
   log line** (same `getenv`-cached-static-lambda pattern used for
   `RT64_LOG_VI_ZERO_SIZE`) printing the render target's actual
   width/height and the pointer/ID identifying which framebuffer it is,
   gated behind a new env var, immediately before the `setScissors`
   call — NOT a fix yet, just enough instrumentation to confirm which
   hypothesis is correct on the next soak.
4. Do NOT implement a guard/fix until the static read (and possibly one
   instrumented soak) has identified the actual mechanism — this
   mirrors s243's discipline (trace first, guard second, confirmed
   guard third) which worked cleanly for the VI bug in s243/s244.
5. If this touches `lib/rt64` (it will, at minimum for instrumentation),
   run `./submodule-patches/export.sh` and commit the refreshed patch
   in the SAME iteration (hard rule, iron rule 9).

## Do NOT do this iteration

- Do NOT re-open or re-guard the `fbSize()==0` VI-NaN bug — s244 fixed
  and confirmed it. Re-litigating it would be regressing to a solved
  problem.
- Do NOT assume the scissor-rect crash is connected to the s238-242
  CALayer SIGSEGV family just because the timing (t≈131s) overlaps —
  that is an unproven hypothesis (see H3 above for the more likely
  boring explanation: this bug was always there, just never reached).
- Do NOT jump straight to a fix/guard without first reading the actual
  code — "clamp `render pass width` to something non-zero" without
  knowing WHY it's 6 risks papering over a real corruption bug the same
  way a blind clamp would have for the VI case (though in that case the
  static trace happened to fully explain the 0/0 NaN mechanism before
  the guard was written — do the same rigor here).
- Do NOT re-run `mtldebug1`/`mtldebug2`/`malloclog1`/`malloclog2`/
  `metalresize1`/`campose15` (all superseded/results stand). A fresh
  soak here should be a NEW tag (e.g. `scissorprobe1`) once
  instrumentation is ready.

## Environment notes (carried forward, still current as of s244)

- **Permission gate CONFIRMED CLEARED through s244.**
- **`GAME_EXTRA_ENV`** (`run_mission_keys.sh`, s241): space-separated
  `VAR=val VAR2=val2` string, scopes extra env vars to ONLY the game
  process. `mtldebug2` used `MTL_DEBUG_LAYER=1 RT64_LOG_VI_ZERO_SIZE=1`
  successfully — same mechanism, just add another `VAR=1` to the string
  for new instrumentation.
- **`RT64_LOG_VI_ZERO_SIZE=1`** is now a real, working env var
  (`lib/rt64/src/render/rt64_vi_renderer.cpp`) — keep it armed in any
  future soak of this render path in case the guard fires unexpectedly
  often (worth knowing even though the immediate crash is fixed).
- **Env-gated logging pattern to reuse for any new instrument**:
  `static const bool s_X = [](){ const char *v =
  std::getenv("VAR_NAME"); return v && v[0] && v[0] != '0'; }();` then
  `if (s_X) { std::fprintf(stderr, ...); std::fflush(stderr); }` —
  matches existing style in `rt64_present_queue.cpp` and now
  `rt64_vi_renderer.cpp`. Needs `#include <cstdio>` and `#include
  <cstdlib>` at the top of the file if not already present.
  **Watch for hlslpp swizzle-type format-string mismatches**: `%u` with
  an `hlslpp::uintN`'s `.x`/`.y` member needs an explicit
  `(unsigned int)(...)` cast or the compiler warns (caught this in s244
  before trusting the soak).
- **Block-wait pattern confirmed again (s244)**: `TaskOutput` with
  `block: true` and a generous timeout (180000-480000ms) against the
  background task ID returns the final result cleanly when the Stop
  hook fires mid-soak — no need to re-launch.
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
- **SELECT-CRAFT->mission transition family tally unchanged this
  session**: 5/10 crashed vs 5/10 survived (CALayer SIGSEGV family
  only, as of `malloclog2`, s242). `mtldebug1`'s NaN-viewport SIGABRT
  and `mtldebug2`'s scissor-rect SIGABRT are BOTH excluded from this
  tally — different crashes entirely.
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

`docs/CURRENT-TRUTH.md` is past both the ~35 KB CLAUDE.md budget (now
~393 KB) and the Read tool's 256 KB single-read limit (confirmed s195,
still true s244 — read it with `grep`/offset-limited `Read`, never a
plain whole-file `Read`) — flagged for 35+ sessions without action.
Migrate durable mechanism/architecture material to `PROJECT-OVERVIEW.md`
and prune superseded detail.

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
(`sinfApprox`, `funcs_5.c`), confirmed DIFFERENT from s243/s244's
HOST-side Metal-validation bugs (different mechanism, different code,
different crash signatures) — do not conflate. Still worth picking up on
its own merits eventually but is NOT the next work unit.
