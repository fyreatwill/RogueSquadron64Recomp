# NEXT work unit — find the internal musyxSynthFrame branch that changes at tick ~20

(Written s310. See docs/CURRENT-TRUTH.md item -170 for the summary and `PORTING-STATE` Session 310 for
the full write-up.)

## Context — s310 refuted H1 and H4, narrowed the freeze to inside musyxSynthFrame

s309 (pure source-read) found the RSP-task freeze (task #39) and the audio-tick freeze (tick #19) are two
separate, sequential stalls, not one shared event. s310 built a batched 4-site diagnostic
(`ROGUESQ_LOG_AUDIOTICK_TRACE`) and ran ONE soak (setDisplayMode's gate site reversed a 4th time to
reproduce the freeze, same recipe as s303/s307). Result — a clean, discriminating, positive-controlled
finding:

- `[vi-cb-loop]` (viRetraceHandlerThread's own loop-top) fired 40/40 possible times — the thread's own
  loop keeps running well past tick 19/20.
- `[vi-cb-slot]` (the 4-slot VI-retrace callback table read) shows slot `0x8011A8A8` holds
  `musyxSynthFrame`'s address (`0x8009123C`) continuously from VI-tick ~3 onward, through the last sample
  (tick ~11 of the un-sampled window) — the table entry never goes null, never changes.
- `[synth-entry]` (musyxSynthFrame's own entry) fired 40/40 possible times — the function itself keeps
  being called, indefinitely, past the freeze point.
- `[synth-rearm-ptr]` (the DMEM-mixer callback-pointer read `musyxSynthFrame` uses to register itself
  into the VI-retrace table) fired exactly ONCE, early — read together with `[vi-cb-slot]`'s timing, this
  looks like a one-time self-registration, not a bug.

**Conclusion: H1 is refuted.** The outer invocation chain (VI retrace → 4-slot callback table →
`musyxSynthFrame` entry) never stops, never drops, never goes silent. Whatever is skipping
`update3DAudioFrame`/`tickAllActiveSongs`/`tickAudioSequencerFrame`/the RSP `M_AUDTASK` submission after
tick ~19-20 must be **inside** `musyxSynthFrame` (or a callee it reaches on the branch that runs those
calls) — an internal state variable or control-flow gate that changes starting around the 20th call, even
though the function keeps being entered normally every time.

**H4 is also refuted** (separately, by source-read): no `M_AUDTASK`-specific fixed-depth queue/ring/depth
counter exists anywhere in `sp.cpp`, `mesgqueue.cpp`, or `events.cpp` — the only audio-task queueing is
an unbounded `moodycamel::BlockingConcurrentQueue` in `events.cpp:132`. There's no fixed-depth structure
to fill, so "H4: a full unreaped queue" cannot be the mechanism.

This leaves **H2 (a new internal gate)** and **H3 (blocks inside musyxSynthFrame before reaching the 3
already-cleared functions)** as the live candidates, effectively converged into one question: **what
inside musyxSynthFrame changes between call #19 and call #20?**

One known instrument is uninformative on this exact question: `[musyx-gate1]`
(`ROGUESQ_LOG_VOICE_TRIGGER_CHAIN`, `funcs_24.c:3560`, already armed by the soak recipe, no new build
needed to re-arm it) prints a countdown/period pair — in s310's log it read `countdown=0, period=16777216`
identically across all 20 of its own capped samples (ticks 0-19). This shows the gate trivially evaluates
"run" every time in the observed window, but its `n<20` cap makes it impossible to tell whether the value
changes starting at tick 20 — exactly the question that matters now.

## The work unit

**Step 1 — raise the ceiling on what's already known, cheaply, before adding anything new.** Two options,
pick based on Step 2's needs (they're not mutually exclusive, but do the minimum that answers the
question — don't build more than one batch):

- **Option A (preferred, smallest change):** in `fixup_game_funcs.py`, find `[musyx-gate1]`'s existing
  patch (search `musyx_gate1`, `funcs_24.c:3560`-area) and widen its print condition from `n < 20` to
  `n < 40 || (n % 128) == 0` (matching s310's own sampling convention) — this alone might show whether
  `countdown`/`period` ever change past tick 19, with zero new anchors needed (same site, same env var,
  just a wider cap). If the values stay `countdown=0, period=16777216` even through tick 39, that RULES
  OUT this specific gate as the mechanism and narrows the search to a DIFFERENT internal branch (see
  Option B). If the values change, that IS the mechanism — read what code sets `period` and trace why it
  changes.
- **Option B (if Option A's gate stays constant):** trace the actual `M_AUDTASK` RSP-submission call
  site. `[audtask-dispatch]` (main.cpp:594-626, `get_rsp_microcode`'s `M_AUDTASK` branch) fires when the
  guest calls the OSTask-submission API (`sp.cpp`'s `M_AUDTASK` branch → `ultramodern::submit_rsp_task`).
  Find what recompiled guest function calls that submission API for audio (likely inside
  `tickAudioSequencerFrame`/`tickMusyXIfActive` or a callee several levels deeper — NOT confirmed yet,
  needs its own source-read/grep for the RSP-task-start libultra call, e.g. `osSpTaskStart`/similar, in
  `funcs_23.c`/`funcs_24.c`/`funcs_25.c`). Add ONE tick-scoped counter at that exact call site (matching
  s310's `n<40||n%128==0` convention) to see directly whether it's reached on every `musyxSynthFrame`
  call, or stops being reached starting at #20 — this settles H2 vs H3 precisely (H2: some earlier gate
  skips the whole "run" branch and this counter also stops; H3: this specific call is what blocks/never
  returns, i.e. this counter's OWN entry might still fire but something after it hangs — distinguish by
  adding both an entry AND exit tag at that call, same as s306's `_reach_entry_patch`/`_reach_exit_block`
  helpers already in the file).

**Step 2 — batch whichever option (or both, if cheap) into ONE fixup_game_funcs.py edit + regen + build,
combined with the same setDisplayMode gate-site reversal used by s303/s307/s310 to reproduce the freeze,
soak once, read the result, update the hypothesis table below, revert setDisplayMode's site again
same session** (per the established discipline — it's not safe to ship reversed; it deterministically
hangs boot). The 4 s310 diagnostics can stay armed (`ROGUESQ_LOG_AUDIOTICK_TRACE=1`, already in the
`run_step310audiotrace.sh` recipe) alongside whatever's new — free confirmation that this session's
findings still hold.

## Environment notes (carried forward, all still valid)

- Regen order: `fixup_game_funcs.py` edit → clear `N64Recomp/RecompiledFuncs/*.c` (python3 glob-delete;
  plain `rm`/`find -delete` are blocked in this sandbox) → `N64Recomp/build/N64Recomp
  rogue_squadron.toml` (cwd = `N64Recomp` checkout; redirect stdout to a file INSIDE one of the 3 allowed
  dirs, not `/tmp` — it's blocked) → `python3 fixup_game_funcs.py` (run exactly once, refuses a 2nd run
  via its own SENTINEL check) → `DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build
  build -j8` (cwd = this repo root). `make_elf.py` not needed unless source/symbol mapping changed.
- Soak driver template: `scratch/s73_post_a_scene/run_step310audiotrace.sh` (s310's recipe, itself copied
  from s307's `run_step307reach.sh`) — copy it, don't hand-roll a new script; bump the output-dir name
  (last line's `${1:-...}` default) and the header comment; only the fixup-script/lib-side edit changes
  between sessions. `ROGUESQ_LOG_AUDIOTICK_TRACE=1` and `ROGUESQ_LOG_INITMUSYX_REACH=1` are both already
  armed in it.
- **Waiting on a soak**: launch via Bash with `run_in_background: true`, then use `TaskOutput` with
  `block: true` and a generous `timeout` (up to 480000ms) — do NOT foreground-poll with a bare `sleep`
  loop or hand-rolled `pgrep` polling. `run_mission_keys.sh` has its own internal 600s phase-timeout that
  exits nonzero (`INCONCLUSIVE`) on the deterministic hang — that's the EXPECTED outcome when the gate
  site is reversed, not a soak-tooling failure; the game process is killed automatically on that path
  (verified s310: no manual SIGKILL needed after the script's own timeout fired).
- **One game run at a time** — confirm `pgrep -f "build/RogueSquadron64Recomp"` is empty before
  launching.
- `scratch/s73_post_a_scene/step310audiotrace/run.log` is s310's saved log (738016 bytes, 7666 lines) —
  has the raw `[vi-cb-loop]`/`[vi-cb-slot]`/`[synth-entry]`/`[synth-rearm-ptr]` data referenced above if a
  future session wants to re-verify before building; grep line numbers are cited in PORTING-STATE Session
  310.
- The `unguarded_walk_candidates.json` sweep (143 sites/43 funcs, 3 addressed) remains the fallback
  M3-audit work unit if a future session finds M5 blocked and maintenance isn't triggered.

HYPOTHESIS-ID: m5-audio-destub-step4-setdisplaymode-hang (same slug, s303-310 — still the active
investigation thread. s306/s307/s309/s310 have each produced a discriminating result in sequence —
resetting the iron-rule-8 no-progress counter every time; this is real, converging progress (H1 and H4
now refuted, H2/H3 the only remaining candidates), not a stall. Continue the same slug next session.)
