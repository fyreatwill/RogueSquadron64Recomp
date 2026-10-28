# NEXT: phase-7 hudDisplayUpdateWorker SIGBUS (wild guest ptr 0x951335B0) on lvl7 dd4 after the 64x64 slot cap (s6591)
HYPOTHESIS-ID: g1c-dd-phase2
Hypotheses: H-dd (dd4 bundle: SPILL_HI / RAMTOP 20MB / DLPOOLX move something the HUD worker dereferences), H-retail (lvl7 phase-7 reload crashes at dd1 too), H-stale (state from the pre-reload level, e.g. freed HUD obj).
Discriminator: run scratch/agent/s6591_run.sh for ret and dd4 (new tag), same recipe; compare whether ret reaches the same phase-7 point and crashes. Also grep what writes 0x951335B0-style values (look at hudDisplayUpdateWorker+5084 guest source).
Outcomes: ret also crashes -> not dd, retail-class bug, find writer; ret clean + dd4 crashes -> bisect bundle env flags one at a time (arms concurrent).
Then: dd4 300 s holds on lvl1/5/10 to confirm the 64x64 cap regressed nothing.
