# NEXT work unit

## s331 was a MAINTENANCE iteration — done, not blocking this one

s331 compacted `docs/CURRENT-TRUTH.md` from 63,161→40,424 bytes (668→459 lines, 209 net line
shrink — clears the >=200 ADVANCED bar). It condensed items -182..-187 (the s323-329 fix/confirm arc)
and merged items -160..-181 (the s297-322 measurement-chasing runway) into two summary paragraphs,
migrating no unique facts — full detail remains in `PORTING-STATE` Sessions 297-329. `docs/
CURRENT-TRUTH.md` is now well under the 60,000-byte Step-0 trigger; **this iteration should proceed
straight to the M5 work below**, no maintenance check needed first (Step 0 will still gate it, but the
byte count should read well clear).

## Runtime-confirm the `waitForMusyXAudioTaskDone` 2nd-spin-loop hypothesis (2nd of 3 budgeted iterations)

### Status note (s330): strong candidate mechanism found via source-read, NOT runtime-confirmed

s330 traced `waitForMusyXAudioTaskDone`'s on-disk body end to end and found the s327 pump-fix
(`funcs_24.c:5456-5477`) only bounds ONE of TWO spin loops in that function. A second, unpatched loop
at `funcs_24.c:5540-5550` (`while (MEM_BU(0x8014974C) != 0) {}`) has no bound, no pump call, no
diagnostic. The flag it spins on is armed inside `musyxSynthFrame` right before an indirect call
(`funcs_24.c:3991-3992`) and only clearable by that same function's own top-of-function logic
(`funcs_24.c:3285-3315`), itself gated behind a blocking `osRecvMesg_recomp`. Personally
byte-for-byte verified (not just the delegating subagent's claim) — see `PORTING-STATE` Session 330
and `docs/CURRENT-TRUTH.md` item -188 for full citations.

**This is NOT yet a closed hypothesis.** No runtime observation was collected — nobody has confirmed
the game thread is actually parked at this loop during an actual stall, nor observed the flag's real
value there. It also does not yet explain why `setDisplayMode`'s 3/3 clean s327/s328 soaks never hit
this same code path despite an identical `musyxNoopStub`→`waitForMusyXAudioTaskDone` call at boot —
the leading (unconfirmed) explanation is that `reapplyDisplayMode` is NOT self-clearing and re-triggers
every frame (unlike `setDisplayMode`'s true one-shot call), compounding the odds of hitting whatever
narrow condition makes loop 2 hang.

## Hypotheses (pick the discriminating probe)

1. **True unconditional deadlock**: once armed, the `0x8014974C` flag genuinely never reaches 0 again
   from the game thread's perspective in this configuration (e.g. the message the clear-path needs
   depends on something the frozen game thread itself would otherwise deliver — a real circular
   dependency). Discriminator: log the flag's value once per iteration of the spin (rate-limited) —
   if it holds at a fixed nonzero value indefinitely, this is confirmed.
2. **Racy-but-technically-clearable**: the background audio thread's own `musyxSynthFrame` calls DO
   periodically clear the flag, but the unsynchronized busy-spin (`MEM_BU`, no yield/atomics) almost
   never samples the brief cleared window before the background thread re-arms it on its next call.
   Discriminator: same flag-value log — if it's seen oscillating 0/1 rapidly but the spin still never
   exits, this is confirmed instead of hypothesis 1.
3. **Not this loop at all** — the real stall is somewhere else entirely and this 600s soak's game
   thread was never actually parked here. Discriminator: a PC/call-stack marker at loop entry
   (`funcs_24.c:5540`) that fires once and is checked for presence in the log — if it never fires,
   this hypothesis wins and the s330 trace needs to be revisited for a wrong-turn earlier in the
   chain (most likely: `reapplyDisplayMode`'s 3-condition guard at `funcs_0.c:1703-1731` never
   actually trips true in this soak's timeline, so `runVideoFrameTick` never even reaches its call).

## The work unit

1. Add a diagnostic (`N64Recomp/fixup_game_funcs.py`, following the established
   `[audio-wait-pump-stall]`/`[synth-entry]` convention — env-gated, rate-limited to ~20-40 prints,
   thread-tagged if cheap via `pthread_self()`/`std::this_thread::get_id()`):
   - one fire at entry to the 2nd spin loop (`funcs_24.c:5540`, before the `L_80091F34:` label) —
     confirms hypothesis 3 is false if it fires at all.
   - a rate-limited periodic print of the flag's value (`MEM_BU(..., -0x68B4)`) while inside that
     loop — distinguishes hypothesis 1 (constant nonzero) from hypothesis 2 (oscillating).
   - a fire at the flag's clear site (`funcs_24.c:3300`, right after `osRecvMesg_recomp` returns and
     before the clear-store) and at the arm site (`funcs_24.c:3991`) — to see which thread/context is
     doing the arming/clearing while the game thread is (or isn't) stuck.
2. Regen (`make_elf.py` → `N64Recomp` → `fixup_game_funcs.py` → cmake — delete `RecompiledFuncs/*.c`
   first, N64Recomp skips existing files), narrow the gate regex to `reapplyDisplayMode`'s site only
   (`0x8008EC88`-ish, matching s329's exact narrowing — confirm via `funcs_23.c` grep, not just the
   patch-count report), rebuild.
3. Soak once with `scratch/s73_post_a_scene/run_s327waitpump.sh` (or equivalent — same driver as
   s327-329), armed with the new diagnostics. Expect: phase-timeout INCONCLUSIVE at 600s again (same
   symptom), but now with the new diagnostics either firing (confirms mechanism, tells you which of
   H1/H2) or not firing (refutes it, forces a return to step-by-step tracing from
   `reapplyDisplayMode`'s guard condition instead).
4. If confirmed (H1 or H2): propose and apply a bound/fallthrough fix on the 2nd loop, mirroring
   s327's pattern exactly (bounded pump/wait count, diagnostic on non-drain, falls through
   regardless), then soak once more to confirm clean VI progression past 640 to title. Do NOT
   promote either gate site to the shipped default without an explicit, separately-flagged decision —
   revert to full force-zero baseline before ending regardless of outcome.
5. If refuted (H3): the diagnostic silence itself is the result — pivot the hypothesis-id and
   redo the guard-condition trace from `funcs_0.c:1703-1731`, this time confirming via a runtime
   fire-once marker whether `reapplyDisplayMode` is even reached in this soak's timeline at all.

## Environment notes (carried forward — see s327-330 for full detail)

- Regen paths: `/Users/williambuckley/Documents/Tools/N64Recomp` (`fixup_game_funcs.py`, untracked).
  Delete `RecompiledFuncs/*.c` before every `N64Recomp` run:
  `python3 -c "import glob, os; [os.remove(f) for f in
  glob.glob('/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/*.c')]"`.
- Soak driver: `scratch/s73_post_a_scene/run_s327waitpump.sh <label>`, invoked from
  `scratch/s73_post_a_scene`, launched via Bash `run_in_background: true` then `TaskOutput` blocking
  up to 600000ms. Log lands at `scratch/s73_post_a_scene/<label>/run.log` — grep, don't read directly.
- `DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build build -j8` — allowlisted
  verbatim.

HYPOTHESIS-ID: m5-audio-destub-waitformusyx-secondspin-hang (2nd of 3 iterations — s330 was the
source-read that identified the candidate mechanism [1st]; s331 was a maintenance iteration and did
not spend a hypothesis iteration on this thread; this iteration is the runtime-confirmation step).
