# Session 3291 — retail submitGfxFrame first recv returns during the viewer

HYPOTHESIS-ID: m5-osvimode-viewer-frame-exit

## Competing hypotheses

- `H-RetailRecvReturns`: during the attract viewer (2.5–6.7 s),
  `0x8000C0B4` fires and `0x8000C0BC` follows in the same 0.1 s
  buckets. Lifetime hits of both PCs are large and matched. The
  port's SENT n=3 block is then a missing/lost producer on
  `0x8011A818`.
- `H-RetailRecvBlocks`: `0x8000C0B4` fires without a following
  `0x8000C0BC` for seconds at a time. Retail also waits here.
- `H-RetailRecvSkipped`: `0x8000C0B4` is silent through the
  viewer. Retail never takes this recv on that screen.
- `H-ExitCoverageInvalid`: whole-RDRAM 10000-write control, title
  `1024 @ 0x00790400`, viewer `0x800C28F0`, or `0x800C2E00` miss.

## What ran

Two independent retail Rice oracles, 25 s, eleven-Start. Watches
are physical. Exec watches armed at first VI (no
`--pc-phase-log-width`).

```
tools/oracle/build/rs64_oracle
  --watch-write 0x0:0x800000
  --watch-pc 0x8000C0B4,0x8000C0BC,0x800C28F0,0x800C2E00
  --secs 25 --hit-cap 10000 --vi-trace --vi-poll
  --video rice
```

Prescribed `--hit-cap 10000` run:
`scratch/agent/s3291_retail_submit_recv.log`. That cap plus
`EXEC_LOG_CAP=64` printed only the first 64 exec hits (32 `C0B4`
+ 32 `C0BC` at 0.9–1.9 s, width 320). Lifetime histogram already
matched (718/718) but could not split a viewer-window return from
a multi-second block. Same-iteration rerun with `--hit-cap 20000`:
`scratch/agent/s3291_retail_submit_recv_cap20000.log`.

No skip, allow, restore, wait bypass, or M5 Step 3.

## Same-run positive controls (cap-20000)

- whole-RDRAM write watch: 10000 hits; `[oracle] positive-control
  threshold reached`; `[gpr-ctl]` at 0.8 s.
- title `1024 @ 0x00790400` at 17.3 s (`640 -> 1024` origin
  `0x00790800`).
- viewer entry `0x800C28F0` at 2.5 s (`prev_pc=0x800C5C98`,
  640 @ `0x0066aa00`).
- viewer return `0x800C2E00` at 6.7 s (`prev_pc=0x800C2DFC`,
  640 @ `0x0066aa00`).
- 1459 VI, 25.1 s wall / 24.3 s emulated. `rc=0`.

Failed instrument would have been a silent `0x800C2E00` or missed
title 1024. Both fired.

## Exec table (cap-20000 print; all 1440 execs printed)

| PC | hits | t | prev_pc | notes |
|---|---:|---|---|---|
| `0x8000C0B4` | 719 | 0.8–25.0 s | `0x8000C0B0` | jal `osRecvMesg`; `$a0=0x8011A818` |
| `0x8000C0BC` | 719 | 0.8–25.0 s | `0x80033300` | recv continuation; `osRecvMesg` `jr ra` |
| `0x800C28F0` | 1 | 2.5 s | `0x800C5C98` | viewer entry |
| `0x800C2E00` | 1 | 6.7 s | `0x800C2DFC` | viewer `jr ra` |

Viewer window 2.5–6.7 s: `C0B4=241` and `C0BC=241` in the same
0.1 s buckets at width 640 origins `0x0066aa00` / `0x005d4500`.
Max `C0B4`→next `C0BC` gap over the whole printed set is 0.1 s.
The 5.2 / 5.3 bucket 6/5 then 6/7 split is 0.1 s rounding, not a
block (12=12 across 0.2 s).

Every `C0BC` `prev_pc` is `0x80033300` (`osRecvMesg` ends at
`0x80033308`). `$a0` at `C0B4` is `0x8011A818` (same queue as
port SENT n=3). After return, `$a2=1` (blocking).

## Classification

This selects `H-RetailRecvReturns` and refutes
`H-RetailRecvBlocks`, `H-RetailRecvSkipped`, and
`H-ExitCoverageInvalid`. Combined with s3290: the port's third
viewer `submitGfxFrame` blocks in a recv retail returns from
every time. Next discriminator is who sends to `0x8011A818`
during the viewer.

No audio or M5 Step 3 change.
