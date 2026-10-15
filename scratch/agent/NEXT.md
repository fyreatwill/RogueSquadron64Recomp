# Next work unit

HYPOTHESIS-ID: m5-aux-store-ab

s4944 showed the image and silent arms emit structurally identical aux-store rows but the silent arm runs ~11x more
mission synth frames per VI (~15.5k vs ~1.3k rows at VI #9600 each). Discriminate WHY: (H-ai-drain-pacing) image
arm's `musyxSynthFrame` rate is gated by AI DMA drain; (H-log-budget) the witness has a per-phase row cap hit
differently; (H-slow-synth) image synth is CPU-bound under 2 concurrent instances.
Boring check FIRST: `grep -n s4938 tools/fixup_game_funcs.py` for the witness budget. Then re-run
`scratch/agent/s4944_aux_ab.sh` with a per-origin count of `musyxSynthFrame` entries and AI-drain events per VI
(one build). Positive control: title rows must equal the 256 cap. Also fix stale `m5-task-contract` grep (0 in both).
