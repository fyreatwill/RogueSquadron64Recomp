# Next work unit: classify the next M5 candidate-span writer classes

HYPOTHESIS-ID: m5-retail-candidate-writer-sweep

Create the next corrected paired retail/port candidate-span scalar-capture
runner by copying the completed `run_s3888_m5_remaining_candidate_writers.sh`
recipe and replacing its three target PCs with
`0x80003A48`, `0x80003A50`, and `0x80003AFC`; then run it once:

    zsh scratch/agent/run_s3889_m5_remaining_candidate_writers.sh

The runner must write only to `scratch/agent/s3889_m5_remaining_candidate_writers/`
and watch those three PCs. Retail must pass whole-RDRAM, title VI 1024,
hangar VI 512, and shutdown controls before classifying the target PCs. The
port arm must report ABI/image-DMA coverage or its crash marker. Use SIGKILL
through the runner and keep all logs under the session-specific scratch
directory.

Competing hypotheses and the discriminating measurement:

- H1: one PC writes the candidate image payload. Qualified writer rows plus
  nonzero post-target samples select H1.
- H2: a PC writes zero/metadata or an unrelated value. Qualified writer rows
  with zero post-target samples select H2.
- H3: none owns the candidate edge. No qualified writer rows after the
  positive controls select H3.

The same-run retail table is the discriminator. The port arm is coverage
evidence only and must not identify a retail producer if it misses its
controls. The completed s3888 arm passed controls, gave no qualified writer
row or post-target sample for any of the three PCs, and reached 2,992 port
image-DMA joins with no crash/abort.
