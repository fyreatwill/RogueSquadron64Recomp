# Next work unit: classify the next M5 candidate-span writer classes

HYPOTHESIS-ID: m5-retail-candidate-writer-sweep

Run one paired retail/port candidate-span scalar capture for
`0x80004E90`, `0x80004E94`, and `0x80004F2C`. The retail arm must phase-gate
the candidate span `0x165000..0x16C000` on title VI 1024 and hangar VI 512,
sample post-store scalar values, and pass the whole-RDRAM/title/hangar/
shutdown controls. The port arm must reach hangar and report image-DMA joins
with crash/abort markers. Use the existing paired candidate-span harness; if
its path is not obvious, locate it first with:

    rg -l 'candidate-span|04E90|04E94|04F2C' scratch tools

Then run the matching harness once, with both arms and all passive breadcrumb
variables enabled, capturing logs under `scratch/agent/soak_results/`.

Competing hypotheses and discriminator:

- H1: one of these PCs writes the candidate image payload; it will produce
  qualified nonzero post-target samples.
- H2: these PCs only write zero/metadata or an unrelated value; they will
  produce qualified writer rows but no nonzero candidate payload.
- H3: none of these PCs owns the candidate edge; they will produce no
  qualified candidate-span writer rows after the controls pass.

The discriminator is one same-run result table: qualified writer rows plus
nonzero post-store samples select H1; qualified rows with zero post-store
samples select H2; no qualified rows with positive controls selects H3. The
port arm is a paired coverage control, not proof of retail producer identity.

Do not run a standalone soak or a second counter build. Record the exact
controls and both arms in the next ledger entry.
