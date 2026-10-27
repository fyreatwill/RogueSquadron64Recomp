# NEXT: qualify the actual pre-VTX byte writer
HYPOTHESIS-ID: g3c-owner-visual

s6335's exact `rsp_dmem_to_rdram` lane payload witness passed its controls but
did not match the red bytes later consumed by F5 VTX. Competing hypotheses:
H-guest-store (a phase-5 guest store writes the red bytes, but the generic
shadow's value argument is stale/zero), H-host-write-order (a different host
write or DMA populates the range after the logged store), and H-readback (the
source is red before VTX but is transformed or lost after VTX). The
discriminator is a post-store byte readback for every phase-5 guest store that
joins a phase-6 VTX lane, compared against the later VTX bytes; no matching
guest store plus a host-write overlap selects H-host-write-order, while an
exact post-store match selects H-guest-store. Missing ordinary-store, VTX,
bulk, or source-red controls invalidate the run.

Work unit: extend the regeneration-preserved F5 store shadow to read the
actual post-store 4/8-byte guest-RDRAM value for candidate phase-5 stores,
retain the writer PC/address/width and phase, and print only bounded joins to
the phase-6 VTX ranges. Keep the existing exact DMA payload witness and all
controls. Build and run the same route with a new `s6336` tag; do not add a
fade/cull mitigation.
