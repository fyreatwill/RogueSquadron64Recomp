# Session 3057 — M5 VI writer mapping

## Question and competing hypotheses

The retail VI-register watch attributed the 640→1024 write to guest PC
`0x80035798`. The alternatives were `H-WriterMissing` (the containing writer
or caller is absent), `H-WriterAliased` (the port resolves it to the wrong
body), and `H-ModeDescriptorCorrupt` (a legitimate 1024 descriptor is
corrupted before commit). The discriminator was to resolve the PC interval,
match its state transition and game-side callsites, and compare the s3056
port request table.

## Identity and call-chain table

| Item | Retail | Port |
|---|---|---|
| Attributed PC | `0x80035798` | Host VI commit path, not generated MIPS |
| Containing symbol | `__osViSwapContext`, `0x80035550`, size `0x35C` | `events.cpp::update_vi()` |
| Register write | VI context swap copies mode fields into VI registers | `events.cpp:449–462` copies `common_regs`/`field_regs` into `events_context.vi.regs` |
| Mode publication | `osViSetMode` selects the next VI context | `events.cpp:950–957` stores `mode`, `mode_guest`, and control in next state |
| Game callsites | `initVideoSubsystem` `0x8001B720`; `applyPendingViChanges` `0x8001B8DC`; `swapBufferWithViMode` `0x8001BB54`; `selectAndApplyViMode` `0x8001BC28` | Generated `funcs_5.c` contains all four calls, plus the separate boot call in `funcs_0.c` |
| Registration | `osViSetMode`, `osViSwapBuffer`, and `__osViSwapContext` are named in the retail map | `osViSetMode` is the registered host callback; `__osViSwapContext` is implemented by the runtime VI thread, so it has no generated overlay entry |

The address interval is decisive: `0x80035798` is outside `osViSetMode`
(`0x800352D0–0x80035338`) and inside `__osViSwapContext`
(`0x80035550–0x800358AC`). It is a consumer-side VI-register commit, not the
game-side mode-descriptor writer.

## Port evidence

The s3056 port capture (`/tmp/port_osvisetmode_s3056_run2.log`) logged these
four requests:

| Request | Host site | Width | Phase |
|---:|---|---:|---|
| 1 | `initVideoSubsystem` | 320 | boot |
| 2 | `swapBufferWithViMode` | 2 | transient malformed descriptor |
| 3 | `initVideoSubsystem` | 640 | VI-640 stall |
| 4 | `applyPendingViChanges` | 640 | VI-640 stall |

There was no width-1024 request. `osViSetMode` forwards the guest pointer
unchanged to the next state; `update_vi` later reads `common_regs->width`
unchanged and writes `VI_WIDTH_REG`. No port-side 1024 descriptor exists for
the runtime writer to consume in this capture.

## Classification

This rejects `H-WriterMissing` and `H-WriterAliased` at the runtime boundary:
the retail PC is a libultra context-commit routine and the port has the
corresponding commit implementation. `H-ModeDescriptorCorrupt` is not
selected because the port never produced a 1024 descriptor; the width-2 entry
is separate and the later request is 640. The blocker remains upstream:
identify which retail game-side call/state produces 1024 and why that path is
not reached by the port.

This uses two sources: the retail symbol interval/map and the port source plus
s3056 call table. No behavior changed.
