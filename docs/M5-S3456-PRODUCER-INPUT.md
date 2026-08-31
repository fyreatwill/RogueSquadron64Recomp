# M5 Session 3456 — producer/input boundary

The independent retail oracle was qualified with Rice video, the documented
Start schedule, and a whole-RDRAM positive control. It reached title origin
`0x00790400` at width 1024, with 10,000 positive-control callbacks and 3,233
executions of `0x80001C98` from caller `0x800645AC`.

The port build retained the four-PC schema positive control and emitted 1,024
new rows at the input load immediately before `0x800645AC`. The load at
`0x800645A8` consistently used source pointer `0x801E8710`. In the first
ordered title prefix, retail target rows began with `s0=0x00000000`, then
`0x801B4F00`; the port producer rows began with `0x00000000`, then
`0x801B5E70`. The port target rows preserve that producer-side value, so the
first divergence is upstream of `rs_free` and its host wrapper.

This selects `H-UpstreamProducer` and rules out `H-WrapperClobber` at this
boundary. It does not yet identify the writer of `*(0x801E8710)` or establish
whether the differing source word is written by the port or is a legitimate
route difference. The next probe must attribute that slot's writer in both
systems.

Sources: `scratch/agent/s3456_oracle_ground_truth_rice.log` and
`scratch/agent/s3456_port_producer.log`.
