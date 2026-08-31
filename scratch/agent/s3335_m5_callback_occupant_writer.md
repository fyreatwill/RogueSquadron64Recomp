# Session 3335 — M5 callback occupant-writer attribution

## Work unit

The independent retail oracle was run first with whole-RDRAM and callback-table
write controls. The port was then rebuilt with a phase poller that samples all
four callback words at 1 ms when `ROGUESQ_LOG_M5_CALLBACK_CENSUS=1`, recording
the changed table and `g_rs64_last_guest_pc`. Existing callback, task, host,
and hangar controls remained enabled.

## Results

Retail passed the whole-RDRAM control at 10,000 writes and reached the driven
title/hangar route. The callback-table watch reported 19 writes. Retail
executed `0x80007928` with `$a0=0x80003250`, then with `$a0=0x8009123C`, and
executed the known callback consumers `0x8009B5A8` and `0x8009BD7C` in the
target route. This independently confirms that the occupied entries are
produced by real callback registration activity.

The port passed the host/task controls, title VI 1024, and hangar VI 512.
The census observed these table transitions:

```
n=1  cb=[80003250,00000000,00000000,00000000] last_pc=80001F88
n=2  cb=[80003250,8009123C,00000000,00000000] last_pc=80007A68
n=3  cb=[80003250,8009123C,8009123C,00000000] last_pc=80001F88
```

Static source inspection maps `0x80001F88` to the return delay slot after the
caller at `0x80002FDC` invokes `registerSiCallback` with `0x80003250`. The
1-ms poll is not an exact store-PC witness, and `0x80007A68` is a later
function-end marker; therefore the exact second registration caller remains
unresolved. The phase-gated known writer hooks still show the initializer's
legitimate `0x8009B5A8` registration, while no `0x80007928` store occurs in
the full-table phase because all slots are already occupied.

## Discriminator outcome

`H-PortCallbackOccupantIsRuntime` is selected at the class level: the port's
pre-existing occupants are populated during generated execution, not by the
initializer under test. Exact attribution of the `0x8009123C` registrations
is still open because the asynchronous census records a nearby last-PC, not a
write instruction. No behavior change or mitigation was made.

Evidence is two-source: the retail callback-table/PC capture and the port
same-run census with task/host/VI controls.
