# NEXT work unit (s2293) — M5 retail 0x800078EC target-phase writer contract

HYPOTHESIS-ID: m5-step3-retail-port-writer-join

## Work unit

Run one oracle-only writer-contract capture. Watch retail execution at guest PC
`0x800078EC`, phase-gated to `512 @ 0x006AB400`, while retaining the independent
whole-RDRAM, task/output, title, hangar, and exact 16-slot write controls from
s2292. Add the bounded post-value-PC sample for `0x800078EC` and the same
per-slot writer/post-value summaries. Do not launch a port arm and do not
implement a writer, writeback, consumer, slot, gate, guard, or address remap.
The two qualified port comparison rows are
`0x168850/0x300/0x2B9E9631/nz=621` and
`0x168B50/0x300/0x6ADD4218/nz=639`.

## Competing hypotheses and discriminating measurement

- H-RetailWriterTargetPhase: `0x800078EC` executes in the target 512 phase and
  its GPR tuple plus post-value row identifies a nonzero store to one of the
  two qualified port slots. This selects a shared target-phase writer edge.
- H-RetailWriterPreTarget: the whole-RDRAM and title/hangar controls pass, but
  `0x800078EC` has no target-phase execution or post-value sample; all exact
  slot writes are pre-target. This selects a pre-target staging writer, not a
  target payload producer.
- H-RetailMetadataContract: target-phase execution occurs, but its
  `$v0/$s1/$a0/$a2` and slot rows identify pointer/length or metadata activity
  without a nonzero payload/order match to either port tuple. This retains the
  retail/port contract gap without authorizing a mitigation.
- H-CoverageInvalid: the whole-RDRAM threshold, retail title/hangar, or the
  target-phase control is absent; no writer null is interpretable.

The discriminator is one table keyed by `(target-phase exec PC, VI origin,
$v0/$s1/$a0/$a2, slot, writer PC, post-value sample, destination, length,
payload polarity/FNV, ordering)`. A target-phase nonzero exact-slot join
selects H-RetailWriterTargetPhase; controls plus no target writer select
H-RetailWriterPreTarget; target writer/metadata rows without a payload join
select H-RetailMetadataContract; missing controls select H-CoverageInvalid.

## Exact commands

1. Create the self-contained driver
   `scratch/agent/run_s2293_m5_retail_writer_phase_join.sh`. It must run from
   the repo root, launch the retail oracle with Rice video and the eleven
   `start` presses, use watch index 0 for `0x0:0x800000`, index 1 for
   `0x166000:0x16A000`, index 2 for `0x141AD0:0x141AF0`, and indexes 3–18 for
   the same 16 `0x300` windows beginning at `0x166450` through `0x169150`.
   Arm `--watch-pc 0x800078EC`,
   `--pc-phase-log-width 0x006AB400:512`,
   `--post-value-pc 0x800078EC`, `--pc-hist-watch 3` through `18`, and
   `--post-value-watch 3` through `18`. Gate interpretation on the positive
   control threshold `10000` plus retail title/hangar; retain the natural
   oracle shutdown summary.
2. Check and run exactly that driver:

   `zsh -n scratch/agent/run_s2293_m5_retail_writer_phase_join.sh`

   `zsh scratch/agent/run_s2293_m5_retail_writer_phase_join.sh`

If any independent control is absent, record H-CoverageInvalid and do not
interpret target-phase writer or post-value nulls.
