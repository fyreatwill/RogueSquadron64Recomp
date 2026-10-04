# Next work unit: classify the next M5 candidate-span writer classes

HYPOTHESIS-ID: m5-retail-candidate-writer-sweep

Create the next corrected paired retail/port candidate-span scalar-capture
runner by copying the completed `run_s3889_m5_remaining_candidate_writers.sh`
recipe and replacing its three target PCs with
`0x80003B98`, `0x800044C8`, and `0x80004AB0`; then run it once:

    zsh scratch/agent/run_s3890_m5_remaining_candidate_writers.sh

The runner must write only to `scratch/agent/s3890_m5_remaining_candidate_writers/`
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
controls. The completed s3889 arm passed controls; all three PCs had
qualified candidate-span writer rows but zero post-target samples, and the
port crashed before ABI/image-DMA controls.
