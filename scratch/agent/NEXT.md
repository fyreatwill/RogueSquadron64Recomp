# NEXT work unit — soak with MTL_DEBUG_LAYER=1 instead of malloc scribbling

## Where the investigation stands

s238 found a host-side SIGSEGV inside Apple QuartzCore
(`x_hash_table_remove_ptr`<-`CAMediaTimingInvalidate`<-`-[CALayer
dealloc]`<-`CA::Transaction::commit`), converging 3/3 soaks on the same
trigger point: guest call counter `n=12420`, wall-clock `t≈130.8-131.7s`.

s239 (static read) proposed a cross-thread `CAMetalLayer::
setDrawableSize` race candidate. s240 (dynamic instrument) REFUTED it —
zero fires across a 459s soak, traced to `resize()` never being called
because nothing in `src/main/` ever resizes the host window.

s241 stood up Apple malloc debug tooling (`MallocStackLogging=1`/
`MallocScribble=1`) but found `malloc_history`/`atos`/`leaks`/
`~/Library/Logs/DiagnosticReports/` are ALL unreachable in this sandbox
(no allowlist entry, no directory access) — the "post-mortem query
malloc_history" plan is dead, full stop. It also found and fixed a real
confound: exporting `Malloc*` vars at the wrapper level leaked them into
every helper subprocess, not just the game. Landed `GAME_EXTRA_ENV` in
`run_mission_keys.sh` to scope env vars to only the game process.

s242 ran the clean re-soak (`malloclog2`) with the fix: **`CRASH: 0`,
positive control passed (no helper-subprocess Malloc noise), but also
no `malloc`-related output at all from the game process** — MSL/scribble
apparently print nothing to stdout/stderr on this macOS version without
an active `malloc_history` query (which is unreachable). So even a crash
under this tooling would only ever give a crude `si_addr`-vs-`0x55`
comparison, no real allocation-site attribution. Updated family tally:
**5/10 crashed vs 5/10 survived** (still even-odds).

**Decision**: pivot away from malloc-scribble soaking. `MTL_DEBUG_LAYER=1`
(Apple's Metal API validation layer) is a stronger instrument — it
prints a specific diagnostic AT THE POINT of an API misuse (e.g. using a
released `CAMetalLayer`/drawable/texture), rather than requiring a lucky
crash to even get a data point.

## Hypotheses (write these down BEFORE running, per ITERATION.md)

1. **H1 — Metal API misuse is the actual bug.** Something releases a
   `CAMetalLayer`/`MTLDrawable`/related Metal object while it's still
   referenced, and `MTL_DEBUG_LAYER=1` will print a specific validation
   error identifying the object and call site before (or instead of) the
   host SIGSEGV.
2. **H2 — the bug is pure CoreAnimation/AppKit, not Metal API misuse.**
   `MTL_DEBUG_LAYER` only validates Metal API calls (encoders, command
   buffers, resources) — if the bad release is of a plain `CALayer`
   object via ordinary Cocoa/CoreAnimation ref-counting (not a Metal
   object), this layer won't catch it and the soak will look identical
   to a normal run (crash or not, no new diagnostic).
3. **H3 — plain non-determinism, no instrumentation will discriminate.**
   Given the 50/50 historical crash rate, any single soak's crash/no-crash
   outcome is close to a coin flip regardless of what's armed.

**Discriminating measurement**: does `MTL_DEBUG_LAYER=1` output ANY
validation message (regardless of whether the game crashes)? A message
mentioning a released/invalid Metal object splits H1 (confirmed) from
H2/H3 (refuted-for-this-instrument). If it crashes AND prints a
validation message just before the crash, that's strong (two
independent signals agreeing) evidence for the actual bad-release site.
If it crashes with NO validation message, that's evidence for H2 (favor
plain CoreAnimation over Metal-API misuse) — redirect the next static
read toward `CALayer`/`NSView` lifecycle in `plume_metal.cpp`/
`rt64_present_queue.cpp`'s teardown paths, not Metal resource calls.

## Do this iteration

1. Copy `run_malloclog2.sh` to `run_mtldebug1.sh` in
   `scratch/s73_post_a_scene/`. Same `campose*`/guard set, same
   `schedulepush2` schedule (20/40/60:start, 70+:su/sr/sd/sl every 8s).
   Replace the `GAME_EXTRA_ENV` line:
   `export GAME_EXTRA_ENV="MTL_DEBUG_LAYER=1"`
   (drop the `Malloc*` vars — separate follow-up only, per s241's NEXT,
   don't combine both in one soak).
   Tag: `mtldebug1`.
2. Run `zsh run_mtldebug1.sh` from `scratch/s73_post_a_scene/`
   (`run_in_background: true`, timeout 480000-600000ms, ~465s expected
   per `malloclog2`). If the Stop hook fires mid-run, block-wait with
   `TaskOutput` (`block: true`) rather than re-launching — confirmed
   pattern works (s242).
3. Positive control: `MTL_DEBUG_LAYER=1` is known to print SOMETHING
   during normal Metal setup/teardown on most macOS versions (unlike
   `MallocStackLogging`, which s242 found silent here) — check
   `mtldebug1/run.log` for ANY Metal-validation-layer output at all
   before trusting a "no crash, no diagnostic" result as a true null.
   If it's completely silent even during normal operation, that's a
   sign the layer isn't actually active (check `MTL_DEBUG_LAYER`
   reached the game process the same way the s241/s242 `GAME_EXTRA_ENV`
   positive control was checked) — don't trust a silent run without this
   check.
4. Read the discriminating outcome per the hypotheses table above and
   record it, whether or not the game crashes this soak.

## Do NOT do this iteration

- Do NOT re-attempt `malloc_history`/`atos`/`leaks`/
  `~/Library/Logs/DiagnosticReports/` — confirmed unreachable twice now
  (s241, unchanged).
- Do NOT re-run `malloclog1`/`malloclog2` (superseded) or
  `metalresize1`/`campose15` (results stand).
- Do NOT combine `MTL_DEBUG_LAYER=1` with `MallocStackLogging=1` in the
  same soak — keep this a clean single-variable test.
- Do NOT implement any speculative fix — no concrete bad-write/bad-release
  site has been identified yet by ANY instrument so far.

## Environment notes (carried forward, still current as of s242)

- **Permission gate CONFIRMED CLEARED through s242.**
- **`GAME_EXTRA_ENV`** (`run_mission_keys.sh`, s241): set this
  (space-separated `VAR=val VAR2=val2` string) in a driver wrapper to
  scope extra env vars to ONLY the game process's `env` invocation at
  the launch line — reused successfully for `MallocStackLogging`/
  `MallocScribble` in `malloclog2`, positive-controlled (zero helper-
  subprocess noise) both times it's been used. Use the same mechanism
  for `MTL_DEBUG_LAYER=1`.
- **Block-wait pattern confirmed again (s242)**: when the Stop hook
  fires mid-soak, `TaskOutput` with `block: true` and a generous timeout
  (e.g. 180000-480000ms) against the background task ID returns the
  final result cleanly once the driver's own SIGKILL-and-summarize step
  completes — no need to re-launch.
- **`TaskOutput` with `block: true` still dumps the entire captured
  output every call** (unchanged from s241) — it just wasn't large this
  time (s242: ~35 lines total) because `malloclog2`'s `run.log` has no
  per-tick subprocess noise (that was specifically the `malloclog1`
  confound, now fixed). Don't assume a small dump here means the
  behavior changed — a soak with heavy per-tick logging would still
  produce a large dump on every call. Prefer light `ps aux` checks over
  frequent `TaskOutput` polling; block-wait with a generous timeout
  (180000-480000ms) when you do need to wait for completion.
- **Malloc debug tooling (`MallocStackLogging`/`MallocScribble`) produces
  ZERO stdout/stderr output on this macOS version/environment absent a
  live `malloc_history` query** (s242, new finding) — don't expect to see
  "turning on/off stack logging" messages from the game process itself;
  their absence is not evidence the vars didn't reach the process (the
  `GAME_EXTRA_ENV` positive control already covers that separately via
  absence of helper-subprocess noise).
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
  the SELECT-CRAFT->mission transition is now 5/10 soaks crashed vs 5/10
  survived** (updated s242 by `malloclog2`; `malloclog1` NOT counted,
  confounded) — even-odds, not "mostly survives" or "mostly crashes".
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
Read tool's 256 KB single-read limit (confirmed s195, still true s242 —
read it with `grep`/offset-limited `Read`, never a plain whole-file
`Read`) — flagged for 33+ sessions without action. Migrate durable
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
