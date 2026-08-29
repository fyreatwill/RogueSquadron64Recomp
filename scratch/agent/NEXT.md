# NEXT work unit — enumerate the missing retail mode writer

HYPOTHESIS-ID: m5-retail-mode-writer-boundary

## Single work unit

Use one genuinely new independent-retail boundary to attribute the caller or
descriptor source responsible for the 640→1024 mode publication. The direct
watches from Session 3107 are closed and must not be repeated. Retain the
whole-RDRAM positive control, validated Start schedule, VI trace, and title /
hangar phase coverage. Do not modify the port until retail identifies a
specific boundary.

## Competing hypotheses

- H-WrapperCaller: the 640→1024 writer is reached through an existing wrapper,
  but outside the three watched direct callsites.
- H-DescriptorProducer: the mode is selected from a descriptor/table producer
  whose publication source can be attributed independently of the wrapper.
- H-OtherCallsite: a different direct caller performs the mode publication.
- H-Unevaluable: the control or target phase is absent, or the new boundary
  watch is not live.

## Discriminating measurement

The same run must show 10,000 whole-RDRAM callbacks, the 17.2s title
`1024 @ 0x00790400` transition, the 38.4s hangar `512 @ 0x006AB400`
transition, and an execution/data row from the new boundary at the first
transition. A wrapper row with a caller identifies H-WrapperCaller; a
descriptor/table write or read paired to that transition identifies
H-DescriptorProducer; a different direct caller identifies H-OtherCallsite;
missing controls or target phases selects H-Unevaluable.

## Constraint

Before building any port instrument, obtain this retail boundary attribution;
it is currently single-source oracle evidence.
