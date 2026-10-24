# NEXT: fold s6088 bucket-table soaks (G1c phase 2, dd3 node-cache drain)
HYPOTHESIS-ID: g1c-phase2-drawdist
Read scratch/agent/SOAK-RESULTS.md tail; `grep '\[bucketlog\]'` in soak_results/s6088_bucket_dd1_* and _dd3_*.
Positive control: dd1 log must show call=1 and call=4096k dumps (else instrument dead, redo).
H-bucket: dd3 zero-return dump shows nonempty=0/totcnt=0 (guest supply exhausted) -> raise supply (guest pool/second arena for DL nodes) not a guard.
H-leak: buckets non-empty but ret=0 -> scan/corruption; find writer.
H-drain: totcnt trends down across dd3 4096-cadence dumps vs flat at dd1 -> something consumes without reclaim; instrument reclaimDisplayListChunk 0x80007CDC next.
A NULL guard is a mitigation and needs an ORIGIN line.
