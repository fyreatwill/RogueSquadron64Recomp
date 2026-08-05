# NEXT work unit — root-cause the `reapplyDisplayMode` VI=640 graphics-task stall

## Status note (s329): new failure mode found, symptom characterized, cause NOT yet traced

s329 tested the 3rd/last M5 gate site (`reapplyDisplayMode`, `0x8008EC88`) with `setDisplayMode`
still force-zeroed (the mirror image of every s303-328 test). Result: **not** a rerun of
`setDisplayMode`'s VI=320 spin-wait deadlock. Instead, VI reaches 640 at 2.3s (baseline timing) and
then the graphics-task pipeline stalls **permanently** for the entire 600s soak —
`[vi-fs-decision] stalled=1 pairs=0` continuously from right after the 640 transition to the log's
end, never another `[phase]` VI change, never title (1024). Audio stays fully alive the whole time
(`[synth-entry]`/`[audtask-dispatch]` both fire end-to-end, `[dma-ring-caller]` backtraces show live
`musyxSynthFrame` DMA calls to the last log lines) — ruling out a repeat of the classic mechanism.
Full detail: `docs/CURRENT-TRUTH.md` item -187, `PORTING-STATE.md` Session 329. Gate reverted to
full force-zero baseline before s329 ended, per convention.

**This is genuinely new information, not yet root-caused.** Do not assume the s327 spin-pump fix
(built for `setDisplayMode`'s mechanism) applies here without evidence — the symptom is different in
kind (a graphics-task stall with audio unaffected, vs. a process-wide spin-wait freeze).

## Hypotheses (pick the discriminating probe)

1. **`reapplyDisplayMode`'s per-frame call volume corrupts or exhausts a resource the graphics-task
   producer depends on** — e.g. the shared `dmem[]` serialization (`rs64_dmem_lock/unlock`,
   `lib/N64ModernRuntime/librecomp/src/rsp.cpp`, s5) that gfx and audio RSP tasks both go through;
   a real per-frame audio write path un-gated for the first time could contend for this lock
   differently than a one-shot boot call ever did.
2. **`reapplyDisplayMode` itself does something on repeated (2nd+) calls that `setDisplayMode` never
   does on its single call** — s326 found the two functions structurally near-identical (same
   sequence of `initAudioSubsystem`/`resetSongSubsystemCounter`/etc. calls, same gate-byte
   bookend), but `reapplyDisplayMode` is called every frame (s304) — its 2nd+ invocations may
   re-run an init sequence that isn't idempotent, corrupting state the graphics side reads.
3. **Coincidence of timing, not causation from the gate reversal at all** — the s176-183
   already-documented, unresolved "graphics-task-submission stall" (`[vi-fs-decision] stalled=1
   pairs=0`, same diagnostic shape) could share a root cause unrelated to audio gating, and s329's
   soak just happened to trigger it earlier than usual. Weakened by: that documented stall's onset
   is ~90-115s post-menu-navigation in every prior sighting, vs. 2.3s here — a large, unexplained
   timing gap this hypothesis would need to account for.

**Discriminating measurement**: source-read `reapplyDisplayMode`'s full body first (cheap, no
build/soak) — same technique s326 used to fully explain `setDisplayMode`'s hang from text alone.
Compare its call sequence and any *2nd-call-specific* branches against `setDisplayMode`'s (which s326
already fully documented at `funcs_23.c:9586-9804`). Also check: is `reapplyDisplayMode`'s caller
inside or near the graphics-task producer's own call chain (would explain contention directly), or
in a wholly separate thread (points toward hypothesis 1's shared-lock theory instead)?

## The work unit

1. Read `reapplyDisplayMode`'s full body in `RecompiledFuncs/funcs_23.c:9805-10023` (already located
   by s326's trace — no regen needed, current baseline build already has this un-annotated text).
   Note every call it makes, in order, and diff against `setDisplayMode`'s body (`9586-9804`,
   s326's summary: `initAudioSubsystem`, `resetSongSubsystemCounter`, `initSongSequencerPools`,
   `resetMusyXEngineState`, `clearStreamedVoiceFlags`, `reset3DAudioLists`, gate byte set to 1 at
   the end).
2. Find `reapplyDisplayMode`'s caller(s) via grep for its address (`0x8008EBxx`-ish range boundary —
   confirm exact entry address first) across `funcs_*.c`, and check whether that caller is inside
   the same per-VI-frame tick path as `runVideoFrameTick` (s326 found `runVideoFrameTick` is
   `musyxNoopStub`'s only caller — check if it's ALSO `reapplyDisplayMode`'s caller, or a sibling
   function in the same per-frame chain).
3. Check the shared `dmem[]`/RSP-task-lock mechanism (`lib/N64ModernRuntime/librecomp/src/rsp.cpp`,
   `rs64_dmem_lock`/`rs64_dmem_unlock`, s5) for anything `reapplyDisplayMode`'s newly-live call chain
   could hold across a yield point that the graphics-task producer also needs — this is the
   concrete mechanism hypothesis 1 predicts; confirm or refute by inspection before any new soak.
4. If source-reading identifies a concrete mechanism: propose the fix (likely in
   `N64Recomp/fixup_game_funcs.py`, following the s327 spin-pump-fix pattern of patching the
   problematic call/wait site rather than reverting the gate), then soak once to confirm, following
   the established "1 soak first, 2 confirmatory if informative" cadence.
5. If source-reading is inconclusive: the next informative probe is a NEW diagnostic at the
   graphics-task producer's own skip-decision site (why does it start returning `pairs=0` at exactly
   the VI=640 transition) — this is more informative than another soak of the same recipe, since the
   symptom is already reproducible 1/1 and well-characterized; another soak without new
   instrumentation would not discriminate between the 3 hypotheses above.
6. Whatever code changes result, revert the audio-gate regex back to the full `(?:B40|C88)`
   alternation (force-zero baseline) before ending the session, confirm `audio gate patched x2`,
   rebuild — same convention as every prior session on this gate, UNLESS a fix is found and
   confirmed clean (in which case document that explicitly and treat promotion as its own decision
   point, same as `setDisplayMode`'s open promotion question).

## Environment notes (carried forward — see s327/s328/s329 for full detail)

- Regen paths: `/Users/williambuckley/Documents/Tools/N64Recomp` (`fixup_game_funcs.py`, untracked).
  Order: `make_elf.py` -> `N64Recomp` -> `fixup_game_funcs.py` -> `cmake`. `RecompiledFuncs/*.c` MUST
  be deleted before every `N64Recomp` run (it skips existing files):
  `python3 -c "import glob, os; [os.remove(f) for f in
  glob.glob('/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/*.c')]"`.
- Soak driver: `scratch/s73_post_a_scene/run_s327waitpump.sh <label>`, invoked from
  `scratch/s73_post_a_scene`, launched via Bash `run_in_background: true` then `TaskOutput` blocking
  up to 600000ms. Log lands at `scratch/s73_post_a_scene/<label>/run.log` (large — grep for
  `\[CRASH\]`, `\[phase\]`, `\[synth-entry\]`, `\[vi-fs-decision\]`, do not read directly).
- `DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build build -j8` — allowlisted
  verbatim.
- `docs/CURRENT-TRUTH.md` is at 58,714 bytes — very close to the 60,000-byte Step-0 maintenance
  trigger. The NEXT iteration after this one will very likely open as a MAINTENANCE iteration; don't
  be surprised if Step 0 fires before this work unit even starts.

HYPOTHESIS-ID: m5-audio-destub-step4-reapplydisplaymode-reversal (2nd iteration — 1st iteration
[s329] was the discriminating soak that found the new failure mode; this iteration is the
root-cause trace).
