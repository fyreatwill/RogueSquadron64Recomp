# Next work unit (M5 task-contract route discriminator)

HYPOTHESIS-ID: m5-task-contract-route-discriminator

WORK UNIT: build one phase-gated task-family provenance table on the qualified
image route. Correlate every phase-5 image `M_AUDTASK` publication with its
guest task pointer, declared data/output fields, image completion, SP
completion, and PCM source row. This must be a new route discriminator for the
s4854 port-load null; do not repeat the old target control unchanged.

Competing hypotheses:

* H-task-load-live: phase-5 image tasks publish a stable task family and the
  task-field row joins image completion, SP completion, and nonzero PCM.
* H-task-load-unreached: the qualified route reaches title/hangar and PCM but
  never publishes the target task family in phase 5.
* H-task-route-invalid: the new task-family control or title/hangar/SP/PCM
  controls fail, so task-load absence is unevaluable.

DISCRIMINATING MEASUREMENT: one build/run must include the task-family table,
publication ordinal, completion/SP joins, title/hangar controls, and nonzero
PCM control. A valid phase-5 task row joined to completion and PCM selects
H-task-load-live; a positive route with zero target-family rows selects
H-task-load-unreached; missing phase or completion/PCM controls selects
H-task-route-invalid. The table must include all candidate image task fields
in one run, not one field per iteration.

Exact commands:

    DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build build --config Debug --target RogueSquadron64Recomp
    zsh scratch/agent/run_s4860_m5_task_family.sh

Before building, inspect the existing task publication/route-order helpers and
run the retail oracle with its whole-RDRAM positive control plus title/hangar
VI controls. Keep the qualified image route and use SIGKILL in the recipe.
