# NEXT (s7442)
HYPOTHESIS-ID: guest-probe-gates

Class CY (CURRENT-TRUTH Next steps item 1). s7441 found the s5835 aim-thread probe running ungated on every guest sphere
test (0.096 ms/f + 20 MB stderr per run). Its siblings may share the defect.
Step 1 (offline, one pass): for every tools/apply_s5*.py and tools/apply_s6*.py that inserts code into RecompiledFuncs,
find the inserted call site in /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_*.c (grep its PATCH tag)
and classify: GATED (env latch before any work), GATED-INSIDE (call is out-of-line but returns at once), UNGATED-DIAG (work or
prints with no env), UNGATED-NEEDED (behaviour: guard/fix, keep). Write the table with a small script
(tools/s7442_probe_gate_census.py) so it re-runs.
Step 2 (same build): gate every UNGATED-DIAG site at the call site (=ROGUESQ_G1E_TRIM=0 restores), via the apply script's
idempotent upgrade step like s7441 (the fixup imports apply()). Rebuild with
DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build build -j8.
Measure: env S7431_ARM=CY zsh tools/s7433_probe_cost.sh; python3 tools/s7438_rt64_terms.py scratch/s7442 (CONTROL PASS);
python3 tools/s7441_rs64_census.py scratch/s7442; guest-function inclusive for each gated site vs scratch/s7441 (python pass in
PORTING-STATE s7441); stderr tag ranking of run.tlog vs scratch/s7441/run.tlog. Consumer control: one 150 s
tools/s7431_stderr_volume.sh arm with every gated probe's env armed; each must print.
Outcomes: H-clean (no UNGATED-DIAG site -> close CY), H-hidden (sites found, gated, samples/stderr drop), H-needed (a site
feeds a default-on fix -> document and keep).
