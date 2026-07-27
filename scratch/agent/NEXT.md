# NEXT work unit — M3: find the indirect caller of `submitDmaRequestBatch`

s96 was the 2nd consecutive inconclusive attempt at this. Read
PORTING-STATE.md's Session 96 entry before doing anything else; this
file only has the actionable summary.

## What's established (do not re-derive)

- `get_function` (`lib/N64ModernRuntime/librecomp/src/overlays.cpp:397`)
  is the genuine single chokepoint for every indirect (`LOOKUP_FUNC`/
  `jalr`) call in the recompiled program (s95, confirmed via codegen
  template + a 28388/28389 call-site count). The known boot-time call
  to `submitDmaRequestBatch` is a **direct** call and structurally
  cannot trigger the instrument. **Do not re-derive this.**
- `ROGUESQ_LOG_DMA_CALLER=1` is armed, correctly implemented, and
  **cheap**: `rs64_log_dma_ring_caller` (`overlays.cpp:406-423`) does a
  single `int32_t` compare against the target address *before* any
  `getenv` call, and the `getenv` itself is cached in a function-local
  `static const bool`. **s96 checked this by reading the source (no
  soak needed) and refuted "the instrument perturbs timing" as an
  explanation for early deaths — do not re-check this.**
- Two soaks in a row (s95, s96) with this instrument armed died before
  the ~140s mark where the DMA phenomenon occurs, each to a
  **different, unrelated** crash (12th class `composeNpcOrientationMatrix`
  at s95; a brand-new 13th class, an RT64-internal
  `reinterpretTileRecord` "Unimplemented reinterpretation logic" assert
  at `rt64_framebuffer_manager.cpp:480`, at s96). **Neither counts as
  evidence against the DMA-caller hypothesis** — both are environment
  misses (the run never reached the relevant window). Per rule 8,
  that's 2 of up to 3 allowed non-discriminating attempts.
- Do NOT re-plan "dump the `OSIoMesg` at `mb`" (refuted s92) or cite
  `ra=0` as corruption evidence (refuted s92, routine on 487+ calls).
  Do NOT re-open "is it a consumer index-desync bug" or "is it an
  external RDRAM stomp" — s94's producer-side log already shows the
  corruption present at write-time, ruling out both.
- Do NOT re-grep for `submitDmaRequestBatch(rdram` or the
  `LOOKUP_FUNC(` call-site count — both done, stable, not changing.

## The 13th crash class (new this session, s96)

SIGABRT: `Assertion failed: ("Unimplemented reinterpretation logic." &&
(...three OR'd format-combo checks on srcFmt/srcSiz/dstFmt/dstSiz/
tlutFormat...)), function reinterpretTileRecord, file
rt64_framebuffer_manager.cpp, line 480`. Backtrace:
`RT64::FramebufferManager::reinterpretTileRecord` ← `recordOperations`
← `State::fullSync`'s per-pair lambda ← `fullSync` ← `GBI_RDP::fullSync`
← `Interpreter::processRDPLists` ← the normal RDP-submission chain.
This is RT64-internal code (same class as the s86 TMEM-zero assert) —
no source-level bug on our side, just a format-reinterpretation case
its own author never implemented. First occurrence, hold+~3s. No field
values logged at the assert site (only the source condition text).
**Not yet instrumented** — per the project's convention, wait for a
2nd recent recurrence before dedicating a soak to it.

## The work unit

One more identical retry of the exact s95/s96 repro (this is the 3rd
and last allowed attempt per rule 8 before parking):

```
env ROGUESQ_LOG_ANIM_CB=1 ROGUESQ_LOG_TMEM_ZERO=1 \
    ROGUESQ_LOG_ANIM_TEX_STREAM=1 ROGUESQ_LOG_HANGAR_ENTRY=1 \
    ROGUESQ_LOG_DMA=1 ROGUESQ_LOG_DMA_RING=1 ROGUESQ_LOG_DMA_CALLER=1 \
    ROGUESQ_LOG_THREAD_RESUME=0 \
    PROBE_MODE=start_only HOLD_S=30 zsh \
    scratch/s73_post_a_scene/run_mission_keys.sh s97_dmacaller3 0 12
```

Note: the script's own `print` output (phase timings, `[keys]` lines,
hold/grace status) goes to the Bash tool's own stdout capture, NOT into
`$OUTDIR/run.log` — only the game binary's stdout/stderr is redirected
there. Read both: the tool output for the script's own timeline/status
lines, `run.log` for `[CRASH]`/instrument fires. (s96 initially grepped
`run.log` for `[keys]` and got a false 0 — wasted a step rediscovering
this; don't repeat it.)

Outcomes:

1. **Reaches ~140s and `ROGUESQ_LOG_DMA_CALLER` fires** — read the
   backtrace, it names the actual indirect caller of
   `submitDmaRequestBatch` directly. Go read that caller's source: the
   bug is almost certainly a wrong field offset or wrong array stride
   writing a name/label-table value into a `devAddr` field.
2. **Reaches ~140s, `do_rom_read` crashes but `ROGUESQ_LOG_DMA_CALLER`
   never fired** — genuinely new, contradicts s94's finding; re-examine
   whether s94's read of the producer log was specific to that run.
3. **Dies early again to any crash (12th, 13th, or new)** — this is
   the 3rd non-discriminating attempt. Per rule 8, STOP retrying this
   blind repro. Instead: tally which of the hangar-tick-adjacent crash
   classes (9th `updateAnimatedTextureStreaming`, 10th
   `static_5_800B4048`, 11th `projectModelBoundsToScreen`, 12th
   `composeNpcOrientationMatrix`) has the most total occurrences across
   all sessions and give *that one* a dedicated `ROGUESQ_LOG_*`
   entry-log (same pattern as `ROGUESQ_LOG_ANIM_TEX_STREAM`/
   `ROGUESQ_LOG_HANGAR_ENTRY`) as the next work unit — reducing how many
   different crashes can win the early-death race is now higher
   expected value than a 4th blind retry of the same repro. (The 13th
   class, `reinterpretTileRecord`, is RT64-internal and not part of
   this MEM_W-off-an-arg family — don't fold it into this tally.)

Rebuild is not needed (nothing changed since s95's build). If a
dedicated instrument for a hangar-tick crash class is landed instead
(outcome 3), the pipeline is `make_elf.py` → `N64Recomp` →
`fixup_game_funcs.py` → `cmake --build`.

## Do not

- Do not re-grep for `submitDmaRequestBatch(rdram`, the ring literal
  constants, or `LOOKUP_FUNC(` call-site counts — all done, stable.
- Do not cite `ra=0x00000000` as evidence of anything — routine (s92).
- Do not re-plan "dump the `OSIoMesg` at `mb`" — refuted (s92).
- Do not re-open "index-desync in the consumer" or "external stomp
  after a clean write" as hypotheses — s94's producer-side log already
  shows the bad value at write-time, ruling both out.
- Do not combine `ROGUESQ_LOG_THREAD_RESUME=1` with this repro without
  a specific reason — confirmed confound (s93).
- Do not re-check whether `ROGUESQ_LOG_DMA_CALLER` itself adds overhead
  — read the source and refuted, s96 (single int compare, cached
  getenv).
- Do not grep `run.log` for the script's own `[keys]`/phase-timing
  lines — they aren't there (s96); read the Bash tool's stdout capture
  for those instead.
