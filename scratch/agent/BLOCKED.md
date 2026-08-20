# Blocked: s2015 port-side gate/status writer join

Need from the project owner:

- the phase-valid s2007 generated snapshot containing `funcs_*.c`, `funcs.h`,
  `recomp_overlays.inl`, and `lookup.cpp`; or
- explicit authorization to reconcile the four pending companion symbol files
  in the current external generated tree.

This iteration ran the required retail whole-RDRAM positive control and the
debugger-on Rice gate watch. The control reached its 10,000-callback cap; the
target reached VI 1024 and hangar VI 512 and reported the expected retail gate
writer PCs. That evidence closes the retail attribution branch but cannot
identify the port-side writer/thread without a phase-valid generated witness.

Once the artifact or authorization is supplied, run the single seven-site
join specified in `scratch/agent/NEXT.md`. No status, audio, spin, PI, guard,
or mitigation change is needed to unblock it.
