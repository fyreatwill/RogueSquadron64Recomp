# s7751 cxd4 gfx-task replay (independent RSP second source)

1. Capture: run the game with `ROGUESQ_S7751_SNAP=<abs dir>` plus a `ROGUESQ_POSE_FREEZE` (tools/g3_optin_pose_arms.sh).
   src/rsp/s7751_task_snap.cpp keeps the last 3 gfx tasks (16 MB RDRAM + DMEM at task begin, plus every raw RDP byte the
   ucode hands rsp_dpc_submit) and writes them as `k<k>_s<serial>.bin` after the freeze sleep. Off when unset.
2. Build: `zsh tools/s7751_cxd4_task/run.sh` (scalar C cxd4 from ~/Documents/Tools/rs64-oracle/src/mupen64plus-rsp-cxd4).
3. Replay: `tools/s7751_cxd4_task/replay <snap.bin> <out.rdp>`. Hardware boot: _VirtualToPhysicalTask on the OSTask,
   rspboot to IMEM 0, PC 0; RDP modelled as instant. cxd4 halts on its SP_STATUS poll timeout thousands of times per task;
   the harness re-kicks until BREAK (exit 0; 4 = no BREAK).
4. Compare: `python3 tools/s7751_rdp_compare.py <snap.bin> <out.rdp>`. Lists |W|<=0.01 textured tris (the s7309 pin) per stream.
   Gotcha: macOS raises SIGBUS on the PROT_NONE guard; the harness routes it to cxd4's SIGSEGV probe handler.
