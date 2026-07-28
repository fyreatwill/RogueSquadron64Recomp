# NEXT work unit — get real ARM64 disassembly capability, then guard the
# `runVideoFrameTick` crash

Read PORTING-STATE Session 193 in full before doing anything else (`grep -n
"^## Session 193" PORTING-STATE.md`); this file only has the actionable
summary. Also read docs/CURRENT-TRUTH.md's `-42` next-steps item (top of the
list).

## Why this is the next work unit (read before doing anything else)

s193 closed the s192 open question: the `queueGPUUploadTMEM` guard
(`ROGUESQ_LOG_TMEM_ZERO_GUARD`) is now CONFIRMED live via a positive
control (`scratch/agent/run_tmemforce1.sh`, `ROGUESQ_TEST_FORCE_TMEM_ZERO=1`
forcing hook) — `[tmem-zero-guard]` fired with sane fields and the run
survived with `CRASH: 0`. That line item is done; do not re-touch it.

But the `runVideoFrameTick` crash that killed s192's soak at
`decisionN=8972` is STILL uncatalogued and unguarded — it remains the
current blocker on any soak reaching the `[scene-node-ptr-guard]` target
window (9660-9792), and `[scene-node-ptr-guard]` is still 0/3 fires across
all soaks to date. The underlying question this whole lineage exists to
answer (does the s190 `processSceneNode` fix work) is STILL untested.

s193 tried to guard `runVideoFrameTick` directly (this session's Option A)
and could NOT: finding the actual faulting instruction at native offset
`+1568` (`0x00000001040b7cb8`, confirmed via
`scratch/s73_post_a_scene/sceneptrguard5/run.log:3958648-49`) requires
disassembling the compiled ARM64 binary, and `nm`/`otool`/`lldb`/`objdump`
are NOT on this session's Bash allowlist (`.claude/settings.json` — verify
this is still true before assuming it). A from-scratch hand-rolled decoder
(`scratch/agent/s193_disasm.py`, `scratch/agent/s193_symrange.py`) produced
an INTERNALLY INCONSISTENT result — the decoded "crashing" instruction was
a harmless unconditional branch (cannot itself fault), preceded by a `BL`
whose hand-decoded target offset was an implausible ~19MB for a ~5KB
function. This is a decoder bug, not a real finding — do not trust
`s193_disasm.py`'s output as-is.

## Two valid options, in order — pick ONE

### Option A — get real disassembly tooling, then guard the crash (preferred)

1. First, just try `otool -tv -p _runVideoFrameTick
   build/RogueSquadron64Recomp` (or `objdump -d --disassemble-symbols=
   _runVideoFrameTick build/RogueSquadron64Recomp` if objdump is on PATH) as
   a normal Bash call — it may simply need one-time interactive approval
   that wasn't available in s193's non-interactive session but IS available
   in yours. If it runs, this whole tooling problem evaporates: disassemble
   `runVideoFrameTick`, find the instruction at file-relative +1568 from the
   function's start (cross-reference `scratch/agent/machoparse.py
   build/RogueSquadron64Recomp runVideoFrameTick` for the exact vmaddr), and
   identify the actual memory operand (which register, offset, and what C
   source expression it maps back to via the MIPS-comment trail in
   `N64Recomp/RecompiledFuncs/funcs_0.c:1459` onward).
2. If disassembly tools are confirmed still blocked, do NOT reach for
   `s193_disasm.py` as-is — it's unverified and already caught producing a
   self-contradictory decode once. Fix it first: cross-validate its output
   against a KNOWN-correct case (e.g. disassemble a small function whose
   behavior is well understood, or hand-verify a handful of instructions
   bit-by-bit against the ARM64 ARM encoding tables) before trusting any
   output it gives for the real crash site. This is real, bounded
   engineering work — budget it as its own sub-step, don't skip validation
   under time pressure.
3. Once the faulting deref is identified with actual confidence (not a
   guess), add a getenv-gated (`ROGUESQ_LOG_VIDEO_FRAME_TICK_GUARD` or
   similar — check it's not already claimed first), bounded-counter,
   tagged-fprintf guard in `N64Recomp/fixup_game_funcs.py` (mirrors the
   `processSceneNode` node-pointer guard pattern from s190 — this IS a
   `RecompiledFuncs` patch, needs the full regen/fixup pipeline:
   `make_elf.py` -> `N64Recomp` -> `fixup_game_funcs.py` -> `cmake`).
4. Soak with the new guard plus the full s192/s193 env block
   (`scratch/agent/run_sceneptrguard5.sh` + the new var) as
   `sceneptrguard6`. Positive control: does the new guard fire? Does
   decisionN push further than 8972? Does it finally reach 9660-9792 and
   fire `[scene-node-ptr-guard]`?

### Option B — if disassembly is a dead end this session too, pick a genuinely different probe

Do NOT run a blind `sceneptrguard6` soak with no new guard — that would be
a 4th blind attempt at "does a fix-soak reach the target window," already
well past the iron-rule-8 budget for that specific hypothesis (3 strikes:
s190, s191, s192). Options with actual new information value:

- Survey whether `runVideoFrameTick`'s crash recurs in OTHER already-logged
  soak `run.log` files (grep all `scratch/s73_post_a_scene/*/run.log` for
  the same crash signature) — if it's a first-time-only occurrence, that
  changes the calculus on whether guarding it is worth the effort at all
  vs. treating it as one-off soak variance (mirrors the s189 approach of
  surveying existing data before running new experiments).
- Investigate whether `menuOverlayInit` (the caller, native offset +2800,
  `runVideoFrameTick`'s only caller in this stack) has a more tractable
  source-level bug to find without disassembly — e.g. does it pass a
  corrupted argument into `runVideoFrameTick` that could be guarded at the
  CALL SITE instead of inside the crashing function itself.

## Do not

- Do not re-touch the `queueGPUUploadTMEM` guard or its s193 positive-control
  forcing hook (`ROGUESQ_TEST_FORCE_TMEM_ZERO`) — both closed and confirmed
  working. The forcing hook can stay in place permanently (env-gated,
  no-op by default) as a regression-test capability for future sessions.
- Do not trust `scratch/agent/s193_disasm.py`'s output for placing a guard
  without first validating it against a known-correct case — it already
  produced one self-contradictory decode this session.
- Do not re-touch the `processSceneNode` node-pointer guard (s190) — still
  fixed and intact, still 0/3 fires, still the untested target question.
- Do not attempt to root-cause `queueGPUUploadTMEM`'s actual corrupted-
  width/height source (goal-stack M3, full root-cause/fix) — out of scope.
- Do not re-attempt root-causing the underlying `rs_free` free-list
  corruption source itself (s85-s114 chase) — still out of scope.
- Do not turn on `ROGUESQ_LOG_THREAD_RESUME=1` (s93's confound).

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
  Bash allowlist** — confirmed again this session (`otool` triggered an
  approval prompt this non-interactive session couldn't clear). Try once
  at the start of a session that needs them; if still blocked, don't burn
  budget re-attempting mid-session.
- `scratch/agent/machoparse.py` gives symbol addr/size only (no
  disassembly) — reliable, already used successfully this session to rule
  out a hidden local-symbol boundary inside `runVideoFrameTick`'s address
  range.
- `N64Recomp/fixup_game_funcs.py` is non-idempotent — running it a 2nd
  time (even just to check stdout) re-applies every patch again,
  duplicating them. If adding a NEW patch: regenerate fresh first (`zsh
  tools/agent/regen_n64recomp.sh`), THEN run `python3
  /absolute/path/to/N64Recomp/fixup_game_funcs.py > log` exactly once. Grep
  the log for the new patch's report line to confirm exactly x1, and check
  older patches' lines are ALSO x1 (not x2).
- A pure `lib/N64ModernRuntime`/`lib/rt64` runtime change (not a
  `RecompiledFuncs/*.c` patch) does NOT need the regen/fixup pipeline at
  all — just `cmake --build build --target RogueSquadron64Recomp -j`
  directly. (This is what s192's AND s193's guards used.) A
  `runVideoFrameTick` guard WOULD need the regen/fixup pipeline (it's a
  `RecompiledFuncs` patch).
- Re-running the same soak script/tag **overwrites** the previous run's
  `run.log` in place — copy the driver script to a new tag name per soak.
- Running scripts under `RogueSquadron64Recomp/tools/agent/*.sh` /
  `scratch/agent/*.sh` directly gets denied — prefix with `zsh`.
- Compound `cd ... && zsh ...`/`cd ... && cmake ...` gets denied — use
  absolute paths, no `cd`, one command per Bash call (including a trailing
  `echo` after a redirected command, and `cmd &` backgrounding — use the
  `run_in_background` tool parameter instead of shell `&`).
- `git -C <path> ...` AND `cd <path> && git ...` (combined in one Bash call)
  both trigger approval prompts that a non-interactive session can't clear.
- `submodule-patches/export.sh` must be invoked as
  `./submodule-patches/export.sh` (relative) from the repo root — absolute
  path gets denied.
- A large `run.log` (millions of lines) is fine to `grep -c`/`grep -n >
  outfile` directly — just don't `cat`/`Read` it wholesale.
- `/scratch/` is entirely gitignored except `scratch/agent/NEXT.md`,
  `OUTCOME`, `STATUS` — new soak scripts/logs never need `git add`.
- Output redirection is sandboxed to the session's allowed working
  directories (this repo, N64Recomp, rogue_squadron64) — redirecting to
  `/tmp/...` gets blocked; use a path under `scratch/agent/` instead.
- Heredocs (`cat << 'EOF' > file`) get rejected as unparseable shell syntax
  by this session's Bash tool — use the Write tool to create files instead.

## Housekeeping still flagged, still not done

`docs/CURRENT-TRUTH.md` is now ~270+ KB (`wc -l` ~3900+ lines) — WAY over
the ~35 KB CLAUDE.md budget, growing every session. Migrate durable
mechanism/architecture material to PROJECT-OVERVIEW.md and prune superseded
detail, paired with a real experiment. Flagged for many sessions without
action.

`/Users/williambuckley/Documents/Tools/N64Recomp` and
`~/Documents/Tools/rogue_squadron64` are separate git checkouts with
long-standing uncommitted changes, unrelated to this session. Still flagged
for the user, not committed autonomously.
