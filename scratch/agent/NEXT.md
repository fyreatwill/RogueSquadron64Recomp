# NEXT work unit — M5-AUDIO-PLAN.md step 4 (continued): reverse `setDisplayMode`'s gate-byte site

## Context (read `docs/M5-AUDIO-PLAN.md` §4 step 4, and CURRENT-TRUTH Next-steps item -164 — condensed
pointer, not a re-derivation)

s302 executed the first slice of step 4: reversed `initMusyXEngine`'s gate-byte force-zero site
(`0x8008E9F8`) in `N64Recomp/fixup_game_funcs.py`, validated with 2 soaks — 0/2 recurrence of crash
family #1's signature (`waitForMusyXAudioTaskDone`/`shutdownAudioEngine` hang), `WAITFORSLOT_GUARD`
fired 0/2, both soaks instead died to independently pre-existing, already-documented crash classes
(RDRAM-host-base/`reserveAndEmitDLEntry`; `evalCubicSplineAtTime` NaN div0). Full detail:
`PORTING-STATE` Session 302.

**Do not re-run step 4's `initMusyXEngine` soaks** — done, evidence recorded. This session's work is
the second of the plan's 3 gate-byte sites: `setDisplayMode` (`0x8008EB40`).

## The work unit

`N64Recomp/fixup_game_funcs.py` currently has (after s302's split):

    new, n = re.subn(
        r"(// 0x8008E(?:B40|C88): sb          \$v0, 0xF50\(\$at\)\n    MEM_B\(0XF50, ctx->r1\)) = ctx->r2;",
        r"\1 = 0; // PATCH: force audio-engine-disabled (MusyX stubbed; spin-wait wedges coop scheduler)",
        text)

Split this further: remove `B40` from the alternation (leaving only `C88`/`reapplyDisplayMode` force-
zeroed), so `setDisplayMode`'s site (`0x8008EB40`, in `funcs_23.c`, function `setDisplayMode`) falls
through to the guest's own write. Regen order: `cd N64Recomp && ./build/N64Recomp rogue_squadron.toml
&& python3 fixup_game_funcs.py` (expect `audio gate patched x1` now, was `x2`), then from repo root
`DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build build -j8`. Confirm by
inspecting the regenerated `funcs_23.c` around the `setDisplayMode` function (search `sb          $v0,
0xF50($at)` — should show `MEM_B(0XF50, ctx->r1) = ctx->r2;` with no `= 0` override).

**Why this site is riskier than `initMusyXEngine`**: `setDisplayMode` runs on every display-mode
change, not just once at boot — the plan flagged this as "a much hotter path" than the boot-time-only
`initMusyXEngine` site. Watch for any NEW recurrence pattern tied to display-mode transitions
specifically (title→menu, menu→craft-select, etc.), not just family #1's exact hang signature.

## Validation soak

Same recipe as s301/s302: copy `scratch/s73_post_a_scene/run_step4gate2.sh` (or `run_waitforslotguard1.sh`)
to a new `run_step4gate3.sh` (relabel the header comment and the `run_mission_keys.sh` argument), keep
`ROGUESQ_AUDIO_UCODE=1` and `ROGUESQ_LOG_WAITFORSLOT_GUARD=1` armed, plus the full passive
diagnostic/guard set already in that script.

**Discriminating outcomes** (same structure as step 4's first slice):
1. Crash family #1's exact signature recurs (`waitForMusyXAudioTaskDone`/`shutdownAudioEngine` boot-
   scheduler-wedge hang — a HANG, process stays alive until harness timeout, not a crash) → needs a
   source-level fix in the ucode's task-completion signaling. Do NOT just re-force this site's gate
   zero and call it done.
2. 2 soaks, 0/2 family #1 recurrence (crashes to other pre-existing classes are fine, as s302 found —
   check the crashing signature against the already-documented classes before treating it as new) →
   reverse `reapplyDisplayMode`'s site next session (the last of the 3), same validation.
3. A new/unattributable crash signature tied specifically to a display-mode-change moment → do not
   dismiss as baseline noise; check whether the crashing function's own entry diagnostics fired (s301's
   method: zero entry-diagnostic lines despite the crash PC resolving inside an instrumented function's
   byte range = corrupted-jump/wild-write signature, not a legitimate call).

## Environment notes (carried forward, all still valid)

- Regen order still applies: `make_elf.py` only if a source-level change is made (none needed for this
  slice — it's a `fixup_game_funcs.py`-only edit) → `N64Recomp` → `fixup_game_funcs.py` → `cmake`.
- `N64Recomp/fixup_game_funcs.py` is NOT git-tracked in the `N64Recomp` checkout itself — the durable
  record is this project's own `PORTING-STATE.md`/`CURRENT-TRUTH.md` plus the physical file on disk.
  No `submodule-patches/export.sh` applies (that's only for `lib/N64ModernRuntime`/`lib/rt64`).
- Soak driver: build `run_step4gate3.sh` from the `run_step4gate2.sh` template (env-var block +
  `ROGUESQ_AUDIO_UCODE=1`/`ROGUESQ_LOG_WAITFORSLOT_GUARD=1`). `HOLD_S`/`PROBE_MODE` env-overridable,
  phase-gates on VI width 1024, self-SIGKILLs at the end, prints a `--- summary ---` block.
- **Waiting on a soak**: `run_in_background: true` then find the game's own pid (`pgrep -f
  "\./RogueSquadron64Recomp"`) and block on it with a foreground Bash call
  (`while kill -0 <pid> 2>/dev/null; do sleep 5; done; echo done`, generous timeout e.g. 400000ms) — a
  bare foreground `sleep` is rejected but a polling loop like this is accepted and genuinely blocks
  wall-clock time within the same tool call, which is what let s302 finish within one turn under the
  Stop-hook's synchronous exit-contract check. Do NOT rely on Monitor/background-notification alone to
  end the turn — the Stop hook fires and blocks immediately regardless of pending background tasks; the
  turn must not end until the exit contract files are actually written.
- **One game run at a time** — confirm the prior soak's game process (`RogueSquadron64Recomp` binary
  itself, not the wrapper `tail -f`/`zsh` processes) has actually exited before launching the next.
- s302's own crash data point: both soaks died within the first hold-iter (~15s into a 240s window) to
  pre-existing crash classes unrelated to this change — budget for this again; a soak reaching the full
  240s hold window has not happened recently for this scene, independent of the audio work.
- The `unguarded_walk_candidates.json` sweep (143 sites/43 funcs, 3 addressed) remains the fallback
  M3-audit work unit if a future session finds M5 blocked and maintenance isn't triggered.

HYPOTHESIS-ID: m5-audio-destub-step4
