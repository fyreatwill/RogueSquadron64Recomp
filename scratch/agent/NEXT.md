# Next work unit

HYPOTHESIS-ID: mission-phase-correctness

s4735: runaway tasks' call stream is exactly periodic (period ~45 pushes) and restarts at root pc 0x180; stack is fine. Question: why does the ROOT command stream restart?

Hypotheses:
- H-root-reload: the root chunk DMA (generated L_11B4, r2 = RDRAM source) is re-issued from an earlier address (port ring / DL pointer wrap in src/main/main.cpp task submit or dpc_bridge wrap path).
- H-cyclic-data: the root DL words in RDRAM themselves contain a 0x07 branch / 0x06 back to the start (game-side), would also happen in retail.
- H-iter-restart: the self-restart label (RS64_UCODE_ENTRY) / fixup re-enters the ucode after a spurious exit mid-task with the same root_dl.

Discriminator (one build, one run): extend ROGUESQ_DLWALK to log, for tasks with fetches>=16000 and the first normal tasks, every DMA source address passed to L_11B4 at root level (depth 0) and every RSP entry (RS64_UCODE_ENTRY) with root_dl; plus dump the 64 RDRAM words at the first repeated root source. Outcomes: source repeats w/o RSP re-entry => H-root-reload or cyclic data (then check RDRAM word at the branch: 0x07 present => H-cyclic-data); re-entry count>1 => H-iter-restart.
Positive control: normal task 41 must show monotone increasing root sources and exactly 1 entry.
Run: zsh scratch/agent/s4735_run.sh (build first; patch tool: tools/patch_s4735_dlwalk.py, already applied).
