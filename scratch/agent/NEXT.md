# NEXT work unit — enumerate the missing retail mode writer through initVideoSubsystem

HYPOTHESIS-ID: m5-retail-mode-writer-boundary

## Single work unit

Use one genuinely new independent-retail boundary: watch the earlier
`initVideoSubsystem` range `0x8001A098:0x8001B7B8`, phase-gated to the live 640
origin, with exact-PC and previous-PC reporting. Attribute the caller or
descriptor source responsible for the 640→1024 publication. The direct
watches from Session 3107 and the `selectAndApplyViMode` range from Session
3111 are closed and must not be repeated. Retain the whole-RDRAM positive
control, validated Start schedule, VI trace, and title/hangar phase coverage.
Do not modify the port until retail identifies a specific boundary.

## Competing hypotheses

- H-InitWrapper: the range executes at the first transition; its exact PC and
  previous PC identify the earlier mode wrapper/caller.
- H-DescriptorProducer: the range executes at the transition with GPR or
  pointed-field values that identify the descriptor/table source.
- H-OtherCallsite: the transition occurs while this range is absent, but the
  range exposes a caller path that can be correlated to another publication
  site.
- H-Unevaluable: the control or target phase is absent, or the new boundary
  watch is not live.

## Discriminating measurement

The same run must show 10,000 whole-RDRAM callbacks, the 17.2s title
`1024 @ 0x00790400` transition, the 38.4s hangar `512 @ 0x006AB400`
transition, and a new-range execution/data row at the first transition. An
exact range PC plus `prev_pc` at that transition selects H-InitWrapper; a
descriptor/GPR row tied to the transition selects H-DescriptorProducer; a
range absence with an independently correlated publication path selects
H-OtherCallsite; missing controls or target phases selects H-Unevaluable.

## Constraint

Before building any port instrument, obtain this retail boundary attribution;
it is currently single-source oracle evidence.
