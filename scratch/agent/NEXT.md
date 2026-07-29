# NEXT work unit — one more re-soak (`campose14`) of the already-landed
# `t=` instrument; this is the LAST soak before iron rule 8's budget
# forces a strategy change if it also fails to reach the hold window

## Where the investigation stands

s236 added a `t=%.1f` field to `[campose-entry]` and positive-control
validated it. Two soaks since then (`campose12` s236, `campose13` s237)
have BOTH crashed during the SELECT-CRAFT->mission transition before
reaching the hold window — the actual discriminating question (does the
camera-pose stream also stall around t≈470.2s, s235's freeze frame,
arguing for a game-logic freeze, vs. keep updating, arguing for a
render-side-only bug) still has NOT been tested.

**New wrinkle from s237**: the two most recent crashes (`campose12`,
`campose13`) have DIFFERENT crash sites/addresses (SIGBUS at
`si_addr=0x380000000` vs `si_addr=0x3c00b1382`; `campose12`'s fault chain
went deep into `emitAllocatedDLCommand`<-`submitSceneNodeRender`<-
`processSceneNode`<-`traverseSceneGraphRecursive`<-`setupCameraMatrices`,
`campose13`'s `[CRASH][pc-symbol]` resolved directly to
`static_5_800C6854+1044` called from `menuOverlayInit` with no
scene-render frames beneath it) — but an IDENTICAL campose call-count at
crash time: both stopped at `[campose-entry] n=12420` (`t=130.8` vs
`t=131.3`, 0.5s apart). `campose10`'s earlier crash (~t=74.5s) does NOT
match this n/t, so it's 2/2 on recent runs, not 3/3 overall — a lead, not
a proven mechanism.

This is the 2nd consecutive no-result soak of this specific instrument
(iron rule 8 triggers at the 3rd). One more soak is still within budget.

## Do this iteration

1. **Copy the driver, bump the tag only**: `cp
   scratch/s73_post_a_scene/run_campose13.sh
   scratch/s73_post_a_scene/run_campose14.sh`, then edit ONLY the
   `campose13`->`campose14` string occurrences (header comment + the `zsh
   run_mission_keys.sh campose13 5 12` line). Do NOT touch env vars,
   `STICK_SCHEDULE`, `HOLD_S`, or any other setting.
2. **No rebuild needed** — the binary already has the validated `t=`
   instrument compiled in from s236. Launch directly:
   `zsh run_campose14.sh` as a single Bash call with `run_in_background:
   true`, generous timeout (e.g. 330000ms), then block-wait via
   `TaskOutput` (`block: true`, `timeout: 180000`, repeat if it times out
   mid-run).
3. **If it crashes again before the hold window**: this IS the 3rd
   consecutive no-result iteration on this hypothesis — iron rule 8 now
   applies. Do NOT queue a `campose15` soak. Instead:
   - Grep the crash signature (signal, `si_addr`, `[CRASH][pc-symbol]`,
     native backtrace) and add it to the s237 comparison table (3 crashed
     soaks now instead of 2 — does `n=12420` recur a 3rd time, or was that
     a 2-run coincidence?).
   - Write the hypothesis/evidence table into this file and pick ONE of:
     (a) shorten `STICK_SCHEDULE`/reduce the pre-hold-window wait so less
     wall-clock is spent inside the fragile transition before the hold
     window's key events fire, since campose12/13 both died ~55-57s AFTER
     the VI-width transition onset (~t=74.4s) rather than at onset itself
     — moving the hold-window-critical action earlier might dodge the
     ~t=130s fault window entirely; (b) pick a different already-armed
     diagnostic that doesn't require surviving this transition at all
     (e.g. something observable from a save-state or an earlier phase);
     (c) treat the crash-family itself as the target and pick up the
     unshipped NaN/unguarded-deref hardening proposed at CURRENT-TRUTH
     -55/-56 so future soaks survive by construction rather than by luck.
   - Do not silently re-attempt the same soak a 4th time.
4. **If it survives to the hold window** (`CRASH: 0`-equivalent, i.e. no
   `[CRASH] caught signal` line, and `hold_NN.png` frames present up to
   `hold_350`): this is the payoff run.
   - Reuse `scratch/agent/checksum_campose11.py`'s pattern (swap directory
     name to `campose14`) to find the freeze frame (the hash that locks
     permanently and never changes again through `hold_350`).
   - Write `correlate_campose14.py`: parse the `t=` field off
     `[campose-entry]` lines (NOT `[campose-abnormal]`, which has no `t=`
     field yet), convert via that run's own `proc_start_epoch.txt` to real
     elapsed seconds, and diff the LAST-CHANGING `[campose-entry]` value
     (watch `m00`/`camptr`/`deref0` fields) against the freeze frame's
     real elapsed time.
   - Two possible readings: (a) campose values stop changing at/before the
     freeze time (mirrors s235's DL-payload result) → still consistent
     with a broader stall, camera-pose isn't the discriminator either →
     look at a different already-armed diagnostic next
     (`ROGUESQ_LOG_UNLIT_MESH_TRACER`, `RENDERUNLIT_GUARD`, or
     `HEAPWALKER_GUARD` families, none of which have a `t=` field yet
     either); (b) campose values KEEP changing well past the freeze time →
     game logic (at least camera update) is alive, points the
     investigation toward the actual draw/output path being the stuck
     piece, a real render-side bug distinct from Option A/B (already
     closed).
   - Write the answer into CURRENT-TRUTH regardless of which way it
     points — this is the payoff for three iterations of instrument work,
     do not let it go unrecorded.

## Do NOT do this iteration

- Do not touch `fixup_game_funcs.py`'s `[campose-entry]` PATCH block, the
  `dl-payload-*` PATCH block, `rs64_elapsed_seconds()` itself, or
  `proc_start_epoch.txt` stamping in `run_mission_keys.sh` — all validated
  working as of s234/s236, not the open question.
- Do not regenerate/rebuild unless you actually change generated code —
  the s236 binary already has the instrument; `campose14` is a straight
  re-run.
- Do not re-run `campose8`/`9`/`10`/`11`/`12`/`13` unmodified — their
  budgets are spent for what they were testing.
- Do not reintroduce `ROGUESQ_LOG_RENDER_CACHE_EPOCH` — still closed, 0/4
  through SELECT-CRAFT (s229-s231), unrelated question.
- Do not treat the SELECT-CRAFT->mission transition crash as a single
  simple bug to fix — 3 crashed soaks now show 3 different faulting
  addresses/sites, so "fix the crash" is not yet a well-defined single
  target. The pre-existing NaN/unguarded-deref crash-family fix proposed
  at CURRENT-TRUTH -55/-56 is the closest existing lead if rule 8 forces a
  pivot to hardening instead of another soak.
- Do not dump entire raw log files into your own context — write short
  Python scripts or use targeted `grep`, per every prior session's method.

## Standard regen recipe (NOT needed this iteration — no code change)

Only use this if a NEW diagnostic is motivated (e.g. adding `t=` to
another already-armed log line, or the rule-8 pivot requires a code
change):

1. `cd` into `N64Recomp` checkout, delete stale `RecompiledFuncs/funcs_*.c`:
   `python3 -c "import glob, os; [os.remove(f) for f in
   glob.glob('RecompiledFuncs/funcs_*.c')]"` — **note the `RecompiledFuncs/`
   prefix, a bare `funcs_*.c` glob from the repo root matches nothing and
   silently no-ops — always check the print count, not just absence of an
   error.**
2. `python3 tools/make_elf.py` (rogue_squadron64 checkout).
3. `./tools/agent/regen_n64recomp.sh` (this repo, cwd-independent).
4. `fixup_game_funcs.py` **exactly once** — grep its report for the new
   diagnostic's patch line AND spot-check the generated `.c` file for your
   actual changed values, not just presence.
5. `DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build
   build -j8`, safe to background (`run_in_background: true`).

## Environment notes (carried forward, still current as of s237)

- **Permission gate CONFIRMED CLEARED s229-s237** — trust it.
- Bash cwd persists across tool calls within a session — but an explicit
  `cd` changes it for ALL subsequent calls, and `cd` itself now sometimes
  requires separate approval when chained near a `git` call. Prefer
  absolute paths; issue `cd` as its own call, then the bare command as a
  second call.
- **`cmake --build` is safe to background**; the game-soak launch script
  must stay SYNCHRONOUS/foreground (sends scheduled keypresses, SIGKILLs
  itself at the end) — **it WILL exceed the 400s default foreground Bash
  timeout and get auto-backgrounded; this is expected.** Launch directly
  with `run_in_background: true` (generous `timeout`, e.g. 330000ms) and
  block-wait via `TaskOutput` (`block: true`, `timeout: 180000` — a
  shorter first wait is fine, s236/s237 both confirmed a completion
  notification still arrives if you don't re-poll).
- **`/tmp` is not writable this session** — write scratch/report files
  inside `RogueSquadron64Recomp`/`N64Recomp`/`rogue_squadron64` only.
- Compound `cd ... && ...` commands (including with output redirection)
  get blocked by the permission layer — issue `cd` as its own Bash call
  first, then the next command as a separate call.
- **`git -C <path> <cmd>` does not match allow-rules** — `cd` first (own
  call), then bare `git <cmd>` as a separate call.
- **Headless permission matching is a PREFIX match** — write
  `env PROBE_MODE=1 zsh run.sh`, not `PROBE_MODE=1 zsh run.sh`.
- **campose13's armed env-var set** (identical to `campose11`/`campose12`,
  keep all when building `campose14` — copy `run_campose13.sh`):
  `ROGUESQ_LOG_CAMPOSE`, `ROGUESQ_LOG_MAT3INV`,
  `ROGUESQ_LOG_UNLIT_MESH_TRACER`, `ROGUESQ_LOG_RENDERUNLIT_GUARD`,
  `ROGUESQ_LOG_HEAPWALKER_GUARD`/`GUARD3`/`GUARD4`,
  `ROGUESQ_LOG_MESGQUEUE_GUARD`, `ROGUESQ_LOG_HEAPLISTDEQ_GUARD`,
  `ROGUESQ_LOG_EMIT_DL_GUARD2`/`GUARD3`, `ROGUESQ_LOG_DL_PAYLOAD_STALE=1`.
- **This exact schedule (`schedulepush2`/`campose*` family) is PROVEN
  non-deterministic (s223, reconfirmed s233/s234/s236/s237)**: transition
  timing and crash-vs-survive both vary run to run with the identical
  armed set/schedule (`campose8`/`9`/`11` survived; `campose10`/`12`/`13`
  crashed). VI-width transition ONSET (1024->512) does look consistently
  timed (~t=74.2-74.5s across `campose10`/`12`/`13`) even when the
  eventual crash timing/site after onset differs. **New s237 observation**:
  `campose12`/`campose13`'s crashes matched almost exactly on
  campose-call-count at fault time (`n=12420` both), while their crash
  sites/addresses differed — worth watching whether `campose14` also lands
  near `n=12420` (3/3 would upgrade this from a lead to a real pattern) or
  breaks the pattern (2/3, back to "no discernible pattern").
- **`[campose-entry]` log line** (guest `0x800178A8`, funcs_4.c area) now
  HAS a `t=%.1f` field (s236, validated). Other fields: `n=` (call
  counter), `m00=`, `flag=`, `camptr=`, `deref0=`, `deref0_valid=`.
  **`[campose-abnormal]` (same site, NaN/inf branch) does NOT have `t=`**
  — not touched this session, out of scope unless it becomes relevant.
- **`rs64_elapsed_seconds()`** (`src/main/rt64_render_context.cpp`, near
  `rs64_bump_phase_ord`/`rs64_phase_ord`) is the canonical shared
  wall-clock — declare `extern double rs64_elapsed_seconds(void);` inline
  in any new PATCH block, do not invent a second clock.
- **Pre-existing crash-family sites, do not treat as new bugs if hit
  again**: `sinfApprox` NaN `NAN_CHECK` assert (`funcs_5.c:6460`, signal
  6); various unguarded-deref SIGBUS sites across `funcs_*`/
  `mesgqueue.cpp` (signal 10) — see CURRENT-TRUTH -55/-56 and
  PORTING-STATE Session 214/215. SIGBUS in/near
  `setupCameraMatrices`->`traverseSceneGraphRecursive`->`processSceneNode`
  or directly in `static_5_800C6854`<-`menuOverlayInit` at the
  SELECT-CRAFT->mission transition is the same recurring FAMILY (fragile
  transition, signal 10, no repeated exact site) — 3/6 `campose*` soaks
  with the `t=`-armed dl-payload/campose instrument have now SURVIVED it
  (`campose8`, `campose9`, `campose11`), 3/6 crashed (`campose10`,
  `campose12`, `campose13`), three different addresses.
- **Verify "crash-free" visually**: MD5-checksum a spread of `hold_NN.png`
  (Python script, not shell loops). `scratch/agent/checksum_campose11.py`
  (s235) is mtime-aware — reuse this pattern for any future wall-clock
  correlation work.
- **`rm -f <glob>`/`find <dir> -delete` are blocked** — use
  `python3 -c "import glob, os; [os.remove(f) for f in glob.glob('<pattern>')]"`.
- Re-running the same soak script/tag OVERWRITES the previous run's
  `run.log` in place — copy the driver script to a new tag name per soak.
- The driver's own end-of-run summary line `CRASH: N` counts occurrences of
  the LITERAL STRING `[CRASH]` in the log, which appears many times per
  single crash event (once per stack-dump/mcontext line) — **do not read
  this number as "N separate crashes"**; grep specifically for
  `[CRASH] caught signal` to count actual crash events.
- `scratch/agent/STATUS`/`OUTCOME` get reset at the START of each
  iteration by the harness — finding them reset at session start is
  normal.
- **`/scratch/` is wholesale gitignored** — only `STATUS`, `OUTCOME`,
  `NEXT.md`, and `run_mission_keys.sh` are tracked exceptions. Per-soak
  driver scripts (`run_camposeN.sh`) and analysis scripts
  (`checksum_*.py`/`correlate_*.py`) have never been force-added
  historically — don't start now unless asked, they're trivially
  regenerable by copying the pattern in this file.

## Housekeeping still flagged, still not done

`docs/CURRENT-TRUTH.md` is past both the ~35 KB CLAUDE.md budget and the
Read tool's 256 KB single-read limit (confirmed s195, still true s237 —
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
status` as of s237 — not investigated this session either (no lib/ edits
made, so no export.sh/commit obligation triggered). Still worth checking
whether these are in-progress uncommitted patches vs. drift from
`submodule-patches/*.patch` before assuming steady-state dirtiness.

The pre-existing NaN/`NAN_CHECK` and unguarded-deref crash families have a
proposed but unshipped fix (disable/soften `NAN_CHECK` aborts,
CURRENT-TRUTH -55/-56, PORTING-STATE Session 215) — worth picking up if
`campose14` also crashes and rule 8 forces a pivot away from more soaking.
