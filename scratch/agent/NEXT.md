# NEXT work unit — why does reversing setDisplayMode's gate-byte site hang the process at VI=320 before title (VI=1024)?

## Status note (s325): pivot — the tick37-vs-hardstop40 hypothesis is CLOSED

s325 ran the discriminating build+soak NEXT.md queued: widened gate1/gate2/gate3's diagnostic print cap
in `fixup_game_funcs.py` (N64Recomp repo) from `n<40` to `n<4096`, so every real invocation gets logged
instead of only the first 40. Result, uncapped: gate1 fired 71 times (33 real calls), gate2 4 times (4
calls), gate3 0 times — **33+4+0 = 37, an EXACT match** to the tick-producer functions' own independent
entry count (`reach-allsongs-entry`/`tick-audio-seq`, both 37/37) in the SAME run. Two independent
measurement mechanisms agree exactly. The "37 vs 40"/14-call gap was a 4th instance of the sampling-cap
illusion already found and fixed 3 times before in this investigation (s312/s313/s315) — the diagnostic
cap (`n<40`) was silently hiding 31 real gate1 invocations because no run had ever printed past `n=39`
(the `n%128==0` fallback never fired since gate1 never reached `n=128`). Full detail: CURRENT-TRUTH item
-183, PORTING-STATE Session 325.

**This closes `HYPOTHESIS-ID: m5-audio-destub-step4-tick37-vs-hardstop40` (s303-325) for good.** The
call-count mystery is solved. It does NOT close the underlying M5 step 4 task.

## Context — what actually blocks M5 step 4

Per `docs/M5-AUDIO-PLAN.md` §4 step 4: reverse each of the 3 audio-gate-byte force-zero sites one at a
time, watching for crash family #1 (`waitForMusyXAudioTaskDone`/`shutdownAudioEngine` boot-hang, a
confirmed historical failure mode) to recur. `initMusyXEngine`'s site was reversed at s302 and validated
0/2 recurrence — but s306 found that "clean" result was actually dead code (a positive-controlled entry
counter showed `initMusyXEngine` is never called at all in any soak), so gate=1 there has still never
been genuinely exercised. `setDisplayMode`'s site is next in the plan's sequence, and it has been
reversed and re-reverted 15 times now (s303-325) — but EVERY one of those reversals was in service of
instrumenting the gate1/2/3 call-count side-question (now closed), not to actually validate step 4's own
question. **What actually happens when `setDisplayMode`'s site is reversed, independent of any of the
gate1/2/3 diagnostics**: the process reliably hangs at VI=320/rdpFs=39 and never reaches the title screen
(VI=1024, ~46.5s in the default/baseline config). Nobody has root-caused why yet — this has been treated
as "the expected, established behavior for this soak recipe" (a backdrop fact used to justify the phase
timeout in every one of the 15 reversal soaks) rather than as the actual open question it is.

## Competing hypotheses — write down 2-4, find the DISCRIMINATING measurement

1. **`setDisplayMode` itself, once un-force-zeroed, does something that stalls VI/present progression**
   — e.g. it now actually calls into real display-mode-setting code (framebuffer reconfiguration, video
   mode change) that never gets properly completed/acknowledged in this recomp, wedging a
   handshake/semaphore the VI-retrace thread depends on. Discriminator: source-read `setDisplayMode`
   (`funcs_23.c`, guest ~0x8008EB40) in full — what does it do besides the gate-byte store when NOT
   force-zeroed? Does it touch any VI/framebuffer/scheduler state that the present/VI-retrace path reads?
2. **The gate byte's OWN state (now genuinely 1 instead of 0) changes control flow somewhere downstream
   of `setDisplayMode` in a way that stalls audio-adjacent scheduling, which in turn (per the historical
   family #1 signature) wedges the cooperative scheduler that VI progression also depends on.**
   Discriminator: grep every OTHER read site of the gate byte (0x800A0F50) besides the 3 gate1/2/3 sites
   and `setDisplayMode`/`reapplyDisplayMode`'s own stores — does any of them gate scheduler/VI-adjacent
   code specifically (not just audio ticking)?
3. **This is not really about `setDisplayMode` at all — it's a pre-existing hang that ONLY manifests
   when this specific code path is reached, and reversing the gate byte is incidental (e.g. it changes
   timing enough to expose a race that's independent of audio).** Discriminator: a soak with
   `setDisplayMode`'s site reversed but the CALLING convention/environment otherwise identical to a
   known-good baseline soak — compare a VI-progress diagnostic (frame-by-frame VI width log, if one
   exists, or add one) between the two configs to see exactly which frame/call stalls, then correlate
   against `setDisplayMode`'s own call count in the same window.
4. **A genuinely different function entirely (not `setDisplayMode`) is what's actually gated by the
   byte at the point that matters for VI progression**, and `setDisplayMode` merely happens to be the
   easiest site to flip textually. Discriminator: same as (2) — full inventory of gate-byte read sites.

## Suggested first step — pure source-read, no soak

Read `setDisplayMode`'s full guest-disassembly-annotated body in `funcs_23.c` (search
`0x8008EB40` in `/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_23.c`) end to end.
Identify every side effect besides the gate-byte store. Cross-reference against `docs/M5-AUDIO-PLAN.md`
§1's inventory of where audio is stubbed, to see if `setDisplayMode`'s un-stubbed body calls into any of
that stubbed machinery. This alone may explain the VI=320 hang without needing a new instrumented soak —
try it first, per the standing "source-read before build+soak" convention this whole investigation
established.

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
- gate1/2/3's diagnostic print cap is now permanently `n<4096` (widened s325, was `n<40`) — no further
  action needed there, this was a deliberate, durable improvement.
- To reverse ONLY `setDisplayMode`'s site (not `reapplyDisplayMode`'s): narrow the STORE-patch regex in
  `fixup_game_funcs.py` (currently ~line 179-181, search for `0x8008E(?:B40|C88)`) to `0x8008EC88` ONLY.
  Verify via `audio gate patched x1` in the fixup report (x2 = both sites/default, x1 = one site
  reversed). MUST restore the full `(?:B40|C88)` alternation before ending session (`audio gate patched
  x2`).
- Soak driver template: `scratch/s73_post_a_scene/run_step325widecap.sh` (newest; copy it). Invoke as
  `zsh run_foo.sh <label>`, not `./run_foo.sh`. `cd` into `scratch/s73_post_a_scene` first as its own bare
  command. Launch via Bash with `run_in_background: true`, then `TaskOutput` with `block: true` and
  `timeout` up to 600000ms — do NOT foreground-poll. Confirm `pgrep -f "build/RogueSquadron64Recomp"` is
  empty before AND after. Expect `phase timeout (INCONCLUSIVE)` after ~600s with `setDisplayMode`
  reversed — this is the hang under investigation, not a run failure; the log data before the freeze (or
  a new VI-progress diagnostic, if step 3/4 of the hypothesis above calls for one) is what matters.
- `DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build build -j8` from this repo's
  root — allowlisted verbatim, works as a single command.

HYPOTHESIS-ID: m5-audio-destub-step4-setdisplaymode-vi320-hang (1st iteration — new thread, pivoted from
the now-closed m5-audio-destub-step4-tick37-vs-hardstop40. Per iron rule 8, budget 3 experimental
iterations before a forced pivot/BLOCKED preamble.)
