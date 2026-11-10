s7092 RSP vector-unit differential, built against the LIVE librecomp headers (rsp_vu.hpp, rsp_vu_impl.hpp, the DMEM
block of rsp.hpp, constants_init from rsp.cpp; all extracted by run.sh each build, so it cannot go stale).

1. Every vector load/store (LBV LDV LLV LQV LRV LSV LUV LPV LHV LFV LWV, SBV SDV SLV SQV SSV SUV SPV SHV SRV SFV) x every
   template e 0..15 x every DMEM address 0..0xFFF and a 0x40000000-aliased copy, random vector + DMEM: s6774 fast path
   (rs64_g1e_dmem=1) vs ares byte loop (=0), compares the vector register, all 4 KB of DMEM, and a guard page.
2. Scalar RSP_MEM_{W,HU,H}_LOAD / {W,H}_STORE fast vs byte loop at every address.
3. Divide unit vs an INDEPENDENT reference: cxd4 do_div + its MAME-derived div_ROM (rs64-oracle/src/mupen64plus-rsp-cxd4).
   VRCP/VRSQ all 65536 single inputs, VRCPL-without-VRCPH, and VRCPH->VRCPL / VRSQH->VRSQL over all 2^32 inputs
   (full 32-bit DivOut compared).

usage: zsh run.sh [none|ldv_lane|wrap|lqv_cnt|rcp_rom] [dp_step]   (exit 0 = no difference; ~31 s at dp_step 1)
s7092 result: none -> 8,592,990,208 compares, 0 bad. Controls: ldv_lane 2048 per LDV e (0/4/8), wrap 2 per LDV e
(address 0xFFC only), lqv_cnt 1024 LQV e=0, rcp_rom 390 divide diffs.
Not hardware: (1)/(2) prove the fast paths equal ares' loops; (3) agrees two independently written emulators.
