# NEXT work unit — settle whether `initMusyXEngine` is ever reached, batched with the 3
# gate-consumer function tags

## Context (read `docs/CURRENT-TRUTH.md` item -166 and `PORTING-STATE` Session 304 — condensed
## pointer, not a re-derivation)

s304's source-read refuted both of s303's anticipated hypotheses for why reversing `setDisplayMode`'s
gate-byte force-zero site (`0x8008EB40`) deterministically hangs boot (2/2 soaks, VI stuck at width 320,
39 RSP tasks, 600s): the write is a simple constant `1` (not a wrong/computed value), and
`setDisplayMode` is called exactly once at boot (not a hot per-frame path) — same shape as
`initMusyXEngine`'s already-reversed, already-validated site.

s304 also surfaced a single-source (text-grep only) finding that could invalidate s302's validation
entirely: **no code anywhere in `RecompiledFuncs/*.c` appears to call `initMusyXEngine`** — no direct
`jal` to `0x8008E940`, no `lui`/`addiu` absolute-pointer construction of that address anywhere outside
its own function body. If true, s302's "clean" 2-soak validation of reversing `initMusyXEngine`'s site
never actually put a nonzero value in the gate byte during either soak — meaning `setDisplayMode`'s
s303 reversal would be the FIRST time the gate byte has ever gone nonzero in a real run, and the
leading explanation for the hang becomes "first-ever execution of `musyxSynthFrame`'s 3 previously
always-skipped ancillary functions" (`update3DAudioFrame`, `tickAllActiveSongs`,
`tickAudioSequencerFrame`, per s300 item -162) — not anything specific to `setDisplayMode`'s own write.

## The work unit

**Step 1 — settle reachability.** Add ONE cheap entry counter/log line to `initMusyXEngine`
(`0x8008E940` in `N64Recomp/RecompiledFuncs/funcs_23.c`, patched via `N64Recomp/fixup_game_funcs.py` so
it survives regen) — env-gated (`ROGUESQ_LOG_INITMUSYX` or similar), fires once per call. **This needs
a same-run positive control**, per iron rule 1 — a null result (0 fires) is worthless without proof the
logging mechanism itself works. Add a matching log line to a function `initMusyXEngine` is KNOWN to
call unconditionally on every invocation (e.g. `resetMusyXEngineState`, called from within it) so the
soak has a "mark everything" comparison: if `resetMusyXEngineState`'s counter fires but
`initMusyXEngine`'s never does, that's a clean, controlled null — reachability genuinely refuted, not a
broken instrument.

**Step 2 — batch in the downstream tags while you're building anyway** (per "one build carrying every
counter" rule, don't spend a 2nd build-run cycle later). Add entry/exit tagged log lines to
`update3DAudioFrame`, `tickAllActiveSongs`, `tickAudioSequencerFrame` (the 3 functions `musyxSynthFrame`
gates on the gate byte, per s300 item -162 / `funcs_23.c:6785`, `funcs_24.c:3146` for the read sites) —
these are inert (log-only) at the CURRENT baseline since the gate is 0 whenever these would be reached,
so they cost nothing this soak but save a build-run cycle for whichever next step follows.

**Step 3 — soak the CURRENT baseline, do NOT touch `setDisplayMode`'s site this session.** Current
baseline = `initMusyXEngine` reversed (real write, per s302), `setDisplayMode`/`reapplyDisplayMode`
still force-zeroed (per s303's revert, unchanged since). Soak template:
`scratch/s73_post_a_scene/run_step4gate2.sh` (s302's already-validated recipe) — add the new env var(s)
for the new instruments, keep everything else identical. One soak, boot→title→hold, same
`ROGUESQ_AUDIO_UCODE=1` arming as prior soaks in this thread.

## Expected discriminating outcomes

- **`initMusyXEngine` counter fires (>0), `resetMusyXEngineState` counter also fires (positive
  control confirmed)**: reachability CONFIRMED — `initMusyXEngine` really does run, gate=1 really was
  exercised safely for ~75s in s302 as s303 assumed. This REFUTES the "first-ever execution" theory as
  currently framed — the 3 downstream functions (if they also fire in this soak, confirming gate=1 took
  effect and `musyxSynthFrame` read it) already ran without incident under `initMusyXEngine`'s reversal.
  In this branch, the open question reverts to something specific to `setDisplayMode`'s own toggle
  structure (entry-zero → reset sequence → re-enable, all inside one call) — next-next session's work
  becomes re-reversing `setDisplayMode`'s site WITH the 3-function tags already in place (from step 2)
  to localize exactly which of the 3, if any, is where the hang lands.
- **`initMusyXEngine` counter never fires, `resetMusyXEngineState` counter DOES fire (clean, controlled
  null)**: reachability REFUTED — `initMusyXEngine` is dead code in the currently-recompiled game.
  s302's validation is retroactively meaningless (it validated an unreached code path). This promotes
  "first-ever execution of the 3 previously-skipped functions inside `musyxSynthFrame`" from
  leading-but-unconfirmed to the primary hypothesis for s303's hang. Update CURRENT-TRUTH's
  Overturned-conclusions section to flag s302's validation as not meaningful (with why it was
  believable — the soaks WERE clean, just for the wrong reason). Next-next session's work becomes:
  re-reverse `setDisplayMode`'s site with the 3-function tags in place, soak, and read WHICH of the 3
  functions logs entry but never logs exit (localizes the actual hang site) — or if none of the 3 even
  log entry, the stall is somewhere else entirely (inside `initAudioSubsystem` itself, or one of the
  reset-sequence calls, called unconditionally by `setDisplayMode` regardless of the gate patch — a
  3rd hypothesis class not yet explored).
- **Neither counter fires (both null)**: broken instrument, not a data result — the logging mechanism
  itself is faulty (env var name typo, patch didn't land, wrong log level). Fix and re-soak before
  drawing any conclusion; do not report this as "resetMusyXEngineState also dead code" without first
  confirming the log macro/env-gate works via a totally unrelated always-firing counter already known
  good (e.g. `[audtask-dispatch]` from s300, still presumably active).

## Environment notes (carried forward, all still valid)

- Regen order: source-level patch → `N64Recomp/fixup_game_funcs.py` → `cmake`. `make_elf.py` only
  needed if editing the original guest source, not applicable here (these are code-gen patches).
- `N64Recomp/fixup_game_funcs.py` is NOT git-tracked in the `N64Recomp` checkout itself — durable
  record is this project's own `PORTING-STATE.md`/`CURRENT-TRUTH.md` plus the physical file on disk.
- Soak driver template: `scratch/s73_post_a_scene/run_step4gate2.sh` (s302's recipe, already validated
  for the current baseline config) — copy and add the new env var(s), don't hand-roll a new script.
- **Waiting on a soak**: `run_in_background: true` for the game launch, then poll the actual game pid
  (`pgrep -f "\./RogueSquadron64Recomp"`) with a foreground polling-loop script (not a bare `sleep`) —
  see `scratch/agent/wait_step4gate3_1b.sh` for a reusable 580s-budget polling template.
- **One game run at a time** — confirm `pgrep -f "\./RogueSquadron64Recomp"` is empty before launching.
- `[phase]` line count is a fast triage signal: 2 lines total (stuck at width=320 forever) means a
  s303-style hang; many lines advancing through 640→1024 means normal progress. Check this FIRST.
- The `unguarded_walk_candidates.json` sweep (143 sites/43 funcs, 3 addressed) remains the fallback
  M3-audit work unit if a future session finds M5 blocked and maintenance isn't triggered.

HYPOTHESIS-ID: m5-audio-destub-step4-setdisplaymode-hang (iteration 3 on this slug — s303 created it,
s304 was iteration 2 (pure source-read, no pivot), this write-up is iteration 3's plan. Per iron rule 8,
a 4th consecutive iteration on this exact slug would need a pivot preamble if it produces no
discriminating result — the step-1/step-2 counter soak above IS designed to discriminate, so this
should not trigger that.)
