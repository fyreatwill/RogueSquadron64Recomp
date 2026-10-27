# NEXT: explain the impossible EBC writer delta before rerunning
HYPOTHESIS-ID: g1c-dd8-limit

The s6502 single-snapshot run passed both controls, but the 0x80042EBC count
delta underflowed while 0x80042DB4 had positive deltas. The guest thread IDs
matched, so the result cannot yet name a writer. Do one offline source audit
before another build: enumerate every declaration, assignment, and call of
`s6500_wcount[2]`, `s6501_post_wcount[2]`, and `s6500_note_writer(0x80042EBCu)`
in the generated funcs_9.c and all three fixup scripts, then inspect the exact
control-flow placement around 0x80042EBC.

Competing hypotheses and discriminator:

- H-duplicate: a second declaration or stale generated fragment resets/aliases
  the EBC counter. A complete assignment census finds one or more reset sites.
- H-uninstrumented: EBC is written through an uninstrumented path, so the
  snapshot and current counter are from different writer populations. The
  source audit finds a matching table-byte store without s6500_note_writer.
- H-boundary: the snapshot is taken in a different call/phase than the stream
  row despite equal guest IDs. The exact CFG and sequence placement show a
  call boundary between the post snapshot and return.

The audit selects one of these; only then build one regeneration-safe fix and
rerun `zsh scratch/agent/s6492_forface.sh`, requiring dd1 nonempty and dd4
EMPTY controls. No soak is justified before the audit resolves the underflow.
