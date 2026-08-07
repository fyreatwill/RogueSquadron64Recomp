# NEXT work unit

HYPOTHESIS-ID: m3-dod-warroom-crash-s423

## s423 recap

Acted on s422's own pre-authorized fallback (USER DIRECTIVE's three legs all closed/exhausted, loop
restarted with no fresh human direction): ran the M3-DoD first-look driven-run calibration NEXT.md had
specified. It did NOT reach mission content, or even AVAILABLE CRAFT/SELECT YOUR CRAFT — it surfaced two
new findings instead:

1. **SELECT GAME "waits for input indefinitely" is real and costly**: the menu sat at VI=1024 (title +
   SELECT GAME share that width) for 134s despite 4 presses scheduled within the first 15s; only a much
   later press (~100-130s) actually advanced it. A `"3:start 7:start 11:start"`-style rapid cadence does
   NOT work on this screen — most of those presses appear to have been dropped or ignored.
2. **New crash, one phase further than any prior soak**: ~1.3s after finally reaching the war-room/SELECT
   LEVEL screen (VI=512, origin `0x6AB400`), SIGBUS in `startPlayerSlotAnimationChannelLooping+456`
   (backtrace `startSlotLoopAnimWithVoiceSync → tickCraftSelectScreen → drawRadarIcon → menuOverlayInit →
   mainGameLoop`), sharing s422's `0x800290d4` sparse-breadcrumb last-guest-pc value. This is a SEVENTH
   function converging on that sink — NOT one of the six `m4_known_bad.txt` phantom-relocation functions
   — and the first one hit during ordinary menu progression, not an M4 bisection experiment.

Single-source (one run). Confirmation soak queued: `scratch/agent/soak_queue/s423_m3dod_warroom_crash_confirm.sh`
(identical schedule, checks `run.log` for the same `0x800290d4` signature / a different crash / a clean
512-phase arrival / no-positive-control). Full detail: `PORTING-STATE` Session 423, `CURRENT-TRUTH` item
-260.

## Where this leaves the USER DIRECTIVE

Still needs human reconfirmation on strategic direction — s423 does not resolve that, it adds new
information relevant to it: if the war-room crash reproduces, the `0x800290d4` sink s422 declined to
root-cause is now blocking M3 forward progress, not only an M4-relocation side effect. That could argue
for reopening a dedicated root-cause session specifically for `startPlayerSlotAnimationChannelLooping`
once reproduction-confirmed — but that is a call for whoever reconfirms direction, not something to
pre-empt autonomously (the USER DIRECTIVE's M3 constraint is idiom-class audits, not reactive
single-crash chases, and a fresh crash is exactly a reactive chase unless/until it's established as
systemic).

## Work unit for the next iteration

**Read `scratch/agent/SOAK-RESULTS.md` (tail) FIRST** — the confirmation soak may have already run
between iterations. Three branches depending on what it shows:

1. **If `s423_m3dod_warroom_crash_confirm` REPRODUCED (same `0x800290d4` signature)**: two independent
   data points now exist for a genuinely new crash blocking M3 progress at the earliest post-title
   transition. This crosses from "single anecdote" to "reproducible" — the next work unit is deciding
   (or asking the human to decide) whether this becomes the M3 root-cause target, superseding the
   "idiom-audit-only, no reactive chases" framing since it's no longer a one-off. Do NOT start a
   root-cause session without either explicit human sign-off or a second reproduction plus a clear
   argument that this is now systemic (blocking ALL forward menu progress, not an edge case).
2. **If it shows a DIFFERENT crash or NO_POSITIVE_CONTROL**: the war-room crash is not yet established
   as reliably reproducible. Re-run the identical schedule ONE more time (still single low-cost soak,
   still not a root-cause session) before concluding either way — 1 data point is not a result, 2
   matching is a weak signal, per iron rule 4 (two independent lines of evidence).
3. **If neither has run yet**: this iteration IS the soak — either wait for the queue to process it, or
   (if urgency is low) pick a different bounded work unit and let the queue catch up; do not spend a live
   foreground game run duplicating what's already queued.

**Separately, regardless of the above**: the SELECT-GAME input-timing finding (item 1 above) is worth
fixing once, independent of the crash thread — future driven runs past the title screen should NOT
assume `"N:start N+4:start N+8:start"` works past SELECT GAME. If/when another driven-run work unit is
attempted, budget 100-150s+ of real time between the title-arrival press and the war-room-entry press,
or find a `[keys]`-adjacent log line that proves the game's menu handler actually consumed a given press
(not just that the OS posted it) so schedules can be built confidently instead of by guesswork.

## Soak queue

- `scratch/agent/soak_queue/s423_m3dod_warroom_crash_confirm.sh` — queued this session, not yet run.
