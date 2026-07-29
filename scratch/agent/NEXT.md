# NEXT work unit — add a wall-clock/hold_N bridge to the per-content
# staleness tracker, then correlate staleness onset with the visual freeze

## Where the investigation stands

s233 closed off s232's Option B (the disputed `0x80332xxx`-`0x80335xxx`
address pool is unambiguously runtime heap, ~1.8MB past every static ELF
section — `scratch/agent/elf_segments.py` confirmed this against
`rogue_squadron64/build/roguesquadron.elf`, no soak needed) and landed +
soak-validated Option A: a 256-slot per-content-pointer staleness tracker
(`ROGUESQ_LOG_DL_PAYLOAD_STALE=1`, same `funcs_4.c:13918`/`L_80014FE8`
anchor as s232's `ROGUESQ_LOG_DL_PAYLOAD_HASH`, `fixup_game_funcs.py`).

Two soaks (`campose8`, `campose9`, both `CRASH: 0`, both budgeted attempts
used) reproduced a real signal: the SAME 13 content pointers
(`0x800D1100` through `0x800FA1A4`) independently went genuinely stale
(identical DL-payload hash across a >=10000-call gap) in BOTH runs — a
two-independent-soak match. `campose9` (which ran further before its own
freeze) additionally caught staleness in the previously-disputed
`0x80332xxx` range, single-source only. **This is real progress but NOT
yet a resolved finding** — it shows specific objects go and stay constant
for a long time, which partially undercuts "just static HUD" for those 13
objects (s232's own heartbeat called that address range "diverse/changing,
dynamic 3D"), but does not by itself prove a stuck render cache, since
"this object never changed for 10000+ calls" is also consistent with
legitimate load-once-then-static content that simply took a while to first
appear.

**The missing piece, identified this session**: there is no timestamp or
`hold_N` bridge between the `dl-payload-*` log lines (keyed only by the
processSceneNode call counter `n`) and the checksum-based visual-freeze
frame (`hold_NN.png`, MD5'd offline). Without that bridge we can only
guess at whether staleness onset happens AT, BEFORE, or well AFTER the
frame where the picture actually stops changing — which is exactly the
question that would discriminate "this is the freeze bug" from "this
object was always going to settle here." Full data and exact addresses:
PORTING-STATE Session 233. Raw logs: `scratch/s73_post_a_scene/campose8/
run.log`, `scratch/s73_post_a_scene/campose9/run.log`. Analysis scripts:
`scratch/agent/checksum_campose8.py`/`checksum_campose9.py` (visual freeze
point), `scratch/agent/elf_segments.py` (static ELF section ranges, Option
B's closing evidence).

There's also a second, unexplained open question from s233 (lower
priority, don't chase this iteration unless the primary work below turns
up nothing): `campose8`'s enqueue site went completely SILENT after
n=54073 for the rest of the 449s run (no more `[dl-payload-*]` lines of
any kind, while unrelated `[thr-resume]` diagnostics kept counting past
n=170000), but `campose9`'s kept firing at high volume with zero new
content to at least n=325000. Two qualitatively different post-freeze
behaviors for the identical code path — not yet explained by the schedule's
known non-determinism alone.

## Do this iteration

1. **Add a wall-clock timestamp to the existing `dl-payload-*` PATCH block**
   (`fixup_game_funcs.py`, same anchor as `ROGUESQ_LOG_DL_PAYLOAD_STALE`).
   Find how the existing capture-tick screenshot loop timestamps `hold_NN`
   frames (grep `run_mission_keys.sh`/`funcs_4.c` diagnostics for an
   existing wall-clock read, e.g. `gettimeofday`/`clock()`/a frame counter
   already threaded through `ctx` or a global) and reuse THE SAME clock —
   do not invent a second, potentially-skewed one. Emit it on every
   `[dl-payload-content-changed]`/`[dl-payload-content-stale]`/heartbeat
   line, e.g. append ` t=%.1f` (seconds since process start, or whatever
   base the screenshot loop uses — must be directly comparable to
   `hold_NN`'s own timing, which starts counting at hold-window-start, not
   process-start — so also emit or compute the hold-window-start offset
   once, e.g. log a `[hold-window-start] t=...` line right when the hold
   phase begins if that anchor exists in the launch script's env/log, or
   derive it from the already-logged `[phase]` transition line's timestamp
   the launch driver prints).
2. Standard regen recipe (below). Budget 1 fresh soak (copy `campose9`'s
   script to a new tag, e.g. `campose10`) — this is validating a NEW
   diagnostic feature (timestamp emission), not re-running the same probe a
   3rd time, so it's a fresh budget, but keep it to 1 attempt for THIS
   validation pass; if it reveals something worth a second confirmatory
   soak, that's a new, explicit budget decision for the iteration after.
3. After the soak: MD5-checksum the frames (reuse the `checksum_campose8.py`
   pattern) to get the visual-freeze timestamp/frame, then cross-reference
   against the new `t=` field on the `[dl-payload-content-stale]` lines —
   does staleness onset (first stale event, or the point where
   `changed_count` stops increasing) happen AT/AFTER the freeze frame's
   timestamp (supports the render-cache-stuck reading) or well BEFORE it
   (supports "this content was always static, freeze is unrelated")?
4. Write the answer into CURRENT-TRUTH regardless of which way it points —
   a clean "before" result closes off the stuck-cache theory as
   convincingly as an "at/after" result would open it up further.

## Do NOT do this iteration

- Do not re-run `campose8`/`campose9` unmodified — their data is already
  extracted and budget-exhausted for the diagnostic as it currently exists
  (no timestamp field). Only soak again once the timestamp is landed.
- Do not chase the `campose8`-silent-vs-`campose9`-noisy discrepancy first
  — it's real but lower priority than closing the timestamp gap, which
  directly unblocks the HUD-vs-stuck-cache question this whole probe chain
  (s229-s233) has been working toward. Only pivot to it if step 3 above
  turns up nothing useful.
- Do not reintroduce `ROGUESQ_LOG_RENDER_CACHE_EPOCH` — still closed, 0/4
  through SELECT-CRAFT (s229-s231).
- Do not dump entire raw log files into your own context — write short
  Python scripts or use targeted `grep`, per every prior session's method.
- Do not treat "13 pointers reproduced stale across 2 soaks" as proof of a
  stuck cache in CURRENT-TRUTH — it's real and two-source, but the timing
  correlation (this iteration's job) is what would actually prove or
  disprove the causal link to the freeze.

## Standard regen recipe (unchanged)

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

## Environment notes (carried forward, still current as of s233)

- **Permission gate CONFIRMED CLEARED s229-s233** — trust it; all
  `tools/*`/`build/*` commands ran normally again this session.
- Bash cwd persists across tool calls within a session — but an explicit
  `cd` changes it for ALL subsequent calls. Prefer absolute paths or re-`pwd`
  if unsure.
- **`cmake --build` is safe to background**; the game-soak launch script
  must stay SYNCHRONOUS/foreground (sends scheduled keypresses, SIGKILLs
  itself at the end) — **but it WILL exceed the 400s default foreground Bash
  timeout (HOLD_S=350 + setup/grace overhead runs ~450-460s total) and get
  auto-backgrounded; this is expected, not a failure. Launch it directly
  with `run_in_background: true` (a generous `timeout`, e.g. 330000ms) and
  block-wait on the returned task id with TaskOutput** — s233 used this
  pattern successfully (TaskOutput with `block: true`, `timeout: 480000`,
  then a shorter follow-up call once near-complete) rather than a manual
  `kill -0` polling script.
- **`/tmp` is not writable this session** — write scratch/report files
  inside `RogueSquadron64Recomp`/`N64Recomp`/`rogue_squadron64` only.
- Compound `cd ... && ... > file` commands with output redirection get
  blocked by the permission layer ("Commands that change directories and
  write via output redirection require explicit approval") — issue the
  `cd` as its own Bash call first, then the redirecting command as a
  separate call (cwd persists, per above). This also applies to plain
  `cd dir && git ...` — even without redirection, a leading `cd` in a
  compound command gets flagged; always split it into two calls.
- **`git -C <path> <cmd>` does not match a `Bash(git <cmd>:*)` allow-rule**
  — `cd` first, then bare `git <cmd>`.
- **Headless permission matching is a PREFIX match on the command
  string** — write `env PROBE_MODE=1 zsh run.sh`, not
  `PROBE_MODE=1 zsh run.sh`.
- **campose8/campose9's armed env-var set** (keep all when building the
  next soak script — copy `run_campose8.sh` or `run_campose9.sh`):
  `ROGUESQ_LOG_CAMPOSE`, `ROGUESQ_LOG_MAT3INV`,
  `ROGUESQ_LOG_UNLIT_MESH_TRACER`, `ROGUESQ_LOG_RENDERUNLIT_GUARD`,
  `ROGUESQ_LOG_HEAPWALKER_GUARD`/`GUARD3`/`GUARD4`,
  `ROGUESQ_LOG_MESGQUEUE_GUARD`, `ROGUESQ_LOG_HEAPLISTDEQ_GUARD`,
  `ROGUESQ_LOG_EMIT_DL_GUARD2`/`GUARD3`, plus
  `ROGUESQ_LOG_DL_PAYLOAD_STALE=1` (new gate, independent of
  `ROGUESQ_LOG_DL_PAYLOAD_HASH` — both can be armed together if you want
  the s232 heartbeat/transition data alongside the new timestamp field).
- **This exact schedule (`schedulepush2`/`campose*` family) is PROVEN
  non-deterministic (s223), reconfirmed hard by s233**: `campose8`'s
  SELECT-CRAFT->mission transition landed at 73.8s with freeze at
  `hold_40`; `campose9`'s transition landed at 174.8s with freeze at
  `hold_182` — same script, wildly different timing both times. Any
  timing-based conclusion needs the SAME-RUN bridge this iteration is
  building, not a cross-run comparison.
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
  `$s0+0x34`=`$a1`/`ctx->r5`. The per-content staleness tracker (s233) is
  in the SAME PATCH block, gated by `ROGUESQ_LOG_DL_PAYLOAD_STALE`.
- **`setupCameraMatrices` is `funcs_4.c:19142-21603`**, camera-pose
  diagnostic at guest `0x800178A8`, `ROGUESQ_LOG_CAMPOSE=1`, keep armed.
- **Pre-existing crash-family sites, do not treat as new bugs if hit
  again**: `sinfApprox` NaN `NAN_CHECK` assert (`funcs_5.c:6460`, signal 6);
  various unguarded-deref SIGBUS sites across `funcs_*`/`mesgqueue.cpp`
  (signal 10) — see CURRENT-TRUTH -55/-56 and PORTING-STATE Session 214/215
  for the wider family and a proposed (not yet shipped) NAN_CHECK-disable
  fix that could clear this whole recurring family in one shot.
- **`emitAllocatedDLCommand` is `funcs_3.c:2622-3210`** — s221's guard
  doesn't cover all fault sites; flagged, not chased (orthogonal).
- **`fixup_game_funcs.py` lives at
  `/Users/williambuckley/Documents/Tools/N64Recomp/fixup_game_funcs.py`**
  — untracked in that sibling checkout (known since s83).
- **`fixup_game_funcs.py` is NOT idempotent** — never run it twice without
  a delete-all-funcs regen in between.
- **Verify "crash-free" visually**: MD5-checksum a spread of `hold_NN.png`
  (Python script, not shell loops).
- **`rm -f <glob>`/`find <dir> -delete` are blocked** — use
  `python3 -c "import glob, os; [os.remove(f) for f in glob.glob('<pattern>')]"`.
- Re-running the same soak script/tag OVERWRITES the previous run's
  `run.log` in place — copy the driver script to a new tag name per soak.
- `scratch/agent/STATUS`/`OUTCOME` get reset at the START of each iteration
  by the harness — finding them reset at session start is normal.
- **`/scratch/` is wholesale gitignored** — only `STATUS`, `OUTCOME`, and
  `NEXT.md` are tracked exceptions. Use `git add -f` for anything else
  under `scratch/` you want to survive.

## Housekeeping still flagged, still not done

`docs/CURRENT-TRUTH.md` is past both the ~35 KB CLAUDE.md budget and the
Read tool's 256 KB single-read limit (confirmed s195, still true s233 —
read it with `grep`/offset-limited `Read`, never a plain whole-file `Read`).
Migrate durable mechanism/architecture material to `PROJECT-OVERVIEW.md` and
prune superseded detail — flagged for 29+ sessions without action.

`fixup_game_funcs.py`'s untracked, single-copy state in the `N64Recomp`
sibling checkout has been flagged since s83, still not fixed (not this
repo's commit scope) — worth surfacing to the user directly.

`/Users/williambuckley/Documents/Tools/N64Recomp` and
`~/Documents/Tools/rogue_squadron64` are separate git checkouts with
long-standing uncommitted changes, unrelated to this repo's commit scope.
Still flagged for the user, not committed autonomously.

`lib/rt64` and `lib/N64ModernRuntime` both still show as modified in `git
status` as of s233 — not investigated this session either (no lib/ edits
made, so no export.sh/commit obligation triggered). Still worth checking
whether these are in-progress uncommitted patches vs. drift from
`submodule-patches/*.patch` before assuming steady-state dirtiness.

The pre-existing NaN/`NAN_CHECK` and unguarded-deref crash families have a
proposed but unshipped fix (disable/soften `NAN_CHECK` aborts, CURRENT-TRUTH
-55/-56, PORTING-STATE Session 215) that could reduce how often unrelated
soaks die to this family before reaching their actual target. Worth
picking up as its own work unit if a future soak keeps dying to this
family.
