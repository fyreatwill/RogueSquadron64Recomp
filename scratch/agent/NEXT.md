# Next: M4 accumulator boundary revisit

Work unit: design one complete task-keyed sampler at a shared,
retail-comparable instruction/step boundary for the transient `0x8000` VACC
state. Do not add a mitigation or build until the sampler has a non-runtime
ground-truth counterpart and a positive control.

Competing hypotheses and discriminator:

- H1: the task-keyed sampler can align the port and retail at a comparable
  boundary; the stage-10/11 versus stage-12/13 `0x8000` difference is real and
  attributable.
- H2: the sampler can align tasks but retail and port differ in accumulator
  origin or lifetime; the current stage-hook comparison is misleading.
- H3: no shared boundary can be established with positive controls; keep M4
  parked and do not add a mitigation.

Discriminating measurement: for the same task key and step/PC boundary, record
the first writer, last writer, and task-end value of the VACC lane in both the
port and the independent retail oracle. The three possible outcomes above must
select attribution, divergence, or unevaluable status respectively.

Ground-truth prerequisite: read `tools/oracle/README.md` and identify the
retail watch/PC attribution needed before writing the port instrument. Also
read `docs/F5-UCODE-REFERENCE.md` if the boundary touches a Factor 5 task.

HYPOTHESIS-ID: m4-accumulator-boundary
