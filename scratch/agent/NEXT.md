# NEXT: G1e — attribute the remaining ucode accessor time to its op (s6774 follow-up)
HYPOTHESIS-ID: g1e-ucode-interp

s6774 landed aligned DMEM fast paths (LDV/SDV/LLV/SLV/LSV/SSV/LQV/SQV + scalar W/H) and a constexpr element-select table
(was a static-init guard on every vector op). Flight lvl5 dd4: -6.5% ns/cmd same-run; select 9.5% -> 0.5% of ucode samples.
A mixed-arm profile still shows rsp_vu.hpp:75 (r128::byte() const) at ~9% of ucode samples, callers unknown.
Hypotheses (one clean profile splits them):
- H-lbv: LBV<odd e> (15 sites each for e=3,5,7,9) / SBV byte ops -> one-byte ops already minimal; nothing to gain.
- H-unaligned: the fast paths miss because the ucode's LDV/LSV addresses are often unaligned or e is odd -> count misses.
- H-other-ld: LUV/LPV/LHV/LFV/SUV/SPV byte loops (LUV<0> 9 sites) -> fast-path those with a shuffle.
Work unit:
1. Run scratch/agent/s6716_bridge.zsh 5 4 prof2 (DMEM default on, no toggle) with HOLD_S=330; at ~240 s run
   `env PROF_DELAY=0 PROF_TAG=tp3 zsh scratch/s6774/prof.sh` (xctrace 20 s; edit sleep).
2. tools/xctrace_tp.py tp3.xml --thread Gfx --under factor5_ucode --dump-addrs; lldb `image lookup -v -a` per self address
   (inline chain names the RSP:: op template that inlined byte()/element()); bucket self samples by op.
3. Fast-path the top op in lib/N64ModernRuntime/librecomp/include/librecomp/rsp_vu_impl.hpp behind rs64_g1e_dmem, extend
   tools/g1e_dmem_equiv.cpp to that op (mutant positive control), export.sh + commit, same-run A/B with
   ROGUESQ_G1E_DMEM_TOGGLE=10 (tools/g1e_fast_ab.py --key dmem --phase 7).
Discriminating outcome: op-bucketed accessor samples name H-lbv (stop: accessor time is irreducible, move to G1e ladder
measurement of real game fps at dd2/dd4) vs H-unaligned / H-other-ld (land the fast path).
Soak fold due: s6774_dmem_lvl1_dd1, s6774_dmem_lvl10_dd4 (qualification of the default-on fast paths).
