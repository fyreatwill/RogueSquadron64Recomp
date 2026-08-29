# NEXT work unit — statically identify a new retail VI handoff boundary

HYPOTHESIS-ID: m5-retail-video-publication-boundary

## Single work unit

Perform a bounded static audit of the code immediately following the closed
retail execution ranges through `0x8001BB6C`, using the generated function
body, its call targets, and the companion symbol/decomp names. Identify one
previously unwatched caller or handoff that can be tested independently by
the retail oracle. Do not modify runtime behavior or repeat any already
closed range/callsite.

## Competing hypotheses

- H-NewHandoff: a newly identified caller/handoff contains the 640-to-1024
  publication path.
- H-ExistingConsumer: the candidate only consumes an already-published mode;
  the writer is elsewhere.
- H-DeadOrAliased: the candidate is unreachable in the retail route or is an
  overlay-aliased duplicate and cannot be used as a new boundary.

## Discriminating measurement

The audit must produce a concrete PC/range candidate and an instruction-level
reason it can distinguish those hypotheses. The next oracle run must watch
that candidate with the whole-RDRAM positive control and VI phase controls:
transition-time execution selects H-NewHandoff; target-phase execution only
without a transition handoff selects H-ExistingConsumer; no execution with
valid controls selects H-DeadOrAliased.

## Exact commands

`rg -n "8001B7B8|8001BB6C|8001BC48|800182D8|800C2984" RecompiledFuncs src syms docs`

Then read only the bounded generated-function window and companion symbol
records around the selected target, and write the candidate plus its call
edge to `scratch/agent/s3117_m5_retail_handoff_static/AUDIT.md`.
