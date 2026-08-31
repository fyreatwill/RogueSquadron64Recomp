# M5-S3406 retail producer dispatch census

The retail ELF was scanned across `.entry`, `.text`, and all three overlay
sections for encoded `JAL` instructions targeting `rs_memset` at `0x800078E0`.
The body at `0x800078E0..0x80007908` contains no outbound call. The scan found
88 direct sites, including 37 in main, 8 in mission, 35 in menu, and 8 in
cinematic. The disputed boundary is not in that direct set.

At `0x8002BEEC`, the retail ELF contains `0x42000018`, not an encoded direct
`JAL`; the following instruction at `0x8002BEF0` is a `JAL` to `0x8002B480`.

The valid focused independent oracle arm passed the positive controls: 10,010
whole-RDRAM writes, 10 writes at `0x1935E0`, and 1,281 VI rows in the
`0x006AB400`/512 hangar bucket. It recorded 191,046 executions at
`0x8002BEEC`, 3,244,175 at `0x800078EC`, and
`exec-prev pc=0x800078ec prev=0x8002beec n=177`. No direct candidate was an
observed producer predecessor. The attempted all-88-PC watch arm exited 2 at
oracle setup and is not evidence.

At this measured scope, `H-IndirectDispatch` is selected, while
`H-StaticCallsite` and `H-RouteMismatch` are refuted. The exact runtime
meaning of the `0x8002BEEC` predecessor relation remains open because the
oracle predecessor field and static instruction classification are independent
lines of evidence. No port code or audio behavior changed.

Evidence: `scratch/agent/s3406_retail_producer_dispatch/oracle.log`,
`oracle-fixed.log`, and `oracle-focused.log`.
