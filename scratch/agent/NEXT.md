# Next work unit

HYPOTHESIS-ID: m5-audio-destub

Run one complete A10 voice/list/table guard-class audit for M5 Step 8. The
previous qualified route proved the named status-03 publish/reap writer, but
did not authorize relaxing any generated pointer guard.

Competing hypotheses:

- H-A10-valid: the selected generated voice/list/table guard is reached only
  with legitimate in-range pointers; removing it preserves traversal and
  slot/task/PCM outcomes.
- H-A10-invalid: the guard suppresses a legitimate traversal; the relaxed arm
  reaches a named writer/consumer with improved work.
- H-A10-source: the guard protects a genuinely invalid pointer published by an
  identifiable writer; it must remain in force.
- H-A10-unreached: the candidate guard class is not executed in target phase,
  so changing it would be an unevaluable mitigation.

Discriminating measurement: enumerate every A10 guard site in generated
`funcs_25.c`/`funcs_26.c`, then build both guard-on and one guard-off arms in
one binary. Phase-gated rows must include guard PC/pointer, named pointer
writer PC/value, traversal/consumer entry, slot transition, completed audio
task, nonzero PCM, title/hangar VI, and the retail whole-RDRAM control. A
guard-off run with an in-range pointer, same traversal, and improved
downstream work selects H-A10-invalid. An invalid writer value selects
H-A10-source. Zero guard hits in target phase selects H-A10-unreached.
Missing controls make the result invalid; no skip is allowed without an
ORIGIN line.

Before building, read the A10 inventory and ground-truth oracle instructions,
then add both arms and the complete guard census to one batch. Exact commands:

    rg -n -C 6 'KSEG0|voice.*base|voice.*list|song.*table|return;' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_25.c /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_26.c
    cmake --build build -j8
    zsh scratch/agent/run_s4680_m5_a10_guard_audit.sh

Require title `0x00790400`, hangar `0x006AB400`, retail whole-RDRAM control,
and same-phase guard/writer/traversal/task/PCM joins before selecting an
explanation. Do not change the status wait or force-clear status. Use SIGKILL
for cleanup.
