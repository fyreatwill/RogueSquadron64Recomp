# NEXT work unit

## s373 CLOSED the `m5-audio-destub-step6-pcm-sanity` thread (iteration 2, as planned)

Question answered via pure source trace, no soak needed: PCM is silent because voices are never
populated in the first place, not because of an internal ucode mixing bug. Full mechanism:
`docs/CURRENT-TRUTH.md` item -227, `docs/M5-AUDIO-PLAN.md` §4 Step 6, `PORTING-STATE.md` Session 373.

One-paragraph version: `tickMusyXIfActive` (sole caller of the voice-population functions,
`tickActiveSongs`/`tickAndReap3DAudioVoices`) short-circuits whenever the gate byte at `0x800A0F50`
reads 0. `reapplyDisplayMode` runs every video frame, unconditionally zeros that byte at its own
entry, then (when `reapplyAudioConfig` succeeds — the common case) resets the whole song/voice/stream
state and would restore the byte to 1 at its tail — except that tail write (`0x8008EC88`) is the
exact site `N64Recomp/fixup_game_funcs.py` force-zeroes, and it has to stay that way (s343: reversing
it broke title-reach 0/5 times). Net: every frame wipes any voice state and never durably re-opens
the gate, so the RSP ucode is faithfully mixing "nothing" — Hypothesis 1 (voice array never
populated) confirmed, Hypotheses 2/3 (internal mixing gate, wrong buffer) are moot.

## The decision this closes into — pick ONE explicitly, don't default

M5's plan doc (`M5-AUDIO-PLAN.md` §4) now has every step (1-6) either DONE or ANSWERED. The only
remaining path to actual audible audio is resolving why reversing the C88 (`reapplyDisplayMode`)
gate site causes a deterministic pre-title hang — and that specific question was never root-caused
even across the original 41-session s297-337 gate-reversal arc (PROJECT-OVERVIEW §9), which closed
on an empirical revert, not a mechanism finding. Two legitimate options for the next iteration:

**Option A — reopen it, but narrowly, with fresh context this session's read supplied.** The old
arc never had today's structural picture of `reapplyDisplayMode` (the entry-zero + conditional
reset + tail-reenable toggle, s373). A bounded FIRST probe, source-read only, no soak (mirrors
M5-AUDIO-PLAN Step 1's own precedent):
- Competing hypotheses for why C88-reversed hangs pre-title:
  1. **First-ever execution of the 3 previously-gated `musyxSynthFrame` functions**
     (`update3DAudioFrame`/`tickAllActiveSongs`/`tickAudioSequencerFrame`, s304's original leading
     hypothesis, never actually confirmed or refuted for the PRE-TITLE hang specifically — s304's
     discussion was about the VI=320 `setDisplayMode` hang, a different, already-fixed issue).
  2. **A durable gate=1 exposes `tickMusyXIfActive`'s newly-unblocked voice-population calls
     (`tickActiveSongs`/`tickAndReap3DAudioVoices`) to some other pre-title-time state that's
     invalid/uninitialized this early in boot** — plausible given voices have literally never run
     this early in any prior soak.
  3. **The toggle race itself**: with C88 unblocked, gate flips 0→(reset)→1 every frame; if some
     OTHER thread reads the gate mid-reset (during the ~5-function reset window before the
     re-enable), it could observe a transient state the original single-threaded N64 hardware
     never produced at this timing.
  - Discriminating read: grep every caller of the 3 functions in hypothesis 1 AND of
    `tickActiveSongs`/`tickAndReap3DAudioVoides` for what they touch before the hang's last known
    log line (per s342/343's logs, if still on disk) — same method s304 used for the VI=320 hang,
    applied to the pre-title hang instead. If inconclusive from source alone, the next step is a
    build+soak with entry/exit tags on all 5 functions (batch instrumentation, one soak) — do NOT
    build blind before this source pass.
  - New `HYPOTHESIS-ID` if pursued: `m5-audio-destub-c88-pretitle-hang`.

**Option B — pivot to M3 idiom-class audits (strategic priority 3).** M5's actionable plan is
exhausted; Option A is explicitly a NEW, potentially multi-session investigation, not a quick
follow-on. Per the strategic priority order this is still legitimate to defer if Option A's first
source pass (above) doesn't quickly narrow the field — M3 audits are the standing fallback per
`docs/CURRENT-TRUTH.md`'s USER DIRECTIVE.

Either is a legitimate call for the next iteration — make it explicitly (write which one and why),
don't default silently.

## Iteration budget

This is a fresh decision point, not a continuation — if Option A is picked, `m5-audio-destub-c88-pretitle-hang`
starts its own budget at iteration 1. If Option B, this is a normal M3-audit iteration, no
hypothesis-ID budget carries over.

HYPOTHESIS-ID: none active — next iteration must pick Option A or B above and set one.
