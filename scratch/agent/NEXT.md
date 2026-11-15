# NEXT (s7373)
HYPOTHESIS-ID: tsan-mission-coverage

s7372: TSan+coverage arm (tools/build_tsan.sh COV=1, build_tsan_cov/) + tools/s7372_aq_runtime_cross.py. Mission run c1
(scratch/s7372/c1, ~405 mission frames): 17 AQ rows exercised in mission + 8 boot-only, 0 races on own access;
73 rows never executed (list: `grep ' EXEC 0 ' scratch/s7372/cross_c1_full.txt`).

Work unit (OFFLINE, no game run): classify the GATE of each of the 73 unexecuted rows from source:
  G-env    the function is reached only under a ROGUESQ_* env var / diag flag that the c1 recipe did not set
  G-dtor   destructor / shutdown path (SIGKILL never runs it)
  G-const  std::array size() / static decl rows (no runtime access to cover)
  G-branch default path, function ran but the row's unlocked line is in a branch not taken (e.g. s6702_release_locked:3934)
  G-route  default-on path the c1 route never reached (hangar abort, level select, audio join...)
Tool: extend tools/s7372_aq_runtime_cross.py with a --gates TSV or write tools/s7373_aq_gate_table.py; output a table.
Hypotheses: H-diag (>= 90% are G-env/G-dtor/G-const -> AQ runtime half CLOSED, the static verdicts stand for the rest),
H-route (>= 1 G-route/G-branch row on a default-on path -> one TSan+cov run on a route that reaches it, e.g. the s7331
abort route or ROGUESQ_SPILL_FORCE for the tagged-spill branch). Positive control: the gate classifier must call the
TextureCache destructor row G-dtor and the presents/workloads size() rows G-const.
If the table closes AQ: CURRENT-TRUTH item 16 / 17 (next idiom-class audit or the 3c ladder).
