# NEXT work unit (s983)

Perform one bounded read-only source/disassembly audit of the corrected
oracle's `r4300_pc` wrapper contract. Do not edit the recomp runtime or run a
retail soak.

HYPOTHESIS-ID: oracle-pif-r4300-pc-wrapper-state

Competing hypotheses:

- H-pif-r4300-opaque: the installed wrapper receives an object that is not
  the `r4300_core` expected by `read_with_bp_checks`, so `r4300_pc` returns an
  invalid pointer.
- H-pif-r4300-pc-layout: the opaque is a valid core object, but the compiled
  `r4300_pc` accessor/layout disagrees with the wrapper's expected return
  contract.
- H-pif-wrapper-state: `r4300_pc` and layout are coherent; a state-dependent
  owner/writer leaves the returned PC pointer invalid before the callback.

Discriminating measurement: map the concrete `r4300_pc` definition, the
`r4300_core` layout, the PIF debugger-handler opaque assignment, and the
failing wrapper instructions into one ownership chain. An opaque-type
mismatch selects H-pif-r4300-opaque; an accessor/layout mismatch selects
H-pif-r4300-pc-layout; a coherent chain with a state writer selects
H-pif-wrapper-state.

Exact commands: grep the oracle source for `r4300_pc`,
`read_with_bp_checks`, and PIF handler installation; inspect the corresponding
dylib symbols with `nm -an` and `otool -tvV`; read only bounded function
windows. The s982 evidence is in
`scratch/agent/oracle_probe_s982_fixed.log`; no retail phase result may be
inferred.
