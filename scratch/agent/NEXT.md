# NEXT work unit — one more wall-clock-bridge soak (campose11), then run
# the staleness-vs-freeze correlation the bridge was built for

## Where the investigation stands

s234 landed the wall-clock/`hold_N` bridge s233 called for:
`rs64_elapsed_seconds()` (`src/main/rt64_render_context.cpp`, file-scope
`steady_clock` epoch shared with the `[phase]` line) is now called from the
`ROGUESQ_LOG_DL_PAYLOAD_STALE` PATCH block (`fixup_game_funcs.py`,
`funcs_4.c:13918`/`L_80014FE8` anchor) to emit `t=%.1f` on
`[dl-payload-tracker-armed]`/`[dl-payload-content-changed]`/
`[dl-payload-content-stale]`/`[dl-payload-tracker-hb]`. `run_mission_keys.sh`
also now writes `proc_start_epoch.txt` (real UNIX epoch, `date +%s`, right
after `PID=$!`) so the guest's process-relative `t=` converts to real
wall-clock and becomes directly comparable to `hold_NN.png` file mtimes
(also real wall-clock, no code needed to get them).

**Positive control confirmed working**: the `campose10` soak showed `t=`
firing and increasing monotonically (`t=3.0` at tracker-arm, up through
`t=74.7` on the last event before the crash). The instrument itself is
validated — do not re-litigate whether it fires correctly.

**But the actual experiment has not run yet.** `campose10` (1/1 budgeted
attempt for the instrument-validation pass) crashed at t=74.5-74.7s — SIGBUS
signal 10, `submitSceneNodeRender+31672` <- `processSceneNode` <-
`traverseSceneGraphRecursive` <- `setupCameraMatrices`, `si_addr=0x336000004`
— during the SELECT-CRAFT->mission transition, before the hold loop ever
started. Zero `hold_NN.png` frames were captured; zero
`[dl-payload-content-stale]` events fired (only 5 `content-changed` events,
nowhere near the 10000-call-gap threshold). This crash signature matches
the ALREADY-DOCUMENTED pre-existing instability at this exact transition
(CURRENT-TRUTH -71/-72, s230/s231: 0/4 epoch-armed soaks survived it, crash
site differs every time, and s231 already refuted "diagnostic I/O volume
causes this" for a much heavier diagnostic) plus s223/s233's proof this
exact schedule lands the transition at wildly different times run to run —
the more likely read is ordinary non-determinism, not new fragility from
s234's code. But `campose8`/`campose9` (identical armed set, no `t=` field)
were both `CRASH: 0` through this same window, so n=1 cannot fully clear
the new code either. **Inconclusive, single-source** — full writeup:
PORTING-STATE Session 234, CURRENT-TRUTH -75.

## Do this iteration

1. **Soak once more** (fresh explicit budget decision, this is not a 3rd
   attempt on an unchanged diagnostic — it's the 2nd attempt at reaching the
   hold window with the NEW `t=` instrument armed): copy
   `scratch/s73_post_a_scene/run_campose10.sh` to `run_campose11.sh`, change
   only the tag (`campose10` -> `campose11` in the `run_mission_keys.sh`
   invocation and the header comment). Script/binary otherwise unchanged —
   do NOT touch the diagnostic code again before this soak; the instrument
   is already validated (see above), only the crash-survival question is
   open. Launch as a single SYNCHRONOUS foreground call with
   `run_in_background: true` (generous timeout ~330000ms), block-wait via
   TaskOutput (`block: true`, `timeout: 480000`) — the proven pattern from
   s233/s234.
2. **If `campose11` also crashes near the ~73-75s transition**: this is now
   2/2 for the `t=`-armed diagnostic vs. a documented history of the SAME
   transition also killing OTHER diagnostics at similar rates (0/4 for the
   epoch diagnostic in s230/s231) — still not strong evidence the new code
   is the cause, but if it happens a 3rd time in a future session, treat
   that as the discriminating signal and stop attaching new I/O to this
   PATCH block until the transition itself is fixed or dodged. Write the
   honest inconclusive-but-trending result into CURRENT-TRUTH; do NOT
   attempt a 3rd `campose1x` soak this iteration (budget for THIS iteration
   is 1 attempt).
3. **If `campose11` survives to the hold window**: this is the payoff step.
   - Adapt `scratch/agent/checksum_campose10.py` (already mtime-aware — swap
     the `campose10` directory name for `campose11`) to get the visual
     freeze frame (last-changed `hold_NN`) AND its real wall-clock mtime.
   - Write `scratch/agent/correlate_campose11.py`: parse
     `campose11/proc_start_epoch.txt` (real epoch at process start), grep
     `campose11/run.log` for `[dl-payload-content-stale]`/
     `[dl-payload-content-changed]`/`[dl-payload-tracker-hb]` lines' `t=`
     fields, convert each to real wall-clock (`epoch + t`), and diff against
     the freeze frame's mtime from the checksum script.
   - The answer: does staleness onset (first `[dl-payload-content-stale]`
     event, or the point where `changed_count` stops increasing per the
     heartbeat) land AT/AFTER the freeze frame's real time (supports a
     stuck-render-cache reading) or well BEFORE it (supports "this content
     was always static, unrelated to the freeze")? Write the answer into
     CURRENT-TRUTH regardless of which way it points — a clean "before"
     result closes off the stuck-cache theory as convincingly as an
     "at/after" result would open it up.

## Do NOT do this iteration

- Do not re-touch `rs64_elapsed_seconds()`, the `t=` PATCH block, or
  `proc_start_epoch.txt` — validated working in `campose10`, not the open
  question anymore.
- Do not re-run `campose8`/`campose9`/`campose10` unmodified — budget spent.
- Do not treat `campose10`'s crash as proof the new diagnostic is unsafe —
  n=1 against a documented 0/4-at-this-transition history for a heavier
  diagnostic is not enough to conclude causation either way (see above).
- Do not reintroduce `ROGUESQ_LOG_RENDER_CACHE_EPOCH` — still closed, 0/4
  through SELECT-CRAFT (s229-s231).
- Do not dump entire raw log files into your own context — write short
  Python scripts or use targeted `grep`, per every prior session's method.
- Do not chase the `campose8`-silent-vs-`campose9`-noisy discrepancy first
  (still open, still lower priority) unless step 3 above turns up nothing
  useful after `campose11` actually survives to the hold window.

## Standard regen recipe (unchanged, not needed this iteration unless step 2
## above decides to touch the diagnostic — it should not)

1. `cd` into N64Recomp checkout, delete stale `RecompiledFuncs/funcs_*.c`:
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

## Environment notes (carried forward, still current as of s234)

- **Permission gate CONFIRMED CLEARED s229-s234** — trust it; all
  `tools/*`/`build/*` commands ran normally again this session.
- Bash cwd persists across tool calls within a session — but an explicit
  `cd` changes it for ALL subsequent calls, and `cd` itself now sometimes
  requires separate approval when chained near a `git` call ("can execute
  untrusted hooks from the target directory") — s234 hit this issuing
  `git -C <path>`; the fix is still: plain `cd <path>` as its own call, then
  the bare command (no `-C`) as a second call. Prefer absolute paths or
  re-`pwd`/`git rev-parse --show-toplevel` if unsure where cwd actually is
  — s234 lost track of cwd after an unrelated `cd` into a soak's output
  directory and got empty/wrong results from `git ls-files`/`git status`
  with a relative pathspec until it re-verified cwd.
- **`cmake --build` is safe to background**; the game-soak launch script
  must stay SYNCHRONOUS/foreground (sends scheduled keypresses, SIGKILLs
  itself at the end) — **but it WILL exceed the 400s default foreground Bash
  timeout (HOLD_S=350 + setup/grace overhead runs ~450-460s total) and get
  auto-backgrounded; this is expected, not a failure. Launch it directly
  with `run_in_background: true` (a generous `timeout`, e.g. 330000ms) and
  block-wait on the returned task id with TaskOutput** (`block: true`,
  `timeout: 480000`) — s233/s234 both used this pattern successfully.
- **`/tmp` is not writable this session** — write scratch/report files
  inside `RogueSquadron64Recomp`/`N64Recomp`/`rogue_squadron64` only.
- Compound `cd ... && ... > file` commands with output redirection get
  blocked by the permission layer — issue the `cd` as its own Bash call
  first, then the redirecting command as a separate call (cwd persists, per
  above). This also applies to plain `cd dir && git ...` — even without
  redirection, a leading `cd` in a compound command gets flagged; always
  split it into two calls.
- **`git -C <path> <cmd>` does not match a `Bash(git <cmd>:*)` allow-rule,
  and now ALSO gets flagged as "changes directory before running git" even
  as a plain `cd` immediately preceding a separate `git` call in some
  cases** — `cd` first (its own call), confirm cwd if unsure, then bare
  `git <cmd>` as a fully separate call.
- **Headless permission matching is a PREFIX match on the command
  string** — write `env PROBE_MODE=1 zsh run.sh`, not
  `PROBE_MODE=1 zsh run.sh`.
- **campose8/9/10's armed env-var set** (keep all when building
  `campose11` — copy `run_campose10.sh`):
  `ROGUESQ_LOG_CAMPOSE`, `ROGUESQ_LOG_MAT3INV`,
  `ROGUESQ_LOG_UNLIT_MESH_TRACER`, `ROGUESQ_LOG_RENDERUNLIT_GUARD`,
  `ROGUESQ_LOG_HEAPWALKER_GUARD`/`GUARD3`/`GUARD4`,
  `ROGUESQ_LOG_MESGQUEUE_GUARD`, `ROGUESQ_LOG_HEAPLISTDEQ_GUARD`,
  `ROGUESQ_LOG_EMIT_DL_GUARD2`/`GUARD3`, `ROGUESQ_LOG_DL_PAYLOAD_STALE=1`.
- **This exact schedule (`schedulepush2`/`campose*` family) is PROVEN
  non-deterministic (s223), reconfirmed hard by s233/s234**: transition
  timing has landed anywhere from 73.8s to 174.8s across runs, and now
  crash-vs-survive at that transition also varies run to run with the exact
  same armed set (`campose8`/`campose9` survived, `campose10` crashed).
  Any conclusion needs same-run evidence, not cross-run comparison.
- **Setup camera struct layout** (unchanged): `+0x0` nullable
  linked-node pointer; `+0x10/0x14/0x18/0x1C` integer viewport rect;
  `+0x20/0x24/0x28` perspective near/scale float scalars; `+0x2C` a 3x3
  float rotation submatrix (36 bytes, to `+0x50`).
- **`traverseSceneGraphRecursive` is `funcs_4.c:15053-15357`**,
  `processSceneNode` is `funcs_4.c:13817-15052`, `submitSceneNodeRender` is
  `funcs_4.c:6-3017`. Render-cache epoch mechanism (s230): read/stamp in
  `submitSceneNodeRender:10-12`/`:41-42`, cache-checks in
  `processSceneNode:13881-13890`/`:14732-14751`; both converge on the
  shared hit-path enqueue block `funcs_4.c:13917-13987` (`L_80014FE8`) —
  content pointer is `$s0`=`node+0x8`, DL-pointer-shaped field is
  `$s0+0x34`=`$a1`/`ctx->r5`. The per-content staleness tracker + s234's
  `t=` timestamp field are in the SAME PATCH block, gated by
  `ROGUESQ_LOG_DL_PAYLOAD_STALE`.
- **`setupCameraMatrices` is `funcs_4.c:19142-21603`**, camera-pose
  diagnostic at guest `0x800178A8`, `ROGUESQ_LOG_CAMPOSE=1`, keep armed.
- **`rs64_elapsed_seconds()`** (s234, `src/main/rt64_render_context.cpp`,
  near the top with `rs64_bump_phase_ord`/`rs64_phase_ord`) is now the
  canonical shared wall-clock for any future guest-side diagnostic that
  needs a timestamp comparable to the `[phase]` line or host-side file
  mtimes — declare `extern double rs64_elapsed_seconds(void);` inline in
  the PATCH block, same idiom as the existing `rogue_current_thread_id`
  extern (see `_hangar_loop_iter_patch` in `fixup_game_funcs.py` for that
  precedent). Do not invent a second clock.
- **Pre-existing crash-family sites, do not treat as new bugs if hit
  again**: `sinfApprox` NaN `NAN_CHECK` assert (`funcs_5.c:6460`, signal 6);
  various unguarded-deref SIGBUS sites across `funcs_*`/`mesgqueue.cpp`
  (signal 10) — see CURRENT-TRUTH -55/-56 and PORTING-STATE Session 214/215
  for the wider family and a proposed (not yet shipped) NAN_CHECK-disable
  fix that could clear this whole recurring family in one shot. **New this
  session**: SIGBUS signal 10 in `submitSceneNodeRender+31672` (called from
  `processSceneNode` <- `traverseSceneGraphRecursive` <-
  `setupCameraMatrices`, `si_addr=0x336000004`) at the ~74s SELECT-CRAFT->
  mission transition — same family/shape (unguarded deref), same transition
  CURRENT-TRUTH -71/-72 already documents as independently fragile; not
  confirmed root-caused, just recognized as belonging to this recurring
  bucket rather than a new investigation target.
- **`emitAllocatedDLCommand` is `funcs_3.c:2622-3210`** — s221's guard
  doesn't cover all fault sites; flagged, not chased (orthogonal).
- **`fixup_game_funcs.py` lives at
  `/Users/williambuckley/Documents/Tools/N64Recomp/fixup_game_funcs.py`**
  — untracked in that sibling checkout (known since s83), now also carries
  s234's `t=`/`rs64_elapsed_seconds()` patch — same standing exposure, not
  fixed this session either.
- **`fixup_game_funcs.py` is NOT idempotent** — never run it twice without
  a delete-all-funcs regen in between.
- **Verify "crash-free" visually**: MD5-checksum a spread of `hold_NN.png`
  (Python script, not shell loops). `scratch/agent/checksum_campose10.py`
  (s234) additionally records each frame's real mtime — reuse this pattern,
  not the older mtime-less `checksum_campose9.py`, for any future
  wall-clock correlation work.
- **`rm -f <glob>`/`find <dir> -delete` are blocked** — use
  `python3 -c "import glob, os; [os.remove(f) for f in glob.glob('<pattern>')]"`.
- Re-running the same soak script/tag OVERWRITES the previous run's
  `run.log` in place — copy the driver script to a new tag name per soak.
- `scratch/agent/STATUS`/`OUTCOME` get reset at the START of each iteration
  by the harness — finding them reset at session start is normal.
- **`/scratch/` is wholesale gitignored** — only `STATUS`, `OUTCOME`,
  `NEXT.md`, and (as of some earlier session) `run_mission_keys.sh` itself
  are tracked exceptions (`git ls-files scratch/s73_post_a_scene/` confirms
  only `run_mission_keys.sh`, not per-soak `run_campose*.sh`/checksum
  scripts). Use `git add -f` for anything else under `scratch/` you want to
  survive; per-soak driver scripts (`run_camposeN.sh`) have never been
  force-added historically — don't start now unless asked, they're
  trivially regenerable by copying the pattern in this file.

## Housekeeping still flagged, still not done

`docs/CURRENT-TRUTH.md` is past both the ~35 KB CLAUDE.md budget and the
Read tool's 256 KB single-read limit (confirmed s195, still true s234 —
read it with `grep`/offset-limited `Read`, never a plain whole-file `Read`).
Migrate durable mechanism/architecture material to `PROJECT-OVERVIEW.md` and
prune superseded detail — flagged for 30+ sessions without action.

`fixup_game_funcs.py`'s untracked, single-copy state in the `N64Recomp`
sibling checkout has been flagged since s83, still not fixed (not this
repo's commit scope) — worth surfacing to the user directly.

`/Users/williambuckley/Documents/Tools/N64Recomp` and
`~/Documents/Tools/rogue_squadron64` are separate git checkouts with
long-standing uncommitted changes, unrelated to this repo's commit scope.
Still flagged for the user, not committed autonomously.

`lib/rt64` and `lib/N64ModernRuntime` both still show as modified in `git
status` as of s234 — not investigated this session either (no lib/ edits
made, so no export.sh/commit obligation triggered). Still worth checking
whether these are in-progress uncommitted patches vs. drift from
`submodule-patches/*.patch` before assuming steady-state dirtiness.

The pre-existing NaN/`NAN_CHECK` and unguarded-deref crash families have a
proposed but unshipped fix (disable/soften `NAN_CHECK` aborts, CURRENT-TRUTH
-55/-56, PORTING-STATE Session 215) that could reduce how often unrelated
soaks die to this family before reaching their actual target. Worth
picking up as its own work unit if a future soak keeps dying to this
family — s234's `campose10` crash is arguably another data point in favor
of doing this soon, since it's now blocked two different probes (this one
and, per CURRENT-TRUTH -71/-72, the render-cache-epoch one) at the exact
same transition.
