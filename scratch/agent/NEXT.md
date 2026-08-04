# NEXT work unit — MAINTENANCE FIRST, then instrument the M_AUDTASK-submission call itself

## Step 0 will trigger MAINTENANCE this session

`docs/CURRENT-TRUTH.md` is 60051 bytes as of s313's edits (>60000 threshold). Per
`tools/agent/ITERATION.md` Step 0, the next iteration's FIRST job is a maintenance pass: compact toward
~35 KB, migrate durable material to `docs/PROJECT-OVERVIEW.md`, prune/merge superseded items, renumber
the Next-steps backlog into one monotonic sequence (currently ends at -173), refresh the stale "as of
session N" headline. Do NOT run the audio experiment below in a maintenance iteration — do maintenance
ONLY that session, then pick up this work unit the session after.

## Context — s313 overturned the "3 gate-consumer functions stop at call 19/20" conclusion

s313 executed s312's work unit (widen `GATE3_REACH`/`tick-audio-seq`/`tick-all-audio-channels`'s flat
`n<20` print caps to the resampled `n<40||n%128==0` convention) and got a clean, decisive, 3-way split
result from one soak:

| tag | true call count |
|---|---|
| `update3DAudioFrame` (`[reach-update3d-*]`) | **40/40** — matches the hard-stop boundary exactly |
| `tickAllActiveSongs`/`tickAudioSequencerFrame`/`tickAllAudioChannels` | **37/37** — stops 3 calls early |
| RSP `M_AUDTASK` submission (`[audtask-dispatch]`, already resampled since s310) | **20/20** — unchanged |

The old "all 3 gate-consumer functions + M_AUDTASK submission stop together at 19/20" framing is
OVERTURNED (moved to CURRENT-TRUTH's Overturned Conclusions, s313 entry). There isn't one shared stop
point — there are three. Full detail: `docs/CURRENT-TRUTH.md` Next-steps item -173, `PORTING-STATE`
Session 313.

## The work unit (AFTER maintenance)

**Find why `M_AUDTASK` submission stops at call 20 while `tickAudioSequencerFrame`/`tickAllAudioChannels`
(its own callers, confirmed by s313 to still be entering/exiting normally) keep running 17 more calls
to 37.** This is now the narrowest, most information-dense unknown — the submission call itself, or
whatever gates it, lives somewhere inside or downstream of 2 functions already confirmed reachable at
that point, not "somewhere in 3 unknown functions."

1. Source-read `tickAudioSequencerFrame` and `tickAllAudioChannels` (`funcs_23.c`, same file as the
   `_tick_audio_seq_patch`/`_tick_all_audio_channels_patch` call sites, ~line 1999-2050 region for the
   entry-diagnostic anchors) end-to-end: find every call that could reach RSP `M_AUDTASK` submission
   (likely several frames down — `[audtask-dispatch]`'s own patch site, find it in `fixup_game_funcs.py`
   via `grep -n "audtask-dispatch"`, then trace which function actually contains that instrumented call
   and how `tickAudioSequencerFrame`/`tickAllAudioChannels` reach it).
2. Identify the specific branch/condition/loop-bound between "definitely still executing at call 37"
   (the functions' own entry/exit) and "stopped executing at call 20" (the submission call) — this is
   the same kind of gap s312 found for `update3DAudioFrame` (a single-byte gate), so check for a similar
   single-condition gate first (cheapest hypothesis) before assuming something more complex (a counter,
   a queue-depth check, a modulo-N frame-skip).
3. Once a candidate site is found, add ONE new diagnostic there (reuse the existing env-var/cap
   conventions: `n<40||n%128==0` from the start, don't repeat the flat-cap mistake) and batch it into the
   same regen/soak cycle as any other counters this session wants (batch-instrumentation rule).
4. Regen order: `fixup_game_funcs.py` edit → clear `RecompiledFuncs/*.c` → `N64Recomp/build/N64Recomp
   rogue_squadron.toml` → `python3 fixup_game_funcs.py` → `cmake --build build -j8`. Reverse
   `setDisplayMode`'s gate site (`RecompiledFuncs/funcs_23.c`, `MEM_B(0XF50, ctx->r1) = 0` → `=
   ctx->r2`, near "0x8008EB40") an 8th time to exercise gate=1, one full soak, read result, **revert the
   site again same session** (mandatory — not safe to ship reversed, deterministic boot hang).

**Discriminating outcome**: if a single-condition gate is found and its value is shown (via the new
diagnostic) to go stale/flip exactly around call 20 while the surrounding function keeps running →
localizes the M_AUDTASK-submission stop precisely, ready for a fix attempt. If no such single condition
exists in the direct call path → the stop is likely inside a deeper callee not yet identified; widen the
source-read one level further (which callee of `tickAudioSequencerFrame`/`tickAllAudioChannels` actually
performs `M_AUDTASK` submission — may not be either of them directly).

## Environment notes (carried forward, all still valid)

- Regen paths are in the `N64Recomp` working directory (`/Users/williambuckley/Documents/Tools/N64Recomp`),
  NOT this repo — `fixup_game_funcs.py`, `RecompiledFuncs/*.c`, `build/N64Recomp`, `rogue_squadron.toml`
  all live there. This repo (`RogueSquadron64Recomp`) only has `build/` (cmake) and the `scratch/`
  soak-driver scripts.
- `cd` into `N64Recomp` FIRST as its own bare `cd` command, THEN run `./build/N64Recomp rogue_squadron.toml`
  with output redirection in a SEPARATE Bash call — combining `cd` and a redirect in one compound command
  triggers a permission prompt in this sandbox. Same for any other cd+redirect combo (soak launch, etc.) —
  do the `cd` alone first.
- `python3 -c "import glob, os; [os.remove(f) for f in glob.glob('/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/*.c')]"`
  clears RecompiledFuncs (use the ABSOLUTE path — a relative `N64Recomp/RecompiledFuncs/*.c` from this
  repo's root resolves to nothing and silently clears 0 files).
- `DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build build -j8` from this repo's
  root (`RogueSquadron64Recomp`) — this exact form is allowlisted verbatim, works as a single command.
- Soak driver template: `scratch/s73_post_a_scene/run_step313widecap.sh` — copy it, don't hand-roll a
  new script; bump the output-dir default (last line) and header comment.
  `ROGUESQ_LOG_AUDIOTICK_TRACE=1`, `ROGUESQ_LOG_VOICE_TRIGGER_CHAIN=1`, and
  `ROGUESQ_LOG_INITMUSYX_REACH=1` are all already armed in it.
- Launch the soak via Bash with `run_in_background: true` (cd into `scratch/s73_post_a_scene` first as
  its own bare command), then `TaskOutput` with `block: true` and `timeout` up to 600000ms — do NOT
  foreground-poll. `run_mission_keys.sh`'s own 600s phase-timeout exits nonzero (exit 5, INCONCLUSIVE)
  on the expected deterministic hang — that's success for this soak design, not a tooling failure; the
  game process is killed automatically. Confirm `pgrep -f "build/RogueSquadron64Recomp"` is empty before
  AND after.
- `/tmp` is blocked for redirects — use a path inside this repo, `N64Recomp`, or `rogue_squadron64`
  instead.
- `scratch/s73_post_a_scene/step313widecap/run.log` is s313's saved log (744723 bytes) if a future
  session wants to re-verify the 40/37/20 call-count split before building anything new.

HYPOTHESIS-ID: m5-audio-destub-step4-setdisplaymode-hang (same slug, s303-313 — still the active
investigation thread. s306/s307/s309/s310/s311/s312/s313 have each produced a discriminating result in
sequence — resetting the iron-rule-8 no-progress counter every time; this is real, converging progress
(H1/H4 refuted, Option A ruled out, two freeze boundaries dated, the "soft stop at 19/20" conclusion
directly measured and overturned, and the unknown narrowed from "3 functions" to "1 specific call/gate
inside 2 confirmed-still-running functions"), not a stall. Continue the same slug next non-maintenance
session.)
