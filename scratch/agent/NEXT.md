# NEXT work unit — source-read: what does `setDisplayMode` write to the audio gate byte?

## Context (read `docs/M5-AUDIO-PLAN.md` §4 step 4, and CURRENT-TRUTH Next-steps item -165 —
condensed pointer, not a re-derivation)

s303 attempted the 2nd slice of M5-AUDIO-PLAN.md step 4: reversed `setDisplayMode`'s gate-byte
force-zero site (`0x8008EB40`, `N64Recomp/fixup_game_funcs.py`). 2/2 validation soaks reproduced an
**identical deterministic full boot hang**: VI width stuck at 320 (never reaches title) for the
entire 600s window, exactly 39 RSP tasks executed both times. This does NOT match family #1's known
string signature and does NOT go through `waitForAnyAudioSlot`'s drain loop (0 log lines both soaks
— that loop was never entered) — it's a different, currently unlocalized stall, but unambiguously
caused by this specific site's reversal (this signature never appeared in any of s300-302's soaks).
**Re-reverted same session** — the committed baseline is back to exactly s302's validated state
(`initMusyXEngine` alone reversed, `setDisplayMode`/`reapplyDisplayMode` both force-zeroed again).
Full detail: `PORTING-STATE` Session 303.

**Do not re-attempt reversing `setDisplayMode`'s site blind** — that's proven to hang. This session's
work is a FREE source-read (no build/soak) to find out WHY, before touching either remaining site.

## The work unit

Read `N64Recomp/RecompiledFuncs/funcs_23.c` around `setDisplayMode` (currently regenerated with the
force-zero patch active — search for `0x8008EB40: sb          $v0, 0xF50($at)`, currently shows
`MEM_B(0XF50, ctx->r1) = 0; // PATCH: force audio-engine-disabled`). Trace backward from that line to
find where `ctx->r2` (`$v0`) is computed in `setDisplayMode` — is it:
- a fixed immediate (`li $v0, N` for a constant N, same shape as `initMusyXEngine`'s write, which
  s302 confirmed is "the real init-success value")? If so, the hang is NOT explained by "wrong value
  written" and the mechanism must be call-frequency-related (setDisplayMode is called more than once,
  vs. initMusyXEngine's boot-once call) — pivot to instrumenting call count / gate-byte value over
  time instead.
- a computed/branch-dependent value (e.g. derived from a display-mode-change success/failure code, or
  copied from some other register that has nothing semantically to do with "audio enabled")? If so,
  this write was likely never intended as a general-purpose "audio enable" toggle at this call site —
  the shared address `0x800A0F50` may be doing double duty, and letting this specific write through
  could be writing garbage/wrong-state into the gate byte, which downstream audio-tick code (already
  identified in s300: `update3DAudioFrame`, `tickAllActiveSongs`, `tickAudioSequencerFrame` inside
  `musyxSynthFrame`) may not handle gracefully.

Also do the same read for `initMusyXEngine`'s already-reversed site (`0x8008E9F8`) as a comparison
baseline — confirm textually that its $v0 source really is a simple constant, to sharpen the contrast.

**Do NOT build or soak this session unless the source-read produces a concrete new hypothesis worth
testing** — if it does, that becomes next session's build+soak work unit (name it explicitly in the
next NEXT.md write-up, don't just re-try the same reversal).

## Fallback if the source-read is inconclusive or setDisplayMode's write also turns out to be a
simple constant (i.e. "wrong value" is refuted)

Pivot to instrumenting: how many times is `setDisplayMode` called during the boot→title window, and
what does the gate byte actually read as immediately before the hang's onset (task #39, i.e. within
the first ~5-10 real RSP tasks)? A repeated ON/OFF toggle racing with `musyxSynthFrame`'s per-VI-tick
read could produce a livelock-shaped slowdown (not a true infinite loop, hence the 39 tasks over 600s
rather than exactly 0) without ever entering `waitForAnyAudioSlot` at all. This would need one cheap
counter (`ROGUESQ_LOG_...` env-gated, gate-byte value + call-site tag logged once per
`setDisplayMode`/`musyxSynthFrame`-gate-read pair) — batch it into the same build as whatever the
source-read suggests, per the "one build carrying every counter" rule.

## Environment notes (carried forward, all still valid)

- Regen order still applies: `make_elf.py` only if a source-level change is made → `N64Recomp` →
  `fixup_game_funcs.py` → `cmake`. This session's work is read-only against the regenerated
  `funcs_23.c` — no regen needed unless a new instrument gets added (see fallback above).
- `N64Recomp/fixup_game_funcs.py` is NOT git-tracked in the `N64Recomp` checkout itself — the durable
  record is this project's own `PORTING-STATE.md`/`CURRENT-TRUTH.md` plus the physical file on disk.
- Soak driver template if a build+soak becomes warranted: `scratch/s73_post_a_scene/run_step4gate3.sh`
  (already exists from s303, reusable as-is if the change under test doesn't need new env vars).
- **Waiting on a soak**: `run_in_background: true` for the game launch, then poll the actual game pid
  (`pgrep -f "\./RogueSquadron64Recomp"`) with a foreground polling-loop script (not a bare `sleep`) —
  see `scratch/agent/wait_step4gate3_1b.sh` for a reusable 580s-budget polling template. A single Bash
  tool call caps at 600000ms, so a 600s phase-timeout soak needs the polling script's own internal
  budget to stay under that, or a 2nd Bash call to finish waiting.
- **One game run at a time** — confirm `pgrep -f "\./RogueSquadron64Recomp"` is empty before launching
  the next soak.
- `[phase]` line count is a fast triage signal: 2 lines total (stuck at width=320 forever) means a
  s303-style hang; many lines advancing through 640→1024 means normal progress. Check this FIRST
  before reading the rest of a soak's ~700KB+ log.
- The `unguarded_walk_candidates.json` sweep (143 sites/43 funcs, 3 addressed) remains the fallback
  M3-audit work unit if a future session finds M5 blocked and maintenance isn't triggered.

HYPOTHESIS-ID: m5-audio-destub-step4-setdisplaymode-hang
