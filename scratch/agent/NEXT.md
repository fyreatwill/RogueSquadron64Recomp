# NEXT work unit — why do the 3 tick-producer functions stop 3 calls short (37/37) of the shared 40/40 hard-freeze boundary?

## Context — s322 closed the 14-call-gap sub-investigation; this is a fresher, unrelated gap

s321 (exhaustive grep) and s322 (gate3 reachability source-read) together exhausted both testable
explanations for the "14-call gap" (gate1+gate2's measured real-call rate, 23-24, vs. the tick-producer
functions' own measured entry count, 37-38): no undiscovered static/simple-indirect call site exists
(s321), and gate3's persistent 0/40-reached is real game-state-dependent control flow, not a diagnostic
bug (s322). The only surviving explanation for that specific gap — a fully dynamic indirect call among
28,388 `LOOKUP_FUNC` sites — needs runtime call-site logging keyed on target address, not text search;
out of scope for a bounded session with current tooling. **Do not resume that specific gap-chase.**

Separately, item -174 (s315) found and left open a DIFFERENT, smaller, never-directly-investigated gap:
in the same soak runs, `[reach-update3d-entry/exit]` (`update3DAudioFrame`), `[audtask-dispatch]`
(`M_AUDTASK` RSP-task submission, `src/main/main.cpp:581-636`), and the RSP task-runner's own last
dispatch (`[runner] task #39`) all hit **40/40** together — a genuine hard-freeze boundary. But
`tickAllActiveSongs`/`tickAudioSequencerFrame`/`tickAllAudioChannels` (the SAME 3 functions the gate1/2/3
investigation was chasing) stop **37/37**, three calls before everything else. s315 measured this
directly and moved on without investigating WHY. No session since has looked at it — it predates and is
independent of the gate1/2/3/14-call-gap thread. This is the new work unit.

## The work unit — pure source-read first, build+soak only if source-read doesn't resolve it

1. **Source-read the 3 tick-producer functions' own bodies** (`tickAllActiveSongs` at guest address
   `0x80096D08`, `tickAudioSequencerFrame` at `0x8008D960`, and `tickAllAudioChannels` — find its guest
   address via `grep -n "tickAllAudioChannels" RecompiledFuncs/*.c | grep RECOMP_FUNC` in
   `~/Documents/Tools/N64Recomp`) for any EARLY-RETURN or conditional-skip path near their end — a
   branch that could make the exit-side diagnostic fire fewer times than the entry-side one, or that
   could make them stop being called at all after some internal state changes on call ~38.
2. **Check whether the existing entry/exit diagnostics themselves have any asymmetry** — `[reach-
   allsongs-entry]` vs `[reach-allsongs-exit]` vs `[reach-audioseq-exit]` (search `fixup_game_funcs.py`
   for these names) — do entry and exit both stop at 37, or does one stop earlier/later than the other
   (which would point at an internal early-return rather than the caller simply stopping)?
3. **Check what's different about calls 38-40 specifically** — since `update3DAudioFrame` and
   `M_AUDTASK` dispatch both continue to 40, whatever stops the tick-producers must be inside them or
   their direct callees, not further upstream (their caller — gate1/2 — clearly keeps running, since
   gate1's own diagnostic reaches 40 per s320). Read gate1's calling convention once more
   (`funcs_24.c:3619-3632`, already read s321/s322) for anything that could make the CALL itself become
   a no-op after call 37 while gate1's own `n` counter keeps incrementing (e.g. a countdown/flag inside
   the tick-producer functions themselves that causes them to self-skip past some threshold).
4. **If source-read doesn't find an obvious internal early-return or self-gating threshold**, this needs
   a build+soak: add one more field to the ALREADY-armed `[reach-allsongs-entry/exit]` etc. diagnostics
   (or a fresh minimal counter) logging some piece of internal state at calls 35-40 specifically (e.g. a
   sample index, a channel-active count, whatever the source-read step above surfaces as the likeliest
   internal gate) to catch the state right before/at the point they stop. Reuse the existing
   `n<40||(n%128)==0` sampling convention. This DOES need `setDisplayMode`'s site reversed (a 14th time)
   to exercise the real call path — follow the same revert-same-session discipline as every prior
   session in this thread.

## Expected discriminating outcomes

- If step 1-3 finds an internal early-return/self-gating condition in one of the 3 functions: that's the
  answer — no build needed, write it up, and consider whether it explains the whole 37-vs-40 gap or only
  narrows it further.
- If step 4's soak shows the SAME internal state value (e.g. a countdown reaching 0, a flag going false)
  right at call 37-38 across the 3 functions but NOT in `update3DAudioFrame`/`M_AUDTASK`: strong
  candidate for a shared resource specific to the tick-producers (distinct from the shared coop-scheduler
  resource s307 already identified for the LARGER 40-call freeze).
- If nothing distinguishes call 37 from call 36 or 38 in any sampled state: the gap may be a sampling/
  ordering artifact of the diagnostics themselves rather than a real game-state event — check the
  print-cap convention on all 5 relevant diagnostics once more for a s312/s313/s315-class unwidened-cap
  bug (the SAME bug class has now been found and fixed 3 times in this investigation; a 4th instance
  would not be surprising and should be checked FIRST, cheaply, before any new instrumentation).

## Environment notes (carried forward from s321/s322, still valid)

- Regen paths for game-code patches are in `/Users/williambuckley/Documents/Tools/N64Recomp`
  (`fixup_game_funcs.py`, `RecompiledFuncs/*.c`, `build/N64Recomp`, `rogue_squadron.toml`), NOT this
  repo. `[audtask-dispatch]` lives in THIS repo's `src/main/main.cpp:581-636` (native runtime code, not
  a `RecompiledFuncs` patch) — edits there need a normal rebuild, no `N64Recomp` regen, no
  `submodule-patches/export.sh` (it's not under `lib/`).
- If a build/soak turns out to be needed (step 4): regen order is `make_elf.py` -> `N64Recomp` ->
  `fixup_game_funcs.py` -> `cmake`, in that exact order (`N64Recomp` skips files that already exist on
  disk — item -20 — so `RecompiledFuncs/*.c` MUST be deleted before every `N64Recomp` run). `cd` into
  `N64Recomp` FIRST as its own bare `cd` command, THEN run `./build/N64Recomp rogue_squadron.toml` with
  output redirection in a SEPARATE Bash call.
- To reverse ONLY `setDisplayMode`'s site (not `reapplyDisplayMode`'s): narrow the shared regex in
  `fixup_game_funcs.py` (~line 173) from `0x8008E(?:B40|C88)` to `0x8008EB40` only. MUST restore the
  full `(?:B40|C88)` alternation before ending session, verified via `audio gate patched x2` in the
  fixup report.
- `python3 -c "import glob, os; [os.remove(f) for f in glob.glob('/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/*.c')]"`
  clears RecompiledFuncs (use the ABSOLUTE path).
- `DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build build -j8` from this repo's
  root — allowlisted verbatim, works as a single command.
- Soak driver template: `scratch/s73_post_a_scene/run_step320synthentryvsgate1.sh` (newest; copy it,
  don't hand-roll). Invoke as `zsh run_foo.sh`, not `./run_foo.sh`. `cd` into `scratch/s73_post_a_scene`
  first as its own bare command. Launch via Bash with `run_in_background: true`, then `TaskOutput` with
  `block: true` and `timeout` up to 600000ms — do NOT foreground-poll. Confirm `pgrep -f
  "build/RogueSquadron64Recomp"` is empty before AND after.
- `/tmp` is blocked for redirects — use a path inside this repo, `N64Recomp`, or `rogue_squadron64`.
- Multi-operation Bash commands combining `cd`+redirect, or `export VAR=...` chained with other
  commands, trigger permission prompts — issue `cd` as its own bare command, run each `export`/command
  separately.

HYPOTHESIS-ID: m5-audio-destub-step4-tick37-vs-hardstop40 (NEW — s322 pivoted here from
`m5-audio-destub-step4-setdisplaymode-hang`'s now-exhausted 14-call-gap sub-thread; see CURRENT-TRUTH
item -181 and the closed note on item -180's parent hypothesis-id).
