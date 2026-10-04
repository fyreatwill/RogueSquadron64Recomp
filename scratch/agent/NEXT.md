# Next work unit: classify the next M5 candidate-span writer classes

HYPOTHESIS-ID: m5-retail-candidate-writer-sweep

Run one corrected paired retail/port candidate-span scalar capture for
`0x80066474`, `0x80097524`, and `0x8009752C`, using
`zsh scratch/agent/run_s3883_m5_remaining_candidate_writers.sh` after changing
its output directory, target PCs, and session label to the next unit. The
retail arm must watch `0x165000..0x16C000`, phase-gate title VI 1024 and
hangar VI 512, sample post-store scalar values, and pass whole-RDRAM/title/
hangar/shutdown controls. The port arm must report ABI/image-DMA coverage or
its crash marker. Use SIGKILL and keep all logs under
`scratch/agent/soak_results/` or a session-specific scratch directory.

Competing hypotheses and discriminator:

- H1: one of these PCs writes the candidate image payload; qualified writer
  rows plus nonzero post-target samples select H1.
- H2: these PCs write zero/metadata or an unrelated value; qualified writer
  rows with zero post-target samples select H2.
- H3: none owns the candidate edge; no qualified writer rows after positive
  controls select H3.

The same-run retail table is the discriminator. The port arm is coverage
evidence only and must not be used to identify a retail producer if it crashes
before its controls.
