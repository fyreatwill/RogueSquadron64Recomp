# NEXT work unit — patch the audio-task-done spin loop to pump real dispatch, then soak for VI progress past 320

## Status note (s326): mechanism CLOSED via pure source-read — this is now a fix-and-validate task

s326 ran NEXT.md's suggested first step (read `setDisplayMode`'s full body) and it fully explained the
VI=320 hang, no build/soak needed. Full trace: `docs/CURRENT-TRUTH.md` item -184, `PORTING-STATE.md`
Session 326. Summary of the mechanism, so this file is self-contained:

- `setDisplayMode`/`reapplyDisplayMode` (`funcs_23.c:9586-9804`/`9805-10023`) already run their full
  real body regardless of the gate-byte patch; the patch only prevents the FINAL store that re-enables
  the gate byte (sets it back to 1) at the end of each function.
- `runVideoFrameTick` (`funcs_0.c:1459`) calls `musyxNoopStub` (`funcs_23.c:10098`) as the literal first
  action every video frame. `musyxNoopStub` reads the gate byte (RAM `0x800A0F50`); if nonzero, it calls
  `waitForMusyXAudioTaskDone` (`funcs_24.c:5425`).
- `waitForMusyXAudioTaskDone` seeds a countdown at RAM `0x8014998A` to `0x10`, then busy-spins
  (`funcs_24.c:5448-5461`) with **zero yield instructions** in the loop body, waiting for the countdown
  to reach 0. `shutdownAudioEngine` (`funcs_24.c:5143-5178`) has the identical pattern on the same
  address.
- The ONLY decrement site anywhere in the recompiled game code (exhaustively grepped) is inside
  `musyxSynthFrame`, which can never run *from inside the spin* — so once the gate byte flips to 1,
  `runVideoFrameTick` deadlocks on its own first line of work, and VI stops advancing at whatever count
  it last reached (320 in every observed soak).

This confirms, at full address-level rigor, exactly what `docs/M5-AUDIO-PLAN.md` §3 row 1 / §4 step 4
already predicted as the single highest-risk regression of the whole M5 plan: *"needs a source-level fix
in the ucode's task-completion signaling, not a gate re-revert."*

## The work unit — one bounded source patch + one validation soak

**Change**: patch `waitForMusyXAudioTaskDone`'s and `shutdownAudioEngine`'s spin loops
(`funcs_24.c:5448-5461` and `5166-5178` in
`/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_24.c` — but recall these are
REGENERATED files; the actual edit point is wherever `fixup_game_funcs.py` patches this call chain, or a
new fixup entry if none exists yet for these two functions) so that each spin iteration explicitly calls
into real M_AUDTASK dispatch (the path s300/step 2 already confirmed live and crash-free:
`ROGUESQ_AUDIO_UCODE=1` → `factor5_ucode_b` dispatch in `main.cpp:594-620`) or otherwise pumps whatever
processes pending audio DMA batches, instead of relying on an unreachable decrementer. The minimal
version: replace the bare spin with a bounded loop (say 64 iterations) that calls the dispatch/pump
function each time it re-reads the countdown, then falls through regardless of whether the countdown
ever reaches 0 (log a diagnostic if it falls through without reaching 0, env-gated, free).

**Alternative, lower-risk framing if the pump call turns out non-trivial to wire in**: since `musyxSynthFrame`
is the ONLY decrementer, and it's a normal per-frame-tick function (not itself gated behind this spin),
consider instead whether `musyxSynthFrame` (or its caller) should run BEFORE `waitForMusyXAudioTaskDone`
is ever entered on the very first frame — i.e., is the countdown's initial seed of `0x10` meant to
represent "16 audio tasks were just queued, wait for RSP to finish them" in a context where, on real
hardware, an interrupt asynchronously decrements it as the RSP completes work in the background? If so,
the more faithful recomp fix may be making M_AUDTASK dispatch (already confirmed synchronous per step 2)
decrement this SAME countdown directly as part of its own synchronous completion, rather than relying on
`musyxSynthFrame`'s batch-count subtraction. Grep for what actually queues into this countdown (is `0x10`
literal, or does it vary?) and cross-reference against the M_AUDTASK dispatch counter from step 2 before
committing to the "pump the spin loop" framing above — a source-read pass on this specific question is
CHEAP relative to a wrong patch, do it before writing the fixup.

**Discriminating measurement for the soak**: with `setDisplayMode`'s gate-byte site reversed (patch
already exists for this — narrow the store-patch regex in `fixup_game_funcs.py` to `0x8008EB40` only,
same procedure as all prior sessions) AND the new spin-loop patch applied, does VI progress past 320 to
title (VI=1024, ~46.5s baseline)? Two clean soaks (per the M5 plan's own bar) without crash-family #1's
signature recurring would validate the fix; a hang at a DIFFERENT VI count than 320 would indicate the
patch worked but exposed a new downstream issue; a hang still at exactly 320 would falsify this session's
mechanism trace and needs re-investigation.

## Environment notes (carried forward, still valid)

- Regen paths for game-code patches: `/Users/williambuckley/Documents/Tools/N64Recomp`
  (`fixup_game_funcs.py`, untracked/uncommitted loose file — NOT git-tracked in that repo, so no
  N64Recomp-side commit is needed after edits there; only THIS repo's ledger records what changed).
  Regen order: `make_elf.py` -> `N64Recomp` -> `fixup_game_funcs.py` -> `cmake`, in that exact order.
  `N64Recomp` skips files that already exist on disk, so `RecompiledFuncs/*.c` MUST be deleted before
  every `N64Recomp` run: `python3 -c "import glob, os; [os.remove(f) for f in
  glob.glob('/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/*.c')]"`. `cd` into
  `N64Recomp` FIRST as its own bare `cd` command, THEN run `./build/N64Recomp rogue_squadron.toml` with
  output redirection in a SEPARATE Bash call (`/tmp` is blocked for redirects).
- To reverse ONLY `setDisplayMode`'s site (not `reapplyDisplayMode`'s): narrow the STORE-patch regex in
  `fixup_game_funcs.py` (search for `0x8008E(?:B40|C88)`) to `0x8008EB40` ONLY. Verify via
  `audio gate patched x1` in the fixup report. MUST restore the full `(?:B40|C88)` alternation before
  ending session (`audio gate patched x2`).
- Soak driver template: `scratch/s73_post_a_scene/run_step325widecap.sh` (copy it). Invoke as
  `zsh run_foo.sh <label>`, not `./run_foo.sh`. `cd` into `scratch/s73_post_a_scene` first as its own
  bare command. Launch via Bash with `run_in_background: true`, then `TaskOutput` with `block: true` and
  `timeout` up to 600000ms — do NOT foreground-poll. Confirm `pgrep -f "build/RogueSquadron64Recomp"` is
  empty before AND after.
- `DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build build -j8` from this repo's
  root — allowlisted verbatim, works as a single command.
- Arm `ROGUESQ_AUDIO_UCODE=1` in the soak (step 2's real-ucode toggle) so the "pump real dispatch"
  patch has real dispatch available to pump, not the `musyx_stub` default path.

HYPOTHESIS-ID: m5-audio-destub-step4-setdisplaymode-vi320-hang (2nd of budgeted 3 iterations — s326 was
pure source-read/mechanism-tracing, this iteration is the first to spend a soak on it. Per iron rule 8,
a 3rd consecutive iteration with no discriminating result forces a pivot preamble.)
