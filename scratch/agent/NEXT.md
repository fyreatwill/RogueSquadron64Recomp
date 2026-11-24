# NEXT (s7900)
HYPOTHESIS-ID: g3-island-b
First: `python3 tools/crash_reports.py --since 2026-11-13 | grep -v '^FOLDED' | head`, owner answers in docs/OWNER-REVIEW-QUEUE.md,
new SOAK-RESULTS lines. A crash or owner report outranks this.
State (s7899): crawl-tail island B (m11 N213) is guest INPUT drift. cxd4 replay of the port's own gfx-task snapshots is bit-identical
to our LLE on 40/40 tasks (20 in the drift window) and carries the identical retail diff, so the RSP is not the cause. The drift is
vertex-level sub-pixel (median 0.69 px, no common delta, no growth, not a permutation of retail's tris): first a large white object
entering top-right (port 6068-6080), then ~28 tiny 2-5 px white tris clustered x375-530 y204-238.
Kept: port task snapshots scratch/s7899/snap/tasks/k900_s6110..s6290.bin (RDRAM+DMEM at task begin, serial = port frame + 42),
port RDP scratch/s7899/snap/p1.bin.zst (offset retail-port -530), retail scratch/s7895/m11k/r1/retail.bin + oracle.log.
Unit:
  1. Offline: walk the F5 display list in snapshot s6150 (docs/F5-UCODE-REFERENCE.md: segment table, G_MTX/G_VTX equivalents) and find
     the matrix + vertex buffer addresses feeding the drifting tris (screen box x375-530 y204-238). Control: a vertex in the identified
     buffer, nudged in a copy of the snapshot and replayed on cxd4 (tools/s7751_cxd4_task/replay), must move exactly those tris.
  2. One retail oracle run (recipe in tools/s7849_det_pair.sh r1 step + `--pc-ram-dump <osSpTaskLoad/gfx submit PC>:<matrix/vtx range>`)
     dumping the same addresses at the same frame; diff float bits port vs retail.
  Hypotheses: H-matrix (object/camera matrix differs by LSBs: guest float path; check which PATCH code with fmadd touches it, e.g.
  s7103 camfix / s7108 camwide in setupCameraMatrices), H-vtx (vertex positions written by a CPU particle/stars routine differ: name
  the writer with XTRACE on port + --watch-write on retail), H-state (an object state field (rotation angle, scale) differs, not dt).
  Discriminator: which of matrix vs vertex bytes differ between port and retail at the same task.
