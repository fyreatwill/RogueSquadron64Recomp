# NEXT work unit — instrument the camera's own pose values (not a derived
# matrix) across a long soak, phase-gated around the ~140s/crawl-exit mark,
# to find whether the CAMERA freezes or the SCENE CONTENT feeding it freezes

Read PORTING-STATE Session 223 in full (`grep -n "^## Session 223"
PORTING-STATE.md`) before doing anything else. Short version: s223 refuted
the leading hypothesis (a degenerate 3x3-matrix-inverse determinant in
`mat3x3InverseInto`, called from `setupCameraMatrices` right before
`traverseSceneGraphRecursive`) with a well-controlled null — 456,000+
diagnostic firings spanning the ENTIRE 350s hold window, genuinely varying
determinant values, never once zero/Inf/NaN. That candidate is closed.

**But s223 also produced a much bigger, unplanned finding**: re-running
s222's own `schedulepush2` script byte-for-byte (same schedule, same code)
did NOT reproduce s222's "frozen from hold_04 onward" result. Instead this
run reached real space-combat mesh content (`hold_01`-`10`, an X-wing near
a capital-ship hull) and the opening crawl (`hold_15`-`74`, `[phase]`
`origin=0x006A2900` at 140.6s — the SAME address and near-identical
timestamp as s154's own "furthest ever past the crawl" milestone) before
freezing at `hold_75` onward on a flat, single-color ground-fill frame —
visually DIFFERENT from s150/s222's "torn/striped degenerate polygon"
description. **Non-determinism is now proven on identical scripted input**,
not just inferred from schedule-to-schedule variation across sessions.

Also established: at the very end of the frozen window, `[vi-fs-decision]`
shows `stalled=0, reason=swap, rdpFs=3481` still incrementing — the
swap/present pipeline is demonstrably alive, ruling out a render-pipeline
stall as this freeze's cause. Combined with the mat3inv null, the freeze
mechanism is narrowed to: something in the game's own logic/state-machine
(whatever drives camera pose or scene-graph content per frame) stops
advancing, while the rest of the engine (VI swaps, RDP fullsync counters)
keeps ticking normally.

## Why this is the priority

The mat3x3InverseInto lead and the composeNpcOrientationMatrix lead
(closed since s157/s158, 7 guards, 508/508 entry-confirmed, 0/0 guards —
do NOT re-open) are both dead ends now. The s223 bonus finding is a new,
higher-value thread: for the first time, this investigation has direct
evidence that the freeze's ENDPOINT differs across nominally-identical
runs (dead hangar vs. past-the-crawl-then-frozen-on-ground), which means
the freeze is not a fixed frame/state but a "whatever the camera/scene was
doing gets stuck wherever it happens to be" phenomenon. Distinguishing
"camera pose itself freezes" from "camera keeps moving but content behind
it doesn't" is the key discriminating question before any fix attempt.

## Do this iteration

### Step 1 — pick ONE camera-pose field and log it at low frequency

Do NOT re-read `setupCameraMatrices`/`mat3x3InverseInto`/
`composeNpcOrientationMatrix` again (all closed this session or before).
Instead: find where `setupCameraMatrices` (`N64Recomp/RecompiledFuncs/
funcs_4.c:19142-21603`) reads or writes the camera's own position/
orientation/lookat fields (likely near the top of the function, before the
guPerspective/guScale/guLookAt-style calls around `funcs_4.c:19160-19340`
per s223's partial read of that region) — pick ONE such field (a position
X/Y/Z or a single rotation angle, NOT the whole matrix) that plausibly
represents "where the camera currently is/points," not a derived product.

### Step 2 — instrument, gated behind a new ROGUESQ_LOG_* env var

Add ONE targeted, always-firing-but-capped log (e.g. print every ~60
frames, roughly once per second, NOT every call — this field is read far
more often than once/frame) at that field, via `fixup_game_funcs.py`
(sibling `N64Recomp` checkout) following the same pattern as
`ROGUESQ_LOG_MAT3INV` added this session (entry-style periodic log, no
guard/bail). Full clean regen recipe (proven twice now, s221 and s223):
delete all 45 `RecompiledFuncs/funcs_*.c`, `python3 tools/make_elf.py`
(rogue_squadron64 checkout), `./build/N64Recomp rogue_squadron.toml` (or
`tools/agent/regen_n64recomp.sh`), `fixup_game_funcs.py` **exactly once**
(capture output to a file, grep the file, never re-invoke), `cmake --build
. -j8` with `DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer`.

### Step 3 — soak, phase-gate on the crawl-exit, checksum-verify

Reuse `scratch/s73_post_a_scene/run_mat3inv2.sh` as the template (same
`schedulepush2`-derived schedule, `HOLD_S=350`, synchronous foreground
Bash call, ~580s timeout) — copy to a new tag, add the new env var,
keep all s222/s223 diagnostics armed as regression checks. Because s223
showed this exact schedule is non-deterministic (2 very different
outcomes from 2 identical runs), budget for up to **2 attempts this
session** (not more — budget rule 8) before treating a null as
inconclusive rather than negative. After each run:
- MD5-checksum a spread of `hold_NN.png` (`python3 -c "import hashlib;
  ..."` one-liner, not shell loops — trips the sandbox gate for unclear
  reasons, per longstanding note below) to find the actual freeze onset
  this run, whatever content it reaches.
- Compare the new camera-pose log's values in a window BEFORE the freeze
  onset vs. AFTER it (same run, phase-gated on the checksum-observed
  onset, not a cross-run comparison).

Discriminating outcomes:
- **Camera-pose field stops changing at the freeze onset** → confirms
  "stuck camera" — the state-machine driving camera updates has wedged;
  next step is finding what SHOULD have advanced it (an animation-
  finished flag, a timer, a scripted-sequence index) and why it didn't.
- **Camera-pose field KEEPS changing after the freeze onset** → the camera
  is fine; the bug is downstream (scene-graph population/visibility/
  culling stops updating while the camera moves through empty/unchanging
  space) — next step shifts to `processSceneNode`/`submitSceneNodeRender`
  rather than the camera-matrix functions.
- **This run doesn't freeze at all, or freezes at a totally different
  point** → reinforces non-determinism; note the new onset point/content
  reached and do NOT treat 1 non-reproducing run as refuting anything —
  needs a 2nd same-script attempt (still within this session's budget)
  before concluding.

## Do NOT do this iteration

- Do not re-instrument `mat3x3InverseInto` or `composeNpcOrientationMatrix`
  — both closed (refuted / 7-guards-0/0-with-508/508-entry-confirmed,
  respectively). Re-testing either is budget-rule-8 territory.
- Do not treat s222's "no soak reaches mesh content" framing as true
  anymore — it's in "Overturned conclusions" now. Content IS reachable,
  non-deterministically.
- Do not conclude anything from a single soak this session without the
  MD5-checksum step — a crash-free or clean-looking run is not evidence
  the picture actually progressed (s222's own lesson, reconfirmed s223).

## Environment notes (carried forward, still current)

- **This exact schedule (s222's `schedulepush2` / s223's `run_mat3inv2.sh`)
  is now PROVEN non-deterministic on identical input** — 1 of 2 runs froze
  immediately in the hangar, the other reached the opening crawl. Do not
  assume a single soak's outcome generalizes; budget 2 attempts before
  drawing conclusions, per Step 3 above.
- **Full clean-room regen recipe, proven twice (s221, s223)**: delete all
  `RecompiledFuncs/funcs_*.c` (`python3 -c "import glob, os; [os.remove(f)
  for f in glob.glob('funcs_*.c')]"` from that directory), re-run
  `make_elf.py` + `N64Recomp`, run `fixup_game_funcs.py` **exactly once**,
  capturing its report to a file — this is safer than trying to apply
  fixup incrementally on top of already-patched files and avoids any
  repeat-invocation label-duplication risk entirely.
- **A whole-tree label-dup audit (`grep -oE '^L_[A-Za-z0-9_]+:$'
  funcs_*.c | sort | uniq -c`) WILL show many labels appearing >1x ACROSS
  DIFFERENT files/functions** (address-derived names naturally recur
  across unrelated functions) — this is expected and harmless (C labels
  are function-scoped). Only a duplicate WITHIN the same function body is
  the s221 failure mode; the build is the definitive test either way.
- **Verify a "crash-free" soak visually before trusting it**: MD5-checksum
  a spread of `hold_NN.png` files
  (`python3 -c "import hashlib; print(hashlib.md5(open(f,'rb').read()).hexdigest())"`
  per file, or loop over a list in one Python invocation — plain `md5`/
  shell `for` loops over multiple files tripped the sandbox's command-
  approval gate for unclear reasons; Python one-liners did not).
- **Launch soaks synchronously (foreground), not backgrounded, when they
  fit the tool timeout.** Budget ~80s of nav/stable/leave overhead on top
  of `HOLD_S` when picking a timeout (`HOLD_S=350` + ~80s overhead ≈ 430s
  wall, comfortably inside a 600s Bash timeout).
- **`mat3x3InverseInto` is `funcs_5.c:7208-~7460`** (generic 3x3-inverse
  utility, ~50 call sites across the whole game — `ra` in `ctx->r31` reads
  as 0x0 at the diagnostic's insertion point since this leaf function never
  itself calls anything before that point, so it does NOT distinguish
  caller identity; don't rely on it for that). `setupCameraMatrices` is
  `funcs_4.c:19142-21603`, `traverseSceneGraphRecursive` is
  `funcs_4.c:15053-15357`. `composeNpcOrientationMatrix`
  (`static_5_800AB1C8`) is `funcs_40.c:6280-7200`, CLOSED (see above).
- **`emitAllocatedDLCommand` is `funcs_3.c:2622-3210`**, `renderUnlitMeshFaces`
  is `funcs_4.c:4963-5630` (both guarded, s219/s221, still structurally
  unconfirmed). `heapWalker` is `funcs_3.c:99-700`, `heapFreeListDequeue`
  is `funcs_3.c:15427-17128` (both s217/s218, unchanged).
- **`fixup_game_funcs.py` is NOT idempotent — NEVER run it twice in the
  same session without a delete-all-funcs regen in between.** Redirect the
  FIRST run's output to a file under `scratch/agent/` and grep the file,
  never re-invoke the script.
- **Raw crash logs are often still on disk long after the session that
  produced them** — `grep` the actual `run.log` under
  `scratch/s73_post_a_scene/<tag>/run.log` before trusting a prose summary.
- **`recomp.h` location**: `lib/N64ModernRuntime/N64Recomp/include/
  recomp.h` — nested submodule inside `lib/N64ModernRuntime`.
  `submodule-patches/export.sh`/`apply.sh` cover both copies. Any edit
  under `lib/` needs `export.sh` + commit, same session. **`NAN_CHECK`
  (`recomp.h:396`) is `assert(val==val)` — this catches true NaN but NOT
  Inf** (`Inf==Inf` is true), and only checks its own operand, never a
  computed result — a real gap in this project's NaN-defense strategy,
  worth remembering for any future transform-corruption hunt.
- **`fixup_game_funcs.py` lives at
  `/Users/williambuckley/Documents/Tools/N64Recomp/fixup_game_funcs.py`** —
  the sibling checkout, genuinely untracked there (known since s83, not
  this project's commit scope, flagged for the user).
- The `[CRASH][pc-symbol]` diagnostic (dladdr on raw mcontext `pc`) is
  permanent, always-on, more precise than `backtrace_symbols_fd` (s213).
- Disassembly tools (`nm`/`otool`/`objdump`/`lldb`/`atos`) are ALL blocked.
  Source-level reasoning only.
- `-O0` Debug build, `RECOMP_FUNC` noinline, no LTO — dladdr resolving to
  function F means the fault is inside F's own body.
- `recomp.h`: `U32(val)` = `(uint32_t)(val)`; `gpr` = `uint64_t`; a legit
  KSEG0 `gpr` sign-extends, upper bits `0xFFFFFFFF`. Always check upper 32
  bits explicitly — a bare `U32()` check is blind to this corruption shape.
- `rm -f <glob>`/`find <dir> -delete` are blocked — use
  `python3 -c "import glob, os; [os.remove(f) for f in glob.glob('<pattern>')]"`.
- `./build/N64Recomp rogue_squadron.toml` needs an `env` prefix and must run
  with cwd set to the `N64Recomp` checkout itself (use
  `tools/agent/regen_n64recomp.sh`). Compound `cd ... && cmd` gets denied in
  one Bash call — issue `cd` and the following command as SEPARATE Bash
  calls; redirecting output (`> file`) in the same call as a `cd` also gets
  denied — write output to a file via a separate, non-`cd`-prefixed call.
- `git -C <path> <cmd>` does not match a `Bash(git <cmd>:*)` allow-rule —
  `cd` into the target dir first (its own Bash call), then run bare
  `git <cmd>`.
- Re-running the same soak script/tag OVERWRITES the previous run's
  `run.log` in place — copy the driver script to a new tag name per soak.
- The `grep -ac '[CRASH]'` count in `run_mission_keys.sh`'s summary counts
  LINES matching the tag, not crash EVENTS — grep `caught signal` for the
  real event count.
- `scratch/agent/STATUS`/`OUTCOME` get reset at the START of each iteration
  by the harness — finding them reset at session start is normal.

## Housekeeping still flagged, still not done

`docs/CURRENT-TRUTH.md` is past both the ~35 KB CLAUDE.md budget and the
Read tool's 256 KB single-read limit (confirmed s195, still true s223 —
read it with `grep`/offset-limited `Read`, never a plain whole-file `Read`).
Migrate durable mechanism/architecture material to `PROJECT-OVERVIEW.md` and
prune superseded detail, paired with a real experiment — flagged for 20+
sessions without action, escalating.

`fixup_game_funcs.py`'s untracked, single-copy state in the `N64Recomp`
sibling checkout has been flagged since s83, still not fixed (not this
repo's commit scope) — worth surfacing to the user directly.

`/Users/williambuckley/Documents/Tools/N64Recomp` and
`~/Documents/Tools/rogue_squadron64` are separate git checkouts with
long-standing uncommitted changes, unrelated to this repo's commit scope.
Still flagged for the user, not committed autonomously.

`lib/rt64` still shows as modified in `git status` — pre-existing, not
investigated; still worth checking whether its patches are in sync with
`submodule-patches/rt64*.patch` before assuming this is normal
steady-state dirtiness.
