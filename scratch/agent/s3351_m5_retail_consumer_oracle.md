# Session 3351 — retail M5 consumer reachability oracle

The retail oracle ran for 180 seconds with Rice, the eleven-Start schedule,
the whole-RDRAM write watch, and phase-gated execution watches. The positive
control fired in the same run: the whole-RDRAM watch reached its 10,000-hit
cap, with 10,000 writes reported, and the oracle completed 10,769 VI frames.
The target hangar phase armed at `512 @ 0x006AB400`.

| PC | hits | previous-PC histogram |
|---|---:|---|
| `0x8009B5A8` | 8,469 | `0x80019B74` (8,469) |
| `0x8009BD7C` | 1,879 | `0x80097E48` (1,764), `0x80097EBC` (115) |
| `0x8009B600` | 8,469 | `0x8009B5FC` (8,469) |
| `0x8009B85C` | 8,469 | `0x8009B858` (8,469) |
| `0x8009BDE8` | 1,879 | `0x8009BDE4` (1,879) |

This proves that the retail service and accumulator bodies are live and that
the three named consumer PCs are the corresponding executed route. It refutes
`H-ConsumerWrongNames` and the retail-side absence arm of
`H-ConsumerIndirect`. It does not by itself distinguish a port reachability
gap from a port status/slot gate, because no port arm was part of this
ground-truth work unit. The next discriminator is a same-build port run with
regeneration-surviving entry probes at these PCs, retaining the existing host,
task, title, and hangar controls.

Evidence log: `scratch/agent/s3351_retail_consumer_oracle.log`.
