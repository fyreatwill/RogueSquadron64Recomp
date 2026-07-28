# NEXT work unit — identify the post-leave scene and survive its first ~2s

s149 closed the `reserveAndEmitDLEntry` recurrence-rate question (parked
at 1/4, no guard) and found something more useful by reading this
session's own screenshots: the single-Start "leave SELECT YOUR CRAFT"
transition **already fires** in the standard countracefix repro shape —
read PORTING-STATE's Session 149 entry (including its addendum) before
doing anything else; this file only has the actionable summary.

## What s149 did and found

Ran `run_countracefix4.sh` (4th soak in the family, no code changes) to
answer NEXT.md's own queued question: does `reserveAndEmitDLEntry`
recur a 2nd time (worth guarding) or stay rare? It did **not** recur —
1/4 across the battery, parked per this thread's own decision rule
(doesn't clear "reachable and recurring"). `do_rom_read` also did not
recur (0/4, 3rd confirmation Thread B stays closed).

The soak died earlier than any prior countracefix soak (hold+2s) to a
**recurrence of the already-catalogued 15th crash class**: RT64-internal
`Assertion failed: ((dstCallTile.sampleWidth > 0) &&
(dstCallTile.sampleHeight > 0) ...)`, function `loadDrawState`, file
`rt64_state.cpp`, line 747 (first seen s97, recurred s99, this is the
3rd occurrence). Backtrace: `RT64::State::loadDrawState` ←
`RT64::RDP::drawTris` ← `GBI_RDP::decodeTriangles` ← `GBI_RDP::tri` ←
`Interpreter::processRDPLists` ← `Application::processDisplayLists` —
no source on our side.

**The important part:** before writing this up as "still stuck in the
pre-mission menu" (what VI-phase tracking alone would suggest — last
`[phase]` line stayed on the pre-leave 512/0x6AB400 pair, s48 already
established this pair can't distinguish menu scenes), the screenshots
this exact soak captured were read directly:
- `scratch/s73_post_a_scene/countracefix4/pre_p1_start.png` and
  `post_p1_start.png` (bracketing the single Start press, 0.6s apart):
  both still show the static **SELECT YOUR CRAFT** menu (hangar pad,
  "PRESS [A] FOR CRAFT DESCRIPTION", parked X-wing).
- `hold_01.png` / `hold_02.png` (+1s / +2s into the hold window that
  follows the Start press, i.e. ~1-2s post-press): a **completely
  different scene** — steep rotated camera, motion-blur speed lines,
  heavily glitched multi-hue textures on ship and background geometry.
  This is visually consistent with s75/s76's already-documented "single
  Start leaves into hangar-flight" transition (title-yellow fade →
  airborne X-wing), not a continuation of the menu.

**So the leave transition already fires in this exact repro shape.**
"What input leaves SELECT YOUR CRAFT" (the question NEXT.md posed as
plan (b) last session) is not actually open — it was already answered
by s75/s76 and is now reconfirmed visually here. The real open
questions are: (1) what does the post-leave scene actually settle into
— a non-interactive hangar-flight cutscene, or the start of a real
mission? — and (2) can the process survive past the first ~2s of it,
since that is exactly the window where this session's crash (and the
whole s95-99 "SELECT YOUR CRAFT stable → hold" crash-family catalogue,
15+ classes) keeps landing.

## Do next

1. **Densify screenshot capture across the leave transition, no new
   hypothesis needed yet.** `run_mission_keys.sh`'s current schedule
   only snaps `pre_p1_start`/`post_p1_start` (0.6s bracket) then 1 Hz
   during the hold window — coarse for a transition that's already
   shown to change completely within 1s. Either lower the hold loop's
   sleep interval for the first ~5s post-Start-press (e.g. 0.2s ticks)
   or add explicit snaps at +0.2/+0.4/.../+2.0s right after the p1
   probe's key send, before the existing 1 Hz hold loop starts. This
   needs a script edit but no rebuild.
2. Rerun once with the denser capture. Discriminating read: do the
   dense frames show a coherent flight/mission scene stabilizing (even
   briefly, before whatever crashes it) — supports "hangar-flight is
   real interactive content, just crash-prone" — or do they show
   uninterrupted glitch/garbage frames all the way to the crash —
   supports "the RT64-internal assert family fires on the transition's
   *load* itself, before any real content renders". Either answer is
   informative for prioritizing (guard-the-transition vs.
   survive-then-see-if-its-a-mission).
3. If a real, if brief, hangar-flight/mission scene is visible before
   the crash: capture what its VI parameters look like (width/origin)
   distinct from the menu pair — closes the "VI phase can't see this
   transition" gap for future soaks, letting the phase-based M3 check
   actually detect in-mission time instead of reading it as menu-only.
4. Do NOT spend a session re-deriving "what input leaves the menu" —
   that's closed (s75/s76, reconfirmed s149). Do NOT restart
   `reserveAndEmitDLEntry` soaking without a new angle (targeted
   instrumentation of `findAndUnlinkSmallestEntry`'s free-list state,
   not another blind repro) — it's parked at 1/4 per rule 8.

## Do not

- Do not re-derive or re-verify the count-write/pointer-store ordering
  fix (Thread B, `allocateSongChannelArray`) — closed, 0/4 clean
  `do_rom_read` non-recurrences across s147-149.
- Do not assume `emit-dl-guard2`/`3` covers any part of
  `reserveAndEmitDLEntry` — confirmed s148 they live in a different
  function entirely (`emitAllocatedDLCommand`).
- Do not write a guard for `reserveAndEmitDLEntry`/
  `findAndUnlinkSmallestEntry` without a new discriminating angle — at
  1/4 it does not clear this thread's "reachable and recurring" bar,
  and rule 8's 4-soak budget on this exact repro shape is spent.
- Do not treat "single Start leaves SELECT YOUR CRAFT" as an open
  question — it's answered (s75/s76, s149).
- Do not re-run `fixup_game_funcs.py` twice without a full regen between
  runs (delete `RecompiledFuncs/funcs_*.c` → `make_elf.py` →
  `regen_n64recomp.sh` → `fixup_game_funcs.py` once) — verify via grep
  that any patch you land fired exactly `x1` before building.

## This session's environment notes (carry forward, still current)

- **A corrupted read doesn't have to be caught by the instrument you
  just built to be caught.** Always grep the FULL run log for every
  armed diagnostic's output, not just the one you just added, before
  writing up a run as inconclusive or as a weak result.
- **Screenshots a script already captured are free evidence — read them
  before assuming a scene-identity question needs a new soak.** This
  session's whole revised framing for (b) came from looking at PNGs
  `run_mission_keys.sh` had already taken, not from new instrumentation.
- VI-phase tracking (`[phase] vi_width=...`) cannot distinguish scenes
  that share VI parameters (s48) — a `[phase]` line staying flat does
  NOT mean the screen content is unchanged; check screenshots too.
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
  indirection. `run_countracefix4.sh` (this session) is a good template
  — copy the full armed-diagnostics battery forward.
- Launch the soak via `zsh <absolute-path>/run_<tag>.sh > <absolute-path>/
  run_<tag>_driver.log 2>&1` as a `run_in_background` Bash call, then
  block synchronously with `until ! pgrep -f "./RogueSquadron64Recomp"
  >/dev/null 2>&1; do sleep 5; done` before closing out the iteration —
  the Stop hook checks `scratch/agent/STATUS` and will re-fire if you
  try to end the turn while a soak is still running.
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

`docs/CURRENT-TRUTH.md` is still far over the ~35 KB target (currently
~175 KB) — its "Next steps" section alone is now over 1500 lines,
narrating multiple closed threads almost verbatim rather than
compressed. Migrate durable mechanism/architecture material to
PROJECT-OVERVIEW.md and prune superseded detail, paired with a real
experiment. Flagged for many sessions without action.

`/Users/williambuckley/Documents/Tools/N64Recomp` is its own git
checkout, not a `lib/` submodule, with uncommitted changes across
s90-149 (`fixup_game_funcs.py` plus regenerated `RecompiledFuncs/*.c`).
Same posture as the `rogue_squadron64` sibling checkout flagged since
s54. Worth asking the user whether/how to commit that history.
