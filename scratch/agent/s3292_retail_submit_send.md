# Session 3292 — retail 0x8011A818 producer is spTaskSchedulerThread

HYPOTHESIS-ID: m5-osvimode-viewer-frame-exit

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
- `H-RetailSpSchedulerProducer`: those sends have `prev_pc` inside
  `spTaskSchedulerThread` (`0x80019BF4`..`0x8001A018`).
- `H-SendCoverageInvalid`: whole-RDRAM 10000-write control, title
  `1024 @ 0x00790400`, viewer `0x800C28F0`, or `0x800C2E00` miss,
  or no `$a0=0x8011A818` send/jam row in 2.5–6.7 s.

## What ran

One independent retail Rice oracle, 25 s, eleven-Start. Watches
are physical. Exec watches armed at first VI (no
`--pc-phase-log-width`). `--hit-cap 20000`.

```
tools/oracle/build/rs64_oracle
  --watch-write 0x0:0x800000
  --watch-pc 0x80033410,0x8002C3B0,0x800C28F0,0x800C2E00
  --secs 25 --hit-cap 20000 --vi-trace --vi-poll
  --video rice
```

Capture: `scratch/agent/s3292_retail_submit_send.log`.
Hit-cap printed through t=7.9 s (n=20000), after the 6.7 s
viewer return, so the fallback `--pc-phase-log-width` rerun was
not required.

No skip, allow, restore, wait bypass, or M5 Step 3.

## Same-run positive controls

- whole-RDRAM write watch: 10000 hits; `[oracle] positive-control
  threshold reached`; `[gpr-ctl]` at 0.7 s.
- title `1024 @ 0x00790400` at 17.3 s (`640 -> 1024` origin
  `0x00790800`).
- viewer entry `0x800C28F0` at 2.5 s (`prev_pc=0x800C5C98`,
  640 @ `0x0066aa00`).
- viewer return `0x800C2E00` at 6.7 s (`prev_pc=0x800C2DFC`,
  640 @ `0x0066aa00`).
- 1462 VI, 25.1 s wall / 24.4 s emulated. `rc=0`.

Failed instrument would have been a silent `0x800C2E00` or missed
title 1024. Both fired.

## Lifetime watches

| watch | hits |
|---|---:|
| write `[0x0,0x800000)` | 10000 |
| `osSendMesg` `0x80033410` | 40980 |
| `osJamMesg` `0x8002C3B0` | 2327 |
| viewer entry `0x800C28F0` | 1 |
| viewer return `0x800C2E00` | 1 |

`osJamMesg` exec-prev is a single caller `0x800324E4` n=2327.
Zero printed jam rows have `$a0=0x8011A818`.

## Viewer-window `$a0=0x8011A818` (printed; 2.5–6.7 s)

242 `osSendMesg` rows, **all** `prev_pc=0x80019F1C`.
`$a1=0` `$a2=0` (NOBLOCK, null mesg). Width 640, origins
`0x0066aa00` / `0x005d4500`. First at 2.7 s, last at 6.7 s.
~6 sends per 0.1 s bucket.

s3291 viewer recvs on the same queue were 241 in the same
window; lifetime `0x80019F1C` send-prev n=723 vs s3291 recv 719.

Generated body (`RecompiledFuncs/funcs_4.c`): `0x80019F1C` is
`jal osSendMesg` inside `spTaskSchedulerThread` (`0x80019BF4`,
size `0x424`). Delay-slot/`lui`/`addiu` load
`$a0=0x80120000-0x57E8=0x8011A818`. The send is skipped when
`lbu 0x80128D44 == 0` (`beq` to `L_80019F24`); on take it stores
zero to that byte then sends.

## Classification

This selects `H-RetailSpSchedulerProducer` and refutes
`H-RetailEventMesgProducer`, `H-RetailSubmitSelfProducer`,
`H-RetailViRetraceProducer`, and `H-SendCoverageInvalid`.

`viRetraceHandlerThread` ends at `0x80019BC4` (syms size `0x35C`).
`0x80019F1C` is 0x328 into the scheduler thread, not the retrace
handler or `postSwapRdpReset`. `submitGfxFrame` send jal
`0x8000C2A0` is a lifetime n=4 caller of `osSendMesg` and is not
this queue.

Combined with s3290/s3291: the port's third viewer
`submitGfxFrame` blocks in a recv whose retail producer is the
scheduler jal at `0x80019F1C`, gated on `0x80128D44`.

No audio or M5 Step 3 change.
