# Next work unit: M5 Step 9h — split H-state-zero vs H-cmd-skip for the zero audio-ucode output

HYPOTHESIS-ID: m5-audio-destub-sequence

s4209: RDRAM->DMEM reads are nonzero and exact in phases 4/5; DMEM->RDRAM writes are all-zero after early phase 4 (3 writes/task: w0 len 768, w1 len 408, ...). Live-tree patches only (tools/apply_s4208_dma_ring.py, apply_s4209_dma_read_ring.py); never regen.

Hypotheses:
- H-state-zero: mix executes but volume/ADPCM/loop state in DMEM is zero (state read from +0x2C/saved state arrives zero or is masked).
- H-cmd-skip: ucode command dispatch skips the mix/ADPCM ops (cmdlist op histogram differs from phase 3).

Discriminator (one build, one run): per task log per-write-index (len, nz) and a histogram of executed command opcodes (hook the ucode dispatch loop in build/factor5_ucode or rsp.cpp audio path) for phase 3 vs 5, plus DMEM nz hash of the mix buffers at exit. Positive control: phase 3 has nonzero writes.
Outcomes: op histogram equal and writes zero => H-state-zero (log state words read); histogram lacks mix/ADPCM ops in phase 5 => H-cmd-skip (find which op and why the cmd list differs).
