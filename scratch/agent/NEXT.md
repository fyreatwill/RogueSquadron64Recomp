# NEXT work unit — M3: test the shared-corruption-race hypothesis (s85, new)

s85 reproduced the s84 `frameStartReset` scenario twice
(`env PROBE_MODE=start_only HOLD_S=30 zsh scratch/s73_post_a_scene/run_mission_keys.sh <tag> 0 12`,
same script as s84). `frameStartReset` **never recurred** — both soaks
instead hit s80's parked `do_rom_read` Abort/SIGSEGV
(`osPiStartDma_recomp` → `do_dma` → `do_rom_read`, `pi.cpp:65`), with a
**garbage `physical_addr`** that differed between runs (an odd small value
→ SIGABRT on the alignment assert; `0x1C676672`, ~208 MB past `rom_base`
→ SIGSEGV reading unmapped memory). New instrument added this session:
`[rom-read] phys=... ram=... bytes=...` logged at `do_rom_read` entry,
gated on `ROGUESQ_LOG_DMA` (`lib/N64ModernRuntime`, exported + committed).

## The hypothesis

`osPiStartDma_recomp` (`lib/N64ModernRuntime/librecomp/src/pi.cpp:339-354`)
computes `physical_addr` directly from the calling thread's recompiled
register context: `devAddr = ctx->r7 | recomp::rom_base`. If `ctx` (or the
guest-stack reads at `MEM_W(0x10/0x14, ctx->r29)` feeding `dramAddr`/`size`)
belongs to a thread whose register context was corrupted by the **same**
race behind:
- s70–s72's OSThread UAF (`runAiAudioStreamPlaybackLoop` context bit-corrupt)
- s83–s84's thr-resume `bad=1` detector (`threads.cpp:198-238`, gated but
  never validated — `bad_total=0` across 3 soaks now)

...then a garbage `ctx->r7` would produce exactly this symptom, and would
also explain s84's `frameStartReset` SIGBUS (a per-frame function
dereferencing a different corrupted pointer/offset) — i.e. **one shared
race, not 3+ independent crash classes**, surfacing wherever a corrupted
read happens to be dereferenced first. That would explain why the
"dominant blocker" has changed shape every session since s83 started
peeling back the deterministic NaN assert: spline NaN → Metal SIGSEGV /
thr-resume UAF → frameStartReset SIGBUS → do_rom_read corruption.

**This is not yet proven** — it is a plausible mechanism from reading the
source, not a measurement. Do not write it into CURRENT-TRUTH as fact
until the discriminating measurement below runs.

## Discriminating measurement

1. Add a diagnostic identifying *which thread* is executing
   `osPiStartDma_recomp` when `[rom-read]` shows garbage — thread id / OSThread
   pointer / a cheap checksum of the register file (e.g. XOR of r4-r7,
   ctx pointer identity). Log unconditionally alongside the existing
   `[rom-read]` line (both gated on `ROGUESQ_LOG_DMA`; add
   `ROGUESQ_LOG_DMA=1` to the soak invocation — it is not one of
   `run_mission_keys.sh`'s always-on exports).
2. `run_mission_keys.sh` already exports `ROGUESQ_LOG_THREAD_RESUME=1` and
   `ROGUESQ_LOG_OST_WB=1` unconditionally — those logs are already in every
   soak's `run.log`. After a soak reproduces the corrupted `physical_addr`,
   grep the same `run.log` for `[thr-resume]`/`[ost-wb]` lines naming the
   **same thread id / OSThread pointer** in the ~10-50 lines immediately
   before the `[rom-read]` garbage line (same pattern as s72's "writer is
   the depth writeback immediately after last-drawn" correlation).
3. Rebuild + one soak (same script, same env, `ROGUESQ_LOG_DMA=1`):
   ```bash
   env DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer ROGUESQ_LOG_DMA=1 \
     PROBE_MODE=start_only HOLD_S=30 \
     zsh scratch/s73_post_a_scene/run_mission_keys.sh corrgate1 0 12
   ```
4. **Discriminate:**
   - The DMA-issuing thread appears in a `[thr-resume]`/`[ost-wb]` line
     shortly before the corruption, on this run AND it matches the pattern
     of a suspicious event (a swap, a writeback overlapping that thread's
     context range) → **supports** the shared-race hypothesis. Next step:
     trace that specific writer the way s72 did for the OSThread UAF (find
     the actual store that corrupts the register/stack memory).
   - No such correlation, or the DMA-issuing thread was never touched by
     a resume/writeback event near the corruption → **hypothesis
     refuted**. Fall back to characterizing `do_rom_read` corruption and
     `frameStartReset` as independent bugs; next in line is whichever
     recurs (currently do_rom_read, 2/2 this session vs. frameStartReset's
     1/3 recent soaks).

## Do not
- Do not "fix" `do_rom_read` by relaxing the alignment asserts or clamping
  `physical_addr` into range — that would silently let a ~208 MB-OOB read
  through as memory corruption instead of a loud, diagnosable crash. The
  asserts are doing their job; the bug is upstream of them.
- Do not re-attempt the thr-resume gate soak in isolation (next-steps item
  2) before item 1 — if the shared-race hypothesis is right, the same soak
  serves both purposes; if wrong, item 2 is unlikely to get further than
  the 3 prior attempts (do_rom_read keeps winning the race first).
- Budget: this is iteration 1 on the shared-race hypothesis. Per
  ITERATION.md rule 8, if 3 consecutive iterations don't produce a
  discriminating result, stop and go back to characterizing crash sites
  independently rather than continuing to chase the unifying theory.
