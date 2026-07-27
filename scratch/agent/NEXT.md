# NEXT work unit — M3: instrument the DMA ring's producer/consumer traffic to find why `piDmaWorker` reads a corrupted `devAddr` its only known producer never wrote

s93 found the exact consumer mechanism by reading the recompiled guest
C directly (no rebuild needed for that part — it was pure source
reading). Read PORTING-STATE.md's s93 entry and its "same-session
follow-up" subsection before doing anything else; this file only has
the actionable summary.

## What's established (do not re-derive)

- `piDmaWorker` (guest `0x80005570`, `~/Documents/Tools/N64Recomp/
  RecompiledFuncs/funcs_1.c`) is a persistent consumer loop over a
  256×20B ring at guest `0x801112B0`. Its `osPiStartDma` call site has
  **literal constants `mb=0x80111270 pri=1 dir=0`** — matches all 4
  `do_rom_read` crash occurrences (s85, s91×2, s93) exactly. `devAddr`
  comes from `ring_slot+0x4`, `dramAddr` from `ring_slot+0x8`, `size`
  from `ring_slot+0x0`; `ring_slot = 0x801112B0 + (consumer_idx%256)*20`.
- `submitDmaRequestBatch` (guest `0x8000569C`) is the **only** function
  in all 45 `RecompiledFuncs/funcs_*.c` referencing the ring's base
  literal (`grep -rl "0X12B0\b"` / `grep -rl "0X26B4"` both return only
  `funcs_1.c`). Its **only static call site** is inside boot-only
  `mainBootstrapWorker` (`0x80000C68`), submitting exactly one request
  with fixed constants (`size=0xCE00 rom=0xB0101000 dram=0x80100400`)
  that **does not match** the crash's target (`dram=0x80195190
  size=0x600`).
- `ra=0x00000000` is NOT corruption evidence (s92, routine on 487+
  calls). Do NOT plan to "dump the `OSIoMesg` at `mb`" (s92,
  `osPiStartDma_recomp` never dereferences `mb`).
- `ROGUESQ_LOG_THREAD_RESUME` is a confirmed confound for `do_rom_read`
  repro attempts (s93) — the harness script
  (`scratch/s73_post_a_scene/run_mission_keys.sh`) was fixed this
  session (`export ROGUESQ_LOG_THREAD_RESUME=${ROGUESQ_LOG_THREAD_RESUME:-1}`,
  line 8) so `env ROGUESQ_LOG_THREAD_RESUME=0` now actually works —
  don't re-diagnose this if a soak behaves oddly re: confounds, just
  use `ROGUESQ_LOG_THREAD_RESUME=0` unless you specifically need it.

## The work unit

Add two new log points, gated on a new env var `ROGUESQ_LOG_DMA_RING=1`,
via `N64Recomp/fixup_game_funcs.py` (guest-code hand-edits go there,
not `lib/` — this is recompiled game code, not runtime code):

1. **Producer side** — inside `submitDmaRequestBatch`
   (`funcs_1.c` around guest `0x8000573C`, right after the 3 `MEM_W`
   writes to `ring_slot+0x0/0x4/0x8` in the loop body), log: producer
   index before increment, and the 3 values just written (size,
   devAddr, dramAddr). Expect this to fire **exactly once per run**
   with the fixed boot constants — if it fires more than once, or with
   different values, that alone falsifies "one static producer" and
   points at an indirect/`jalr` caller elsewhere (search for that next
   instead).
2. **Consumer side** — inside `piDmaWorker` (`funcs_1.c` around guest
   `0x80005608`, right after the `ring_slot+0x10` tag-byte read,
   *before* the `if (tag != 0)` branch so it logs every iteration, not
   just DMA-tagged ones), log: consumer index, the tag byte, and
   (when tag==0) the 3 values about to be forwarded to
   `osPiStartDma_recomp`. This is the same data the existing
   `[pi-start-dma]` log shows post-hoc, but from the read side, every
   iteration — the interesting new data is the *index sequence*, not
   the values themselves (already known-good/known-corrupted from the
   existing `[rom-read]`/`[pi-start-dma]` logs).

Rebuild (`make_elf.py` → `N64Recomp` → `fixup_game_funcs.py` → `cmake
--build`), then one soak reproducing `do_rom_read` (the s93 command
still applies, add the new flag):

```
env ROGUESQ_LOG_ANIM_CB=1 ROGUESQ_LOG_TMEM_ZERO=1 \
    ROGUESQ_LOG_ANIM_TEX_STREAM=1 ROGUESQ_LOG_HANGAR_ENTRY=1 \
    ROGUESQ_LOG_DMA=1 ROGUESQ_LOG_DMA_RING=1 ROGUESQ_LOG_THREAD_RESUME=0 \
    PROBE_MODE=start_only HOLD_S=30 zsh \
    scratch/s73_post_a_scene/run_mission_keys.sh s94_dmaring1 0 12
```

## What the outcomes would mean (the discriminating part)

- **Producer fires >1 time**: a second producer exists (a `jalr`
  through a function pointer this session's literal-address grep
  couldn't see, or a duplicate inlined ring-write). Next step: find
  callers of `submitDmaRequestBatch`'s address via a function-pointer
  table, or grep for a *different* register-relative pattern writing
  the same offsets.
- **Producer fires exactly once, consumer index repeats or grows past
  what one fill should allow**: consumer-side index-desync bug — a
  new, sharper root cause than "shared corruption race," and probably
  fixable at the source level once found (an off-by-something in the
  modulo-256 wrap arithmetic, or two threads racing on the same
  counter without the mutex `getDmaSlotMutex` that `submitDmaRequestBatch`
  itself calls but `piDmaWorker`'s consumer loop does NOT appear to
  call around its own index read/write — worth checking directly in
  the `funcs_1.c` source whether the consumer loop is unprotected).
- **Both sides show clean, matching 1:1 traffic with no logged write
  ever producing the corrupted value**: the stomp is external to this
  pair — strongest evidence yet for a genuine cross-subsystem memory
  race landing specifically in `0x801112B0..0x801126C0`. At that point
  the next escalation is a general RDRAM write-range watch on that
  20-byte window if the runtime has (or can cheaply add) one, rather
  than more targeted logging at this pair.

## Do not

- Do not re-read `osPiStartDma_recomp` source again — done, refuted
  (s92).
- Do not cite `ra=0x00000000` as evidence of anything — routine (s92).
- Do not re-attempt "read decomp asm for the PI manager" — confirmed
  absent from this checkout (s92), and turned out to be unnecessary
  anyway since the *recompiled* C (not decomp) already has full
  coverage (s93).
- Do not combine `ROGUESQ_LOG_THREAD_RESUME=1` with this repro without
  a specific reason — confirmed confound (s93).
- Do not re-run the "arm one flag, hope for TMEM-zero" soak — 0/7,
  stays opportunistic.
