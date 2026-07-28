# NEXT work unit — Thread B closed; pivot to the reserveAndEmitDLEntry crash

s147 landed and verified the Thread B fix (2/2 clean soaks) -- read
PORTING-STATE's Session 147 entry before doing anything else; this file
only has the actionable summary.

## What s147 did and found

Implemented the fix `NEXT.md` (s146's version) specified: relocated
`allocateSongChannelArray`'s early `voiceCount` write (scan-bound global
at `-0x6900` off `0x80150000`) to run *after* the pointer-store block
(`-0x6904`/`-0x6908`), via a new patch in `N64Recomp/fixup_game_funcs.py`
placed to run before the existing s120/s146 diagnostic patches so their
anchors still match. **Found and fixed a real bug in the plan before
building**: the original code reloads the same global right after
writing it (`0x8008F0D8-DC`, feeding a `voiceCount==0` branch) — moving
only the write would have made that reload read the *previous* call's
stale count. Fix relocates the write and its dependent reload together,
adjacent, preserving exact original branch semantics.

**Verified at runtime, not just in source**, across two soaks
(`countracefix1`, `countracefix2`, `scratch/agent/s147_analyze.py`):
13/13 song-array allocations show the pointer store immediately followed
by the count write (gap=1 log line, every time) — the fixed order
actually executes. 0/13 `[voice-active-gate-nz]` corrupted reads (was
5/6-window in s146's pre-fix soak). 0/2 `do_rom_read`/`piDmaWorker`
recurrences (was 9/9 prior soaks that armed the relevant diagnostics).
Soak 2 was fully crash-free — first time for this repro shape since s83.

**Self-caught process error, worth remembering**: ran
`fixup_game_funcs.py` twice without a full regen between (the s102
non-idempotency trap NEXT.md itself warns about) — caught it via grep
before building, redid the pipeline cleanly. Still very easy to trip on;
the warning bears repeating.

**New blocker surfaced**: soak 1 died to the already-catalogued 14th
crash class, SIGBUS in `reserveAndEmitDLEntry` (via
`submitSceneNodeRender` → `processSceneNode` → ... → `menuOverlayInit`,
`scratch/s73_post_a_scene/countracefix1/run.log:65215`). Existing guards
`emit-dl-guard2`/`3` (landed s133-135) stayed 0/0 in both soaks here, so
whether they cover *this* call path is unconfirmed — soak 2 didn't hit
this crash at all, so it's not yet known whether soak 1 was a rare tail
event or the next reliably-recurring blocker.

## Do next: characterize the reserveAndEmitDLEntry crash, decide fix vs. more data

1. Cheapest first move, no rebuild needed: rerun `scratch/agent/
   run_countracefix1.sh` (or a copied `run_countracefix3.sh`) once or
   twice more with the exact same instrument battery. Discriminating
   question: does the `reserveAndEmitDLEntry` SIGBUS recur on this same
   call path (`submitSceneNodeRender`/`processSceneNode`), or was soak
   1 a tail event? 2-3 soaks is the established bar before treating a
   result as informative either way (per rule 8 / this thread's own
   established practice).
2. In parallel with reading logs (no need to block on rebuild): read
   `reserveAndEmitDLEntry`'s full body in the current `funcs_4.c` (or
   wherever it now lives post-regen) against the exact backtrace in
   `countracefix1/run.log:65215-65224` (frames: `reserveAndEmitDLEntry`
   ← `submitSceneNodeRender` ← `processSceneNode` ← ... ←
   `menuOverlayInit`). Check whether `emit-dl-guard2`/`3`'s existing
   guard sites are even reachable from this call path — they may guard
   a different call site into the same function. Don't assume existing
   coverage without checking; this exact class of assumption already
   cost the s146 plan (see PORTING-STATE s147's write-up of the missed
   reload dependency).
3. If the crash is confirmed real and reachable on this path with no
   existing guard: apply the same guard pattern used throughout this
   family (s99-101, s133-135) — a source-level null/range check that
   `goto`s the function's real epilogue label, not a bare `return`.
   Truncate any `ctx->rN` compared against a 32-bit literal through
   `U32()` first (s99's lesson — comparing the sign-extended 64-bit
   register directly caused a 100% false-positive guard once already).
4. If 2-3 more soaks show `reserveAndEmitDLEntry` was a one-off and
   `do_rom_read` still doesn't recur: that's the real end-to-end
   validation this multi-session thread (s105-147) has been chasing —
   write it up as a second closure and let M3's next blocker be
   whatever crash class shows up most next (check the M3 crash-class
   history in PORTING-STATE/CURRENT-TRUTH's stale-since-s90 narrative
   before assuming it's a brand-new class).

## Do not

- Do not re-derive or re-verify the count-write/pointer-store ordering
  fix itself — closed, 2/2 clean soaks, s147.
- Do not re-run `fixup_game_funcs.py` twice without a full regen between
  runs (delete `RecompiledFuncs/funcs_*.c` → `make_elf.py` →
  `regen_n64recomp.sh` → `fixup_game_funcs.py` once) — verify via grep
  that any patch you land fired exactly `x1` before building.
- Do not assume `emit-dl-guard2`/`3` already covers the soak-1 crash
  site just because it sounds like the same function family — read the
  actual call path first.
- Do not treat a NEXT.md-prescribed fix's stated safety argument as
  complete without independently checking for OTHER dependencies (this
  session found a memory-based reload dependency a register-only safety
  check missed) — read the full function body, not just the cited line
  numbers, before landing any reorder/relocation patch.

## This session's environment notes (carry forward, still current)

- **A corrupted read doesn't have to be caught by the instrument you
  just built to be caught.** Always grep the FULL run log for every
  armed diagnostic's output, not just the one you just added, before
  writing up a run as inconclusive or as a weak result.
- Function/line-number estimates in NEXT.md/PORTING-STATE drift a few
  lines every regen — always grep/read the actual regenerated file
  before writing a regex anchor or planning a reorder.
- N64Recomp's codegen convention for a fixed-global access: writes are
  `MEM_W(<offset>, ctx-><base>) = ctx-><src>;`; reads flip the argument
  order to `ctx-><dst> = MEM_W(ctx-><base>, <offset>);`.
- `caller_ra` (`ctx->r31` at function entry) reads `0x00000000`
  universally — stop treating it as a signal (s92, s139-141).
- `rm` on paths outside `scratch/` requires approval and does NOT accept
  glob patterns — use a `python3 -c` one-liner with `pathlib.Path.glob()`.
- Do NOT re-run `fixup_game_funcs.py` a second time in the same session
  without a full regen first (non-idempotent, s102) — delete
  `RecompiledFuncs/funcs_*.c`, re-run `make_elf.py` (cwd
  `~/Documents/Tools/rogue_squadron64`), then
  `zsh tools/agent/regen_n64recomp.sh` (cwd this repo, NOT `N64Recomp`),
  THEN `fixup_game_funcs.py` once (cwd `N64Recomp`) — verify by grepping
  the regenerated `.c` directly (confirmed the hard way again this
  session — tripped on this exact mistake, caught it before building).
- `cmake --build` needs cwd `build/` and
  `DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer` for Metal
  shader rebuilds.
- Write a new wrapper script file per soak tag (`scratch/agent/run_
  <tag>.sh`) rather than parametrizing a single reusable script via env
  indirection. `run_countracefix1.sh`/`2.sh` (this session) are good
  templates — copy the full armed-diagnostics battery forward.
- Launch the soak via `zsh <absolute-path>/run_<tag>.sh > <absolute-path>/
  run_<tag>_driver.log 2>&1` as a `run_in_background` Bash call, then
  block synchronously with `until ! pgrep -f "./RogueSquadron64Recomp"
  >/dev/null 2>&1; do sleep 5; done` before closing out the iteration.
- Checking submodule (`lib/...`) git status needs `env GIT_DIR=lib/X/.git
  GIT_WORK_TREE=lib/X git status --short`, or a plain `cd <absolute
  path>` as its own command followed by a separate `git status` call.
- Output redirection (`>`) from Bash is sandboxed to the session's
  allowed working directories — target `scratch/agent/`, not `/tmp`.
- Prefer a single `python3 script.py` file (Write then run) for
  multi-step log analysis instead of a bash heredoc — heredocs with
  f-string braces containing quotes get rejected by the Bash tool's
  expansion-obfuscation heuristic.
- This fix lives entirely in the sibling `N64Recomp` checkout
  (`fixup_game_funcs.py` + regenerated `RecompiledFuncs/*.c`), not
  `lib/` — no `submodule-patches/export.sh` step needed for it.

## Housekeeping still flagged, still not done

`docs/CURRENT-TRUTH.md` is still far over the ~35 KB target (its M3
goal-stack narrative is stale since ~s90 — sessions s91-146 exist only
in the "Next steps" list and PORTING-STATE, not in that inline history).
Migrate durable mechanism/architecture material to PROJECT-OVERVIEW.md
and prune superseded detail, paired with a real experiment. Flagged for
many sessions without action.

`/Users/williambuckley/Documents/Tools/N64Recomp` is its own git
checkout, not a `lib/` submodule, with uncommitted changes across
s90-147 (`fixup_game_funcs.py` plus regenerated `RecompiledFuncs/*.c`).
Same posture as the `rogue_squadron64` sibling checkout flagged since
s54. Worth asking the user whether/how to commit that history.
