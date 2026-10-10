# NEXT: does allocateSongChannelArray publish count 32 with base 0x801714D0

HYPOTHESIS-ID: odd-dma-alloc-pair

s4541 selected H-index-30. Do not re-run the mix-index print. Do not re-read `ctx->r31` at `musyxRenderVoiceSamples`. Do not read `r5` as the scaled offset. Do not grep for a skipped init index. Do not add a skip. Do not re-probe `0x800921E8`.

Result log: `scratch/s4541_mix_index_20261010-044733/run.log`. One run. Phase 1024 at 48.5s, hangar 512 at 58.7s, origin `0x006A2900` at 169.1s. Death is the odd `do_rom_read` assertion, `last-guest-pc` `0x80001b08`. Not `fillSampleStreamRange`. No `NAN_CHECK`.

Controls, all `sum==a0`:

- `[s4540-call] kind=arm a0=0x8018D4A0 n_all=1 s0=0 base=0x8018D4A0 count=16 sum=0x8018D4A0`
- Eighteen `kind=in` lines, indices 0..17, base `0x801714D0`, `s0` equal to the index. Count is 15 on indices 0..14 and 18 on 15..17. Index 17 prints before 15 and 16.
- `[s4540-call] kind=bad a0=0x801724C0 n_all=125746 n_in=18 s0=30 base=0x801714D0 count=32 sum=0x801724C0`
- Next line is the entry bad. Next is `[s4534-jal] kind=bad site=800903F0` s1 `0x801724C0` raw34=a3=`0x6C617465`.

`0x801714D0 + 30*0x88` is `0x801724C0`. Count 32 is greater than 30, and it is late: this base was 15, then 18, before 32.

The count halfword `0x80149700` has one original store, `allocateSongChannelArray` `sh $s0` at `0x8008F0CC` (`funcs_23.c`, `MEM_H(-0X6900, ctx->r1) = ctx->r16`). `s0` was copied from `a0` at `0x8008F0B0`. The malloc pointer is stored twice after `rs_malloc` returns: `sw` at `0x8008F0E4` (`-0x6904`) and `sw` at `0x8008F0EC` (`-0x6908`, `MEM_W(-0X6908, ctx->r1) = ctx->r2`). s3602 is the static census. The jal to `rs_malloc` overwrites `r31` before the `sw`. Do not read `r31` there. The init loop after the `sw` writes `+0x0 = 0` for each slot below the reloaded count; that is not this measurement.

One new print, after the `0x8008F0EC` store, before the zeroing loop. New script `tools/apply_s4542_alloc_pair.py`. Diagnostic only. Do not skip the store or the malloc. Gate `ROGUESQ_LOG_S4539=1`. Leave the s4541 fields in place.

On each call print `[s4542-alloc] n=%u count=%u s0=%u base=0x%08X` when any of these holds: it is the first call, `(count, base)` differs from the previous printed pair, or `count>=18`. Cap 48. `count` is the halfword reloaded with `MEM_HU(-0x6900, S32(0x8015 << 16))`. `s0` is `(uint32_t)ctx->r16 & 0xFFFF` after the `sw` (callee-saved; if it disagrees with `count`, quote both and judge on `count`). `base` is `(uint32_t)ctx->r2`, the pointer just stored. A pair with `count>=18` must not be dropped by the cap; if the cap would drop one, that run is not a result.

Competing hypotheses, judged only if a control pair with `count==16` and `base==0x8018D4A0` prints before the s4540 arm line, and the bad s4540 line is again `s0=30` `base=0x801714D0` `count=32` `sum==a0`:

- H-paired-32: some printed pair has `count==32` and `base==0x801714D0` before the bad call. The named sh/sw published the pair the mix loop reads. Quote that line. Stop. Do not add a probe.
- H-unpaired: the last printed pair with `base==0x801714D0` has `count!=32`, some pair has `count==32` with a different base, and the bad call still shows base `0x801714D0` count 32. Quote both pairs. Stop. Do not add a probe.
- H-no-32: no printed pair has `count==32`, and no `count>=18` line was dropped. The halfword 32 was not this `sh`. Stop.

Positive control, same run: the `count==16` `base==0x8018D4A0` pair before `[s4540-call] kind=arm` with that same base and count; the bad call triple (s4540 bad, entry bad, `[s4534-jal] kind=bad site=800903F0` with s1 `0x801724C0` and raw34 `0x6C617465`). A VI-640 death whose stack is `fillSampleStreamRange` is not this edge; retry the same binary once. A second such death is not a result. A `NAN_CHECK` in `advanceVolumeFadeEnvelope` before the bad jal is not a result; retry once.

Rebuild `funcs_23.c` via the apply script and cmake. `funcs_24.c` is already instrumented; do not regenerate it. Do not run `N64Recomp`. Full regeneration is still unsafe.

```
python3 tools/apply_s4542_alloc_pair.py
env DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build build --target RogueSquadron64Recomp
# confirm the new binary contains s4542-alloc and s4540-call; if not, do not run
stamp=$(date +%Y%m%d-%H%M%S)
out="$(pwd)/scratch/s4542_alloc_pair_${stamp}"
mkdir -p "$out"
cd build
env \
  ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 \
  ROGUESQ_STUB_MISSING_FUNCS=1 \
  ROGUESQ_LOG_RUNNER=1 ROGUESQ_LOG_S4222=1 ROGUESQ_LOG_S4526=1 \
  ROGUESQ_LOG_DMA=1 ROGUESQ_LOG_S4298=1 \
  ROGUESQ_LOG_S4533=1 ROGUESQ_LOG_S4534=1 ROGUESQ_LOG_S4535=1 \
  ROGUESQ_LOG_S4537=1 ROGUESQ_LOG_S4538=1 \
  ROGUESQ_LOG_S4539=1 \
  PROBE_PHASE_WIDTH=1024 PROBE_PHASE_TIMEOUT=180 \
  PROBE_KEYS_FROM_PHASE=1 PROBE_LEAVE_OK=1 \
  PROBE_KEYS="3:start 7:start 11:start 15:a 100:start 130:start" \
  zsh ../tools/probe.sh "$out" 180 2
```

Pass `probe.sh` an absolute `$out`. Run one game. SIGKILL if the probe wrapper does not reap it. The edge is the bad call on the 512-to-640 transition (origin `0x006A2900`).

Outcomes:

- Controls hold and a pair is H-paired-32: selects H-paired-32. Quote `count` and `base`. Stop.
- Controls hold and the pairs are H-unpaired: selects H-unpaired. Quote both pairs. Stop.
- Controls hold and no pair has count 32: selects H-no-32. Quote the last pair whose base is `0x801714D0`. Stop.
- No control pair before the arm, or no bad call: not a result. Do not move the print.
