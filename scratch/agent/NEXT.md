# Next work unit: positive control for the allocateDisplayListBuffer guard census, then close the patcheslib-shadowed thread
HYPOTHESIS-ID: patcheslib-shadowed
s5378: census all-zero through mission in one run (see PORTING-STATE s5378) but the guard branches have no same-run positive control.
Plan: (1) add an env-gated forced g2bad/g3bad (or poisoned slot) in tools/fixup_* so the [a5370] row must read nonzero; (2) enqueue one soak with the control plus the normal arm in scratch/agent/soak_queue; (3) control fires and normal arm stays 0 -> record guards inert-on-route and close the thread.
Outcomes: control nonzero + normal zero -> close; control zero -> census instrument broken, fix it.
