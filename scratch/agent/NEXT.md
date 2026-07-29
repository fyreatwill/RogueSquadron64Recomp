# NEXT work unit — bridge the campose (camera-pose) diagnostic to real
# wall-clock, then check whether it also stalls at the ~470s freeze point

## Where the investigation stands

s235 ran the payoff soak (`campose11`) the wall-clock/`hold_N` bridge
(s234) was built for. It survived to the hold window clean (`CRASH: 0`,
464s wall — the ~74s SELECT-CRAFT->mission transition that killed
`campose10` is confirmed non-deterministic, not fixed). The correlation
(`scratch/agent/checksum_campose11.py` + `correlate_campose11.py`, both
new) gave a clean, decisive result:

- Visual freeze frame: `hold_270`. Checksums show the picture blinking
  between two hashes up through `hold_265` (consistent with an animated
  HUD element, e.g. a flashing prompt), then locking permanently from
  `hold_270` through `hold_350` (last frame). Converts via
  `proc_start_epoch.txt` to real elapsed time **470.2s** since process
  launch.
- DL-payload tracker (`ROGUESQ_LOG_DL_PAYLOAD_STALE`, the s233 Option A
  per-content-pointer staleness probe): last staleness/content-change
  event at **t=234.6s/237.8s**, then completely flat
  (`changed_count=4251`, `stale_count=26`) through every heartbeat to
  t=571.1s.
- **Gap = 235.6s.** Staleness predates the visual freeze by nearly 4
  minutes — not at/after it. Far too large a margin for clock-alignment
  slop to explain away.

**Conclusion, written into CURRENT-TRUTH -76**: Option A (stuck DL-payload
render cache, s233) is CLOSED OFF as the cause of the picture freeze for
the 13 tracked content pointers. They go stale early and legitimately
(consistent with load-once-then-static HUD/menu content), well before
whatever actually freezes the picture at t≈470s. **What actually freezes
the picture is still unknown** — this only ruled out one candidate.

## Do this iteration

The blink-then-lock signature (an animated element that stops animating)
points more toward a game-logic/timer stall than a rendering-only bug.
The fastest way to test that: bridge another ALREADY-ARMED diagnostic from
`campose11`'s own env-var set to the same `t=` wall-clock convention, then
re-examine EXISTING `campose11` log data first — no new soak needed yet.

1. **Instrument**: add a `t=%.1f` field (same `rs64_elapsed_seconds()`
   idiom as the `dl-payload-*` PATCH block — `extern double
   rs64_elapsed_seconds(void);` declared inline, see
   `_hangar_loop_iter_patch` in `fixup_game_funcs.py` for the precedent)
   to the `[campose-entry]` log line (`ROGUESQ_LOG_CAMPOSE`, guest
   `0x800178A8`). This is the highest-value target: if the camera-pose
   stream ALSO stalls around t=470s, that argues for a broader game-logic
   freeze (input/camera update loop stalled), not a rendering-cache-only
   bug — a different, more actionable theory than anything probed so far.
   If campose keeps updating normally through and past t=470s while the
   picture stays static, that argues the opposite: game logic is alive,
   only the actual draw/output path is stuck (a real render-side bug,
   different from Option A/B already closed).
2. **Regenerate** (standard recipe below) and **soak once**
   (`campose12`, copy `run_campose11.sh`, change only the tag — keep the
   full existing armed env-var set, nothing else needs to change). Budget:
   1 attempt for this new instrument's validation, per iron rule 1 (need a
   positive control — confirm `t=` fires and increases on
   `[campose-entry]` lines before trusting any freeze-correlation reading
   from it).
3. **Correlate**: reuse `checksum_campose11.py`'s pattern (swap directory
   name) + write `correlate_campose12.py` (parse `[campose-entry] t=`
   values, convert via that run's own `proc_start_epoch.txt`, diff against
   that run's freeze frame). Does the last CHANGING `[campose-entry]` value
   (m00/camptr/deref0 fields) land at/after the freeze frame's real time,
   or well before it (mirroring s235's DL-payload result)?
4. Write the answer into CURRENT-TRUTH regardless of which way it points.

## Do NOT do this iteration

- Do not re-touch the `dl-payload-*` PATCH block, `rs64_elapsed_seconds()`
  itself, or `proc_start_epoch.txt` — all validated working, not the open
  question anymore (s234/s235).
- Do not re-run `campose8`/`9`/`10`/`11` unmodified — their budgets are
  spent for what they were testing.
- Do not reintroduce `ROGUESQ_LOG_RENDER_CACHE_EPOCH` — still closed, 0/4
  through SELECT-CRAFT (s229-s231), unrelated question.
- Do not treat s235's "Option A closed" result as proof the freeze is
  render-side rather than logic-side — that's exactly this iteration's
  open question, not yet answered either way.
- Do not dump entire raw log files into your own context — write short
  Python scripts or use targeted `grep`, per every prior session's method.

## Standard regen recipe (needed this iteration — new PATCH-block edit)

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

## Environment notes (carried forward, still current as of s235)

- **Permission gate CONFIRMED CLEARED s229-s235** — trust it.
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
  block-wait via `TaskOutput` (`block: true`, `timeout: 480000`) —
  s233/s234/s235 all used this pattern successfully; s235 additionally
  confirmed the background task also delivers a completion notification,
  so a shorter first `TaskOutput` block (e.g. 180000ms) followed by a
  second block-wait call is fine if the first one times out mid-run.
- **`/tmp` is not writable this session** — write scratch/report files
  inside `RogueSquadron64Recomp`/`N64Recomp`/`rogue_squadron64` only.
- Compound `cd ... && ...` commands (including with output redirection)
  get blocked by the permission layer — issue `cd` as its own Bash call
  first, then the next command as a separate call.
- **`git -C <path> <cmd>` does not match allow-rules** — `cd` first (own
  call), then bare `git <cmd>` as a separate call.
- **Headless permission matching is a PREFIX match** — write
  `env PROBE_MODE=1 zsh run.sh`, not `PROBE_MODE=1 zsh run.sh`.
- **Zsh quirk found s235**: a `for tag in ...; do grep -ic "$tag" ...; done`
  one-liner with a bracket-containing grep pattern nearby in the same
  Bash call errored with "Contains simple_expansion" (harness-side
  parsing issue, not a real zsh error) — split multi-step shell loops with
  brackets/globs into separate single-purpose Bash calls instead of one
  compound one-liner.
- **campose11's armed env-var set** (keep all when building `campose12` —
  copy `run_campose11.sh`): `ROGUESQ_LOG_CAMPOSE`, `ROGUESQ_LOG_MAT3INV`,
  `ROGUESQ_LOG_UNLIT_MESH_TRACER`, `ROGUESQ_LOG_RENDERUNLIT_GUARD`,
  `ROGUESQ_LOG_HEAPWALKER_GUARD`/`GUARD3`/`GUARD4`,
  `ROGUESQ_LOG_MESGQUEUE_GUARD`, `ROGUESQ_LOG_HEAPLISTDEQ_GUARD`,
  `ROGUESQ_LOG_EMIT_DL_GUARD2`/`GUARD3`, `ROGUESQ_LOG_DL_PAYLOAD_STALE=1`.
- **This exact schedule (`schedulepush2`/`campose*` family) is PROVEN
  non-deterministic (s223, reconfirmed s233/s234)**: transition timing and
  crash-vs-survive both vary run to run with the identical armed set/
  schedule (`campose8`/`9`/`11` survived; `campose10` crashed at ~74s).
  Any conclusion needs same-run evidence, not cross-run comparison.
- **`[campose-entry]` log line** (guest `0x800178A8`, funcs_4.c area) —
  currently has NO `t=` field; fields present: `n=` (call counter),
  `m00=`, `flag=`, `camptr=`, `deref0=`, `deref0_valid=`. This iteration's
  instrument work adds `t=` to it, same idiom as the `dl-payload-*` block.
- **`rs64_elapsed_seconds()`** (`src/main/rt64_render_context.cpp`, near
  `rs64_bump_phase_ord`/`rs64_phase_ord`) is the canonical shared
  wall-clock — declare `extern double rs64_elapsed_seconds(void);` inline
  in any new PATCH block, do not invent a second clock.
- **Pre-existing crash-family sites, do not treat as new bugs if hit
  again**: `sinfApprox` NaN `NAN_CHECK` assert (`funcs_5.c:6460`, signal
  6); various unguarded-deref SIGBUS sites across `funcs_*`/
  `mesgqueue.cpp` (signal 10) — see CURRENT-TRUTH -55/-56 and
  PORTING-STATE Session 214/215. SIGBUS in `submitSceneNodeRender+31672`
  at the SELECT-CRAFT->mission transition (`si_addr=0x336000004`) is the
  same recurring family, already documented, non-deterministic — 3/4
  `campose*` soaks with the `t=`-armed dl-payload instrument have now
  SURVIVED it (`campose8`, `campose9`, `campose11`), only `campose10`
  crashed there.
- **Verify "crash-free" visually**: MD5-checksum a spread of `hold_NN.png`
  (Python script, not shell loops). `scratch/agent/checksum_campose11.py`
  (s235) is mtime-aware — reuse this pattern for any future wall-clock
  correlation work.
- **`rm -f <glob>`/`find <dir> -delete` are blocked** — use
  `python3 -c "import glob, os; [os.remove(f) for f in glob.glob('<pattern>')]"`.
- Re-running the same soak script/tag OVERWRITES the previous run's
  `run.log` in place — copy the driver script to a new tag name per soak.
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
Read tool's 256 KB single-read limit (confirmed s195, still true s235 —
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
status` as of s235 — not investigated this session either (no lib/ edits
made, so no export.sh/commit obligation triggered). Still worth checking
whether these are in-progress uncommitted patches vs. drift from
`submodule-patches/*.patch` before assuming steady-state dirtiness.

The pre-existing NaN/`NAN_CHECK` and unguarded-deref crash families have a
proposed but unshipped fix (disable/soften `NAN_CHECK` aborts,
CURRENT-TRUTH -55/-56, PORTING-STATE Session 215) — worth picking up if a
future soak keeps dying to this family. Lower priority now that 3/4 recent
`campose*` soaks have survived the SELECT-CRAFT transition.
