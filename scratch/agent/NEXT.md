# NEXT (s7752)
HYPOTHESIS-ID: cxd4-port-rdp-residual
First: `python3 tools/crash_reports.py --since 2026-11-13 | grep -v '^FOLDED'`, then any owner report, then new SOAK-RESULTS lines.
s7751 closed the FARMAX mechanism two-source (cxd4 replay reproduces the 3 pinned dome tris exactly). Side datum to explain:
per task cxd4 and our LLE agree on 98.8% of RDP commands (difflib, scratch/s7751/snap_f0/k0_s4054.bin vs cxd4_f0_s4054.rdp).
Residual: (a) 5 tris with one differing slope word (first: cmd#83 op 0E, DxHDy fe33.. vs fc1b..), (b) ~18 port-only 0F tris,
(c) one ~850-command state+tri block emitted in a different order (insert/replace pair of equal content).
Hypotheses:
- H-snapshot: the CPU rewrites vertex/matrix/DL RDRAM while the live task runs, so the begin-snapshot is not what our RSP read.
  Discriminator: add a task-END RDRAM copy to the slot (same file, ver 2), diff begin vs end over the DL/vertex segments the
  differing commands came from; replay cxd4 on the END image too. Differences that vanish/flip with the image = H-snapshot.
- H-fixup: a deliberate ucode fixup (UCODE_CAP, s6418 far clip, spill/segment patches) changes output; the port-only tris
  appear only with the fixup on. Check the fixup list in tools/fixup_*.py touching the F5 gfx ucode against op 0F emitters.
- H-rspemu: a real LLE divergence (slope words = VMACF/VRCP path); bisect with the s6388 cxd4_vu_replay ring at the cmd#83 tri.
One capture run (L1 21:9 dd8 pose as s7751, scratch/s7751/run.zsh), everything else offline. Max 2 CPU-heavy jobs.
