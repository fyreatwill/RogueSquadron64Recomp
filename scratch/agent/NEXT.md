# NEXT work unit (s2379) — M5 A1 retail flag semantics

HYPOTHESIS-ID: m5-a1-retail-flag-semantics

## Work unit

Run one independent oracle-side execution capture around the retail
`osRecvMesg` call at `0x80001CB8..0x80001CC0`. Establish whether retail's
`$a2=0` is the actual delay-slot operand and whether the call returns through
the same successor observed in the port. Do not change the port flag or any
game behavior.

## Competing hypotheses and discriminating measurement

- H-RetailNonblocking: retail executes a zero-valued delay-slot/flag at the
  call and returns under nonblocking semantics.
- H-RetailBlockingObserved: the oracle's `$a2=0` row is not the effective
  call flag; a nearby instruction or ABI path supplies blocking semantics.
- H-RetailLabelArtifact: the watched retail PC/rows do not correspond to the
  same call ordinal as the port's generated `0x80001CB8` sequence.

The discriminator is one phase-gated oracle table containing execution rows at
`0x80001CB8`, `0x80001CBC`, and `0x80001CC0`, with `$a0/$a1/$a2/$v0`, previous
PC, and the successor/return marker. H-RetailNonblocking is selected if the
call and delay-slot rows both show `$a2=0` and the call joins the expected
successor; H-RetailBlockingObserved if the effective call path shows a
nonzero/blocking flag; H-RetailLabelArtifact if the rows cannot join by
previous-PC and successor.

## Ground truth and exact commands

Read `tools/oracle/README.md`; arm the whole-RDRAM positive control first,
then use the already-qualified target 640 origins and watch PCs. Run the oracle
from its build directory with the retail ROM, capture to a non-dot final path,
and SIGKILL only if the watchdog must terminate it. No port build is needed
unless the oracle route control fails and must be paired with an existing
same-build control.
