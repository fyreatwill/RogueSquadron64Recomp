# NEXT: G3c(b) spike pinned-Y: stale slot vs ucode constant
HYPOTHESIS-ID: g3c-owner-visual-b
s6368 fold: pinY=-170.25 (s15.2 -681 = 0xFD57) sits at DMEM 0x43A and 0x462 in 117/120 wedge rows; apexX control hit only 8/120.
Hypotheses: H-stale-slot (0x43A/0x462 are vertex-buffer slots never rewritten by the VTX DMA), H-ucode-const (value is a ucode/clip constant or scratch written by ucode), H-coincidence.
Discriminating build (one): in the F5 VTX handler/DMA log dmem dest+len per task, and on non-spike tasks dump the 16-bit at 0x43A/0x462 every task. Outcomes: offsets inside a VTX window and value unchanged for tasks whose window excluded them => stale slot (find which VTX/index references slot); value identical on ALL tasks incl. non-spike and outside any VTX window => ucode constant (then check if the tri path reads it: H-rsp). Control: a known VTX-window vertex word must be seen to change with its DMA.
