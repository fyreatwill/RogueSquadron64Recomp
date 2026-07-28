# NEXT work unit — guard `reinterpretTileRecord`'s assert (13th crash
# class, now confirmed recurring, current dominant pre-target-window
# blocker)

Read PORTING-STATE Session 195 in full before doing anything else (`grep -n
"^## Session 195" PORTING-STATE.md`); this file only has the actionable
summary. Also read docs/CURRENT-TRUTH.md's `-44` next-steps item (top of
the list) and the updated 13th-class catalog entry (`grep -n "13th,"
docs/CURRENT-TRUTH.md`).

## Why this is the next work unit (read before doing anything else)

s195 re-ran s194's mcontext soak (`mcontext2`, identical config) looking
for a 2nd occurrence of s194's `processSceneNode`-adjacent crash. It did
NOT recur (still single-occurrence, correctly parked — do not chase it
further per iron rule 4). Instead the soak died to a DIFFERENT crash:
`RT64::FramebufferManager::reinterpretTileRecord`'s
`assert("Unimplemented reinterpretation logic." && (...))`
(`lib/rt64/src/hle/rt64_framebuffer_manager.cpp:476-480`) — this is the
project's own 13th crash class, first seen at s96 and explicitly parked
"until 2nd recurrence." s195 IS that 2nd recurrence (~99 sessions later,
byte-for-byte identical backtrace). It fires at `decisionN~7968`, well
before the 9660-9792 target window, making it the current dominant
soak-blocker — the same role `queueGPUUploadTMEM` played before its s192
guard landed. `[scene-node-ptr-guard]` (s190) is still 0/5 fires across
every soak on record; the primary open goal-stack question (does the s190
fix work) is still completely untested.

## Do this, in order

1. Read `lib/rt64/src/hle/rt64_framebuffer_manager.cpp:439-480` (the whole
   `reinterpretTileRecord` function) and `lib/rt64/src/render/
   rt64_texture_cache.cpp:1286-1329` (the s192 `queueGPUUploadTMEM` guard —
   the pattern to mirror: `static int s_..._enabled = -1;` +
   `std::getenv` check on first call, then a bounded fire-counter log
   behind that env gate).
2. Replace the hard `assert("Unimplemented reinterpretation logic." &&
   (cond))` at line 476-480 with: compute `cond` into a named bool, and if
   it's false, log (gated by a new env var, e.g.
   `ROGUESQ_LOG_REINTERPRET_TILE_GUARD=1`, bounded counter, same style as
   `[tmem-zero-guard]`) and `return;` instead of dispatching the
   reinterpret — skip the unsupported format combo entirely rather than
   crashing. Keep the assert for the true-case path removed entirely (the
   guard IS the replacement, not an addition alongside it) — matches how
   s192's guard replaced the crash-causing path, not added a second check.
3. This is a `lib/rt64` edit — per hard rule, run
   `./submodule-patches/export.sh` (relative path from repo root) and
   `git add -A && git commit` the refreshed `submodule-patches/rt64.patch`
   in the SAME session, or the edit is lost at the next reset.
4. Pure `lib/rt64` runtime change — does NOT need the regen/fixup
   pipeline, just `cmake --build build --target RogueSquadron64Recomp -j`
   directly (`DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer`
   needed for Metal rebuilds).
5. Soak with the SAME config as `mcontext2`/`sceneptrguard5`
   (`scratch/agent/run_mcontext2.sh` is a ready template — copy to a new
   tag, e.g. `reinterptileguard1`) plus the new
   `ROGUESQ_LOG_REINTERPRET_TILE_GUARD=1` env var added. Discriminating
   outcomes:
   - **`[reinterpret-tile-guard]` (or whatever you name it) fires with
     sane fields AND the soak reaches further than decisionN=9792 with
     `[scene-node-ptr-guard]` finally firing** → best possible outcome,
     the s190 fix is finally testable — write it up as the headline
     finding, this becomes the new primary result.
   - **Guard fires (positive control confirmed) but soak still dies before
     9792 to something else** → guard is confirmed working, but a new
     blocker is now dominant — catalog it the same way this session
     catalogued the promotion of the 13th class, don't guess further,
     hand off to the next iteration.
   - **Guard never fires (0 count)** → either the guard is unreachable
     this run (need a forcing hook like s193's `ROGUESQ_TEST_FORCE_TMEM_
     ZERO` to get a positive control) or the crash doesn't recur a 3rd
     time — check which before concluding either way.

## Do not

- Do not re-touch the `processSceneNode` s194 lead (`far=rdram_base+
  0x80630062`, `processSceneNode+8772`) — still single-occurrence,
  non-recurring as of s195, out of scope per iron rule 4 until it recurs
  on its own.
- Do not re-touch `queueGPUUploadTMEM`'s guard (s192) or its s193 forcing
  hook — both closed and confirmed working, not implicated this session.
- Do not re-touch the `processSceneNode` node-pointer guard itself (s190)
  — still intact, still 0/5 fires, still the primary untested target
  question. This work unit is about REMOVING AN EARLIER BLOCKER so a soak
  can reach it, not about the guard itself.
- Do not re-touch the `[CRASH][siginfo]`/`[CRASH][mcontext]` dump (s194) —
  landed, confirmed via 2 positive controls now (SIGSEGV/SIGBUS at s194,
  SIGABRT at s195), permanent, no env gate needed.
- Do not re-attempt `otool`/`objdump`/`nm`/`lldb` this session unless you
  have concrete new evidence the allowlist changed (check
  `.claude/settings.json` first) — not needed for this work unit anyway
  (the assert site and its condition are already fully known from source).
- Do not guess at WHY the game emits this unsupported format combo (i.e.
  don't chase the game-side root cause of which framebuffer op needs this
  reinterpretation) — out of scope, matches how `queueGPUUploadTMEM`'s
  actual corrupted-width/height source was explicitly left out of scope
  at s192 (goal-stack M3).

## Blocking on a long-running soak (learned the hard way, still current)

Run the driver script as a single foreground Bash call with output
redirected to a log file and a generous timeout (~480s), OR launch with
`run_in_background: true` and block on the returned task ID via
`TaskOutput(task_id, block=true, timeout=300000-480000)` — this is the
correct way to synchronously wait for a soak before writing the exit-
contract docs; ending the turn while a background soak is still running
trips the Stop hook's exit-contract check prematurely.

## This session's environment notes (carry forward, still current)

- **Disassembly tools (`nm`, `otool`, `lldb`, `objdump`) are NOT on the
  Bash allowlist** — confirmed blocked at s193 AND s194; not re-attempted
  at s195 (not needed — source-level assert site was sufficient). Check
  `.claude/settings.json` for a new allow rule before trying a 3rd time.
- **The crash handler dumps siginfo + full ARM64 register file on every
  SIGSEGV/SIGBUS/SIGABRT** (`src/main/main.cpp`, `[CRASH][siginfo]`/
  `[CRASH][mcontext]` lines) — now confirmed via positive control on BOTH
  SIGSEGV/SIGBUS (s194) and SIGABRT (s195). Durable capability for all
  future crash investigations — check these lines first before reaching
  for a disassembler.
- `N64Recomp/fixup_game_funcs.py` is non-idempotent — running it a 2nd
  time (even just to check stdout) re-applies every patch again,
  duplicating them. NOT needed for this work unit (pure `lib/rt64` change,
  not a `RecompiledFuncs` patch) — skip the whole regen/fixup pipeline,
  just `cmake --build` directly.
- A pure `lib/rt64`/`lib/N64ModernRuntime`/`src/main` runtime change does
  NOT need the regen/fixup pipeline at all — just `cmake --build build
  --target RogueSquadron64Recomp -j` directly. This work unit is exactly
  that shape.
- Re-running the same soak script/tag **overwrites** the previous run's
  `run.log` in place — copy the driver script to a new tag name per soak.
- Running scripts under `RogueSquadron64Recomp/tools/agent/*.sh` /
  `scratch/agent/*.sh` directly gets denied — prefix with `zsh`.
- Compound `cd ... && zsh ...`/`cd ... && cmake ...` gets denied — use
  absolute paths, no `cd`, one command per Bash call (including a trailing
  `echo` after a redirected command, and `cmd &` backgrounding — use the
  `run_in_background` tool parameter instead of shell `&`).
- `git -C <path> ...` AND `cd <path> && git ...` (combined in one Bash
  call) both trigger approval prompts a non-interactive session can't
  clear — the `m lib/...` in top-level `git status` is a standing,
  permanent state from applied `submodule-patches/*.patch` files, not
  something to "fix" — only run `export.sh` when YOU add a new edit under
  `lib/` in the same session (this work unit does).
- `submodule-patches/export.sh` must be invoked as
  `./submodule-patches/export.sh` (relative) from the repo root —
  absolute path gets denied.
- A large `run.log` (millions of lines) is fine to `grep -c`/`grep -n >
  outfile` directly — just don't `cat`/`Read` it wholesale.
- `/scratch/` is entirely gitignored except `scratch/agent/NEXT.md`,
  `OUTCOME`, `STATUS` — new soak scripts/logs never need `git add`.
- Output redirection is sandboxed to the session's allowed working
  directories (this repo, N64Recomp, rogue_squadron64) — redirecting to
  `/tmp/...` gets blocked; use a path under `scratch/agent/` instead.
- Heredocs (`cat << 'EOF' > file`) get rejected as unparseable shell
  syntax by this session's Bash tool — use the Write tool to create files
  instead.

## Housekeeping still flagged, still not done

`docs/CURRENT-TRUTH.md` is now ~280+ KB (`wc -l` ~4050+ lines) — WAY over
the ~35 KB CLAUDE.md budget, and it now EXCEEDS the Read tool's 256 KB
single-read limit (confirmed s195 — a plain `Read` on the whole file
errored). This is no longer just a housekeeping nit: it is starting to
degrade the agent's ability to read its own memory in one shot. Migrate
durable mechanism/architecture material to PROJECT-OVERVIEW.md and prune
superseded detail, paired with a real experiment — flagged for many
sessions without action, escalating.

`/Users/williambuckley/Documents/Tools/N64Recomp` and
`~/Documents/Tools/rogue_squadron64` are separate git checkouts with
long-standing uncommitted changes, unrelated to this session. Still
flagged for the user, not committed autonomously.
