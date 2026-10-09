# Next work unit (s4340): name the C88C branch-state writer

HYPOTHESIS-ID: m5-step9-branch-state-writer

s4339 passed the host positive control, title VI 1024, hangar VI 512, both
filter controls, and emitted 256 C88C/direct rows. Port C88C had
`branch_state=0` on all rows, while retail C904 at origin `0x006AB400` used
`0x3108` for `s1=2` and `0x0010` for `s1=1`; port source words/bytes and row
order also diverged. The prior reader bug was fixed and the same recipe reran.
The external field-key arm remains parked as route-invalid.

Competing hypotheses:

- H-port-writer-missing: retail has a writer/publication boundary for the
  low physical field at `s1+0x22` that the port does not execute.
- H-port-stale-read: the port writer executes, but the C88C witness reads the
  field before publication or from a different task/state epoch.
- H-field-mapping: `s1+0x22` is not the semantic counterpart at the port even
  though the C904/C88C entry shapes agree.

Discriminator: one batched, phase-gated writer census of physical addresses
`0x20..0x30` in the port plus the independent retail oracle's same range. The
port must include a positive-control write and print writer PC, value, and
the C88C row/sequence key. Matching writer PCs/values with a zero-at-entry
selects H-port-stale-read; retail-only writers select H-port-writer-missing;
no corresponding writer/value in either arm selects H-field-mapping. A null
without both positive controls is unevaluable.

Run requirements:

1. Keep the qualified seeded-save in-process autopilot route, `M4_Y8000_WIDTH=512`,
   LLE/solo/spin-yield, real audio, and phase gates.
2. Build every writer arm in one build; run one port capture and one retail
   oracle capture with whole-RDRAM/VI controls and the low-range watch.
3. Do not add a guard, alter decoder/RSP/AI behavior, or use the external
   field-key route.
