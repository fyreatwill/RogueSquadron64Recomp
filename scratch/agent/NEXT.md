# Next work unit: identify the first M5 source-construction divergence

HYPOTHESIS-ID: m5-source-producer-call-context

Use the qualified s4138 retail writer table and the existing port source/DMA
rows to join the first divergent caller, argument, or source-buffer
construction boundary. Keep image, wait, cap, predicate, slot state, guest
behavior, and host writeback unchanged. Do not repeat the completed watch-index
repair or chase downstream rendering.

Competing hypotheses and discriminator:

- H-retail-port-caller-match: retail and port share the same caller/arguments
  and source buffer, so the split is after the named producer.
- H-retail-port-caller-split: the first divergent caller, source pointer, or
  length appears before the source-span store.
- H-route-invalid: either route loses a target phase or the phase-keyed join
  lacks a positive control.

The single discriminating measurement is one batch instrument that records a
phase-keyed tuple at the known retail writer family and its immediate caller
chain: writer PC, previous PC/return site, `a0`, `a1`, `a2`, source pointer,
length, destination span, and value/hash. The same run must include the
whole-RDRAM oracle control, title/hangar gates, and the qualified port image
source/DMA rows. A matching tuple selects H-retail-port-caller-match; a
qualified tuple split selects H-retail-port-caller-split; missing controls or
phases selects H-route-invalid.

Before building, read `tools/oracle/README.md` and ask ground truth with the
existing positive-control oracle route. Then batch the new oracle caller table
and port tuple fields in one Debug build/run. Exact commands should be recorded
here before execution; use SIGKILL cleanup and capture logs under a non-dot
final path.
