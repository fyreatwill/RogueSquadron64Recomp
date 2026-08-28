# s2948 route-prepare rejection results

The first launch variant was invalid because `timeout` is unavailable on this
host; it produced no game output. The fixed launch used a background watchdog
and SIGKILL cleanup. The game launcher returned 127, but its child emitted a
complete diagnostic log; remaining processes were then SIGKILLed before these
counts were computed.

- `[route-prep]`: 771 rows
- `[f5-fetch-control]`: 8 rows (positive control; four in phase 2 and four in phase 4)
- `[phase]`: 4 transitions: 320 boot, 2/0x006DD000, 640/0x0066A500
- `[m5-route-candidate]`: 0 rows
- `[CRASH]`/`[ABORT]`: 0 rows

All 771 route-prep rows had `target=0 accepted=0`; no row reached the target
1024/0x00790400 or 512/0x006AB400 keys. The scheduler state was populated:
`s0=0x80128C70` or `0x00000001`, `s1=0x00000001`, `s2=0x8011A89F`,
`s3=0x8011A8A0`, `s4=0x8011A89C`, `s5=0x00000002`, and `a1=0x8011D460`,
`a2=1`. Message types observed were `0x01`, `0x02`, and `0x81`, mapping to
the accept, terminal, and retry branches respectively.

## Discrimination

The same-run positive control proves the probe was live. The route stopped at
pre-title VI 640, so the new measurement does not select
H-PrepareFieldBad, H-PrepareTimingBad, or H-PrepareLogicBad: the accepted
retail phase was never reached. It confirms H-PreparePreTitle / route
qualification failure and rules out a missing scheduler invocation. The next
probe must ground-truth the message/branch tuple in the retail target phase
before adding another port-side field.

## Samples

```text
[f5-fetch-control] phase=2 n=1 op=0x06 w0=0x06000000 w1=0x80037658
[f5-fetch-control] phase=2 n=2 op=0xB6 w0=0xB6000000 w1=0x001F3204
[f5-fetch-control] phase=2 n=3 op=0xB7 w0=0xB7000000 w1=0x00800005
[f5-fetch-control] phase=2 n=4 op=0xBC w0=0xBC000404 w1=0x00000002
[route-prep] n=244 phase=4 width=640 origin=0x66A500 target=0 accepted=0 pc=0x80019CD8 caller=0x00000000 sp=0x8011D450 s0=0x00000001 s1=0x00000001 s2=0x8011A89F s3=0x8011A8A0 s4=0x8011A89C s5=0x00000002 a0=0x80128C70 a1=0x8011D460 a2=0x00000001 v0=0x00000000 msg=0x81 branch=3 active=0 ordinal=4294967295 row=4294967295 exit=0
```
