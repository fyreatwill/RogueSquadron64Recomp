# NEXT work unit — M5 port callback-table host-boundary census

HYPOTHESIS-ID: m5-consumer-reachability-audit

Retail ground truth passed whole-RDRAM, title, and hangar controls. Its 19
callback-table writes all came from guest `registerSiCallback` (`0x80007928`)
or guest clear (`0x80007968`); no host writer or stale transition was observed.
The port still starts with three `0x8009123C` occupants before the legitimate
`0x8009B5A8` registration.

Competing hypotheses:

- `H-PortHostBoundary`: a host/runtime helper writes the port guest table.
- `H-PortIndirectGuestWriter`: an unresolved generated indirect path writes
  the occupants.
- `H-PortPreinitializedImage`: the occupants are initialized before generated
  execution and are legitimate overlay/image state.

Discriminator: enumerate the host-side guest-memory write boundary and build
one regeneration-surviving port census that records every write to physical
`0x0011A8A4:0x0011A8B4`, its host caller/classification, and post-table values
through title and hangar. A host caller writing `0x8009123C` selects
`H-PortHostBoundary`; a generated/indirect writer selects
`H-PortIndirectGuestWriter`; no write with the occupants already present at
first valid RDRAM observation selects `H-PortPreinitializedImage`. Do not
change behavior or add a mitigation.

Exact preparation commands:

```sh
rg -n 'rdram|RDRAM|write.*memory|memcpy|TO_PTR|callback_table|11A8A4|07928|07968' src lib
rg -n 'callback_table|11A8A4|registerSiCallback' tools RecompiledFuncs
```

Before any build, record the full hypothesis table and positive-control result
in the session evidence. Build all host-boundary fields in one instrument and
run the validated title/hangar recipe once; do not spend a build per counter.
