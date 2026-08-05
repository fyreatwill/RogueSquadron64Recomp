# NEXT work unit — re-reverse setDisplayMode's gate, rebuild, run 1-2 more confirmatory soaks

## Status note (s327): the fix WORKS on 1/1 soaks — this is now a confirmation-soak task, not more design

s327 landed and validated (once) the fix NEXT.md asked for: `waitForMusyXAudioTaskDone`/
`shutdownAudioEngine`'s spin loops (patched in `N64Recomp/fixup_game_funcs.py`, untracked, no `lib/`
change) now call `musyxSynthFrame` directly instead of blocking on a countdown only that call could
decrement. With `setDisplayMode`'s gate-byte site reversed, the soak reached VI=1024 (title) at the
untouched baseline timing (45.6s) and progressed through the ENTIRE menu chain into SELECT YOUR
CRAFT's 240s hold — something no prior session in this 25-session, 15-reversal investigation had ever
achieved (every prior reversal hung dead at exactly VI=320). Full trace/result:
`docs/CURRENT-TRUTH.md` item -185, `PORTING-STATE.md` Session 327.

**The soak did NOT complete perfectly clean**: it died at hold-iter 28 (~32s into the hold) to
`SIGBUS` in `processSceneNode+1424`. This is important context, not a blocker — grep
`PORTING-STATE.md` for `processSceneNode+1424` and you'll find 3 PRIOR sightings (Sessions
~281-285), every one already logged as "already-catalogued, unrelated," recurring in this exact
scene under this exact `HOLD_S=240` soak shape, in totally unrelated investigation threads that
never touched audio. No audio diagnostic (`[synth-entry]`, `[musyx-*]`, `[audio-wait-pump*]`) fired
anywhere near the crash. Treat it as a pre-existing background crash class the soak simply lived
long enough to hit, not evidence against the fix — but this is still only ONE soak, and the M5 plan's
own bar is "two clean soaks... without crash-family #1's signature recurring."

**The gate is currently back at the safe baseline** (both `setDisplayMode`/`reapplyDisplayMode`
force-zeroed, `audio gate patched x2` confirmed, rebuilt) — s327 reverted it before ending, matching
every prior session's convention. The spin-pump code fix itself stays in the tree permanently (inert
when the gate is 0, since `musyxNoopStub`'s own gate-byte check short-circuits before ever reaching
the spin) — no action needed there, it does not need to be re-applied.

## The work unit — re-reverse, rebuild, soak twice more

1. In `N64Recomp/fixup_game_funcs.py`, narrow the audio-gate store regex from
   `r"(// 0x8008E(?:B40|C88): sb ..."` to `r"(// 0x8008EC88: sb ..."` (C88-only — same exact edit as
   s327, s325, s323, s320, s319; search for `0x8008E(?:B40|C88)` in the file to find the line).
2. Full regen pipeline, in order: `make_elf.py` -> clear `RecompiledFuncs/*.c` -> `N64Recomp` ->
   `fixup_game_funcs.py` -> `cmake --build`. Confirm the patch report shows `audio gate patched x1`
   (not x2) and `audio-wait spin pump patched x2` (the fix code should already be there from s327 —
   if the report doesn't show it, the fixup edit was lost; re-check the file).
3. Run `zsh scratch/s73_post_a_scene/run_s327waitpump.sh <label>` (background, `TaskOutput` block
   with up to 600000ms timeout — do NOT foreground-poll) TWICE, with different labels. Confirm
   `pgrep -f "build/RogueSquadron64Recomp"` is empty before AND after each run.
4. For each soak, check: does VI reach 1024 (title, ~45.6s)? Does it progress into SELECT YOUR CRAFT?
   If it crashes, is the crash `processSceneNode+1424` again (consistent with s327, strengthens the
   "pre-existing unrelated background crash" reading) or something else (would need investigation —
   check whether it correlates with any `[synth]`/`[musyx]`/`[audio-wait-pump]` diagnostic firing
   near the crash line, the same check s327 did)?
5. **If both soaks clear the VI=320 hang** (regardless of what they eventually die to further along):
   the `m5-audio-destub-step4-setdisplaymode-vi320-hang` fix is FULLY validated per the M5 plan's own
   bar. At that point it's a legitimate question (write it down, don't just act on it) whether to
   promote the reversed gate to the new shipped default — that's a bigger call than fits in "the same
   work unit," flag it for explicit consideration rather than deciding unilaterally mid-soak-review.
   **If either soak hangs again at exactly VI=320**: this falsifies s327's fix — re-open the
   mechanism investigation, do NOT just re-run.
6. Revert the gate back to force-zero (`(?:B40|C88)` alternation) before ending the session, same as
   every session on this hypothesis so far, UNLESS step 5's both-clean result leads to an explicit
   decision (documented, not implicit) to promote it.

## Environment notes (carried forward, still valid)

- Regen paths for game-code patches: `/Users/williambuckley/Documents/Tools/N64Recomp`
  (`fixup_game_funcs.py`, untracked/uncommitted loose file — NOT git-tracked in that repo, so no
  N64Recomp-side commit is needed after edits there; only THIS repo's ledger records what changed).
  Regen order: `make_elf.py` -> `N64Recomp` -> `fixup_game_funcs.py` -> `cmake`, in that exact order.
  `N64Recomp` skips files that already exist on disk, so `RecompiledFuncs/*.c` MUST be deleted before
  every `N64Recomp` run: `python3 -c "import glob, os; [os.remove(f) for f in
  glob.glob('/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/*.c')]"`. `cd` into
  `N64Recomp` FIRST as its own bare `cd` command, THEN run `./build/N64Recomp rogue_squadron.toml`;
  redirecting its output to a file under `/tmp` is blocked by the sandbox (triggers a "Contains
  simple_expansion" denial) — either pipe through `| tail -N` directly, or redirect to a file inside
  a repo directory instead.
- Soak driver: `scratch/s73_post_a_scene/run_s327waitpump.sh` (self-contained, reusable — do NOT put
  it in `scratch/agent/soak_queue/`, it needs the gate reversed at BUILD time first and the queue
  mechanism only runs against a static build, it cannot re-run the regen pipeline). Invoke as
  `zsh run_s327waitpump.sh <label>` from `scratch/s73_post_a_scene`. Launch via Bash with
  `run_in_background: true`, then `TaskOutput` with `block: true` and `timeout` up to 600000ms — do
  NOT foreground-poll. The actual console log lands at `scratch/s73_post_a_scene/<label>/run.log`
  (large, several million lines with the full breadcrumb set armed — grep for `\[CRASH\]`,
  `\[phase\]`, `\[synth-entry\]`, `audio-wait-pump` rather than reading it directly).
- `DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build build -j8` from this repo's
  root — allowlisted verbatim, works as a single command.

HYPOTHESIS-ID: m5-audio-destub-step5-confirm-waitpump-fix (1st of budgeted 3 iterations — s327's own
soak was the discriminating result that closed the PRIOR hypothesis; this is a fresh thread
confirming the fix generalizes, not a stalled repeat.)
