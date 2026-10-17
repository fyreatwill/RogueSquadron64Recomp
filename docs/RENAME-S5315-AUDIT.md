# Generated-symbol audit — Session 5315

Candidate: `freeNpcBurstSpawnerTables = 0x80041B48`

The bounded helper reported `already-synchronized` and renamed zero
references in zero files. Independent inspection found the same human name in
the companion `main_overlay.txt` map, the generated body in `funcs_9.c`, the
prototype in `funcs.h`, and the overlay record in `recomp_overlays.inl`.
`funcs_42.c` also contains a generated caller at `0x800FBA7C`. No
`func_80041B48` placeholder or conflicting fragment was found.

Conclusion: H1, already synchronized. H2 (real rename) and H3 (data/ABI
preservation) are not selected for this address. No build or soak was run.
