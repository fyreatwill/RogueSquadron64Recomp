# Session 3241 — target-phase VI-swap output relation

The independent retail oracle was run with Rice, the validated Start schedule,
and a whole-physical-RDRAM write watch as the same-run positive control. It
reached title VI 1024 (`0x00790400`/`0x00790800`) and hangar VI 512
(`0x006AB400`). The positive control reached its 10,000-callback threshold.

The corrected target-phase execution watch on `osViSwapBuffer` (`0x80035500`)
was phase-gated at width 1024, origin `0x00790400`. It recorded 1,130
executions, all with predecessor `0x8001BE24`. Target rows showed
`$a0=0x80790000`, physical framebuffer `0x00790000`, and alternating target
VI origins `0x00790400` and `0x00790800`. The VI trace places the swap rows
after the 640-to-1024 transition and before the later 512 hangar transition.

The first attempt used the pre-transition `0x00790A00:640` bucket and produced
zero watched executions; its controls were valid but its gate was wrong. The
fixed run used `0x00790400:1024` and produced the target rows above.

Result: `H-PortBoundary` is selected as a target-phase output relation is now
available for the port comparison. This is single-source oracle evidence: the
independent execution watch and VI callback are two signals from one retail
run, not two independent implementations. No port instrumentation, guest
value, ordering change, guard, or mitigation was made.

ORIGIN: no mitigation or guest value was changed; the framebuffer pointer and
VI origins are legitimate retail publication values observed at the swap edge.

Evidence: `scratch/agent/soak_results/s3241_m5_vi_swap_target/oracle.log`.
