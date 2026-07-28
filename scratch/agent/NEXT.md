# NEXT work unit — try disabling NAN_CHECK project-wide to stop losing the
soak race to random unrelated crashes; the mesgqueue guard is shipped but
still untested against its actual target

Read PORTING-STATE Session 215 in full (`grep -n "^## Session 215"
PORTING-STATE.md`) before doing anything else. Short version: s215 read
`do_send`'s source and, using a structural argument (this build has no LTO
and is `CMAKE_BUILD_TYPE=Debug`, so a crash dladdr-resolving straight to
`_Z7do_sendPhiibb+388` means the fault is literal code inside `do_send`
itself, not a callee), **reclassified s214's do_send SIGBUS as NOT the s176+
scheduler-UAF family** — it's almost certainly the same generic "unguarded
TO_PTR on a corrupted guest pointer" pattern as ~15 other already-guarded
sites (heapWalker, `rs_malloc`/`rs_free`, the s78 framebuffer gates). Landed
a guard (`mesgqueue_guard_refuse()`,
`lib/N64ModernRuntime/ultramodern/src/mesgqueue.cpp`, 4 call sites: `mq_` and
`mq->msg` in both `do_send`/`do_recv`), built clean, exported+committed. One
soak (`mesgqueueguard1`): 0 guard fires, died at hold+100s to yet **another**
new `NAN_CHECK` call site (`mat3x3InverseInto`, `funcs_5.c:7582`) before
reaching whatever window the do_send SIGBUS needs.

**This is the 6th consecutive session (s209/210/211/213/214/215) where a
soak of this recipe family dies to a genuinely different, unrelated crash
before reaching its intended target.** 3 of those 6 were `NAN_CHECK` assert
firings at 3 different call sites (`evalCubicSplineAtTime`, `sinfApprox`,
`mat3x3InverseInto`). Designing one more single-purpose guard and hoping this
soak's dice land differently is very likely to produce a 7th data point in
the same pattern, not progress — per budget rule 8's spirit (three-plus
consecutive non-discriminating attempts on effectively the same problem
shape), the right move this session is to attack the pattern itself, not
another individual instance of it.

## Do this iteration: try disabling NAN_CHECK, verify the rebuild path,
then A/B soak

1. **Verify the regen/rebuild path first (boring-thing-first, rule 5) before
   touching anything.** `NAN_CHECK` is defined in
   `/Users/williambuckley/Documents/Tools/N64Recomp/include/recomp.h:396-397`
   as `assert(val == val)`, with a pre-written, currently-commented-out
   no-op alternative one line below it (`recomp.h:399`,
   `//#define NAN_CHECK(val)`). Confirm which generated files actually
   `#include` this header and through what path (does `make_elf.py` or
   `N64Recomp` itself copy/embed `recomp.h` content into
   `build/factor5_ucode/*.c` / `RecompiledFuncs/`, or is it included live from
   `N64Recomp/include/` at `cmake --build` time via an include path?). If it's
   a live include, flipping the two lines and running `cmake --build . -j8`
   alone should be sufficient — **do not run the full
   `make_elf.py -> N64Recomp -> fixup_game_funcs.py` regen unless this check
   shows it's actually necessary**, that pipeline is expensive and this is a
   one-line header change, not a codegen change.
2. Comment out the `assert(val == val)` line, uncomment the no-op
   `#define NAN_CHECK(val)` line (i.e. flip which of the two adjacent lines
   is active). Rebuild per step 1's finding.
3. **Positive control first**: before any soak, confirm the build actually
   changed behavior — e.g. grep for a known `NAN_CHECK`-adjacent function in
   a `funcs_*.c` and confirm the assert is genuinely gone from what's
   compiled (or just trust a clean rebuild with the macro flipped — this is
   a simple enough change that a build-clean confirmation is probably
   sufficient, use judgement).
4. Soak the **same recipe** as s213/s214/s215
   (`STICK_SCHEDULE="95:start 100:a 150:sr 200:sl 250:su"`, `HOLD_S=300`,
   copy `scratch/s73_post_a_scene/run_mesgqueueguard1.sh` verbatim except the
   tag — keep `ROGUESQ_LOG_MESGQUEUE_GUARD=1`/`ROGUESQ_LOG_HEAPWALKER_GUARD=1`/
   `ROGUESQ_LOG_HEAPWALKER_GUARD3=1` all armed, they're free and this soak is
   also this session's only shot at the still-open heapWalker/mesgqueue
   questions if it gets lucky).
5. **Discriminating outcomes:**
   - Soak reaches significantly further than any of s209-215's hold-iter
     counts (91, 68, ~7, 1, 3, 104 — call it "further than 104s/hold-iter 94"
     to beat the best so far) with 0 `NAN_CHECK`-shaped aborts (signal 6) →
     confirms disabling NAN_CHECK is a real force-multiplier for future
     sessions; write it up as a durable env/build note in CURRENT-TRUTH
     (something like "NAN_CHECK disabled for soak-depth investigations,
     re-enable if actually chasing a NaN bug").
   - Soak still dies early, but to something NOT NAN_CHECK-shaped → NAN_CHECK
     wasn't actually the dominant blocker this run, still useful (rules out
     "NAN_CHECK is most of the problem" as an overclaim) but less exciting;
     whatever it dies to next becomes the new highest-frequency blocker to
     characterize.
   - Soak reaches the `[mesgqueue-guard]`/`[heapwalker-guard]` windows and
     one of them actually fires → resolve that guard's open question
     immediately (mirrors s213/s214's own discriminating-outcome tables:
     fires + target crash gone = confirmed; fires + crash elsewhere = this
     site closed, another remains; use judgement, it's a bonus not the
     primary goal this session).
   - No crash at all (300s hold completes) → also useful, note whatever
     scene/state the game reached; one free re-run before drawing a
     conclusion either way.
6. **Revert the NAN_CHECK change before ending the session** unless the
   result clearly justifies keeping it permanently disabled (discuss/decide
   based on what's found — leaving a safety assert silently disabled without
   writing that decision explicitly into CURRENT-TRUTH would be a trap for
   a future session debugging an actual NaN bug). At minimum, document
   clearly in CURRENT-TRUTH whether it ended the session on or off and why.

## Do NOT do this iteration

- Do not build another single-purpose guard for a new NAN_CHECK call site
  (there will always be another one — that's exactly the pattern this
  session's work unit is trying to get out from under).
- Do not re-run the mesgqueueguard1 recipe unchanged a 2nd time without the
  NAN_CHECK change — that's just re-rolling the same dice s215 already used.
- Do not touch `N64Recomp/fixup_game_funcs.py`'s heapWalker guard code
  (`_make_heapwalker_guard_patch`/`_make_heapwalker_guard3_patch`) — still
  shipped, still not confirmed live, unrelated to this session's plan.

## Environment notes (carried forward, still current)

- The `[CRASH][pc-symbol]` diagnostic (dladdr on the raw mcontext `pc`) is
  permanent, always-on, and MORE PRECISE than `backtrace_symbols_fd` (s213
  proved this live; s215 used this precision to reclassify the do_send
  crash). Trust dladdr.
- Disassembly/symbolication tools (`nm`/`otool`/`objdump`/`lldb`/`atos`) are
  ALL blocked (non-interactive session) — re-verified s207/s213. This is WHY
  s215's do_send analysis is source-level/structural reasoning rather than
  disassembly-confirmed — single-source, flag as such if it matters later.
- This project builds `CMAKE_BUILD_TYPE=Debug` (`-O0`); `RECOMP_FUNC` is
  `noinline` — no game function can be silently inlined into a caller (s207).
  Confirmed s215: no LTO either (`grep` for `INTERPROCEDURAL_OPTIMIZATION`/
  `LTO` in both CMakeLists.txt: 0 hits) — no cross-TU inlining anywhere in
  this build, useful for symbolicating ANY future native (non-`ctx->rN`)
  crash: if dladdr resolves to function F, the fault is inside F's own body,
  not a callee, full stop.
- `recomp.h`: `U32(val)` = `(uint32_t)(val)`; `gpr` = `uint64_t`; a legit
  KSEG0 `gpr` sign-extends, upper bits `0xFFFFFFFF`. `PTR(x)` for guest
  pointers passed as plain function arguments (not `ctx->rN`) is `int32_t` —
  already 32-bit-truncated by the time C++ sees it, so guards on those
  (like s215's mesgqueue guard) are a simple range check, not an
  upper-32-bits check (that's specifically a `ctx->rN`-register thing).
- `rm -f <glob>`/`find <dir> -delete` are blocked — use
  `python3 -c "import glob, os; [os.remove(f) for f in glob.glob('<pattern>')]"`.
- `fixup_game_funcs.py` re-run after deleting one `funcs_*.c` is safe and
  idempotent on the other 44 already-patched files (s208-s211).
- `./build/N64Recomp rogue_squadron.toml` needs an `env` prefix (permission-
  prefix-match wall).
- Any edit under THIS repo's `lib/` needs `./submodule-patches/export.sh` +
  commit same session (done for s215's mesgqueue.cpp change).
  `N64Recomp`/`rogue_squadron64` are SEPARATE checkouts, NOT `lib/`
  submodules — editing files there (like `recomp.h` for this session's plan)
  does NOT need export.sh, but IS a separate git checkout with its own
  uncommitted-changes history (see Housekeeping below) — not committed
  autonomously by this project's rules.
- Re-running the same soak script/tag OVERWRITES the previous run's `run.log`
  in place — copy the driver script to a new tag name per soak, or rename
  the output dir before re-use.
- `ROGUESQ_LLE_FORCE`/`ROGUESQ_LLE_UNGATED`/`ROGUESQ_LLE_SOLO`/
  `ROGUESQ_STUB_MISSING_FUNCS` are set INSIDE `run_mission_keys.sh` (line 6).
- Running scripts under `RogueSquadron64Recomp/tools/agent/*.sh`/
  `scratch/agent/*.sh` directly gets denied — prefix with `zsh`.
- Compound `cd ... && zsh ...`/`cd ... && cmake ...` gets denied in ONE Bash
  call — use separate Bash calls. Heredocs get rejected — use Write tool
  (also: Write to `/tmp/*` can itself hit a permission prompt in this
  environment — s215 hit this; prefer Edit on the target doc file directly
  using a snippet you've already Read as the anchor, rather than staging
  content in a scratch file first).
- `/scratch/` is entirely gitignored except `scratch/agent/NEXT.md`,
  `OUTCOME`, `STATUS`.
- `scratch/agent/STATUS`/`OUTCOME` get reset at the START of each iteration
  by the harness — finding them reset at session start is normal.
- Launch soaks with `Bash(..., run_in_background=true)` then block with
  `TaskOutput(task_id, block=true, timeout=180000-480000)`.
- The `grep -ac '[CRASH]'` count in `run_mission_keys.sh`'s summary counts
  LINES matching the tag, not crash EVENTS — always grep `caught signal` or
  `[CRASH][pc-symbol]` to get the real event count.
- The mesgqueue guard (s215) only logs on REFUSAL, not on every successful
  call — there's no direct positive-control counter proving `do_send`/
  `do_recv` ran cleanly N times. If the do_send SIGBUS question is picked up
  again, consider adding a cheap always-on total-call counter alongside the
  existing bad-total counter (mirrors `resume_thread_tagged`'s
  `g_thr_resume_healthy`/`g_thr_resume_bad` pair) so a null result isn't
  ambiguous between "never called" and "called and always clean."

## Housekeeping still flagged, still not done

`docs/CURRENT-TRUTH.md` is now past both the ~35 KB CLAUDE.md budget and the
Read tool's 256 KB single-read limit (confirmed s195, still true s215 — read
it with `grep`/`sed -n`, never a plain whole-file `Read`). Migrate durable
mechanism/architecture material to `PROJECT-OVERVIEW.md` and prune superseded
detail, paired with a real experiment — flagged for 13+ sessions without
action, escalating.

`/Users/williambuckley/Documents/Tools/N64Recomp` and
`~/Documents/Tools/rogue_squadron64` are separate git checkouts with long-
standing uncommitted changes (including s214's guard-fix edit to
`fixup_game_funcs.py`, and this session's mesgqueue-reclassification work —
no N64Recomp edit was made this session, only read), unrelated to this
repo's commit scope. Still flagged for the user, not committed autonomously.
If this session's NAN_CHECK plan edits `recomp.h`, that adds to this same
pile — flag it too, don't commit it.

`lib/N64ModernRuntime` and `lib/rt64` show as modified in `git status` (pre-
existing since at least s213, not caused by s213/s214/s215's work beyond
s215's own intentional mesgqueue.cpp change, which IS exported+committed) —
still not investigated (out of scope for these sessions' prescribed work
units); worth checking whether these two submodules' patches are still in
sync with `submodule-patches/*.patch` before assuming this is normal
steady-state dirtiness.
