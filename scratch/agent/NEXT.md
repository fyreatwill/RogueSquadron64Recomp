# NEXT: what index and bound make musyxMixActiveVoices pass 0x801724C0

HYPOTHESIS-ID: odd-dma-mix-index

s4540 selected H-one-caller. Do not re-read `ctx->r31`. Do not re-run the entry-only probe. Do not re-run the index span. Do not grep for a skipped init index. Do not add a skip. Do not re-probe `0x800921E8`.

Result log: `scratch/s4540_render_caller_retry_20261010-043550/run.log`. `musyxMixActiveVoices` jal `0x80090F00` is the only call of `musyxRenderVoiceSamples`. Its arm is a0 `0x8018D4A0` (`n_all=1`), immediately followed by the entry arm with the same a0 and `ra=0`. It then passes every index 0..17 of base `0x801714D0` (`n_in=18`; index 17 is printed before 15 and 16, and the set is complete). The bad line is `[s4540-call] kind=bad a0=0x801724C0 n_all=125625 n_in=18`, the next line is the entry bad with `ra=0`, and the next is `[s4534-jal] kind=bad site=800903F0` with raw34=a3=`0x6C617465`. Death is the odd `do_rom_read` assertion, `last-guest-pc` `0x80001b08`, after origin `0x006A2900`. Not `fillSampleStreamRange`.

The loop, static, not yet measured at the bad call:

- `s0` is zeroed at `0x80090E2C` and incremented at `0x80090F48`, after the jal.
- Head `0x80090E70` uses `s0 & 0xFFFF` as the index. Scale to `index*0x88` is `0x80090E7C..0x80090E84`.
- Base is reloaded at `0x80090EBC`: `lw` from `0x801496F8` (`0x80150000-0x6908`). `a0 = base + a1` at `0x80090EC0`.
- The jal is skipped when byte 0 of that voice is 0 (`0x80090EC8`).
- The bound is the halfword at `0x80149700` (`0x80150000-0x6900`), compared at `0x80090F44..0x80090F54`: continue while `(s0 & 0xFFFF) < count`.

At the jal, `s0` is still the index (`ctx->r16`). `a1` (`ctx->r5`) has been overwritten by the delay-slot-adjacent `andi` at `0x80090ECC`, so do not read `r5` as the scaled offset. Read the base from memory.

One new field on the existing bad call, plus the same fields on the arm and on the first in-range call. Extend `rs64_s4540_call` in `tools/apply_s4540_render_caller.py` (the script is already applied; a second script `tools/apply_s4541_mix_index.py` should patch the existing bad/arm/in prints, or edit the helper in place and keep it idempotent). Diagnostic only. Do not skip the call. Gate remains `ROGUESQ_LOG_S4539=1`.

On arm, on the first `kind=in`, and on `kind=bad`, add `s0=%u base=0x%08X count=%u sum=0x%08X`. `s0` is `(uint32_t)ctx->r16 & 0xFFFF`. `base` is the word at `0x801496F8`. `count` is the halfword at `0x80149700`. `sum` is `base + s0*0x88` computed in uint32. The function needs `rdram` only if `MEM_W` requires it; use the same absolute form as the recompiled `lw` (`MEM_W(-0x6908, S32(0x8015 << 16))` and `MEM_HU(-0x6900, S32(0x8015 << 16))`).

Competing hypotheses, judged on the bad line, and only if arm and the first in-range line both have `sum == a0`:

- H-index-30: `s0==30`, `base==0x801714D0`, `count>30`. The bound admits slot 30 of the init lattice. Init's 0..17 is not this loop's span.
- H-other-base: `base!=0x801714D0` and `sum==a0`. The voice is a slot of a different array. Quote `base`, `s0`, and `count`.
- H-formula-wrong: `sum!=a0` on the bad line. `s0` at the jal is not the index the `addu` used. Stop. Do not guess another register.

Positive control, same run: arm line before the bad line, a0 top byte `0x80`, `base` top byte `0x80`, `count>0`, and `sum==a0`; a `kind=in` line with index in 0..17, `sum==a0`, before the bad line; the bad call, the entry bad, and `[s4534-jal] kind=bad site=800903F0` with s1 `0x801724C0` and raw34 `0x6C617465`. A VI-640 death whose stack is `fillSampleStreamRange` is not this edge; retry the same binary once. A second such death is not a result. A `NAN_CHECK` in `advanceVolumeFadeEnvelope` before the bad jal is not a result; retry once.

Rebuild only `funcs_24.c` via the apply script and cmake. Do not run `N64Recomp`. Full regeneration is still unsafe.

```
python3 tools/apply_s4541_mix_index.py
env DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build build --target RogueSquadron64Recomp
# confirm the new binary contains s4540-call and the new field name; if not, do not run
stamp=$(date +%Y%m%d-%H%M%S)
out="$(pwd)/scratch/s4541_mix_index_${stamp}"
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

- Controls hold and the bad line is H-index-30: selects H-index-30. Quote `s0`, `base`, `count`. Stop. Do not add a probe.
- Controls hold and the bad line is H-other-base: selects H-other-base. Quote `s0`, `base`, `count`, `sum`. Stop. Do not add a probe.
- Bad line `sum!=a0`: selects H-formula-wrong. Quote the four numbers. Stop.
- No bad call, or arm `sum!=a0`, or no in-range line before the bad call: not a result. Do not change the formula in that same run.
