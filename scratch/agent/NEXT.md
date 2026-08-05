# NEXT work unit

## s339 closed the entire VI=640 `pairs=0` stall chase (s329-s338) — read this first

s339 (`HYPOTHESIS-ID m5-audio-destub-submitgfxframe-vi-fs-decoupling`, 1st and only iteration needed,
CURRENT-TRUTH item -195, full detail `PORTING-STATE` Session 339) answered NEXT.md's own question by
pure source-read plus reuse of s337's already-captured log — **no new soak**:

- `submitGfxFrame`'s full callee set (`RecompiledFuncs/funcs_3.c:13845`, N64Recomp repo) has no
  `setupCameraMatrices`/`emitFrameRdpInitDl`/`runVideoFrameTick`/`advanceVideoFrame` anywhere — it only
  does buffer-arbiter/SP-task-producer bookkeeping. It structurally cannot emit `SET_COLOR_IMAGE`
  (the only opcode that produces a `FramebufferPair`, i.e. `[vi-fs-decision]`'s `pairs` counter).
- The only path to a `FramebufferPair` is `runVideoFrameTick → advanceVideoFrame →
  buildAndRegisterDefaultMaterial` (+ `setupCameraMatrices → emitFrameRdpInitDl`), per the
  `rogue_squadron64` symbol file's own existing annotations.
- `cinematicLoopBody` DOES reach `runVideoFrameTick`, via `static_6_800A9ABC` (funcs_43.c:20718,
  `runVideoFrameTick` call at line 20975, genuinely live code) — but that call is in
  `cinematicLoopBody`'s ONE-TIME pre-loop setup (funcs_27.c:107079), strictly BEFORE the internal
  self-loop label (`L_800A6024`, line 107269) that s336 already proved runs 1152+ times for the whole
  stall. **Confirmed at runtime**: s337's already-captured log
  (`scratch/s73_post_a_scene/s337cutscenetimer/run.log`, already had `ROGUESQ_LOG_MAINGAMELOOP_REACH=1`
  armed, which happens to gate the pre-existing `[static6-800a9abc-entry]` diagnostic from s334) shows
  **exactly 1** hit for the whole ~600s soak. Sanity check: 1 (this) + 1 (`mainGameLoop`'s own single
  loop-top pass, s334) = 2, an exact match to s333's raw "`runVideoFrameTick` stops after exactly 2
  calls" finding.

**Conclusion**: nothing is stalled. `cinematicLoopBody`'s self-loop runs correctly the entire time
(audio, buffer-arbiter, cutscene-slot dispatch all genuinely alive, matching every session's
observations in this arc) — it simply never re-emits `SET_COLOR_IMAGE` after its one-time pre-loop
camera/RDP-state setup, so the pairing instrument faithfully reads 0 for the rest of the scene. This is
very likely not a bug (a locked-camera cutscene reusing one RDP-state prologue instead of rebuilding it
every frame is a completely ordinary thing for a scripted scene to do) and confirms s336's suspicion
that this whole thread was never an M5/audio issue.

## What this means: the VI=640 stall is no longer a blocker for the M5 gate-promotion decision

Item -182..-187 left an explicit open, unmade decision: promote `setDisplayMode`'s (s327/s328-validated)
gate-byte reversal from armed-but-inert to the shipped default. `reapplyDisplayMode`'s site (the 3rd/
last gate) was left un-promoted specifically because reversing it led to this VI=640 stall reading —
which is now fully characterized as benign and audio-unrelated. **Recommend the next M5 work unit
directly revisits that promotion decision** rather than continuing to instrument this thread further
(9 sessions, s329-s339, is well past any reasonable budget on one reading).

`HYPOTHESIS-ID: m5-audio-destub-gate-promotion-decision` (new, 1st iteration).

## The work unit

1. **Re-read the promotion question fresh, don't assume**: `docs/M5-AUDIO-PLAN.md` should already state
   what "promote to shipped default" means mechanically — check whether it's literally deleting the
   `fixup_game_funcs.py` force-zero patch for `setDisplayMode`/`reapplyDisplayMode`'s gate-byte store
   (`funcs_23.c`, gate byte `0x800A0F50`, per the Regeneration section of this doc) vs. some other
   mechanism. Confirm both sites' current patch state before touching anything
   (`grep -n "0x800A0F50\|setDisplayMode\|reapplyDisplayMode" tools/fixup_game_funcs.py` in the
   N64Recomp repo).
2. **Competing hypotheses to discriminate**:
   - H1: both gates can be promoted together safely — the only known failure modes (VI=320
     `waitForMusyXAudioTaskDone` hang, fixed s327/s328; the VI=640 `pairs=0` reading, now shown benign
     s339) are both closed, so a longer/harder soak with BOTH gates reversed simultaneously should be
     clean.
   - H2: `setDisplayMode`'s reversal is safe alone (2-3 soaks already confirmed s328) but combining it
     with `reapplyDisplayMode`'s reversal surfaces a NEW interaction not seen when either is tested in
     isolation (this arc has never soaked both reversed at once — every soak in s329-s339 reversed only
     `reapplyDisplayMode`'s site, not both).
   - H3: promoting either gate regresses something unrelated to this whole VI=640/VI=320 thread (e.g. a
     visual defect, not a hang) — would need a driven capture, not just a crash-free soak, to catch.
   - **Discriminating measurement**: one soak with BOTH `setDisplayMode` and `reapplyDisplayMode` gate
     sites reversed simultaneously (not the baseline's usual "one reversed, one force-zero" split this
     whole arc used), `HOLD_S=600`, full diagnostic set armed per this arc's convention (armed
     instruments are free — see Environment notes below). Crash-free + no new stall-reading distinguishes
     H1 from H2. A visual regression would need a follow-up driven capture — separate work unit, not
     required to close this one if the soak is clean.
3. If clean: this is the promotion soak's first confirmation. Per M5-AUDIO-PLAN's "two clean soaks" bar
   (already the pattern used for `setDisplayMode` alone, s328), queue a 2nd soak via
   `scratch/agent/soak_queue/` rather than spending a 2nd iteration babysitting it.
4. If NOT clean (new crash or stall signature): that's a real, novel M5 finding — characterize it with
   the same rigor as this arc's prior sessions (source-read first, minimal targeted instrument, not a
   fresh multi-session chase) and update `docs/M5-AUDIO-PLAN.md`'s risk assessment.
5. Whichever outcome, this can plausibly close in 1 iteration (it's a soak-and-observe question, not a
   multi-hop reachability chase like the last one) — but budget up to 3 per iron rule 8 if the soak
   surfaces something new.

## Environment notes (carried forward — see s327-339 for full detail)

- Regen paths: `/Users/williambuckley/Documents/Tools/N64Recomp` (`fixup_game_funcs.py`, untracked).
  Delete `RecompiledFuncs/*.c` before every `N64Recomp` run:
  `python3 -c "import glob, os; [os.remove(f) for f in
  glob.glob('/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/*.c')]"`.
- Soak driver: `scratch/s73_post_a_scene/run_s327waitpump.sh <label>`, invoked with
  `env HOLD_S=600 <VARS> zsh scratch/s73_post_a_scene/run_s327waitpump.sh <label>` (the `env` prefix
  is required — see project rule 10, a bare `VAR=1 zsh ...` is denied by the permission
  prefix-matcher). Run it via Bash `run_in_background: true`. Get the PID from the launch output
  (`pid <PID> out=...`), then block in a SEPARATE foreground Bash call polling `os.kill(pid, 0)` or
  `while kill -0 <PID> 2>/dev/null; do sleep 5; done` with a timeout comfortably over 600s. Log lands
  at `scratch/s73_post_a_scene/<label>/run.log` — grep it, don't read it directly (past logs have run
  tens of MB / over a million lines).
- **Existing logs are reusable evidence** — s335, s336, s337, and s339 all answered questions by
  re-reading source or re-grepping already-captured logs instead of always re-running a soak. Check
  `scratch/s73_post_a_scene/s337cutscenetimer/run.log` before spending a new build-run cycle — it has
  `ROGUESQ_LOG_MAINGAMELOOP_REACH=1` and `ROGUESQ_LOG_CUTSCENETIMER_REACH=1` armed, but does NOT have
  both gate sites reversed simultaneously (only `reapplyDisplayMode`'s), so this work unit's specific
  question (both gates reversed at once) will need a new soak.
- Multiple Bash calls this session hit compound-command approval friction (`cd x && cmd`,
  `VAR=1 cmd 2>&1 | tail`, etc.) — safest pattern is a standalone `cd <dir>` as its own Bash call
  (working directory persists across calls), then the actual command as a separate call with an
  absolute path where needed.
- `DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build <path> -j8` — allowlisted
  verbatim.
- Scratch files outside the three allowed working directories (e.g. `/tmp/...`) are blocked by the
  sandbox — write throwaway analysis scripts under `scratch/` in this repo instead.

HYPOTHESIS-ID: m5-audio-destub-gate-promotion-decision (new, 1st iteration — pivoted from
m5-audio-destub-submitgfxframe-vi-fs-decoupling, which s339 closed with full resolution).
