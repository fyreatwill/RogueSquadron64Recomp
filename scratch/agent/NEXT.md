# NEXT: owner reports first; otherwise RSP vector-unit fast-path differential (DMEM load/store + non-elementwise ops)
HYPOTHESIS-ID: rsp-vu-fastpath-diff
Context: s7091 closed the RSP ucode fixup layer (tools/s7091_ucode_insn_census.py, 0 unexplained; regen via
tools/ucode_regen.sh). The layer under it is librecomp's RSP vector unit (lib/N64ModernRuntime/librecomp/include/
librecomp/rsp_vu_impl.hpp). tools/rsp_vu_diff (s6301) fuzzed 31 ELEMENTWISE ops SIMD vs SISD (496/496 identical).
NOT covered, but used by the compiled gfx/audio ucode: (a) the s6774 aligned DMEM fast paths
(`if (rs64_g1e_dmem && !(address & 3))` in LDV/SDV, LLV/SLV, LSV/SSV, LQV/SQV) vs their byte-loop slow paths;
(b) LBV/SBV/LRV/LUV/SUV; (c) VRCP/VRCPH/VRCPL, VMOV, VSAR (non-elementwise, state-carrying DivIn/DivOut).
Hypotheses: H-fast-ok (fast path == byte loop for every e, address, incl. 0xFFF wrap and the e<=8 boundary) vs
H-fast-bad (some (e, address) pair differs: wrong lane, wrong wrap, endian); for (c) H-div-ok vs H-div-bad
(SIMD vs SISD differ on a VRCP/VRCPH/VRCPL sequence or VSAR element).
Unit (offline, one tool, extend tools/rsp_vu_diff harness or a new tools/s7092_vu_mem_test):
1. Exhaustive for (a)/(b): every template e (0..15), every DMEM address 0..0xFFF, random vector + DMEM contents;
   run with rs64_g1e_dmem=1 and =0 and compare full vector reg + DMEM bytes. Same for stores.
2. (c): random sequences of VRCPH->VRCPL->VRCP (and VRSQ family if compiled) in SIMD vs SISD builds, compare vd +
   DivIn/DivOut/DivDP state; VSAR e=8/9/10 and others.
Controls: positive = flip one lane in a copy of a fast path (or the wrap mask) and show it is flagged; negative =
the same op run twice with the same path.
Expected outcomes: all equal (closes the VU layer for the ops the ucode uses), or a named (op, e, address) pair ->
fix in lib/ (then ./submodule-patches/export.sh + commit) + `zsh tools/ucode_regen.sh verify` + L6 boot
(`zsh scratch/s7089/run.zsh`).
