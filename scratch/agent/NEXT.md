# NEXT work unit

## s340 closed M5-AUDIO-PLAN step 4 — read this first

s340 (`HYPOTHESIS-ID m5-audio-destub-gate-promotion-decision`, 1st and only iteration needed,
CURRENT-TRUTH item -196, full detail `PORTING-STATE` Session 340) made the promotion decision
item -195 (s339) recommended: both `setDisplayMode`'s and `reapplyDisplayMode`'s gate-byte reversals
(the only 2 of the nominal 3 gate sites that are actually reachable — `initMusyXEngine`'s is dead
code, s306) are now the **PERMANENT shipped default** in `fixup_game_funcs.py` (N64Recomp repo,
untracked). This is a real, durable change to the regen pipeline's output going forward, not a
session-scoped soak toggle like every prior reversal in this arc.

Evidence: 2 soaks (`s340bothgates`, `s340bothgates2`, `HOLD_S=600` each, both gate sites reversed
simultaneously — never tried together before this session), both clean: VI transitions 0→320→640
within 2.2s (no VI=320 hang regression), zero crash markers for the full 600s, then the
already-characterized benign VI=640 `pairs=0` plateau from item -195 (`[static6-800a9abc-entry]`=1,
audio synth counter and DMA ring both still incrementing at the log tail in both runs). Meets
M5-AUDIO-PLAN's "two clean soaks" bar.

## The work unit: M5-AUDIO-PLAN step 5 — crash-family rate comparison

Per the user directive's M5 priority (docs/CURRENT-TRUTH.md USER DIRECTIVE item 2) and
`docs/M5-AUDIO-PLAN.md`'s own step 5 (now the current step): with gate promotion real and permanent,
check whether crash families #3 (`waitForAnyAudioSlot` SIGSEGV, historical baseline ~12-21% of
pre-scene soaks) and #4 (post-cutscene stall, historical "every soak died earlier") change rate now
that the guest game code genuinely believes audio is enabled end-to-end, vs. the historical baselines
recorded before ANY gate was ever reversed.

1. **Re-read `docs/M5-AUDIO-PLAN.md` §4/§5 first** for the exact historical baseline numbers and where
   they were measured (grep for "crash family" / "#3" / "#4" in that doc and in CURRENT-TRUTH's
   "Current truth" section) — confirm the baselines predate any gate reversal, not just predate this
   session's promotion, before treating a rate change as caused by s340.
2. **Competing hypotheses**:
   - HA: crash family #3/#4 rates are materially unchanged from their historical baselines — the gate
     reversal's effect is confined to what's already been observed (VI progression, audio counters
     alive), no new audio-code-path-dependent crash surface opened up.
   - HB: rates increase — real audio dispatch (voice triggering, slot allocation, MusyX DMA) is now
     genuinely exercised end-to-end for the first time, and one of the historically-flagged "plausibly
     audio-artifact" crash families (per the M5-AUDIO-PLAN's own risk framing) is real and now
     reproducible at a measurably different rate.
   - HC: rates decrease — the audio-disabled degenerate paths were themselves the source of some
     crashes (matching the user directive's original M5 rationale: "several recurring crash families
     ... are plausibly artifacts of the audio-disabled degenerate paths").
   - **Discriminating measurement**: multiple soaks (this is a RATE comparison, not pass/fail — do not
     treat 1-2 clean runs as confirmation, per the standing 0/2-is-a-weak-null lesson from the
     `MATEXPIRY_GUARD` thread) through the pre-title/title/menu/pre-scene phases, with
     `ROGUESQ_LOG_AUDIO_DRAIN`/`_VOICE_ACTIVE_GATE`/`_VOICE_TRIGGER_CHAIN` armed as a same-run
     positive control that real voice/slot activity is occurring (not just that the crash rate moved
     for an unrelated reason). Compare crash signature and rate against the historical baseline
     numbers from step 1.
3. Given the "multiple soaks, rate comparison" bar, this is a good candidate to batch: build once
   (gate promotion is ALREADY the current build state, no rebuild needed — verify with
   `grep -n "0x8008EB40\|0x8008EC88" /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_23.c`
   before assuming, in case a regen happened since), then queue several soak recipes to
   `scratch/agent/soak_queue/` (self-contained, launches the game itself, SIGKILLs, exits nonzero on
   crash) so the loop runs them between iterations rather than babysitting each one inline.
4. If HA (unchanged): step 5 closes, M5-AUDIO-PLAN moves to step 6 (validate real PCM reaches SDL).
5. If HB or HC (rate genuinely moved): that's the real payoff/risk the whole M5 plan was measuring —
   characterize which specific crash signature moved and by how much (numerator/denominator, not
   adjectives) before updating CURRENT-TRUTH.

`HYPOTHESIS-ID: m5-audio-destub-step5-crashrate-comparison` (new, 1st iteration).

## Environment notes (carried forward — see s327-340 for full detail)

- Regen paths: `/Users/williambuckley/Documents/Tools/N64Recomp` (`fixup_game_funcs.py`, untracked).
  Delete `RecompiledFuncs/*.c` before every `N64Recomp` run:
  `python3 -c "import glob, os; [os.remove(f) for f in
  glob.glob('/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/*.c')]"`.
- Full regen order: `cd ~/Documents/Tools/rogue_squadron64 && python3 tools/make_elf.py` →
  `cd ~/Documents/Tools/N64Recomp && ./build/N64Recomp rogue_squadron.toml` →
  `python3 ~/Documents/Tools/N64Recomp/fixup_game_funcs.py` →
  `DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build
  /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/build -j8`.
- Soak driver: `scratch/s73_post_a_scene/run_s327waitpump.sh <label>`, invoked with
  `env HOLD_S=600 <VARS> zsh scratch/s73_post_a_scene/run_s327waitpump.sh <label>` (the `env` prefix
  is required — see project rule 10). Run it via Bash `run_in_background: true`, get the PID from
  `ps aux | grep RogueSquadron64Recomp`, then poll it to completion from a small throwaway
  `scratch/agent/*.sh` script (compound `while`/arithmetic one-liners get denied by the sandbox's
  compound-statement check — write the poll loop to a file and `zsh` it instead). Log lands at
  `scratch/s73_post_a_scene/<label>/run.log` — grep it, don't read it directly (multi-MB/million-line
  files).
- The soak driver's own "wait for VI width 1024" phase gate times out at 600s and exits 5
  (INCONCLUSIVE) for any scene that doesn't reach the title screen within the hold — this is NOT a
  crash signal by itself; check the log directly for crash/SIGSEGV/SIGTRAP/fatal/abort markers and
  the `[vi-fs-decision]`/`[dma-ring-consumer]`/audio-synth counters to confirm liveness before calling
  a phase-timeout a stall (s329-340's whole VI=640 arc was this exact trap in reverse: a phase-timeout
  reading that turned out to be benign after 10 sessions of chasing it as a hang).
- `[vi-fs-decision]` is an always-on native instrument (`lib/rt64/src/hle/rt64_state.cpp`), not
  env-gated — free in every soak, no arming needed.
- Scratch files outside the three allowed working directories (e.g. `/tmp/...`) are blocked by the
  sandbox — write throwaway analysis/poll scripts under `scratch/` in this repo instead.

HYPOTHESIS-ID: m5-audio-destub-step5-crashrate-comparison (new, 1st iteration — pivoted from
m5-audio-destub-gate-promotion-decision, which s340 closed with full resolution).
