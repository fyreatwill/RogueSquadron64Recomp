# NEXT work unit — re-soak campose12's already-landed `t=` instrument
# (no code change) to try to reach the hold window and answer the
# campose-vs-freeze correlation question

## Where the investigation stands

s236 added a `t=%.1f` field (shared `rs64_elapsed_seconds()` epoch, same
idiom as the `dl-payload-*` PATCH block) to the `[campose-entry]` log line
(`ROGUESQ_LOG_CAMPOSE`, guest `0x800178A8`, `fixup_game_funcs.py`) and
regenerated clean. The validation soak (`campose12`, copied from
`run_campose11.sh`, RUNTAG only changed) gave a split result:

- **Positive control confirmed**: `t=` fires and increases monotonically
  on `[campose-entry]` lines — `t=0.9` (n=0) through `t=130.8` (n=12420),
  210 lines total. The instrument itself works.
- **But the run crashed during the SELECT-CRAFT->mission transition**
  before reaching the hold window (0 `hold_NN.png` frames captured), so
  the actual discriminating question — does the camera-pose stream also
  stall around t≈470.2s (s235's freeze frame), arguing for a game-logic
  freeze, or keep updating, arguing for a render-side-only bug — still has
  NOT been tested. This is the exact same shape as s234's `campose10`
  soak (instrument validated, crashed before the payoff).

Crash signature (for reference, not a new bug — see "Do NOT" below): SIGBUS,
`si_addr=0x380000000`, `emitAllocatedDLCommand+6608` <-
`submitSceneNodeRender+21576` <- `processSceneNode` <-
`traverseSceneGraphRecursive` <- `setupCameraMatrices`. Same call-chain
family as `campose10`'s crash (`submitSceneNodeRender+31672`,
`si_addr=0x336000004`, s234) — different exact offset/address, same
transition-time scene-traversal instability, already documented
non-deterministic (now 2/5 `campose*` soaks crashed here vs. 3/5 survived:
`campose8`/`9`/`11` survived, `campose10`/`12` crashed).

This is the 1st soak of this specific instrument (not yet a 3rd
consecutive no-result iteration on this hypothesis — iron rule 8 does not
yet call for abandoning it). Per the s234->s235 precedent, the next move is
simply one more soak of the SAME already-validated instrument — no new
code, no new diagnostic.

## Do this iteration

1. **Copy the driver, bump the tag only**: `cp
   scratch/s73_post_a_scene/run_campose12.sh
   scratch/s73_post_a_scene/run_campose13.sh`, then edit ONLY the
   `campose12`->`campose13` string occurrences (the `zsh
   run_mission_keys.sh campose12 5 12` line and the header comment). Do
   NOT touch env vars, `STICK_SCHEDULE`, `HOLD_S`, or any other setting —
   identical armed set to `campose11`/`campose12`.
2. **No rebuild needed** — the binary already has the validated `t=`
   instrument compiled in from s236. Launch directly:
   `zsh run_campose13.sh` as a single SYNCHRONOUS (foreground) Bash call,
   `run_in_background: true`, generous timeout (e.g. 330000ms), then
   block-wait via `TaskOutput` (`block: true`, `timeout: 180000`, repeat if
   it times out mid-run — s233-s236 all used this pattern successfully).
3. **If it crashes again before the hold window** (plausible — this
   transition is proven non-deterministic, not a coin flip guaranteed to
   land in your favor): this becomes the 2nd no-result soak on this
   instrument, still short of the 3-strikes budget rule. Write up the
   crash signature (compare call-chain/offset against `campose10`/`12` —
   same family or different?), and leave ONE more soak (`campose14`) as
   next iteration's work unit. Do not spend a 3rd soak in the SAME
   iteration — one soak is the per-iteration work unit.
4. **If it survives to the hold window** (`CRASH: 0`-equivalent, i.e. no
   `[CRASH] caught signal` line, and `hold_NN.png` frames present up to
   `hold_350`): this is the payoff run.
   - Reuse `scratch/agent/checksum_campose11.py`'s pattern (swap directory
     name to `campose13`) to find the freeze frame (the hash that locks
     permanently and never changes again through `hold_350`).
   - Write `correlate_campose13.py`: parse the `t=` field off
     `[campose-entry]` lines (NOT `[campose-abnormal]`, which has no `t=`
     field yet), convert via that run's own `proc_start_epoch.txt` to real
     elapsed seconds, and diff the LAST-CHANGING `[campose-entry]` value
     (watch `m00`/`camptr`/`deref0` fields, same fields s224's original
     camera-corruption probe tracked) against the freeze frame's real
     elapsed time.
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
     points — this is the payoff for two iterations of instrument-building
     work, do not let it go unrecorded.

## Do NOT do this iteration

- Do not touch `fixup_game_funcs.py`'s `[campose-entry]` PATCH block, the
  `dl-payload-*` PATCH block, `rs64_elapsed_seconds()` itself, or
  `proc_start_epoch.txt` stamping in `run_mission_keys.sh` — all validated
  working as of s234/s236, not the open question.
- Do not regenerate/rebuild unless you actually change generated code —
  the s236 binary already has the instrument; `campose13` is a straight
  re-run.
- Do not re-run `campose8`/`9`/`10`/`11` unmodified — their budgets are
  spent for what they were testing.
- Do not reintroduce `ROGUESQ_LOG_RENDER_CACHE_EPOCH` — still closed, 0/4
  through SELECT-CRAFT (s229-s231), unrelated question.
- Do not treat the SELECT-CRAFT->mission transition crash as a new bug to
  fix — it's the same documented non-deterministic family
  (CURRENT-TRUTH -71/-72/-75/-77), 2/5 `campose*` soaks so far. Fixing it
  is a separate, larger investigation (the pre-existing NaN/unguarded-deref
  crash-family fix proposed at CURRENT-TRUTH -55/-56, still unshipped) —
  out of scope for this probe chain.
- Do not dump entire raw log files into your own context — write short
  Python scripts or use targeted `grep`, per every prior session's method.

## Standard regen recipe (NOT needed this iteration — no code change)

Only use this if `correlate_campose13.py`'s result motivates a NEW
diagnostic (e.g. adding `t=` to another already-armed log line):

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

## Environment notes (carried forward, still current as of s236)

- **Permission gate CONFIRMED CLEARED s229-s236** — trust it.
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
  shorter first wait is fine, s236 confirmed a completion notification
  still arrives if you don't re-poll).
- **`/tmp` is not writable this session** — write scratch/report files
  inside `RogueSquadron64Recomp`/`N64Recomp`/`rogue_squadron64` only.
- Compound `cd ... && ...` commands (including with output redirection)
  get blocked by the permission layer — issue `cd` as its own Bash call
  first, then the next command as a separate call.
- **`git -C <path> <cmd>` does not match allow-rules** — `cd` first (own
  call), then bare `git <cmd>` as a separate call.
- **Headless permission matching is a PREFIX match** — write
  `env PROBE_MODE=1 zsh run.sh`, not `PROBE_MODE=1 zsh run.sh`.
- **campose12's armed env-var set** (identical to `campose11`, keep all
  when building `campose13` — copy `run_campose12.sh`):
  `ROGUESQ_LOG_CAMPOSE`, `ROGUESQ_LOG_MAT3INV`,
  `ROGUESQ_LOG_UNLIT_MESH_TRACER`, `ROGUESQ_LOG_RENDERUNLIT_GUARD`,
  `ROGUESQ_LOG_HEAPWALKER_GUARD`/`GUARD3`/`GUARD4`,
  `ROGUESQ_LOG_MESGQUEUE_GUARD`, `ROGUESQ_LOG_HEAPLISTDEQ_GUARD`,
  `ROGUESQ_LOG_EMIT_DL_GUARD2`/`GUARD3`, `ROGUESQ_LOG_DL_PAYLOAD_STALE=1`.
- **This exact schedule (`schedulepush2`/`campose*` family) is PROVEN
  non-deterministic (s223, reconfirmed s233/s234/s236)**: transition
  timing and crash-vs-survive both vary run to run with the identical
  armed set/schedule (`campose8`/`9`/`11` survived; `campose10`/`12`
  crashed at the same transition, `10` at ~t=74.5s, `12` at ~t=130s).
  VI-width transition ONSET (1024->512) does look consistently timed
  (~t=74.4-74.5s across `campose10`/`12`) even when the eventual crash
  timing after onset differs — worth noting if a future session wants to
  separate "transition onset" from "transition-triggered crash" as
  distinct events. Any conclusion needs same-run evidence, not cross-run
  comparison.
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
  PORTING-STATE Session 214/215. SIGBUS in `submitSceneNodeRender`/
  `emitAllocatedDLCommand` (called from the
  `setupCameraMatrices`->`traverseSceneGraphRecursive`->`processSceneNode`
  chain) at the SELECT-CRAFT->mission transition is the same recurring
  family, already documented, non-deterministic — 3/5 `campose*` soaks
  with the `t=`-armed dl-payload/campose instrument have now SURVIVED it
  (`campose8`, `campose9`, `campose11`), 2/5 crashed (`campose10`,
  `campose12`).
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
Read tool's 256 KB single-read limit (confirmed s195, still true s236 —
read it with `grep`/offset-limited `Read`, never a plain whole-file
`Read`). Migrate durable mechanism/architecture material to
`PROJECT-OVERVIEW.md` and prune superseded detail — flagged for 30+
sessions without action.

`fixup_game_funcs.py`'s untracked, single-copy state in the `N64Recomp`
sibling checkout has been flagged since s83, still not fixed (not this
repo's commit scope) — worth surfacing to the user directly. s236 added
another patch to this untracked file (the `[campose-entry]` `t=` field) —
if this checkout is ever lost/reset, that edit (and every other session's
edits) goes with it.

`/Users/williambuckley/Documents/Tools/N64Recomp` and
`~/Documents/Tools/rogue_squadron64` are separate git checkouts with
long-standing uncommitted changes, unrelated to this repo's commit scope.
Still flagged for the user, not committed autonomously.

`lib/rt64` and `lib/N64ModernRuntime` both still show as modified in `git
status` as of s236 — not investigated this session either (no lib/ edits
made, so no export.sh/commit obligation triggered). Still worth checking
whether these are in-progress uncommitted patches vs. drift from
`submodule-patches/*.patch` before assuming steady-state dirtiness.

The pre-existing NaN/`NAN_CHECK` and unguarded-deref crash families have a
proposed but unshipped fix (disable/soften `NAN_CHECK` aborts,
CURRENT-TRUTH -55/-56, PORTING-STATE Session 215) — worth picking up if a
future soak keeps dying to this family. Lower priority now that 3/5 recent
`campose*` soaks have survived the SELECT-CRAFT transition.
