# NEXT: does a later allocateSongChannelArray store publish count 32 with base 0x801714D0

HYPOTHESIS-ID: odd-dma-alloc-pair

s4542 did not select. Both runs died in `fillSampleStreamRange+15156` (guest pc `0x8000834c`, signal 10) during VI 640, before VI 1024. `NAN_CHECK` was 0. No bad jal. That is the parked bus error, not this edge. Do not add a skip. Do not move the print. Do not re-apply `tools/apply_s4542_alloc_pair.py`. Do not regenerate `funcs_23.c` or `funcs_24.c`. Do not run `N64Recomp`.

The print control passed in both runs. These lines are not the bad-call pair. Do not read them as H-no-32. `s0` matched `count`. `n` is 1, 2, 3 with no gap. The lattice store is overwritten by the arm store before mix:

- `[s4542-alloc] n=1 count=20 s0=20 base=0x80169460`
- `[s4542-alloc] n=2 count=17 s0=17 base=0x801714D0`
- `[s4542-alloc] n=3 count=16 s0=16 base=0x8018D4A0`
- `[s4540-call] kind=arm a0=0x8018D4A0 n_all=1 s0=0 base=0x8018D4A0 count=16 sum=0x8018D4A0`

Logs: `scratch/s4542_alloc_pair_20261010-050340/run.log` and `scratch/s4542_alloc_pair_20261010-050428/run.log`.

Rebuild only if `grep -a -o s4542-alloc build/RogueSquadron64Recomp` is empty. One new run. If the death stack is `fillSampleStreamRange` before the bad jal, retry the same binary once. A second such death is not a result. Do not change the print between the two tries. A `NAN_CHECK` in `advanceVolumeFadeEnvelope` before the bad jal is not a result; retry once.

A same-count non-special base after the first printed line of that count is folded and does not get its own line. The lattice base `0x801714D0` and the arm control (count 16, base `0x8018D4A0`) are never folded. If a lattice line is missing while `n` jumps over it, that run is not a result.

Competing hypotheses, judged only if the control pair `count==16` `base==0x8018D4A0` prints before the s4540 arm line, and the bad s4540 line is again `s0=30` `base=0x801714D0` `count=32` `sum==a0`:

- H-paired-32: some printed pair has `count==32` and `base==0x801714D0` before the bad call. The named sh/sw published the pair the mix loop reads. Quote that line. Stop. Do not add a probe.
- H-unpaired: the last printed pair with `base==0x801714D0` has `count!=32`, some pair has `count==32` with a different base, and the bad call still shows base `0x801714D0` count 32. Quote both pairs. Stop. Do not add a probe.
- H-no-32: no printed pair has `count==32`, and no lattice or `count>=18` line was folded away. The halfword 32 was not this `sh`. Stop.

Positive control, same run: the `count==16` `base==0x8018D4A0` pair before `[s4540-call] kind=arm` with that same base and count; the bad call triple (s4540 bad, entry bad, `[s4534-jal] kind=bad site=800903F0` with s1 `0x801724C0` and raw34 `0x6C617465`). The pre-title count-17 lattice line will appear again. It is not the discriminator.

```
stamp=$(date +%Y%m%d-%H%M%S)
out="$(pwd)/scratch/s4543_alloc_pair_${stamp}"
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

Pass `probe.sh` an absolute `$out`. SIGKILL if the probe wrapper does not reap the game.

Outcomes:

- Controls hold and a pair is H-paired-32: selects H-paired-32. Quote `count` and `base`. Stop.
- Controls hold and the pairs are H-unpaired: selects H-unpaired. Quote both pairs. Stop.
- Controls hold and no pair has count 32: selects H-no-32. Quote the last pair whose base is `0x801714D0`. Stop.
- No control pair before the arm, or no bad call: not a result. Do not move the print.
