# NEXT: identify the other RSP-visible width input
HYPOTHESIS-ID: g1d-widescreen

Session 6192 selected neither sampled input: post-DMA `ucode_data` matched
exactly, and every callback-selected root-DL first-0x100 window was zero-filled
in both arms. The root probe fired for 26/29 unique roots, with the same
normalized relocation sequence and the required 656/615 joins and 400/400
copy rows. The extra central TEXRECTs therefore come from another RSP-visible
RDRAM read.

Next work unit: enumerate the Factor 5 main-ucode RDRAM reads reachable from
the command-source path at guest PC `0x8000834C`, then add one phase-scoped
read witness for the complete candidate table set in the fixup pipeline. The
witness must record address, access width, guest PC, task/root, and a bounded
hash/nonzero count of each candidate region, with control and wide arms in one
build/run. Keep `[g1d-task]`, `[g1d-root]`, command-source, join, and copy probes
enabled. Do not modify rendering or filter commands. Build once, then run:

    zsh scratch/agent/s6179_g1d_rdp_words.sh

The new read witness is gated by `ROGUESQ_LOG_G1D_READS` and must have a
positive control in each arm: at least 160 joins, 400 copies, and both known
root sequences. A candidate region whose normalized hash differs between arms
is the width-bearing input; if all candidates match, instrument the first
uncatalogued RDRAM read in the same ucode path rather than declaring absence.

Competing hypotheses and discriminator:

- H-table: one enumerated RDRAM table hash differs at the same task/root and
  source PC; that table is the width-bearing producer.
- H-DMEM-derived: all enumerated RDRAM table hashes match but a DMEM-derived
  address/value differs; trace the first differing derived read.
- H-unlisted: all candidate hashes match; the census is incomplete and the
  next read witness must expand to the first unlisted RDRAM read.

The discriminator is the first normalized address/hash difference paired with
the same guest source PC and DPC window. Do not add a rendering mitigation.
