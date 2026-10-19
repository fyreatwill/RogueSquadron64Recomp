# cxd4 normalized M4 schema

The maintained cxd4 oracle arm emits `RSM2` mid-task records and `RSD2`
completion records when its existing `RS64_RSP_MID_DUMP` and
`RS64_RSP_DUMP` variables are set. `RSM2` adds the FNV-1a hash of the live
4 KiB IMEM image and the completed task's instruction count to each selected
PC sample. `RSD2` carries the same image hash and task instruction count at
completion. The repository analyzer converts the instruction count to a
0..1000 task-progress bucket and derives the phase epoch from the VI/task
positive-control pairing.

The producer changes live in the local cxd4 checkout used by the oracle build;
this file records the wire contract so a fresh checkout can reproduce it.
Legacy `RSM1`/`RSD1` captures deliberately remain image-less and are rejected
by `tools/analyze_m4_normalized.py` as H3 rather than being assigned a guessed
image identity.
