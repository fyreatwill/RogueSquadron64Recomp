# NEXT work unit — who sends to 0x8011A818 during the retail viewer

HYPOTHESIS-ID: m5-osvimode-viewer-frame-exit

## Resume context

Session 3291 selected `H-RetailRecvReturns`: retail's
`submitGfxFrame` first `osRecvMesg` at `0x8000C0B4`
(`mq=0x8011A818`, blocking) returns every time during the attract
viewer (241/241 in 2.5–6.7 s, max gap 0.1 s). Session 3290: the
port's third viewer invocation enters that recv and does not
return. Iron rule 12: ask retail who produces on that queue
before another port instrument. Keep s3288 fade / s3289 SENT /
s3290 inner probes in the port tree; this unit is oracle-only.

## Competing hypotheses

- `H-RetailEventMesgProducer`: during 2.5–6.7 s, `osSendMesg`
  (`0x80033410`) or `osJamMesg` (`0x8002C3B0`) with
  `$a0=0x8011A818` has `prev_pc` in the libultra event/interrupt
  path (SP/DP complete, `__osEventState`, around
  `0x8002xxxx`/`0x80033xxx` other than the send/jam bodies).
- `H-RetailSubmitSelfProducer`: those sends have `prev_pc` inside
  `submitGfxFrame` (`0x8000C07C`..`0x8000C6CC`).
- `H-RetailViRetraceProducer`: those sends have `prev_pc` inside
  `viRetraceHandlerThread` (`0x80019868`..`0x80019C00`) or
  `postSwapRdpReset` (`0x8001C12C`).
- `H-SendCoverageInvalid`: whole-RDRAM 10000-write control, title
  `1024 @ 0x00790400`, viewer `0x800C28F0`, or `0x800C2E00` miss,
  or no `$a0=0x8011A818` send/jam row in 2.5–6.7 s.

## Discriminator

One independent retail Rice oracle, 25 s, eleven-Start. Watches
are physical. Exec watches armed at first VI (no
`--pc-phase-log-width` on the first run). Histogram plus printed
exec-prev rows: `osSendMesg` / `osJamMesg` with `$a0=0x8011A818`
during 2.5–6.7 s, with viewer entry/return as gates.

`prev_pc` in the event/interrupt range selects
`H-RetailEventMesgProducer`. `prev_pc` in `submitGfxFrame`
selects `H-RetailSubmitSelfProducer`. `prev_pc` in the VI
retrace / post-swap range selects `H-RetailViRetraceProducer`.
Missed controls or no matching `$a0` row is a failed instrument.

Use `--hit-cap 20000` so the send/jam flood still prints through
the viewer after the 10000-write control is removed. If printed
`$a0=0x8011A818` rows still miss 2.5–6.7 s, same-iteration rerun
with `--pc-phase-log-width 0x0066A500:640` plus
`0x0066AA00:640` and `0x005D4500:640`.

Do not add a skip, allow, restore, or wait bypass. No M5 Step 3.

## Exact commands

```
tools/oracle/build/rs64_oracle \
  --watch-write 0x0:0x800000 \
  --watch-pc 0x80033410,0x8002C3B0,0x800C28F0,0x800C2E00 \
  --secs 25 --hit-cap 20000 --vi-trace --vi-poll \
  --video rice
```

Log: `scratch/agent/s3292_retail_submit_send.md` plus the oracle
capture. Filter printed execs to `$a0=0x8011A818` (and jam
equivalent) in the viewer window; keep the lifetime exec-prev
histogram.
