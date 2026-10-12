# NEXT: close M4 H-source as unevaluable, or obtain a retail hangar reference
HYPOTHESIS-ID: m4-accumulator-source

The s4649 reconstruction is complete. Both controls pass; 515 complete
triplets / 4,120 lanes have zero reconstructed post-VMADH mismatches. H3 is
refuted on the port. The existing s4630 vertex comparison disfavors H2, but
the s4631 dynamic matrix capture cannot join to s4626: separate-run task IDs
and no shared frame/object/lane key. See `scratch/agent/s4649_m4_join.md`.

Next work unit: check whether a retail hangar pixel/reference artifact is now
available without a new runtime instrument. If none exists, record that
absence and close the M4 source thread; do not add another diagnostic field or
rerun the same capture. If a reference exists, use one bounded visual
comparison to decide whether the remaining port artifact is a real defect.
