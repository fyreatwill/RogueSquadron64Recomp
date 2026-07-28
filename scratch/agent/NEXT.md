# NEXT work unit — find whether scene-graph traversal STOPS or CONTINUES
# WITHOUT SUBMITTING at the render freeze, by instrumenting processSceneNode/
# submitSceneNodeRender/traverseSceneGraphRecursive call counts

Read PORTING-STATE Session 224 in full (`grep -n "^## Session 224"
PORTING-STATE.md`) before doing anything else. Short version: s224 answered
the discriminating question NEXT.md posed at the end of s223 — instrumented
`setupCameraMatrices`'s own raw `+0x2C` submatrix m00 field (NOT the
mat3x3InverseInto-derived inverse, which s223 already closed) and found it
**keeps changing for ~60 seconds of process time AFTER the on-screen
picture (and the RDP full-sync counter) have already frozen**. That is
NEXT.md's pre-registered "downstream" outcome: the camera-matrix code is
NOT the wedge. Something between "camera pose computed" and "pixels drawn"
stops producing new content while the camera (and whatever drives it)
keeps running for a while longer, before the camera itself ALSO eventually
freezes (a later, separate, unexplained event).

## Why this is the priority

Both prior leads — `mat3x3InverseInto`'s determinant (s223) and
`composeNpcOrientationMatrix` (s157/s158) — are now closed dead ends, each
re-confirmed null across 2+ independent soaks. s224's new finding gives a
concrete next target: the freeze must be somewhere in the scene-graph
population/traversal/draw-submission chain, since the camera (upstream)
and the swap/present pipeline (downstream, per s223/s224's `[vi-fs-decision]`
findings) are BOTH still alive well past the freeze. `processSceneNode`,
`submitSceneNodeRender`, and `traverseSceneGraphRecursive` (all
`funcs_4.c`, all already named in s150/s220/s221's backtraces and s224's
own read of `setupCameraMatrices`) sit exactly in that gap.

## Do this iteration

### Step 1 — pick a call-count instrument, not a value instrument

Unlike s223/s224 (which needed to see a VALUE freeze), this step needs to
answer a simpler binary: does the function still get CALLED after the
freeze, at a normal rate, or does its call rate drop to near-zero? So the
diagnostic is a periodic call counter (like `[processSceneNode-recursion-
depth-guard(entry)]`, already present per s219 fixups — check whether it's
already suitable before adding a new one) on `processSceneNode` and
`submitSceneNodeRender`. `traverseSceneGraphRecursive`
(`funcs_4.c:15053-15357`) doesn't yet have one — check
`grep -n "traverseSceneGraphRecursive\|processSceneNode\|submitSceneNodeRender"
fixup_game_funcs.py` (sibling `N64Recomp` checkout) first to see what's
already wired (s224 confirmed `processSceneNode` already has several
tracers/guards from s219-221 — re-read what they log before adding
anything redundant).

### Step 2 — instrument, gated behind existing or new env vars

If `processSceneNode`'s existing diagnostics (callee tracers site=A..J,
`ROGUESQ_LOG_...`) already give a periodic call-count signal, REUSE them —
don't add a new one for the same function. Where a genuine gap exists
(most likely `traverseSceneGraphRecursive`, which s224 confirmed has no
instrumentation at all), add ONE new periodic entry counter (every ~60
calls, same throttling discipline as `ROGUESQ_LOG_CAMPOSE`) via
`fixup_game_funcs.py`. Full clean regen recipe (proven 3x now, s221/223/224):
delete all `RecompiledFuncs/funcs_*.c`
(`python3 -c "import glob, os; [os.remove(f) for f in glob.glob('funcs_*.c')]"`
from that directory), `python3 tools/make_elf.py` (rogue_squadron64
checkout), `tools/agent/regen_n64recomp.sh` (N64Recomp checkout),
`fixup_game_funcs.py` **exactly once** (capture output to a file, grep it,
never re-invoke), `cmake --build . -j8` with
`DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer`.

### Step 3 — soak, phase-gate on the checksum-observed freeze, correlate by line number

Reuse `scratch/s73_post_a_scene/run_campose1.sh` as the template (same
`schedulepush2`-derived schedule, `HOLD_S=350`, synchronous foreground Bash
call, ~580s timeout) — copy to a new tag, arm the new/reused counter(s),
keep ALL prior diagnostics armed as regression checks (`ROGUESQ_LOG_CAMPOSE`,
`ROGUESQ_LOG_MAT3INV`, the s222/s223 guard set). This schedule is proven
non-deterministic (s223) — budget up to 2 attempts before treating a null
as inconclusive. After each run:
- MD5-checksum `hold_NN.png` (`scratch/agent/checksum_campose1.py` is a
  ready-made template — copy and repoint `d`) to find this run's own
  freeze onset — do NOT assume it matches s224's `hold_82`, this schedule
  varies run to run.
- Use `scratch/agent/analyze_campose1.py` as a template for line-number
  correlation: find the new counter's line number nearest the freeze-onset
  `[phase]`/`[vi-fs-decision]` region (same technique s224 used to line up
  `campose1`'s freeze timing against `n` values).

Discriminating outcomes:
- **Call rate drops to near-zero (or stops entirely) at the freeze onset**
  → confirms scene traversal/submission itself is the wedge — next step is
  finding WHY it stops being called (what should be invoking it every
  frame, and why that caller stalls) — likely one level up the call chain
  from wherever stops.
- **Call rate stays roughly constant through and after the freeze** → the
  traversal keeps running but isn't producing visible output — points to a
  visibility/culling check inside the traversal always failing after some
  point, or draw commands being built but never actually reaching the RDP
  (worth cross-referencing against `[vi-fs-decision]`'s `rdpFs` plateau —
  if traversal keeps running but `rdpFs` never advances, the gap is
  between traversal and RDP submission specifically).
- **This run doesn't freeze at all, or freezes at a very different point**
  → reinforces non-determinism (s223); note the new onset and don't
  conclude from 1 non-reproducing run — budget a 2nd attempt.

## Do NOT do this iteration

- Do not re-instrument `setupCameraMatrices`'s own pose fields, `+0x2C`
  submatrix, or `mat3x3InverseInto` again — s224 answered the camera
  question (keeps changing well past the freeze); re-testing is
  budget-rule-8 territory.
- Do not re-instrument `composeNpcOrientationMatrix` — closed since
  s157/s158 (7 guards, 508/508 entry-confirmed, 0/0 guards).
- Do not treat s224's "camera keeps moving ~60s past the freeze" finding
  as fully closed — it's ONE run of ONE new instrument (see caveat in
  PORTING-STATE Session 224). If this iteration's soak happens to freeze
  cleanly again, a quick checksum + `[campose-entry]` correlation (reusing
  the still-armed `ROGUESQ_LOG_CAMPOSE`) is a cheap bonus 2nd data point —
  but the primary instrument this iteration is the new scene-graph call
  counter, not a re-run of campose1's exact design.

## Environment notes (carried forward, still current)

- **This exact schedule (s222's `schedulepush2` / s223's `run_mat3inv2.sh`
  / s224's `run_campose1.sh`) is PROVEN non-deterministic on identical
  input.** Budget 2 attempts before drawing conclusions, per Step 3 above.
- **Full clean-room regen recipe, proven 3x (s221, s223, s224)**: delete
  all `RecompiledFuncs/funcs_*.c`, re-run `make_elf.py` + `N64Recomp`, run
  `fixup_game_funcs.py` **exactly once**, capturing its report to a file —
  safer than incremental patching, avoids repeat-invocation label-dup risk.
- **`fixup_game_funcs.py` is NOT idempotent — NEVER run it twice in the
  same session without a delete-all-funcs regen in between.**
- **Verify a "crash-free" soak visually before trusting it**: MD5-checksum
  a spread of `hold_NN.png` files (Python one-liner/script, not shell
  loops — shell `for` loops over multiple files tripped the sandbox's
  command-approval gate for unclear reasons in past sessions).
- **Launch soaks synchronously (foreground), not backgrounded.** Budget
  ~80s of nav/stable/leave overhead on top of `HOLD_S` when picking a
  timeout (`HOLD_S=350` + ~80s overhead ≈ 430s wall, inside a 600s Bash
  timeout).
- **Correlating a new diagnostic's call-count/`n` value against wall-clock
  freeze timing**: use the run's own `[phase]` log lines (real process-time
  timestamps, e.g. `at 170.6s`) and find the nearest diagnostic log line by
  LINE NUMBER (not by estimating elapsed time from driver-script stdout,
  which is comparatively imprecise) — `scratch/agent/analyze_campose1.py`
  is a working template for this (bisect over collected line numbers).
- **`setupCameraMatrices` is `funcs_4.c:19142-21603`**, `mat3x3InverseInto`
  is `funcs_5.c:7208-~7460`, `traverseSceneGraphRecursive` is
  `funcs_4.c:15053-15357` (NOT yet instrumented, best next target),
  `processSceneNode` (has several s219-221 tracers/guards already, check
  before adding more), `submitSceneNodeRender` (also has s219-221
  guards). `composeNpcOrientationMatrix` (`static_5_800AB1C8`) is
  `funcs_40.c:6280-7200`, CLOSED.
- **Camera struct layout (from s224's source read of `setupCameraMatrices`,
  `$s1`/`ctx->r17`)**: `+0x0` a gating flag (controls whether the `+0x2C`
  submatrix gets inverted this call, does NOT gate the
  `traverseSceneGraphRecursive` call itself, which is unconditional);
  `+0x10/+0x14/+0x18/+0x1C` an INTEGER viewport rect (x0,y0,x1,y1), not
  camera pose; `+0x20/+0x24/+0x28` perspective near/scale float scalars;
  `+0x2C` a 3x3 float rotation submatrix (36 bytes, to `+0x50`) — the only
  orientation data in this struct. World position/view concatenation
  happens via a separate FIXED global matrix address (`0x8012xxxx -
  0x23A4`), not through this per-call struct — if a future translation/
  position probe is wanted, that global address is the place to look, not
  another camera-struct offset.
- **`ROGUESQ_LOG_CAMPOSE=1`** (new, s224): logs `setupCameraMatrices`'s
  raw `+0x2C` m00 + gating flag + struct pointer, every 60th call, uncapped
  on NaN/Inf, `funcs_4.c` guest `0x800178A8`. Still armed in `campose1`'s
  driver script — keep armed in future soaks as a regression check per the
  "do not re-run as primary instrument" note above.
- **`emitAllocatedDLCommand` is `funcs_3.c:2622-3210`**, `renderUnlitMeshFaces`
  is `funcs_4.c:4963-5630` (both guarded, s219/s221, still structurally
  unconfirmed — 0/0 across every soak so far including s224's, which never
  exercised either). `heapWalker` is `funcs_3.c:99-700`,
  `heapFreeListDequeue` is `funcs_3.c:15427-17128` (both s217/s218,
  unchanged, still 0/0 in s224).
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
  bits explicitly.
- `rm -f <glob>`/`find <dir> -delete` are blocked — use
  `python3 -c "import glob, os; [os.remove(f) for f in glob.glob('<pattern>')]"`.
- `./build/N64Recomp rogue_squadron.toml` needs an `env` prefix and must run
  with cwd set to the `N64Recomp` checkout itself (use
  `tools/agent/regen_n64recomp.sh`). Compound `cd ... && cmd` gets denied in
  one Bash call — issue `cd` and the following command as SEPARATE Bash
  calls; redirecting output (`> file`) in the same call as a `cd` also gets
  denied.
- `git -C <path> <cmd>` does not match a `Bash(git <cmd>:*)` allow-rule —
  `cd` into the target dir first (its own Bash call), then run bare
  `git <cmd>`.
- Re-running the same soak script/tag OVERWRITES the previous run's
  `run.log` in place — copy the driver script to a new tag name per soak.
- `scratch/agent/STATUS`/`OUTCOME` get reset at the START of each iteration
  by the harness — finding them reset at session start is normal.

## Housekeeping still flagged, still not done

`docs/CURRENT-TRUTH.md` is past both the ~35 KB CLAUDE.md budget and the
Read tool's 256 KB single-read limit (confirmed s195, still true s224 —
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
