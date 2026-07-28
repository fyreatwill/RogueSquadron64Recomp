# NEXT work unit — dump the corrupted free-list node in rs_malloc (22nd crash class)

s164 ran attempt 2/3 of the audio-drain/H-INPUT soak (`audiodrain2`, no
rebuild — same recipe as s163's `audiodrain1`) and it died even earlier
than attempt 1 (hold-iter 2 vs. hold-iter 6), **not** to a recurrence of
`emitAllocatedDLCommand`/s132 but to a brand-new, never-before-seen 22nd
crash class: SIGBUS **inside `rs_malloc` itself** (the guest heap
allocator), called from `rebuildActiveDisplayObjectList` with fixed, sane
arguments (`size=1024 flags=0`) — identical to 14 immediately-prior
successful calls the same run. Read PORTING-STATE Session 164 before doing
anything else; this file only has the actionable summary.

## What s164 established (read before instrumenting)

- `rs_malloc` (`N64Recomp/RecompiledFuncs/funcs_0.c:2745`) is a genuine
  free-list-walking allocator, not a stub. After `ensureHeapInitialized`
  and an `osRecvMesg` lock, it walks a linked list starting around
  `L_80001BB0`: for each node it loads a `flags` halfword
  (`MEM_HU(a0, 0)`) and a `size` word (`MEM_W(a0, 0x4)`), and on
  "not-last-node" advances `a0 = a0 + size + 0x10` to the next node
  (`L_80001BF4`/`L_80001C00`, loop back to `L_80001BC4`).
- The crash backtrace is `rs_malloc + 492` ← `rebuildActiveDisplayObjectList
  + 224` ← `static_5_800AAD9C` (known dispatcher, not itself a bug site,
  per the closed s157 question — do not re-open that) ← `static_5_800C6854`
  ← `menuOverlayInit`.
- The already-armed `[rs-malloc]` log (`ROGUESQ_LOG_RS_MALLOC=1`, already
  in `scratch/agent/run_audiodrain2.sh`'s env block — free, no new
  instrument needed for this alone) shows **14 identical successful
  calls** (`ptr=0x801CD7D0 size=1024 flags=0x0`) immediately before the
  crash, and the crashing call has **no matching log line** — meaning it
  faulted mid-walk, before `rs_malloc`'s own return/log statement. This
  rules out "always fails on this input" — the allocator's own bookkeeping
  went bad between two otherwise-identical calls.
- This pattern-matches (does NOT yet prove identical to) the long-parked
  "shared heap/struct-field corruption" thread from s85–s114
  (`voice+0x34`, DMA-ring `devAddr`, OSThread context corruption) — a
  fixed struct offset (here: a free-list node's `size` field) going bad
  between calls is the same shape of bug. Worth testing directly rather
  than treating as yet another independent crash class to whack down.

## Do next

1. **Instrument the free-list walk directly** (no rebuild needed for
   anything else this session — batch this with whatever else you land).
   In `N64Recomp/fixup_game_funcs.py`, add a diagnostic patch to
   `rs_malloc` (`funcs_0.c`, file-scope it to that file per the project's
   own hard-won lesson about cross-file guard/regex collisions — see
   s100's false positive) that logs each free-list node visited during
   the walk: node address (`a0`/`ctx->r4`), `flags` halfword, `size` word,
   BEFORE the advance (`a0 = a0 + size + 0x10`). Gate behind a new env var,
   e.g. `ROGUESQ_LOG_RS_MALLOC_WALK=1`. Follow the existing `[rs-malloc]`
   log's style/location in the same file for consistency.
   - Positive control: it should fire many times per `rs_malloc` call in
     normal operation (multiple nodes per walk) — confirm a healthy run
     shows sane, small, plausible `size` values before trusting a crash
     capture.
2. **Full regen** (delete `RecompiledFuncs/funcs_*.c` → `python3
   tools/make_elf.py` (cwd `~/Documents/Tools/rogue_squadron64`) → `zsh
   tools/agent/regen_n64recomp.sh` (cwd this repo) → `fixup_game_funcs.py`
   **exactly once**, redirect its output to a log file, never re-invoke
   just to check) → `cmake --build` (cwd `build/`, need
   `DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer`).
3. **Copy `run_audiodrain2.sh` to `run_audiodrain3.sh`** (RUNTAG=audiodrain3
   in the final `run_mission_keys.sh` line), add
   `export ROGUESQ_LOG_RS_MALLOC_WALK=1` to its env block (keep every other
   flag — this is soak attempt 3/3 for the H-AUDIO-DRAIN/H-INPUT question,
   so don't waste it: keep the full existing flag set, just add the one
   new instrument). Run it, block synchronously on process exit (see
   "Blocking" note below), then read
   `scratch/s73_post_a_scene/audiodrain3/run.log`.
4. **Branch on the outcome:**
   - **If `rs_malloc` crashes again**: check the walk-log immediately
     before the crash. A `size` value that decodes as ASCII text (like the
     DMA-ring family's `"wing"`/`"lcre"` pattern) or another clearly
     implausible value **confirms** the shared-corruption-family
     hypothesis directly — a real, writable finding linking two previously
     separate investigations. A merely-large-but-plausible-looking value
     would be inconclusive; say so.
   - **If it reaches the stall window (hold+~90s+) and stalls as before**:
     this was the original H-AUDIO-DRAIN/H-INPUT question — check
     `[audio-drain-enter]`/`[audio-drain-heartbeat]`/`[audio-drain-exit]`
     against the stall's onset (`grep -n "vi-fs-decision.*stalled=1"`). An
     entry with no exit and climbing heartbeats confirms H-AUDIO-DRAIN; if
     the stall clears after the `95:start`/`100:a` presses instead, that's
     H-INPUT. This is the 3rd and FINAL allowed attempt at this exact
     recipe (budget rule 8) — do not run a 4th unmodified repeat regardless
     of outcome. If still inconclusive, park the blind-soak approach and
     write up the walk-log findings (even a null result on the walk-log is
     informative at this point) as the next work unit's starting point.
   - **If it dies to yet another different crash**: catalogue it (23rd if
     new), note whether the walk-log fired anything useful incidentally,
     and treat the recipe itself as too unstable pre-cutscene to keep
     probing blind — the next work unit should pivot to characterizing/
     guarding whichever crash class is currently blocking furthest, not
     another identical soak.

## Do not

- Do not re-open the s157 `static_5_800AAD9C` dispatcher question — it's a
  pass-through frame in this crash's backtrace, not the bug.
- Do not treat this as a recurrence of `emitAllocatedDLCommand`/s132 — it
  is a different function, different call chain, genuinely new (22nd)
  class. Don't re-litigate s133-135's closed work.
- Do not spend a 4th soak attempt on the unmodified `audiodrain*` recipe
  after this one (attempt 3/3) regardless of outcome — per rule 8, park
  and pivot instead.
- Do not re-run `run_subtitleguard1.sh`/`run_subtitleguard2.sh` (s160-162,
  answered) or reopen the s159 `loadDrawState`/15th-class question
  (closed s157).

## Blocking on a long-running soak (learned the hard way this session)

`until ! pgrep -f "RogueSquadron64Recomp" ...` as a polling condition is
broken when run via the Bash tool's `run_in_background` — the wrapper
shell's own command line contains the literal string
"RogueSquadron64Recomp" (from the pgrep pattern text itself), so `pgrep -f`
matches the wrapper and the loop never exits even after the game process
is actually gone. Prefer polling on something that can't self-match, e.g.
`until ! pgrep -x RogueSquadron64Recomp >/dev/null 2>&1; do sleep 10; done`
(`-x` = exact process-name match, not full-command substring) or just
check `scratch/agent/run_audiodrainN_driver.log` for the `--- done ---`
sentinel line the driver script itself prints on completion. Either way,
after starting a background wait, verify completion by reading the driver
log / checking `ps -p <pid>` directly rather than trusting the polling
loop's own exit.

## This session's environment notes (carry forward, still current)

- **CRITICAL: `fixup_game_funcs.py` is non-idempotent even within
  checking its own output** — running it a 2nd time (even just to `grep`
  stdout) re-applies every patch a 2nd time, duplicating them. Redirect
  output to a log file on the ONE invocation; never invoke a 2nd time
  "just to see the output again."
- `nm`, `otool`, `lldb` are NOT on the Bash allowlist — use
  `scratch/agent/machoparse.py` for Mach-O symbol reads if ever needed.
- The actual per-tag guard/control counts live in
  `scratch/s73_post_a_scene/<tag>/run.log`, not the driver log (driver log
  only has the summary block + phase/key timeline).
- Reading a `RECOMP_FUNC` body directly from
  `N64Recomp/RecompiledFuncs/funcs_*.c` (via `grep -n "RECOMP_FUNC void
  <name>"`) is far more reliable than trusting a `symbol_files/*.txt`
  comment.
- `git -C <path> status` from the Bash tool triggers an approval prompt
  (treated like a directory-changing compound command) — use a separate
  `cd <path>` Bash call followed by a separate command in the next call
  instead (working directory persists between Bash calls in this
  session).
- Reading screenshots directly (the `Read` tool on a `.png`) remains
  ground truth for scene identity.
- `rm` on paths outside `scratch/` requires approval and does NOT accept
  glob patterns.
- Output redirection (`>`) from Bash is sandboxed to the session's allowed
  working directories — target `scratch/agent/`, never `/tmp`.
- `cmake --build` needs cwd `build/` and
  `DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer`.
- `lib/N64ModernRuntime` and `lib/rt64` always show as "modified content"
  in the parent repo's `git status` — this is the project's normal,
  long-standing state (months of uncommitted patches mirrored in
  `submodule-patches/*.patch`), not new drift. Only run
  `submodule-patches/export.sh` + commit if you actually edit something
  under `lib/` yourself this session.

## Housekeeping still flagged, still not done

`docs/CURRENT-TRUTH.md` is still far over the ~35 KB target — migrate
durable mechanism/architecture material to PROJECT-OVERVIEW.md and prune
superseded detail, paired with a real experiment. Flagged for many
sessions without action.

`/Users/williambuckley/Documents/Tools/N64Recomp` is its own git checkout,
not a `lib/` submodule, with uncommitted changes across s90-164
(`fixup_game_funcs.py` plus regenerated `RecompiledFuncs/*.c`). Same
posture as the `rogue_squadron64` sibling checkout flagged since s54.
Worth asking the user whether/how to commit that history.

`~/Documents/Tools/rogue_squadron64` also still carries pre-existing
uncommitted `symbol_files/*` changes from earlier sessions (unrelated to
this session's work). Still flagged for the user, not committed
autonomously.
