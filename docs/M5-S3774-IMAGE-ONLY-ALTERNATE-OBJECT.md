# M5 s3774 — image-only alternate-object boundary

The existing Debug build and `run_s3773_m5_image_only.sh` were run on
2026-10-02 with the retail oracle in parallel. The oracle whole-RDRAM
positive control fired (`1`), the image arm reached title (`1024`, 5,968
phase rows) and hangar (`512`, 1,022 phase rows), and all six family-store
controls fired.

The image arm emitted 256 S stores and 256 L stores in each target phase.
Every recorded S/L destination was outside the clear-associated target
buffer; all rows reported `target=0`, `clear_obj=0`, and `clear_span=0`.
The I family emitted 256 title rows and no hangar rows. There were no
family-edge rows in this recipe, so the I call-edge arm was not measured.
The clear-associated writer setup also did not qualify a clear object
(`clear_obj=0`, `alloc_len=0` in its target-phase rows).

This selects the image-only I hangar-edge absence for this capture. It does
not distinguish a legitimate alternate object from a route/object mismatch:
the clear-object join was unevaluable, not false. The missing silent arm
also prevents any image-versus-silent claim. No mitigation or value
injection was added.

Evidence: `scratch/agent/s3773_m5_image_only/summary.txt`, `image.log`, and
`oracle.log`.
