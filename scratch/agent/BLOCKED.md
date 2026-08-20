# Blocked: M5 port-side writer/thread census

Need from the project owner: either

- the phase-valid s2007 generated snapshot containing `funcs_*.c`, `funcs.h`,
  `recomp_overlays.inl`, and `lookup.cpp`; or
- explicit authorization to reconcile the four pending companion symbol files
  against the current generated tree.

This iteration checked every local candidate under the workspace and found
only 45-function trees. The external N64Recomp tree also has uncommitted
generated/source edits, so it is not safe to infer that any candidate is the
phase-valid witness. No authorization was present in the request or workspace
references. The s2014 retail oracle evidence does not substitute for the
port-side generated provenance.

After the artifact or authorization is supplied, verify the four files and
run the one batched, phase-gated seven-site join. The discriminating outcomes
are: same-slot `0x03` then clear with the worker edge (H1), another slot or
writer (H2), or no live slot-0 `0x03` writer during shutdown (H3).
