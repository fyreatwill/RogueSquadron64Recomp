# NEXT work unit — execute step 1 of the M5 audio de-stubbing plan (free source-read, no code/soak)

## What s298 did (context, not a re-derivation prompt)

Pivoted off the `tickTextureMaterialExpiry-guard` thread (loop's mandatory-pivot rule fired after 3
straight iterations; no `BREADCRUMB12` recurrence arrived this session to react to). Wrote
`docs/M5-AUDIO-PLAN.md` — the priority-2 design doc the USER DIRECTIVE (`docs/CURRENT-TRUTH.md` top)
calls for. Read that doc's §1-§4 before starting this work unit; summary:

- The audio stub is ONE function-pointer swap: `musyx_stub()` registered as the `M_AUDTASK` handler
  in `src/main/main.cpp`'s `get_rsp_microcode()` (line ~594-595), returning `RspExitReason::Broke`
  with zero ucode execution. `factor5_ucode_b` (recompiled MusyX ucode) is compiled/linked but
  never dispatched.
- The `dmem[]`-sharing concern is already solved by the s5 `g_lle_task_mutex` — no new
  synchronization design needed.
- The host SDL audio bridge (`ultramodern::audio_callbacks_t`, `SDL_QueueAudio` wiring, guest-facing
  `osAi*` functions) is already fully functional — needs no work.
- Crash-family payoff is weaker than the goal-stack's original framing: only 1 of 4 documented
  audio-adjacent crash families is confirmed stub-caused, and reversing that one's fix (the gate-byte
  force-zero) directly re-exposes a previously-fatal boot-time scheduler wedge unless the ucode now
  genuinely completes tasks.

## This session's work unit: M5-AUDIO-PLAN.md §4 step 1

**Question to answer** (source-read only — no code change, no build, no soak, no game run):

Does the guest game ever call `osSpTaskStartGo` for a real `M_AUDTASK` while the audio-engine-enable
gate byte (`0x800A0F50`) reads 0 (its current forced-disabled state), or does the gate short-circuit
audio task creation before it ever reaches the RSP task queue?

**Why this is the right next step**: it determines whether M5-AUDIO-PLAN.md's step 2 (swapping
`musyx_stub` → `&factor5_ucode_b` in the dispatch switch, gate still forced off) is a **provable
no-op** — a safe, low-risk first structural change — or **already changes behavior** the moment it
lands, in which case step 2 needs its own soak scrutiny from the start rather than being treated as
inert plumbing.

**How to do it**: trace forward from the 3 gate-byte read/write sites already catalogued
(`initMusyXEngine`, `setDisplayMode`, `reapplyDisplayMode` — the same 3 sites
`fixup_game_funcs.py:94-101` force-zeros) through `tickMusyXIfActive`/`musyxSynthFrame` (the
per-VI-retrace audio tick, caller confirmed s101 to be `viRetraceHandlerThread`) to find where task
submission either proceeds unconditionally or is gated on the enable byte. Source is
`N64Recomp/RecompiledFuncs/funcs_*.c` (grep the function names above to find which numbered file each
lives in — do NOT grep the whole tree blind, the survey agents already have file:line references in
`docs/M5-AUDIO-PLAN.md` §1 to start from) and cross-reference against `PORTING-STATE.md`'s existing
s101/s173 notes (s173 already flagged an unresolved observation that the enable flag appeared nonzero
mid-run despite the force-zero patch — this session's read should either explain or flag that
contradiction, not ignore it).

**Discriminating outcomes**:
1. **Task submission is itself gated** (e.g. `tickMusyXIfActive` returns early / never calls
   `osSpTaskStartGo` when the byte is 0): step 2 is provably inert. Proceed straight to landing it as
   a trivial structural change, validate with 1 soak confirming zero behavior change (phase timeline,
   crash rate identical), then move to step 3 (`waitForAnyAudioSlot` timeout guard) same session if
   budget allows.
2. **Tasks ARE submitted regardless of the gate** (the gate only affects downstream guest-side logic,
   not RSP task creation): step 2 is a real first test of `factor5_ucode_b` executing at all. Plan the
   step-2 soak with that expectation — watch for a hang or crash appearing for the first time right
   after the swap, before the title screen, as the discriminator between "ucode itself is broken" vs.
   "gate-byte reversal (step 4) is what's risky."
3. **s173's contradiction resolves** (e.g. a different byte/offset was actually being read, or the
   gate only affects a subset of the 3 call sites): note the correction in `docs/M5-AUDIO-PLAN.md` §1
   and `PORTING-STATE.md` — this would change which of the 3 gate sites in step 4 needs which fix.

Write the finding into `docs/M5-AUDIO-PLAN.md` §1's "one open question" callout (replace it with the
answer) and into this session's `PORTING-STATE.md` entry. If time/budget remains after this free
step, proceed directly into step 2 per the plan — do not treat "wrote one source-read finding" alone
as enough for `ADVANCED` if the session has budget left; step 2 is cheap (one line in
`src/main/main.cpp`) and continuing the same thread in one session is preferable to a 1-line iteration.

## Environment notes (carried forward, all still valid — see s297's NEXT.md history for the full list)

- Regen commands unchanged: `make_elf.py` not needed (ELF/ROM mapping unchanged since s284).
  `N64Recomp` needs cwd `N64Recomp`, `fixup_game_funcs.py` needs cwd `N64Recomp`. Delete
  `funcs_*.c` before regen.
- `src/main/main.cpp` lives in THIS repo (`RogueSquadron64Recomp`), not `N64Recomp` or `lib/` — a
  step-2 edit there needs a normal cmake rebuild (`DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer
  cmake --build build -j8` from repo root, or whatever the established build invocation is — verify
  the exact cmake invocation before assuming; this file has not been touched by recent sessions so
  the build command isn't freshly confirmed in this doc).
- Soak driver: `scratch/s73_post_a_scene/run_dequeuearg1.sh` (`HOLD_S` env-overridable). See s297's
  carried-forward notes (prior NEXT.md, now superseded but visible in git history) for the full
  soak-log-size / Bash-tool-timeout / background-polling guidance if a soak is run this session.
- `BREADCRUMB12`/`MATEXPIRY_GUARD` thread is DORMANT, not closed — still armed passively in every
  soak via the shared driver. If a 3rd `BREADCRUMB12` recurrence or a `[matexpiry-guard]` fire shows
  up in `scratch/agent/SOAK-RESULTS.md` at a future session start, fold it into the ledger per the
  decision tree in `PORTING-STATE.md` Session 297 — but do not make it this session's primary work
  unit unless it does.
- The `unguarded_walk_candidates.json` sweep (143 sites/43 funcs, 3 addressed) remains the fallback
  M3-audit work unit if a future session finds M5 blocked and maintenance isn't triggered — but M5 is
  priority 2 and this doc's step 1-2 are cheap; don't skip to the fallback prematurely.

HYPOTHESIS-ID: m5-audio-destub-step1
