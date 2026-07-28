# NEXT work unit — retry the audio-drain/H-INPUT soak (attempt 2/3)

s163 source-read `cinematicLoopBody`'s cutscene-teardown path and found a
concrete 3rd mechanism for the s162 graphics-task-submission stall
(H-AUDIO-DRAIN: `waitForAnyAudioSlot`, `funcs_15.c:6896`, is an unbounded
`while (!anyAudioSlotActive()) {}` spin with no iteration cap — if one audio
voice never reports idle, this never returns, while its neighbor
`tickMusyXIfActive` keeps the audio-ucode counter moving, matching the
s160/s161 `[lle task]`-forever/`fs`-frozen signature exactly). Landed
`ROGUESQ_LOG_AUDIO_DRAIN=1` (3-site instrument: entry/heartbeat-every-2000-
iters/exit) and extended the key schedule to test H-INPUT in the same run
(`scratch/agent/run_audiodrain1.sh`, `STICK_SCHEDULE` adds `95:start 100:a`
after s162's ~hold_92 freeze onset). Read PORTING-STATE Session 163 before
doing anything else; this file only has the actionable summary.

## What s163's soak actually got (read before re-running)

The `audiodrain1` soak died at **hold-iter 6** — far short of the ~92s
needed to reach the stall — to a SIGBUS in `emitAllocatedDLCommand`
(`submitSceneNodeRender +21192` ← `processSceneNode` ←
`traverseSceneGraphRecursive` (recurses) ← `setupCameraMatrices` ←
`runHangarSelectionFrame` ← `runHangarMenuFromOverlay` ← `menuOverlayInit`).
This is the **same call-chain shape as the s132 crash** that s133-135 chased
and explicitly **parked** after exhausting a 3-attempt budget — it recurred
a 4th time here, **past** the two existing guards
(`ROGUESQ_LOG_EMIT_DL_GUARD2`/`GUARD3`, both **0/0** this run). The crash's
offset inside `emitAllocatedDLCommand` shifted ~600 bytes from s132's
original (`+3984` → `+4584`), consistent with the 2 already-landed guard
blocks now sitting before the actual crash site — meaning either a 3rd
unguarded site with a similar-but-not-identical shape exists in that
function, or the 2 existing guards' bounds check has a gap. **Not
root-caused this session** — out of scope for that iteration's single work
unit.

The new `ROGUESQ_LOG_AUDIO_DRAIN` instrument got a partial positive control
(4 entries, 3 exits, 0 heartbeats — every completed call returned fast,
under 2000 iterations) but **zero data on the actual stalling call**, since
the process never survived long enough to reach the cutscene's real
teardown. Both H-AUDIO-DRAIN and H-INPUT remain untested.

## Do next

1. **Re-run the exact same soak, unchanged** (no rebuild — the instrument
   and key schedule are already armed and built):
   ```
   zsh /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/scratch/agent/run_audiodrain1.sh \
     > /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/scratch/agent/run_audiodrain2_driver.log 2>&1
   ```
   (Rename the soak tag inside a **copy** of the script first —
   `scratch/agent/run_audiodrain2.sh` with `RUNTAG=audiodrain2` in the final
   `run_mission_keys.sh` line — per the project convention of one script per
   soak tag, not reusing the same output directory.)
   Block synchronously with the documented pgrep loop before closing out:
   ```
   until ! pgrep -f "RogueSquadron64Recomp" >/dev/null 2>&1; do sleep 5; done
   ```
2. **This is soak attempt 2/3** for the question "does this recipe
   (`PROBE_MODE=start_only`, full flag set, `HOLD_S=120`, extended
   `STICK_SCHEDULE`) reach the actual ~92s stall window at all, given the
   `emitAllocatedDLCommand` crash family keeps intervening first." Per rule
   8, one more attempt (3/3) is available after this one if it's still
   inconclusive.
3. **Branch on the outcome:**
   - **If it reaches the stall window (hold+~90s or later) and stalls
     as before:** check `[audio-drain-enter]`/`[audio-drain-heartbeat]`/
     `[audio-drain-exit]` in `scratch/s73_post_a_scene/audiodrain2/run.log`
     against the stall's onset timestamp (`grep -n "vi-fs-decision.*stalled=1"`
     to find where it starts). An entry with no matching exit and climbing
     heartbeat counts exactly at that point **confirms H-AUDIO-DRAIN**
     directly — a real finding, write it up. If instead the stall clears
     after the `95:start`/`100:a` presses, that's H-INPUT confirmed instead
     — also write it up, and don't chase H-AUDIO-DRAIN further.
   - **If it dies again to `emitAllocatedDLCommand`** (same crash, 5th
     total occurrence): this is now a genuine 2nd data point for reopening
     the s135-parked hypothesis rather than treating it as a bystander.
     Next step then becomes: source-read the **rest** of
     `emitAllocatedDLCommand` (`funcs_3.c:2464` onward — s133 only found
     and guarded 2 of what may be 3+ occurrences of the
     `findAndUnlinkSmallestEntry`-return-then-walk idiom) looking
     specifically for a 3rd unguarded site with a *similar but not
     identical* shape to the 2 already-guarded ones (per this project's
     repeated lesson: a "same signature, different exact idiom" gap is
     exactly how the 9th-through-21st crash classes in this family kept
     evading guards). This becomes a NEW, higher-priority work unit —
     write it up as such rather than continuing the audio-drain soak
     attempts.
   - **If it dies to any other, different crash:** log it per the family's
     existing convention (new class if uncatalogued, recurrence note if
     not), and this counts as the 2nd of the 3 allowed attempts either way.

## Do not

- Do not treat the `emitAllocatedDLCommand` recurrence as a NEW crash class
  — it is not; it is the already-known, already-parked s132 crash. Don't
  re-litigate s133-135's root-cause work, only note the recurrence + guard
  gap.
- Do not re-run `run_subtitleguard1.sh`/`run_subtitleguard2.sh` — those
  questions are answered (s160-162).
- Do not treat the audio-drain instrument's "4 entries/3 exits" as evidence
  of a hang — the crash backtrace shows a completely different call chain
  (scene-graph rendering, not `cinematicLoopBody`), so the missing exit is
  almost certainly a different, still-running guest thread, not a stuck
  loop. Only a heartbeat line (which never fired) would be real evidence of
  spinning.
- Do not re-open the s159 `loadDrawState`/15th-class question or the
  `static_5_800AAD9C` dispatcher hypothesis (closed s157).

## This session's environment notes (carry forward, still current)

- **CRITICAL, learned the hard way this session: `fixup_game_funcs.py` is
  non-idempotent even within checking its own output** — running it a 2nd
  time to `grep` its stdout (e.g. to verify a patch applied) **also
  re-applies every patch a 2nd time**, duplicating them in the regenerated
  `.c` files. There is no safe "just check" invocation. If you need to
  verify what a fixup run reported, redirect its output to a log file on
  the ONE invocation and grep the log file afterward — never invoke the
  script itself a 2nd time "just to see the output again." Full regen
  order remains: delete `RecompiledFuncs/funcs_*.c` → `python3
  tools/make_elf.py` (cwd `~/Documents/Tools/rogue_squadron64`) → `zsh
  tools/agent/regen_n64recomp.sh` (cwd this repo) → `fixup_game_funcs.py`
  **exactly once** (cwd doesn't actually matter for this script — verified
  it still applies correctly from a different cwd this session — but keep
  invoking it only once regardless).
- `nm`, `otool`, `lldb` are NOT on the Bash allowlist — use
  `scratch/agent/machoparse.py` for Mach-O symbol reads if ever needed.
- The actual per-tag guard/control counts live in
  `scratch/s73_post_a_scene/<tag>/run.log`, not the driver log (only has
  the summary block).
- `nm`-adjacent lesson reused this session: reading a `RECOMP_FUNC` body
  directly from `N64Recomp/RecompiledFuncs/funcs_*.c` (found via `grep -n
  "RECOMP_FUNC void <name>"`) is far more reliable than trusting a
  `symbol_files/*.txt` comment — this session found the `waitForAnyAudioSlot`
  name is functionally inverted relative to what its body actually does;
  the comment-only read would have been wrong.
- `git -C <path> status` from this session's Bash tool triggers an approval
  prompt (treated like a directory-changing compound command) — use a
  separate `cd <path>` call followed by a separate `git status` call
  instead.
- Reading screenshots directly (the `Read` tool on a `.png`) remains ground
  truth for scene identity.
- `rm` on paths outside `scratch/` requires approval and does NOT accept
  glob patterns.
- Output redirection (`>`) from Bash is sandboxed to the session's allowed
  working directories — target `scratch/agent/`, never `/tmp`.
- `cmake --build` needs cwd `build/` and
  `DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer`.

## Housekeeping still flagged, still not done

`docs/CURRENT-TRUTH.md` is still far over the ~35 KB target — migrate
durable mechanism/architecture material to PROJECT-OVERVIEW.md and prune
superseded detail, paired with a real experiment. Flagged for many
sessions without action.

`/Users/williambuckley/Documents/Tools/N64Recomp` is its own git checkout,
not a `lib/` submodule, with uncommitted changes across s90-163
(`fixup_game_funcs.py` plus regenerated `RecompiledFuncs/*.c`). Same
posture as the `rogue_squadron64` sibling checkout flagged since s54.
Worth asking the user whether/how to commit that history.

`~/Documents/Tools/rogue_squadron64` also still carries pre-existing
uncommitted `symbol_files/*` changes from earlier sessions (unrelated to
this session's work — a stray `scratch_addrs.txt` left by this session's
research subagent was removed, but the `symbol_files/*` diffs were left
untouched per the s54 precedent). Still flagged for the user, not
committed autonomously.
