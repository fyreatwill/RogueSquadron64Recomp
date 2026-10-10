# NEXT: does init's index range cover voice 0x801724C0

HYPOTHESIS-ID: odd-dma-init-index-span

s4538 selected H-index-absent. Do not re-run that census. Do not grep for the skipped index. Do not add a probe. Do not add a skip. Do not re-probe `0x80090C80`. Do not re-run the retail watch.

Port `musyxInitVoiceFromSample` `0x800921E8` stored 1183 words before the bad jal. `n_lattice=560`, `n_this=0`. The jal still reads `raw34=0x6C617465` on voice `0x801724C0`. The first lattice voice is `0x801714D0`, word `0xB03910A0`, exactly 30 slots below the target. The next three printed voices are the next slots up, at consecutive `n_all`. The other 556 lattice addresses were not printed. Log: `scratch/s4538_init_lattice_20261010-035456/run.log`.

The address is `base + index*0x88`. At the store, `ctx->r7` is still that index (`a3`) and `ctx->r4` is the voice. An existing print, gated by `ROGUESQ_LOG_INIT_VOICE_SAMPLE`, already emits both. Its label `slotBase` is the voice (`a0` after the `addu`), not the array base. There is one such print, in `funcs_24.c`, and the current binary already contains the format string. Do not rebuild unless `strings` on `build/RogueSquadron64Recomp` lacks `init-voice-slot-ptr`.

Competing hypotheses, over the lattice rows only (`(voice - 0x801724C0) mod 0x88 == 0`, with the s4538 fold: subtract 120 mod 0x88 when the voice is below the target):

- H-hole: one recovered base `B = voice - index*0x88` has `k = (0x801724C0 - B) / 0x88` inside that base's inclusive `[min index, max index]`, and no row's voice is `0x801724C0`. The caller passes a span that covers this slot and the store does not happen for that index.
- H-outside: for every lattice base, that `k` is outside `[min index, max index]`. The caller never passes this slot's index.
- H-census-wrong: a row's voice is `0x801724C0`. This contradicts s4537 and s4538. Select only if that row exists.

One run. No new counter. Same route as s4538, plus `ROGUESQ_LOG_INIT_VOICE_SAMPLE=1`. Keep `ROGUESQ_LOG_S4538=1` so the arm residue and the jal snapshot still fire.

Positive control, same run: the `[s4538-init] kind=arm` line with a residue field, before the bad jal, and `n_all>=1` on that jal. The index field is live only if the four known lattice voices `0x801714D0`, `0x80171558`, `0x801715E0`, `0x80171668` each appear as the printed voice and their `voiceIdx` values differ by `+1` in that order. If those four voices are absent from `[init-voice-slot-ptr]`, or their indices are not `+1`, the index field is not `a3`. Not a result.

```
# no rebuild if the binary already contains init-voice-slot-ptr
stamp=$(date +%Y%m%d-%H%M%S)
out="$(pwd)/scratch/s4539_init_index_${stamp}"
mkdir -p "$out"
cd build
env \
  ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 \
  ROGUESQ_STUB_MISSING_FUNCS=1 \
  ROGUESQ_LOG_RUNNER=1 ROGUESQ_LOG_S4222=1 ROGUESQ_LOG_S4526=1 \
  ROGUESQ_LOG_DMA=1 ROGUESQ_LOG_S4298=1 \
  ROGUESQ_LOG_S4533=1 ROGUESQ_LOG_S4534=1 ROGUESQ_LOG_S4535=1 \
  ROGUESQ_LOG_S4537=1 ROGUESQ_LOG_S4538=1 \
  ROGUESQ_LOG_INIT_VOICE_SAMPLE=1 \
  PROBE_PHASE_WIDTH=1024 PROBE_PHASE_TIMEOUT=180 \
  PROBE_KEYS_FROM_PHASE=1 PROBE_LEAVE_OK=1 \
  PROBE_KEYS="3:start 7:start 11:start 15:a 100:start 130:start" \
  zsh ../tools/probe.sh "$out" 180 2
```

Pass `probe.sh` an absolute `$out`. Run one game. SIGKILL if the probe wrapper does not reap it. The edge is the `[s4534-jal] kind=bad site=800903F0` line with `s1=0x801724C0`, on the 512-to-640 transition (origin `0x006A2900`). A VI-640 death whose stack is `fillSampleStreamRange` is the parked bus error, not this edge.

Offline, from `[init-voice-slot-ptr]` lines only: voice is the third field (labeled `slotBase`), index is `voiceIdx`. Lattice test as above. Recover `B` per row. Group by `B`.

Outcomes:

- Arm residue printed, the four known voices have consecutive indices, bad jal still `raw34=0x6C617465`, `n_this=0`, and some lattice base has `k` inside `[min, max]`: selects H-hole. Quote `B`, `k`, `min`, `max`, and `n` for that base. Stop. Do not grep for the branch that skipped `k`.
- Same controls, and every lattice base has `k` outside `[min, max]`: selects H-outside. Quote each base's `B`, `k`, `min`, `max`, and `n` (cap 4 bases). Stop. Do not grep.
- A row with voice `0x801724C0`: selects H-census-wrong. Quote its index and `B`. Stop.
- The four known voices do not show consecutive indices, or no `[init-voice-slot-ptr]` line exists: the index field is dead. Not a result. Do not add a replacement probe in that same run.
- No bad jal, or the run never reaches origin `0x006A2900`: not a result about this voice.
