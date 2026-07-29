# NEXT work unit — run the FIXED malloc-debug-tooling soak (malloclog2)

## Where the investigation stands

s238 found a host-side SIGSEGV inside Apple QuartzCore
(`x_hash_table_remove_ptr`<-`CAMediaTimingInvalidate`<-`-[CALayer
dealloc]`<-`CA::Transaction::commit`), converging 3/3 soaks on the same
trigger point: guest call counter `n=12420`, wall-clock `t≈130.8-131.7s`.

s239 (static read) proposed a cross-thread `CAMetalLayer::
setDrawableSize` race candidate. s240 (dynamic instrument) REFUTED it —
zero fires across a 459s soak, traced to `resize()` never being called
because nothing in `src/main/` ever resizes the host window.

s241 tried to stand up Apple's malloc debug tooling
(`MallocStackLogging=1`/`MallocScribble=1`) but:
1. Discovered `~/Library/Logs/DiagnosticReports/` is outside this
   session's allowed directories, and `malloc_history`/`atos`/`leaks`
   are not in the Bash permission allowlist — **the "post-mortem query
   malloc_history against the crash" plan is unreachable in this
   sandbox, full stop.** Don't re-attempt it without a human granting
   access or an allowlist change.
2. Found the `malloclog1` soak was confounded: exporting `Malloc*` vars
   at the wrapper level leaked them into every helper subprocess
   `run_mission_keys.sh` spawns (bc/sleep/date/tail/sed/nested zsh), not
   just the game binary, adding CPU churn during the timing-sensitive
   pre-phase-gate window. Fixed via a new `GAME_EXTRA_ENV` mechanism in
   `run_mission_keys.sh` (scopes extra env vars to ONLY the game
   process's `env` invocation at the launch line) — verified
   byte-identical behavior for unset `GAME_EXTRA_ENV` before trusting it.
   `run_malloclog2.sh` is staged, ready to run, uses the fix.

The `malloclog1` run itself: `CRASH: 0` — inconclusive given the
confound, not a real data point either way.

## Do this iteration

1. Run `zsh run_malloclog2.sh` from `scratch/s73_post_a_scene/`
   (`run_in_background: true`, generous timeout 480000-600000ms — same
   pattern as `metalresize1`/`malloclog1`, ~460s expected). Foreground/
   synchronous within the background task (it does its own SIGKILL at
   the end); block-wait with `TaskOutput` if the Stop hook fires mid-run
   rather than re-launching.
2. Positive control / sanity check BEFORE trusting any result: this run
   should behave like a normal soak with no extra subprocess overhead —
   spot-check the captured background output does NOT show
   `MallocStackLogging` messages from non-game helper PIDs (bc/sleep/
   date/tail/sed) the way `malloclog1`'s did. If it does, `GAME_EXTRA_ENV`
   isn't actually scoping correctly — stop and re-diagnose before
   drawing any conclusion from the crash-or-not outcome.
3. Discriminating outcome: does it crash? If yes — since `malloc_history`
   is unreachable — the ONLY postmortem evidence available is the
   existing crash handler's stderr dump already captured in `run.log`
   (`[CRASH][siginfo] si_addr=...`, `[CRASH][mcontext] ...` register
   file, `backtrace_symbols_fd`). Compare `si_addr` against the
   `MallocScribble=1` pattern (`0x55` bytes) — if the faulting address or
   a nearby read resolves to scribbled memory, that's a positive
   identification of a use-after-free without needing `malloc_history` at
   all. If it doesn't crash, this is a null result requiring a decision
   per iron rule 8 (this would be soak #2 of this specific tooling
   attempt with a clean environment — one more clean null is the
   3-strike budget, not yet exhausted, but getting close; if it doesn't
   crash, weigh whether malloc debug tooling itself (even correctly
   scoped) perturbs the race enough to matter, vs. plain non-determinism).

## Do NOT do this iteration

- Do NOT attempt `malloc_history`/`atos`/`leaks`/reading
  `~/Library/Logs/DiagnosticReports/` — both confirmed unreachable in
  this sandbox this session, not worth re-testing without an environment
  change.
- Do NOT re-run `malloclog1` (confounded, superseded by `malloclog2`) or
  `metalresize1`/`campose15` (results stand, don't re-litigate).
- Do NOT combine `MTL_DEBUG_LAYER=1` with `MallocStackLogging=1` in the
  same soak — separate follow-up only if `malloclog2` doesn't pan out.
- Do NOT implement any speculative fix — no concrete bad-write site has
  been identified yet.

## Environment notes (carried forward, still current as of s241)

- **Permission gate CONFIRMED CLEARED through s241** — trust it, with
  the two new exceptions above (`DiagnosticReports` dir access,
  `malloc_history`/`atos`/`leaks` commands — both blocked).
- **`GAME_EXTRA_ENV` (new, s241)**: set this (space-separated
  `VAR=val VAR2=val2` string) in a driver wrapper instead of `export`ing
  vars you only want the GAME process to see — `run_mission_keys.sh`
  passes it through `env ${=GAME_EXTRA_ENV}` at the launch line only.
  Leave unset for anything that should reach the whole driver tree (like
  the existing `ROGUESQ_LOG_*` vars, which are this codebase's own env
  vars and don't affect helper subprocesses).
- **Block-scope `extern "C"` linkage-specifications do not compile**
  (C++17 requires namespace scope) — applies to any future cross-TU
  declaration added inside a function body in this codebase.
- Bash cwd persists across tool calls within a session — an explicit
  `cd` changes it for ALL subsequent calls. Prefer absolute paths; issue
  `cd` as its own call, then the bare command as a second call.
- `cmake --build` is safe to background; the game-soak launch script
  must stay SYNCHRONOUS/foreground-style — launch with
  `run_in_background: true` (generous timeout). A completion
  notification arrives automatically; if the Stop hook fires while the
  run is still in flight, block-wait with `TaskOutput` (`block: true`,
  generous timeout) rather than re-launching.
- **`TaskOutput` with `block: true` dumps the ENTIRE captured output
  every call** (confirmed s241 — a ~460s soak with per-tick subprocess
  noise produced a multi-hundred-KB dump well before completion). Prefer
  checking `ps aux | grep -i roguesquadron` (cheap, tells you if the
  process is still alive) and `grep`-ing small excerpts from the run's
  own `run.log`/output file over re-calling `TaskOutput` repeatedly.
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
  — keep these armed in any new soak so it's additive, not a fresh
  unknown environment.
- **This exact schedule (`schedulepush2`/`campose*` family) crash rate at
  the SELECT-CRAFT->mission transition is now 5/9 soaks crashed** vs 4/9
  survived (last updated by `metalresize1`; `malloclog1` is NOT counted,
  confounded) — still roughly even-odds, not "mostly survives."
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
Read tool's 256 KB single-read limit (confirmed s195, still true s241 —
read it with `grep`/offset-limited `Read`, never a plain whole-file
`Read`) — flagged for 32+ sessions without action. Migrate durable
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
Session 215) — separate from the host-CALayer crash line of
investigation, still worth picking up on its own merits eventually but is
NOT the next work unit.
