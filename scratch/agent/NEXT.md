# NEXT: fold s6367 spike-dmem soak (G3c b)
HYPOTHESIS-ID: g3c-owner-visual-b
Soak s6367_spike_dmem queued (lvl2, ROGUESQ_LOG_SPIKE=1 ROGUESQ_SPIKE_DMEM=1). Read [spike-dmem] lines in its log (scratch/agent/m6/g1_lvl2s6367spikedmem/run.log or soak_results).
Per bad tri it logs DMEM hit counts/offsets for pinned Y, apex Y, apex X in s15.2 and s15.16 BE encodings.
Control: apexY/apexX should hit in some encoding (else format guess wrong -> inspect DMEM vertex layout via docs/F5-UCODE-REFERENCE.md, try other encodings).
Discriminator: pinY hits at a constant DMEM offset across swaps while apex hits move => stale slot (note offset; compare with VTX-loaded window). pinY with 0 hits while controls hit => value is computed/not resident (H-clip-const).
Note DMEM is read at submit time, may not equal state during the tri emit.
