# NEXT work unit — stand up Apple's own allocation/layer debug tooling
# (MallocNanoZone=0 MallocStackLogging=1 / MTL_DEBUG_LAYER=1) against the
# s238 host-side QuartzCore SIGSEGV, now that TWO static/dynamic candidate
# searches (s239, s240) have both come up empty for a concrete write site.

## Where the investigation stands

s238 found a host-side SIGSEGV inside Apple QuartzCore
(`x_hash_table_remove_ptr`<-`CAMediaTimingInvalidate`<-`-[CALayer
dealloc]`<-`CA::Transaction::commit`), converging 3/3 soaks
(`campose12`/`13`/`14`) on the same trigger point: guest call counter
`n=12420`, wall-clock `t≈130.8-131.7s`.

s239 (static read of `plume_metal.cpp`/`rt64_present_queue.cpp`) proposed
ONE candidate: a cross-thread `CAMetalLayer::setDrawableSize` race in
`MetalSwapChain::resize()`, called from the `PresentQueue` background
thread, not the main thread that owns `CA::Transaction::commit`.

s240 instrumented `resize()`'s drawable-size-change branch
(`[metal-resize-entry]`, `plume_metal.cpp:2092-2096`) and soaked it
(`metalresize1`): **zero fires in 459s**, including a run that survived
the historical crash trigger point entirely (`CRASH: 0`). Traced why:
`needsResize()` (`plume_metal.cpp:2105-2109`) gates `resize()`, and
nothing in `src/main/` ever resizes the host window, so `resize()` is
never invoked in normal operation. **This REFUTES the s239 hypothesis**
with two independent lines of evidence (static + dynamic) — full detail
PORTING-STATE Session 240, CURRENT-TRUTH -81.

That closes the only concrete candidate either static read has found.
Continuing to hunt for a 2nd/3rd candidate site by eyeballing
`plume_metal.cpp` is low information value now — two passes over the
same ~2000-line file have found one candidate and it was wrong. The
higher-value move is to stop guessing WHERE the corruption happens and
instead let Apple's own tooling tell us, at the point it actually
occurs.

## Do this iteration — stand up the tooling, do NOT expect to fix anything yet

This is a TOOLING + ONE SOAK work unit. The goal is a captured stack
trace at the actual over-release/bad-write, not a patch.

1. **Read `run_mission_keys.sh` and the launch line
   (`./RogueSquadron64Recomp > "$OUTDIR/run.log" 2>&1 &`,
   `scratch/s73_post_a_scene/run_mission_keys.sh:27`)** — the env vars
   below need to be exported in the driver script BEFORE that launch
   line, same pattern as the existing `ROGUESQ_LOG_*` exports.
2. Add to a new copy of the driver
   (`run_malloclog1.sh`, copied from `run_metalresize1.sh` — do NOT
   overwrite `run_metalresize1.sh`, that instrument/result stays as
   ground truth):
   - `export MallocNanoZone=0`
   - `export MallocStackLogging=1`
   - Consider `MallocScribble=1` too (fills freed memory with a
     recognizable pattern, `0x55`, making use-after-free reads more
     likely to crash immediately/visibly instead of silently reading
     stale-but-plausible data) — cheap to add, same soak, no extra cost.
   - Do NOT add `MTL_DEBUG_LAYER=1` in the SAME soak as
     `MallocStackLogging=1` — Metal's own validation layer is expensive
     and changes GPU-side timing/scheduling enough that it could mask or
     shift the bug (the crash is already known to be timing-sensitive,
     iron rule 2 territory). Run `MallocStackLogging` alone first; only
     add `MTL_DEBUG_LAYER` as a SEPARATE follow-up soak if the malloc
     approach doesn't pan out.
3. **Positive control, in the same run**: `MallocStackLogging=1` alone
   does not crash on its own — verify it's actually active by checking
   for its known startup behavior (it prints nothing by default, but
   `leaks`/`malloc_history` can query a live PID). If unsure how to
   positive-control this cheaply, the crash itself IS the control: if
   the process crashes with `MallocStackLogging=1` active, run
   `atos`/`malloc_history <pid> <bad-address>` (or capture the crash
   dump path from `Console`/`~/Library/Logs/DiagnosticReports/`) on the
   captured `si_addr` BEFORE the process's memory is torn down —
   `MallocStackLogging` data lives in the process while it's alive AND
   in a `.malloc_history`/crash-report addendum after a crash on macOS,
   depending on OS version; check which applies THIS macOS version
   before assuming the workflow.
4. Run ONE soak with the same schedule/env as `metalresize1` (full
   `campose*`/guard set stays armed) plus the new malloc env vars.
5. **Discriminating outcome**: does this soak crash at all (given the
   non-determinism, it may not — that's a null result requiring a
   re-soak per iron rule 8's 3-strikes budget, not evidence of anything
   yet)? If it crashes, does `MallocStackLogging`/`malloc_history`
   produce an allocation-site stack trace for the faulting address? If
   yes, that stack trace names the actual bug — evaluate it directly
   rather than continuing to guess.

## Do NOT do this iteration

- Do NOT re-run `campose15` or touch the old `[campose-entry]` instrument
  (iron rule 8 budget spent, unchanged).
- Do NOT re-run `metalresize1` — that result stands (0 fires, hypothesis
  refuted). Do not re-litigate it without new information.
- Do NOT combine `MallocStackLogging=1` and `MTL_DEBUG_LAYER=1` in the
  same soak (see above — confounds timing-sensitive results).
- Do NOT implement any speculative fix — no concrete bad-write site has
  been identified yet; there is nothing to fix.

## Environment notes (carried forward, still current as of s240)

- **Permission gate CONFIRMED CLEARED through s240** — trust it.
- **Block-scope `extern "C"` linkage-specifications do not compile**
  (C++17 requires namespace scope) — new finding this session, applies
  to any future cross-TU declaration added inside a function body in
  this codebase (`plume_metal.cpp` or elsewhere in `lib/rt64`).
- Bash cwd persists across tool calls within a session — an explicit
  `cd` changes it for ALL subsequent calls. Prefer absolute paths; issue
  `cd` as its own call, then the bare command as a second call.
- `cmake --build` is safe to background; the game-soak launch script
  must stay SYNCHRONOUS/foreground-style — launch with
  `run_in_background: true` (generous timeout, e.g. 330000-600000ms). A
  completion notification arrives automatically; if the Stop hook fires
  while the run is still in flight, block-wait with `TaskOutput`
  (`block: true`, generous timeout) rather than re-launching.
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
  — keep these armed in the new soak so it's additive, not a fresh
  unknown environment.
- **This exact schedule (`schedulepush2`/`campose*` family) crash rate at
  the SELECT-CRAFT->mission transition is now 5/9 soaks crashed** vs 4/9
  survived (updated by `metalresize1`'s clean run) — still roughly
  even-odds, not "mostly survives."
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
Read tool's 256 KB single-read limit (confirmed s195, still true s240 —
read it with `grep`/offset-limited `Read`, never a plain whole-file
`Read`) — now larger still after s240's addition. Migrate durable
mechanism/architecture material to `PROJECT-OVERVIEW.md` and prune
superseded detail — flagged for 31+ sessions without action.

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
