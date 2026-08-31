# Session 3334 — M5 callback-writer attribution

The independent retail arm ran first with Rice for 75 seconds and the
required whole-RDRAM positive control. It reached the target 512 phase at
`0x006AB400`; the control produced 10,019 writes and the callback-table watch
produced 19 writes. Retail executed the expected edges: `0x80066AA4` to
`0x8009BBA0` twice, `0x8009BC50` to `0x80007910` three times, and the
dispatcher reached `0x8009B5A8` 2,166 times and `0x8009BD7C` 1,163 times.

The single rebuilt port arm reached title `1024 @ 0x00790400` and hangar
`512 @ 0x006AB400`. Its positive controls fired: 512 task-handoff rows and
132 host-boundary rows. The new callback-writer control fired in both target
phase buckets, and the three initializer/callsite rows appeared in each:

```text
edge=1 pc=0x80066AA4 value=0x00000000
edge=2 pc=0x8009BBA0 value=0x00000000
edge=3 pc=0x8009BC50 value=0x8009B5A8
```

There were three rows for each edge in each bucket and zero rows for edge 4,
the actual `0x80007928` store. The phase poll simultaneously showed
`cb=[80003250 8009123C 8009123C 8009123C]`. Therefore the initializer is
reached and passes the legitimate target `0x8009B5A8`, but the registration
function finds no empty callback slot and performs no store. This refutes
`H-PortCallbackWriterIsInit` and `H-PortCallbackWriterUnobserved` for the
qualified route. It does not yet identify the writer/loader that populated
the three `0x8009123C` slots, so no behavior change is authorized.

The persistent replay helper is `tools/apply_s3334_m5_callback_writer.py`.
