# NEXT work unit — identify a new retail-grounded upstream handoff

HYPOTHESIS-ID: m5-audio-route-upstream-retail-boundary

## Single work unit

Use one static audit to choose a genuinely new instruction or handoff upstream
of the retail `__osViSwapContext` origin publication, then run one oracle
capture for that exact edge. Do not repeat `0x800356A8`, the closed
`0x80034F38:0x80035B00` consumer range, or `0x80035788`; the port publication
probe had positive controls but stopped at VI 640.

## Competing hypotheses

- H-NewRetailBoundary: the new watched PC executes in retail during title or
  hangar, giving direct attribution for an upstream handoff.
- H-RetailBoundaryAbsent: whole-RDRAM and title/hangar controls pass but the
  new candidate has zero target-phase executions; select another static edge.
- H-RetailControlInvalid: the positive control or title/hangar phase markers
  fail, so the candidate result is unevaluable.

## Discriminating measurement

The oracle run must pass the whole-RDRAM positive control and reach title
`1024 @ 0x00790400` plus hangar `512 @ 0x006AB400`. A target-phase execution
row for the new PC selects H-NewRetailBoundary; valid controls plus no such
row selects H-RetailBoundaryAbsent; missing controls or either target phase
selects H-RetailControlInvalid.

## Exact commands

1. Read the relevant static VI-manager code and select one new upstream PC.
2. Run `tools/oracle/build/rs64_oracle` with `--watch-write 0x0:0x800000`,
   `--watch-pc <new-pc>`, `--vi-trace`, Rice, and the verified Start schedule.
3. Record the control count, title/hangar phase rows, and candidate-PC rows;
   do not add a port instrument unless the oracle selects H-NewRetailBoundary.
