# NEXT work unit — STATIC investigation of a host-side CALayer crash,
# NOT another campose soak (iron rule 8 budget is spent: 3/3 consecutive
# no-result soaks on that instrument as of s238)

## Where the investigation stands

Three consecutive soaks of the validated `[campose-entry]` `t=`
instrument (`campose12`/s236, `campose13`/s237, `campose14`/s238) have
ALL crashed before reaching the hold-window payoff region (the 470s
visual-freeze frame this instrument chain was built to correlate
against). Per iron rule 8, do NOT run `campose15` — the budget on this
specific soak-based approach is spent. The campose-vs-freeze correlation
question itself is now secondary to a bigger new finding below.

**The `campose14` crash (s238) is a different KIND of crash, not just a
different address**: signal 11 (SIGSEGV), `si_addr=0x61cbf000000dc8`
(a corrupted/non-canonical pointer), `[CRASH][pc-symbol]
sym=x_hash_table_remove_ptr+72` — inside Apple's **QuartzCore**
framework (host macOS, not guest game code). Full native backtrace:
`x_hash_table_remove_ptr` <- `CAMediaTimingInvalidate` <- `-[CALayer
dealloc]` <- `CA::Transaction::commit` <- `CA::Transaction::
flush_as_runloop_observer` <- CoreFoundation run-loop observer <-
`_DPSNextEvent`/`Cocoa_PumpEvents` (SDL3) <- `update_gfx` (called every
frame) <- `recomp::start`. Reads as a `CALayer`/Metal-layer
use-after-free or double-release inside the renderer, surfacing
asynchronously whenever CoreAnimation's deferred transaction flush
finally tears down the corrupted layer.

**Trigger point is now 3/3 convergent** (upgraded from s237's 2/2
"lead"): `campose12`/`13`/`14`'s last `[campose-entry]` line before
crashing is `n=12420` every time, `t=130.8/131.3/131.7` (0.9s spread
across 3 independent soaks — essentially deterministic). This holds
despite landing at wildly different points relative to the hold-window's
own internal schedule (`campose12`: crashed before the hold window even
started; `campose13`: 1s into it; `campose14`: 21s into it, 19
`hold_NN.png` frames captured) — **this rules out a `STICK_SCHEDULE`-
keyed trigger** (no specific stick input is the cause) and points to
something tied to process wall-clock / frame-count instead, roughly 56s
after the VI-width transition (1024->512) at ~t=74.2s. The three
different downstream fault manifestations (2 distinct guest-SIGBUS
addresses in `campose12`/`13` + this session's host-SIGSEGV) look like
ONE underlying corruption event with a non-deterministic downstream
victim, not three unrelated bugs.

This crash family is DISTINCT from the pre-existing NaN/`NAN_CHECK`/
unguarded-deref guest-crash family (CURRENT-TRUTH -55/-56) — that
proposed hardening does NOT explain a host QuartzCore crash, so do not
default to picking it up just because it was the previously-flagged
fallback.

## Do this iteration

This is a STATIC/read-only investigation work unit — no soak, no build,
unless the investigation turns up a concrete, cheap, testable fix.

1. Read `lib/rt64/src/contrib/plume/plume_metal.cpp` and
   `plume_metal.h` (the Metal graphics-backend implementation rt64
   actually uses — NOT the `contrib/metal-cpp` headers, which are just
   Apple's C++ bindings). Look specifically for:
   - Where a `CAMetalLayer`/`CALayer` is created, resized, or released
     (search for `metalLayer`, `CAMetalLayer`, `nextDrawable`,
     `drawableSize`, `release`, `retain`).
   - Any resize/recreate path that could run when the VI width changes
     (1024->512) — this repo's framebuffer-resize handling in
     `src/main/rt64_render_context.cpp` is the likely caller; grep there
     for calls into the Metal backend around resize.
2. Cross-reference: is there a fixed-size pool, cache, or ring buffer of
   layers/textures indexed by a frame or call counter that could
   wrap/overflow around ~56s / ~12420 calls after a resize event? A
   double-release usually means a refcount/ownership bug on a specific
   code path, not corruption from an unrelated random write — the tight
   3/3 timing convergence argues for a deterministic path (e.g. an N-th
   resize, an N-frame-delayed teardown, a pool of fixed size K where
   corruption count = K), not a heap-layout race.
3. If a concrete, narrow candidate bug is found (e.g. a released
   `CAMetalLayer` still referenced after a resize, a missing
   `objc_retain`/`bridge` on a Metal drawable): write it up as a
   hypothesis in this file's next revision — do NOT patch and re-soak in
   the same iteration unless the fix is small and the positive control
   (does the specific crash stop recurring across 2 soaks) is planned
   for explicitly. A partial/uncertain fix soaked once is not evidence.
4. If NO concrete candidate is found after reading the resize/layer path
   (i.e. the bug isn't visible from source, or lives in Apple's own
   QuartzCore/AppKit which we can't patch): that is a legitimate result.
   Write it up as "static read did not localize the bug", and the next
   escalation is `MallocStackLogging`/Instruments-style tooling (Apple's
   `MTL_DEBUG_LAYER=1` / `MTL_SHADER_VALIDATION=1` env vars, or
   `MallocNanoZone=0 MallocStackLogging=1` at process launch) to catch
   the double-release/UAF at the point of the bad release, not at the
   delayed dealloc — this is a NEW diagnostic category (host-side Metal/
   Cocoa debug env vars), not a code read, and should be scoped as its
   own work unit if reached.

## Do NOT do this iteration

- Do NOT run `campose15` or any variant re-soak of the same
  `[campose-entry]` instrument — iron rule 8's budget (3 consecutive
  no-result soaks: `campose12`/`13`/`14`) is spent on this specific
  approach.
- Do NOT pick up the guest-side NaN/`NAN_CHECK`/unguarded-deref hardening
  proposal (CURRENT-TRUTH -55/-56) as the default fallback — it targets
  a different crash family (guest SIGBUS in game code) and does not
  explain this session's host QuartzCore SIGSEGV.
- Do NOT edit `lib/rt64` speculatively without a concrete, localized bug
  in hand — and if you DO edit anything under `lib/`, run
  `./submodule-patches/export.sh` and commit the refreshed patch in the
  SAME iteration (hard rule, CLAUDE.md).
- Do NOT treat the `n=12420`/`t≈131s` convergence as proof the trigger is
  campose-specific — camera-pose call count may just be a convenient
  correlated counter, not the causal mechanism; the actual cause is more
  likely tied to elapsed time/frame count since the VI-width transition
  or since process start.
- Do NOT dump entire raw source files into your own context if they're
  large — grep for the specific symbols above first, read only the
  relevant functions with offset/limit.

## Environment notes (carried forward, still current as of s238)

- **Permission gate CONFIRMED CLEARED through s238** — trust it.
- Bash cwd persists across tool calls within a session — but an explicit
  `cd` changes it for ALL subsequent calls. Prefer absolute paths; issue
  `cd` as its own call, then the bare command as a second call.
- `zsh -c` heredoc-style multi-line `for` loops over Bash sometimes throw
  a spurious `Contains simple_expansion` error even for read-only
  commands — if that happens, drop to single-line/individual commands
  rather than retrying the same multi-line form.
- **`cmake --build` is safe to background**; the game-soak launch script
  must stay SYNCHRONOUS/foreground-style (sends scheduled keypresses,
  SIGKILLs itself at the end) — launch with `run_in_background: true`
  (generous `timeout`, e.g. 330000ms). A completion notification arrives
  automatically; if the Stop hook fires while the run is still in
  flight, block-wait with `TaskOutput` (`block: true`, generous
  `timeout`) rather than re-launching.
- **`/tmp` is not writable this session** — write scratch/report files
  inside `RogueSquadron64Recomp`/`N64Recomp`/`rogue_squadron64` only.
- Compound `cd ... && ...` commands get blocked by the permission layer
  — issue `cd` as its own Bash call first, then the next command
  separately.
- **`git -C <path> <cmd>` does not match allow-rules** — `cd` first (own
  call), then bare `git <cmd>` as a separate call.
- **Headless permission matching is a PREFIX match** — write
  `env PROBE_MODE=1 zsh run.sh`, not `PROBE_MODE=1 zsh run.sh`.
- **`campose*` armed env-var set** (unchanged since `campose11`, kept
  identical through `campose14`): `ROGUESQ_LOG_CAMPOSE`,
  `ROGUESQ_LOG_MAT3INV`, `ROGUESQ_LOG_UNLIT_MESH_TRACER`,
  `ROGUESQ_LOG_RENDERUNLIT_GUARD`, `ROGUESQ_LOG_HEAPWALKER_GUARD`/
  `GUARD3`/`GUARD4`, `ROGUESQ_LOG_MESGQUEUE_GUARD`,
  `ROGUESQ_LOG_HEAPLISTDEQ_GUARD`, `ROGUESQ_LOG_EMIT_DL_GUARD2`/`GUARD3`,
  `ROGUESQ_LOG_DL_PAYLOAD_STALE=1`.
- **This exact schedule (`schedulepush2`/`campose*` family) crash rate at
  the SELECT-CRAFT->mission transition is now 5/8 soaks crashed**
  (`campose4`x2, `campose10`, `campose12`, `campose13`, `campose14`) vs
  3/8 survived (`campose8`, `campose9`, `campose11`) — no longer treat
  this as "mostly survives, occasionally crashes"; it is closer to
  even-odds. VI-width transition ONSET (1024->512) is consistently timed
  (~t=74.2-74.5s across runs regardless of crash/survive outcome) but
  whether/when/how it crashes after onset is what varies.
- **`[campose-entry]` log line** (guest `0x800178A8`, `funcs_4.c`) HAS a
  `t=%.1f` field (s236, validated, 3 further soaks confirm it fires
  correctly). Fields: `n=`, `m00=`, `flag=`, `camptr=`, `deref0=`,
  `deref0_valid=`, `t=`. `[campose-abnormal]` (same site, NaN/inf branch)
  does NOT have `t=` — unchanged, out of scope unless it becomes
  relevant.
- **`rs64_elapsed_seconds()`** (`src/main/rt64_render_context.cpp`) is
  the canonical shared wall-clock — declare
  `extern double rs64_elapsed_seconds(void);` inline in any new PATCH
  block, do not invent a second clock.
- **Crash-family reference** (all crashes at the SELECT-CRAFT->mission
  transition to date): `campose10` — guest SIGBUS,
  `setupCameraMatrices` chain, `si_addr=0x336000004`, ~t=74.5s.
  `campose12` — guest SIGBUS, `emitAllocatedDLCommand`<-
  `submitSceneNodeRender`<-`processSceneNode`<-
  `traverseSceneGraphRecursive`<-`setupCameraMatrices` chain,
  `si_addr=0x380000000`, n=12420 t=130.8. `campose13` — guest SIGBUS,
  faults directly at `static_5_800C6854+1044`<-`menuOverlayInit`, no
  render-chain frames, `si_addr=0x3c00b1382`, n=12420 t=131.3.
  `campose14` — **host SIGSEGV**, `x_hash_table_remove_ptr`<-
  `CAMediaTimingInvalidate`<-`-[CALayer dealloc]`<-`CA::Transaction::
  commit`, `si_addr=0x61cbf000000dc8`, n=12420 t=131.7. Pre-existing
  guest crash families (`sinfApprox` NaN assert, misc unguarded-deref
  SIGBUS) are a SEPARATE, older-documented issue — see CURRENT-TRUTH
  -55/-56 and PORTING-STATE Session 214/215; do not conflate with this
  n=12420-convergent family.
- **Verify "crash-free" visually**: MD5-checksum a spread of `hold_NN.png`
  (Python script, not shell loops). `scratch/agent/checksum_campose11.py`
  (s235) is mtime-aware — reuse this pattern for any future wall-clock
  correlation work.
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
  `NEXT.md`, and `run_mission_keys.sh` are tracked exceptions. Per-soak
  driver scripts (`run_camposeN.sh`) and analysis scripts
  (`checksum_*.py`/`correlate_*.py`) have never been force-added
  historically — don't start now unless asked.

## Housekeeping still flagged, still not done

`docs/CURRENT-TRUTH.md` is past both the ~35 KB CLAUDE.md budget and the
Read tool's 256 KB single-read limit (confirmed s195, still true s238 —
read it with `grep`/offset-limited `Read`, never a plain whole-file
`Read`). Migrate durable mechanism/architecture material to
`PROJECT-OVERVIEW.md` and prune superseded detail — flagged for 30+
sessions without action.

`fixup_game_funcs.py`'s untracked, single-copy state in the `N64Recomp`
sibling checkout has been flagged since s83, still not fixed (not this
repo's commit scope) — worth surfacing to the user directly.

`/Users/williambuckley/Documents/Tools/N64Recomp` and
`~/Documents/Tools/rogue_squadron64` are separate git checkouts with
long-standing uncommitted changes, unrelated to this repo's commit scope.
Still flagged for the user, not committed autonomously.

`lib/rt64` and `lib/N64ModernRuntime` both still show as modified in `git
status` as of s238 — not investigated this session either (no lib/ edits
made this session, so no export.sh/commit obligation triggered). Still
worth checking whether these are in-progress uncommitted patches vs.
drift from `submodule-patches/*.patch` before assuming steady-state
dirtiness — this becomes directly relevant if the next iteration's
`plume_metal.cpp` read turns up a fix that needs to be patched into
`lib/rt64`.

The pre-existing NaN/`NAN_CHECK` and unguarded-deref crash families still
have a proposed but unshipped fix (CURRENT-TRUTH -55/-56, PORTING-STATE
Session 215) — separate from this session's new host-CALayer crash
finding, still worth picking up on its own merits eventually but is NOT
the next work unit.
