# Next work unit: add VACC/DMEM dump to the local cxd4 RSP plugin and run the M4 retail witness

HYPOTHESIS-ID: m4-accumulator-origin-new-witness

The s5001 block was refuted (see scratch/agent/UNBLOCK.md): cxd4 is already built at
~/Documents/Tools/rs64-oracle/src/mupen64plus-rsp-cxd4/projects/unix/ and was driven to the hangar in s4514.
Steps: (1) patch cxd4 (local source, rs64-oracle tree) to dump VACC[3][8] + DMEM slice at task completion
(env-gated, e.g. RS64_RSP_DUMP=path); rebuild with the existing Makefile. (2) Positive controls first: run with
tools/oracle/rdplog via scratch/agent/s4514_cxd4.sh, confirm title VI 1024 non-empty RDP + whole-RDRAM and
VI-phase 512@0x6ab400 reached, and that the dump is non-zero for a known F5 task. (3) Only then compare against
port stage rows. Phase-gate on VI transitions; do not A/B across animating scenes. Record the rs64-oracle patch
in the ledger (it is outside this repo — save the diff under tools/oracle/ so it is not lost).
