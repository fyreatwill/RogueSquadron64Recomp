# NEXT work unit — M5 step 4, 3rd gate site: reverse `reapplyDisplayMode` (0x8008EC88)

## Status note (s328): `setDisplayMode`'s site is CLOSED at 3/3 clean VI=320 soaks — this unit moves to the plan's next site

s328 ran the 2 confirmatory soaks NEXT.md asked for. Both cleared the VI=320 hang (VI reached 1024 at
baseline timing ~45.5s, full menu chain into SELECT YOUR CRAFT) — 3/3 combined with s327. One soak
(s328a) died hold-iter 5 to the already-catalogued, unrelated near-`0x80000000` pointer family in
`buildPositionAndCallTransformHelper` (`BREADCRUMB6`, first landed Session 273); the other (s328b)
survived the ENTIRE 240s hold with zero crashes — the cleanest run of this whole investigation.
`m5-audio-destub-step5-confirm-waitpump-fix` is CLOSED. Full detail: `docs/CURRENT-TRUTH.md` item
-186, `PORTING-STATE.md` Session 328. `setDisplayMode`'s site (`0x8008EB40`) was reverted back to
force-zero before s328 ended, matching every prior session's convention.

**Open, explicitly-flagged decision NOT made yet**: whether to promote `setDisplayMode`'s gate
reversal to the shipped default now that its hang is closed. This is a human call (tradeoffs
written up in CURRENT-TRUTH item -186) — do NOT decide this unilaterally this iteration. It does
NOT block the work below, which is orthogonal: testing the 3rd and last gate site per
`docs/M5-AUDIO-PLAN.md` §4 step 4's own designed sequence ("reverse `setDisplayMode`'s site next...
then `reapplyDisplayMode` last").

## Hypotheses (pick the discriminating soak)

1. **`reapplyDisplayMode`'s gate reversal is safe the same way `setDisplayMode`'s was** — same
   VI=320-class hang mechanism (spin-wait on `waitForMusyXAudioTaskDone`/`shutdownAudioEngine`), same
   fix already in the tree (inert until this gate flips), should clear cleanly the same way.
2. **`reapplyDisplayMode` is different** — s304 found it's a HOT PER-FRAME path (called every frame,
   unlike `setDisplayMode` which is a one-shot mode-change call) — reversing it could re-expose the
   same wedge mechanism far more frequently, or a distinct one (per-frame call volume stresses the
   spin-pump fix's 64-pump bound differently than a one-shot call would).
3. **Both gates need to be reversed together** for correct audio behavior (e.g., some downstream
   consumer expects both real-write paths active) — reversing `reapplyDisplayMode` alone with
   `setDisplayMode` still force-zeroed could produce a NEW, third failure mode neither prior
   investigation thread has seen.

**Discriminating measurement**: same `HOLD_S=240` soak recipe as s327/s328, gate narrowed to
`0x8008EB40`-only this time (the mirror-image edit — exempt B40/setDisplayMode from the force-zero
match, leave C88/reapplyDisplayMode force-zeroed). Does VI still reach 1024 at baseline timing
(~45.5s)? Does the process progress through the menu chain? What (if anything) does it eventually
crash to, and does that crash correlate with an audio diagnostic at the crash site (discriminates
hypothesis 2/3 from a clean pass matching hypothesis 1)?

## The work unit

1. In `N64Recomp/fixup_game_funcs.py` (search for `0x8008E(?:B40|C88)` to find the line, ~line 197),
   change the audio-gate store regex from the baseline `r"(// 0x8008E(?:B40|C88): sb ..."` (both
   sites patched) to `r"(// 0x8008EB40: sb ..."` (B40-only). This leaves `reapplyDisplayMode`'s
   `0x8008EC88` site UNPATCHED (reversed/live) while `setDisplayMode`'s `0x8008EB40` stays
   force-zeroed. **This is the mirror image of the s327/s328 edit — do not accidentally repeat the
   C88-only edit, that tests the wrong site this time.**
2. Full regen: delete `RecompiledFuncs/*.c` -> `N64Recomp` -> `fixup_game_funcs.py` -> `cmake --build`
   (`make_elf.py` unchanged since s328, safe to skip per s328's own precedent). Confirm patch report
   shows `audio gate patched x1`, then VERIFY which site by grepping regen'd `funcs_23.c` for
   `0x8008EB40`/`0x8008EC88`: C88's line should show the `= 0; // PATCH:` comment, B40's should NOT
   (plain generated code) — don't trust the count alone, confirm the site, a script mistake here
   would silently test the wrong hypothesis.
3. Run `zsh scratch/s73_post_a_scene/run_s327waitpump.sh <label>` (background, `TaskOutput` with up
   to 600000ms timeout, do NOT foreground-poll) ONCE first (single soak, not 2 — new site, same "1
   soak first, 2 confirmatory if informative" cadence s327 used for setDisplayMode). Confirm
   `pgrep -f "build/RogueSquadron64Recomp"` is empty before AND after.
4. Check: does VI reach 1024? Progress into SELECT YOUR CRAFT? What crash (if any), and does it
   correlate with an audio diagnostic at the site (same check s327/s328 used)? If `TaskOutput`'s
   block times out waiting on the driver script's own summary tail on a long clean run, use
   `grep -c "\[CRASH\] caught" <label>/run.log` directly instead of waiting further (s328b's summary
   generation lagged well behind the actual clean-run result on a 178M-line log).
5. If clean/comparable to setDisplayMode's result: this closes step 4 of the M5 plan (all 3 gate
   sites individually validated as reversible without reintroducing the historical hang). Write that
   up as a new hypothesis-close; flag (don't decide) whether to promote reapplyDisplayMode's gate too.
   If it hangs or crashes differently: genuinely new information — reapplyDisplayMode's per-frame
   call volume may need its own fix, distinct from the spin-pump patch already in the tree. Do not
   assume the existing fix covers it without evidence.
6. Revert to full force-zero baseline (`0x8008E(?:B40|C88)` alternation) before ending, same
   convention as every prior session on this thread, regardless of outcome.

## Environment notes (carried forward, still valid — see s327/s328 for full detail)

- Regen paths: `/Users/williambuckley/Documents/Tools/N64Recomp` (`fixup_game_funcs.py`, untracked).
  Order: `make_elf.py` -> `N64Recomp` -> `fixup_game_funcs.py` -> `cmake`. `RecompiledFuncs/*.c` MUST
  be deleted before every `N64Recomp` run (it skips existing files):
  `python3 -c "import glob, os; [os.remove(f) for f in
  glob.glob('/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/*.c')]"`.
- Soak driver: `scratch/s73_post_a_scene/run_s327waitpump.sh <label>`, invoked from
  `scratch/s73_post_a_scene`, launched via Bash `run_in_background: true` then `TaskOutput` blocking
  up to 600000ms. Log lands at `scratch/s73_post_a_scene/<label>/run.log` (large — grep for
  `\[CRASH\]`, `\[phase\]`, `\[synth-entry\]`, `audio-wait-pump`, do not read directly).
- `DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build build -j8` — allowlisted
  verbatim.

HYPOTHESIS-ID: m5-audio-destub-step4-reapplydisplaymode-reversal (1st iteration — fresh thread, prior
hypothesis `m5-audio-destub-step5-confirm-waitpump-fix` closed s328).
