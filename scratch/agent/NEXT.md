# NEXT work unit — widen the GATE3_REACH/tick-audio-seq flat print caps and re-measure

(Written s312. See docs/CURRENT-TRUTH.md item -172 for the summary and `PORTING-STATE` Session 312 for
the full write-up.)

## Context — s312 found a fresh contradiction with the s307-s311 "soft stop at call 19/20" framing

s311 ruled out NEXT.md's Option A (musyx-gate1's raw countdown/period inputs never change through call
39). s312 executed Option A's sibling lead 1 (read the actual decrement-and-compare after `[musyx-gate1]`'s
load) via a full source-read of `musyxSynthFrame` (`funcs_24.c:3146` onward), which turned up two things:

1. **`[musyx-gate1]`'s own branch is provably, and now runtime-confirmedly, ALWAYS "skip"** in this
   window — `taken_skip=1` on all 40/40 samples this session (a new field added to the existing
   diagnostic, derived from `countdown!=1`). It cannot be the mechanism gating anything at call 19,
   because it never takes the "run" path at all across the full window.
2. **`update3DAudioFrame` (1 of the "3 gate-consumer functions") is gated by a completely separate,
   simpler mechanism than the countdown maze**: a single raw-byte read of `0x800A0F50` near
   `musyxSynthFrame`'s top (`funcs_24.c:3242-3259`), no countdown/period, no other condition between the
   read and the call. A new diagnostic (`[audio-gate-raw]`) logging that byte fresh every call found it
   **constant at 1 across all 40/40 samples (n=0-39)** — meaning `update3DAudioFrame`'s call MUST be
   happening on every one of `musyxSynthFrame`'s 40 confirmed entries in this window.

This is in direct tension with the s307/s310/s311 conclusion that `update3DAudioFrame` (and
`tickAllActiveSongs`/`tickAudioSequencerFrame`) "stop firing at call 19/20" — that conclusion rests on
`[reach-update3d-entry/exit]`/`[reach-allsongs-entry/exit]`/`[reach-audioseq-exit]`
(`ROGUESQ_LOG_INITMUSYX_REACH`, s306) and `[tick-audio-seq]` (`ROGUESQ_LOG_VOICE_TRIGGER_CHAIN`, s107).
**Both diagnostic families use a flat `if (n < 20) { print }` guard with NO modulo resample** — unlike
`[musyx-gate1]`/`[audio-gate-raw]`/`[audtask-dispatch]`/the 4 AUDIOTICK_TRACE tags, which all got a
`n%K==0` resample specifically so silence-past-cap is decisive (s310/s311's own fix for this exact class
of ambiguity). A log showing exactly 20 lines from the flat-cap family is consistent with either "really
stopped at 20" or "kept being called, print just stopped at line 20" — indistinguishable from the log
alone. Given `update3DAudioFrame`'s OWN gate byte stays nonzero through call 39 (a fresh, resampled,
decisive measurement), "kept being called" is now the better-supported reading for at least that one
function — but not yet DIRECTLY measured. **Flagged contested, not yet overturned in CURRENT-TRUTH.**

## The work unit

**Widen the flat `n<20` print caps to the established `n<40||(n%128)==0` convention** (or a numerically
equivalent resample) for every tag in this family, so the same soak that reproduces the freeze also
directly measures whether these functions' TRUE call counts stop at 20 or continue:

1. `fixup_game_funcs.py`, `_reach_entry_patch`/`_reach_exit_block` helpers (~line 7913-7943, used by
   `[reach-update3d-entry]`/`[reach-update3d-exit]`/`[reach-allsongs-entry]`/`[reach-allsongs-exit]`/
   `[reach-audioseq-exit]`): change `if ({varname}_n < 20)` to `if ({varname}_n < 40 || ({varname}_n % 128)
   == 0)`. This is a single shared-helper edit, applies to all 5 call sites at once — do not hand-edit
   each site.
2. `_tick_audio_seq_patch` (~line 1999-2012, `[tick-audio-seq]`, s107, `ROGUESQ_LOG_VOICE_TRIGGER_CHAIN`):
   same widening, `if (s_tick_audio_seq_n < 20)` → `if (s_tick_audio_seq_n < 40 || (s_tick_audio_seq_n %
   128) == 0)`.
3. Optionally also widen `_tick_all_audio_channels_patch` (~line 2028, `[tick-all-audio-channels]`) while
   in the area — same bug class, not yet cited in the active hypothesis but cheap to fix now per the
   batch-instrumentation rule (avoids a 3rd build-run cycle if it turns out relevant).

Regen (`fixup_game_funcs.py` edit → clear `N64Recomp/RecompiledFuncs/*.c` → `N64Recomp/build/N64Recomp
rogue_squadron.toml` → `python3 fixup_game_funcs.py` → `cmake --build build -j8`), re-reverse
`setDisplayMode`'s gate-byte site a 7th time (`reapplyDisplayMode` stays force-zero), one full 600s soak
(`ROGUESQ_LOG_VOICE_TRIGGER_CHAIN=1 ROGUESQ_LOG_INITMUSYX_REACH=1` both already armed in the
`run_step312rawgate.sh` template — copy it, bump the name), read the result, **revert `setDisplayMode`'s
site again same session** (mandatory, not safe to ship reversed — deterministic boot hang).

**Discriminating outcomes**:
- If `[reach-update3d-entry]` (etc.) print PAST n=20 (i.e. n=20, 21, ... appear, or a `n%128==0` line
  fires later) → the "soft stop at 19/20" conclusion is REFUTED for these functions; move it to
  Overturned Conclusions and reopen the search for why `[audtask-dispatch]` (independently, genuinely,
  resampled-confirmed) still stops at call 20 — likely a break further downstream in the chain from these
  3 functions to actual RSP `M_AUDTASK` submission, or a 4th function not yet on the gate-consumer list.
- If they stay silent past n=20 despite the widened cap (no `n=20+` lines, no `n%128==0` echo) → the
  original "soft stop" conclusion CONFIRMED with a 2nd, decisive line of evidence — the tension with
  `[audio-gate-raw]`'s constant-1 byte then needs its own explanation (e.g. a per-call condition INSIDE
  `update3DAudioFrame` itself, past its own entry, that this session's diagnostics don't reach — would
  need the entry tag itself confirmed still capped-not-stopped first, which this soak settles either way).

## Environment notes (carried forward, all still valid — see s311/s312 NEXT.md history for detail)

- Regen order and gotchas: `fixup_game_funcs.py` edit → clear `RecompiledFuncs/*.c` (python3 glob-delete)
  → `N64Recomp/build/N64Recomp rogue_squadron.toml` (cd into `N64Recomp` checkout FIRST as its own bare
  `cd` command, THEN run the binary with output redirection in a SEPARATE Bash call — combining `cd` and
  a redirect in one compound command triggers a permission prompt in this sandbox) → `python3
  fixup_game_funcs.py` (once; audit the patch report for the expected `xN` counts, especially "audio gate
  patched x1" while reversed / "x2" once reverted) → `cmake --build build -j8` (cwd = this repo root,
  `DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer` prefix, this exact form is allowlisted
  verbatim). `make_elf.py` not needed unless source/symbol mapping changed.
- Soak driver template: `scratch/s73_post_a_scene/run_step312rawgate.sh` (s312's recipe, copied from
  s311's `run_step311gate1cap.sh`) — copy it, don't hand-roll a new script; bump the output-dir name
  (last line's `${1:-...}` default) and the header comment. `ROGUESQ_LOG_AUDIOTICK_TRACE=1`,
  `ROGUESQ_LOG_VOICE_TRIGGER_CHAIN=1`, and `ROGUESQ_LOG_INITMUSYX_REACH=1` are all already armed in it.
- Launch the soak via Bash with `run_in_background: true`, then `TaskOutput` with `block: true` and
  `timeout` up to 600000ms — do NOT foreground-poll. `run_mission_keys.sh`'s own 600s phase-timeout exits
  nonzero (exit 5, `INCONCLUSIVE`) on the expected deterministic hang — that's success for this soak
  design, not a tooling failure; the game process is killed automatically on that path. Confirm
  `pgrep -f "build/RogueSquadron64Recomp"` is empty before AND after.
- `/tmp` is blocked for redirects — use a path inside this repo, `N64Recomp`, or `rogue_squadron64`
  instead.
- `scratch/s73_post_a_scene/step312rawgate/run.log` is s312's saved log (740610 bytes) if a future
  session wants to re-verify `[audio-gate-raw]`/`[musyx-gate1] taken_skip`/`[reach-*]` counts before
  building.

HYPOTHESIS-ID: m5-audio-destub-step4-setdisplaymode-hang (same slug, s303-312 — still the active
investigation thread. Each of s306/s307/s309/s310/s311/s312 has produced a discriminating result in
sequence — resetting the iron-rule-8 no-progress counter every time; this is real, converging progress
(H1/H4 refuted, Option A ruled out, two freeze boundaries dated, and now a methodological gap found in
the diagnostic underlying the "soft stop" framing itself), not a stall. Continue the same slug next
session.)
