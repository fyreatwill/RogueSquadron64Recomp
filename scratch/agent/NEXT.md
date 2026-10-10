# NEXT: is voice 0x801724C0 on init's 0x88 slot lattice

HYPOTHESIS-ID: odd-dma-init-lattice

s4537 selected H-init-skipped. Do not re-run that census. Do not grep for a writer. Do not add a skip. Do not re-probe `0x80090C80`. Do not re-run the retail watch.

Port `musyxInitVoiceFromSample` `0x800921E8` stored 1178 words before the bad jal. `n_this=0` and `n_phys=0` for voice `0x801724C0`. The jal still reads `raw34=0x6C617465`. The arm store was `0xB0373B68` on voice `0x8018D4A0`, so a `0xB0` word is visible to the counter. Log: `scratch/s4537_init_voice_20261010-034056/run.log`.

The store address is `base + index*0x88` (`sll`/`addu`/`sll`/`addu` ending at `0x800921E4`). `0x8018D4A0 - 0x801724C0 = 0x1AFE0`, and `0x1AFE0 % 0x88 = 128`, so the arm voice is a different residue class (48 vs 56). The same-edge ctl voice `0x80172328` is exactly `3*0x88` below `0x801724C0`. Two addresses do not classify the other 1177 stores.

Competing hypotheses:

- H-not-a-slot: none of the init stores are congruent to `0x801724C0` mod `0x88`. Init's addresses cannot be this voice. The jal is reading a pointer outside that lattice.
- H-index-absent: at least one init store is on that lattice, and none of them is `0x801724C0`. Init writes the array and skips this slot.
- H-census-wrong: a target-voice store appears. This contradicts s4537. Select only if `n_this>=1` or a `kind=voice` line prints.

One new probe, one build, one run. Same route as `scratch/agent/soak_queue/done/s4532_fill_devaddr_20261010-023837.sh`, plus `ROGUESQ_LOG_S4534=1`, `ROGUESQ_LOG_S4535=1`, and `ROGUESQ_LOG_S4537=1`. Keep the s4537 counter. At `0x800921E8` only, also count `n_lattice` when `(voice - 0x801724C0) % 0x88 == 0`, and print each such store with its voice and word, cap 4. On the existing bad jal (`0x800903F0`, voice `0x801724C0`), print `n_all`, `n_this`, and `n_lattice`. The arm line must include the first voice and `(voice - 0x801724C0) % 0x88`. Do not skip the store.

Positive control, same run: that arm line, with a residue field, before the bad jal. s4537's `n_all>=1` on the jal is the same-run count control. An arm line with no residue means the new classifier did not run.

```
# after tools/apply_s4538_init_lattice.py and a rebuild of RogueSquadron64Recomp
stamp=$(date +%Y%m%d-%H%M%S)
out="scratch/s4538_init_lattice_${stamp}"
mkdir -p "$out"
cd build
env \
  ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 \
  ROGUESQ_STUB_MISSING_FUNCS=1 \
  ROGUESQ_LOG_RUNNER=1 ROGUESQ_LOG_S4222=1 ROGUESQ_LOG_S4526=1 \
  ROGUESQ_LOG_DMA=1 ROGUESQ_LOG_S4298=1 \
  ROGUESQ_LOG_S4533=1 ROGUESQ_LOG_S4534=1 ROGUESQ_LOG_S4535=1 \
  ROGUESQ_LOG_S4537=1 ROGUESQ_LOG_S4538=1 \
  PROBE_PHASE_WIDTH=1024 PROBE_PHASE_TIMEOUT=180 \
  PROBE_KEYS_FROM_PHASE=1 PROBE_LEAVE_OK=1 \
  PROBE_KEYS="3:start 7:start 11:start 15:a 100:start 130:start" \
  zsh ../tools/probe.sh "$out" 180 2
```

Pass `probe.sh` an absolute `$out`. A relative path after `cd build` lands the log under `build/scratch/`. Run one game. SIGKILL if the probe wrapper does not reap it. The edge is the `[s4534-jal] kind=bad site=800903F0` line with `s1=0x801724C0`, on the 512-to-640 transition (origin `0x006A2900`). A VI-640 death whose stack is `fillSampleStreamRange` is the parked bus error, not this edge.

Outcomes:

- Arm residue printed, bad jal present, `n_all>=1`, `n_lattice=0`, `n_this=0`: selects H-not-a-slot. Init never addresses this voice's lattice. Stop. Do not grep. Do not add a skip.
- Arm residue printed, bad jal still `raw34=0x6C617465`, `n_lattice>=1`, `n_this=0`: selects H-index-absent. Quote one lattice voice, its word, and `n_lattice`. Stop. Do not grep for the skipped index.
- `n_this>=1` or a target-voice word is printed: selects H-census-wrong. Quote the word. This contradicts s4537. Stop.
- No bad jal, or the run never reaches origin `0x006A2900`: not a result about this voice.
- No arm residue and no `n_lattice` field: the instrument is dead. Not a result.
