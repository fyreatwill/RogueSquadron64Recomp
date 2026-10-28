# NEXT: why does prepending extra DL chunks at the flight reinit fault even at px1?
HYPOTHESIS-ID: g1c-dd-phase2
Facts (s6564): ROGUESQ_DD_REINITX=2 (+ROGUESQ_DLPOOLX_MB=4) -> `[reinitx] len 2909 -> 5853` then the 0x380000004 NULL-node SIGBUS ~105 log lines later at px1 (c3) and px2 (r4, 6/6). Unpatched px1 never faults. Boot-reinit scaling faulted at begin 1.
Hypotheses:
- H-P1: chunks at >= 0x80800000 (arena 0x80C00000-0x81000000) break the game's/our pop path (range guard, rdram backing, or mirror) — placement is the fault.
- H-P2: prepend layout (new chunks in FRONT, back-pointer +4 writes into old head) breaks an invariant (e.g. begin expects head's +4 == 0 or an allocator-owned tail).
- H-P3: the extra chunks are fine but the 0x80018094 store hook/census (rs64_s6287) rewrote the head after my edit.
Discriminator (one build, arms in one iteration): ROGUESQ_DD_REINITX_MODE=head|tail|selfonly. tail = append extra chunks after the original last chunk (head unchanged); selfonly = walk and re-link the original 2909 chunks through my loop with ZERO extra (control for H-P2/H-P3 layout code); plus k=1.1 (+291 chunks, MB=1) dose arm. All at px1 first. Fault-free tail => H-P2; faults in every arm incl. selfonly => H-P3 or code bug; only >=0x80800000 arms fault => H-P1. Positive control: [reinitx] len line and len after via host walk without the 0x80800000 cap.
Then, only if some arm is fault-free: px2 x3 with it. H-D2 verdict: no NULL-node + no empty_b => supply-limited.
Note: s6553_run.sh logs under scratch/agent/m6/g1_lvl1s6553_dd4_pxN_<arm>/; background cap is 600 s, so run at most 2 arms per background job.
