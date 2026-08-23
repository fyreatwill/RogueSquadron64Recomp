# NEXT work unit (s2197) — retain retail swap arguments by VI origin

HYPOTHESIS-ID: m5-a1-vi-swap-caller-parity

## Work unit

Extend the independent retail oracle, not the port, with one bounded execution
table for `osViSwapBuffer` (`0x80035500`). At each execution, when the live VI
width is 640, accumulate `(VI origin, PREVIOUS_PC, $a0 physical framebuffer)`
and print the complete bounded table at shutdown. Preserve the existing
whole-RDRAM positive-control watch, execution watch, and `--vi-trace` in the
same run.

Add the table to `tools/oracle/rs64_oracle.c`, rebuild the oracle, then run:

```sh
tools/oracle/build.sh
tools/oracle/build/rs64_oracle \
  --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib \
  --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 \
  --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib \
  --secs 45 --hit-cap 10000 \
  --watch-write 0x0:0x800000 --watch-pc 0x80035500 \
  --first-watch 0 --vi-trace \
  > scratch/agent/s2197_retail_vi_swap_phase_table.log 2>&1
```

The positive controls must be at least 10,000 whole-RDRAM writes and positive
`osViSwapBuffer` execution hits. The VI trace must contain repeated 640 rows
at both `0x00696100` and `0x00696600`; otherwise reject the comparison. Parse
the new table for both target origins and compare it to s2196's port rows,
where host symbols recovered the two generated callers but `$r31-8` was
`0xFFFFFFF8`.

## Competing hypotheses and discriminator

- H-RetailPortCallerParity: retail has the same `(prev_pc, a0)` pairs at
  `0x00696600` that the port already produced at `0x00696100`; the failure is
  downstream of the guest swap call.
- H-PortMissingSecondCaller: a retail pair at `0x00696600` is absent from the
  port table; the guest route does not reach that swap.
- H-PortWrongSwapArgument: the retail caller exists in both runs, but the
  port's framebuffer argument is a different physical buffer at the covered
  phase.
- H-HostPhaseCommit: the retail target table matches the port caller/argument
  sequence, but the port never publishes `0x00696600` through its host VI
  transition.
- H-CoverageFailure: either same-run positive control or either target VI
  origin is absent; reject the comparison as invalid.

The single origin/caller/framebuffer table is the discriminator. A missing
retail target pair selects H-PortMissingSecondCaller; a matching caller with a
different port argument selects H-PortWrongSwapArgument; matching pairs with
no port second-origin phase select H-HostPhaseCommit; matching target tables
select H-RetailPortCallerParity. Do not add a port guard, mitigation, task
rewrite, writer filter, or audio-default change.
