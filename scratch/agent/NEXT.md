# NEXT work unit (s1217)

HYPOTHESIS-ID: retail-entry-capability

Work unit: audit and smoke-test one genuinely independent retail-entry
capability: the installed Mupen64Plus debugger/front-end's scripted memory or
register control. Determine whether it can pause the retail core, write a
known harmless RAM word, and resume; if so, use one phase-gated write at the
320 title boundary in a paired undriven/control run. Do not arm M4 target
watches unless a later VI width/origin phase is reached.

Competing hypotheses and discriminator:

- H1: the debugger/front-end exposes a safe, callable control that can alter
  the retail state path and reach a later VI width/origin phase.
- H2: the control surface is absent or cannot affect the state path; the run
  remains at width 320/origin `0x006dd280`.
- H3: the control disrupts whole-RDRAM or PIF/VI controls, making the result
  unevaluable.

Discriminator: first a documented debugger command/API that demonstrably writes
the harmless control word and resumes; then phase-gated VI width/origin plus
positive-control and PIF records in the same paired run. A later phase only in
the controlled arm selects H1; width 320 selects H2; missing controls selects
H3. If no callable control exists, record the capability gap and do not invent
another button schedule.

Ground-truth controls are the oracle's whole-RDRAM watch, PIF trace, and VI
trace described in `tools/oracle/README.md`; use them in both arms. Inspect
only the installed debugger/front-end sources and help first, then run one
bounded smoke from the repository root. Exact command form must be recorded
after the capability audit; no build is allowed until a positive write/resume
control is named.
