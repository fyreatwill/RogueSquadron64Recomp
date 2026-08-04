# NEXT work unit — re-reverse setDisplayMode's gate-byte site, with the 3
# gate-consumer entry/exit tags already armed, to localize s303's hang

(Written s306, a hypothesis-execution iteration — see docs/CURRENT-TRUTH.md item -167 for the full
write-up and `PORTING-STATE` Session 306 for full detail.)

## Context

s306 settled the open question s304 raised: a same-run-positive-controlled entry counter
(`ROGUESQ_LOG_INITMUSYX_REACH`), run across 2 soaks (one full-length 300s, zero crashes; one cut short
by an unrelated, already-catalogued crash), found `initMusyXEngine` is **never called** anywhere in the
current recompiled game — 0 fires across both soaks, while the positive control
(`resetMusyXEngineState`, called independently from `setDisplayMode`/`reapplyDisplayMode`) fired 2 and 7
times respectively, confirming the logging plumbing itself works. This retroactively invalidates s302's
"clean" validation of reversing `initMusyXEngine`'s gate-byte site — that reversed write never executed
in either of s302's soaks, so its cleanliness reflects dead code, not a proven-safe gate=1 state.

**Net effect**: gate=1 has still never been exercised by any soak conducted to date. s303's reversal of
`setDisplayMode`'s site (`0x8008EB40`) remains the only attempt that ever put a nonzero value in the
gate byte during a real run, and it produced a deterministic full-boot hang (2/2 soaks, VI stuck at
width 320 the entire 600s window, exactly 39 RSP tasks both times). s303 re-reverted the same session
without localizing which of the 3 gate-consumer functions (`update3DAudioFrame`, `tickAllActiveSongs`,
`tickAudioSequencerFrame` — the only 3 functions `musyxSynthFrame` gates on this byte, per s300 item
-162) the hang actually lands in, if any of them at all.

s306 batched in exactly the instrument needed to answer that localization question, ready and armed but
never yet exercised under gate=1 (since the baseline it soaked was gate=0 throughout, per
`initMusyXEngine` being dead code): `[reach-update3d-entry]`/`[reach-update3d-exit]`,
`[reach-allsongs-entry]`/`[reach-allsongs-exit]`, `[reach-audioseq-exit]` (entry already covered by the
pre-existing s107 `[tick-audio-seq]` under `ROGUESQ_LOG_VOICE_TRIGGER_CHAIN`), all gated by
`ROGUESQ_LOG_INITMUSYX_REACH=1`.

## The work unit

**Step 1 — re-reverse `setDisplayMode`'s gate-byte force-zero site**, same edit s303 made and then
undid: split the regex in `fixup_game_funcs.py` so `setDisplayMode`'s force-zero patch is skipped
(`initMusyXEngine`'s stays reversed too — it's a no-op either way since it's dead code, no need to
re-revert it back; `reapplyDisplayMode`'s stays force-zeroed, unchanged, per the plan's one-site-per-
session design). Regen: clear `RecompiledFuncs/`, `N64Recomp rogue_squadron.toml`,
`python3 fixup_game_funcs.py`, `cmake --build build -j8`.

**Step 2 — soak with everything armed.** Copy `scratch/s73_post_a_scene/run_step5reach1.sh` (this
session's already-validated recipe, carries `ROGUESQ_LOG_INITMUSYX_REACH=1` plus the full passive
diagnostic set) — no new env vars needed, everything required is already armed. Expect the same
deterministic hang s303 saw (VI stuck at 320, 2 minutes should be enough to confirm the signature
recurs — don't wait the full 600s if the phase log shows the same 2-lines-total stuck-at-320 pattern
within the first 60-90s).

**Step 3 — read the log for which of the 3 functions logged entry but not exit.**
- If NONE of the 3 log even entry: the hang is not inside any of them — it's somewhere else entirely,
  either inside `initAudioSubsystem` itself or one of the reset-sequence calls `setDisplayMode` makes
  unconditionally regardless of the gate patch (per s304's structural finding: `setDisplayMode`
  sandwiches `resetSongSubsystemCounter`→...→`reset3DAudioLists` between its own entry-zero and
  tail-re-enable of the gate byte — the hang could be in that reset sequence, not downstream of the
  gate at all). Next step: source-read that reset sequence.
- If exactly one of the 3 logs entry but never exit: that function is the hang site — dig into its body
  next (source-read what happens after its logged entry point, guest-instruction by guest-instruction,
  same method as s304's `setDisplayMode`/`initMusyXEngine` source-read).
- If one or more log both entry AND exit cleanly: those functions are NOT the hang site; narrows the
  remaining candidates.

## Expected discriminating outcomes

Each of the 3 outcomes above points to a different next investigation (dig into the reset sequence vs.
dig into a specific gated function's body vs. narrow further) — this is a genuine localization step, not
a repeat of s303's undifferentiated black-box reversal.

## Environment notes (carried forward, all still valid)

- Regen order: `fixup_game_funcs.py` edit → clear `N64Recomp/RecompiledFuncs/*.c` (python3 glob-delete,
  plain `rm`/`find -delete` are blocked in this sandbox) → `N64Recomp/build/N64Recomp
  rogue_squadron.toml` (cwd = `N64Recomp` checkout) → `python3 fixup_game_funcs.py` (run exactly once,
  refuses a 2nd run via its own SENTINEL check) → `DEVELOPER_DIR=/Applications/Xcode.app/Contents/
  Developer cmake --build build -j8` (cwd = this repo root). `make_elf.py` not needed unless
  source/symbol mapping changed (it didn't).
- `N64Recomp/fixup_game_funcs.py` is NOT git-tracked in that checkout — durable record is this project's
  own `PORTING-STATE.md`/`CURRENT-TRUTH.md` plus the physical file on disk.
- Soak driver template: `scratch/s73_post_a_scene/run_step5reach1.sh` (s306's recipe, copy it — don't
  hand-roll a new script; only the fixup-script edit changes between this session and the next, the
  soak env vars needed are already all armed).
- **Waiting on a soak**: launch via Bash with `run_in_background: true`, then use `TaskOutput` with
  `block: true` and a generous `timeout` (up to 480000ms) to wait for completion — do NOT foreground-
  poll with a bare `sleep` loop (blocked in this harness) or hand-rolled `pgrep` polling loops (noisy,
  unnecessary — the background task auto-notifies on completion).
- **One game run at a time** — confirm `pgrep -f "\./RogueSquadron64Recomp"` is empty before launching.
- `[phase]` line count is a fast triage signal: 2-3 lines total stuck at width 320 (s303's/s306-soak1's
  signature) means a hang or an early crash — check `[CRASH]` presence to distinguish; many lines
  advancing through 640→1024 means normal progress toward title.
- The `unguarded_walk_candidates.json` sweep (143 sites/43 funcs, 3 addressed) remains the fallback
  M3-audit work unit if a future session finds M5 blocked and maintenance isn't triggered.

HYPOTHESIS-ID: m5-audio-destub-step4-setdisplaymode-hang (same slug as s303-305 — still the active
investigation thread. s303 = iteration 1 (black-box reversal, hung). s304 = iteration 2 (source-read,
refuted 2 hypotheses, surfaced the reachability question). s305 = mandated MAINTENANCE, does not count.
s306 = iteration 3 — and unlike a stalled iteration, it DID produce a discriminating result (reachability
settled, a prior conclusion overturned), so per iron rule 8 this does not trigger the "3 iterations, no
result → stop" condition; it's fresh ground, not a repeat. The work unit above (re-reverse + localize via
the newly-armed tags) is the next genuinely new probe on this thread, effectively resetting the
no-progress counter since real information keeps landing each iteration.
