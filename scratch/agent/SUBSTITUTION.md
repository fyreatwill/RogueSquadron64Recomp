1. The planned M4 reconstruction and join could not be completed in this
   retry; this was a checkpoint close-out rather than a fresh experiment.
2. This iteration's filesystem check found no
   `scratch/agent/s4649_m4_reconstruct.log` and no joined ledger, while the
   existing s4626/s4628/s4630/s4631 artifacts were unchanged.
3. The falsifying experiment is the exact resume command in NEXT.md, followed
   by the single task/phase/lane join. A complete join with synthetic controls
   passing would refute this substitution and select H1, H2, or H3.
