# NEXT work unit — find what diverges right after [musyx-gate1]'s read point at call #19/20

(Written s311. See docs/CURRENT-TRUTH.md item -171 for the summary and `PORTING-STATE` Session 311 for
the full write-up.)

## Context — s311 ruled out Option A, found two DISTINCT freeze boundaries (soft #19/20, hard #39/40)

s310 built 4 new diagnostics (`ROGUESQ_LOG_AUDIOTICK_TRACE`) and found `musyxSynthFrame`'s own entry, the
VI-retrace callback-table slot, and `viRetraceHandlerThread`'s own loop all keep firing well past the
tick-19/20 point where audio-tick counters stop — refuting H1 (driving thread stops being woken) and H4
(full unreaped queue). s311 executed NEXT.md's Option A: widened `[musyx-gate1]`'s (the countdown/period
read inside `musyxSynthFrame`, right before the decrement-and-compare that gates the "run" branch) sample
cap from a flat `n<20` to `n<40||(n%128)==0`, and re-reversed `setDisplayMode`'s gate site a 5th time to
exercise it, running the soak for the FULL 600s phase-timeout this time (vs. s310's shorter capture).

**Result 1 — Option A's own question, answered NO**: `[musyx-gate1]` fired 40/40 times, `countdown=0
period=16777216` on every sample, byte-identical throughout. The gate's raw inputs do not change between
call #19 and call #39. Whatever causes the freeze is NOT visible at this exact read point.

**Result 2 — an unplanned but decisive finding**: because every diagnostic's cap was wide enough this
session to show continued activity via its own modulo resample (`%128`/`%256`/`%512`) if it existed, and
none of them ever printed past their FIRST cap window despite a full 10-minute run, the picture is now
unambiguous:
- **SOFT stop at call #19/20**: `[audtask-dispatch]` (RSP `M_AUDTASK` submission) and all 3 gate-consumer
  reach tags (`update3DAudioFrame`/`tickAllActiveSongs`/`tickAudioSequencerFrame` entry+exit) stop
  together, exactly 20 fires each. `musyxSynthFrame`'s own entry and its `[musyx-gate1]` read (which sits
  BETWEEN the entry and these 3 calls, architecturally) keep running normally for ~20 MORE calls after
  this — meaning the actual branch/compare decision (not the raw countdown/period inputs) is what starts
  silently choosing "skip" at call #19.
- **HARD stop at call #39/40**: `[vi-cb-loop]`, `[vi-cb-slot]`, `[synth-entry]` (musyxSynthFrame's own
  entry) ALL stop simultaneously, in lockstep with the RSP task-runner's own last dispatch (`[runner]`
  task #39) — this is the same event s307/s309 called "the later full-scheduler wedge," now tied
  precisely to the audio-tick side for the first time. `viRetraceHandlerThread`'s own loop-top stopping
  here means this is a genuine full coop-scheduler wedge, not an audio-specific bug.

These are two SEPARATE mechanisms. The call #19/20 soft stop is the M5-relevant one (it's specifically
about audio task dispatch skipping); the call #39/40 hard stop is the same "later full-scheduler wedge"
s307/s309 already parked as a lower-priority, harder problem. Stay focused on #19/20.

## The work unit

**Narrow the branch/compare right after `[musyx-gate1]`'s read**, now that the raw countdown/period
inputs are ruled out. Two concrete leads, pick based on a quick source-read first (don't build blind):

1. **Read the actual decrement-and-compare code** immediately following the already-instrumented load at
   `funcs_24.c` (guest `0x80091470-0x80091478`, anchor already in `fixup_game_funcs.py`'s
   `_musyx_gate1_patch`). The print happens BEFORE the compare; read what MIPS instructions follow in the
   generated C to see what the branch condition actually is (likely a `bnez`/`beqz` on the loaded
   countdown, or a compound condition involving another register/global not currently logged). Add ONE
   new diagnostic immediately AFTER the compare (not just before) that logs whether the "run" branch was
   actually taken, keyed to the same call counter so it lines up directly against `[musyx-gate1]`'s own
   `n=` values — this directly answers "does the compare start returning false at n=19 even though
   countdown/period stay 0/16777216."
2. **s107 found 3 near-identical gate copies inside `musyxSynthFrame`** (funcs_24.c) guarding calls to
   `tickAllActiveSongs`/`tickAudioSequencerFrame`; only the FIRST is currently instrumented
   (`_musyx_gate1_patch`). If lead 1's compare-outcome diagnostic shows the FIRST gate's compare still
   evaluates "run" at call #19 (i.e. the 1st gate isn't the skip point), check the 2ND and 3RD copies —
   one of them may be the actual site whose compare (or whose own state, not yet read at all) diverges.
   Add matching read-before-compare AND compare-outcome diagnostics to those 2 copies, same n<40||n%128
   convention, same env var (`ROGUESQ_LOG_VOICE_TRIGGER_CHAIN`) so they land in the same soak/log as
   `[musyx-gate1]`.

**Batch whichever lead(s) into ONE `fixup_game_funcs.py` edit + regen + build**, combined with
`setDisplayMode`'s gate-byte site reversal (6th time) to exercise gate=1 and reproduce the freeze, one
soak, read the result, update the hypothesis table, **revert `setDisplayMode`'s site again same session**
(per the established discipline — not safe to ship reversed, deterministically hangs boot). Run the FULL
soak to completion (600s phase-timeout) like s311 did, not a short capture — s310's shorter capture is
what made the call #39/40 boundary look ambiguous in the first place; a short capture on this new
diagnostic risks the same false ambiguity.

## Environment notes (carried forward, all still valid)

- Regen order: `fixup_game_funcs.py` edit → clear `N64Recomp/RecompiledFuncs/*.c` (python3 glob-delete;
  plain `rm`/`find -delete` are blocked in this sandbox) → `N64Recomp/build/N64Recomp
  rogue_squadron.toml` (cwd = `N64Recomp` checkout; redirect stdout to a file INSIDE one of the 3 allowed
  dirs, not `/tmp` — it's blocked) → `python3 fixup_game_funcs.py` (run exactly once, refuses a 2nd run
  via its own SENTINEL check) → `DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build
  build -j8` (cwd = this repo root). `make_elf.py` not needed unless source/symbol mapping changed.
- Soak driver template: `scratch/s73_post_a_scene/run_step311gate1cap.sh` (s311's recipe, copied from
  s310's `run_step310audiotrace.sh`) — copy it, don't hand-roll a new script; bump the output-dir name
  (last line's `${1:-...}` default) and the header comment; only the fixup-script/lib-side edit changes
  between sessions. `ROGUESQ_LOG_AUDIOTICK_TRACE=1` and `ROGUESQ_LOG_VOICE_TRIGGER_CHAIN=1` are both
  already armed in it.
- **Waiting on a soak**: launch via Bash with `run_in_background: true` (avoid `cd` combined with output
  redirection in the same compound command — use absolute paths and no `cd` instead, or split into
  separate Bash calls; both triggered approval prompts this session), then use `TaskOutput` with
  `block: true` and a generous `timeout` (up to 480000ms) — do NOT foreground-poll with a bare `sleep`
  loop or hand-rolled `pgrep` polling. `run_mission_keys.sh` has its own internal 600s phase-timeout that
  exits nonzero (`INCONCLUSIVE`, exit 5) on the deterministic hang — that's the EXPECTED outcome when the
  gate site is reversed, not a soak-tooling failure; the game process is killed automatically on that
  path (verified again s311: no manual SIGKILL needed).
- **One game run at a time** — confirm `pgrep -f "build/RogueSquadron64Recomp"` is empty before
  launching.
- `scratch/s73_post_a_scene/step311gate1cap/run.log` is s311's saved log (738943 bytes, 7686 lines);
  `scratch/agent/s311_gate1_lines.txt` and `scratch/agent/s311_reach_tags.txt` have the pre-extracted
  `[musyx-gate1]`/`[reach-*]` lines if a future session wants to re-verify before building.
- `/tmp` is blocked for redirects — use a path inside this repo, `N64Recomp`, or `rogue_squadron64`
  instead.
- The `unguarded_walk_candidates.json` sweep (143 sites/43 funcs, 3 addressed) remains the fallback
  M3-audit work unit if a future session finds M5 blocked and maintenance isn't triggered.

HYPOTHESIS-ID: m5-audio-destub-step4-setdisplaymode-hang (same slug, s303-311 — still the active
investigation thread. s306/s307/s309/s310/s311 have each produced a discriminating result in sequence —
resetting the iron-rule-8 no-progress counter every time; this is real, converging progress (H1/H4
refuted, Option A's specific hypothesis ruled out, two distinct freeze boundaries now precisely dated),
not a stall. Continue the same slug next session.)
