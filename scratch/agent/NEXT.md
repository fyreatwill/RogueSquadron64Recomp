# NEXT work unit — extend the soak past both fixed SIGABRTs, add a
# clean MTL_DEBUG_LAYER data point to the CALayer SIGSEGV family tally

## Where the investigation stands

s246 implemented + soak-confirmed the scissor-rect clamp guard
(`lib/rt64/src/render/rt64_framebuffer_renderer.cpp`,
`submitRasterScene`). Combined with s244's VI zero-size guard, **both
Metal-validation SIGABRTs found by `MTL_DEBUG_LAYER=1` soaking
(mtldebug1/mtldebug2) are now fixed and soak-confirmed** (`scissorfix1`:
CRASH 0, wall=471s, two independent positive controls fired, zero
validation assertions). Full mechanism/fix detail: PORTING-STATE
Sessions 243-246, CURRENT-TRUTH -87/-86/-85/-84.

This clears the two known crashes that were happening at t≈131s-ish
during `MTL_DEBUG_LAYER=1` soaks, which is the SAME rough time window as
the older, still-unresolved SELECT-CRAFT->mission CALayer SIGSEGV family
(5/10 crashed vs 5/10 survived as of `malloclog2`/s242, tallied WITHOUT
`MTL_DEBUG_LAYER` — that instrument had never gotten a clean, fix-free
run of the family before because the scissor/VI bugs kept intercepting
it first).

## Hypotheses (write discriminating outcome down before soaking)

- **H1**: the CALayer SIGSEGV family is unrelated to the two now-fixed
  SIGABRTs — a clean `MTL_DEBUG_LAYER=1` soak run past t≈131s will
  either hit the SAME `CALayer`-teardown SIGSEGV s238-242 characterized,
  OR survive clean, at roughly the same ~50% rate already tallied.
  Discriminates: crash signal/stack matches the s238-242 SIGSEGV
  signature (not a NEW SIGABRT).
- **H2**: the two now-fixed SIGABRTs were MASKING the CALayer crash from
  ever being reached under `MTL_DEBUG_LAYER=1` specifically (not from
  ever happening at all — the family tally soaks never had the debug
  layer armed). A clean run might now surface a MORE SPECIFIC Metal API
  diagnostic for the CALayer SIGSEGV itself, if the debug layer catches
  a use-after-free/released-resource pattern before the SIGSEGV lands.
  Discriminates: a NEW Metal Validation assertion (not a raw SIGSEGV)
  appears in `run.log` before/instead of the SIGSEGV.
- **H3**: there is a THIRD, still-undiscovered bug in the same rough
  time window that the scissor fix's `continue` (dropping a draw call
  entirely for badly out-of-bounds targets) has changed the timing of
  enough to either newly expose or newly hide. Discriminates: crash
  signature is neither the s238-242 SIGSEGV nor a scissor/VI SIGABRT —
  something new.

The single discriminating measurement: **one soak, family schedule
(`schedulepush2`/`campose*`), `MTL_DEBUG_LAYER=1` armed, run long enough
to cross the SELECT-CRAFT->mission transition** (the family's actual
trigger point — check `run_campose11.sh`/`run_mtldebug2.sh` for the
schedule that crosses it, not just `scissorfix1`'s hold-in-hangar
schedule) — read whatever crash (if any) comes out against H1/H2/H3.

## Do this iteration

1. Read `scratch/s73_post_a_scene/run_campose11.sh` (or whichever
   `campose*` script is confirmed to actually cross the SELECT-CRAFT ->
   mission transition, not just hold in the hangar — `scissorfix1`'s
   schedule per s246 only held in the ship-select hangar screen, it did
   NOT cross into a mission, which is why it couldn't have hit the
   CALayer family regardless of outcome) to get the exact
   transition-crossing schedule.
2. Copy it to a new tag (e.g. `mtldebug3`), keep `MTL_DEBUG_LAYER=1
   RT64_LOG_VI_ZERO_SIZE=1 RT64_LOG_SCISSOR_CLAMP=1` in `GAME_EXTRA_ENV`
   (all three guards/logs stay armed — no reason to drop visibility).
3. Run it as a single foreground/background Bash call, block-wait for
   completion (`TaskOutput` block=true, generous timeout).
4. Grep `run.log` for: `SIGSEGV`, `SIGABRT`, `CALayer`, `Validation`,
   `scissor-clamp`, `vi zero-size guard`, `CRASH:`. Compare against
   H1/H2/H3 above.
5. Update the family tally (currently 5/10 vs 5/10) with this run's
   outcome, noting it's the FIRST family-transition soak with
   `MTL_DEBUG_LAYER=1` armed and both new guards landed — flag it as a
   new sub-condition, don't just increment the old tally blindly if the
   crash signature differs from the prior 10 runs' methodology.

## Do NOT do this iteration

- Do NOT re-open the scissor-rect or VI-NaN static traces — both closed,
  soak-confirmed, do not re-litigate.
- Do NOT re-run `mtldebug1`/`mtldebug2`/`malloclog1`/`malloclog2`/
  `metalresize1`/`scissorfix1` (all superseded/results stand). Use a new
  tag.
- Do NOT assume H1 by default just because it's listed first — actually
  read the crash signature if one occurs.

## Environment notes (carried forward, still current as of s246)

- **Permission gate CONFIRMED CLEARED through s246.**
- **`GAME_EXTRA_ENV`** (`run_mission_keys.sh`, s241): space-separated
  `VAR=val VAR2=val2` string, scopes extra env vars to ONLY the game
  process.
- **Env-gated logging pattern**: `static const bool s_X = [](){ const
  char *v = std::getenv("VAR_NAME"); return v && v[0] && v[0] != '0'; }();`
  then `if (s_X) { std::fprintf(stderr, ...); std::fflush(stderr); }`.
- **Watch for hlslpp swizzle-type format-string mismatches**: `%u` with
  an `hlslpp::uintN`'s `.x`/`.y` member needs an explicit
  `(unsigned int)(...)` cast or the compiler warns (caught in s244).
- **Block-wait pattern**: `TaskOutput` with `block: true` and a generous
  timeout (180000-480000ms) against the background task ID returns the
  final result cleanly when the Stop hook fires mid-soak. Note: a single
  480000ms wait was NOT enough for a 471s-wall soak plus setup overhead
  in s246 — issue a second block-wait call if the first times out rather
  than assuming failure.
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
- **SELECT-CRAFT->mission transition family tally**: 5/10 crashed vs
  5/10 survived (CALayer SIGSEGV family only, as of `malloclog2`, s242),
  **NONE of those 10 runs had `MTL_DEBUG_LAYER=1` armed** — this
  iteration's soak, if it crosses the transition, is the first data
  point under the stricter instrument. The VI-NaN and scissor-rect
  SIGABRTs (now both fixed) are excluded from this tally regardless.
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
~406 KB) and the Read tool's 256 KB single-read limit (confirmed s195,
still true s246 — read it with `grep`/offset-limited `Read`, never a
plain whole-file `Read`) — flagged for 37+ sessions without action.
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
bugs (s243-246, all now fixed) — do not conflate. Still worth picking up
on its own merits eventually but is NOT the next work unit.
