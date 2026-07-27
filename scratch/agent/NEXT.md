# NEXT work unit — M3: run the batched-instrument soak (next-steps item 1)

s90 ran the exact NEXT.md-prescribed soak (`animcb4`) to try to catch
the `queueGPUUploadTMEM` zero-size assert with `ROGUESQ_LOG_TMEM_ZERO=1`
armed. It still didn't fire (0/4 across s87/animcb2/animcb3/animcb4) —
a **different, newer** crash preempted it, the **3rd time in a row**
this exact experiment shape (arm the flag, hope the target crash wins
the race) has failed to discriminate anything. Per ITERATION.md rule 8,
that specific plan is now demoted from "dedicated soak" to
"opportunistic" — do not spend another soak *specifically* chasing the
TMEM-zero assert alone.

Instead, s90 spent the rest of its budget landing **batched**
entry-log instruments for the two most recent, previously-uninstrumented
crash sites, following the existing `_anim_cb_patch` pattern in
`N64Recomp/fixup_game_funcs.py`:

- `ROGUESQ_LOG_ANIM_TEX_STREAM=1` — 9th crash class,
  `updateAnimatedTextureStreaming` (`funcs_11.c:13665`), logs `a0`
  (`ctx->r4`) at entry.
- `ROGUESQ_LOG_HANGAR_ENTRY=1` — 10th crash class, `static_5_800B4048`
  (`funcs_41.c:577`, called from `updateHangarBayScene`), logs `a0`/`a1`
  (`ctx->r4`/`ctx->r5`) at entry.

Both landed (`grep` confirmed x1 each), the build is clean (exit 0,
only pre-existing-class format warnings), but **neither has been run
yet**. That's this iteration's job.

## Why batch instead of one flag at a time

The last 3 soaks (s87, animcb3, animcb4) each armed a different single
diagnostic flag hoping to catch its target crash — and each time, a
*different, newer* crash fired first instead, so the armed flag never
got a chance to log anything useful. ITERATION.md's own rule ("batch
instrumentation: one build carrying every counter you will want, one
run collecting all of them") says this directly: stop testing one
hypothesis per soak. Arm everything live at once so whichever crash
actually fires this run, there's a good chance its instrument is
already reading.

## Command

```
env ROGUESQ_LOG_ANIM_CB=1 ROGUESQ_LOG_TMEM_ZERO=1 \
    ROGUESQ_LOG_ANIM_TEX_STREAM=1 ROGUESQ_LOG_HANGAR_ENTRY=1 \
    ROGUESQ_LOG_DMA=1 \
    PROBE_MODE=start_only HOLD_S=30 zsh \
    scratch/s73_post_a_scene/run_mission_keys.sh animcb5 0 12
```

(`ROGUESQ_LOG_THREAD_RESUME=1`/`ROGUESQ_LOG_OST_WB=1`/
`ROGUESQ_LOG_RUNNER=1`/`ROGUESQ_LOG_RUNNER_ALL=1` are already exported
inside `run_mission_keys.sh` itself — don't re-set them. **s90 resolved
the item-4 unknown**: the `[rom-read]` gate is `ROGUESQ_LOG_DMA`, not
`ROGUESQ_LOG_ROM_READ` (checked `lib/N64ModernRuntime/librecomp/src/
pi.cpp:72` directly — every prior soak since s86 that thought it was
arming this diagnostic was actually a no-op). Reuses the existing
build — no regen needed.)

## Discriminating measurement

1. `grep -n CRASH scratch/s73_post_a_scene/animcb5/run.log` — find the
   crash signal and backtrace.
2. Match the crashing function against the backtrace symbols
   (`static_5_800B4048` = 10th class / hangar-entry;
   `updateAnimatedTextureStreaming` = 9th class / anim-tex-stream;
   `queueGPUUploadTMEM` assert = TMEM-zero; anything else = an 11th,
   brand-new class — do not assume it's one of the 10 known ones
   without checking function names).
3. If it's one of the two newly-instrumented classes, grep the
   matching log tag (`[anim-tex-stream]` or `[hangar-entry-800B4048]`)
   for the last few entries before the crash — do the logged arg
   pointer(s) look like plausible RDRAM addresses (0x80xxxxxx range,
   in-bounds) or garbage (wildly out of range, misaligned in a way that
   doesn't match any real struct)? Garbage favors the shared-corruption-
   race hypothesis (next-steps item 4); plausible-but-still-crashing
   favors a logic bug local to that function.
4. If it's the TMEM-zero assert, read the `[tmem-zero-upload]` fields
   (uls/ult/lrs/lrt/masks/etc.) per the existing plan in CURRENT-TRUTH
   item 2 — sane-looking fields (e.g. `lrs<=uls`) → legitimate
   degenerate LOADTILE; fields outside any real tile descriptor's range
   → corruption.
5. If `ROGUESQ_LOG_ROM_READ` fired with a corrupted `physical_addr`,
   cross-reference its logged thread id/ctx against the nearest
   `[thr-resume]`/`[ost-wb]` events in the same log — this is the first
   real chance since s85 to test the shared-corruption-race hypothesis
   directly (item 4).
6. `[anim-recurse]` sp: note whether it stays in the known 6-value/
   312-byte band through this crash too — bonus data point only, not
   the primary target (that hypothesis is parked).

## Do not

- Do not run another soak with only `ROGUESQ_LOG_TMEM_ZERO` armed alone
  — that specific plan is demoted per rule 8 above.
- Do not spend this iteration chasing `advancePlayerAnimationPhase`
  (parked, CURRENT-TRUTH next-steps item 5) — 3 non-recurrences already.
- If this soak's crash is an 11th, genuinely new class, follow the
  established pattern: resolve the backtrace symbols against
  `symbol_files/*.txt` in the sibling `rogue_squadron64` checkout
  (read-only lookup, no edits needed there), read the crashing
  function's source in `N64Recomp/RecompiledFuncs/funcs_*.c` to find
  which argument-derived pointer is being dereferenced unchecked, and
  either add its entry-log instrument in this same iteration (if time
  allows, batched into the same fixup_game_funcs.py edit) or write up
  the finding and hand the instrument to the next NEXT.md.
- Budget: this is a fresh soak (animcb5), not a repeat of a
  rule-8-exhausted experiment — the batched-instrument approach is a
  different plan from "arm one flag and hope," so the counter resets.
