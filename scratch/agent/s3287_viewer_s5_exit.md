# Session 3287 — retail bc1tl then beq to slot tail; delay-slot watch miss

HYPOTHESIS-ID: m5-osvimode-viewer-frame-exit

## Competing hypotheses

- `H-DelaySlotWatchMiss`: `0x800C2B84` (`bc1tl`) fires near 6.8 s and
  `0x800C2D50` then `0x800C2DA0` follow. Mupen does not report the
  nullifiable delay-slot PC `0x800C2B88` even when the branch is taken.
  The fade store ran.
- `H-BeqTakenWithoutFadeStore`: `0x800C2D50` fires and `0x800C2DA0`
  follows, but `0x800C2B84` is silent.
- `H-Da0WithoutBeq`: `0x800C2DA0` fires without `0x800C2D50`.
- `H-ExitCoverageInvalid`: whole-RDRAM control, title 1024, or the
  6.8 s `0x800C2E00` watch silent.

## Same-run controls

Rice, 25 s. Prescribed `--hit-cap 10000` run:
`scratch/agent/s3287_viewer_s5_exit.log`. That cap plus
`EXEC_LOG_CAP=64` printed only the first 64 exec hits (all
`0x800C2D50` at 2.7–3.7 s). Timed join used a same-watches rerun with
`--hit-cap 20000`:
`scratch/agent/s3287_viewer_s5_exit_cap20000.log`.
Summary counts matched both runs (31 / 243 / 1 / 1).

- whole-RDRAM write watch: 10000 hits; `[oracle] positive-control
  threshold reached`; `[gpr-ctl]` at 0.8 s.
- title `1024 @ 0x00790400` at 17.3 s (`640 -> 1024` origin
  `0x00790800`).
- `0x800C2E00` exec at 6.7 s (`prev_pc=0x800C2DFC`, `v0=1`).

Failed instrument would have been a silent `0x800C2E00`. It fired.

All exec-prev rows sit inside `0x800C28F0..0x800C2E08`.

## Exec table (cap-20000 print)

| PC | hits | t | prev_pc | notes |
|---|---:|---|---|---|
| `0x800C2B84` | 31 | 6.1–6.6 s | `0x800C2B80` | `bc1tl`; fade-out window only; `s0=0xA` |
| `0x800C2D50` | 243 | 2.6–6.6 s | `0x800C2D4C` | `beq $s5,$v0`; `v0=1` at every printed hit |
| `0x800C2DA0` | 1 | 6.6 s | `0x800C2D50` | beq taken to slot tail |
| `0x800C2E00` | 1 | 6.7 s | `0x800C2DFC` | `jr ra`; `v0=1` |

Exit interleave at 6.6 s: `2D50` n=10272 not-taken (`s5!=1`);
`2B84` n=10273; `2D50` n=10274 taken; `2DA0` n=10275; `2E00` n=10276
at 6.7 s. In `runMenuModelViewerScreen` the only `$s5=1` writer is
the `0x800C2B88` delay slot (`addiu $s5,$zero,1`); `$s5` is zeroed at
`0x800C2934`. `$v0` is hardwired 1 at `0x800C2D4C`, so the taken beq
is `$s5==1`. Combined with s3285's zero `0x800C2B88` hits, Mupen did
not report the taken delay slot.

`0x800C2B84` is reached from `L_800C2B00` (`s2==2` fade-out:
`sub.s $f24`). Other `$s2` paths jump to `L_800C2B8C` and skip it,
which is why 2B84 is silent until 6.1 s while 2D50 runs from 2.6 s.

## Classification

This selects `H-DelaySlotWatchMiss` and refutes
`H-BeqTakenWithoutFadeStore`, `H-Da0WithoutBeq`, and
`H-ExitCoverageInvalid`. s3285's `H-RetailNoFadeStore` is superseded:
the store ran; `0x800C2B88` silence is a delay-slot watch miss.

No audio behavior change. Combined with s3278: the port entered this
screen and never reached the slot tail, so it never completed this
`$s2==2` / `$f24==0` / `$s5=1` exit.
