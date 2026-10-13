# Next work unit

HYPOTHESIS-ID: mission-phase-correctness

s4733: port mission RDP ≈ retail on an aligned frame (see PORTING-STATE s4733). Remaining defect is renderer-side OR the port-only runaway frames (port_rdp frames 1846/1849/1851: 20K-102K tris, 100+ setcimg w512).

Work unit: explain the runaway frames. Using /tmp/s4733.pkl (regenerate with scratch/agent/s4733_cmp.py) or s4733_port_rdp/port_rdp.bin: for frame 1849, list ranges (lo,phase) that compose it, find where the repeating setcimg/DL pattern starts, and correlate with the run.log TASKSUBMIT lines (ROGUESQ_LOG_TASKSUBMIT) to name the task/DL that loops or the missing full-sync.
Hypotheses: H-nosync (a task omits OP_FULLSYNC; frames just merge), H-loop (a DL walk repeats the same sub-DL), H-dump-artifact (RS64_RDP_BIN_PORT recording duplicates ranges at wrap).
Discriminator: are the repeated setcimg blocks byte-identical copies (loop/dump dup) or progressing (nosync merging distinct frames)? Positive control: same check on a normal frame splits into 1 block.
