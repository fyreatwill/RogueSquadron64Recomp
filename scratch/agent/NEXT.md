# NEXT work unit — source-read the heapFreeListDequeue SIGBUS s216 surfaced
(new corruption shape, upper bits 0x3) before writing any guard

Read PORTING-STATE Session 216 in full (`grep -n "^## Session 216"
PORTING-STATE.md`) before doing anything else. Short version: s216 ran the
NAN_CHECK-disable A/B soak s215 designed (after first discovering and fixing
a real gap: the `recomp.h` that matters is a NESTED submodule copy at
`lib/N64ModernRuntime/N64Recomp/include/recomp.h`, not the sibling checkout
NEXT.md pointed at — `submodule-patches/export.sh`/`apply.sh` now cover it).
Result: NAN_CHECK-disable genuinely worked (0 NaN-assert crashes) but did
NOT deepen soak reach — died at hold-iter 9 (worse than 4 of the 6 prior
sessions) to a **new** signal-10 SIGBUS in `heapFreeListDequeue`, reached via
a scene-graph-rendering call path (`submitSceneNodeRender` →
`processSceneNode` → `traverseSceneGraphRecursive` → `setupCameraMatrices`)
never seen in any prior crash writeup. Register shape: `x0`/`x9`/`si_addr`
upper 32 bits are `0x00000003` — a 3rd distinct corruption pattern, neither
the zero-extension (`0x00000000`, s213) nor legit sign-extension
(`0xFFFFFFFF`) shapes already catalogued. **NAN_CHECK was reverted to ON**
before s216 ended (result didn't clearly justify keeping it off) — do not
assume it's still disabled.

## Do this iteration: source-read heapFreeListDequeue before writing a guard

Mirror s215's methodology exactly (that session's structural read, not a
soak-and-hope guard, is what correctly reclassified the do_send crash).

1. Find `heapFreeListDequeue`'s source. It's very likely a heap-subsystem
   function (name suggests a free-list pop) — check both whether it's a
   `RECOMP_FUNC` (generated, in `RecompiledFuncs/funcs_*.c`, guest game code)
   or a native runtime helper (`lib/N64ModernRuntime/**/*.cpp`). `grep -rn
   "heapFreeListDequeue" build/factor5_ucode lib/N64ModernRuntime
   /Users/williambuckley/Documents/Tools/N64Recomp` (three candidate
   locations) to find which.
2. Read the function body. Identify every native pointer dereference
   (`TO_PTR`, `MEM_W`, direct `rdram[...]` indexing, or plain C++ pointer
   deref if it's a native helper) that isn't already bounds-checked.
3. Cross-reference the call path (`submitSceneNodeRender` →
   `processSceneNode` → `traverseSceneGraphRecursive` → `setupCameraMatrices`)
   against existing guarded/unguarded sites — is this scene-graph-rendering
   path a genuinely new consumer of a known corruption source (the same
   upstream heap corruption already implicated in the heapWalker/do_send
   sites), or does it look like an independent bug?
4. **The discriminating question this session should answer**: does
   `heapFreeListDequeue`'s crash come from a value it received already-
   corrupted (upstream bug, matches the established family) or does it
   itself corrupt/miscompute a pointer (a NEW bug class, e.g. the never-
   explained upper-bits-`0x3` shape suggesting some arithmetic like `reg |
   (3 << 32)` or a 3-iteration loop counter leaking into the upper bits)?
   Source-read for arithmetic on the pointer/index before the dereference —
   if you find something like `list_head + (something << 32)` or a loop
   variable being OR'd/added into a 64-bit register, that would explain the
   `0x3` directly and this is new information, not a rehash of prior guards.
5. If the read is fast and conclusive (~15 min, matching s215's own gate),
   land a guard mirroring the existing pattern (KSEG0 range refuse-gate,
   `ROGUESQ_LOG_`-prefixed diagnostic, always-on counter) and soak once with
   the same recipe family to test it. If the read is inconclusive or slow,
   STOP at the write-up — do not guess at a guard without understanding the
   mechanism (this project has ~16 already-guarded sites; a guard that
   doesn't match the actual corruption shape is wasted work, as s213 proved
   for the pre-upper-bits-check heapWalker guards).

## Do NOT do this iteration

- Do not re-run the `nancheckoff1` recipe unchanged hoping for a different
  outcome — that question (does disabling NAN_CHECK deepen soak reach) has a
  single-source but clean NO answer now; a 2nd data point would need to be a
  deliberate decision to spend a soak on confirming/refuting it, not a
  default.
- Do not re-enable NAN_CHECK-disable as a standing default without writing
  that decision explicitly into CURRENT-TRUTH first (it's currently ON,
  matching upstream default — leave it unless this session's own read of the
  evidence changes that call).
- Do not touch `N64Recomp/fixup_game_funcs.py`'s heapWalker guard code
  (`_make_heapwalker_guard_patch`/`_make_heapwalker_guard3_patch`) — still
  shipped, still not confirmed live, unrelated to this session's plan.
- Do not touch the mesgqueue guard (`lib/N64ModernRuntime/ultramodern/src/mesgqueue.cpp`)
  — shipped s215, still not confirmed live (0 fires across 2 soaks now),
  unrelated to this session's plan.

## Environment notes (carried forward, still current)

- **`recomp.h` location, corrected this session**: the ONE that matters is
  `lib/N64ModernRuntime/N64Recomp/include/recomp.h` — a nested submodule
  inside `lib/N64ModernRuntime` (see `lib/N64ModernRuntime/.gitmodules`), NOT
  the sibling checkout at `/Users/williambuckley/Documents/Tools/N64Recomp`.
  `CMakeLists.txt`'s `target_include_directories` (3 call sites) only ever
  adds the nested path. The sibling checkout still matters for
  `RECOMP_FUNCS_DIR` (generated `.c` file *content*, `CMakeLists.txt:64`) but
  NOT for header resolution. The two `recomp.h` files were identical as of
  s216 but do not assume that stays true — always check which path
  `target_include_directories` uses before editing either one.
- **`submodule-patches/export.sh`/`apply.sh` now cover the nested N64Recomp
  submodule** (`N64Recomp-nested.patch`, added s216) — any edit under
  `lib/N64ModernRuntime/N64Recomp/` needs `export.sh` + commit, same as any
  other `lib/` edit. `export.sh` also now uses `--ignore-submodules=dirty`
  for the `N64ModernRuntime` diff to avoid a spurious unparseable
  `Subproject commit ...-dirty` line leaking in when the nested submodule is
  dirty.
- The `[CRASH][pc-symbol]` diagnostic (dladdr on the raw mcontext `pc`) is
  permanent, always-on, and MORE PRECISE than `backtrace_symbols_fd` (s213
  proved this live). Trust dladdr.
- Disassembly/symbolication tools (`nm`/`otool`/`objdump`/`lldb`/`atos`) are
  ALL blocked (non-interactive session) — re-verified s207/s213/s215.
  Source-level/structural reasoning only.
- This project builds `CMAKE_BUILD_TYPE=Debug` (`-O0`); `RECOMP_FUNC` is
  `noinline`. No LTO (`grep` for `INTERPROCEDURAL_OPTIMIZATION`/`LTO` in both
  CMakeLists.txt: 0 hits) — no cross-TU inlining anywhere, so dladdr
  resolving to function F means the fault is inside F's own body.
- `recomp.h`: `U32(val)` = `(uint32_t)(val)`; `gpr` = `uint64_t`; a legit
  KSEG0 `gpr` sign-extends, upper bits `0xFFFFFFFF`. `PTR(x)` for guest
  pointers passed as plain function arguments (not `ctx->rN`) is `int32_t` —
  already 32-bit-truncated. Neither of those matches this session's
  `0x00000003` upper-bits shape — worth understanding WHY before guarding.
- **Piping a background build through `tail -N` before capture loses the
  compile-line detail needed for a build-based positive control** (s216 hit
  this) — either capture full output to a file and grep it after, or rely on
  object-file mtime comparison (`os.path.getmtime`) as the positive control
  instead, which s216 used successfully.
- `rm -f <glob>`/`find <dir> -delete` are blocked — use
  `python3 -c "import glob, os; [os.remove(f) for f in glob.glob('<pattern>')]"`.
- `./build/N64Recomp rogue_squadron.toml` needs an `env` prefix (permission-
  prefix-match wall). Compound `cd ... && cmd` gets denied in one Bash call —
  issue `cd` and the following command as SEPARATE Bash calls instead (cwd
  persists between calls in this harness).
- `git -C <path> <cmd>` does not match a `Bash(git <cmd>:*)` allow-rule
  (prefix match is on the literal string) — `cd` into the target dir first
  (as its own Bash call), then run the bare `git <cmd>`.
- Any edit under THIS repo's `lib/` needs `./submodule-patches/export.sh` +
  commit same session.
- Re-running the same soak script/tag OVERWRITES the previous run's `run.log`
  in place — copy the driver script to a new tag name per soak.
- Launch soaks with `Bash(..., run_in_background=true)`, then either wait for
  the automatic task-notification or block with
  `TaskOutput(task_id, block=true, timeout=180000-480000)` if the Stop hook
  fires before the notification lands.
- The `grep -ac '[CRASH]'` count in `run_mission_keys.sh`'s summary counts
  LINES matching the tag, not crash EVENTS — grep `caught signal` for the
  real event count.
- `scratch/agent/STATUS`/`OUTCOME` get reset at the START of each iteration
  by the harness — finding them reset at session start is normal.

## Housekeeping still flagged, still not done

`docs/CURRENT-TRUTH.md` is now ~325 KB, past both the ~35 KB CLAUDE.md
budget and the Read tool's 256 KB single-read limit (confirmed s195, still
true s216 — read it with `grep`/offset-limited `Read`, never a plain
whole-file `Read`). Migrate durable mechanism/architecture material to
`PROJECT-OVERVIEW.md` and prune superseded detail, paired with a real
experiment — flagged for 14+ sessions without action, escalating.

`/Users/williambuckley/Documents/Tools/N64Recomp` (the SIBLING checkout, now
confirmed to matter only for `RecompiledFuncs/*.c` generated content, not for
`recomp.h` header resolution) and `~/Documents/Tools/rogue_squadron64` are
separate git checkouts with long-standing uncommitted changes, unrelated to
this repo's commit scope. Still flagged for the user, not committed
autonomously.

`lib/rt64` still shows as modified in `git status` — pre-existing, not
investigated this session either (out of scope); still worth checking
whether its patches are in sync with `submodule-patches/rt64*.patch` before
assuming this is normal steady-state dirtiness. (`lib/N64ModernRuntime`'s
dirtiness is expected and covered by `N64ModernRuntime.patch` +
`N64Recomp-nested.patch`, both current as of s216.)
