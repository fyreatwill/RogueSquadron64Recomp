# NEXT: does port init store anything to voice 0x801724C0

HYPOTHESIS-ID: odd-dma-port-init-voice

s4536 selected H-port-only. Do not re-run the retail watch. Do not grep for a writer. Do not add a skip. Do not re-probe `0x80090C80`. Do not re-test "did init store `0x6C617465`" as the question: s4535 already printed that word if init stored it, and it did not.

Retail, armed from title `0x00790400` through origin `0x6a2900`: the only writer of physical `0x1724F4` (voice `0x801724C0` + 0x34) is `musyxInitVoiceFromSample` `0x800921E8`. 87 stores, 23 unique values, all `0xB0xxxxxx`, scalar mismatch 0. 22 of them are at origin `0x6a2900`. `0x6C617465` is absent. The s4535 probe returns without printing a `0xB0` word (`tools/apply_s4535_voice_store.py`), so the port run did not say whether init writes this voice.

Competing hypotheses:

- H-init-skipped: port `0x800921E8` never stores to voice `0x801724C0`. Retail does, 87 times. The jal still reads `0x6C617465` because init never replaced it.
- H-overwritten: port init stores one or more `0xB0` pointers to that voice, and the jal still reads `0x6C617465`. A later store replaced the pointer. Init is not that later store.
- H-init-ascii: port init stores `0x6C617465` to that voice. This contradicts s4535 (exact-word cap unused, arm line live). Select only if the new line prints that word.

One new probe, one build, one run. Same route as `scratch/agent/soak_queue/done/s4532_fill_devaddr_20261010-023837.sh`, plus `ROGUESQ_LOG_S4534=1` and `ROGUESQ_LOG_S4535=1`. At `0x800921E8` only, count every store (`n_all`) and every store whose voice is `0x801724C0` (`n_this`). Print each target-voice store with its word, cap 16. Print `n_all` and `n_this` on the existing bad jal (`0x800903F0`, voice `0x801724C0`). Do not skip the store.

Positive control, same run: the existing `[s4535-store] kind=arm` line, or a printed `n_all>=1`, before the bad jal. A counter that stays zero with no arm line is a dead instrument.

```
# after tools/apply_s4537_init_voice.py and a rebuild of RogueSquadron64Recomp
stamp=$(date +%Y%m%d-%H%M%S)
out="scratch/s4537_init_voice_${stamp}"
mkdir -p "$out"
cd build
env \
  ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 \
  ROGUESQ_STUB_MISSING_FUNCS=1 \
  ROGUESQ_LOG_RUNNER=1 ROGUESQ_LOG_S4222=1 ROGUESQ_LOG_S4526=1 \
  ROGUESQ_LOG_DMA=1 ROGUESQ_LOG_S4298=1 \
  ROGUESQ_LOG_S4533=1 ROGUESQ_LOG_S4534=1 ROGUESQ_LOG_S4535=1 \
  ROGUESQ_LOG_S4537=1 \
  PROBE_PHASE_WIDTH=1024 PROBE_PHASE_TIMEOUT=180 \
  PROBE_KEYS_FROM_PHASE=1 PROBE_LEAVE_OK=1 \
  PROBE_KEYS="3:start 7:start 11:start 15:a 100:start 130:start" \
  zsh ../tools/probe.sh "$out" 180 2
```

Run from the repo root for the `cd build`. Do not start a second game. SIGKILL if the probe wrapper does not reap it. The edge is the `[s4534-jal] kind=bad site=800903F0` line with `s1=0x801724C0`, on the 512-to-640 transition (origin `0x006A2900`). A VI-640 death whose stack is `fillSampleStreamRange` is the parked bus error, not this edge.

Outcomes:

- Arm or `n_all>=1` printed, bad jal present, `n_this=0`: selects H-init-skipped. Retail init writes this voice; port init does not. Stop. Do not grep. Do not add a skip.
- Arm or `n_all>=1` printed, bad jal still `raw34=0x6C617465`, and at least one target-voice store is a `0xB0` pointer: selects H-overwritten. Quote the last such word and `n_this`. Stop. The replacement writer is still unnamed; do not grep for it in this session's conclusion.
- A target-voice store word is `0x6C617465`: selects H-init-ascii. Quote it. This contradicts s4535. Stop. Do not add a skip.
- No bad jal, or the run never reaches origin `0x006A2900`: not a result about this voice.
- No arm line and `n_all` absent: the instrument is dead. Not a result.
