The M5 provenance work unit needs a human decision before it can run.

Needed from the project owner:

- provide the phase-valid s2007 generated tree: every `funcs_*.c` plus
  `funcs.h`, `recomp_overlays.inl`, and `lookup.cpp`; or
- explicitly authorize reconciling the four pending companion symbol files
  in `/Users/williambuckley/Documents/Tools/rogue_squadron64/symbol_files/`.

This iteration checked the current tree without modifying it. It contains 45
generated function files, the N64Recomp checkout has uncommitted generated
files, all four companion symbol files are modified, and
`scratch/agent/s2009-provenance.log` shows the provenance retry died while
waiting for VI 1024. No build or runtime behavior was changed. Once the input
arrives, run the exact commands in `scratch/agent/NEXT.md`; VI 1024 is the
required positive control before the status census.
