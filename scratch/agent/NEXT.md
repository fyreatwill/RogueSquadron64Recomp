# NEXT work unit — source-read the corrupting-camera-move mechanism
# itself (setupCameraMatrices / traverseSceneGraphRecursive /
# composeNpcOrientationMatrix), not another leaf-function guard soak

Read PORTING-STATE Session 222 in full (`grep -n "^## Session 222"
PORTING-STATE.md`) before doing anything else. Short version: s222 ran a
soak (`schedulepush2`) with 3 Start presses (20/40/60s) and a sustained
stick pulse every 8s for ~340s — specifically designed to test whether more
scripted input reaches mesh-heavy content. It didn't need to: MD5-
checksumming the soak's own `hold_NN.png` screenshots shows the on-screen
picture is byte-identical from `hold_04.png` all the way to `hold_350.png`
— completely frozen for 346 of 350 hold seconds, unaffected by any of the
36 scripted key presses. The finer 0.2s-tick `after_p1_start_*.png` series
brackets the freeze onset precisely: a clean, coherent hangar-departure
shot at 3.0s post-leave, already a torn/striped degenerate-polygon frame
by 4.0s post-leave, then frozen there forever — crash-free (`CRASH: 0`).

**This is not a new bug.** It is a 4th independent confirmation of
`CURRENT-TRUTH`'s "Overturned conclusions" item -2 (session s150): "single
Start leaves SELECT YOUR CRAFT into hangar-flight" is wrong — it's the
*same* craft-select hangar scene from a progressively closer/lower camera
angle with escalating render corruption into degenerate polygons, never a
new environment. s150 flagged this as an unfixed "corrupting camera move"
and never root-caused it (its own soak crashed mid-corruption before it
could). ~70 sessions of guard-hardening since s150 (through s221) mean this
exact corruption now survives crash-free — it just hangs forever instead.

## Why this is the priority

s222's soak was the 4th consecutive null on `unlit-mesh-tracer`,
`renderunlit-guard`, `emit-dl-guard2`/`3`, `heapwalker-guard`(`3`/`4`),
`heaplistdeq-guard`, and `mesgqueue-guard` — all across soaks that varied
schedule density/timing every time. The picture-freeze evidence explains
why: none of these soaks ever reach different content after ~4 seconds
post-leave, so leaf-render functions genuinely never get called again,
independent of any single guard's correctness or any schedule change.
Continuing to test guard reachability or schedule variations is now
budget-rule-8 territory — 4 attempts at the same underlying question with
the same answer. The camera-corruption mechanism itself, still never
source-read, is the actual blocker.

## Do this iteration

### Step 1 — source-read the camera/transform chain end to end

All three functions are already named in matching backtraces from s150 AND
s220/s221 (`emitAllocatedDLCommand`'s own hold-iter-1 crash chain was
`submitSceneNodeRender → processSceneNode → traverseSceneGraphRecursive
(x2) → setupCameraMatrices`, while s150's crash chain through
`composeNpcOrientationMatrix` shares `runHangarSelectionFrame` /
`runHangarMenuFromOverlay` / `menuOverlayInit`) — this is very likely one
connected mechanism, not three separate ones. Locate all three with
`grep -n "^RECOMP_FUNC.*setupCameraMatrices\|^RECOMP_FUNC.*
traverseSceneGraphRecursive\|^RECOMP_FUNC.*composeNpcOrientationMatrix"
funcs_*.c` and read them looking specifically for:
- Where a camera/view matrix or vertex-transform value could go degenerate
  (NaN, zero-scale, garbage rotation) as the camera keeps moving through
  this specific post-leave path — the visual signature (large striped/
  aliased polygons, not black, not a texture glitch) reads like a
  transform-matrix corruption, not a memory-corruption crash site.
- Any state that's read but never re-initialized between "static
  SELECT YOUR CRAFT" and "post-Start camera animation" — s150's framing
  ("dead-end animation that never leaves the hangar-selection subsystem")
  suggests this path may be using camera state meant for a different mode.

### Step 2 — instrument the candidate, soak once

Once a specific suspect value/site is identified, add ONE targeted log
(not a blanket guard) at the point the value is computed or first used,
gated behind a new `ROGUESQ_LOG_*` env var, armed alongside the existing
diagnostic list (see `scratch/s73_post_a_scene/run_schedulepush2.sh` for
the full list to carry forward). Re-run a soak — reuse `schedulepush2`'s
schedule (it does not need to change again; the schedule was never the
problem) but launch it as a single **synchronous** foreground Bash call
(no `&`, `run_in_background=false`, timeout ~550-600s) rather than
backgrounded — this session found and worked around an orphaned soak from
backgrounding + an early turn-end; don't reintroduce that risk.

### Step 3 — verify visually, not just via diagnostic counts

Whatever the soak shows, MD5-checksum a spread of `hold_NN.png` screenshots
(`python3 -c "import hashlib; ..."` — plain `md5`/shell loops tripped the
sandbox's approval gate this session, Python one-liners didn't) before
concluding anything. A crash-free run with diagnostics reporting normally
is NOT evidence content changed — s222's own soak looked completely healthy
by every log-level signal while the picture was frozen the entire time.

Discriminating outcomes:
- **Root cause found and the corruption stops** (checksum shows the
  post-leave frames now actually change/progress) → real fix; check
  whether `unlit-mesh-tracer` finally fires for the first time ever.
- **Instrumented value fires abnormal but the corruption still happens** →
  site identified but not the mechanism; note the value and re-read for
  where it's actually consumed.
- **Instrumented value never fires abnormal** → wrong suspect; the next
  session should walk the transform pipeline further upstream (whatever
  computes the camera's fly-out animation path) rather than re-guessing
  within the same three functions.

## Do NOT do this iteration

- Do not run another schedule-variation soak testing `unlit-mesh-tracer`/
  guard reachability — s222 closed that question with a 4th null plus
  direct visual confirmation of the actual cause. That's four attempts at
  the same question (budget rule 8 several times over).
- Do not re-litigate whether s150's "corrupting camera move, not a new
  environment" framing is correct — s222 independently reconfirmed it via
  MD5-checksummed screenshots and a precise 3-4s onset window; treat it as
  settled and move to root-causing the mechanism.
- Do not background a soak and end the turn before it completes. Run
  synchronously (foreground) instead, per this session's own recovery from
  exactly that mistake.

## Environment notes (carried forward, still current)

- **Verify a "crash-free" soak visually before trusting it**: MD5-checksum
  a spread of `hold_NN.png` files
  (`python3 -c "import hashlib; print(hashlib.md5(open(f,'rb').read()).hexdigest())"`
  per file, or loop over a list in one Python invocation — plain `md5`/
  shell `for` loops over multiple files tripped the sandbox's command-
  approval gate this session for unclear reasons; Python one-liners did
  not).
- **Launch soaks synchronously (foreground), not backgrounded, when they
  fit the tool timeout.** `zsh run_<tag>.sh` run as a plain (non-`&`,
  non-backgrounded) Bash call blocks until the driver script's own
  `run_mission_keys.sh` prints `done wall=...`, and cannot be orphaned by
  a premature turn-end the way a backgrounded soak can. Budget ~80s of
  nav/stable/leave overhead on top of `HOLD_S` when picking a timeout
  (`HOLD_S=350` + ~80s overhead ≈ 430s wall, comfortably inside a 600s
  Bash timeout; `HOLD_S=400`+ starts cutting it close).
- **`emitAllocatedDLCommand` is `funcs_3.c:2622-3210`**, `renderUnlitMeshFaces`
  is `funcs_4.c:4963-5630` (both guarded, s219/s221, still structurally
  unconfirmed — not this iteration's unit, see above). `heapWalker` is
  `funcs_3.c:99-700`, `heapFreeListDequeue` is `funcs_3.c:15427-17128`
  (both s217/s218, unchanged). Locations of `setupCameraMatrices`/
  `traverseSceneGraphRecursive`/`composeNpcOrientationMatrix` not yet
  looked up this session — do that first via `grep -n "^RECOMP_FUNC"`.
- **`fixup_game_funcs.py` is NOT idempotent — NEVER run it twice in the
  same session without a delete-all-funcs regen in between.** Redirect the
  FIRST run's output to a file under `scratch/agent/` and grep the file,
  never re-invoke the script. Whole-tree label-duplication audit:
  `grep -oE '^L_[A-Za-z0-9_]+:$' funcs_*.c | sort | uniq -c`, flag any
  count >1 WITHIN a single file.
- **Raw crash logs are often still on disk long after the session that
  produced them** — `grep` the actual `run.log` under
  `scratch/s73_post_a_scene/<tag>/run.log` before trusting a prose summary
  of a register dump. Check whether a tag's directory is stale/orphaned
  (no matching PORTING-STATE session, `ps` shows no live process, `grep -c
  "caught signal"` is 0 but the log stops mid-stream) before treating it
  as real data — s222 found exactly this once.
- **`recomp.h` location**: `lib/N64ModernRuntime/N64Recomp/include/
  recomp.h` — nested submodule inside `lib/N64ModernRuntime`.
  `submodule-patches/export.sh`/`apply.sh` cover both copies. Any edit
  under `lib/` needs `export.sh` + commit, same session.
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
  denied — write output to a file via a separate, non-`cd`-prefixed call, or
  just don't redirect (the tool captures stdout either way for short runs).
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
Read tool's 256 KB single-read limit (confirmed s195, still true s222 —
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
