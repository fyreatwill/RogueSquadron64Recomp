# Next: M4 task-keyed port accumulator comparison

Work unit: capture a comparable per-task port table using the existing
`g_e9prov.task`/`[m4-accum]` and `[m4-end]` probes. The retail join now proves
that 1,222/2,083 tasks can have transient `0x8000` while all task ends are
zero; the port row cap must be removed or made per-task before H1/H2 can be
selected.

Competing hypotheses:

- H1: the port has a comparable per-task prevalence and stage/PC distribution
  of transient `0x8000`, with zero at task end; the remaining artifact is not
  an accumulator-origin mismatch.
- H2: the port has a materially different per-task prevalence or stage/source
  distribution, so the accumulator-origin boundary remains causal/open.
- H3: task IDs or phase gates fail to align the port mid-task and end-task
  rows, so no comparison is authorized.

Discriminator: one run must produce a complete task-keyed table for every
phase-qualified graphics task, including mid-task `0x8000` presence and first/
last stage plus task-end `sat8000`, with positive VI-512, whole-run, and probe
controls. H1 requires the resulting table to match the retail 1,222/2,083
prevalence and broad stage distribution; H2 requires a mismatch; H3 is any
failed control or missing task-key join.

Exact commands:

`DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build build --config Debug --target RogueSquadron64Recomp`

`env ROGUESQ_LOG_M4_ACCUM=1 ROGUESQ_LOG_M4_END=1 ROGUESQ_M4_TARGET_CAP=0 ROGUESQ_M4_SRC_CAP=0 tools/run-m4-port-task-join.sh`

`python3 tools/analyze_m4_port_task_join.py scratch/agent/m4_port_task_join/port.log`

HYPOTHESIS-ID: m4-retail-accumulator-pc-provenance
