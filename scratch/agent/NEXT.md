# NEXT work unit (s2191) — complete the second-origin port writer census

HYPOTHESIS-ID: m5-a1-retail-writer-census

## Work unit

Run the already-built binary with the s2190 writer probe, without menu keys,
so the passive route can reach the later 640 B-frontend origin
`0x00696600`. The s2190 positive control and covered-origin rows remain the
control; do not add a guard, task rewrite, mitigation, or audio-default flip.

Exact command:

```sh
zsh scratch/agent/run_s2191_m5_second_origin.sh
```

After it exits, parse the complete two-origin table into
`scratch/agent/s2191_m5_second_origin.txt`:

```sh
grep -a '\[m5-writer-parity\]' scratch/agent/s2191_m5_second_origin/run.log
grep -a '\[phase\] vi_width=640' scratch/agent/s2191_m5_second_origin/run.log
```

The table must include all six targets at both `0x00696100` and
`0x00696600`, with unique guest PCs and the positive-control count. A missing
second-origin phase is coverage-limited, not a null.

## Competing hypotheses and discriminator

- H-PortRetailParitySecond: at `0x00696600`, sparse port PCs match s2189
  retail: target 1=`0x80018F5C`, target 2=`0x80018F60`, target
  3=`0x800078EC`/`0x800A8144`, target 5=`0x800078EC`/`0x80018F60`, and
  target 6=`0x80057100`; target 4 remains broad.
- H-PortOriginMismatchConfirmed: any sparse PC set differs from retail, or
  a writer appears under the opposite origin bucket.
- H-PortSecondOriginAbsent: the route has a positive 640 control but exits or
  times out before `0x00696600`, leaving the second-origin cells uncovered.
- H-PortCoverageFailure: the helper control or phase control does not fire,
  so the run cannot classify writer parity.

The discriminator is one same-run table of all six targets at both 640
origins. It selects second-origin parity, confirms an origin-specific port
mismatch, identifies a route boundary, or rejects the run as uncovered.
