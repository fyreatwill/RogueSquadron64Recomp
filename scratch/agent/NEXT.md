# NEXT: who calls musyxRenderVoiceSamples with voice 0x801724C0

HYPOTHESIS-ID: odd-dma-render-caller

s4539 selected H-outside. Do not re-run the index span. Do not grep for a skipped init index. Do not re-probe `0x800921E8`. Do not add a skip. Do not re-run the retail watch.

Log: `scratch/s4539_init_index_20261010-041352/run.log`. Init base `B=0x801714D0` stored indices exactly 0..17 (n=565). k=30 is outside. `B + 30*0x88` is voice `0x801724C0`. The bad jal still has raw34=a3=`0x6C617465`. The ctl row immediately before it is s1=`0x80172328`, which is `B + 27*0x88`, also outside 0..17, raw34=`0x00C80000`.

In `musyxRenderVoiceSamples` (`funcs_24.c`, entry `0x8008FFAC`) the only write of s1 before the jal at `0x800903F0` is `addu $s1, $a0, $zero` at `0x8008FFB4`. The bad s1 is the entry a0. ra is still the caller there: the two instructions above it are `addiu sp, -0x60` and `sw s1`. Nothing prints that ra today.

One new probe, one rebuild, one run. Insert it in `tools/apply_s4539_render_entry.py` immediately after that `addu`, gated by `ROGUESQ_LOG_S4539=1`. Diagnostic only. Do not skip the call. Do not touch the four jals.

At entry, a0 is `ctx->r4` and ra is `ctx->r31`. Base `B=0x801714D0`, stride `0x88`. In-range: `(a0 - B)` is divisible by the stride and the quotient is in 0..17. Keep a set of in-range ras, capped at 32; a 33rd distinct ra sets `overflow=1` and is not stored.

Prints, all flushed:

- First entry, any a0: `[s4539-entry] kind=arm a0=0x%08X ra=0x%08X`.
- Each new in-range ra, up to 32: `[s4539-entry] kind=in a0=0x%08X ra=0x%08X index=%d n_in=%u`.
- a0 `0x801724C0`, cap 4: `[s4539-entry] kind=bad a0=0x%08X ra=0x%08X in_match=%d n_in=%u overflow=%d`. `in_match` is 1 when ra is already in the set.

Competing hypotheses:

- H-one-caller: `overflow=0`, `n_in>=1`, `in_match=1`. The caller that passes an initialized slot also passes index 30.
- H-split-caller: `overflow=0`, `n_in>=1`, `in_match=0`. No initialized-slot entry used the bad ra.
- H-census-wrong: an in-range row has a0 `0x801724C0`. That contradicts s4539. Select only if the quotient is in 0..17.

Positive control, same run: the arm line, with ra's top byte `0x80`, before the bad entry; at least one `kind=in` with index in 0..17 before that bad entry; and the existing `[s4534-jal] kind=bad site=800903F0` with s1 `0x801724C0` and raw34 `0x6C617465` after it. A VI-640 death whose stack is `fillSampleStreamRange` is not this edge. A death in `advanceVolumeFadeEnvelope`'s `NAN_CHECK` before the bad jal is not a result; retry the same binary once. A second such death is still not a result. Do not chase the NaN.

Rebuild only `funcs_24.c` via the apply script and cmake. Do not run `N64Recomp`. Full regeneration is still unsafe.

```
python3 tools/apply_s4539_render_entry.py
env DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build build --target RogueSquadron64Recomp
# confirm the new binary contains s4539-entry; if not, do not run
stamp=$(date +%Y%m%d-%H%M%S)
out="$(pwd)/scratch/s4540_render_entry_${stamp}"
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

Pass `probe.sh` an absolute `$out`. Run one game. SIGKILL if the probe wrapper does not reap it. The edge is the `[s4534-jal] kind=bad site=800903F0` line on the 512-to-640 transition (origin `0x006A2900`).

Outcomes:

- Controls hold, `overflow=0`, `in_match=1`: selects H-one-caller. Quote bad ra, the in-range a0 and index that shared it, and `n_in`. Name the function that contains ra if a symbol already maps it. Stop. Do not add a probe.
- Controls hold, `overflow=0`, `in_match=0`: selects H-split-caller. Quote the bad ra and the in-range ra set (cap 8). Stop. Do not add a probe.
- An in-range row whose a0 is `0x801724C0`: selects H-census-wrong. Quote its index. Stop.
- `overflow=1`, or no `kind=in` before the bad entry, or no bad entry, or no bad jal: not a result. Do not raise the cap in that same run.
