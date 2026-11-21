# NEXT (s7753)
HYPOTHESIS-ID: rdp-output-regression-gate
First: `python3 tools/crash_reports.py --since 2026-11-13 | grep -v '^FOLDED'`, then any owner report, then new SOAK-RESULTS lines.
s7752 closed cxd4-port-rdp-residual (CURRENT-TRUTH item 25): offline replay of our own ucode on an s7751 snap reproduces the
live RDP stream byte-for-byte. That makes a real end-to-end ucode OUTPUT regression gate possible (today's ucode gates
s7741/s7742 compare generated C text, not what the ucode emits).
Unit: tools/s7753_rdp_output_gate.py, registered in tools/s7651_gate_sweep.py like the other NEEDS-INPUT gates.
- Inputs: scratch/s7751/snap_f0/k0_s4054.bin and scratch/s7751/snap_d/k0_s4056.bin (retain; NEEDS-INPUT when absent).
- Check: `zsh tools/s7752_port_task/build.sh` if harness older than build/.../factor5_ucode_lean.cpp.o; run
  `env ROGUESQ_UCODE_CAP=1048576 ROGUESQ_G5B_TG_FIX=1 harness <snap> out` and require out == the snap's live tail (GREEN).
- Controls (--controls): TG_FIX=0 must DIFFER from the tail and have the cxd4 length (1,716,608 / 1,718,528); CAP=65536 must
  give a strict prefix (cap_fires=1). A gate that cannot see those is HOLLOW.
Expected: GREEN on the current tree. A RED after a future ucode fixup edit means the emitted RDP stream changed: either
intended (re-capture with scratch/s7751/run.zsh and say so) or a regression.
Max 2 CPU-heavy jobs. If the sweep integration takes <1 h, spend the rest on the next ladder rung (item 3c).
