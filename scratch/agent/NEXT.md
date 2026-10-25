# NEXT: identify the width-dependent RSP input
HYPOTHESIS-ID: g1d-widescreen

Session 6190 selected the same-source RSP/width-dependent geometry path: phase-4
central TEXRECTs used guest PC `0x8000834C`, the same alternating two-root-DL
pattern after relocation, and one coherent DPC window per task; wide emitted
about 123-127 central TEXRECTs per task versus 61-65 in control. H-secondary-
pass and a distinct menu-writer/source-PC path are ruled out for this capture.

Next work unit: add one phase-scoped trace at `rs64_run_lle_gfx` that records
the guest OSTask input identity for phase-4 gfx tasks alongside the existing
command source: task data_ptr, data_size, ucode, ucode_data, ucode_data_size,
and root DL. Build once, then run
`zsh scratch/agent/s6179_g1d_rdp_words.sh` until both arms have >=160 joins and
>=400 copy rows; snapshot the phase-4 rows before killing the wrappers.

Competing hypotheses and discriminator:

- H-width-input: control and wide use the same task/data identity except for
  the expected relocated framebuffer/root addresses; the width-dependent
  command population is produced by RSP viewport/scissor input.
- H-task-builder: wide has a distinct data_ptr/data_size/ucode-data identity
  at the same guest PC; the game-side task builder is the producer.
- H-dl-source: task identity matches, but root DL contents/source ranges differ
  in a way not explained by relocation; the DL builder/input stream is the
  producer.

A normalized same-task join (task input fields, root DL relocation delta, DPC
  range, and first wide-only central command) is the discriminator. Identical
  task inputs select H-width-input; a wide-only task identity selects
  H-task-builder; identical task inputs with an unexplained DL/source delta
  selects H-dl-source. No rendering mitigation is allowed.
