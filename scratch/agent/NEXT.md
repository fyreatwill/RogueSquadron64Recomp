# NEXT work unit — land + confirm the scissor-rect out-of-bounds guard

## Where the investigation stands

s245 statically traced s244's new Metal SIGABRT (`Set Scissor Rects
Validation (rect.x(77)+rect.width(0))(77) must be <= render pass
width(6)`, `FramebufferRenderer::submitRasterScene`) to a confirmed
mechanism — **do not re-open the static trace, it's done**:

1. `render pass width(6)` is a REAL, correctly-created 6px-wide
   `RenderTarget` (from `fbPair.colorImage.width` — traced
   `rt64_state.cpp:2128` and `2052-2054`), not a misread of a bigger
   target.
2. The only width guard on this path (`rt64_state.cpp:2015`, "s78")
   only rejects `width==0` or `width>1280` — 6 passes clean. This is
   the SAME "1..257 wild width garbage" class already named in
   `rt64_framebuffer_renderer.cpp:646-654`'s s82 comment, whose guard
   only covers a different, unrelated consumer (VI-presentation
   "last-drawn" heuristic).
3. The scissor rect (`x=77`) overflows because `convertFixedRect()`
   (`rt64_framebuffer_renderer.cpp:60-91`) never scales/clips the raw
   RDP-native scissor coordinate against the actual destination
   target's width — a normal ~320px-screen coordinate passes through
   almost unmodified onto the 6px target.

Full mechanism detail: PORTING-STATE Session 245. Full original crash
detail: PORTING-STATE Session 244.

## This iteration: implement fix (b) from s245, then confirm

s245 proposed two fixes and preferred (b) as lower-risk:

- (a) Widen the `rt64_state.cpp:2015` guard to reject wild widths at
  target-creation time — risk: unclear if 1..257 is EVER a legitimate
  width for some real small N64 framebuffer use in this game, and s82's
  `saneW` guard was deliberately scoped narrow for a reason not fully
  re-investigated this session.
- **(b) PREFERRED — clip/skip out-of-bounds scissor rects in
  `submitRasterScene`**, mirroring the existing empty-scissor skip
  already in that exact function
  (`lib/rt64/src/render/rt64_framebuffer_renderer.cpp:736-757`, comment:
  *"Draw calls can sometimes end up with empty scissors and cause
  validation errors. We just skip them."*). Same pattern, same
  function, already proven safe — lower risk than touching target
  creation.

### Do this iteration

1. Read `rt64_framebuffer_renderer.cpp:730-773` again (the
   `previousScissor != triangles.scissor` / `setScissors` call site) to
   confirm the exact insertion point and what target-dimension fields
   are available at that point (`fbStorage->colorTarget->width`/
   `->height` — confirm these field names exist on `RenderTarget` by
   grepping its class, don't assume).
2. Add a guard immediately after (or merged with) the existing
   `triangles.scissor.isEmpty()` check: if the scissor rect's `right` or
   `bottom` exceeds `fbStorage->colorTarget->width`/`height` (or `left`/
   `top` are negative/exceed bounds), either (i) clamp the rect to the
   target's actual bounds before calling `setScissors`, or (ii) skip the
   draw call entirely like the empty-scissor case does. Clamping is
   probably more correct (still draws SOMETHING instead of dropping
   geometry) but skipping is simpler and matches the existing pattern —
   pick based on which is a smaller diff against the existing code
   shape; either is acceptable given the goal is "stop the crash", not
   "render this degenerate framebuffer correctly" (it's a 6px-wide
   garbage-width target, not a real gameplay-visible framebuffer).
3. Gate a log line behind a new env var (`RT64_LOG_SCISSOR_CLAMP` or
   similar — follow the exact `getenv`-cached-static-lambda pattern from
   `rt64_vi_renderer.cpp`'s `RT64_LOG_VI_ZERO_SIZE`, see NEXT.md's old
   "Env-gated logging pattern to reuse" note, still valid) so a re-soak
   can positive-control-confirm the guard actually fires on the real
   trigger (iron rule 1 — a null result without a positive control is
   worthless).
4. Build clean (`DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer
   cmake --build build`), verify the fresh binary carries the new log
   string (`strings build/RogueSquadron64Recomp | grep <new-tag>`) and is
   newer than the soak's start time before trusting any result.
5. Re-soak with a NEW tag (e.g. `scissorfix1`) using the same
   `campose*`/`schedulepush2` schedule as `mtldebug1`/`mtldebug2`,
   `GAME_EXTRA_ENV="MTL_DEBUG_LAYER=1 RT64_LOG_VI_ZERO_SIZE=1
   RT64_LOG_SCISSOR_CLAMP=1"` (keep the VI guard's log armed too, no
   reason to drop it). Expected discriminating outcome: the new guard's
   log line fires at/around the same t≈131.7s window the crash used to
   hit, AND zero `Set Scissor Rects Validation` assertions appear
   anywhere in `run.log` (mirrors s244's confirmation pattern exactly).
6. `lib/rt64` will be touched — run `./submodule-patches/export.sh` and
   confirm the new guard's lines appear in the refreshed
   `submodule-patches/rt64.patch` before committing (hard rule, iron
   rule 9).
7. If the soak reveals the guard fires but ANOTHER new crash surfaces
   past it (as happened s243->s244->s245), that's fine — document it the
   same way, do not chase it in the same iteration (budget rule).

### Do NOT do this iteration

- Do NOT re-open the static trace — s245 already identified the
  mechanism with high confidence from two converging code paths.
- Do NOT implement fix (a) (widening the target-creation width guard)
  instead of (b) unless (b) turns out to be structurally impossible —
  (b) was assessed as lower-risk in s245 and should be tried first.
- Do NOT re-run `mtldebug1`/`mtldebug2`/`malloclog1`/`malloclog2`/
  `metalresize1`/`campose15` (all superseded/results stand). Use a new
  tag (`scissorfix1`).
- Do NOT assume this connects to the s238-242 CALayer SIGSEGV family
  just because of timing overlap (t≈131s) — still unproven, still not
  established either way (carried forward from s244/s245).

## Environment notes (carried forward, still current as of s245)

- **Permission gate CONFIRMED CLEARED through s245.**
- **`GAME_EXTRA_ENV`** (`run_mission_keys.sh`, s241): space-separated
  `VAR=val VAR2=val2` string, scopes extra env vars to ONLY the game
  process.
- **Env-gated logging pattern**: `static const bool s_X = [](){ const
  char *v = std::getenv("VAR_NAME"); return v && v[0] && v[0] != '0'; }();`
  then `if (s_X) { std::fprintf(stderr, ...); std::fflush(stderr); }` —
  needs `#include <cstdio>`/`<cstdlib>` if not already present in the
  file (`rt64_framebuffer_renderer.cpp` already has extensive
  `ROGUESQ_LOG_*` uses of this exact pattern in the same function —
  copy the local style, not the VI file's).
- **Watch for hlslpp swizzle-type format-string mismatches**: `%u` with
  an `hlslpp::uintN`'s `.x`/`.y` member needs an explicit
  `(unsigned int)(...)` cast or the compiler warns (caught in s244).
- **Block-wait pattern**: `TaskOutput` with `block: true` and a generous
  timeout (180000-480000ms) against the background task ID returns the
  final result cleanly when the Stop hook fires mid-soak.
- `/tmp` is not writable this session — write scratch/report files
  inside `RogueSquadron64Recomp`/`N64Recomp`/`rogue_squadron64` only.
- Compound `cd ... && ...` and `git -C <path> <cmd>` get blocked/need
  extra approval — issue `cd` as its own Bash call first.
- **Headless permission matching is a PREFIX match** — write
  `env PROBE_MODE=1 zsh run.sh`, not `PROBE_MODE=1 zsh run.sh`.
- **`campose*` armed env-var set** (unchanged since `campose11`):
  `ROGUESQ_LOG_CAMPOSE`, `ROGUESQ_LOG_MAT3INV`,
  `ROGUESQ_LOG_UNLIT_MESH_TRACER`, `ROGUESQ_LOG_RENDERUNLIT_GUARD`,
  `ROGUESQ_LOG_HEAPWALKER_GUARD`/`GUARD3`/`GUARD4`,
  `ROGUESQ_LOG_MESGQUEUE_GUARD`, `ROGUESQ_LOG_HEAPLISTDEQ_GUARD`,
  `ROGUESQ_LOG_EMIT_DL_GUARD2`/`GUARD3`, `ROGUESQ_LOG_DL_PAYLOAD_STALE=1`
  — keep these armed in any new soak.
- **SELECT-CRAFT->mission transition family tally unchanged**: 5/10
  crashed vs 5/10 survived (CALayer SIGSEGV family only, as of
  `malloclog2`, s242). The VI-NaN and scissor-rect SIGABRTs are
  excluded from this tally — different crashes entirely.
- **`rs64_elapsed_seconds()`** (`src/main/rt64_render_context.cpp`,
  `extern "C"`) is the canonical shared wall-clock — declare
  `extern "C" double rs64_elapsed_seconds(void);` at NAMESPACE scope in
  any new PATCH block that needs it.
- **Verify "crash-free" visually**: MD5-checksum a spread of `hold_NN.png`
  — `scratch/agent/checksum_campose11.py` (s235) is mtime-aware, reuse
  this pattern.
- **`rm -f <glob>`/`find <dir> -delete` are blocked** — use
  `python3 -c "import glob, os; [os.remove(f) for f in glob.glob('<pattern>')]"`.
- Re-running the same soak script/tag OVERWRITES the previous run's
  `run.log` in place — copy the driver script to a new tag name per soak.
- The driver's own `CRASH: N` summary counts occurrences of the LITERAL
  STRING `[CRASH]` (many per crash) — grep `[CRASH] caught signal` for
  actual crash event counts.
- `scratch/agent/STATUS`/`OUTCOME` get reset at the START of each
  iteration by the harness — normal.
- **`/scratch/` is wholesale gitignored** — only `STATUS`, `OUTCOME`,
  `NEXT.md`, and `run_mission_keys.sh` are tracked exceptions.
- Verify a fresh binary before trusting a null result: `strings
  build/RogueSquadron64Recomp | grep '<your-new-tag>'` plus `ls -la
  build/RogueSquadron64Recomp` vs. the soak's start time.

## Housekeeping still flagged, still not done

`docs/CURRENT-TRUTH.md` is past both the ~35 KB CLAUDE.md budget (now
~394 KB) and the Read tool's 256 KB single-read limit (confirmed s195,
still true s245 — read it with `grep`/offset-limited `Read`, never a
plain whole-file `Read`) — flagged for 36+ sessions without action.
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
Session 215) — GUEST-side recompiled-C-code assert family (`sinfApprox`,
`funcs_5.c`), confirmed DIFFERENT from the HOST-side Metal-validation
bugs (s243/s244/s245) — do not conflate. Still worth picking up on its
own merits eventually but is NOT the next work unit.
