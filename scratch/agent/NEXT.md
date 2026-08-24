# NEXT work unit (s2209) — join retail early origins to `__osViNext`

HYPOTHESIS-ID: m5-a1-retail-early-context-parity

## Work unit

Before building, make one bounded diagnostic change in
`tools/oracle/rs64_oracle.c`: keep the existing `--vi-context-table-pc`
instrument and let its context join accept every width-640 origin observed in
s2208, without changing the post-swap table. The allowlist is
`0x0066A500`, `0x005D4500`, `0x0066AA00`, `0x00696600`, `0x00696100`,
`0x0062C200`, and `0x0062BD00`. Raise only the context-row cap from 256 to
1024 so the one collection cannot confuse coverage with overflow. Build the
oracle once, then run one 10-second Rice collection with the whole-RDRAM
positive control and the same verified Start schedule:

```sh
bash tools/oracle/build.sh
tools/oracle/build/rs64_oracle \
  --core /Users/williambuckley/Documents/Tools/rs64-oracle/iter974-armB2/projects/unix/libmupen64plus.dylib \
  --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 \
  --video /opt/homebrew/Cellar/mupen64plus/2.6.0/lib/mupen64plus/mupen64plus-video-rice.dylib \
  --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start \
  --hold-ms 150 --secs 10 --watch-write 0x0:0x800000 \
  --watch-pc 0x80035550 --vi-context-table-pc 0x80035550 --vi-trace \
  > scratch/agent/s2209_retail_early_context.log 2>&1
rg -n "positive-control|^\\[vi\\].*width=640|^\\[vi-context-row\\]|vi-context-summary|\\[oracle\\] done" \
  scratch/agent/s2209_retail_early_context.log
```

Do not change port VI behavior, the field knob, logger dispatch, task data,
audio dispatch, or any mitigation.

## Competing hypotheses and discriminator

- H-RetailEarlyContextAlternates: with a positive control and non-overflowing
  rows, `0x0066A500` joins valid context rows selecting field 0/candidate 0,
  while `0x0066AA00` joins valid rows selecting field 1/candidate 1. This
  proves the retail early pair uses the same frame-plus-field context
  mechanism already established for the target pair.
- H-RetailEarlyContextFixedField: both early origins join valid rows with the
  same selected field/candidate, most plausibly field 0. This proves that the
  legitimate `0x0066AA00` origin is not produced by the target field toggle.
- H-RetailEarlyContextOther: early rows are valid but their selected
  candidates, frame pointer, mode, or field relationship does not explain the
  next origin. This moves the source boundary to another VI producer.
- H-RetailEarlyContextCoverage: the whole-RDRAM control and 640 phase rows
  are positive, but early context rows are absent or the 1024-row table
  overflows. This proves only that the join scope is still insufficient and
  requires a narrower phase window.

The discriminator is the same-run tuple `(whole-RDRAM hit count, joined-row
count per 640 origin, context_valid/mode_valid, current_field, and whether
framep + selected field origin equals next_origin)`. A zero control count
invalidates every context conclusion. A mixed result that fits none of the
first three models is recorded as mixed, not promoted to a port explanation.
