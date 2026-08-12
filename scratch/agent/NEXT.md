# NEXT work unit

HYPOTHESIS-ID: m3-post-exit-fs-stall

Build one same-run authoritative command-advance audit for item -421. Read
`docs/F5-UCODE-REFERENCE.md` first. At `processRDPLists`, log a phase-budgeted
ring of the raw command address/opcode, selected command length, next address,
and pending-command boundary state for post-sec2 tasks whose independent
`DL_SYNC2` walk reports `e9_aligned>0`. Include a positive-control sample from
tasks where authoritative E9 does dispatch. Do not change command lengths or
inject/drop commands.

Commands:

    ./submodule-patches/export.sh
    DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build build -j8
    env BUDGET_S=2400 zsh scratch/agent/s670_postsec2_pulse_freeroll.sh

## Competing hypotheses

- **H-rdp-length-skip:** `commandWordLengths[op]` advances across aligned E9
  slots because an earlier command length is wrong for Factor 5 output.
- **H-rdp-boundary-carry:** pending-command carry across DPC submissions
  consumes or reassembles bytes so the E9 slot is never a command boundary.
- **H-rdp-source-divergence:** the independent guest walker and authoritative
  RDP parser are examining different buffers/stages; no local advance crosses
  the walker's E9 address.

## Discriminating measurement

Join each aligned E9 address to the authoritative address/advance ring.
Positive controls: section 2 reached, `e9_aligned>0`, millions of authoritative
commands, E7 nonzero before the scoped window, and at least one authoritative
E9 with matching handler/state lines.

- An earlier command's `[addr,next)` spans the E9 slot: H-rdp-length-skip;
  compare that opcode's length with the reference table.
- The E9 bytes enter/leave pending-command state: H-rdp-boundary-carry.
- No authoritative range covers the aligned address: H-rdp-source-divergence;
  add buffer provenance/range IDs next.
- Addresses and boundaries match yet E9 is not decoded: instrument the exact
  raw bytes at the first mismatch before proposing any fix.
