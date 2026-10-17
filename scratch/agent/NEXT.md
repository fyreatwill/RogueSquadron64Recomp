# Next: M4 task-keyed retail accumulator join

Work unit: add an explicit graphics-task serial to the cxd4 `RSM1` mid-task
record, rebuild only the oracle plugin, and rerun the existing qualified
retail route. The serial must be captured at task entry and copied into every
mid-task sample until the corresponding task ends. Keep the existing RSD1
completion dump and whole-RDRAM watch as same-run positive controls.

Competing hypotheses:

- H1: task-keyed retail samples show `0x8000` in the same per-task population
  and stage/PC window as the port’s stage-10/12 transient.
- H2: task-keyed retail samples show a different per-task prevalence or PC/
  stage distribution, leaving the port-side origin unresolved.
- H3: the new task serial or RSM1/RSD1 alignment fails, so the join remains
  unevaluable and no runtime conclusion is authorized.

Discriminator: every `RSM1` record must carry a valid task serial, and the
task-keyed join must compare mid-task `0x8000` presence/first-last sample
stage against the matching RSD1 end record for the same graphics task. H1
requires valid controls plus matching per-task distributions; H2 requires
valid controls plus a distribution mismatch; H3 is selected by any failed
control or missing task-key join.

Exact commands:

`python3 tools/apply_sXXXX_cxd4_mid_task_serial.py`

`make -C ../rs64-oracle/src/mupen64plus-rsp-cxd4/projects/unix`

`tools/oracle/build/rs64_oracle --core ... --rom ... --secs 75 --vi-trace --rsp ... --video tools/oracle/rdplog/rdplog.dylib --watch-write 0x0:0x800000 --hit-cap 16 --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start`

`python3 tools/analyze_m4_task_join.py <mid.dump> <rsp.dump> <oracle.log>`

HYPOTHESIS-ID: m4-retail-accumulator-pc-provenance
