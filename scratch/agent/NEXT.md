# NEXT work unit — audit port callsites for the missing retail slot/status edge

HYPOTHESIS-ID: m5-step1-slot-status-source-audit

Session 3330 established that the image arm reaches hangar with valid task and
PCM controls but has no slot/status rows or named retail consumer-PC rows.
Perform one bounded static audit; do not change behavior or add a mitigation.

## Competing hypotheses

- `H-PortCallsiteAbsent`: the generated port tree has no reachable references
  to one or more retail consumer PCs, so the missing edge is dispatch/source
  coverage.
- `H-PortCallsiteGated`: the references exist, but a state/route predicate
  prevents them from executing in the qualified hangar path.
- `H-PortRangeWriterDifferent`: the port uses different callers or data
  ranges, so matching the retail PC list is the wrong discriminator.

## Discriminator

No build or runtime run. From the repository root, enumerate the generated
tree and source symbol maps for all four retail PCs and both retail watch
ranges, then inspect each containing function and its immediate callers:

    rg -n -i '80094648|8009b600|8009b85c|8009bde8|141ad0|154620' \
      RecompiledFuncs src lib docs
    rg -n 'func_80094648|func_8009B600|func_8009B85C|func_8009BDE8' \
      RecompiledFuncs src

The discriminating result is: no references selects `H-PortCallsiteAbsent`;
references with a proven blocked predicate selects `H-PortCallsiteGated`;
different concrete callers/ranges selects `H-PortRangeWriterDifferent`.
If the audit cannot classify all four PCs and both ranges, do not infer a
hypothesis; record the unresolved site list and redesign the next probe.

The Session 3330 evidence remains at
`scratch/agent/s3330_m5_slot_status_qualification.md`; no Step 3 contract
change is authorized by this static audit alone.
