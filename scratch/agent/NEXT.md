# Next work unit: re-qualify the legacy/real M5 route

HYPOTHESIS-ID: m5-candidate-writer-census

Competing hypotheses:

- H1: the prior failure was transient and the legacy/real route again reaches
  title VI 1024 and hangar VI 512 with audio/image census rows.
- H2: the route is intermittently unstable; this repeat may fail before the
  target phases despite the same controls.
- H3: the route failure is persistent, so the candidate census must be parked
  for a route-level investigation.

Discriminator: one same-run retail positive control plus title VI 1024 and
hangar VI 512 on the paired legacy/real port. Both target phases with nonzero
audio/image row counts select H1; missing either phase or all port census rows
select H2 for one repeat and require a route-level pivot; a second pre-target
failure selects H3 and parks the candidate sweep.

Exact command:

    zsh scratch/agent/run_s4005_m5_candidate_writers.sh

This repeats the last qualified legacy/real candidate route once. Do not add
candidate fields or interpret candidate nulls in this unit.
