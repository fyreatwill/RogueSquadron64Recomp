# NEXT: is the lvl7 CAPX=2 window overrunning the cell array? (H-overrun vs H-unbuilt)
HYPOTHESIS-ID: g1c-dd-phase2
State (s6588): fault = NULL record table at desc 0x80136DC0+4 hit by cells with idx!=0 at ptr 0x803118E2 (deterministic). tools/apply_s6588_tblnull.py has the log.
Work unit: extend the [tblnull] log with the cell-array base/length from the descriptor (fields near 0x80136DC0, see s6038 cellprobe line for field names) and window x0/w/z0/d. H-overrun: cellp outside [base, base+rows*cols*2). H-unbuilt: inside the array, so the record table is simply not built for this plane -> look at who allocates desc+4.
Outcome: overrun -> clamp window to array length for lvl3/7 under CAPX (land as opt-in default for CAPX>1) and close dd>4 for those levels; unbuilt -> trace allocation of desc+4 with a write watch.
