# NEXT work unit (s1218)

HYPOTHESIS-ID: retail-entry-capability

Work unit: select and smoke-test one state-changing debugger target at the 320
boundary, using the validated DEBUGGER=1 core and oracle write path. The
harmless control target is already proven; do not repeat it. Candidate targets
must be justified from the retail symbols/oracle state observations before
being written. Run paired undriven/control arms with whole-RDRAM, PIF, and VI
controls. Do not arm M4 target watches unless a later VI width/origin phase is
reached.

Competing hypotheses and discriminator:

- H1: a justified RAM/register target changes the retail state path and reaches
  a later VI width/origin phase.
- H2: the target is not state-changing or the run remains at width
  320/origin `0x006dd280`.
- H3: the target disrupts whole-RDRAM or PIF/VI controls, making the result
  unevaluable.

Discriminator: a later VI width/origin only in the target arm selects H1;
width 320 in both arms selects H2; missing whole-RDRAM/PIF/VI controls selects
H3. The already-demonstrated console and oracle write/read/resume controls are
the positive control for the debugger path.

Ground-truth controls are the oracle's whole-RDRAM watch, PIF trace, and VI
trace described in `tools/oracle/README.md`; use them in both arms. Read the
specific symbol/data source and `docs/F5-UCODE-REFERENCE.md` before adding a
new target instrument. Exact command form and expected outcomes must be
recorded before the oracle build.
