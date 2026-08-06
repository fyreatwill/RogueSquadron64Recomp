# NEXT work unit

## s372 was MAINTENANCE (Step 0 triggered at 61,918 bytes) — no experiment ran; the s371 work unit
## below is UNCHANGED and still the next thing to actually run.

`docs/CURRENT-TRUTH.md` is now 42,407 bytes / 478 lines (was 61,918 / 692) after folding the
now-fully-closed s354-370 M5 Step 5 guard-hunting arc (Thread A, Thread B, heapWalker GUARD5) into
`docs/PROJECT-OVERVIEW.md` §11. See `PORTING-STATE.md` Session 372 for the full compaction summary.
This did not touch the actual investigation state below — pick it up exactly where s371 left it.

## s371: M5 Step 6 ANSWERED (real PCM is 100% silent) — trace WHY next, or pivot

Step 6's question ("does real PCM reach SDL, not just does the guest stop hanging") now has a real
answer: **no** — see `docs/CURRENT-TRUTH.md` Next-steps item -226 and `docs/M5-AUDIO-PLAN.md` §4.
Along the way, found and fixed a genuine, previously-undetected bug: `queue_samples`
(`src/main/main.cpp:677-`) was silently dropping half the bytes of every PCM buffer handed to
`SDL_QueueAudio` (byte-count/sample-count unit mismatch, present since this bridge was written).
Fixed. Added `ROGUESQ_LOG_PCM_SANITY`. Two soaks (13,832 total logged calls, 13,825 of them under
confirmed genuine RSP-dispatched `real_ucode=1`) found **100% of samples are exactly zero** — the
ucode dispatches and completes without crashing but the actual audio content never becomes
non-silent.

## Competing hypotheses for "why is PCM silent" (the natural Step 6 follow-on)

1. **Voice array never populated** — the ucode's mixing step reads a voice/channel array that
   nothing upstream (note-on / envelope triggering, `initVoiceSample` etc.) is actually filling in
   under this LLE-only, no-audio-enable-gate execution path, so it correctly mixes "nothing" into
   silence. Expected discriminating signal: a counter on whatever loop/array `musyxSynthFrame`
   reads per-voice (or its RSP-side equivalent in `factor5_ucode_b`) shows 0 active voices the
   whole run, even during the SELECT YOUR CRAFT / hangar phase.
2. **Mixing gated off** — a global "audio enabled"/mix-active flag (distinct from the gate-byte
   sites already reversed in Steps 2-4) still short-circuits the mix step to write zeros
   unconditionally, independent of voice content. Expected signal: same 0-voices-active counter as
   #1 would NOT distinguish this from #1 alone — need a second check, e.g. whether the mix loop body
   executes its accumulate/write instructions at all vs. skipping straight to a memset-style zero
   fill.
3. **Wrong buffer/stride being read at some pipeline stage** — the ucode writes real, non-zero PCM
   to ONE buffer/offset, but `osAiSetNextBuffer`/`queue_samples` reads from a different one (stale
   pointer, off-by-one double-buffer index, DMEM segment mismatch). Expected signal: a raw dump of
   the FULL DMEM/ucode-output audio buffer immediately after `factor5_ucode_b` returns, compared
   against what `queue_samples` receives — if the ucode's own output buffer is non-zero but
   `queue_samples`'s copy is zero, this is confirmed and #1/#2 are ruled out.

**Discriminating measurement**: needs source-tracing `factor5_ucode_b`'s task body (or its
recompiled MIPS source, whichever is more direct) to find (a) where/whether it reads a per-voice
active-list before mixing, and (b) whether the accumulate step is skipped or genuinely runs on all-
zero inputs. This is a source-read-first work unit (per the standing "batch instrumentation" rule,
don't build a counter blind) — read before instrumenting.

## Alternative: declare Step 6 sufficiently answered and pivot

Per the strategic priority order, M5 audio de-stubbing is priority 2 (after maintenance) — Step 6
itself is now empirically answered (silent, not garbage, not crashing). If the "why" investigation
above is judged lower-value than returning to M3 idiom-class audits (priority 3) or another M5
open thread, that's a legitimate call for the next iteration to make explicitly, not by default.

## Iteration budget

s372 was maintenance, not an experiment iteration — it does not consume a slot against the
3-iteration budget on this hypothesis thread. The next iteration that actually RUNS the Step 6
"why" experiment is iteration 2 of this thread (s371 was iteration 1: it answered the parent
question and opened this follow-on, but did not yet attempt the follow-on itself).

HYPOTHESIS-ID: m5-audio-destub-step6-pcm-sanity (iteration 2 — Step 6's original question answered
s371; this continues into "why is it silent" under the same thread since it's a direct follow-on,
not a new hypothesis).
