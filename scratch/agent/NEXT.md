# NEXT work unit — why do the 3 tick-producer functions stop 3 calls before everything else?

## Context — s315 refuted the "M_AUDTASK diverges at call 20" question; simplified, not answered

s315 executed s313's remaining open question (why does RSP `M_AUDTASK` submission stop 17 calls
before its own upstream callers) and found the premise was false: `[audtask-dispatch]`
(`src/main/main.cpp`'s `get_rsp_microcode()`, the RSP-scheduler dispatch point — NOT a
`fixup_game_funcs.py` patch) had the exact same unwidened `n<20||n%256==0` flat print-cap bug s312/
s313 had just fixed in 4 *other* M5 audio diagnostics, just in a file nobody thought to re-check
because it's native runtime code, not recompiled game code. Widening it and re-running the standard
soak (`setDisplayMode`'s site reversed) found `[audtask-dispatch]` actually fires **40/40**, matching
`update3DAudioFrame` and the RSP task-runner's own last dispatch (task #39) — not diverging from
anything.

**Current state, 2 stop points, not 3:**

| tag | true call count |
|---|---|
| `update3DAudioFrame` (`[reach-update3d-*]`) | **40/40** |
| RSP `M_AUDTASK` submission (`[audtask-dispatch]`) | **40/40** (was wrongly measured as 20/20 through s313) |
| RSP task-runner (`[runner] task #N`) | last dispatch **task #39** (same boundary as the above) |
| `tickAllActiveSongs`/`tickAudioSequencerFrame`/`tickAllAudioChannels` (`[reach-allsongs-*]`/`[tick-audio-seq]`/`[tick-all-audio-channels]`) | **37/37** — stops 3 calls before everything else |

Full detail: `docs/CURRENT-TRUTH.md` Next-steps item -174, `PORTING-STATE` Session 315.

## The work unit

**Find why the 3 tick-producer functions (`tickAllActiveSongs`/`tickAudioSequencerFrame`/
`tickAllAudioChannels`) stop 3 calls before `update3DAudioFrame`/`M_AUDTASK` submission/the RSP
task-runner (37 vs 40).** This is now the single remaining divergence in this investigation — every
other pairing has resolved to "same boundary, was a print-cap illusion." Before assuming this one is
real (it might not be — it's the one gap that has NOT yet been directly cross-checked against a
positive control), consider it might ALSO be measurement, not mechanism:

1. **First, sanity-check the instrument, cheaply, before designing new diagnostics** (the s312/s313/
   s315 pattern: check the boring explanation before the exotic one). The `reach-allsongs`/
   `reach-audioseq`/`tick-audio-seq`/`tick-all-audio-channels` tags were already widened to
   `n<40||(n%128)==0` in s313 and s315's soak reused them unchanged at 37/37 — so THIS specific gap is
   NOT the flat-cap bug (37 < 40 either way, the widened cap would show it). This gap looks real. But
   double check: are `tickAllActiveSongs`/`tickAudioSequencerFrame`/`tickAllAudioChannels` actually 3
   separate call sites, or could 2 of the 3 tags be counting the SAME underlying call from different
   points (entry vs exit of one function, not 2-3 distinct functions)? A quick `grep -n
   "reach-allsongs\|reach-audioseq\|tick-audio-seq\|tick-all-audio-channels"` against
   `fixup_game_funcs.py`'s patch definitions (search for `_reach_entry_patch(` call sites and the
   `_tick_audio_seq_patch`/`_tick_all_audio_channels_patch` definitions, ~line 1999-2046 and
   ~7981-8040) will show exactly which function each tag instruments — confirm they're 3 genuinely
   distinct functions before treating "37 vs 40" as one phenomenon rather than several.
2. If the gap holds up: source-read whichever of the 3 functions is the outermost/latest-called in the
   frame's call order (their entry/exit ordering relative to `update3DAudioFrame` and `M_AUDTASK`
   submission should be visible in `run.log` by interleaving order, not just per-tag counts — grep the
   existing s315 log `scratch/s73_post_a_scene/step315audtaskcap/run.log` for lines around the 30-40
   window across ALL tags together, sorted by file position, before running anything new). Look for a
   condition, early-return, or loop bound that could fire on iteration 37 specifically (a modulo-N
   frame-skip is the next cheapest hypothesis after "single condition" per the established M5-audio
   pattern — `musyxSynthFrame`'s own countdown/period gate, already ruled out for that function in
   s311/s312, is worth checking whether any of these 3 functions have their own independent copy of a
   similar countdown).
3. If a candidate site is found, add ONE new diagnostic there using the established `n<40||(n%128)==0`
   convention from the start (never repeat the flat-cap mistake — s315 is now the 3rd time this exact
   bug class has been caught in this investigation), batch it into the same regen/soak cycle as
   anything else this session wants measured.
4. Regen: if the new diagnostic touches `RecompiledFuncs/*.c` content (a `fixup_game_funcs.py` patch),
   full order applies: `fixup_game_funcs.py` edit → clear `RecompiledFuncs/*.c` → `N64Recomp/build/
   N64Recomp rogue_squadron.toml` → `python3 fixup_game_funcs.py` → `cmake --build build -j8`. If it's
   native runtime code (like s315's fix, in `src/main/main.cpp` or similar), just `cmake --build build
   -j8` — no N64Recomp regen needed.
5. Reverse `setDisplayMode`'s gate site (`RecompiledFuncs/funcs_23.c`, direct hand-edit — change
   `MEM_B(0XF50, ctx->r1) = 0;` to `= ctx->r2;` near the `// 0x8008EB40` comment) a 9th time to exercise
   gate=1, one full soak (copy `scratch/s73_post_a_scene/run_step315audtaskcap.sh`, it's the current
   template — all passive breadcrumbs armed, `HOLD_S=240`, `ROGUESQ_AUDIO_UCODE=1`), read the result,
   **revert the site again same session** (mandatory — deterministic boot hang if shipped reversed).

**Discriminating outcome**: if the 3 tick-producer tags turn out to be 2 distinct functions or fewer
(step 1 finds a labeling artifact), the "37 vs 40" gap may collapse entirely and this investigation
could be DONE — every measured divergence in the whole s297-315 lineage would then trace to either a
print-cap artifact or dead code, meaning the M5 audio subsystem's tick/dispatch machinery is fully
healthy up to the shared hard-stop boundary at call/task ~39-40, and the real next question becomes
"what causes the hard stop itself" (a new, more consequential thread) rather than continuing to chase
soft-stop divergences. If the 3 functions ARE genuinely distinct and the 37-vs-40 gap is real, a
located condition/gate is the direct next fix candidate.

## Environment notes (carried forward, all still valid)

- Regen paths for game-code patches are in `/Users/williambuckley/Documents/Tools/N64Recomp`
  (`fixup_game_funcs.py`, `RecompiledFuncs/*.c`, `build/N64Recomp`, `rogue_squadron.toml`), NOT this
  repo. Native runtime diagnostics (like s315's `[audtask-dispatch]` fix) live in this repo's
  `src/main/main.cpp` and only need `cmake --build build -j8` from this repo's root — no N64Recomp
  regen, no `fixup_game_funcs.py`. Check which kind of change you're making before picking a rebuild
  path; s315 wasted no cycles here but a future session might if it assumes every M5-audio diagnostic
  lives in `fixup_game_funcs.py`.
- `cd` into `N64Recomp` FIRST as its own bare `cd` command, THEN run `./build/N64Recomp
  rogue_squadron.toml` with output redirection in a SEPARATE Bash call — combining `cd` and a redirect
  in one compound command triggers a permission prompt in this sandbox. Same for any cd+redirect combo
  (soak launch, etc.) — do the `cd` alone first.
- `python3 -c "import glob, os; [os.remove(f) for f in glob.glob('/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/*.c')]"`
  clears RecompiledFuncs (use the ABSOLUTE path).
- `DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build build -j8` from this repo's
  root — allowlisted verbatim, works as a single command.
- Soak driver template: `scratch/s73_post_a_scene/run_step315audtaskcap.sh` (now the newest; copy it,
  don't hand-roll). The *actual* game stderr/stdout log lands in a subdirectory named after the run
  (`scratch/s73_post_a_scene/<name>/run.log`), NOT the top-level driver log of the same name in the
  parent dir (that one is just the phase-gate driver's own short status log — s315 briefly checked the
  wrong file and saw 4 lines with 0 hits before finding the real 745 KB log one directory down).
- Launch the soak via Bash with `run_in_background: true` (cd into `scratch/s73_post_a_scene` first as
  its own bare command), then `TaskOutput` with `block: true` and `timeout` up to 600000ms — do NOT
  foreground-poll. `run_mission_keys.sh`'s own 600s phase-timeout exits nonzero (exit 5, INCONCLUSIVE)
  on the expected deterministic hang — that's success for this soak design, not a tooling failure; the
  game process is killed automatically. Confirm `pgrep -f "build/RogueSquadron64Recomp"` is empty
  before AND after.
- `/tmp` is blocked for redirects — use a path inside this repo, `N64Recomp`, or `rogue_squadron64`
  instead.
- `scratch/s73_post_a_scene/step315audtaskcap/run.log` (745 KB) is s315's saved log if a future session
  wants to re-verify the 40/37/40 call-count split (updated from s313's 40/37/20) before building
  anything new.

HYPOTHESIS-ID: m5-audio-destub-step4-setdisplaymode-hang (same slug, s303-315 — still the active
investigation thread. s306/s307/s309/s310/s311/s312/s313/s315 have each produced a discriminating
result in sequence — resetting the iron-rule-8 no-progress counter every time; this is real, converging
progress, not a stall. s314 (maintenance) doesn't count against the slug's session count. Continue the
same slug next non-maintenance session, or close it out if step 1 above collapses the remaining gap.)
