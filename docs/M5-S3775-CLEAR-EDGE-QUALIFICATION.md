# M5 s3775 — clear-object and family-edge qualification remained unevaluable

The repaired image-only harness was built once and run beside the retail
oracle. The oracle whole-RDRAM positive control fired, and the image process
fired all six family-store controls. The image process did not reach either
target VI and crashed in `spTaskSchedulerThread+9556` with
`last-guest-pc=0x8000834c`.

The clear writer-setup control and all family-edge controls were absent. Thus
there is no valid `clear_obj`, `clear_span`, or `I` call-edge comparison in
this run. H1, H2, and H3 remain unevaluable; this is not evidence that the
clear/object join or I edge is absent. The new harness is retained at
`scratch/agent/run_s3774_m5_clear_edge.sh` and adds the missing writer-setup
probe to the prior image-only recipe.

No mitigation, value injection, or audio-gate change was made.
