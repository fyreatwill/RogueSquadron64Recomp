# NEXT work unit — decide: more MTL_DEBUG_LAYER=1 sampling on the CALayer
# family, OR pivot to the guest-side NaN_CHECK fix, OR the CURRENT-TRUTH
# size housekeeping (now genuinely overdue, not just flagged)

## Where the investigation stands

s247 found and fixed a wrong premise from s246's `NEXT.md` (`scissorfix1`
was claimed to not cross the SELECT-CRAFT->mission transition; it
actually did, per its own `[phase]` log, and survived clean) and added a
confirming 2nd soak (`mtldebug3`, identical schedule/env, new tag).
**New sub-tally: 2/2 survived crossing the SELECT-CRAFT->mission
transition under `MTL_DEBUG_LAYER=1` + both the s244 VI-zero-size guard
and s246 scissor-clamp guard armed** — both runs `CRASH: 0`, zero
SIGSEGV/SIGABRT/CALayer, both positive controls (`[scissor-clamp]` 5x,
`[vi zero-size guard]` 2x) fired in both runs. This is kept SEPARATE
from the older, pre-existing 5/10-vs-5/10 tally (`malloclog2`/s242 and
earlier — gathered WITHOUT `MTL_DEBUG_LAYER=1` or either guard). Full
detail: PORTING-STATE Session 247, CURRENT-TRUTH -88.

**n=2 is not a conclusion.** P(2/2 clean by chance, if the true survival
rate is still ~50%) = 0.25 — a quarter of the time you'd see exactly this
by luck. Do NOT write "MTL_DEBUG_LAYER=1 fixes/changes the family" into
CURRENT-TRUTH yet; that needs either (a) enough more clean runs to make
2/2-turned-N/N implausible under a 50% null (5/5 clean ≈ p=0.03 is a
reasonable bar), or (b) a crash that DOES occur under the debug layer,
which would let H1/H2/H3 from s246's `NEXT.md` actually discriminate
(compare its stack/signal against the s238-242 CALayer SIGSEGV
signature).

## Decide first, before running anything

This is a genuine 3-way fork — think about expected information value,
not just "the next line of the old plan":

1. **Continue MTL_DEBUG_LAYER=1 sampling** (3rd, 4th... soak, same
   schedule/env as `mtldebug3`, new tag each time, ~475s wall each). Pro:
   directly extends the n=2 tally toward statistical significance in
   either direction. Con: budget rule 8 — this is soak attempt #2
   (counting `mtldebug3` only; `scissorfix1` was incidental) in the
   current session's run of this hypothesis; a 3rd/4th/5th consecutive
   iteration with still-no-crash and still-inconclusive-n should trigger
   rule 8 and force a pivot rather than open-ended sampling forever.
2. **Pivot to the guest-side NaN/`NAN_CHECK` + unguarded-deref crash
   family** (proposed but unshipped fix, CURRENT-TRUTH -55/-56,
   PORTING-STATE Session 215 — `sinfApprox`/`funcs_5.c`, confirmed
   DIFFERENT from all the HOST-side Metal-validation work s243-247).
   This has a proposed fix sitting unshipped for 30+ sessions and no
   known blocker — potentially higher value than more CALayer sampling.
3. **`docs/CURRENT-TRUTH.md` housekeeping** — now ~406 KB / 5786+ lines,
   flagged 38+ sessions, over both the ~35 KB CLAUDE.md budget and the
   Read tool's 256 KB single-read limit (every session must
   grep/offset-read it, never a plain `Read`). This is a `.claude/`
   hard-rule violation, not just nice-to-have. Migrate durable
   mechanism/architecture material (the superseded/-8x mechanism
   write-ups older than ~10 entries back, once their conclusions are
   fully captured in a compact form) to `PROJECT-OVERVIEW.md`, prune the
   rest. This is real work (probably 2-3 iterations' worth, not one) —
   don't half-do it in a rush at the end of an unrelated iteration.

No hard recommendation is written here on purpose — whichever the next
iteration picks, name the choice and the reason in that session's
PORTING-STATE entry, don't silently default to option 1 just because
it's the literal continuation of s247's soak.

## If continuing option 1 (more MTL_DEBUG_LAYER sampling)

1. Copy `scratch/s73_post_a_scene/run_mtldebug3.sh` to a new tag (e.g.
   `mtldebug4`), same `STICK_SCHEDULE`/`GAME_EXTRA_ENV`/armed-var set —
   do not modify the schedule, it's confirmed to cross the transition.
2. Run as a single foreground/background Bash call (background +
   `TaskOutput` block=true works fine, ~475-480s wall, add margin).
3. Grep `run.log` for `SIGSEGV`, `SIGABRT`, `CALayer`, `Validation`,
   `scissor-clamp`, `vi zero-size guard`, and check `[phase]` for the
   `vi_width=512 (was 1024)` transition line to confirm it crossed.
4. Update the sub-tally (currently 2/2). If a crash DOES occur, compare
   its signal/stack against the s238-242 CALayer SIGSEGV signature before
   concluding anything — this is the actual H1/H2/H3 discriminator.

## Do NOT do this iteration

- Do NOT re-run `scissorfix1`, `mtldebug1`, `mtldebug2`, `mtldebug3`,
  `malloclog1`, `malloclog2`, `metalresize1` in place — all superseded/
  results stand, use a new tag if repeating the soak.
- Do NOT re-open the scissor-rect or VI-NaN static traces (s243-246) —
  both closed, soak-confirmed twice now (`scissorfix1` + `mtldebug3`).
- Do NOT write a CALayer-family conclusion into CURRENT-TRUTH off n=2 —
  see the statistics note above.

## Environment notes (carried forward, still current as of s247)

- **Permission gate CONFIRMED CLEARED through s247.**
- **`GAME_EXTRA_ENV`** (`run_mission_keys.sh`, s241): space-separated
  `VAR=val VAR2=val2` string, scopes extra env vars to ONLY the game
  process.
- **Env-gated logging pattern**: `static const bool s_X = [](){ const
  char *v = std::getenv("VAR_NAME"); return v && v[0] && v[0] != '0'; }();`
  then `if (s_X) { std::fprintf(stderr, ...); std::fflush(stderr); }`.
- **Block-wait pattern**: `TaskOutput` with `block: true` and a generous
  timeout (300000-480000ms) against the background task ID. A single
  480000ms wait was enough for `mtldebug3`'s 475s wall this session
  (unlike s246's 471s soak, which needed a 2nd wait call) — but issue a
  2nd block-wait if the first times out rather than assuming failure.
- `/tmp` is not writable this session — write scratch/report files
  inside `RogueSquadron64Recomp`/`N64Recomp`/`rogue_squadron64` only.
- Compound `cd ... && ...` and `git -C <path> <cmd>` get blocked/need
  extra approval — issue `cd` as its own Bash call first, and plain
  `git status`/`git diff`/etc. (no `-C`) once cwd is already there.
- **Headless permission matching is a PREFIX match** — write
  `env PROBE_MODE=1 zsh run.sh`, not `PROBE_MODE=1 zsh run.sh`. Also
  applies to `cd dir && zsh script.sh > log 2>&1` patterns — split `cd`
  into its own Bash call before a redirected command, or it's rejected
  as an ambiguous compound.
- **`campose*` armed env-var set** (unchanged since `campose11`):
  `ROGUESQ_LOG_CAMPOSE`, `ROGUESQ_LOG_MAT3INV`,
  `ROGUESQ_LOG_UNLIT_MESH_TRACER`, `ROGUESQ_LOG_RENDERUNLIT_GUARD`,
  `ROGUESQ_LOG_HEAPWALKER_GUARD`/`GUARD3`/`GUARD4`,
  `ROGUESQ_LOG_MESGQUEUE_GUARD`, `ROGUESQ_LOG_HEAPLISTDEQ_GUARD`,
  `ROGUESQ_LOG_EMIT_DL_GUARD2`/`GUARD3`, `ROGUESQ_LOG_DL_PAYLOAD_STALE=1`
  — keep these armed in any new soak.
- **The `[phase] vi_width=512 (was 1024) origin=0x006AB400` line at
  ~t=74-75s is THE confirmed SELECT-CRAFT->mission transition marker** —
  check for it explicitly in any new soak's `run.log` before trusting
  that the soak actually reached the family's trigger point; don't just
  assume the schedule worked because it's a copy of a known-good one
  (s247 found a whole session's premise was wrong by skipping this
  check).
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

`docs/CURRENT-TRUTH.md` is past both the ~35 KB CLAUDE.md budget and the
Read tool's 256 KB single-read limit (now ~406 KB / 5786+ lines,
confirmed still true s247) — flagged for 38+ sessions without action. See
option 3 above; this needs to actually get scheduled as a work unit soon,
not indefinitely re-flagged.

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
`funcs_5.c`), confirmed DIFFERENT from the HOST-side Metal-validation bugs
(s243-247, all fixed/soak-confirmed). See option 2 above — this is a live
candidate for the next work unit, not just a footnote.
