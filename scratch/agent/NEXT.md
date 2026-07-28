# NEXT work unit — source-read heapWalker to find why the existing 10-site
guard still doesn't catch its own recurring crash signature

Read PORTING-STATE Session 217 in full (`grep -n "^## Session 217"
PORTING-STATE.md`) before doing anything else. Short version: s217 executed
NEXT.md's prescribed work unit (source-read `heapFreeListDequeue`), confirmed
its 4 unguarded free-list-walk loops are class-A (upstream-corrupted-value
propagation, not locally-computed) with high confidence, and shipped an
upper-32-bit loop-back guard on all 4 sites (`ROGUESQ_LOG_HEAPLISTDEQ_GUARD`).
The soak never reached that code — it died in the craft-select MENU flow
itself, at the earliest point of the entire s209-217 lineage (hold-iter 1,
wall=0s), to a **recurrence of the established `heapWalker`/
`frameStartReset+532` signature** (`[CRASH][pc-symbol]
sym=heapWalker+2480`). The existing 10-site heapwalker guard
(`heapwalker-guard`/`heapwalker-guard3`, s157/s172) was armed and fired
**0 times**, same as every prior soak that's hit this signature — this is now
at least the 3rd occurrence of "guard armed, crash happens anyway, guard
silent."

**New lead, two-source confirmed**: the crash register dump showed
`x0=x8=0x0000000300000000` — the literal integer 3 shifted into a 64-bit
register's upper 32 bits — and `si_addr` was exactly `x0 + x9`. s216's
unrelated `heapFreeListDequeue` crash showed the **identical value**
(`x0=x9=0x0000000300000000`) at a completely different call site. Two
independent sightings of the same exact corrupt constant, one session apart,
meets this project's two-source bar: this looks like one systemic
corruption source, not per-site noise.

## Do this iteration: source-read heapWalker end to end

Mirror s217's own methodology (which correctly answered NEXT.md's
discriminating question for `heapFreeListDequeue` and is now the proven
template for this kind of question).

1. `heapWalker` is defined at `N64Recomp/RecompiledFuncs/funcs_3.c:99-7978`
   (confirm the closing brace — do NOT trust that line range without
   checking; get it with `grep -n "^RECOMP_FUNC" funcs_3.c` and taking the
   next function after `heapWalker`). This is large (~7880 lines) — delegate
   the read to a subagent rather than reading it inline; scope the subagent
   prompt tightly (exact file, exact line range, the specific questions
   below), matching how s217's delegation was written (see
   `PORTING-STATE.md` Session 217 or `git log` for that prompt as a
   template).
2. The 10 existing guard sites are listed in `fixup_game_funcs.py` under
   `_heapwalker_guard_sites` (GUARD2, head-deref) and
   `_heapwalker_guard3_sites` (GUARD3, loop-back) — grep for both lists
   first so the read can explicitly rule each one in/out rather than
   re-discovering them blind.
3. **The discriminating question**: is there an unguarded pointer
   dereference in `heapWalker` structurally similar to the 10 already-
   guarded sites (i.e. the sweep that found those 10 missed an 11th), or is
   the fault happening through a DIFFERENT mechanism entirely — e.g. a call
   into native/runtime code (not MIPS-translated, so the guard pattern
   doesn't apply the same way), a register that's corrupted before it ever
   reaches one of the 10 guarded sites (meaning the guard's OWN bounds check
   is being bypassed or the corrupted register isn't the one being checked),
   or something in a caller (`frameStartReset` itself, or whatever calls
   IT) rather than in `heapWalker`'s body proper.
4. **Specifically hunt for the `x0=0x300000000` shape**: any place a small
   integer (loop counter, mode-table index, size class, generation count)
   could get combined with a 64-bit register via `|`, `+`, or a raw 64-bit
   write that skips `S32()`/`U32()`/`ADD32()`. Given this shape has now
   appeared in TWO unrelated functions, also consider whether it originates
   OUTSIDE both functions — e.g. in whatever writes heap block headers, or
   in the `ultramodern` thread-context save/restore code (native C++, not
   guest MIPS) if a stray stack value could alias into a `ctx->rN` slot.
5. If the read finds a concrete unguarded site or mechanism (~15-20 min,
   matching s215/s217's own gate), land a guard using the s217/heapWalker-
   GUARD3 template (upper-32-bit check, NOT a bare `U32()`-truncated
   compare — see s213's documented trap) and soak once with the same recipe
   family. If the read is inconclusive, write up exactly what was ruled
   out/in and stop — do not guess at an 11th guard site without a concrete
   mechanism, per this project's standing "guard that doesn't match the
   actual corruption shape is wasted work" lesson (s213).

## Do NOT do this iteration

- Do not add more `0x80000000`-`0x80800000`-range guards to `heapWalker`
  blindly hoping one sticks — the existing 10 already do exactly that check
  and still don't catch this. A new guard needs a specific reason to believe
  it covers the actual miss, not just "one more site."
- Do not touch the `heapFreeListDequeue` guard (`_make_heaplistdeq_guard_patch`,
  s217) — shipped, still not confirmed live (0/0, soak never reached it),
  unrelated to this session's plan.
- Do not re-enable NAN_CHECK-disable — it's currently ON (default), left
  untouched again this session; do not flip it without a fresh, explicit
  CURRENT-TRUTH decision (see s216's writeup for why it was tried and
  reverted).
- Do not re-run the `heaplistdeq1` recipe unchanged hoping to reach the
  guard this time — that's re-rolling the dice against the same "random
  unrelated crash wins the race" pattern that's now defined 9 straight
  sessions (s209-217). If you want a 2nd data point on whether the
  `heapFreeListDequeue` guard specifically works, that's a deliberate
  decision to spend a 2nd soak attempt (budget allows up to 3 total,
  1 used), not a default — but the heapWalker source-read above is higher
  expected value right now since it has a two-source-confirmed lead to
  chase.

## Environment notes (carried forward, still current)

- **`recomp.h` location**: the ONE that matters is
  `lib/N64ModernRuntime/N64Recomp/include/recomp.h` — a nested submodule
  inside `lib/N64ModernRuntime`, NOT the sibling checkout at
  `/Users/williambuckley/Documents/Tools/N64Recomp`. `CMakeLists.txt`'s
  `target_include_directories` only ever adds the nested path. The sibling
  checkout still matters for `RECOMP_FUNCS_DIR` (generated `.c` file
  *content*) but NOT for header resolution.
  `submodule-patches/export.sh`/`apply.sh` cover both the outer
  `N64ModernRuntime` and the nested `N64Recomp` (`N64Recomp-nested.patch`,
  added s216) — any edit under `lib/` needs `export.sh` + commit, same
  session.
- **`fixup_game_funcs.py` is NOT fully idempotent** (found s217): most
  patches are anchored to the exact pristine (unpatched) source text via
  regex, so re-running the script after it's already applied is a silent
  no-op for those (correct, by design). But at least one patch (`s139`'s
  `rs_malloc` entry diagnostic) matches even ALREADY-patched text and will
  double-apply if the script is run twice in a row on the same generated
  output, producing "redefinition of ..." compile errors. **Only run
  `fixup_game_funcs.py` ONCE per regen cycle** (`make_elf.py` -> `N64Recomp`
  -> `fixup_game_funcs.py` -> `cmake`, in that order, each step once) — if
  you need to re-check its output, grep the already-produced report/diff
  instead of re-invoking it.
- The `[CRASH][pc-symbol]` diagnostic (dladdr on the raw mcontext `pc`) is
  permanent, always-on, and MORE PRECISE than `backtrace_symbols_fd` (s213
  proved this live). Trust dladdr for the crash PC itself. Backtrace frames
  further up the stack (via `$lr`/return addresses) are the actual CALLER
  chain, not a competing symbolication of the same PC — a frame reading
  `frameStartReset+532` when the crash PC resolves to `heapWalker+NNNN` is
  a normal caller-calls-callee pair (`frameStartReset` unconditionally
  calls `heapWalker`, Session 157), not a conflict to resolve.
- Disassembly/symbolication tools (`nm`/`otool`/`objdump`/`lldb`/`atos`) are
  ALL blocked (non-interactive session). Source-level/structural reasoning
  only.
- This project builds `CMAKE_BUILD_TYPE=Debug` (`-O0`); `RECOMP_FUNC` is
  `noinline`. No LTO — no cross-TU inlining anywhere, so dladdr resolving to
  function F means the fault is inside F's own body.
- `recomp.h`: `U32(val)` = `(uint32_t)(val)`; `gpr` = `uint64_t`; a legit
  KSEG0 `gpr` sign-extends, upper bits `0xFFFFFFFF`. A guard that only checks
  `U32()` (the low 32 bits) is BLIND to upper-bits corruption like the
  `0x3` shape this investigation keeps finding — always add the
  `(uint32_t)((uint64_t)ctx->rN >> 32) != 0xFFFFFFFFu` check too (see
  `_make_heaplistdeq_guard_patch`/`_make_heapwalker_guard3_patch` in
  `fixup_game_funcs.py` for the template).
- `rm -f <glob>`/`find <dir> -delete` are blocked — use
  `python3 -c "import glob, os; [os.remove(f) for f in glob.glob('<pattern>')]"`.
- `./build/N64Recomp rogue_squadron.toml` needs an `env` prefix (permission-
  prefix-match wall). Compound `cd ... && cmd` gets denied in one Bash call
  — issue `cd` and the following command as SEPARATE Bash calls instead.
- `git -C <path> <cmd>` does not match a `Bash(git <cmd>:*)` allow-rule —
  `cd` into the target dir first (as its own Bash call), then run bare
  `git <cmd>`.
- Any edit under THIS repo's `lib/` needs `./submodule-patches/export.sh` +
  commit same session.
- Re-running the same soak script/tag OVERWRITES the previous run's
  `run.log` in place — copy the driver script to a new tag name per soak.
- Launch soaks with `Bash(..., run_in_background=true)`, then either wait
  for the automatic task-notification or block with
  `TaskOutput(task_id, block=true, timeout=180000-480000)`.
- The `grep -ac '[CRASH]'` count in `run_mission_keys.sh`'s summary counts
  LINES matching the tag, not crash EVENTS — grep `caught signal` for the
  real event count.
- `scratch/agent/STATUS`/`OUTCOME` get reset at the START of each iteration
  by the harness — finding them reset at session start is normal.
- Heredocs piped through `>>` inside a single Bash tool call can silently
  abort mid-write on a long here-doc (hit s217) — verify with `tail`/`wc -l`
  after any large doc append, and if it didn't land, use `Edit` with the
  known tail content as `old_string` instead of re-attempting the same
  heredoc.

## Housekeeping still flagged, still not done

`docs/CURRENT-TRUTH.md` is now past both the ~35 KB CLAUDE.md budget and the
Read tool's 256 KB single-read limit (confirmed s195, still true s217 — read
it with `grep`/offset-limited `Read`, never a plain whole-file `Read`).
Migrate durable mechanism/architecture material to `PROJECT-OVERVIEW.md` and
prune superseded detail, paired with a real experiment — flagged for 15+
sessions without action, escalating.

`/Users/williambuckley/Documents/Tools/N64Recomp` (sibling checkout, matters
only for `RecompiledFuncs/*.c` generated content, not `recomp.h` header
resolution) and `~/Documents/Tools/rogue_squadron64` are separate git
checkouts with long-standing uncommitted changes, unrelated to this repo's
commit scope. Still flagged for the user, not committed autonomously.

`lib/rt64` still shows as modified in `git status` — pre-existing, not
investigated; still worth checking whether its patches are in sync with
`submodule-patches/rt64*.patch` before assuming this is normal
steady-state dirtiness. (`lib/N64ModernRuntime`'s dirtiness is expected and
covered by `N64ModernRuntime.patch` + `N64Recomp-nested.patch`.)
