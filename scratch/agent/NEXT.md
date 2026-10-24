# NEXT: fold s6083_g3b_spike_ctl_l2 / _real_l2 (G3b in-flight spike lines)
HYPOTHESIS-ID: g3b-spike-lines
Instrument landed s6083: rs64_spike_scan in src/rsp/dpc_bridge.cpp (ROGUESQ_LOG_SPIKE=1, ROGUESQ_SPIKE_CTL=<px> guard override), logs `[spike]` per bad tri and `[spike-swap]` per swap.
Fold: grep -c '\[spike\]' and '\[spike-swap\]' in scratch/agent/soak_results/*s6083g3b*.log.
- ctl arm must show >0 (else scanner broken: positive control failed, fix decode).
- real arm >0 => bad vertex already in RDP stream (H-rsp): bisect the offending vector op in F5 ucode; ==0 while owner sees lines => H-rt64 (RT64 draws sane RDP cmds as spikes; look at lib/rt64 vertex clamp/near-plane path) or lines are not triangles (texrects/line prims).
- Also keep 300s holds honest: window must be unlocked.
Then G4 leftovers (l3b/l10/l5b) fold, then G5.
