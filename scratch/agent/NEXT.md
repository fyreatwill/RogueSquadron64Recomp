# Next work unit: identify the caller route entering the zero-clear allocator

HYPOTHESIS-ID: m5-source-clear-caller-route

S3708 selected `H-ClearBranchRoute`: retail and both port arms showed the same
target-phase branch shape and allocator inputs. The clear is entered through
the stable route, but the route/selector inputs at caller `0x80091934` remain
unexplained.

Competing hypotheses:

- `H-CallerSelectorRoute`: selector/mixer state intentionally enters the clear
  allocator before payload production.
- `H-CallerStateDivergence`: the port reaches the same allocator with a
  different caller input that is not visible in the local branch table.
- `H-CallerOrdering`: the caller's preceding route publication/order differs
  from retail even though the allocator's local inputs match.

Discriminator: one phase-gated table at caller `0x80091934` and allocator
entry `0x8008F0A0`, carrying caller PC/RA, `a0/a1/a2`, selector/mixer fields,
route ordinal/row, and the last producer sequence. A retail/port-matching
selector tuple selects `H-CallerSelectorRoute`; a port-only tuple selects
`H-CallerStateDivergence`; a changed route ordinal/order before the same tuple
selects `H-CallerOrdering`. The oracle whole-RDRAM control and caller/entry
execution controls must fire; run real and silent arms in one build/run.

Build:

`DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build build --config Debug --target RogueSquadron64Recomp`

Run:

`zsh scratch/agent/run_s3708_m5_caller_route.sh`

Do not alter the clear or add a mitigation.
