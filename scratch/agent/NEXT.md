# NEXT work unit — does retail's first submitGfxFrame recv return in the viewer

HYPOTHESIS-ID: m5-osvimode-viewer-frame-exit

## Resume context

Session 3290 selected `H-SubmitRecvBlocked`: after `SENT` n=3,
`submitGfxFrame` entered `osRecvMesg` at `0x8000C0B4`
(`mq=0x8011A818`, `a2=1`) and did not return. SENT n=2 recv'd the
same queue and returned. SENT n=1 skipped that recv
(`0x8011A89E==0`). Iron rule 12: ask retail before another port
instrument. Keep s3288 fade / s3289 SENT / s3290 inner probes in
the port tree; this unit is oracle-only.

## Competing hypotheses

- `H-RetailRecvReturns`: during the attract viewer (2.5–6.7 s),
  `0x8000C0B4` fires and `0x8000C0BC` follows in the same 0.1 s
  buckets (recv returns). Lifetime hits of both PCs are large and
  matched. The port's block is then a missing/lost producer on
  `0x8011A818`.
- `H-RetailRecvBlocks`: `0x8000C0B4` fires without a following
  `0x8000C0BC` for seconds at a time. Retail also waits here;
  the port's third-invocation stall is not a unique recv hang.
- `H-RetailRecvSkipped`: `0x8000C0B4` is silent through the
  viewer (`0x8011A89E` stays 0). Retail never takes this recv on
  that screen; the port's n=2/n=3 gate-byte is extra.
- `H-ExitCoverageInvalid`: whole-RDRAM 10000-write control, title
  `1024 @ 0x00790400`, viewer `0x800C28F0`, or `0x800C2E00` miss.

## Discriminator

One independent retail Rice oracle, 25 s, eleven-Start. Watches
are physical. Exec watches armed at first VI (no
`--pc-phase-log-width`). Histogram counts plus printed exec-prev
rows: `0x8000C0B4` vs `0x8000C0BC` during 2.5–6.7 s, with viewer
entry/return as gates.

C0B4 hits with matching C0BC hits in the viewer window select
`H-RetailRecvReturns`. C0B4 without C0BC selects
`H-RetailRecvBlocks`. Silent C0B4 with live viewer entry/return
selects `H-RetailRecvSkipped`. Missed controls are a failed
instrument.

Do not add a skip, allow, restore, or wait bypass. No M5 Step 3.

## Exact commands

```
tools/oracle/build/rs64_oracle \
  --watch-write 0x0:0x800000 \
  --watch-pc 0x8000C0B4,0x8000C0BC,0x800C28F0,0x800C2E00 \
  --secs 25 --hit-cap 10000 --vi-trace --vi-poll \
  --video rice
```

Log: `scratch/agent/s3291_retail_submit_recv.md` plus the oracle
capture. If `EXEC_LOG_CAP=64` truncates the printed join, keep the
lifetime histogram and, only if the histogram cannot split the
hypotheses, rerun with `--hit-cap 20000` in the same iteration.
