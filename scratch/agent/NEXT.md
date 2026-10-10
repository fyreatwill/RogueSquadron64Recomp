# NEXT: confirm the LUV/LFV/LHV unsigned-byte fix visually and triage the residual

HYPOTHESIS-ID: hangar-artifact-triage

s4518: rsp_vu_impl.hpp LFV/LHV/LUV now use unsigned DMEM bytes (RSP_MEM_BU). Entry-frame RDP diff vs retail: 588 -> 3 differing tris (34 shade words). Scripts: scratch/agent/s4518_port_rdp.sh (capture), s4518_shade_cmp.py <capture-dir> (diff), s4518_rsp_vu/run.sh (VU SIMD-vs-scalar differential).
Work unit: (a) read scratch/agent/s4518_port_rdp/f_00*.png and compare against the pre-fix s4517_port_rdp/ pngs for the hangar rim/holo colour band; (b) dump the 3 residual tris (s4518_shade_cmp.py: print word indices/values) and decide whether they are low-order shade-derivative rounding (VRCP/VMACF family) or another load/store sign issue (audit SUV/SFV/SHV/SPV/LTV/STV vs ares in the same file; same idiom class, grep RSP_MEM_B( vs RSP_MEM_BU( everywhere); (c) grep the ledger for guards added against "wild colour"/shade-sign defects and list candidates to re-evaluate.
Outcomes: pngs fixed + residual explained => close hangar-artifact-triage; residual in another idiom-class site => fix it the same way.
