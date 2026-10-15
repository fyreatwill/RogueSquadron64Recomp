# UNBLOCK s5002 — route 1 (refuted)

Block claim: a cxd4/parallel-rsp LLE RSP plugin must be installed (human decision) for M4 accumulator work.
Refutation: no install needed. A built cxd4 LLE RSP already exists in the project-maintained source tree:
  ~/Documents/Tools/rs64-oracle/src/mupen64plus-rsp-cxd4/projects/unix/mupen64plus-rsp-cxd4.dylib (built Aug 10)
It was used in s4514 (scratch/agent/s4514_cxd4.sh, tools/oracle/rdplog) and reached hangar 0x6ab400 (PORTING-STATE ~152404).
Accumulator state is a plain global in that source: `i16 VACC[3][N]` (vu/vu.h:62; ACC_L/M/H macros). DMEM is
handed to the plugin via RSP_INFO. So "expose DMEM/accumulator reads" is a small source patch to a tree we own
(build-from-local-source, not an internet install), not a human decision.
Not done this iteration: the patch/build/run itself (that is the next work unit, see NEXT.md).
Caveat: s4514 showed cxd4+Rice stalls at VI 640 without tools/oracle/rdplog (raises MI_INTR_DP); use the rdplog video plugin.
