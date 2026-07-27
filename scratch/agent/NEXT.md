# NEXT work unit — M3: find the indirect caller of `submitDmaRequestBatch`

s95 landed the instrument this file previously prescribed
(`ROGUESQ_LOG_DMA_CALLER=1`, a `get_function`-chokepoint backtrace
instrument, `lib/N64ModernRuntime/librecomp/src/overlays.cpp`). It is
built, committed, and correctly working (positive control fired), but
its first soak never reached the part of the run where the phenomenon
happens. Read PORTING-STATE.md's Session 95 entry before doing
anything else; this file only has the actionable summary.

## What's established (do not re-derive)

- `get_function` (`lib/N64ModernRuntime/librecomp/src/overlays.cpp:397`)
  is a genuine single chokepoint for every indirect
  (`LOOKUP_FUNC`/`jalr`) call in the recompiled program — confirmed via
  the codegen template (`N64Recomp/src/cgenerator.cpp:410,414`, the
  sibling tool checkout) and a fresh count: 28388/28389 `LOOKUP_FUNC(`
  call sites across all 45 `N64Recomp/RecompiledFuncs/funcs_*.c` are
  followed immediately by `(rdram, ctx);` on the same line (the one
  non-match is a comment). **Do not re-derive this**, it's done once
  already (s95) on top of s93/s94's direct-call-site grep.
- The known boot-time call to `submitDmaRequestBatch` is compiled as a
  **direct** call (literal function name, not through `LOOKUP_FUNC`),
  so it structurally cannot trigger `ROGUESQ_LOG_DMA_CALLER` — only a
  genuine unlocated indirect caller can. No extra filtering is needed
  in the instrument.
- `ROGUESQ_LOG_DMA_CALLER=1` is armed and correctly implemented (uses a
  native `backtrace()` inside `get_function`, since `get_function`'s
  own frame sits directly under the calling generated function — no
  need to widen `get_function`'s signature, which is a shared ABI with
  the mods system and the live-recompiler JIT, don't touch it).
- s95's soak (`s95_dmacaller1`) got **0/0** on this instrument, but
  that is **not evidence against the hypothesis**: the same-run
  positive control (`dma-ring-producer n=0`, the boot call) fired
  exactly as expected, and the process died at hold+~5s — well before
  the ~140s mark where every prior soak that survived that long saw
  the phenomenon. The run simply never reached the relevant window.
  Do not count this as 1 of 3 "non-discriminating attempts" against
  the DMA-caller hypothesis itself; it's an environment miss, not a
  result. (It IS relevant to a different, older hypothesis — see
  "12th crash class" below.)
- Do NOT re-plan "dump the `OSIoMesg` at `mb`" (refuted s92) or cite
  `ra=0` as corruption evidence (refuted s92, routine on 487+ calls).
  Do NOT re-open "is it a consumer index-desync bug" or "is it an
  external RDRAM stomp" — s94's producer-side log already shows the
  corruption present at write-time, ruling out both.
- Do NOT re-grep for `submitDmaRequestBatch(rdram` or the
  `LOOKUP_FUNC(` call-site count — both done, stable, not going to
  change between sessions.

## New this session: 12th crash class (SIGBUS in `composeNpcOrientationMatrix`)

s95's soak died to a SIGBUS at hold+~5s, stack:
`composeNpcOrientationMatrix` (`static_5_800AB1C8`) ←
`runHangarSelectionFrame` (`static_5_800AAD9C`) ←
`runHangarMenuFromOverlay` (`static_5_800C6854`) ← `menuOverlayInit`.
All four names confirmed real via `symbol_files/main_overlay.txt`. Not
actually new — one prior, uncatalogued occurrence exists at session 74
(`keys1` run), before the s78/s82/s84 stability gates landed; it never
recurred in the many soaks between s74 and s95, so it was never folded
into the numbered crash-class list. `thr-resume bad_total=0` both
times — rules out the s72 OSThread-UAF family for this one
specifically. **Not yet instrumented.** Per the project's usual rule
(don't dedicate a soak to a crash until its 2nd *recent* recurrence),
no standalone experiment yet — but if it recurs again in the next
soak, that's the 2nd recurrence in two sessions and it becomes the
next instrumentation target (a `ROGUESQ_LOG_*` entry-log at
`composeNpcOrientationMatrix`'s entry, same pattern as classes 9–11
in `N64Recomp/fixup_game_funcs.py`).

## The work unit

Re-run the exact same repro that s95 used, no changes needed (the
instrument is already built and committed):

```
env ROGUESQ_LOG_ANIM_CB=1 ROGUESQ_LOG_TMEM_ZERO=1 \
    ROGUESQ_LOG_ANIM_TEX_STREAM=1 ROGUESQ_LOG_HANGAR_ENTRY=1 \
    ROGUESQ_LOG_DMA=1 ROGUESQ_LOG_DMA_RING=1 ROGUESQ_LOG_DMA_CALLER=1 \
    ROGUESQ_LOG_THREAD_RESUME=0 \
    PROBE_MODE=start_only HOLD_S=30 zsh \
    scratch/s73_post_a_scene/run_mission_keys.sh s96_dmacaller2 0 12
```

Two possible outcomes, both informative:

1. **`composeNpcOrientationMatrix` recurs again** (2nd time in two
   sessions, 3rd overall counting s74). Treat it as the real blocker
   for this instrument and switch this work unit to characterizing/
   instrumenting it instead — read its source
   (`N64Recomp/RecompiledFuncs/funcs_40.c:6278`, look for an unchecked
   `MEM_W`/`MEM_BU` deref off a register that could hold a corrupt
   value, same shape as classes 9–11) and land an entry-log the same
   way `ROGUESQ_LOG_ANIM_TEX_STREAM`/`ROGUESQ_LOG_HANGAR_ENTRY` were
   added.
2. **The run survives past ~140s** (matches the "fluke" pattern of
   `frameStartReset` at s85, which never recurred). Then either:
   - `ROGUESQ_LOG_DMA_CALLER` fires — read the backtrace, it names the
     actual indirect caller of `submitDmaRequestBatch` directly. Go
     read that caller's source: the bug is almost certainly a wrong
     field offset or wrong array stride writing a name/label-table
     value into a `devAddr` field.
   - It doesn't fire, but `do_rom_read` still crashes — would be a
     genuinely new, discriminating result (contradicts s94's finding
     that the corrupted value only ever appears via the 9 unexplained
     `dma-ring-producer` firings); re-examine whether s94's read of
     the producer log was somehow specific to that one run.

Rebuild is not needed for this iteration (nothing changed since s95's
build). If you do need to rebuild for any reason, the pipeline is
`make_elf.py` → `N64Recomp` → `fixup_game_funcs.py` → `cmake --build`.

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
- Do not treat s95's 0/0 as a strike against the DMA-caller hypothesis
  — the run died before the relevant window, it's an environment miss
  not a null result. Budget rule 8 applies to genuine non-discriminating
  attempts; this doesn't count as one yet.
