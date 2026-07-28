# NEXT work unit — Thread B closed (2nd confirmation); pick (a) firm up reserveAndEmitDLEntry's rate, or (b) find the mission-entry input

s148 reran the exact countracefix soak battery a 3rd time (no code
change) and got a 2nd straight fully crash-free run -- read
PORTING-STATE's Session 148 entry before doing anything else; this file
only has the actionable summary.

## What s148 did and found

Source-read `reserveAndEmitDLEntry` (`N64Recomp/RecompiledFuncs/
funcs_3.c:14487`) against soak 1's exact backtrace
(`scratch/s73_post_a_scene/countracefix1/run.log:65215`) before
instrumenting, per this thread's own established practice. Found
`emit-dl-guard2`/`3` (s133-135) actually live in a **different
function**, `emitAllocatedDLCommand` (`funcs_3.c:2412`) -- confirms
s147's open "is this guard's coverage of this call path unconfirmed?"
question with a definite **no, it doesn't cover it at all**, they just
share a name-adjacent function family. The real crash traces into
`findAndUnlinkSmallestEntry` (`funcs_6.c:12472`), a bucketed best-fit
free-list allocator walking singly-linked lists over fixed globals at
`0x8011xxxx`/`0x8012xxxx`.

Reran the exact same battery a 3rd time (`countracefix3`, no rebuild):
**fully crash-free** (`CRASH: 0`, 5920 LLE tasks, process alive at 58s
wall-clock, killed on schedule not by a signal). Combined across the
3-soak countracefix battery (s147 soak1/2 + s148 soak3):
**`do_rom_read`/`piDmaWorker` is now 0/3** -- Thread B (s105-148) is
closed with two independent clean confirmations, not one.
**`reserveAndEmitDLEntry` is 1/3** -- a rare tail event in the
already-catalogued 14-class crash family (17+ classes catalogued total
across this project), not yet a reliably-recurring blocker. No guard
written -- 1/3 doesn't clear this thread's own bar for "confirmed
reachable and recurring" before writing a fix.

**M3 status check (not advanced this session):** the 58s crash-free
stretch was entirely inside the pre-mission **SELECT YOUR CRAFT**
menu scene (`vi_width` stayed on the 512/640 menu pair the whole run).
M3's "done when" bar needs 60s of *in-mission* rendering -- this result
demonstrates menu-scene stability, not mission-scene stability.

## Do next: pick one, per this session's own two-branch recommendation

**(a) Firm up `reserveAndEmitDLEntry`'s rate (lower-risk, incremental):**
1. Copy `scratch/agent/run_countracefix3.sh` to `run_countracefix4.sh`
   (same battery, tag `countracefix4`), rerun. No rebuild needed.
2. Discriminating question: does the crash recur (2/4, worth guarding)
   or stay rare (1/4, park it and move to (b))? 2-3 soaks total on a
   hypothesis is this project's own established bar (rule 8) -- this
   would be the 4th, so treat whatever this soak shows as the answer,
   don't spend a 5th without a new angle.
3. If it recurs: guard `findAndUnlinkSmallestEntry`'s free-list walk
   using the same pattern as every prior guard in this family (s99-101,
   133-135) -- a source-level null/alignment check that `goto`s the
   real epilogue, `U32()`-truncate any `ctx->rN` compared against a
   literal (s99's lesson).

**(b) Find the mission-entry input from SELECT YOUR CRAFT (higher-value,
unexplored):** this is new territory -- `run_mission_keys.sh`'s
`PROBE_KEYS`/stick schedule was built to exercise the hold window for
crash-hunting, not to test what actually leaves the craft-select menu
into a mission. Read `run_mission_keys.sh` and the menu state machine
notes in `docs/CURRENT-TRUTH.md` (search "SELECT YOUR CRAFT") for what's
already known about this menu's controls, then try a driven soak that
holds a candidate mission-entry input (likely another `a`/start
variant, or a d-pad/stick selection before confirming) instead of just
sticks during the hold window. This is the path toward actually
attempting M3's "done when" bar rather than more menu-scene stability
soaking.

Given (a) is cheap (one more soak, no new code) and (b) is genuinely new
work, a reasonable order is: run (a) first since it's already queued and
free, then spend the bulk of the next session's budget on (b) regardless
of (a)'s outcome -- (a) at 1/4 or 2/4 doesn't change that M3 progress
needs (b) either way.

## Do not

- Do not re-derive or re-verify the count-write/pointer-store ordering
  fix (Thread B) -- closed, 3/3 clean `do_rom_read` non-recurrences
  across s147-148.
- Do not assume `emit-dl-guard2`/`3` covers any part of
  `reserveAndEmitDLEntry` -- confirmed s148 they live in a different
  function entirely (`emitAllocatedDLCommand`).
- Do not write a guard for `reserveAndEmitDLEntry`/
  `findAndUnlinkSmallestEntry` without first confirming a recurrence --
  at 1/3 it does not clear this thread's own "reachable and recurring"
  bar yet.
- Do not re-run `fixup_game_funcs.py` twice without a full regen between
  runs (delete `RecompiledFuncs/funcs_*.c` → `make_elf.py` →
  `regen_n64recomp.sh` → `fixup_game_funcs.py` once) — verify via grep
  that any patch you land fired exactly `x1` before building.

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
  the regenerated `.c` directly.
- `cmake --build` needs cwd `build/` and
  `DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer` for Metal
  shader rebuilds.
- Write a new wrapper script file per soak tag (`scratch/agent/run_
  <tag>.sh`) rather than parametrizing a single reusable script via env
  indirection. `run_countracefix3.sh` (this session) is a good template
  — copy the full armed-diagnostics battery forward.
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
- Multi-statement Bash commands (`&&`, `;`, pipes like `| head`) may
  require interactive approval even for read-only commands (e.g. `nm`,
  `dwarfdump`) in this session's sandbox — prefer single simple commands
  or redirect to a file and Read it instead of piping.
- This fix lives entirely in the sibling `N64Recomp` checkout
  (`fixup_game_funcs.py` + regenerated `RecompiledFuncs/*.c`), not
  `lib/` — no `submodule-patches/export.sh` step needed for it.

## Housekeeping still flagged, still not done

`docs/CURRENT-TRUTH.md` is still far over the ~35 KB target (its "Next
steps" section alone is ~1460 lines, s105-148's Thread B saga narrated
almost verbatim rather than compressed). Migrate durable
mechanism/architecture material to PROJECT-OVERVIEW.md and prune
superseded detail, paired with a real experiment. Flagged for many
sessions without action -- worth doing once Thread B's own history
(now closed) can be compressed to a short summary instead of the full
s105-148 blow-by-blow.

`/Users/williambuckley/Documents/Tools/N64Recomp` is its own git
checkout, not a `lib/` submodule, with uncommitted changes across
s90-148 (`fixup_game_funcs.py` plus regenerated `RecompiledFuncs/*.c`).
Same posture as the `rogue_squadron64` sibling checkout flagged since
s54. Worth asking the user whether/how to commit that history.
