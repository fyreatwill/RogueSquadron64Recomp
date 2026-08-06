# NEXT work unit

## s370: `heapwalker-guard5-site` CLOSED (2/2 non-recurrence) — pivot to M5 Step 6

s369's GUARD5 verify pair drained and both are non-recurrence data points (full detail:
CURRENT-TRUTH item -225, PORTING-STATE Session 370). `heapWalker+1696`/`0x8000834c` is no longer
an open thread. **No M5 Step 5 or escalated-background-noise threads remain open.** Per the
standing directive (`docs/CURRENT-TRUTH.md` USER DIRECTIVE §2) and `docs/M5-AUDIO-PLAN.md` §4,
the next M5 work is **Step 6 — validate real PCM reaches SDL, not just that the guest stopped
hanging.**

## Competing hypotheses for Step 6

1. **PCM is fine** — the ucode (`factor5_ucode_b`, dispatched under `ROGUESQ_AUDIO_UCODE=1` since
   step 2) produces real, non-silent samples and `queue_samples`/`SDL_QueueAudio` pass them through
   correctly. Expected discriminating result: a non-zero-sample counter shows a healthy fraction of
   non-silent buffers once past boot.
2. **Silent-but-not-crashing** — the ucode completes and the pipeline never crashes (already
   confirmed by step 2/step 5's clean soaks), but the buffers `queue_samples` receives are all-zero
   (silence) because of a format mismatch, an unfed voice-mixing step, or the ucode short-circuiting
   its own PCM-generation path even while "completing" the task cleanly. Expected result: the
   silent-buffer counter stays ~100% even well past boot/menu.
3. **Garbage-but-not-crashing** — buffers are non-zero but not coherent audio (e.g. uninitialized
   RDRAM, wrong stride/channel interleave). A simple non-zero check alone can't fully distinguish
   this from hypothesis 1 — if the sanity counter comes back "non-silent," treat that as
   necessary-not-sufficient and note explicitly that only a real listen-test (not automatable here)
   would fully confirm coherent audio, not just non-zero content.

**Discriminating measurement**: an env-gated counter in `queue_samples` (`src/main/main.cpp:677`)
that iterates the `int16_t* samples` buffer for the first N calls (and every Mth call after) and
logs whether every sample in that call was exactly zero, plus a running "all-zero calls / total
calls" ratio. This alone splits hypothesis 2 from {1, 3}. It cannot by itself split 1 from 3 (that
needs either statistical variance/spectral checks or a real listen — out of scope for this pass;
note the limitation rather than over-claim).

## Insertion point (scouted s370, read-only, no code changed yet)

- `queue_samples(int16_t* samples, size_t num_bytes)` — `src/main/main.cpp:677-681`. Note: despite
  the parameter name, `ultramodern::queue_audio_buffer` (`lib/N64ModernRuntime/ultramodern/src/audio.cpp:25-36`)
  actually passes a **sample count**, not a byte count, into this parameter (`sample_count =
  byte_count / sizeof(int16_t)` computed there) — confirm this before writing the iteration bound,
  or the counter will read out of bounds or under-scan.
- Call chain: `osAiSetNextBuffer_recomp` (`lib/N64ModernRuntime/librecomp/src/ai.cpp:18-21`) →
  `ultramodern::queue_audio_buffer` (`audio.cpp:25-36`) → `audio_callbacks.queue_samples` →
  `main.cpp:677-681`'s concrete `queue_samples`, registered at `main.cpp:1842`.
- No existing instrument sits on this path (verified by grep this session). The existing
  `[audtask-dispatch]` counter (`main.cpp:607-634`) is the RSP task-DISPATCH side (a different
  mechanism, already confirmed firing continuously since s300) — do not confuse the two or treat
  dispatch activity as evidence about sample content.
- **This is a `src/` edit, not a `lib/` edit** — `queue_samples` lives in this repo's own
  `src/main/main.cpp`, not the `lib/N64ModernRuntime` submodule. No `submodule-patches/export.sh`
  needed for this specific change (only if the session also happens to touch anything under
  `lib/`).

## Concrete plan for next iteration

1. Read `src/main/main.cpp:670-690` (the `queue_samples` function and its immediate context) and
   `lib/N64ModernRuntime/ultramodern/src/audio.cpp:20-40` to confirm the sample-vs-byte-count
   question above before writing anything.
2. Add an env-gated counter (`ROGUESQ_LOG_PCM_SANITY` or similar; follow the existing
   `getenv`-check + static counter convention already used for `[audtask-dispatch]` at
   `main.cpp:607-634`): for the first ~20 calls then every 256th (matching the existing sampling
   convention), scan the buffer, log `[pcm-sanity] n=<call#> samples=<count> all_zero=<0|1>
   nonzero_n=<count>`, and maintain a running `all_zero_calls`/`total_calls` ratio printed
   periodically.
3. Build (`cd build && cmake --build . -j8`, no regen pipeline needed — this is host-side C++, not
   guest recompiled code).
4. Run ONE soak with `ROGUESQ_AUDIO_UCODE=1` (required — this is the step-2 toggle that makes the
   real ucode dispatch instead of the stub) + the new sanity env var + all current guard/positive-
   control instruments armed (per `run_s327waitpump.sh`'s defaults), `HOLD_S=120` is enough for a
   first pass (this is a per-call-content check, not a rare-crash-recurrence hunt — don't over-
   budget wall time on it).
5. Positive control requirement (iron rule 1): the counter must show SOME calls logged (proves the
   instrument fires at all) before its all-zero ratio means anything. If `queue_samples` is never
   called even with `ROGUESQ_AUDIO_UCODE=1`, that's itself a finding (either the ucode isn't
   actually driving `osAiSetNextBuffer`, or step 2's earlier "M_AUDTASK dispatches from n=0" doesn't
   imply "queue_samples gets called" — check that assumption explicitly, don't take it on faith
   from the step-2 writeup).
6. Read the decision split: all-zero ratio near 100% after boot → hypothesis 2 (silent-but-not-
   crashing), write it up as the closer to M5 Step 6's original question and note that this is the
   FIRST of the 4 M5 crash families' "audio content actually plays" question ever gets a real
   answer either way. All-zero ratio near 0% → hypothesis 1/3, note the "non-zero ≠ verified
   coherent" caveat explicitly rather than declaring victory.

HYPOTHESIS-ID: m5-audio-destub-step6-pcm-sanity (iteration 1 — new thread, pivoted from the closed
heapwalker-guard5-site thread this session).
