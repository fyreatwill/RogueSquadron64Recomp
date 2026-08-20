# Unblock result (s2016)

Route 1 — refuted the dependency as reasoned.

## Claim tested

The prior block said the port-side seven-site census could not run until a
phase-valid s2007 generated snapshot was supplied, or the owner authorized
reconciling four pending companion symbol files.

## Evidence

The N64Recomp README/source was read first. The current generated output already
contains the complete s2006/s2007/s2008 diagnostic path, including the seven
direct status stores and the named `funcs.h`, `recomp_overlays.inl`, and
`lookup.cpp` companion artifacts. The existing binary contains the s2008
markers, so no companion-file reconciliation or new generated snapshot was
needed for this observation.

One fresh, phase-gated run used the existing current binary and eleven-Start
recipe with `ROGUESQ_LOG_S2008_STATUS_WRITERS=1`. It reached:

- VI 1024 at 17.5s, title origin `0x00790400`;
- hangar VI 512 at 29.4s, origin `0x006AB400`;
- status writer `0x8009B2C4`, slot 0, `0x01 -> 0x00`, during shutdown call 3;
- shutdown call 3 entry/exit on host thread 3.

The run later crashed at the already-known guest-PC boundary `0x8000B650`
after the phase controls, before the worker-side positive control became live.
That crash leaves H1/H2/H3 open; it does not invalidate the phase-validity
observation. Static generated-source inspection and the dynamic phase/status
capture are independent evidence lines.

## Conclusion

The exact s2007 snapshot and owner authorization are not prerequisites for
running the port-side census. The block is false as reasoned. The next unit is
the same seven-site join on the current 45-file tree, with a live worker
positive control required before interpreting a null.
