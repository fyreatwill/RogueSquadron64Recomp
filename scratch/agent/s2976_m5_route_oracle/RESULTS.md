# Session 2976 M5 route oracle capture

Execution watches now defer until the first requested `(VI origin,width)`
bucket; memory watches still arm at the first VI. The initial command omitted
Rice and reached no target phase, so it was a setup failure. The corrected
same-unit capture used Rice and VI tracing.

| Measurement | Result |
|---|---|
| Whole-RDRAM positive control | 10,000 write callbacks; removed at threshold |
| Target phase arm | `1024 @ 0x00790400` |
| Retail run | 45.1 s wall, 2,625 VI (~43.8 s emulated) |
| Route-PC executions | 5,204; predecessor `0x80033300` |
| Title target rows | 1,352 |
| Hangar target rows | 810 at `512 @ 0x006AB400` |
| Other rows after arm | 32 at `1024 @ 0x00790800` |

This positively shows retail route preparation at `0x80019CD8` in both target
phases without boot-loop breakpoint overhead. It supports
`H-retail-target-predicate` as single-source evidence and rules out an absent
retail route call and the debugger-overhead explanation for this capture. It
does not establish a port predicate mismatch.
